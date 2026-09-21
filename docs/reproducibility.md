# Reproducibility and tests

EasyWGS is designed to be reproducible at three levels: a portable software
manifest, exact per-machine environment locks, and a container image. On top of
the software environment, every quantitative claim in the guidebook is produced
by a version-controlled script with a fixed random seed, and a small
expected-result gate decides whether a run is acceptable. This page describes
what is tested automatically, what is validated on the cluster, and how to
repeat both.

## Software environments

The portable, unpinned manifest for the main `easywgs` environment is
`install/environment.yml`; it mirrors the package list in
`00_install/install_env.sh`. A much smaller manifest,
`install/environment.ci.yml`, contains only the lightweight tools used by the
synthetic smoke test.

```bash
# full environment for real analyses
conda env create -f install/environment.yml
# minimal environment for the smoke test and continuous integration
conda env create -f install/environment.ci.yml
```

The manifest intentionally does not pin every version, so it keeps working across
operating systems. For an exact, bit-for-bit reproducible analysis environment,
create the environments on a Linux/x86_64 machine and export locks with
`00_install/export_locks.sh`. The locks are written to `install/locks/` as
`<env>.linux-64.yml` and should be committed.

```bash
bash 00_install/install_env.sh     # creates easywgs, longread, checkm2, gunc, bakta, eggnog
bash 00_install/export_locks.sh    # writes exact locks into install/locks/
git add install/locks/*.yml
```

Recreate a locked environment with `conda env create -f
install/locks/easywgs.linux-64.yml`.

## Container image

A Docker image provides the main environment without a local Conda installation.
The image is rebuilt and published to the GitHub Container Registry by
`.github/workflows/container.yml`. The EasyWGS scripts and your data are mounted
at run time, so pulling a new repository revision does not require rebuilding
the image.

```bash
docker build -t easywgs:latest -f Dockerfile .
docker run --rm -it \
  -v "$PWD":/EasyWGS -v "$HOME/easywgs_db":/opt/db:ro \
  -w /EasyWGS -e DBROOT=/opt/db easywgs:latest bash
```

On an HPC cluster that uses Apptainer or Singularity, wrap the same image with
`containers/Singularity.def` (`apptainer build easywgs.sif
containers/Singularity.def`) and bind the database directory with `--bind`.

Large reference databases (CheckM2, GUNC, Bakta, eggNOG and the FCS-GX database)
are never baked into the image. Mount them read-only and point the runtime
variables at them: `DBROOT`, `CHECKM2_DB`, `GUNC_DB`, `BAKTA_DB` and
`EGGNOG_DB`. The dedicated `checkm2`, `gunc`, `bakta` and `eggnog` environments
are created by `install_env.sh` on the cluster rather than included in the
default image.

## What continuous integration runs

The workflow `.github/workflows/ci.yml` has two jobs that run on every push and
pull request to `main`.

The static job installs the documentation requirements and runs
`python tests/run_static_checks.py`, followed by `mkdocs build --clean
--strict`. The static checker validates every shell script with `bash -n`,
compiles every Python file, parses every R script when R is available, enforces
ASCII-only scripts and English-only default Markdown, checks the
`reference/tool_catalog.tsv` schema and status codes, and confirms that the
generated encyclopedia pages are current. The strict MkDocs build treats any
broken cross-reference or warning as an error.

The smoke job creates `install/environment.ci.yml` with micromamba and runs
`bash tests/run_smoke.sh` on a fully synthetic dataset. The generator
`tests/make_toy_data.py` uses a fixed seed (20260921) to build a 120 kb reference
and two isolates: one identical to the reference and one carrying 48 scattered
single-nucleotide changes. Each isolate gets roughly 35-fold coverage in 150 bp
paired reads. The smoke test then runs the real module scripts in order:

1. `01_qc/01.fastp.sh` for trimming and QC;
2. `12_mapping_pipeline/12.1.map_reads.sh` for `bwa mem`, sorted and indexed BAM
   files and coverage summaries;
3. `12_mapping_pipeline/12.2.call_variants.sh` for joint variant calling;
4. the self-contained decontamination spike-in.

The gates require at least 0.90 breadth at onefold depth, 15-fold mean depth and
90 percent mapped reads for both isolates, and at least 20 recovered bi-allelic
SNPs in the seeded mutant. The clean control must not produce a variant set.

The same job runs the read-layer decontamination spike-in in synthetic mode
(`examples/02_run_spikein.sh --synthetic`). Three seeded genomes stand in for the
target, a PhiX-like technical control and a distant bacterium; contaminant pairs
are added at 1, 5 and 10 percent. When `bwa` and `samtools` are present the
production mapping engine performs the classification and filtering; otherwise a
dependency-free k-mer classifier built into
`examples/spikein/synthetic_fixture.py` computes the same metrics. The rules in
`examples/expected/expected_spikein.tsv` (S1 to S5) require the spike to be
detected before cleaning, no more than 2 percent residual contamination after
cleaning, at least 90 percent target retention, and the fixed 12,000-pair
baseline.

## Running the tests yourself

```bash
# static checks only (no bioinformatics tools required)
python tests/run_static_checks.py

# full functional smoke test (needs the tools in environment.ci.yml)
conda activate easywgs-ci
bash tests/run_smoke.sh

# only the synthetic spike-in and its gates (uses the k-mer backend without bwa)
SYNTHETIC=1 bash examples/02_run_spikein.sh
```

The expected-result checker separates a step that has not run from a result that
violates a rule. A missing metric is `WARN` and never fails the build; a measured
value outside its threshold is `FAIL` and returns a non-zero exit code.

```bash
python examples/expected/check_expected.py --mode spikein   # decontamination
python examples/expected/check_expected.py --mode panel     # real isolate panel
python examples/expected/check_expected.py --mode all       # both, the default
```

## A fast smoke run on real reads

The synthetic test cannot reveal problems specific to real sequencing chemistry.
After downloading the public panel, build a reproducible mini panel with a fixed
number of read pairs per isolate and run the assembly route, which needs no
reference genome:

```bash
bash examples/00_download_panel.sh
bash examples/scripts/downsample_panel.sh examples/generated/samplesheet_tier1.csv 200000
bash run_assembly.sh config/my_samples.mini.csv
```

The full tier-1 to tier-5 validation, including assembly, CheckM2/GUNC,
annotation and the real spike-in, is documented step by step in the
[cluster checklist](cluster-checklist.md).

## Scope of the automated tests

SPAdes and Unicycler assembly, CheckM2 and GUNC assembly QC, Bakta and Prokka
annotation, eggNOG-mapper and FCS-GX are deliberately excluded from continuous
integration. They are mature third-party tools that need multi-gigabyte databases
or long compute times, so running them on every commit would be slow and would
add little protection against regressions in EasyWGS itself. They are exercised
on the real public panel under `docs/cluster-checklist.md`, and the expected-result
gate covers their outputs. The synthetic spike-in validates only the read layer;
its assembly and CheckM2/GUNC panels are produced by the real, cluster-run
spike-in and are otherwise left empty rather than filled with simulated values.

## Regenerating figures

All manuscript and guidebook figures come from deterministic Python scripts with
fixed seeds: the workflow and overview figures under `figures/make_*_figure.py`
and the spike-in figure under `examples/spikein/make_spikein_figure.py`. Running a
figure script overwrites the copies in `figures/` and `docs/assets/`, so a figure
always corresponds to the committed script and data.
