# EasyWGS worked example: a multi-pathogen demonstration panel

This directory runs the whole EasyWGS workflow on real, public bacterial
isolates so that every figure and table in the Application section can be
reproduced with one command. The panel is deliberately small but broad: it
covers five major pathogen groups rather than a single organism, includes both
short-read and hybrid (Illumina plus Oxford Nanopore) isolates, and adds a
twelve-isolate temporal *Salmonella* collection for the collection-level
analyses (pangenome, core-SNP phylogeny, time-scaled tree, genotype-phenotype
association) that cannot be demonstrated with one genome.

No sequencing reads are stored in git. The accessions in `panel.tsv` are
verified against the ENA Portal API and are downloaded on demand, then
downsampled so the tutorial runs on an ordinary analysis server.

## Panel design

| Pathogen group | `species` code | Tier-1 short read | Hybrid pair | Tier-2 short reads | Tier-3 extra |
|---|---|---|---|---|---|
| *Salmonella enterica* | `salm` | SE_IT_2011_1 | SE_HY_JP_2010 | 3 | 12-isolate 1992-2017 temporal set (Italy, Japan) |
| *Klebsiella pneumoniae* | `kpsc` | KP_GR_2011 | KP_HY_JP_2015 | 3 | - |
| *Escherichia coli* | `ecoli` | EC_BE_2015 | EC_HY_JP_2015 | 3 (incl. O26) | - |
| *Listeria monocytogenes* | `listeria` | LM_AT_2013 | LM_HY_DE_2019 | 3 | - |
| *Shigella* spp. | `ecoli` | SS_FR_2010 (S. sonnei) | SD_HY_HU_1954 (S. dysenteriae) | 3 (sonnei, flexneri) | - |

Tiers are nested.

- Tier 1, 10 samples: one short-read and one hybrid isolate per group. This is
  the fastest route and exercises every per-isolate module and the assembly and
  mapping routes.
- Tier 2, 20 samples: three short-read isolates per group, giving realistic
  serotyping, MLST and AMR breadth across five groups.
- Tier 3, 29 samples: the full panel. The 13 *Salmonella* genomes (12 short
  reads spanning 1992 to 2017 plus the hybrid) drive pangenome, core-SNP,
  TreeTime molecular-clock and ancestral-location analysis and the GWAS
  demonstration.

Each row of `panel.tsv` records the Illumina and ONT run accessions, the
BioSample that proves a hybrid pair is one isolate, country, collection date,
scientific name and an accession-verified RefSeq complete reference.

## Prerequisites

Install the software environments and the databases once.

```bash
bash 00_install/install_env.sh
DBROOT=$HOME/easywgs_db bash 00_install/download_db.sh
```

The panel needs the CheckM2, GUNC and Bakta databases. The Kraken2 standard
database and FCS-GX are optional for the worked example; module 02 runs without
them and skips the composition scout. The spike-in uses `art_illumina`
(bioconda package `art`) and `bwa`, both included in the `easywgs` environment.
To reuse a shared CheckM2 database instead of downloading it, export
`CHECKM2_DB` (the `uniref100.KO.1.dmnd` file or its `CheckM2_database`
directory) before running `download_db.sh`; module 04 and the spike-in then use
that copy directly. See the Installation chapter of the guidebook for the
resumable download option.

## Run the panel

```bash
# 1. Generate tier configs, download reads and references, downsample Illumina
EXAMPLE_PAIRS=800000 bash examples/00_download_panel.sh 1

# 2. Run QC, decontamination, assembly, QC, annotation, typing, AMR, pangenome,
#    phylogeny, dating, GWAS and reporting end to end
bash examples/01_run_panel.sh 1

# 3. Controlled two-layer decontamination validation (Fig. 4)
bash examples/02_run_spikein.sh
```

Replace `1` with `2` or `3` for the broader tiers. `EXAMPLE_PAIRS` sets the
number of matched read pairs kept per Illumina isolate (default 800000, roughly
50-fold for a 5 Mb genome at 150 bp); set it higher for full-depth assemblies.
ONT reads are kept whole because module 01b applies Filtlong target-base
filtering. Downloads are resumable and already-finished files are skipped.

If an ENA run has no direct FASTQ mirror in your region, fall back to the SRA
toolkit for that accession:

```bash
fasterq-dump --threads 8 --outdir 00_rawdata <RUN_ACCESSION>
gzip 00_rawdata/<RUN_ACCESSION>_*.fastq
# then rename to 00_rawdata/<id>_R1.fastq.gz and _R2.fastq.gz
```

