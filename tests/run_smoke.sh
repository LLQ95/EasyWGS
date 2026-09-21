#!/usr/bin/env bash
# =============================================================================
# tests/run_smoke.sh - lightweight functional smoke test for EasyWGS
#
# Runs the real module scripts on a tiny, deterministic, fully synthetic
# dataset (no download and no large database). It exercises the two routes that
# must always work on a clean install:
#
#   1. read QC        01_qc/01.fastp.sh        (fastp + fastqc + multiqc)
#   2. mapping route  12.1.map_reads.sh        (bwa -> sorted indexed BAM)
#                     12.2.call_variants.sh    (bcftools -> genotype matrix)
#   3. decontam       examples/02_run_spikein.sh --synthetic
#                                                (read-layer spike-in + gates)
#
# Heavy or database-backed steps (SPAdes assembly, CheckM2, GUNC, Bakta,
# eggNOG-mapper, FCS-GX) are mature third-party tools and are validated on the
# real cluster panel; they are intentionally excluded to keep CI fast and
# self-contained. See docs/cluster-checklist.md for that validation.
#
# Requirements on PATH: python3, fastp, fastqc, multiqc, bwa, samtools,
# bcftools, tabix/bgzip. Exit code is non-zero on the first failed assertion.
# =============================================================================
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
WORK=$(mktemp -d -t easywgs-smoke.XXXXXX)
trap 'rm -rf "$WORK"' EXIT
export PROJECT="$WORK"
cd "$ROOT"

MIN_BREADTH=0.90
MIN_DEPTH=15
MIN_SNPS=20

echo "==> [1/5] generating deterministic toy dataset in $WORK"
python3 "$ROOT/tests/make_toy_data.py" "$WORK"
test -s "$WORK/00_rawdata/toy_R1.fastq.gz"
test -s "$WORK/00_rawdata/mut_R1.fastq.gz"

echo "==> [2/5] module 01: read QC (fastp)"
bash "$ROOT/01_qc/01.fastp.sh"
for s in toy mut; do
  test -s "$WORK/01_qc/clean/${s}_R1.fq.gz" || { echo "FAIL: missing cleaned reads for $s"; exit 1; }
done

echo "==> [3/5] module 12.1: reference mapping (bwa + samtools)"
bash "$ROOT/12_mapping_pipeline/12.1.map_reads.sh"
COV="$WORK/12_mapping_pipeline/qc/coverage_summary.tsv"
test -s "$COV" || { echo "FAIL: coverage_summary.tsv missing"; exit 1; }
cat "$COV"
awk -F'\t' -v mb="$MIN_BREADTH" -v md="$MIN_DEPTH" '
  NR>1 {
    if ($3+0 < md)      { print "FAIL: mean depth " $3 " < " md " for " $1; bad=1 }
    if ($4+0 < mb)      { print "FAIL: breadth " $4 " < " mb " for " $1; bad=1 }
    if ($6+0 < 90)      { print "FAIL: mapped% " $6 " < 90 for " $1; bad=1 }
  }
  END { exit bad?1:0 }' "$COV"
for s in toy mut; do
  test -s "$WORK/12_mapping_pipeline/bam/${s}.sorted.bam.bai" || { echo "FAIL: indexed BAM missing for $s"; exit 1; }
done

echo "==> [4/5] module 12.2: variant calling (bcftools)"
bash "$ROOT/12_mapping_pipeline/12.2.call_variants.sh"
GENO="$WORK/12_mapping_pipeline/variants/snp_geno_matrix.tsv"
test -s "$GENO" || { echo "FAIL: snp_geno_matrix.tsv missing"; exit 1; }
NSNP=$(grep -c '^[^#]' "$GENO" || true)
echo "bi-allelic SNP sites recovered: $NSNP (need >= $MIN_SNPS)"
if [ "$NSNP" -lt "$MIN_SNPS" ]; then
  echo "FAIL: too few SNPs recovered from the seeded mutant; mapping/calling is broken"
  exit 1
fi

echo "==> [5/5] decontamination spike-in (self-contained synthetic mode)"
SYNTHETIC=1 bash "$ROOT/examples/02_run_spikein.sh"

echo ""
echo "SMOKE TEST PASSED: QC, mapping, variant calling and the decontamination"
echo "spike-in all ran end to end on deterministic synthetic data."
