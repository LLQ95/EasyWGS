# Pangenome

Pangenome analysis corresponds to module 08. Panaroo clusters homologous genes across
isolates and reports core, accessory and unique genes; Roary is an alternative for smaller,
consistently annotated datasets.

## Input preparation

Panaroo reads the Prokka GFF of each sample directly, and annotation versions and the
genetic code must be consistent. Place the GFF files in one folder or list them with a
wildcard:

```bash
panaroo -i prokka/*/*.gff -o panaroo_out --clean-mode strict \
        --core_threshold 0.98 -a core --threads 16
```

Strict mode introduces fewer merging errors and suits closely related clonal groups; use
moderate for more divergent samples. Before analysis, remove contaminated genomes with mash
or CheckM2 and dereplicate near-duplicate genomes with dereplicator or cd-hit, so repeated
samples do not dominate the core-gene estimate.

## Outputs and downstream use

`gene_presence_absence.csv` gives the distribution of each gene cluster across samples, and
`core_gene_alignment` is the core-gene alignment that can feed module 09 or a standalone
tree. Plotting the growth of core and accessory counts against sample number gives a
rarefaction curve that indicates whether sampling saturates the pangenome.

## Relation to phylogeny

The core-gene alignment suits moderately divergent samples, while core SNPs suit closely
related outbreaks; the two meet in module 09. The accessory presence/absence matrix can also
be associated with phenotype as input to later GWAS, but such association needs adequate
sample size and multiple-testing correction and is not part of the default workflow.
