# Cluster checklist for the real panel

This checklist runs EasyWGS on the public bacterial isolate panel on a Linux
HPC node and produces the measured results that back the manuscript. It is the
complement of the synthetic continuous-integration tests: those verify that the
code works with no data and no databases, whereas this page validates the full
assembly, QC, annotation, typing and phylogeny route on real reads. Work through
it in order, and do not move to the next tier until the expected-result gate
reports no `FAIL`.

All paths below that begin with `/db/student/metagenome` are examples from one
cluster; replace them with the locations of your shared databases.

## 1. Get the code and create the environments

Clone the repository and create the six Conda environments once. The main
environment is named `easywgs`; the others isolate tools with heavy or
conflicting dependencies.

```bash
git clone https://github.com/LLQ95/EasyWGS.git
cd EasyWGS
bash 00_install/install_env.sh
```

If a module reports `EnvironmentNameNotFound: Could not find conda environment:
easywgs`, the installer has not completed successfully; rerun it before anything
else. Mamba is used automatically when available and falls back to Conda. The
Anaconda Terms-of-Service notice from libmamba is informational; the
environments use the conda-forge and bioconda channels.

## 2. Point the pipeline at existing databases

The pipeline never assumes that databases live in a home directory. Source the
runtime helpers and export the locations of shared databases before running a
module. The values shown here reuse databases that already exist on the cluster
and avoid a multi-gigabyte re-download.

```bash
source 00_install/runtime.sh

# CheckM2 diamond database (the file itself, or the directory that contains it)
export CHECKM2_DB=/db/student/metagenome/checkm_db/checkm2_database/CheckM2_database/uniref100.KO.1.dmnd
# Bakta full database (the directory that contains bakta.db and version.json)
export BAKTA_DB=/db/student/metagenome/bakta_db/db
# eggNOG-mapper data directory (the directory that contains eggnog.db)
export EGGNOG_DB=/db/student/metagenome/eggnog_db
# GUNC database; see the download step below if it is not present
export GUNC_DB=/db/student/metagenome/gunc_db/progenomes_2.1/gunc_db.dmnd
```

Register the existing CheckM2 database with the dedicated environment:

```bash
conda run -n checkm2 checkm2 database --setdblocation "$(dirname "$CHECKM2_DB")"
```

The GUNC progenomes 2.1 database is the only large database that still needs to
be fetched on a cluster that already has CheckM2, Bakta and eggNOG. Download it
into the shared area (about 13 GB; use a writable location such as
`$HOME/easywgs_db` if `/db` is read-only):

```bash
mkdir -p /db/student/metagenome/gunc_db
conda run -n gunc gunc download_db /db/student/metagenome/gunc_db
export GUNC_DB=$(find /db/student/metagenome/gunc_db -name 'gunc_db.dmnd' | head -n1)
```

If the CheckM2 download from Zenodo is interrupted with an `IncompleteRead`
error, do not restart from zero inside the installer. Either point `CHECKM2_DB`
at the shared copy as above, or download the archive once with a resumable
client (`wget -c` or `curl -C -`), extract it under `$DBROOT/checkm2_db`, and run
`checkm2 database --setdblocation` on the extracted directory. Any database that
is not already shared can be fetched with `bash 00_install/download_db.sh` after
editing `DBROOT`; comment out the sections you do not need.

## 3. Verify the installation without data

Run the static checks and the self-contained smoke test before downloading
anything. The static checks need only Python; the smoke test uses the minimal
environment or the main environment.

```bash
python tests/run_static_checks.py

conda activate easywgs
bash tests/run_smoke.sh
SYNTHETIC=1 bash examples/02_run_spikein.sh
```

The smoke test creates a temporary synthetic project, runs fastp, reference
mapping and variant calling, and checks coverage and SNP recovery. The synthetic
spike-in uses the `bwa` engine here (it is installed in the environment) and must
finish with `PASS` for every S1 to S5 rule.

## 4. Download the public panel

The panel definition is `examples/panel.tsv`; it groups isolates into five
tiers, starting with a small, well-characterised set and expanding to the full
multi-species collection. Download tier 1 first and inspect the generated
samplesheet.

```bash
bash examples/00_download_panel.sh 1
# generated sheets and metadata land in examples/generated/ (ignored by git)
ls -lh 00_rawdata
```

Reads are placed under `00_rawdata/`, which is not tracked by git. If a download
fails for one accession, rerun the script; the downloader skips files that are
already present.

## 5. Real-data mini smoke run

Before committing to a full tier, subsample a fixed number of read pairs per
isolate and run the assembly route. This reproduces most wiring and path errors
in minutes.

