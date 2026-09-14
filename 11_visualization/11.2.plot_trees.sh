#!/usr/bin/env bash
# =============================================================================
# 11_visualization/11.2.plot_trees.sh
# Publication-ready static trees (ggtree): core-SNP tree, core-gene tree,
# time-scaled tree; rectangular and circular, PDF + PNG, under figures/.
# Set RSCRIPT to a specific interpreter, e.g. RSCRIPT="/path/to/Rscript".
# =============================================================================
set -euo pipefail
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
RSCRIPT=${RSCRIPT:-Rscript}
DIR="$PROJECT/11_visualization"
if ! command -v "$RSCRIPT" >/dev/null 2>&1; then
  echo "[skip] Rscript not found; install R packages with 00_install/install_R_packages.R"
  exit 0
fi
"$RSCRIPT" "$DIR/plot_trees.R" "$PROJECT"
