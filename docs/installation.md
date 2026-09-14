# Installation

The workflow runs on Linux, WSL2 and HPC systems, with dependencies managed through
conda (mamba recommended). Environments are split by purpose so that large databases and
heavy dependencies do not conflict.

## 1. Prepare conda

If conda is not installed, start with Miniforge or Miniconda and consider replacing
`conda` with the faster `mamba`. Add the bioconda and conda-forge channels:

```bash
conda config --add channels conda-forge
conda config --add channels bioconda
```

## 2. Create the environments

```bash
bash 00_install/install_env.sh
```

The script creates the following environments:

| Environment | Purpose |
| --- | --- |
| easyisolate | Main environment: QC, short/long assembly, typing, comparison, phylogeny |
| longread | Medaka polishing and Trycycler consensus (heavy, kept separate) |
| checkm2 | Assembly completeness and contamination |
| gunc | Assembly chimerism detection |
| bakta | Genome annotation (large database) |
| eggnog | GO/KEGG/COG functional annotation |

CLEAN is a Nextflow pipeline; once nextflow is installed, the setup script runs
`nextflow pull rki-mf1/clean`, so no separate environment is needed.

## 3. Download databases

```bash
# Open the script first and point DBROOT to a large, ideally shared disk
bash 00_install/download_db.sh
```

Databases are downloaded once and shared across projects. They include the abricate
databases, AMRFinder data, the Kraken2 database, the CheckM2 model, the GUNC reference
set, Bakta and eggNOG databases and the chewBBACA schemas.

## 4. Hardware and optional components

Short-read analysis of several hundred isolates runs on 16 threads and 64 GB RAM. Flye and
CheckM2 raise memory use, so 128 GB is preferable. Running NCBI FCS-GX locally requires
about 470 GB of reference data and, per the official recommendation, about 512 GB RAM.
When this is not available, keep the CheckM2 and GUNC gates and run FCS-GX online on
usegalaxy.org instead; this route is already anticipated by the workflow.

## 5. Verify the installation

```bash
conda activate easyisolate
fastp --version; unicycler --version; flye --version; mlst --version
conda activate checkm2 && checkm2 --version
```

Returning a version for each command indicates that the main chain is usable. Exact
versions do not need to match this guide, but the long-read polishing chain (Medaka and
Racon) and the assemblers should be recorded in the project log for reproducibility.
