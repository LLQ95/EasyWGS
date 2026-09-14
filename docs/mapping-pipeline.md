# Reference mapping and variant calling (module 12)

Module 12 implements the reference-based route as transparent BAM and VCF
steps, without wrapping them inside another tool. It is independent of module
03 assembly and of module 09 (which uses snippy); module 09 remains a convenient
all-in-one core-SNP workflow, while module 12 exposes each intermediate file so
that alignments and genotype likelihoods can be inspected directly.

## Inputs

The module reads `config/my_samples.csv`. The `reference` column must point to a
single shared FASTA genome for the whole batch (the mapping route does not use
GenBank files). The `platform` column selects the aligner: Illumina and hybrid
samples use paired short reads with BWA-MEM, while ONT and PacBio samples use
minimap2 with `map-ont` or `map-pb` presets on their long reads.

## Step 12.1: align reads to the reference

The reference is indexed once with `samtools faidx` and `bwa index`. Each sample
is aligned, sorted and indexed, and receives a flagstat report and a per-base
depth table.

```bash
bash 12_mapping_pipeline/12.1.map_reads.sh
# short reads
bwa mem -t 8 -R "@RG\tID:ST001\tSM:ST001\tPL:ILLUMINA" ref.fa R1.fq.gz R2.fq.gz \
  | samtools sort -@8 -o bam/ST001.sorted.bam -
samtools index bam/ST001.sorted.bam
# long reads (ONT)
minimap2 -ax map-ont -t 8 ref.fa reads.fq.gz | samtools sort -@8 -o bam/ST001.sorted.bam -
```

The coverage summary `12_mapping_pipeline/qc/coverage_summary.tsv` reports mean
depth, breadth at 1x and 10x, and the percentage of mapped reads for every
sample. A low breadth of coverage usually means the reference is too distant,
whereas a high breadth with uneven depth can flag repeated regions or mixed
contamination. Qualimap BAM QC runs automatically when it is installed.

## Step 12.2: joint variant calling

All BAM files are genotyped jointly with bcftools, normalized against the
reference, filtered by quality and depth, and reduced to a low-missing,
bi-allelic SNP set.

```bash
bash 12_mapping_pipeline/12.2.call_variants.sh
bcftools mpileup -q 20 -Q 20 -a AD,DP -f ref.fa -b bam.list -Ou \
  | bcftools call -mv -Oz -o calls.raw.vcf.gz
bcftools norm -f ref.fa -Oz -o calls.norm.vcf.gz calls.raw.vcf.gz
bcftools filter -e 'QUAL<20 || FMT/DP<4' -s LowQual -Oz -o calls.filt.vcf.gz calls.norm.vcf.gz
bcftools view -m2 -M2 -v snps -i 'F_MISSING<=0.1 && MAC>=2' -Oz -o snps.biallelic.vcf.gz calls.filt.vcf.gz
bcftools query -H -f '%CHROM\t%POS\t%REF\t%ALT\t[%GT\t]\n' snps.biallelic.vcf.gz > snp_geno_matrix.tsv
```

The filtering thresholds (minimum quality, maximum missingness, minimum minor
allele count) are declared at the top of the script and should be tuned to the
sequencing depth and panel size. The raw and normalized VCFs keep indels and
multiallelic sites for detailed inspection, while the bi-allelic SNP VCF feeds
module 13 and any reference-based phylogeny.

## Building a reference-based SNP tree without assembly

The bi-allelic VCF can be converted to a multiple sequence alignment and used
directly for a maximum-likelihood tree, which is useful when assemblies are not
available.

```bash
zcat 12_mapping_pipeline/variants/snps.biallelic.vcf.gz > snps.vcf
vcf2phylip -i snps.vcf -f                  # writes snps.min4.fasta
iqtree3 -s snps.min4.fasta -m GTR+G4 -alrt 1000 -bb 1000 -pre map_snp_tree
snp-dists snps.min4.fasta > map_snp_dists.tsv
```

## Outputs

| Path | Content |
| --- | --- |
| `12_mapping_pipeline/bam/{id}.sorted.bam(.bai)` | sorted, indexed alignments with read groups |
| `12_mapping_pipeline/qc/{id}.flagstat` | alignment summary per sample |
| `12_mapping_pipeline/qc/{id}.depth` | per-reference-base depth |
| `12_mapping_pipeline/qc/coverage_summary.tsv` | mean depth, breadth, mapped percentage |
| `12_mapping_pipeline/variants/calls.raw.vcf.gz` | all jointly called variants |
| `12_mapping_pipeline/variants/calls.norm.vcf.gz` | left-aligned normalized calls |
| `12_mapping_pipeline/variants/snps.biallelic.vcf.gz` | filtered bi-allelic SNPs for module 13 / trees |
| `12_mapping_pipeline/variants/snp_geno_matrix.tsv` | genotype matrix, one column per sample |
