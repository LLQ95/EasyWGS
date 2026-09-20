#!/usr/bin/env bash
# =============================================================================
# 00_install/build_custom_db.sh - build the abricate easywgs_markers database
#
# The marker sequences are neither shipped in git nor auto-downloaded, because
# surface-antigen and toxin alleles carry type-specific reference sets and
# database licences. The curated marker list (gene symbols, classes and
# authoritative sources) is examples/customdb/easywgs_markers.tsv.
#
# Workflow:
#   1. Open examples/customdb/easywgs_markers.tsv and fetch each locus/allele
#      sequence from the cited RefSeq reference genome, VFDB or PubMLST record.
#   2. Concatenate them into one multi-FASTA. Each header must start with the
#      marker_id from the TSV, optionally followed by '|allele' and a note:
#         >VP_tdh|reference thermostable direct hemolysin, RIMD 2210633
#   3. Build the database (default per-user abricate directory):
#         MARKER_FASTA=/path/to/easywgs_markers.fa bash 00_install/build_custom_db.sh
#      Override locations with EASYWGS_ABRICATE_DIR or EASYWGS_MARKER_DIR.
# =============================================================================
set -euo pipefail
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
source "$PROJECT/00_install/runtime.sh"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$EASYWGS_ENV"

FASTA=${MARKER_FASTA:-${DBROOT:-$HOME/easywgs_db}/custom_db/easywgs_markers.fa}
DBDIR=${EASYWGS_ABRICATE_DIR:-$HOME/.abricate/db/easywgs_markers}

if [[ ! -s "$FASTA" ]]; then
  echo "[info] no marker FASTA found at: $FASTA"
  echo "       1. see examples/customdb/easywgs_markers.tsv for the marker list and sources"
  echo "       2. fetch the locus/allele sequences from the cited RefSeq/VFDB/PubMLST records"
  echo "       3. concatenate into one multi-FASTA whose headers start with the marker_id"
  echo "       4. rerun: MARKER_FASTA=/path/to/easywgs_markers.fa bash 00_install/build_custom_db.sh"
  exit 0
fi

mkdir -p "$DBDIR"
cp "$FASTA" "$DBDIR/sequences"
( cd "$DBDIR" && abricate --setupdb )
abricate --list | grep -i easywgs_markers || true
echo "[done] built $DBDIR; module 06.4 now screens assemblies with --db easywgs_markers"