## Outputs

- `99_report/master_table.tsv`: per-isolate assembly, MLST, serotype, CheckM2
  and resistance summary merged by `99_report/merge_results.py`.
- `examples/results/panel_metrics.tsv`: panel metadata joined to the headline
  per-isolate metrics.
- `examples/results/collection_stats.tsv` and `panel_summary.md`:
  collection-level numbers (pangenome core and singleton clusters, core-SNP
  alignment size, pairwise SNP range, clock-rate line, GWAS hits).
- `examples/results/expected_check.tsv`: PASS/WARN/FAIL against
  `expected/expected_results.tsv`. WARN means a module has not run yet; FAIL
  marks a measured value outside the expected band.
- `examples/spikein/results/spikein_metrics.tsv` and
  `Fig_spikein.{png,pdf,svg}`: the decontamination validation.

Numbers are written only by the run. The metric collectors record NA for any
module that has not executed rather than estimating a value, so the manuscript
must quote these files after a real run instead of using placeholder figures.

## The decontamination spike-in

The target is the tier-1 *E. coli* isolate EC_BE_2015. Two contaminant classes
are added at 1, 5 and 10 percent of target read pairs: PhiX (NC_001422), whose
reads are simulated with ART to emulate an Illumina technical control, and real
reads from the phylogenetically distant *K. pneumoniae* isolate KP_GR_2011 as a
near-source contaminant. For each mixture the workflow reports the read-level
fraction mapping to target and contaminant before and after a transparent
bwa/samtools map-and-filter removal, plus assembly size, N50 and CheckM2 scores
for baseline, spiked-10 percent and cleaned-10 percent. This map-and-filter
step is the auditable benchmark; production decontamination uses CLEAN in
module 02 and FCS-GX at the assembly level, which apply the same reference and
k-mer principle with maintained databases. Host (human) removal is exercised
through CLEAN `--host hsa` on real clinical reads and is not simulated here
because it requires the large host reference.

## Collection-level analysis on tier 3

The twelve short-read *Salmonella* isolates come from one study (PRJDB6430) and
span 1992 to 2017 across Japan and Italy, which gives a genuine time and country
structure. Module 08 builds the pangenome, module 09 calls core SNPs and builds
the phylogeny, module 10 runs TreeTime for the molecular clock and ancestral
location, and module 13 runs Scoary, PLINK and pyseer. Year-only ENA dates are
placed at mid-year in `metadata_dates.csv` and flagged in the
`date_precision` column.

The immediately usable binary trait is Italian versus non-Italian origin, a
real and reproducible metadata field that provides two classes for the
association demonstration. It is not a measured phenotype. After module 07,
`scripts/derive_mdr_traits.py` adds `MDR_genotypic`, set to 1 when acquired AMR
genes span at least three distinct AMRFinderPlus drug classes; module 13 can
then be rerun with `TRAIT=MDR_genotypic`. For a real study replace both with
measured susceptibility results in `config/traits.csv`.

## Using your own isolates

Replace the panel with your own data by placing reads in `00_rawdata/`
(`<id>_R1.fastq.gz`, `<id>_R2.fastq.gz`, and `<id>_ONT.fastq.gz` for hybrid or
long-read runs) and editing `config/my_samples.csv` following the column guide
in `config/samplesheet.csv`. Keep one species per collection-level run when
building pangenomes and association tests.

## Data sources

| Group | Source study |
|---|---|
| *Salmonella* temporal and hybrid | PRJDB6430 / DRP004007 (DDBJ/ENA) |
| *K. pneumoniae* | PRJDB4948 / DRP004119 |
| *E. coli* | PRJDB5579, PRJDB5136, PRJDB3552 / DRP004119 |
| *L. monocytogenes* | PRJEB56155 / ERP150987 |
| *Shigella* spp. | PRJEB12097, PRJEB71076, PRJEB73590 / SRP292271 |

Reference genomes: *Salmonella* LT2 GCF_000006945, *K. pneumoniae* MGH78578
GCF_000016305, *E. coli* K-12 MG1655 GCF_000005845, *L. monocytogenes* EGD-e
GCF_000196035, *S. flexneri* GCF_000006925, *S. sonnei* GCF_000283715 and
*S. dysenteriae* GCF_022354085. The Shigella references are recorded by species
and accession only; see `panel.tsv` for the local label used by each isolate.
PhiX is NC_001422. Please cite the original studies and the ENA/SRA accessions in
addition to EasyWGS.
