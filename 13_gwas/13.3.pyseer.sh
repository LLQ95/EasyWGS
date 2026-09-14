#!/usr/bin/env bash
# =============================================================================
# 13_gwas/13.3.pyseer.sh
# Microbial GWAS with pyseer, using a distance matrix to model clonal population
# structure (the equivalent of an LMM/kinship correction in bacterial data).
# Two feature layers are run by default:
#   (a) gene-level presence/absence from Panaroo/Roary (*.Rtab)
#   (b) SNP-level tests from the mapping-route bi-allelic VCF
# A k-mer/unitig route is provided as a commented command for finer mapping.
#
# Choose the trait with  TRAIT=<column> bash 13.3.pyseer.sh   (default MDR)
# Upstream: 08_pangenome (*.Rtab), 12.2 (SNP VCF), 09 (snp_dists.tsv) or Mash
# Output  : 13_gwas/pyseer/assoc_genes.txt, assoc_snps.txt (+ p/effect/beta/SE)
# =============================================================================
set -euo pipefail
TRAIT=${TRAIT:-MDR}
MIN_AF=0.02
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
OUT="$PROJECT/13_gwas/pyseer"; mkdir -p "$OUT"
TRAITS="$PROJECT/config/traits.csv"
command -v pyseer >/dev/null 2>&1 || { echo "pyseer not found; install bioconda 'pyseer'."; exit 1; }
cd "$OUT"

# pyseer phenotype file: header "samples<TAB>trait", one value per sample
COL=$(head -1 "$TRAITS" | tr ',' '\n' | grep -n -x "$TRAIT" | cut -d: -f1)
[[ -n "$COL" ]] || { echo "Trait column '$TRAIT' not in $TRAITS"; exit 1; }
{ printf 'samples\t%s\n' "$TRAIT";
  awk -F',' -v c="$COL" 'NR>1 && $1!="Name"{print $1"\t"$c}' "$TRAITS" | grep -v $'\tNA$'; } > pheno.tsv

# Population-structure distance matrix: prefer the SNP distance matrix (module 09),
# else a Mash triangle/square matrix. Build one with:
#   mash sketch -l genome_list.txt -o ref; mash dist ref.msh ref.msh -t > mash_dist.tsv
DIST_ARG=()
DIST=$(find "$PROJECT/09_phylogeny" -name 'snp_dists.tsv' | head -1)
if [[ -z "$DIST" || ! -f "$DIST" ]]; then DIST=$(find "$PROJECT" -name 'mash_dist.tsv' | head -1); fi
if [[ -n "$DIST" && -f "$DIST" ]]; then
  echo "Using distance matrix for structure control: $DIST"; DIST_ARG=(--distances "$DIST")
else
  echo "[warn] no distance matrix found; running a naive fixed-effect model. Add --distances to control clonal structure."
fi

# (a) Gene-level pan-GWAS (binary presence/absence Rtab matrix)
RTAB=$(find "$PROJECT/08_pangenome" -name 'gene_presence_absence.Rtab' | head -1)
if [[ -n "$RTAB" && -f "$RTAB" ]]; then
  pyseer --phenotypes pheno.tsv --presence "$RTAB" "${DIST_ARG[@]}" \
         --min-af "$MIN_AF" --max-af 0.98 --cpu 4 --output assoc_genes.txt
else
  echo "[skip] gene_presence_absence.Rtab not found (run Panaroo/Roary module 08)."
fi

# (b) SNP-level GWAS from the reference mapping route
VCF="$PROJECT/12_mapping_pipeline/variants/snps.biallelic.vcf.gz"
if [[ -f "$VCF" ]]; then
  pyseer --phenotypes pheno.tsv --vcf "$VCF" "${DIST_ARG[@]}" \
         --min-af "$MIN_AF" --cpu 4 --output assoc_snps.txt
else
  echo "[skip] SNP VCF not found (run modules 12.1/12.2)."
fi

# (c, optional) k-mer/unitig route for causal-marker discovery independent of annotation:
#   unitig-counter --strains genome_list.txt --output unitigs --threads 4
#   pyseer --phenotypes pheno.tsv --kmers unitigs/unitigs.txt "${DIST_ARG[@]}" --output assoc_unitigs.txt
#   python -m pyseer.annotate --assoc assoc_unitigs.txt --gene_annot annot.gff --ref_pan ref --output annotated.txt

echo "[done] pyseer associations in $OUT; feed to 13.4.post_gwas.R."
