#!/usr/bin/env bash
# =============================================================================
# 06_typing/06.3.cgmlst.sh —— chewBBACA 核心基因组多位点序列分型(cgMLST)
# 流程：CreateSchema/PrepExternalSchema 建方案 -> AlleleCall 等位基因判定
#       -> ExtractCgMLST 提取cgMLST矩阵 -> AlleleCallEvaluator 质量评估
# 输出 cgMLST 等位基因矩阵，可直接喂 GrapeTree / PHYLOViZ 画最小生成树
# =============================================================================
set -euo pipefail
THREADS=8
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
GEN="$PROJECT/03_assembly/genomes"
OUT="$PROJECT/06_typing/cgmlst"; mkdir -p "$OUT"
DBROOT=${DBROOT:-$HOME/EasyIsolate_db/chewie}

# 按研究类群选择 cgMLST schema（samplesheet 的 species 决定）
# schema 来源见 00_install/download_db.sh：INNUENDO(沙门) / Pasteur(李斯特) /
# EnteroBase Escherichia-Shigella(大肠志贺) / 肺克公开等位库
pick_schema () {
  case "$1" in
    salm)     echo "$DBROOT/salmonella/Salmonella_enterica_INNUENDO_cgMLST" ;;
    listeria) echo "$DBROOT/listeria/Listeria_monocytogenes_Pasteur_cgMLST" ;;
    ecoli)    echo "$DBROOT/ecoli/Escherichia_Shigella_EnteroBase_cgMLST" ;;
    kpsc)     echo "$DBROOT/kpsc/Klebsiella_cgMLST" ;;
    *)        echo "" ;;
  esac
}

while IFS=',' read -r id species rest; do
  [[ "$id" == "id" || "$id" == \#* || -z "$id" ]] && continue
  schema=$(pick_schema "$species")
  [[ -z "$schema" || ! -d "$schema" ]] && { echo "[$id] 无 $species 的 cgMLST schema，跳过(可用 PrepExternalSchema 自建)"; continue; }
  wd="$OUT/$species"; mkdir -p "$wd"
  echo ">>> cgMLST $id ($species) <- $schema"
  chewBBACA.py AlleleCall -i "$GEN" -g "$schema" -o "$wd/AlleleCall" \
               --cpu "$THREADS" --mode 1
  chewBBACA.py ExtractCgMLST -i "$wd/AlleleCall/results_alleles.tsv" -o "$wd/ExtractCgMLST"
  chewBBACA.py AlleleCallEvaluator -i "$wd/AlleleCall" -g "$schema" \
               -o "$wd/AlleleCallEvaluator" --cpu "$THREADS"
done < "$PROJECT/config/my_samples.csv"

# 若手头只有一组 fasta 等位库而无现成 schema，先用下面命令外部方案适配一次：
# chewBBACA.py PrepExternalSchema -g raw_alleles -o built_schema --cpu 16
# cgMLST 矩阵($OUT/*/ExtractCgMLST/cgMLST.tsv)导入 GrapeTree 画 MST：
# grapetree pg -i cgMLST.tsv -o cgmlst_tree.nw
echo "[完成] cgMLST：$OUT/<species>/ExtractCgMLST/cgMLST.tsv（GrapeTree 出图）"
