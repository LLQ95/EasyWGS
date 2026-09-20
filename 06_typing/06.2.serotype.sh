#!/usr/bin/env bash
# =============================================================================
# 06_typing/06.2.serotype.sh - species-specific serotype/surface-antigen typing,
#   dispatched by samplesheet.species
#   kpsc     : Kleborate (built-in Kaptive; K/O antigens, ST, resistance/virulence scores)
#   ecoli    : ECTyper (O:H antigens, species, stx) + ShigEiFinder (Shigella/EIEC)
#   salm     : SeqSero2 (O/H) + SISTR (serovar prediction, includes cgMLST)
#   listeria : molecular serogroup placeholder (main typing via 06.3 cgMLST)
#   vibrio/yersinia/campylobacter/burkholderia/clostridium: no single CLI serotyper;
#     MLST (06.1) plus the custom surface/toxin marker screen (06.4)
# Note: Kleborate v3 uses -p presets; v2 is equivalent to kleborate --all
# =============================================================================
set -euo pipefail
THREADS=8
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
GEN="$PROJECT/03_assembly/genomes"
OUT="$PROJECT/06_typing/serotype"; mkdir -p "$OUT"
SHEET="$PROJECT/config/my_samples.csv"

while IFS=',' read -r id platform species r1 r2 lr ref date country pheno; do
  [[ "$id" == "id" || "$id" == \#* || -z "$id" ]] && continue
  f="$GEN/${id}.fasta"; [[ -f "$f" ]] || { echo "Assembly missing: $f"; continue; }
  echo ">>> $id [$species]"
  case "$species" in
    kpsc)
      # K. pneumoniae complex: Kleborate v3 (Kaptive K capsule / O LPS loci)
      mkdir -p "$OUT/kleborate"
      kleborate -a "$f" -o "$OUT/kleborate/${id}" -p kpsc --trim_headers --threads "$THREADS"
      # For standalone detailed Kaptive K/O loci (Kaptive v3):
      # kaptive get-loci --kaptive-table / kaptive assembly KpSC ... see --help
      ;;
    ecoli)
      mkdir -p "$OUT/ectyper" "$OUT/shigeifinder"
      ectyper -i "$f" -o "$OUT/ectyper/$id" --cores "$THREADS"
      # Shigella / EIEC typing (assembly mode; paired reads accept -1/-2)
      shigeifinder -i "$f" -o "$OUT/shigeifinder/${id}.tsv" --threads "$THREADS" || \
        echo "  ShigEiFinder flags vary by version; check shigeifinder --help"
      ;;
    salm)
      mkdir -p "$OUT/seqsero2" "$OUT/sistr"
      # -m k = assembly (k-mer) mode; use -m allele for read input
      SeqSero2_package.py -m k -t "$THREADS" -i "$f" -d "$OUT/seqsero2/$id"
      sistr -i "$f" -f csv -o "$OUT/sistr/${id}.csv" -p CGMLST_PROFILES -n NOVEL_ALLELES
      ;;
    listeria)
      echo "  Classical Listeria serotyping is limited; molecular typing is in 06.3.cgmlst.sh (Pasteur schema)" ;;
    vibrio|yersinia|campylobacter|burkholderia|clostridium)
      # No single maintained command-line serotyper for these groups. Module 06.1
      # gives the MLST sequence type and module 06.4 screens the easywgs_markers
      # database for surface-antigen loci, toxin genes and virulence markers.
      echo "  no dedicated CLI serotyper; see 06.1 (MLST) and 06.4 (surface/toxin loci)" ;;
    other)
      echo "  other: serotyping skipped; extend with abricate as needed" ;;
    *) echo "  Unknown species=$species (expected kpsc/ecoli/salm/listeria/other)" ;;
  esac
done < "$SHEET"

# Merge per-tool outputs
cat "$OUT"/kleborate/*/*.txt 2>/dev/null | awk '!a[$1]++' > "$OUT/Kleborate_all.tsv" || true
find "$OUT/ectyper" -name output.csv -exec cat {} \; 2>/dev/null | awk '!a[$0]++' > "$OUT/ECTyper_all.csv" || true
find "$OUT/sistr"  -name '*.csv'      -exec cat {} \; 2>/dev/null > "$OUT/SISTR_all.csv" || true
echo "[done] serotyping: $OUT (per-tool subdirs; *_all are merged tables)"
