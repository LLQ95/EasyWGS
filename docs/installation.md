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

### Reuse existing shared databases

Each large database can be pointed at an existing shared copy with an environment
variable, so the downloader skips it while the corresponding module uses that copy
directly. Set `DBROOT` to the shared root for anything that still has to be downloaded:

| Variable | Points at | Used by |
| --- | --- | --- |
| `CHECKM2_DB` | `uniref100.KO.1.dmnd` file or its `CheckM2_database` directory | module 04, spike-in |
| `BAKTA_DB` | Bakta folder containing `version.json` (or its parent folder) | module 05 |
| `EGGNOG_DB` | eggNOG folder containing `eggnog.db` | module 05 |
| `GUNC_DB` | `gunc_db.dmnd` file or the folder that contains it | module 04 |

For example, on a cluster that already hosts CheckM2, Bakta and eggNOG under
`/db/student/metagenome` and that wants GUNC downloaded into the same area:

```bash
export DBROOT=/db/student/metagenome
export CHECKM2_DB=/db/student/metagenome/checkm_db/checkm2_database/CheckM2_database/uniref100.KO.1.dmnd
export BAKTA_DB=/db/student/metagenome/bakta_db/db
export EGGNOG_DB=/db/student/metagenome/eggnog_db
# GUNC_DB is left unset, so the downloader fetches GUNC into $DBROOT/gunc_db
bash 00_install/download_db.sh
```

The downloader prints `[skip]` for every database it finds and downloads only the
missing ones (in this case GUNC and the small AMRFinder, CARD and abricate data). Add
these `export` lines to `~/.bashrc`, or prepend them to each run, so that modules 04 and
05 pick them up. When a database is absent at run time, the module that needs it logs a
clear warning and writes NA instead of aborting the whole workflow.

The CheckM2 database is about 1.7 GB and the one-shot Zenodo download can break on an
unstable link; the next subsection describes the resumable fallback used when no shared
copy is available.

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
