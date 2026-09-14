#!/usr/bin/env bash
# =============================================================================
# 03_assembly/03.assemble.sh - platform-routed short/long/hybrid assembly+polish
#   illumina : Unicycler first (good for isolates, plasmids and circularization),
#              SPAdes --isolate as fallback
#   nanopore : Flye first (Canu fallback) -> minimap2+Racon x2 (cap rounds to avoid
#              over-correction) -> Medaka polish
#   pacbio   : Flye --pacbio-hifi (HiFi) or --pacbio-raw (CLR)
#   hybrid   : Unicycler --mode bold (recommended) or SPAdes --nanopore/--pacbio,
#              short-read Pilon fill
# Optional: use Trycycler in the longread env for finished-grade multi-assembly
#   consensus (see the commented block at the bottom)
# Unified output: 03_assembly/genomes/{id}.fasta (contigs < 200 nt removed)
# =============================================================================
set -euo pipefail
THREADS=16; MEM=128; MIN_CTG=200
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
SR="$PROJECT/01_qc/clean"                     # cleaned short reads
[[ -d "$PROJECT/02_decontam_reads/clean" ]] && SR="$PROJECT/02_decontam_reads/clean"
LR_DIR="$PROJECT/01_qc/long/clean"           # cleaned long reads (from 01b)
SHEET="$PROJECT/config/my_samples.csv"
OUT="$PROJECT/03_assembly"; mkdir -p "$OUT/run" "$OUT/genomes"
source "$(conda info --base)/etc/profile.d/conda.sh"

polish_pilon () {  # $1=asm to polish $2=R1 $3=R2 $4=outdir/prefix
  local asm=$1 r1=$2 r2=$3 pre=$4
  bwa index "$asm"
  bwa mem -t "$THREADS" "$asm" "$r1" "$r2" | samtools view -Sb - \
      | samtools sort -@ "$THREADS" -o "$pre.bam"
  samtools index "$pre.bam"
  # bioconda pilon is an executable wrapper; for the jar use java -jar pilon.jar
  pilon --genome "$asm" --frags "$pre.bam" --fix all --changes \
        --threads "$THREADS" --output "${pre}_pilon" --outdir "$(dirname "$pre")"
}

racon_rounds () {   # $1=asm $2=long reads $3=out $4=rounds (default 2)
  local asm=$1 reads=$2 out=$3 rounds=${4:-2} cur=$asm
  for ((i=1;i<=rounds;i++)); do
    minimap2 -ax map-ont -t "$THREADS" "$cur" "$reads" > "$OUT/run/tmp_$i.sam"
    racon -t "$THREADS" "$reads" "$OUT/run/tmp_$i.sam" "$cur" > "$OUT/run/racon_$i.fasta"
    cur="$OUT/run/racon_$i.fasta"; rm -f "$OUT/run/tmp_$i.sam"
  done
  cp "$cur" "$out"
}

tail -n +2 "$SHEET" | while IFS=',' read -r id platform species r1 r2 lr rest; do
  [[ -z "$id" || "$id" == \#* ]] && continue
  wd="$OUT/run/$id"; mkdir -p "$wd"; echo ">>> assemble $id [$platform]"
  case "$platform" in
    illumina)
      # Short-read isolate: Unicycler first; switch to spades.py --isolate for large/complex sets
      unicycler -1 "$SR/${id}_R1.fq.gz" -2 "$SR/${id}_R2.fq.gz" \
                -o "$wd" -t "$THREADS" --min_fasta_length "$MIN_CTG"
      cp "$wd/assembly.fasta" "$OUT/genomes/${id}.fasta"
      # Fallback: spades.py --isolate -1 R1 -2 R2 -o wd -t T -m MEM && cp wd/scaffolds.fasta ;;
      ;;
    nanopore|pacbio)
      conda activate easywgs
      L="$LR_DIR/${id}_L.fq.gz"; [[ -f "$L" ]] || L="$PROJECT/$lr"
      if [[ "$platform" == "pacbio" ]]; then
        flye --pacbio-hifi "$L" --genome-size 5m --threads "$THREADS" --out-dir "$wd/flye"
      else
        flye --nano-hq "$L" --genome-size 5m --threads "$THREADS" --out-dir "$wd/flye"
      fi
      # Two Racon rounds (long-read self-correction; do not over-iterate)
      racon_rounds "$wd/flye/assembly.fasta" "$L" "$wd/racon.fasta" 2
      # Medaka consensus polish (separate env; pick the -m model matching r941/r1041 flowcell)
      conda activate longread
      medaka_consensus -i "$L" -d "$wd/racon.fasta" -o "$wd/medaka" -t "$THREADS" \
                       -m r1041_e82_400bps_sup_v4.2.0
      conda deactivate
      cp "$wd/medaka/consensus.fasta" "$OUT/genomes/${id}.raw.fasta" 2>/dev/null \
        || cp "$wd/racon.fasta" "$OUT/genomes/${id}.raw.fasta"
      seqkit seq -m "$MIN_CTG" "$OUT/genomes/${id}.raw.fasta" > "$OUT/genomes/${id}.fasta"
      ;;
    hybrid)
      conda activate easywgs
      L="$LR_DIR/${id}_L.fq.gz"; [[ -f "$L" ]] || L="$PROJECT/$lr"
      # Recommended: Unicycler bold, long reads scaffold and short reads correct, plasmid/circle friendly
      unicycler --mode bold -1 "$SR/${id}_R1.fq.gz" -2 "$SR/${id}_R2.fq.gz" -l "$L" \
                -o "$wd" -t "$THREADS" --min_fasta_length "$MIN_CTG" --keep 0
      # One extra short-read Pilon fill-and-fix pass
      polish_pilon "$wd/assembly.fasta" "$SR/${id}_R1.fq.gz" "$SR/${id}_R2.fq.gz" "$wd/pilon"
      cp "$wd/pilon_pilon.fasta" "$OUT/genomes/${id}.fasta" 2>/dev/null \
        || cp "$wd/assembly.fasta" "$OUT/genomes/${id}.fasta"
      # Fallback (SPAdes hybrid): spades.py --isolate -1 R1 -2 R2 --nanopore L -o wd2 -t T -m MEM
      ;;
    *) echo "Unknown platform=$platform (expected illumina/nanopore/pacbio/hybrid)"; continue ;;
  esac
  # Remove short contigs uniformly (if not already done upstream) and collect stats
  seqkit seq -m "$MIN_CTG" "$OUT/genomes/${id}.fasta" > "$OUT/genomes/${id}.tmp" \
    && mv "$OUT/genomes/${id}.tmp" "$OUT/genomes/${id}.fasta"
done

seqkit stats -a -T -j "$THREADS" "$OUT/genomes"/*.fasta > "$OUT/genome_stats.tsv"
# Circularity: Flye -> run/*/flye/assembly_info.txt (circ=Y); Unicycler log mentions circular
# Finished-grade (optional): conda activate longread; trycycler cluster/reconcile/msa/partition/consensus
echo "[done] unified assemblies: $OUT/genomes/{id}.fasta; stats: genome_stats.tsv"
