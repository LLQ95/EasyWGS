#!/usr/bin/env bash
# =============================================================================
# 02_decontam_reads/02.clean_reads.sh —— reads 层去污染（组装前）
# 思路：先(可选)Kraken2 侦察污染构成 → 用 CLEAN 剔除宿主/PhiX/已知污染
# CLEAN 为 Nextflow 流程；其 --input 的 {1,2} 通配必须加引号交给 nextflow 解析
# =============================================================================
set -euo pipefail
THREADS=8
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
IN="$PROJECT/01_qc/clean"
OUT="$PROJECT/02_decontam_reads"
K2DB=${K2DB:-$HOME/EasyIsolate_db/k2_standard}     # 无 Kraken 库则跳过侦察
HOST="hsa"                                          # 宿主：临床/粪便常为人源 hsa；无宿主改成空 ""
CONTROL="phix"                                      # Illumina 内对照 PhiX（ONT 改 dcs）
# OWN_REF="$PROJECT/02_decontam_reads/known_contam.fa"   # 侦察后已知污染菌参考(可选)
# KEEP_REF="$PROJECT/02_decontam_reads/target_relative.fa" # 目标近缘白名单,防误删(可选)
mkdir -p "$OUT/screen" "$OUT/clean_work"

# ---- 步骤A（可选）：Kraken2+Bracken 侦察，只报告不删除 ----
if [[ -d "$K2DB" ]]; then
  for r1 in "$IN"/*_R1.fq.gz; do
    id=$(basename "$r1" _R1.fq.gz)
    kraken2 --db "$K2DB" --paired --threads "$THREADS" \
            --report "$OUT/screen/${id}.k2report.txt" \
            "$IN/${id}_R1.fq.gz" "$IN/${id}_R2.fq.gz" > /dev/null
    bracken -d "$K2DB" -i "$OUT/screen/${id}.k2report.txt" \
            -o "$OUT/screen/${id}.bracken.tsv" -r 150 -l S || true
  done
  echo "查看污染构成：column -t -s\$'\t' <bracken文件> | sort -k7 -nr | head -20"
fi

# ---- 步骤B：CLEAN 批量剔除 ----
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

# 汇总所有样本的 clean reads 到统一目录
mkdir -p "$OUT/clean"
find "$OUT/clean_work" -path "*/clean/*.fq.gz" -exec cp {} "$OUT/clean/" \;
echo "[完成] 去污染 reads：$OUT/clean；被剔除：各样本 removed/；质控：qc/multiqc_report.html"
