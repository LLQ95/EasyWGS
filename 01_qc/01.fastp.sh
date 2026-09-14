#!/usr/bin/env bash
# =============================================================================
# 01_qc/01.fastp.sh - raw-read QC (adapter trim, sliding-window quality trim,
#   short-read filtering)
# Input : 00_rawdata/{id}_R1.fastq.gz / {id}_R2.fastq.gz
# Output: 01_qc/clean/{id}_R{1,2}.fq.gz plus html/json reports
# =============================================================================
set -euo pipefail
THREADS=8
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}   # resolve easyWGS root
RAW="$PROJECT/00_rawdata"
OUT="$PROJECT/01_qc/clean"
mkdir -p "$OUT"

# Loop over sample prefixes (strip _R1/_R2)
for r1 in "$RAW"/*_R1.fastq.gz; do
  id=$(basename "$r1" _R1.fastq.gz)
  echo ">>> fastp: $id"
  fastp -i "$RAW/${id}_R1.fastq.gz" -I "$RAW/${id}_R2.fastq.gz" \
        -o "$OUT/${id}_R1.fq.gz"    -O "$OUT/${id}_R2.fq.gz" \
        -h "$OUT/${id}.fastp.html"  -j "$OUT/${id}.fastp.json" \
        --detect_adapter_for_pe --correction --cut_tail \
        --qualified_quality_phred 20 --length_required 50 \
        --thread "$THREADS"
done

# FastQC + MultiQC summary (optional)
fastqc -t "$THREADS" "$OUT"/*.fq.gz -o "$OUT"
multiqc "$OUT" -o "$PROJECT/01_qc" -n 01_multiqc.html
echo "[done] cleaned reads in $OUT; overview at 01_qc/01_multiqc.html"
