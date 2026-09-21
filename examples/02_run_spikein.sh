#!/usr/bin/env bash
# =============================================================================
# examples/02_run_spikein.sh - controlled decontamination spike-in validation
#
# Two modes:
#
#   Synthetic (self-contained, no download and no large database):
#       bash examples/02_run_spikein.sh --synthetic
#       SYNTHETIC=1 bash examples/02_run_spikein.sh
#     Uses seeded synthetic genomes and the bwa/samtools engine when present,
#     otherwise a built-in k-mer classifier. Produces the read-layer panels of
#     Fig. 4 in seconds; this is the mode run by continuous integration.
#
#   Real panel (requires tier-1 cleaned reads for EC_BE_2015 and KP_GR_2011 and,
#   for assembly QC, the checkm2/gunc environments with their databases):
#       bash examples/02_run_spikein.sh
#     PhiX reads are simulated with art_illumina (bioconda package "art").
#
# Outputs: examples/spikein/results/spikein_metrics.tsv and Fig_spikein.{svg,pdf,png}
# A version-controlled copy of the figure is published to figures/ and docs/assets/.
# =============================================================================
set -euo pipefail
PROJECT=$(cd "$(dirname "$0")/.." && pwd); export PROJECT
MODE="real"
if [[ "${1:-}" == "--synthetic" || "${SYNTHETIC:-0}" == "1" ]]; then
  MODE="synthetic"
fi

# Activate the conda environment when conda is available and the caller is not
# already inside one (continuous integration activates micromamba itself).
if command -v conda >/dev/null 2>&1 && [[ -z "${CONDA_DEFAULT_ENV:-}" || "${CONDA_DEFAULT_ENV:-base}" == "base" ]]; then
  # shellcheck disable=SC1091
  source "$(conda info --base)/etc/profile.d/conda.sh"
  conda activate "${EASYWGS_ENV:-easywgs}" || echo "[warn] could not activate ${EASYWGS_ENV:-easywgs}; using the current Python"
fi

if [[ "$MODE" == "synthetic" ]]; then
  echo "[spikein] self-contained synthetic mode"
  python "$PROJECT/examples/spikein/spikein_run.py" --synthetic
else
  echo "[spikein] real-panel mode"
  python "$PROJECT/examples/spikein/spikein_run.py"
fi
python "$PROJECT/examples/spikein/make_spikein_figure.py"

# Gate the result against the expected rules (WARN never blocks; FAIL exits non-zero)
python "$PROJECT/examples/expected/check_expected.py" --mode spikein

echo "[done] spike-in metrics and figure are in examples/spikein/results/"
