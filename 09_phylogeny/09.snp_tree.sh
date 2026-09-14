#!/usr/bin/env bash
# =============================================================================
# 09_phylogeny/09.snp_tree.sh - reference-based core-SNP phylogeny
#   per-sample snippy against one reference -> snippy-core merge -> Gubbins
#   recombination removal -> snp-sites invariant SNP extraction ->
#   IQ-TREE/FastTree tree -> snp-dists pairwise SNP matrix
# The reference is column 6 of samplesheet.csv (one reference for the whole batch,
#   preferably a close finished genome; gbk/fasta)
# =============================================================================
set -euo pipefail
THREADS=8
# Prefer IQ-TREE 3 (binary iqtree3); fall back to IQ-TREE 2 (iqtree2) or the generic iqtree name
IQTREE=$(command -v iqtree3 || command -v iqtree2 || command -v iqtree)
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
GEN="$PROJECT/03_assembly/genomes"
OUT="$PROJECT/09_phylogeny"; mkdir -p "$OUT/snippy"
SHEET="$PROJECT/config/my_samples.csv"
REF=$(awk -F',' 'NR==2{print $6}' "$SHEET")      # shared reference
[[ -f "$PROJECT/$REF" ]] && REF="$PROJECT/$REF"
echo "Reference: $REF"

# ---- 1) Per-sample variant calls on assemblies (reads also possible) ----
DIRS=()
while IFS=',' read -r id species r1 r2 rest; do
  [[ "$id" == "id" || "$id" == \#* || -z "$id" ]] && continue
  d="$OUT/snippy/$id"
  if [[ ! -d "$d" ]]; then
    snippy --cpus "$THREADS" --outdir "$d" --ref "$REF" --ctgs "$GEN/${id}.fasta"
    # With reads instead: snippy --ref REF --R1 r1 --R2 r2
  fi
  DIRS+=("$d")
done < "$SHEET"

# ---- 2) Merge the whole-batch core alignment ----
cd "$OUT"
snippy --cpus "$THREADS" --ref "$REF" --outdir core --cleanup "${DIRS[@]}"
# Produces core.full.aln (with invariant sites) and core.aln (SNPs only)

# ---- 3) Gubbins: detect and mask recombinant regions ----
run_gubbins.py --threads "$THREADS" --tree-builder iqtree --prefix gubbins core/core.full.aln

# ---- 4) Extract recombination-free core SNPs and build the tree ----
snp-sites -c gubbins.filtered_polymorphic_sites.fasta > clean.core.aln
"$IQTREE" -s clean.core.aln -m GTR+G4 -alrt 1000 -bb 1000 -nt AUTO -pre core_iqtree
# Fast alternative: FastTree -gtr -nt clean.core.aln > core_fasttree.tre

# ---- 5) Pairwise SNP distance matrix (for cluster cutoffs, e.g. Salmonella 5/10/20 SNP) ----
snp-dists -j "$THREADS" clean.core.aln > snp_dists.tsv
echo "[done] tree: $OUT/core_iqtree.treefile; SNP matrix: $OUT/snp_dists.tsv; feeds 10_treetime and 11_visualization"
