#!/usr/bin/env bash
# =============================================================================
# 12_mapping_pipeline/12.1.map_reads.sh
# Reference-based (mapping) route: align cleaned reads to ONE shared reference
# and produce sorted/indexed BAM files plus per-sample coverage statistics.
#   Illumina : bwa mem (paired-end short reads)
#   ONT/PacBio: minimap2 -ax map-ont / map-pb (long reads)
# This route runs in parallel with the de novo assembly route (module 03);
# it does not consume assemblies and does not require them to exist.
#
# Input : config/my_samples.csv (id,platform,R1,R2,longreads,reference,...)
# Output: 12_mapping_pipeline/bam/{id}.sorted.bam(.bai)
#         12_mapping_pipeline/qc/{id}.flagstat, {id}.depth, coverage_summary.tsv
# =============================================================================
set -euo pipefail
THREADS=8
MIN_BREADTH=0.9          # flag assemblies/alignments whose covered fraction is below this
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
SHEET="$PROJECT/config/my_samples.csv"
OUT="$PROJECT/12_mapping_pipeline"; mkdir -p "$OUT/bam" "$OUT/qc"

# Resolve a column index from the samplesheet header by its name (robust to column order)
colnum () { head -1 "$SHEET" | tr ',' '\n' | grep -n -x "$1" | cut -d: -f1; }
C_ID=$(colnum id); C_PLAT=$(colnum platform); C_R1=$(colnum R1); C_R2=$(colnum R2)
C_LONG=$(colnum longreads); C_REF=$(colnum reference)

REF=$(awk -F',' -v c="$C_REF" 'NR==2{print $c}' "$SHEET")
[[ -f "$PROJECT/$REF" ]] && REF="$PROJECT/$REF"
[[ -f "$REF" ]] || { echo "Reference not found ($REF). The mapping route needs a single FASTA reference."; exit 1; }
case "$REF" in *.gb|*.gbk|*.gff) echo "BWA/minimap2 need a FASTA reference, not GenBank: $REF"; exit 1;; esac
echo "Shared reference: $REF"

# Index once (idempotent): samtools .fai and bwa .bwt
samtools faidx "$REF"
[[ -f "${REF}.bwt" ]] || bwa index "$REF"

SUMMARY="$OUT/qc/coverage_summary.tsv"
echo -e "id\tplatform\tmean_depth\tbreadth_ge1x\tbreadth_ge10x\tmapped_pct" > "$SUMMARY"

map_one () { # $1=id $2=platform $3=R1 $4=R2 $5=longreads
  local id=$1 plat=$2 r1=$3 r2=$4 long=$5 bam="$OUT/bam/${id}.sorted.bam"
  [[ -f "$bam" ]] && { echo "[skip] $bam exists"; return; }
  case "$plat" in
    illumina|hybrid)
      [[ -f "$PROJECT/$r1" && -f "$PROJECT/$r2" ]] || { echo "[warn] $id missing short reads, skip"; return; }
      bwa mem -t "$THREADS" -R "@RG\tID:$id\tSM:$id\tPL:ILLUMINA" "$REF" "$PROJECT/$r1" "$PROJECT/$r2" \
        | samtools sort -@ "$THREADS" -o "$bam" - ;;
    nanopore)
      [[ -f "$PROJECT/$long" ]] || { echo "[warn] $id missing long reads, skip"; return; }
      minimap2 -ax map-ont -t "$THREADS" -R "@RG\tID:$id\tSM:$id\tPL=ONT" "$REF" "$PROJECT/$long" \
        | samtools sort -@ "$THREADS" -o "$bam" - ;;
    pacbio)
      [[ -f "$PROJECT/$long" ]] || { echo "[warn] $id missing long reads, skip"; return; }
      minimap2 -ax map-pb -t "$THREADS" -R "@RG\tID:$id\tSM:$id\tPL=PACBIO" "$REF" "$PROJECT/$long" \
        | samtools sort -@ "$THREADS" -o "$bam" - ;;
    *) echo "[warn] unknown platform '$plat' for $id, skip"; return;;
  esac
  samtools index -@ "$THREADS" "$bam"
  samtools flagstat "$bam" > "$OUT/qc/${id}.flagstat"
  samtools depth -a -H "$bam" > "$OUT/qc/${id}.depth"     # per-base depth, all positions

  # Mean depth, breadth of coverage at >=1x and >=10x, and mapped-read percentage
  awk -v id="$id" -v plat="$plat" -v mb="$MIN_BREADTH" '
    {n++; d+=$3; if($3>=1)b1++; if($3>=10)b10++}
    END{ meand=(n?d/n:0); f1=(n?b1/n:0); f10=(n?b10/n:0);
         printf "%s\t%s\t%.2f\t%.4f\t%.4f\t", id,plat,meand,f1,f10 }' "$OUT/qc/${id}.depth" >> "$SUMMARY"
  grep -m1 'mapped (' "$OUT/qc/${id}.flagstat" \
    | awk '{gsub(/.*\(/,"",$0);gsub(/%.*/,"",$0);printf "%s\n",$0}' >> "$SUMMARY"
  if awk -v mb="$MIN_BREADTH" 'NR>1{exit !(($4+0)<mb)}' "$SUMMARY"; then
    echo "[warn] $id breadth below $(echo "$MIN_BREADTH"): check reference distance or coverage"
  fi
  # Optional duplicate removal (when samtools is recent enough):
  # samtools collate -@T -o - "$bam" | samtools fixmate -m - - | samtools sort -@T | samtools markdup - "${id}.dedup.bam"
  # Optional per-BAM QC report if Qualimap is installed:
  command -v qualimap >/dev/null 2>&1 && qualimap bamqc -bam "$bam" -nt "$THREADS" -outdir "$OUT/qc/${id}_qualimap" || true
}

while IFS=',' read -r row; do
  id=$(echo "$row" | awk -F',' -v c="$C_ID" '{print $c}')
  [[ "$id" == "id" || "$id" == \#* || -z "$id" ]] && continue
  plat=$(echo "$row" | awk -F',' -v c="$C_PLAT" '{print $c}')
  r1=$(echo "$row" | awk -F',' -v c="$C_R1" '{print $c}')
  r2=$(echo "$row" | awk -F',' -v c="$C_R2" '{print $c}')
  lo=$(echo "$row" | awk -F',' -v c="$C_LONG" '{print $c}')
  map_one "$id" "$plat" "$r1" "$r2" "$lo"
done < "$SHEET"

echo "[done] BAM files in $OUT/bam; coverage table: $SUMMARY"
