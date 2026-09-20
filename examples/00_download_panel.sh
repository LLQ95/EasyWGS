#!/usr/bin/env bash
# =============================================================================
# examples/00_download_panel.sh - fetch the curated multi-pathogen panel
#
#   bash examples/00_download_panel.sh [TIER] [extra download_panel.py flags]
#
# TIER 1 (default): one short-read and one hybrid isolate per pathogen (10)
# TIER 2: three short-read isolates per pathogen (20)
# TIER 3: full panel incl. the 12-isolate Salmonella temporal set (29)
# TIER 4: add five more pathogen groups (Vibrio/Yersinia/Campylobacter/Burkholderia/Clostridium; 44)
# TIER 5: add nine more pathogen groups (S. aureus/Cronobacter/S. dysenteriae/V. cholerae/
#         B. anthracis/B. cereus/B. mallei/M. tuberculosis/Brucella; 71)
#
# Useful flags passed through to download_panel.py:
#   --refs   download only the reference genomes   --reads only the reads
# Environment:
#   EXAMPLE_PAIRS=800000  paired reads kept per Illumina isolate (raise for full depth)
#   KEEP_CACHE=1          keep the full downloaded FASTQ after downsampling
# =============================================================================
set -euo pipefail
TIER=${1:-1}
if [[ "$TIER" != [12345] ]]; then echo "TIER must be 1, 2, 3, 4 or 5 (got $TIER)"; exit 1; fi
shift || true
PROJECT=$(cd "$(dirname "$0")/.." && pwd); export PROJECT
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "${EASYWGS_ENV:-easywgs}"

python "$PROJECT/examples/scripts/make_samplesheets.py" "$TIER"
python "$PROJECT/examples/scripts/download_panel.py" "$TIER" "$@"

echo "[done] panel tier $TIER is in 00_rawdata/ and references are in ref/"
echo "       next: bash examples/01_run_panel.sh $TIER"
