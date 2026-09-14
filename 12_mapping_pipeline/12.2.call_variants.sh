#!/usr/bin/env bash
# =============================================================================
# 12_mapping_pipeline/12.2.call_variants.sh
# Joint variant calling from the BAM files produced by 12.1.map_reads.sh,
# using bcftools mpileup/call. Produces a raw multi-sample VCF, a filtered
# bi-allelic SNP VCF and a genotype matrix consumed by module 13 (GWAS) and
# by any reference-based phylogeny (e.g. snp-sites / IQ-TREE).
#
# Upstream : 12.1.map_reads.sh (sorted + indexed BAM for every sample)
# Output   : 12_mapping_pipeline/variants/
#              calls.raw.vcf.gz          all called variants (SNPs + indels)
#              calls.norm.vcf.gz         left-aligned, quality-filtered
#              snps.biallelic.vcf.gz     bi-allelic SNPs, low-missing, MAC>=2
#              snp_geno_matrix.tsv       CHROM POS REF ALT + GT per sample
# =============================================================================
set -euo pipefail
THREADS=8
MIN_QUAL=20
MAX_MISSING=0.1
MIN_MAC=2
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
SHEET="$PROJECT/config/my_samples.csv"
MAP="$PROJECT/12_mapping_pipeline"
OUT="$MAP/variants"; mkdir -p "$OUT"

colnum () { head -1 "$SHEET" | tr ',' '\n' | grep -n -x "$1" | cut -d: -f1; }
C_ID=$(colnum id); C_REF=$(colnum reference)
REF=$(awk -F',' -v c="$C_REF" 'NR==2{print $c}' "$SHEET")
[[ -f "$PROJECT/$REF" ]] && REF="$PROJECT/$REF"
[[ -f "${REF}.fai" ]] || samtools faidx "$REF"

# Build an ordered BAM list following the samplesheet (skips missing files)
: > "$OUT/bam.list"
while IFS=',' read -r row; do
  id=$(echo "$row" | awk -F',' -v c="$C_ID" '{print $c}')
  [[ "$id" == "id" || "$id" == \#* || -z "$id" ]] && continue
  b="$MAP/bam/${id}.sorted.bam"
  if [[ -f "$b" ]]; then echo "$b" >> "$OUT/bam.list"; else echo "[warn] missing BAM for $id"; fi
done < "$SHEET"
[[ -s "$OUT/bam.list" ]] || { echo "No BAM files; run 12.1.map_reads.sh first."; exit 1; }

# 1) Joint genotype likelihoods and multi-allelic calling
bcftools mpileup --threads "$THREADS" -q 20 -Q 20 -a AD,DP -f "$REF" -b "$OUT/bam.list" -Ou \
  | bcftools call --threads "$THREADS" -mv -Oz -o "$OUT/calls.raw.vcf.gz"
tabix -f -p vcf "$OUT/calls.raw.vcf.gz"

# 2) Left-align/normalize against the reference and drop low-quality calls
bcftools norm --threads "$THREADS" -f "$REF" -Oz -o "$OUT/calls.norm.vcf.gz" "$OUT/calls.raw.vcf.gz"
tabix -f -p vcf "$OUT/calls.norm.vcf.gz"
bcftools filter --threads "$THREADS" -e "QUAL<${MIN_QUAL} || FMT/DP<4" -s LowQual -Oz -o "$OUT/calls.filt.vcf.gz" "$OUT/calls.norm.vcf.gz"
tabix -f -p vcf "$OUT/calls.filt.vcf.gz"

# 3) Bi-allelic SNPs suitable for phylogeny/GWAS (low missing, minor allele count)
bcftools view -m2 -M2 -v snps -i "F_MISSING<=${MAX_MISSING} && MAC>=${MIN_MAC}" -Oz \
  -o "$OUT/snps.biallelic.vcf.gz" "$OUT/calls.filt.vcf.gz"
tabix -f -p vcf "$OUT/snps.biallelic.vcf.gz"

# 4) Compact genotype matrix (one SNP per row, one GT column per sample)
#    -H keeps a labelled header row identifying each sample column.
bcftools query -H -f '%CHROM\t%POS\t%REF\tALT\t[%GT\t]\n' "$OUT/snps.biallelic.vcf.gz" > "$OUT/snp_geno_matrix.tsv"

bcftools stats "$OUT/snps.biallelic.vcf.gz" > "$OUT/snps.bcfstats.txt"
NS=$(grep -c '^[^#]' "$OUT/snp_geno_matrix.tsv" || true)
echo "[done] $NS bi-allelic SNP sites in $OUT/snps.biallelic.vcf.gz and snp_geno_matrix.tsv"
echo "Next: module 13 GWAS (13.2 plink / 13.3 pyseer), or convert with snp-sites for an ML tree."
