#!/usr/bin/env bash
# =============================================================================
# examples/02_run_spikein.sh - controlled decontamination spike-in validation
#
# Requires the tier-1 short-read pipeline to have reached module 01 (cleaned
# reads for EC_BE_2015 and KP_GR_2011) and, for assembly QC, the checkm2 and
# gunc environments plus their databases (00_install). PhiX reads are simulated
# with art_illumina (bioconda package "art").
#
#   bash examples/02_run_spikein.sh
#
# Outputs: examples/spikein/results/spikein_metrics.tsv and Fig_spikein.{svg,pdf,png}
# =============================================================================
set -euo pipefail
PROJECT=$(cd "$(dirname "$0")/.." && pwd); export PROJECT
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate easywgs

python "$PROJECT/examples/spikein/spikein_run.py"
python "$PROJECT/examples/spikein/make_spikein_figure.py"

echo "[done] spike-in metrics and figure are in examples/spikein/results/"
