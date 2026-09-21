#!/usr/bin/env bash
# =============================================================================
# examples/scripts/downsample_panel.sh - build a tiny, reproducible panel
#
# Subsamples a fixed number of Illumina read pairs per isolate with seqkit
# (fixed seed, so the result is identical on every run) to create a "mini"
# panel that exercises the full assembly route in minutes on the cluster. This
# is the real-data counterpart of the zero-dependency CI smoke test: it catches
# problems that only appear with genuine reads, without waiting for the full
# tier-1 to tier-5 panels.
#
# Usage:
#   bash examples/scripts/downsample_panel.sh SAMPLESHEET [PAIRS]
#
# Arguments:
#   SAMPLESHEET  panel samplesheet with columns
#                id,platform,species,R1,R2,longreads,reference,date,country,phenotype
#                (for example examples/generated/samplesheet_tier1.csv)
#   PAIRS        read pairs to keep per isolate (default 200000, about 50-80x
#                for a 5 Mb bacterium; override with DOWNSAMPLE_PAIRS)
#
# Output:
#   00_rawdata/mini_<id>_R{1,2}.fastq.gz
#   config/my_samples.mini.csv          (id gets the mini_ prefix)
#
# Then run the assembly route (no reference genome required):
#   bash run_assembly.sh config/my_samples.mini.csv
#
# Only paired-end Illumina rows are subsampled; long reads are left out so the
# mini panel stays small. The same seed applied to the two matched files keeps
# read pairs synchronized.
# =============================================================================
set -euo pipefail
PROJECT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$PROJECT"

SHEET="${1:-config/my_samples.csv}"
PAIRS="${2:-${DOWNSAMPLE_PAIRS:-200000}}"
SEED=42
OUTSHEET="config/my_samples.mini.csv"

if ! command -v seqkit >/dev/null 2>&1; then
  echo "[error] seqkit not found; activate the easywgs environment first" >&2
  exit 1
fi
if [[ ! -f "$SHEET" ]]; then
  echo "[error] samplesheet not found: $SHEET" >&2
  echo "        run examples/00_download_panel.sh first, then pass the generated sheet" >&2
  exit 1
fi

mkdir -p 00_rawdata config
head -n 1 "$SHEET" > "$OUTSHEET"

tail -n +2 "$SHEET" | while IFS=',' read -r id platform species r1 r2 _rest; do
  [[ -z "${id:-}" ]] && continue
  case "$platform" in
    *illumina*|*Illumina*|*short*) ;;
    *) echo "[skip] $id: not paired-end Illumina ($platform)"; continue ;;
  esac
  for f in "$r1" "$r2"; do
    if [[ ! -f "$f" ]]; then
      echo "[skip] $id: missing $f"
      continue 2
    fi
  done
  o1="00_rawdata/mini_${id}_R1.fastq.gz"
  o2="00_rawdata/mini_${id}_R2.fastq.gz"
  seqkit sample -s "$SEED" -n "$PAIRS" "$r1" -o "$o1"
  seqkit sample -s "$SEED" -n "$PAIRS" "$r2" -o "$o2"
  echo "mini_${id},${platform},${species},${o1},${o2},,,,," >> "$OUTSHEET"
  echo "[mini] $id -> $PAIRS pairs"
done

echo ""
echo "[done] wrote $OUTSHEET"
echo "       quick assembly smoke run: bash run_assembly.sh $OUTSHEET"
