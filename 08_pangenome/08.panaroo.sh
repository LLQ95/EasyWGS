#!/usr/bin/env bash
# =============================================================================
# 08_pangenome/08.panaroo.sh —— 泛基因组（推荐 Panaroo，去污染更严；Roary 兼容备用）
# 输入：05_annotation/prokka 下各样本 gff；输出核心/附属基因表与核心基因多序列比对
# 核心比对供 09 建立核心基因树（与 SNP 树互为印证）
# =============================================================================
set -euo pipefail
THREADS=8
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
GFF_DIR="$PROJECT/05_annotation/prokka"
OUT="$PROJECT/08_pangenome"; mkdir -p "$OUT/panaroo_in"

# Panaroo 需要每个样本一个目录，内含同名 gff（prokka 已满足），这里收集 gff 列表
find "$GFF_DIR" -name "*.gff" | sort > "$OUT/gff_list.txt"

# ---- 1) Panaroo 严格模式（适合同一物种、克隆结构强的菌群）----
panaroo -i $(tr '\n' ' ' < "$OUT/gff_list.txt") -o "$OUT/panaroo" \
        --clean-mode strict --remove-invalid-genes --threads "$THREADS" -a core

# ---- 2) 核心基因组多序列比对（core_only），供建树 ----
panaroo-msa --pan_dir "$OUT/panaroo" --outdir "$OUT/core_msa" \
            --core_only --n_cpu "$THREADS"
# 由核心比对直接建一棵核心基因树（可选）
iqtree2 -s "$OUT/core_msa/core_gene_alignment.aln" -m GTR+G4 \
        -alrt 1000 -bb 1000 -nt "$THREADS" -pre "$OUT/core_gene_tree"

# ---- 3)（备选）Roary 流程，与 Panaroo 不兼容，需独立环境 ----
# roary -p "$THREADS" -e --mafft -r -f "$OUT/roary" $(tr '\n' ' ' < "$OUT/gff_list.txt")
# roary_plots.py "$OUT/roary/core_SNP_tree.tre" "$OUT/roary/gene_presence_absence.csv"

# ---- 4) 基因存在缺失关联表型（scoary）与基因耦合（coinfinder，可选）----
# scoary -g "$OUT/panaroo/gene_presence_absence.csv" -t config/phenotype.csv -n tree.nwk
echo "[完成] 泛基因组：$OUT/panaroo（gene_presence_absence.csv）；核心比对：core_msa/"
