#!/usr/bin/env bash
# =============================================================================
# 06_typing/06.1.mlst.sh - classical 7-gene MLST (PubMLST schemes, auto species)
# Input : assembly fasta; Output: merged pubmlst.tab (col 2 scheme, col 3 ST)
# =============================================================================
set -euo pipefail
THREADS=8
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
GEN="$PROJECT/03_assembly/genomes"
OUT="$PROJECT/06_typing"; mkdir -p "$OUT/mlst"

# Run per isolate and keep file names for traceability
: > "$OUT/mlst/pubmlst.tab"
for f in "$GEN"/*.fasta; do
  mlst --threads "$THREADS" "$f" >> "$OUT/mlst/pubmlst.tab"
done
column -t "$OUT/mlst/pubmlst.tab" | less -S || true
# Refresh offline DB periodically: mlst-download_pub_mlst -j 8 -d <env>/db/pubmlst
# List supported schemes: mlst --long | less
echo "[done] MLST: $OUT/mlst/pubmlst.tab (fields: file scheme ST and 7 alleles)"
