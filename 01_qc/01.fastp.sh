#!/usr/bin/env bash
# =============================================================================
# 01_qc/01.fastp.sh —— 原始 reads 质控（去接头、滑窗质量裁剪、过短过滤）
# 输入：00_rawdata/{id}_R1.fastq.gz / {id}_R2.fastq.gz
# 输出：01_qc/clean/{id}_R{1,2}.fq.gz 及 html/json 报告
# =============================================================================
set -euo pipefail
THREADS=8
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}   # 自动定位到 EasyIsolate 根目录
RAW="$PROJECT/00_rawdata"
OUT="$PROJECT/01_qc/clean"
mkdir -p "$OUT"

# 按样本前缀（去掉 _R1/_R2）批量循环
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

# FastQC + MultiQC 汇总（可选）
fastqc -t "$THREADS" "$OUT"/*.fq.gz -o "$OUT"
multiqc "$OUT" -o "$PROJECT/01_qc" -n 01_multiqc.html
echo "[完成] 干净 reads 在 $OUT，总览见 01_qc/01_multiqc.html"