```bash
bash examples/scripts/downsample_panel.sh examples/generated/samplesheet_tier1.csv 200000
bash run_assembly.sh config/my_samples.mini.csv
```

The mini samplesheet uses a `mini_` prefix so the subsampled files are easy to
remove. Increase the pair count if a high-GC genome assembles poorly at the
default depth.

## 6. Run the tiers in order

Run each tier as a batch, starting at tier 1 and only advancing after the
expected-result gate is clean. The optional second argument resumes from a given
sample id, which is useful after a preemption.

```bash
bash examples/01_run_panel.sh 1
python examples/expected/check_expected.py --mode panel
# repeat for tiers 2 to 5
bash examples/01_run_panel.sh 2
# ...
bash examples/01_run_panel.sh 5
python examples/expected/check_expected.py --mode all
```

On a scheduled cluster, submit each tier as its own job rather than running an
interactive shell over several days. A minimal Slurm array-style wrapper gives
each task 16 threads, 32 GB of memory and a long wall time; adjust these to the
queue and place the database exports from step 2 in the job script.

```bash
# example: sbatch --cpus-per-task=16 --mem=32G --time=24:00:00 \
#   --wrap='source 00_install/runtime.sh; export CHECKM2_DB=...; bash examples/01_run_panel.sh 1'
```

The values are planning guidance rather than measured benchmarks. Short-read
SPAdes assembly of a five-megabase genome typically uses well under 16 GB of
memory, whereas hybrid and long-read assembly, Bakta and CheckM2 benefit from
more; record the actual peak memory and run time from the scheduler and report
those measured values rather than the estimates. Running isolates as parallel
array tasks is substantially simpler than sharing one large node.

## 7. Run the real decontamination spike-in

The real spike-in adds simulated PhiX and a distant bacterial contaminant to a
tier-1 isolate and evaluates read-layer removal together with assembly and
CheckM2/GUNC contamination panels. It needs `art_illumina` (the `art` package in
the main environment) and the CheckM2 and GUNC databases.

```bash
export THREADS=16
export MEM=32
bash examples/02_run_spikein.sh
python examples/expected/check_expected.py --mode spikein
```

This fills the assembly and CheckM2/GUNC panels that the synthetic run leaves
empty and regenerates `Fig_spikein` together with the published copies in
`figures/` and `docs/assets/`.

## 8. Expected-result gate and what to archive

The gate distinguishes work that has not run (`WARN`) from a measured violation
(`FAIL`). A complete, acceptable run has no `FAIL`; `WARN` is allowed only for
modules that are intentionally out of scope.

```bash
python examples/expected/check_expected.py --mode all
```

Archive and, where appropriate, commit the small derived tables that support the
manuscript: `examples/results/panel_metrics.tsv`,
`examples/results/collection_stats.tsv`,
`examples/results/expected_check.tsv`,
`examples/spikein/results/spikein_metrics.tsv` and the spike-in expected-check
file. Raw reads, BAM files and large assemblies stay out of git; publish them
through a public repository or an archive if the target journal requires it.

## 9. Lock the validated environment and finalise the manuscript

Once the full panel passes, export the exact environment that produced the
results and commit the locks so that reviewers can recreate them.

```bash
bash 00_install/export_locks.sh
git add install/locks/*.yml
```

Then replace any provisional wording in the manuscript with measured values: the
panel size and tier composition, assembly QC distributions, contamination and
retention from both spike-in modes, typing and resistance calls, the time-tree
substitution rate and dates, and the recorded runtime and memory. Figures must be
regenerated from the committed scripts rather than edited by hand. The synthetic
spike-in is described as a deterministic in-silico control; assembly-level
contamination claims come from the real spike-in and the panel gate.

## Common failures

A missing `easywgs` environment means step 1 was skipped. A reference column that
points at a GenBank file (`.gb` or `.gbk`) is rejected by module 12, which needs a
FASTA reference; convert or download the FASTA first. A failed R package install
only affects the module-11 static figures and can be repeated with
`Rscript 00_install/install_R_packages.R`. A failed `nextflow pull rki-mf1/clean`
because of network restrictions does not block the pipeline; the FCS-GX and
CheckM2 gates still run, and CLEAN can be added later. Permission denied under a
shared `/db` path means that location is read-only; set `DBROOT` to a writable
directory for the databases you must create, such as GUNC, and keep the
read-only shared ones pointed at through their environment variables.

## Scope and responsible use

The worked example uses only public, de-identified sequencing accessions and is
entirely in silico; it includes no culture or wet-laboratory work. Genotypic
predictions of resistance, serotype or virulence are not a substitute for
phenotypic testing or a clinical laboratory report.
