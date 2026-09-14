#!/usr/bin/env bash
# =============================================================================
# 10_treetime/10.treetime.sh - time-calibrated phylogeny (molecular clock) and
#   ancestral/homoplasy analysis
# Upstream: clean.core.aln (core-SNP alignment) and core_iqtree.treefile (tree)
# Metadata: config/metadata_dates.csv (name,date); optional states.csv for geography/phenotype
# A time tree needs adequate sampling-time span (clonal pathogens usually need
#   several years and enough isolates)
# =============================================================================
set -euo pipefail
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
P9="$PROJECT/09_phylogeny"
OUT="$PROJECT/10_treetime"; mkdir -p "$OUT"
DATES="$PROJECT/config/metadata_dates.csv"
TREE="$P9/core_iqtree.treefile"
ALN="$P9/clean.core.aln"
COAL=${COAL:-skyline}        # constant / skyline; use skyline for large, dynamically varying sets

# ---- 1) Root-to-tip regression: clock signal and temporal outliers ----
treetime clock --tree "$TREE" --dates "$DATES" --aln "$ALN" \
        --clock-filter 4 --reroot least-squares --outdir "$OUT/01_clock"
# --clock-filter 4 drops points >4 MAD from the regression; inspect 01_clock/rtt.csv then tighten and rerun

# ---- 2) Main time tree: substitution rate, divergence times, node dates ----
treetime --tree "$TREE" --dates "$DATES" --aln "$ALN" \
        --coalescent "$COAL" --outdir "$OUT/02_timetree"
# Key outputs:
#   02_timetree/timetree.nexus        tree with node dates and year-scaled branches
#   02_timetree/divergence_table.csv, rates.csv, rerooting*.pdf (root-to-tip plot)

# ---- 3) Ancestral sequence reconstruction and mutation mapping (e.g. A45G onto branches) ----
treetime ancestral --aln "$ALN" --tree "$OUT/02_timetree/timetree.nexus" \
        --outdir "$OUT/03_ancestral"

# ---- 4) Homoplasy scan: excess homoplasy hints at recombination/contamination/lab adaptation ----
treetime homoplasy --aln "$ALN" --tree "$OUT/02_timetree/timetree.nexus" \
        --outdir "$OUT/04_homoplasy"
# Focus on 04_homoplasy/ambiguous.tsv and homoplasy_scores.tsv; cross-check with the module-04 gate

# ---- 5) (Optional) discrete-state mugration: geography/phenotype/serotype evolution ----
if [[ -f "$PROJECT/config/states.csv" ]]; then
  for attr in country phenotype serotype; do
    treetime mugration --tree "$OUT/02_timetree/timetree.nexus" \
             --states "$PROJECT/config/states.csv" --attribute "$attr" \
             --outdir "$OUT/05_mugration_$attr" || true
  done
fi
# states.csv format: name,country,phenotype,serotype (one isolate per row)
echo "[done] time tree $OUT/02_timetree/timetree.nexus; open with FigTree/icytree or module 11"
