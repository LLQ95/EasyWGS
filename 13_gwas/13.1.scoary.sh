#!/usr/bin/env bash
# =============================================================================
# 13_gwas/13.1.scoary.sh
# Gene-based (pan-GWAS) association test with Scoary.
# Tests every accessory/core gene in the Panaroo/Roary gene_presence_absence.csv
# against each BINARY (0/1) trait in config/traits.csv, using Fisher's test and
# population-aware pairwise comparisons with Benjamini-Hochberg correction.
#
# Upstream : 08_pangenome (gene_presence_absence.csv), config/traits.csv
# Output   : 13_gwas/scoary/<trait>.csv association tables (naive + corrected p)
# Notes    : Scoary handles binary traits only; continuous columns are skipped.
#            Isolate names in traits.csv must match pangenome sample names (=id).
# =============================================================================
set -euo pipefail
THREADS=8
PERMUTE=1000            # label permutations for empirical p-values (set 0 to skip)
P_CUTOFF=0.05
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
OUT="$PROJECT/13_gwas/scoary"; mkdir -p "$OUT"
TRAITS="$PROJECT/config/traits.csv"
[[ -f "$TRAITS" ]] || { echo "Missing phenotype table: $TRAITS (see config/traits.csv)"; exit 1; }

# Locate the pangenome gene presence/absence matrix (Panaroo or Roary)
PA=$(find "$PROJECT/08_pangenome" -name 'gene_presence_absence.csv' | head -1)
[[ -n "$PA" && -f "$PA" ]] || { echo "gene_presence_absence.csv not found; run module 08 first."; exit 1; }
echo "Pangenome matrix: $PA ; traits: $TRAITS"

# -c BH controls the false discovery rate; use -c B for the stricter Bonferroni FWER.
# -n permutes labels for empirical significance; remove it to run faster on big sets.
scoary -t "$TRAITS" -g "$PA" -o "$OUT" \
       -c BH -p "$P_CUTOFF" -n "$PERMUTE" --threads "$THREADS"

echo "[done] per-trait gene associations in $OUT."
echo "Interpret columns Naive_p, BH_p and pairwise (PW/Empirical) p; feed hits to 13.4.post_gwas.R."
