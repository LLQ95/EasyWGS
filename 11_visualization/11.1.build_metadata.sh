#!/usr/bin/env bash
# =============================================================================
# 11_visualization/11.1.build_metadata.sh
# Merge samplesheet + 99_report/master_table.tsv into merged_metadata.csv, the
# single annotation source shared by every later visualization step.
# =============================================================================
set -euo pipefail
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
PY=${PYTHON:-python3}
DIR="$PROJECT/11_visualization"
"$PY" "$DIR/make_metadata.py" "$PROJECT"
