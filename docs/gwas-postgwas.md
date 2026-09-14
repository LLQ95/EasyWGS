# Microbial GWAS and post-GWAS (module 13)

Module 13 extends EasyWGS from characterization to genotype-to-phenotype
association. It offers three complementary bacterial GWAS layers, Scoary for
gene presence/absence, PLINK for SNP association, and pyseer for both genes and
SNPs with an explicit model of clonal population structure, followed by one
shared post-GWAS step that corrects for multiple testing, draws QQ and
Manhattan plots and consolidates significant hits. Bacterial genomes are
strongly clonal, so association results must always be interpreted together
with the phylogeny rather than by raw p-values alone.

## Preparing the phenotype table

Phenotypes live in `config/traits.csv`. The first column `Name` must equal the
samplesheet `id` and the isolate names used in the pangenome, every further
column is one trait. Scoary uses binary traits coded 0 and 1; PLINK and pyseer
also accept numeric continuous traits; unknown values use NA. The active trait
is chosen with the `TRAIT` variable and defaults to MDR.

```bash
TRAIT=ESBL bash 13_gwas/13.run_gwas.sh       # run every layer for one trait
bash 13_gwas/13.4.post_gwas.R "$(pwd)"       # post-GWAS step alone
```

## 13.1 Gene-based pan-GWAS with Scoary

Scoary tests each gene in the Panaroo or Roary
`gene_presence_absence.csv` against every binary trait using Fisher's exact
test, adds population-aware pairwise comparisons, and controls the false
discovery rate with Benjamini-Hochberg correction. A Bonferroni family-wise
option (`-c B`) is available for stricter confirmatory tests, and label
permutations provide empirical p-values.

```bash
bash 13_gwas/13.1.scoary.sh
scoary -t config/traits.csv -g 08_pangenome/.../gene_presence_absence.csv \
       -o 13_gwas/scoary -c BH -p 0.05 -n 1000 --threads 8
```

Gene-based tests are the first choice when phenotype is plausibly driven by the
accessory genome, such as acquired resistance genes, capsules or pathogenicity
islands, because they operate on gene content regardless of a reference.

## 13.2 SNP association with PLINK

The bi-allelic SNP VCF from module 12.2 is converted to PLINK binary files.
Because human-style random-mating assumptions do not hold for a clonal panel,
the script first builds an IBS-based MDS projection and then includes its axes
as covariates in a case-control logistic or continuous linear regression, in
addition to a fast unadjusted allelic test for comparison.

```bash
TRAIT=MDR bash 13_gwas/13.2.plink.sh
plink --vcf snps.biallelic.vcf.gz --make-bed --double-id --allow-extra-chr \
      --set-missing-var-ids @:# --out base
plink --bfile base --allow-extra-chr --cluster --mds-plot 4 --out mds
plink --bfile base --allow-extra-chr --pheno pheno.txt --1 \
      --covar covar_mds.txt --logistic hide-covar --adjust --ci 0.95 \
      --out assoc_logistic
```

A signal that disappears after adding the MDS axes, or that sits on one clonal
branch, is most likely a lineage marker rather than a causal variant.

## 13.3 Gene and SNP GWAS with pyseer

pyseer is a microbial reimplementation of the SEER framework and accepts
several feature types in one consistent statistical model. The script runs
gene-level tests from the pangenome binary matrix and SNP-level tests from the
module-12 VCF, using a pairwise distance matrix (the module-09 SNP distance
matrix, or a Mash matrix) as a distance kernel to control population structure
with a linear mixed model. An optional k-mer/unitig route is provided as
commented commands for annotation-free causal-marker discovery.

```bash
TRAIT=MDR bash 13_gwas/13.3.pyseer.sh
pyseer --phenotypes pheno.tsv --presence gene_presence_absence.Rtab \
       --distances snp_dists.tsv --min-af 0.02 --max-af 0.98 --cpu 4 \
       --output assoc_genes.txt
pyseer --phenotypes pheno.tsv --vcf snps.biallelic.vcf.gz \
       --distances snp_dists.tsv --min-af 0.02 --cpu 4 --output assoc_snps.txt
```

Allele-frequency bounds remove near-fixed or singleton features that carry no
contrast; tighten them for small panels. pyseer reports effect size (beta),
standard error and likelihood-ratio p-values, and can estimate variance
explained by the lineage kernel as a diagnostic of clonal confounding.

## 13.4 Shared post-GWAS analysis

`13.4.post_gwas.R` reads whichever result files exist, recomputes
Benjamini-Hochberg and Bonferroni adjusted p-values, draws a QQ plot for each
method and layer, draws Manhattan plots for position-coded SNPs (with the
genome-wide and study-specific FDR lines), and writes a combined ranked table of
FDR-significant features. QQ inflation and a strong leftward shift indicate
residual population structure that the chosen correction did not remove.

```bash
Rscript 13_gwas/13.4.post_gwas.R /path/to/EasyWGS
```

## Interpretation and limits

Small clonal panels often yield no FDR-significant hit, and this is a valid
result rather than a failure. Significance should be supported by effect size
and by independence from lineage, by replication in a second panel, and by a
biological mechanism from the module 05 annotation or external databases.
Common confounders that should be balanced across trait groups include host,
country, year and sequencing platform. Concordant hits from a gene method
(Scoary or pyseer genes) and a SNP method are considerably more persuasive than
a single-layer result.

## Outputs

| Path | Content |
| --- | --- |
| `13_gwas/scoary/<trait>.csv` | per-gene naive, BH and pairwise p-values with odds ratios |
| `13_gwas/plink/*.assoc*` | allelic and covariate-adjusted regression results |
| `13_gwas/plink/mds.mds` | IBS axes used as structure covariates |
| `13_gwas/pyseer/assoc_genes.txt` / `assoc_snps.txt` | gene and SNP associations with beta and LRT p |
| `13_gwas/post/qq_*.pdf` / `.png` | QQ plots per method and layer |
| `13_gwas/post/manhattan_*.pdf` / `.png` | Manhattan plots for SNP results |
| `13_gwas/post/*_FDRhits.csv`, `combined_FDRhits.csv` | corrected significant-feature tables |
