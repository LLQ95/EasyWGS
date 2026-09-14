#!/usr/bin/env bash
# =============================================================================
# 01_qc/01b.long_qc.sh - long-read (ONT/PacBio) QC: adapter removal -> QC plot
#   -> quality/length filtering
# Input : the longreads column for rows whose platform is nanopore/pacbio/hybrid
# Note  : long reads must be adapter-trimmed first; NanoPlot shows length/quality
#   distributions and Filtlong keeps high-quality reads
# =============================================================================
set -euo pipefail
THREADS=16
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
SHEET="$PROJECT/config/my_samples.csv"
OUT="$PROJECT/01_qc/long"; mkdir -p "$OUT"/{raw_nanoplot,trim,clean}

# ONT quality thresholds (loosen/tighten as needed)
MIN_LEN=1000          # minimum retained read length
MIN_QUAL=7            # minimum mean read quality (Q7 ~ 80% accuracy; raise to 12 for HiFi)
KEEP=400000000        # filtlong target bases (~80x of a 5 Mb genome); 0 disables targeting

tail -n +2 "$SHEET" | while IFS=',' read -r id platform species r1 r2 lr rest; do
  [[ -z "$id" || "$id" == \#* ]] && continue
  case "$platform" in
    nanopore|pacbio|hybrid) ;;
    *) continue ;;
  esac
  L="$PROJECT/$lr"; [[ -f "$L" ]] || { echo "Long reads missing: $L, skip $id"; continue; }
  echo ">>> long-read QC $id ($platform)"

  # 1) QC plot of raw reads
  NanoPlot --threads "$THREADS" -t "$L" -o "$OUT/raw_nanoplot/$id" --prefix raw_ || true

  # 2) Adapter removal (porechop; single-end fastp also works: fastp -i in -o out)
  porechop -i "$L" -o "$OUT/trim/${id}.trim.fq.gz" --threads "$THREADS"

  # 3) Filter by length+quality; --target_bases keeps the best reads by total bases
  if [[ "$KEEP" -gt 0 ]]; then
    filtlong --min_length "$MIN_LEN" --min_mean_q "$MIN_QUAL" \
             --target_bases "$KEEP" "$OUT/trim/${id}.trim.fq.gz" \
             | gzip > "$OUT/clean/${id}_L.fq.gz"
  else
    filtlong --min_length "$MIN_LEN" --min_mean_q "$MIN_QUAL" \
             "$OUT/trim/${id}.trim.fq.gz" | gzip > "$OUT/clean/${id}_L.fq.gz"
  fi

  # 4) Plot again after filtering for before/after comparison
  NanoPlot --threads "$THREADS" -t "$OUT/clean/${id}_L.fq.gz" \
           -o "$OUT/raw_nanoplot/$id" --prefix clean_ || true
done
echo "[done] cleaned long reads: $OUT/clean/{id}_L.fq.gz (consumed by module 03)"
