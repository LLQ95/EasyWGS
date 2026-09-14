#!/usr/bin/env bash
# =============================================================================
# 11_visualization/11.4.itol_datasets.sh
# Generate iTOL annotation datasets (color strips + binary AMR track) under
# itol/. Upload a tree at https://itol.embl.de and drop the .txt files on it.
# =============================================================================
set -euo pipefail
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
PY=${PYTHON:-python3}
DIR="$PROJECT/11_visualization"
"$PY" "$DIR/make_itol_datasets.py" "$PROJECT"
