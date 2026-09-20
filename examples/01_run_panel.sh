#!/usr/bin/env bash
# =============================================================================
# examples/01_run_panel.sh - run EasyWGS end to end on the curated panel
#
#   bash examples/01_run_panel.sh [TIER] [start step]
#
# Copies the tier config into config/, runs the full master runner, derives a
# genotype-based MDR trait after module 07, and collects every headline metric
# into examples/results/ for the manuscript Application section. The two-layer
# decontamination spike-in is a separate step: examples/02_run_spikein.sh
# =============================================================================
set -euo pipefail
TIER=${1:-1}
START=${2:-00}
if [[ "$TIER" != [1234] ]]; then echo "TIER must be 1, 2, 3 or 4 (got $TIER)"; exit 1; fi
PROJECT=$(cd "$(dirname "$0")/.." && pwd); export PROJECT
G=examples/generated

# 1) Config for the chosen tier (regenerated from panel.tsv, never hand-edited)
python "$PROJECT/examples/scripts/make_samplesheets.py" "$TIER"
cp "$PROJECT/$G/samplesheet.tier$TIER.csv"        "$PROJECT/config/my_samples.csv"
cp "$PROJECT/$G/metadata_dates.tier$TIER.csv"     "$PROJECT/config/metadata_dates.csv"
cp "$PROJECT/$G/traits.tier$TIER.csv"             "$PROJECT/config/traits.csv"

# 2) Full workflow (both routes, typing, pangenome/tree/dating, GWAS, reporting)
bash "$PROJECT/run_all.sh" "$PROJECT/config/my_samples.csv" "$START"

# 3) Genotype-based MDR trait from AMRFinderPlus classes (module 07 output),
#    then the association layer can be rerun on it: TRAIT=MDR_genotypic bash 13_gwas/13.run_gwas.sh
python "$PROJECT/examples/scripts/derive_mdr_traits.py" "$TIER"

# 4) Collect headline metrics into examples/results/ (real numbers only)
python "$PROJECT/examples/scripts/collect_panel_metrics.py" "$TIER"

# 5) Verify the run against the expected-result rules (WARN until modules run)
python "$PROJECT/examples/expected/check_expected.py" || true

echo "[done] tier $TIER finished. Master table: 99_report/master_table.tsv"
echo "       panel metrics: examples/results/panel_metrics.tsv and panel_summary.md"
echo "       decontamination validation: bash examples/02_run_spikein.sh"
