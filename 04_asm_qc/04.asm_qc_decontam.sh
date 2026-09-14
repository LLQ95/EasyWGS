#!/usr/bin/env bash
# =============================================================================
# 04_asm_qc/04.asm_qc_decontam.sh —— 组装评估 + assembly 层去污染门控
# QUAST 组装指标 / CheckM2 完整度污染度 / GUNC 嵌合 / (可选)FCS-GX 切除外源污染
# 门控规则：CheckM2 Contamination>5% 或 GUNC pass=False 列入 04_asm_qc/recheck.list
# =============================================================================
set -euo pipefail
THREADS=8
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
GEN="$PROJECT/03_assembly/genomes"
OUT="$PROJECT/04_asm_qc"; mkdir -p "$OUT/quast" "$OUT/checkm2" "$OUT/gunc"
DBROOT=${DBROOT:-$HOME/EasyIsolate_db}
GUNC_DB=$(ls "$DBROOT"/gunc_db/*progenomes*.dmnd 2>/dev/null | head -n1 || true)
source "$(conda info --base)/etc/profile.d/conda.sh"

# ---- QUAST ----
conda activate easyisolate
quast.py -t "$THREADS" -o "$OUT/quast" "$GEN"/*.fasta

# ---- CheckM2 ----
conda activate checkm2
checkm2 predict --threads "$THREADS" --input "$GEN" --output-directory "$OUT/checkm2" --force \
  --database_path "$DBROOT/checkm2_db/CheckM2_database/uniref100.KO.1.dmnd"
conda deactivate

# ---- GUNC ----
conda activate gunc
for f in "$GEN"/*.fasta; do
  id=$(basename "$f" .fasta)
  gunc run --input_fasta "$f" -r "$GUNC_DB" --out_dir "$OUT/gunc/$id" \
           --threads "$THREADS" --detailed_output --contig_taxonomy_output
done
# 汇总所有样本 maxCSS
find "$OUT/gunc" -name "GUNC.*maxCSS_level.tsv" -exec cat {} \; | awk '!a[$1]++' > "$OUT/gunc_all.tsv"
conda deactivate

# ---- (可选) FCS-GX 切除跨物种污染；需大内存机器与 taxid 表 ----
# samplesheet 增加 taxid 列后在此循环；无环境则把组装传 https://usegalaxy.org 在线跑：
FCS_PY=${FCS_PY:-$HOME/fcsgx/fcs.py}; GXDB=${GXDB:-$DBROOT/fcs_gx_db}
if [[ -f "$FCS_PY" && -d "$GXDB" ]]; then
  mkdir -p "$OUT/fcsgx"
  while IFS=',' read -r id species r1 r2 lr ref date country pheno taxid; do
    [[ "$id" == "id" || -z "${taxid:-}" ]] && continue
    python3 "$FCS_PY" screen genome --fasta "$GEN/${id}.fasta" \
            --out-dir "$OUT/fcsgx/$id" --gx-db "$GXDB" --tax-id "$taxid"
    rpt=$(ls "$OUT/fcsgx/$id"/*.${taxid}.fcs_gx_report.txt)
    cat "$GEN/${id}.fasta" | python3 "$FCS_PY" clean genome \
        --action-report "$rpt" --output "$GEN/${id}.clean.fasta" \
        --contam-fasta-out "$OUT/fcsgx/$id/${id}.contam.fasta"
  done < "$PROJECT/config/my_samples.csv"
fi

# ---- 门控：挑出需要复检/剔除的样本 ----
conda activate easyisolate
awk -F'\t' 'NR==1 || $3>5 {print $1, $2, $3}' "$OUT/checkm2/quality_report.tsv" > "$OUT/recheck_checkm2.tsv"
awk -F'\t' 'NR==1 || $NF=="False" {print}' "$OUT/gunc_all.tsv" > "$OUT/recheck_gunc.tsv"
echo "[完成] QUAST/CheckM2/GUNC 结果在 $OUT；复检清单 recheck_*.tsv"
