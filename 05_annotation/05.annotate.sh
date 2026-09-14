#!/usr/bin/env bash
# =============================================================================
# 05_annotation/05.annotate.sh —— 结构与功能注释
# Prokka(快) 或 Bakta(全,推荐) 批量注释；Prodigal 产蛋白；eggNOG 做 GO/KEGG/COG
# 下游 Panaroo/roary 需要注释产生的 gff，因此本模块是 08 的前置
# =============================================================================
set -euo pipefail
THREADS=8
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
GEN="$PROJECT/03_assembly/genomes"
OUT="$PROJECT/05_annotation"
DBROOT=${DBROOT:-$HOME/EasyIsolate_db}
mkdir -p "$OUT/prokka" "$OUT/prodigal_faa" "$OUT/bakta" "$OUT/eggnog"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate easyisolate

# ---- 1) Prokka 批量注释（--genus 可按样本改；这里用 Bacteria 通用）----
for f in "$GEN"/*.fasta; do
  id=$(basename "$f" .fasta)
  prokka --outdir "$OUT/prokka/$id" --prefix "$id" --cpus "$THREADS" \
         --addgenes --centre EasyIsolate --compliant "$f"
done

# ---- 2) Prodigal 预测蛋白（供 eggNOG / 自建库）----
for f in "$GEN"/*.fasta; do
  id=$(basename "$f" .fasta)
  prodigal -i "$f" -a "$OUT/prodigal_faa/${id}.faa" \
           -d "$OUT/prodigal_faa/${id}.ffn" -o "$OUT/prodigal_faa/${id}.gff" -f gff -p single
done

# ---- 3) Bakta 全量注释（推荐，注释更全；独立环境）----
conda activate bakta
for f in "$GEN"/*.fasta; do
  id=$(basename "$f" .fasta)
  bakta --db "$DBROOT/bakta_db" --output "$OUT/bakta/$id" --prefix "$id" \
        --threads "$THREADS" "$f"
done
conda deactivate

# ---- 4) eggNOG-mapper：GO/KEGG/COG/EC（输入蛋白 faa）----
conda activate eggnog
for faa in "$OUT/prodigal_faa"/*.faa; do
  id=$(basename "$faa" .faa)
  emapper.py -i "$faa" --data_dir "$DBROOT/eggnog_db" --cpu "$THREADS" \
             -m diamond --override -o "$OUT/eggnog/$id"
done
conda deactivate
echo "[完成] 注释结果：$OUT/prokka（gff供泛基因组）、$OUT/eggnog（功能注释）"
