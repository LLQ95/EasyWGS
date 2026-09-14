#!/usr/bin/env bash
# =============================================================================
# 12_mapping_pipeline/12.run_mapping.sh - run the full reference-based route
#   12.1 map cleaned reads to the shared reference (BAM + coverage)
#   12.2 joint bcftools variant calling (raw/filtered VCF + SNP matrix)
# =============================================================================
set -euo pipefail
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}; export PROJECT
DIR="$PROJECT/12_mapping_pipeline"
bash "$DIR/12.1.map_reads.sh"
bash "$DIR/12.2.call_variants.sh"
echo "[done] mapping route: BAM in 12_mapping_pipeline/bam, VCF/SNP matrix in 12_mapping_pipeline/variants"
