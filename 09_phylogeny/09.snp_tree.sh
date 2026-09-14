#!/usr/bin/env bash
# =============================================================================
# 09_phylogeny/09.snp_tree.sh —— 参考依赖的核心 SNP 系统发育
#   snippy 多样本比对统一参考 -> snippy-core 拼合 -> Gubbins 去重组
#   -> snp-sites 提恒定SNP -> IQ-TREE/FastTree 建树 -> snp-dists SNP距离矩阵
# reference 取 samplesheet.csv 的 reference 列（全批次同一参考，推荐近缘完成图, gbk/fasta）
# =============================================================================
set -euo pipefail
THREADS=8
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
GEN="$PROJECT/03_assembly/genomes"
OUT="$PROJECT/09_phylogeny"; mkdir -p "$OUT/snippy"
SHEET="$PROJECT/config/my_samples.csv"
REF=$(awk -F',' 'NR==2{print $6}' "$SHEET")      # 统一参考
[[ -f "$PROJECT/$REF" ]] && REF="$PROJECT/$REF"
echo "使用参考: $REF"

# ---- 1) 用组装(也可用reads)逐样本对参考调用变异 ----
DIRS=()
while IFS=',' read -r id species r1 r2 rest; do
  [[ "$id" == "id" || "$id" == \#* || -z "$id" ]] && continue
  d="$OUT/snippy/$id"
  if [[ ! -d "$d" ]]; then
    snippy --cpus "$THREADS" --outdir "$d" --ref "$REF" --ctgs "$GEN/${id}.fasta"
    # 若直接用 reads：snippy --ref REF --R1 r1 --R2 r2
  fi
  DIRS+=("$d")
done < "$SHEET"

# ---- 2) 拼合全样本核心比对 ----
cd "$OUT"
snippy --cpus "$THREADS" --ref "$REF" --outdir core --cleanup "${DIRS[@]}"
# 产出 core.full.aln（含不变位点）与 core.aln（仅SNP）

# ---- 3) Gubbins 检测并屏蔽重组区 ----
run_gubbins.py --threads "$THREADS" --tree-builder iqtree --prefix gubbins core/core.full.aln

# ---- 4) 提取去重组后的核心SNP并建树 ----
snp-sites -c gubbins.filtered_polymorphic_sites.fasta > clean.core.aln
iqtree2 -s clean.core.aln -m GTR+G4 -alrt 1000 -bb 1000 -nt AUTO -pre core_iqtree
# 快速替代：FastTree -gtr -nt clean.core.aln > core_fasttree.tre

# ---- 5) 两两 SNP 距离矩阵（用于聚类阈值，如沙门5/10/20 SNP）----
snp-dists -j "$THREADS" clean.core.aln > snp_dists.tsv
echo "[完成] 树：$OUT/core_iqtree.treefile；SNP矩阵：$OUT/snp_dists.tsv；供10_treetime"
