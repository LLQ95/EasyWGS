#!/usr/bin/env bash
# =============================================================================
# 13_gwas/13.2.plink.sh
# SNP-based association with PLINK 1.9 on the mapping-route bi-allelic SNP VCF
# (12_mapping_pipeline/variants/snps.biallelic.vcf.gz). Builds PLINK binaries,
# an IBS-based MDS projection (a proxy for the strong clonal structure expected
# in bacteria), and runs both a fast allelic test and a regression that includes
# the MDS axes as covariates.
#
# Choose the trait with  TRAIT=<column> bash 13.2.plink.sh   (default MDR)
# Binary traits (0/1 in traits.csv) -> case/control logistic regression
# Numeric traits                    -> linear regression
# Output: 13_gwas/plink/*.assoc / *.assoc.logistic(adjusted) / *.mds
#
# WARNING: bacterial samples are clonal and often small. Uncorrected association
# p-values are confounded by population structure; always include the MDS axes
# (or use 13.3 pyseer with a distance matrix) and confirm hits on the phylogeny.
# =============================================================================
set -euo pipefail
THREADS=8
TRAIT=${TRAIT:-MDR}
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
OUT="$PROJECT/13_gwas/plink"; mkdir -p "$OUT"
PLINK=$(command -v plink || command -v plink1.9 || true)
[[ -n "$PLINK" ]] || { echo "PLINK not found; install bioconda 'plink'."; exit 1; }
VCF="$PROJECT/12_mapping_pipeline/variants/snps.biallelic.vcf.gz"
[[ -f "$VCF" ]] || { echo "$VCF not found; run 12.1 then 12.2 first."; exit 1; }
TRAITS="$PROJECT/config/traits.csv"
cd "$OUT"

# 1) VCF -> PLINK binary. --double-id uses the sample name as FID/IID; bacterial
#    contig names are not human chromosomes, hence --allow-extra-chr.
"$PLINK" --vcf "$VCF" --make-bed --double-id --allow-extra-chr --set-missing-var-ids @:# --out base

# 2) PLINK phenotype file (FID IID value); binary 0/1 -> control 1 / case 2, NA -> -9
COL=$(head -1 "$TRAITS" | tr ',' '\n' | grep -n -x "$TRAIT" | cut -d: -f1)
[[ -n "$COL" ]] || { echo "Trait column '$TRAIT' not in $TRAITS"; exit 1; }
awk -F',' -v c="$COL" 'NR>1 && $1!="Name"{v=$c; if(v=="NA"||v=="")v=-9; else if(v==0)v=1; else if(v==1)v=2; print $1,$1,v}' OFS='\t' "$TRAITS" > pheno.txt
BINARY=$(awk '$3!=-9{a[$3]=1}END{print (($1 in a)&&($2 in a)&&length(a)==2)?"yes":"no"}' pheno.txt)
echo "Trait=$TRAIT binary=$BINARY ; $(wc -l < pheno.txt) phenotyped samples"

# 3) IBS distance MDS axes used as population-structure covariates
"$PLINK" --bfile base --allow-extra-chr --cluster --mds-plot 4 --out mds
cut -f1-3,5- mds.mds > covar_mds.txt    # FID IID + C1..C4 (drop the SOL column)

# 4) Association, unadjusted and MDS-adjusted
"$PLINK" --bfile base --allow-extra-chr --assoc --out assoc_fast
if [[ "$BINARY" == "yes" ]]; then
  "$PLINK" --bfile base --allow-extra-chr --pheno pheno.txt --1 \
           --covar covar_mds.txt --logistic hide-covar --adjust --ci 0.95 --out assoc_logistic
  echo "Logistic (MDS-adjusted): assoc_logistic.assoc.logistic and .adjusted"
else
  "$PLINK" --bfile base --allow-extra-chr --pheno pheno.txt \
           --covar covar_mds.txt --linear hide-covar --adjust --out assoc_linear
  echo "Linear (MDS-adjusted): assoc_linear.assoc.linear and .adjusted"
fi
echo "[done] PLINK results in $OUT; feed to 13.4.post_gwas.R for Manhattan/QQ plots."
