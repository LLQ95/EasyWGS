#!/usr/bin/env bash
# =============================================================================
# 10_treetime/10.treetime.sh —— 时间标定系统发育（分子钟）与祖先/同源分析
# 上游：09_phylogeny 的 clean.core.aln（核心SNP比对）与 core_iqtree.treefile（树）
# 元数据：config/metadata_dates.csv（name,date 采样时间）；地理/表型可选 states.csv
# 时间树要求采样时间跨度足够（克隆流行病原，通常需数年跨度与足够样本量）
# =============================================================================
set -euo pipefail
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
P9="$PROJECT/09_phylogeny"
OUT="$PROJECT/10_treetime"; mkdir -p "$OUT"
DATES="$PROJECT/config/metadata_dates.csv"
TREE="$P9/core_iqtree.treefile"
ALN="$P9/clean.core.aln"
COAL=${COAL:-skyline}        # constant / skyline；样本多、群体变化明显用 skyline

# ---- 1) root-to-tip 回归：评估分子钟信号、识别时间离群株 ----
treetime clock --tree "$TREE" --dates "$DATES" --aln "$ALN" \
        --clock-filter 4 --reroot least-squares --outdir "$OUT/01_clock"
# --clock-filter 4：剔除偏离回归>4倍MAD的离群点；检查 01_clock/rtt.csv 后可收紧重跑

# ---- 2) 时间树主分析：估计替换速率、分歧时间、祖先节点日期 ----
treetime --tree "$TREE" --dates "$DATES" --aln "$ALN" \
        --coalescent "$COAL" --outdir "$OUT/02_timetree"
# 关键产物：
#   02_timetree/timetree.nexus     带节点日期与年份分支长度的树
#   02_timetree/divergence_table.csv、rates.csv、rerooting*.pdf(root-to-tip图)

# ---- 3) 祖先序列重建与突变标注（把 A45G 这类突变映射到分支）----
treetime ancestral --aln "$ALN" --tree "$OUT/02_timetree/timetree.nexus" \
        --outdir "$OUT/03_ancestral"

# ---- 4) 同源突变(homoplasy)扫描：过量同源提示重组/污染/传代适应 ----
treetime homoplasy --aln "$ALN" --tree "$OUT/02_timetree/timetree.nexus" \
        --outdir "$OUT/04_homoplasy"
# 重点看 04_homoplasy/ambiguous.tsv、homoplasy_scores.tsv，与04污染门控交叉核对

# ---- 5)（可选）离散状态“迁移”：地理来源/表型/血清型在树上的演化 ----
if [[ -f "$PROJECT/config/states.csv" ]]; then
  for attr in country phenotype serotype; do
    treetime mugration --tree "$OUT/02_timetree/timetree.nexus" \
             --states "$PROJECT/config/states.csv" --attribute "$attr" \
             --outdir "$OUT/05_mugration_$attr" || true
  done
fi
# states.csv 格式：name,country,phenotype,serotype（一行一样本）
echo "[完成] 时间树 $OUT/02_timetree/timetree.nexus；可视化用 FigTree/icytree 打开"
