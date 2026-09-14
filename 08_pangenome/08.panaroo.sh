#!/usr/bin/env bash
# =============================================================================
# 08_pangenome/08.panaroo.sh - pangenome (Panaroo recommended, stricter cleanup;
#   Roary kept as compatible fallback)
# Input : per-sample gff under 05_annotation/prokka
# Output: core/accessory gene tables and a core-gene multiple alignment used by
#   module 09 to build a core-gene tree (cross-checks the SNP tree)
# =============================================================================
set -euo pipefail
THREADS=8
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
GFF_DIR="$PROJECT/05_annotation/prokka"
OUT="$PROJECT/08_pangenome"; mkdir -p "$OUT/panaroo_in"

# Panaroo needs one directory per sample with the matching gff (prokka already does); collect the list
find "$GFF_DIR" -name "*.gff" | sort > "$OUT/gff_list.txt"

# ---- 1) Panaroo strict mode (for one species with strong clonal structure) ----
panaroo -i $(tr '\n' ' ' < "$OUT/gff_list.txt") -o "$OUT/panaroo" \
        --clean-mode strict --remove-invalid-genes --threads "$THREADS" -a core

# ---- 2) Core-genome multiple sequence alignment (core_only) for tree building ----
panaroo-msa --pan_dir "$OUT/panaroo" --outdir "$OUT/core_msa" \
            --core_only --n_cpu "$THREADS"
# Build a core-gene tree directly from the alignment (optional)
iqtree2 -s "$OUT/core_msa/core_gene_alignment.aln" -m GTR+G4 \
        -alrt 1000 -bb 1000 -nt "$THREADS" -pre "$OUT/core_gene_tree"

# ---- 3) (Fallback) Roary, mutually exclusive with Panaroo, needs its own env ----
# roary -p "$THREADS" -e --mafft -r -f "$OUT/roary" $(tr '\n' ' ' < "$OUT/gff_list.txt")
# roary_plots.py "$OUT/roary/core_SNP_tree.tre" "$OUT/roary/gene_presence_absence.csv"

# ---- 4) Gene-trait association (scoary) and gene co-occurrence (coinfinder, optional) ----
# scoary -g "$OUT/panaroo/gene_presence_absence.csv" -t config/phenotype.csv -n tree.nwk
echo "[done] pangenome: $OUT/panaroo (gene_presence_absence.csv); core alignment: core_msa/"
