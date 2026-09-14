# Quick start

This chapter walks through the full chain with a minimal example. The working directory is
assumed to be the repository root.

## 1. Place the raw data

Put raw FASTQ files in `00_rawdata/`. Name paired short reads `ID_R1.fastq.gz` and
`ID_R2.fastq.gz`; name long reads, for example, `ID_ONT.fastq.gz` or choose a custom name
and record it in the samplesheet.

## 2. Fill in the samplesheet

```bash
cp config/samplesheet.csv config/my_samples.csv
```

Column definitions are given in Inputs and samplesheet. `config/my_samples.csv` is listed
in .gitignore, so private paths are not committed by accident.

## 3. Run everything or run step by step

```bash
# Whole chain from QC to summary
bash run_all.sh config/my_samples.csv

# Resume from a given step, for example rerun from typing (06) onward
bash run_all.sh config/my_samples.csv 06
```

You can also enter a single folder and run its script manually while debugging:

```bash
bash 01_qc/01.fastp.sh
bash 01_qc/01b.long_qc.sh     # works only for long/hybrid samples, skipped for short-only
bash 02_decontam_reads/02.clean_reads.sh
bash 03_assembly/03.assemble.sh
```

## 4. Inspect the key outputs

| Stage | Key output | What to check |
| --- | --- | --- |
| 03 assembly | `03_assembly/genomes/{id}.fasta`, genome_stats.tsv | contig count, N50, total length versus same-species expectation |
| 04 gate | CheckM2 completeness/contamination, GUNC score | completeness, contamination, CSS and clade separation |
| 06 typing | MLST, serotype, cgMLST allele files | ST, K/O or O:H, allele profile |
| 09–10 | phylogenetic and time trees | topology, clock outliers, date consistency |
| 99 | `99_report/master_table.tsv` | one merged row per isolate |

## 5. A short-read example

Set `platform=illumina` and provide R1/R2. The workflow assembles with Unicycler by
default (friendlier to plasmids and circularization for a single isolate) and you can
switch to `spades.py --isolate` inside the 03 script when needed.

## 6. A hybrid example

Set `platform=hybrid` and provide both paired short reads and long reads. The workflow
runs `unicycler --mode bold`, using long reads for the scaffold and short reads for
correction, followed by one Pilon pass. Hybrid assembly is usually closest to a finished
genome, but the short reads must be decontaminated first, otherwise long reads amplify
contamination into complete but erroneous contigs.
