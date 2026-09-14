#!/usr/bin/env bash
# =============================================================================
# 11_visualization/11.3.grapetree.sh
# Minimum spanning trees (MSTreeV2) with GrapeTree from:
#   - chewBBACA cgMLST allele profiles (06_typing/cgmlst/*/ExtractCgMLST/cgMLST.tsv)
#   - the recombination-filtered core-SNP alignment (09_phylogeny/clean.core.aln)
# Output Newick files plus a metadata table for upload to the GrapeTree web app
# (https://achtman-lab.github.io/GrapeTree) or `grapetree --website`.
# =============================================================================
set -euo pipefail
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
OUT="$PROJECT/11_visualization/grapetree"; mkdir -p "$OUT"
META="$PROJECT/11_visualization/merged_metadata.csv"

if ! command -v grapetree >/dev/null 2>&1; then
  echo "[skip] grapetree not installed; it is in the easywgs env (pip/bioconda grapetree)"
  exit 0
fi

# 1) cgMLST profile MST (one per species schema)
while IFS= read -r profile; do
  sp=$(basename "$(dirname "$(dirname "$profile")")")
  echo ">>> GrapeTree cgMLST ($sp): $profile"
  grapetree -i "$profile" --profile -m MSTreeV2 -o "$OUT/cgmlst_${sp}_mst.nwk" || true
done < <(find "$PROJECT/06_typing/cgmlst" -path "*ExtractCgMLST/cgMLST.tsv" 2>/dev/null)

# 2) Core-SNP alignment MST
ALN="$PROJECT/09_phylogeny/clean.core.aln"
if [[ -f "$ALN" ]]; then
  echo ">>> GrapeTree core-SNP alignment: $ALN"
  grapetree -i "$ALN" -m MSTreeV2 -o "$OUT/coreSNP_mst.nwk" || true
fi

# 3) Metadata for web coloring
[[ -f "$META" ]] && cp "$META" "$OUT/grapetree_metadata.csv"
echo "[done] GrapeTree Newick files in $OUT; open at https://achtman-lab.github.io/GrapeTree"
