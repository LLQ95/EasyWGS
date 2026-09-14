#!/usr/bin/env bash
# =============================================================================
# 13_gwas/13.run_gwas.sh - run all microbial-GWAS layers and the post-GWAS R step
# Select the phenotype column with TRAIT=<name>, e.g. TRAIT=ESBL bash 13.run_gwas.sh
#   13.1 Scoary   : gene-based pan-GWAS on the pangenome (binary traits)
#   13.2 PLINK    : SNP association with IBS/MDS structure control
#   13.3 pyseer   : gene and SNP microbial GWAS with a distance-kernel model
#   13.4 R        : BH/Bonferroni correction, QQ and Manhattan plots, hit tables
# Each layer skips gracefully when its upstream input is absent.
# =============================================================================
set -euo pipefail
export TRAIT=${TRAIT:-MDR}
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}; export PROJECT
DIR="$PROJECT/13_gwas"
bash "$DIR/13.1.scoary.sh"
bash "$DIR/13.2.plink.sh"
bash "$DIR/13.3.pyseer.sh"
Rscript "$DIR/13.4.post_gwas.R" "$PROJECT"
echo "[done] GWAS tables/figures in 13_gwas/post"
