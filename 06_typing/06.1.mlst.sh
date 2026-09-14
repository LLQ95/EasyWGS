#!/usr/bin/env bash
# =============================================================================
# 06_typing/06.1.mlst.sh —— 7基因传统 MLST（PubMLST 方案，自动识别物种）
# 输入组装 fasta；输出全样本合并的 pubmlst.tab（第2列为方案，第3列为ST）
# =============================================================================
set -euo pipefail
THREADS=8
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
GEN="$PROJECT/03_assembly/genomes"
OUT="$PROJECT/06_typing"; mkdir -p "$OUT/mlst"

# 单样本逐个跑，结果带文件名，便于回溯
: > "$OUT/mlst/pubmlst.tab"
for f in "$GEN"/*.fasta; do
  mlst --threads "$THREADS" "$f" >> "$OUT/mlst/pubmlst.tab"
done
column -t "$OUT/mlst/pubmlst.tab" | less -S || true
# 更新离线库（周期性）：mlst-download_pub_mlst -j 8 -d <env>/db/pubmlst
# 查看支持的方案：mlst --long | less
echo "[完成] MLST：$OUT/mlst/pubmlst.tab（字段：文件 方案 ST 7个等位基因）"
