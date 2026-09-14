#!/usr/bin/env bash
# =============================================================================
# 11_visualization/11.5.heatmaps.sh
# Clustered heatmaps (R/pheatmap): pairwise SNP distance, abricate per-DB hit
# counts and gene presence/absence; PDF + PNG under figures/.
# =============================================================================
set -euo pipefail
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
RSCRIPT=${RSCRIPT:-Rscript}
DIR="$PROJECT/11_visualization"
if ! command -v "$RSCRIPT" >/dev/null 2>&1; then
  echo "[skip] Rscript not found; install R packages with 00_install/install_R_packages.R"
  exit 0
fi
"$RSCRIPT" "$DIR/heatmaps.R" "$PROJECT"
