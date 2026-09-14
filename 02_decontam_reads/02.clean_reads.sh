#!/usr/bin/env bash
# =============================================================================
# 02_decontam_reads/02.clean_reads.sh - read-level decontamination (pre-assembly)
# Strategy: (optional) Kraken2 scout for contaminant composition, then CLEAN to
#   remove host / PhiX / known contaminants
# CLEAN is a Nextflow workflow; brace the {1,2} glob in --input with quotes so
#   that nextflow (not the local shell) expands it
# =============================================================================
set -euo pipefail
THREADS=8
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
IN="$PROJECT/01_qc/clean"
OUT="$PROJECT/02_decontam_reads"
K2DB=${K2DB:-$HOME/EasyIsolate_db/k2_standard}     # skip scouting without a Kraken DB
HOST="hsa"                                          # host: human hsa for clinical/stool; set "" for none
CONTROL="phix"                                      # Illumina PhiX control (use dcs for ONT)
# OWN_REF="$PROJECT/02_decontam_reads/known_contam.fa"     # known contaminant reference (optional)
# KEEP_REF="$PROJECT/02_decontam_reads/target_relative.fa" # close-target whitelist, anti-false-removal (optional)
mkdir -p "$OUT/screen" "$OUT/clean_work"

# ---- Step A (optional): Kraken2+Bracken scout, report only, do not remove ----
if [[ -d "$K2DB" ]]; then
  for r1 in "$IN"/*_R1.fq.gz; do
    id=$(basename "$r1" _R1.fq.gz)
    kraken2 --db "$K2DB" --paired --threads "$THREADS" \
            --report "$OUT/screen/${id}.k2report.txt" \
            "$IN/${id}_R1.fq.gz" "$IN/${id}_R2.fq.gz" > /dev/null
    bracken -d "$K2DB" -i "$OUT/screen/${id}.k2report.txt" \
            -o "$OUT/screen/${id}.bracken.tsv" -r 150 -l S || true
  done
  echo "Inspect composition: column -t -s\$'\t' <bracken file> | sort -k7 -nr | head -20"
fi

# ---- Step B: CLEAN batch removal ----
for r1 in "$IN"/*_R1.fq.gz; do
  id=$(basename "$r1" _R1.fq.gz)
  echo ">>> CLEAN: $id"
  ARGS=(--input_type illumina
        --input "$IN/${id}_R{1,2}.fq.gz"
        --control "$CONTROL"
        --output "$OUT/clean_work/$id"
        -work-dir "$OUT/clean_work/$id/work" -profile docker -resume)
  [[ -n "$HOST" ]] && ARGS+=(--host "$HOST")
  [[ -n "${OWN_REF:-}" ]]  && ARGS+=(--own "$OWN_REF")
  [[ -n "${KEEP_REF:-}" ]] && ARGS+=(--keep "$KEEP_REF")
  nextflow run rki-mf1/clean -r v1.1.0 "${ARGS[@]}"
done

# Collect every sample's cleaned reads into one directory
mkdir -p "$OUT/clean"
find "$OUT/clean_work" -path "*/clean/*.fq.gz" -exec cp {} "$OUT/clean/" \;
echo "[done] decontaminated reads: $OUT/clean; removed: per-sample removed/; QC: qc/multiqc_report.html"
