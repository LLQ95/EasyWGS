#!/usr/bin/env bash
# =============================================================================
# 00_install/install_env.sh - EasyWGS environments (split envs avoid conflicts)
# Linux / WSL2 / HPC; uses mamba when available and falls back to conda.
# Covers Illumina short reads, ONT/PacBio long reads and hybrid assembly.
#
# The script is idempotent: an environment that already exists is skipped, so it
# is safe to rerun after a partial install. Override the main environment name
# and the package front-end if needed, for example:
#   EASYWGS_ENV=easywgs CONDA_PKG=mamba bash 00_install/install_env.sh
# =============================================================================
set -euo pipefail
conda config --add channels conda-forge
conda config --add channels bioconda

EASYWGS_ENV=${EASYWGS_ENV:-easywgs}
if command -v mamba >/dev/null 2>&1; then
  CONDA_PKG=${CONDA_PKG:-mamba}
else
  CONDA_PKG=${CONDA_PKG:-conda}
fi
echo "[info] using '$CONDA_PKG'; main environment name: '$EASYWGS_ENV'"

# ensure_env NAME [create arguments...] creates the environment only when absent
ensure_env() {
  local name="$1"; shift
  if conda env list | awk '{print $1}' | grep -qx "$name"; then
    echo "[skip] conda environment '$name' already exists"
  else
    echo "[create] conda environment '$name'"
    "$CONDA_PKG" create -y -n "$name" "$@"
  fi
}

# 1) Main env: QC (short+long) / assembly / mapping & calling / typing / phylogeny / GWAS
#    grapetree builds the cgMLST/core-SNP minimum spanning tree used by module 11
#    module 12 (reference mapping) uses bwa/minimap2 + samtools + bcftools; module 13
#    (microbial GWAS) uses scoary, plink and pyseer
#    The bioconda "iqtree" package now ships IQ-TREE 3 (binary iqtree3); version 2 used iqtree2
#    "art" provides art_illumina for the controlled decontamination spike-in example.
ensure_env "$EASYWGS_ENV" -c bioconda -c conda-forge \
  fastp fastqc multiqc seqkit \
  porechop chopper nanoplot filtlong \
  spades unicycler flye canu dragonflye racon circlator assembly-stats \
  quast mash mummer minimap2 bowtie2 bwa samtools bcftools tabix qualimap vcf2phylip \
  prokka prodigal panaroo roary mafft iqtree fasttree snp-sites snp-dists \
  snippy gubbins treetime \
  mlst abricate ncbi-amrfinderplus rgi mob-suite genomad \
  kleborate ectyper shigeifinder seqsero2 sistr chewbbaca \
  scoary plink pyseer \
  grapetree csvtk r-base nextflow art matplotlib

# 2) Dedicated long-read polishing env: Medaka (heavy deps) and Trycycler (multi-assembly consensus, finished-grade)
ensure_env longread -c bioconda -c conda-forge medaka trycycler racon minimap2

# 3) CheckM2 dedicated env (assembly contamination/completeness)
ensure_env checkm2 -c bioconda -c conda-forge checkm2

# 4) GUNC dedicated env (chimerism, pins the diamond version)
ensure_env gunc -c bioconda -c conda-forge gunc

# 5) Bakta dedicated env (annotation, large and independent database)
ensure_env bakta -c bioconda -c conda-forge bakta

# 6) eggNOG dedicated env (GO/KEGG/COG)
ensure_env eggnog -c bioconda -c conda-forge eggnog-mapper diamond

# 7) R packages for module-11 static figures (ggtree/treeio/pheatmap/ComplexHeatmap).
#    Works with the conda r-base above or a system R; run once:
Rscript 00_install/install_R_packages.R || \
  echo "[warn] R package installation failed; module 11 static figures need the packages listed in install_R_packages.R"

# 8) CLEAN read decontamination is a Nextflow workflow; pull it inside the main env
conda run -n "$EASYWGS_ENV" nextflow pull rki-mf1/clean || \
  echo "[warn] could not pull the CLEAN workflow (network); module 02 can run without it"

echo "[OK] envs: $EASYWGS_ENV (main) / longread (long polishing) / checkm2 / gunc / bakta / eggnog"
echo "     Next: point CHECKM2_DB at an existing database if you have one, then run"
echo "           bash 00_install/download_db.sh to fetch the remaining databases"
