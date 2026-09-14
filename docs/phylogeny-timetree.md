# Phylogeny and time tree

Module 09 builds a core-SNP phylogeny and module 10 uses TreeTime on that tree for molecular
dating and ancestral-state inference.

## Core-SNP phylogeny (09)

Using the common reference specified in the samplesheet, snippy calls variants per sample and
snippy-core merges the whole-site alignment. Recombination creates many false SNPs, so
Gubbins removes it before extracting invariant-informative sites:

```bash
snippy --cpus 16 --ref ref.gbk --out snippy/$id --R1 R1.fq.gz --R2 R2.fq.gz   # or --ctgs assembly
snippy-core --ref ref.gbk snippy/*
run_gubbins.py --prefix gubbins core.full.aln
snp-sites -c gubbins.filtered_polymorphic_sites.fasta > core_snps.fasta
iqtree3 -s core_snps.fasta -m GTR+G4 -bb 1000 -nt 16
snp-dists core.full.aln > snp_distance.tsv
```

For outbreak-scale analysis, also report the pairwise SNP distance matrix to delineate
transmission clusters. The model can be chosen automatically with ModelFinder; FastTree
gives a quick preview for large sets while IQ-TREE 3 is used for the final figure.

## Time tree (10, TreeTime)

A tree can be dated only when it carries sampling dates, taken from the samplesheet date
column. First run the clock regression to screen outliers, then infer the time tree,
ancestral sequences, homoplasies and state migration:

```bash
treetime clock       --tree nwk --aln aln --dates metadata_dates.csv --clock-filter 3
treetime             --tree nwk --aln aln --dates metadata_dates.csv --reroot least-squares
treetime ancestral   --tree nwk --aln aln --outdir ancestral
treetime homoplasy   --tree nwk --aln aln --outdir homoplasy
treetime mugration  --tree nwk --states country.csv --attribute country --outdir geo
```

Samples that clearly deviate in the clock regression should be checked for date and branch
position first rather than deleted. With weak clock signal (low correlation between
root-to-tip distance and date), soften the time-tree claims and report relative order rather
than absolute ages.

## Interpretation and figures

Annotate the phylogeny with multiple tracks of SNP distance, clonal group, serotype,
resistance phenotype and location; the time tree shows the most recent common ancestor ages
and geographic migration on a time axis. A transmission claim requires concordant tree
topology, SNP/cgMLST distance and epidemiological timeline; adjacency in a tree alone is not
enough to assert direct transmission.
