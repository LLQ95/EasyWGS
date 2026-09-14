#!/usr/bin/env bash
# =============================================================================
# 00_install/install_env.sh - EasyWGS environments (split envs avoid conflicts)
# Linux / WSL2 / HPC; prefer mamba, replace mamba with conda if unavailable
# Covers Illumina short reads, ONT/PacBio long reads and hybrid assembly
# =============================================================================
set -euo pipefail
conda config --add channels conda-forge
conda config --add channels bioconda

# 1) Main env: QC (short+long) / assembly / mapping & calling / typing / phylogeny / GWAS
#    grapetree builds the cgMLST/core-SNP minimum spanning tree used by module 11
#    module 12 (reference mapping) uses bwa/minimap2 + samtools + bcftools; module 13
#    (microbial GWAS) uses scoary, plink and pyseer
#    The bioconda "iqtree" package now ships IQ-TREE 3 (binary iqtree3); version 2 used iqtree2
mamba create -y -n easywgs -c bioconda -c conda-forge \
  fastp fastqc multiqc seqkit \
  porechop chopper nanoplot filtlong \
  spades unicycler flye canu dragonflye racon circlator assembly-stats \
  quast mash mummer minimap2 bowtie2 bwa samtools bcftools tabix qualimap vcf2phylip \
  prokka prodigal panaroo roary mafft iqtree fasttree snp-sites snp-dists \
  snippy gubbins treetime \
  mlst abricate ncbi-amrfinderplus rgi mob-suite genomad \
  kleborate ectyper shigeifinder seqsero2 sistr chewbbaca \
  scoary plink pyseer \
  grapetree csvtk r-base nextflow

# 2) Dedicated long-read polishing env: Medaka (heavy deps) and Trycycler (multi-assembly consensus, finished-grade)
mamba create -y -n longread -c bioconda -c conda-forge medaka trycycler racon minimap2

# 3) CheckM2 dedicated env (assembly contamination/completeness)
mamba create -y -n checkm2 -c bioconda -c conda-forge checkm2

# 4) GUNC dedicated env (chimerism, pins the diamond version)
mamba create -y -n gunc -c bioconda -c conda-forge gunc

# 5) Bakta dedicated env (annotation, large and independent database)
mamba create -y -n bakta -c bioconda -c conda-forge bakta

# 6) eggNOG dedicated env (GO/KEGG/COG)
mamba create -y -n eggnog -c bioconda -c conda-forge eggnog-mapper diamond

# 7) R packages for module-11 static figures (ggtree/treeio/pheatmap/ComplexHeatmap).
#    Works with the conda r-base above or a system R; run once:
Rscript 00_install/install_R_packages.R

# 8) CLEAN read decontamination is a Nextflow workflow; pulling it needs no local install
nextflow pull rki-mf1/clean

echo "[OK] envs: easywgs (main) / longread (long polishing) / checkm2 / gunc / bakta / eggnog"
echo "     Next run: bash 00_install/download_db.sh to fetch databases"
