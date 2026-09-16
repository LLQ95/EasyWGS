# Worked example: a multi-pathogen public panel

This chapter runs the whole EasyWGS workflow on real, public bacterial isolates so
that every result in the Application section of the accompanying manuscript can be
reproduced with a small number of commands. The panel is deliberately small but
broad. It covers five major pathogen groups rather than a single organism, includes
both short-read and matched hybrid (Illumina plus Oxford Nanopore) isolates, and adds
a twelve-isolate temporal *Salmonella* collection for the collection-level analyses
(pangenome, core-SNP phylogeny, time-scaled tree and genotype-phenotype association)
that cannot be demonstrated with one genome.

No sequencing reads are stored in the repository. All accessions in
[`examples/panel.tsv`](https://github.com/LLQ95/EasyWGS/blob/main/examples/panel.tsv)
were checked against the ENA Portal and NCBI, and the reads are downloaded on demand
and then downsampled so that the tutorial runs on an ordinary analysis server.

## Panel design

| Pathogen group | `species` code | Tier-1 short read | Hybrid pair | Tier-2 short reads | Tier-3 extra |
| --- | --- | --- | --- | --- | --- |
| *Salmonella enterica* | `salm` | SE_IT_2011_1 | SE_HY_JP_2010 | 3 | 12-isolate 1992-2017 temporal set (Italy, Japan) |
| *Klebsiella pneumoniae* | `kpsc` | KP_GR_2011 | KP_HY_JP_2015 | 3 | - |
| *Escherichia coli* | `ecoli` | EC_BE_2015 | EC_HY_JP_2015 | 3 (incl. O26) | - |
| *Listeria monocytogenes* | `listeria` | LM_AT_2013 | LM_HY_DE_2019 | 3 | - |
| *Shigella* spp. | `ecoli` | SS_FR_2010 (S. sonnei) | SD_HY_HU_1954 (S. dysenteriae) | 3 (sonnei, flexneri) | - |

The three tiers are nested subsets of one panel.

- Tier 1 contains ten samples, one short-read and one hybrid isolate per group; it is
  the fastest route and exercises every per-isolate module and both analysis routes.
- Tier 2 contains twenty samples, three short-read isolates per group, and gives
  realistic serotyping, MLST and resistance breadth across the five groups.
- Tier 3 contains twenty-nine samples. The thirteen *Salmonella* genomes (twelve
  short-read isolates spanning 1992 to 2017 plus the hybrid) drive the pangenome,
  core-SNP, TreeTime molecular-clock and ancestral-location analyses and the GWAS
  demonstration.

Each row of `panel.tsv` records the Illumina and ONT run accessions, the BioSample
that confirms a hybrid pair is one isolate, country, collection date, scientific name
and an accession-verified RefSeq complete reference.

## Prerequisites

Create the software environments and download the databases once, as described in
[Installation](installation.md).

```bash
bash 00_install/install_env.sh
DBROOT=$HOME/easywgs_db bash 00_install/download_db.sh
```

The panel needs the CheckM2, GUNC and Bakta databases. The Kraken 2 standard database
and FCS-GX are optional for the worked example, and module 02 runs without them and
skips the composition scout. The spike-in uses `art_illumina` (Bioconda package `art`)
and `bwa`, both included in the `easywgs` environment. To reuse shared databases
instead of downloading them, export `CHECKM2_DB`, `BAKTA_DB`, `EGGNOG_DB` or
`GUNC_DB` as appropriate before running `download_db.sh`; see
[Installation](installation.md) for the paths each variable expects and the resumable
download option.

## Run the panel

```bash
# 1. Generate tier configs, download reads and references, and downsample Illumina
EXAMPLE_PAIRS=800000 bash examples/00_download_panel.sh 1

# 2. Run QC, decontamination, assembly, quality gate, annotation, typing, AMR,
#    pangenome, phylogeny, dating, GWAS and reporting end to end
bash examples/01_run_panel.sh 1

# 3. Run the controlled two-layer decontamination validation (manuscript Figure 4)
bash examples/02_run_spikein.sh
```

Replace the trailing `1` with `2` or `3` for the broader tiers. `EXAMPLE_PAIRS` sets
the number of matched read pairs kept per Illumina isolate (the default of 800,000 is
roughly 50-fold for a 5 Mb genome at 150 bp); raise it for full-depth assemblies. ONT
reads are kept whole because module 01b applies Filtlong target-base filtering.
Downloads are resumable and already-finished files are skipped.

If an ENA run has no direct FASTQ mirror in your region, fall back to the SRA toolkit
for that accession:

```bash
fasterq-dump --threads 8 --outdir 00_rawdata <RUN_ACCESSION>
gzip 00_rawdata/<RUN_ACCESSION>_*.fastq
# then rename to 00_rawdata/<id>_R1.fastq.gz and 00_rawdata/<id>_R2.fastq.gz
```

## Outputs and the expected-result checker

- `99_report/master_table.tsv` merges the per-isolate assembly, MLST, serotype,
  CheckM2 and resistance summaries through `99_report/merge_results.py`.
- `examples/results/panel_metrics.tsv` joins panel metadata to the headline
  per-isolate metrics, and `collection_stats.tsv` with `panel_summary.md` report
  collection-level numbers such as pangenome core and singleton clusters, core-SNP
  alignment size, pairwise SNP range, the clock-rate line and GWAS hits.
- `examples/results/expected_check.tsv` reports PASS, WARN or FAIL against
  `examples/expected/expected_results.tsv`. WARN means a module has not run yet, and
  FAIL marks a measured value outside its expected band.

The metric collectors write NA for any module that has not executed rather than
estimating a value, so the manuscript and guidebook quote these files after a real run
instead of using placeholder figures.

## The decontamination spike-in

The target is the tier-1 *E. coli* isolate EC_BE_2015. Two contaminant classes are
added at one, five and ten percent of target read pairs: PhiX (NC_001422), whose reads
are simulated with ART to emulate an Illumina technical control, and real reads from
the *K. pneumoniae* isolate KP_GR_2011 as a harder, near-source contaminant. For each
mixture the workflow reports the read-level fraction mapping to target and contaminant
before and after a transparent bwa/samtools map-and-filter removal, together with
assembly size, N50 and CheckM2 scores for the baseline, spiked-ten-percent and
cleaned-ten-percent libraries. This map-and-filter step is the auditable benchmark;
production decontamination uses CLEAN in module 02 and FCS-GX at assembly level, which
apply the same reference and k-mer principle with maintained databases. The four-panel
figure is written to `examples/spikein/results/Fig_spikein.{png,pdf,svg}`.

## Collection-level analysis on tier 3

The twelve short-read *Salmonella* isolates come from one study (PRJDB6430) and span
1992 to 2017 across Japan and Italy, which gives genuine time and country structure.
Module 08 builds the pangenome, module 09 calls core SNPs and builds the phylogeny,
module 10 runs TreeTime for the molecular clock and ancestral location, and module 13
runs Scoary, PLINK and pyseer. Year-only ENA dates are placed at mid-year in
`metadata_dates.csv` and flagged in the `date_precision` column.

The immediately usable binary trait is Italian versus non-Italian origin, a real and
reproducible metadata field that supplies two classes for the association
demonstration; it is not a measured phenotype. After module 07,
`scripts/derive_mdr_traits.py` adds `MDR_genotypic`, set to 1 when acquired resistance
genes span at least three distinct AMRFinderPlus drug classes, and module 13 can then
be rerun with `TRAIT=MDR_genotypic`. For a real study, replace both traits with
measured susceptibility results in `config/traits.csv`.

## Using your own isolates

Place reads in `00_rawdata/` as `<id>_R1.fastq.gz`, `<id>_R2.fastq.gz` and, for hybrid
or long-read runs, `<id>_ONT.fastq.gz`, then edit `config/my_samples.csv` following the
column guide in [Inputs and samplesheet](samplesheet.md). Keep one species per
collection-level run when building pangenomes and association tests.

## Data sources

| Group | Source study |
| --- | --- |
| *Salmonella* temporal and hybrid | PRJDB6430 / DRP004007 (DDBJ/ENA) |
| *K. pneumoniae* | PRJDB4948 / DRP004119 |
| *E. coli* | PRJDB5579, PRJDB5136, PRJDB3552 / DRP004119 |
| *L. monocytogenes* | PRJEB56155 / ERP150987 |
| *Shigella* spp. | PRJEB12097, PRJEB71076, PRJEB73590 / SRP292271 |

Reference genomes and the PhiX control are listed with their RefSeq and GenBank
accessions in [`examples/panel.tsv`](https://github.com/LLQ95/EasyWGS/blob/main/examples/panel.tsv).
Please cite the original studies and the ENA/SRA accessions in addition to EasyWGS.
The full step-by-step notes, including every output file, are maintained in
[`examples/README.md`](https://github.com/LLQ95/EasyWGS/blob/main/examples/README.md).
