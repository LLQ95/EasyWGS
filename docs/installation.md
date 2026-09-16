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
| easywgs | Main environment: QC, short/long assembly, typing, comparison, phylogeny |
| longread | Medaka polishing and Trycycler consensus (heavy, kept separate) |
| checkm2 | Assembly completeness and contamination |
| gunc | Assembly chimerism detection |
| bakta | Genome annotation (large database) |
| eggnog | GO/KEGG/COG functional annotation |

CLEAN is a Nextflow pipeline; once nextflow is installed, the setup script runs
`nextflow pull rki-mf1/clean`, so no separate environment is needed.

The installer is idempotent: rerunning it skips an environment that already exists and
creates only the missing ones, which is useful after a partial install. The main
environment name defaults to `easywgs` and can be overridden with `EASYWGS_ENV`; every
module activates `${EASYWGS_ENV:-easywgs}`, so a workstation that keeps the main tools in
another environment can point the workflow at it (for example
`EASYWGS_ENV=isolateqc bash 00_install/install_env.sh`).

## 3. Download databases or point at shared copies

Databases are downloaded once and shared across projects. Set `DBROOT` to a large,
ideally shared disk before running the downloader (the default is `~/easywgs_db`):

```bash
DBROOT=/data/shared/easywgs_db bash 00_install/download_db.sh
```

The downloader includes the abricate databases, AMRFinder data, the CheckM2 model, the
GUNC reference set, Bakta and eggNOG databases and the chewBBACA schemas. It is safe to
rerun, and completed items are skipped.

### Reuse an existing CheckM2 database

The CheckM2 database is about 1.7 GB and the one-shot Zenodo download can break on an
unstable link. If your cluster already has a copy, export `CHECKM2_DB` and the downloader
skips the download while module 04 and the spike-in example use the shared file directly.
`CHECKM2_DB` accepts either the `uniref100.KO.1.dmnd` file itself or the
`CheckM2_database` directory that contains it:

```bash
# point at the file (or at the CheckM2_database directory)
export CHECKM2_DB=/db/student/metagenome/checkm_db/checkm2_database/CheckM2_database/uniref100.KO.1.dmnd
DBROOT=/data/shared/easywgs_db bash 00_install/download_db.sh   # CheckM2 is now skipped
```

Add the `export CHECKM2_DB=...` line to `~/.bashrc` (or prepend it to each run) so that
module 04 and `examples/02_run_spikein.sh` pick it up.

### Resumable download when no shared copy exists

The downloader fetches CheckM2 with `wget -c`, which resumes after an interruption, so
repeating the command continues the transfer; it then unpacks the archive and registers
the location with `checkm2 database --setdblocation`. To do this by hand instead:

```bash
conda activate checkm2
wget -c -O checkm2_database.tar.gz \
  https://zenodo.org/api/records/14897628/files/checkm2_database.tar.gz/content
tar -xzf checkm2_database.tar.gz
checkm2 database --setdblocation "$PWD/CheckM2_database"
```

The same shared-database idea applies to the other large resources: point `DBROOT` at the
shared location and keep only the missing pieces, or download GUNC, Bakta and eggNOG on a
machine with a better connection and copy the directories into `DBROOT`.

## 4. Hardware and optional components

Short-read analysis of several hundred isolates runs on 16 threads and 64 GB RAM. Flye and
CheckM2 raise memory use, so 128 GB is preferable. Running NCBI FCS-GX locally requires
about 470 GB of reference data and, per the official recommendation, about 512 GB RAM.
When this is not available, keep the CheckM2 and GUNC gates and run FCS-GX online on
usegalaxy.org instead; this route is already anticipated by the workflow.

## 5. Verify the installation

```bash
conda activate easywgs
fastp --version; unicycler --version; flye --version; mlst --version
conda activate checkm2 && checkm2 --version
```

Returning a version for each command indicates that the main chain is usable. Exact
versions do not need to match this guide, but the long-read polishing chain (Medaka and
Racon) and the assemblers should be recorded in the project log for reproducibility.
