#!/usr/bin/env bash
# =============================================================================
# 04_asm_qc/04.asm_qc_decontam.sh - assembly QC + assembly-level decontam gate
# QUAST metrics / CheckM2 completeness+contamination / GUNC chimerism /
#   (optional) FCS-GX to excise foreign contaminants
# Gate rule: CheckM2 Contamination > 5% or GUNC pass=False -> list in recheck_*.tsv
# =============================================================================
set -euo pipefail
THREADS=8
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
GEN="$PROJECT/03_assembly/genomes"
OUT="$PROJECT/04_asm_qc"; mkdir -p "$OUT/quast" "$OUT/checkm2" "$OUT/gunc"
source "$PROJECT/00_install/runtime.sh"
GUNC_DB=$(easywgs_resolve_gunc_db)
CHECKM2_DMND=$(easywgs_resolve_checkm2_db)
source "$(conda info --base)/etc/profile.d/conda.sh"

# ---- QUAST ----
conda activate "$EASYWGS_ENV"
quast.py -t "$THREADS" -o "$OUT/quast" "$GEN"/*.fasta

# ---- CheckM2 ----
# Reuse an existing database by exporting CHECKM2_DB (the uniref100.KO.1.dmnd
# file or its CheckM2_database directory); otherwise fall back to DBROOT.
conda activate checkm2
if [ -n "$CHECKM2_DMND" ] && [ -f "$CHECKM2_DMND" ]; then
  checkm2 predict --threads "$THREADS" --input "$GEN" --output-directory "$OUT/checkm2" --force \
    --database_path "$CHECKM2_DMND"
else
  echo "[warn] CheckM2 database not found (set CHECKM2_DB to uniref100.KO.1.dmnd or its directory); trying the registered default" >&2
  checkm2 predict --threads "$THREADS" --input "$GEN" --output-directory "$OUT/checkm2" --force \
    || echo "[warn] CheckM2 skipped; downstream CheckM2 fields will be NA" >&2
fi
conda deactivate

# ---- GUNC ----
conda activate gunc
if [ -n "$GUNC_DB" ] && [ -f "$GUNC_DB" ]; then
  for f in "$GEN"/*.fasta; do
    id=$(basename "$f" .fasta)
    gunc run --input_fasta "$f" -r "$GUNC_DB" --out_dir "$OUT/gunc/$id" \
             --threads "$THREADS" --detailed_output --contig_taxonomy_output
  done
  # Merge per-sample maxCSS tables
  find "$OUT/gunc" -name "GUNC.*maxCSS_level.tsv" -exec cat {} \; | awk '!a[$1]++' > "$OUT/gunc_all.tsv"
else
  echo "[warn] GUNC database not found (set GUNC_DB to gunc_db.dmnd or run download_db.sh); skipping GUNC" >&2
  : > "$OUT/gunc_all.tsv"
fi
conda deactivate

# ---- (optional) FCS-GX to excise cross-species contaminants; needs large RAM and a taxid column
# Add a taxid column to the samplesheet and loop here; without the setup, upload assemblies to
# https://usegalaxy.org and run FCS-GX online:
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

# ---- Gate: flag samples that need recheck/removal ----
conda activate "$EASYWGS_ENV"
if [ -f "$OUT/checkm2/quality_report.tsv" ]; then
  awk -F'\t' 'NR==1 || $3>5 {print $1, $2, $3}' "$OUT/checkm2/quality_report.tsv" > "$OUT/recheck_checkm2.tsv"
else
  echo -e "Name\tCompleteness\tContamination" > "$OUT/recheck_checkm2.tsv"
  echo "[warn] $OUT/checkm2/quality_report.tsv missing; recheck_checkm2.tsv left empty" >&2
fi
awk -F'\t' 'NR==1 || $NF=="False" {print}' "$OUT/gunc_all.tsv" > "$OUT/recheck_gunc.tsv"
echo "[done] QUAST/CheckM2/GUNC results in $OUT; recheck lists: recheck_*.tsv"
