#!/usr/bin/env bash
# =============================================================================
# 05_annotation/05.annotate.sh - structural and functional annotation
# Prokka (fast) or Bakta (comprehensive, recommended) batch annotation; Prodigal
#   for proteins; eggNOG for GO/KEGG/COG
# Module 08 (Panaroo/Roary) needs the gff produced here, so this is its prerequisite
# =============================================================================
set -euo pipefail
THREADS=8
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
GEN="$PROJECT/03_assembly/genomes"
OUT="$PROJECT/05_annotation"
DBROOT=${DBROOT:-$HOME/easywgs_db}
mkdir -p "$OUT/prokka" "$OUT/prodigal_faa" "$OUT/bakta" "$OUT/eggnog"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "${EASYWGS_ENV:-easywgs}"

# ---- 1) Prokka batch annotation (set --genus per sample if needed; Bacteria is generic) ----
for f in "$GEN"/*.fasta; do
  id=$(basename "$f" .fasta)
  prokka --outdir "$OUT/prokka/$id" --prefix "$id" --cpus "$THREADS" \
         --addgenes --centre EasyWGS --compliant "$f"
done

# ---- 2) Prodigal proteins (for eggNOG / custom databases) ----
for f in "$GEN"/*.fasta; do
  id=$(basename "$f" .fasta)
  prodigal -i "$f" -a "$OUT/prodigal_faa/${id}.faa" \
           -d "$OUT/prodigal_faa/${id}.ffn" -o "$OUT/prodigal_faa/${id}.gff" -f gff -p single
done

# ---- 3) Bakta full annotation (recommended, richer; separate environment) ----
conda activate bakta
for f in "$GEN"/*.fasta; do
  id=$(basename "$f" .fasta)
  bakta --db "$DBROOT/bakta_db" --output "$OUT/bakta/$id" --prefix "$id" \
        --threads "$THREADS" "$f"
done
conda deactivate

# ---- 4) eggNOG-mapper: GO/KEGG/COG/EC (input is protein faa) ----
conda activate eggnog
for faa in "$OUT/prodigal_faa"/*.faa; do
  id=$(basename "$faa" .faa)
  emapper.py -i "$faa" --data_dir "$DBROOT/eggnog_db" --cpu "$THREADS" \
             -m diamond --override -o "$OUT/eggnog/$id"
done
conda deactivate
echo "[done] annotation: $OUT/prokka (gff for pangenome), $OUT/eggnog (functional annotation)"
