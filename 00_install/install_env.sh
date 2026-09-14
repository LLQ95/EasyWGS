#!/usr/bin/env bash
# =============================================================================
# 00_install/install_env.sh —— EasyIsolate 环境安装（分环境，避免依赖冲突）
# Linux / WSL2 / HPC；优先 mamba，没有则把 mamba 换成 conda
# 覆盖：二代(Illumina)、三代(ONT/PacBio)、混合(hybrid)三类场景
# =============================================================================
set -euo pipefail
conda config --add channels conda-forge
conda config --add channels bioconda

# 1) 主环境：质控(二代+三代) / 组装 / 评估 / 分型 / 比较 / 系统发育
mamba create -y -n easyisolate -c bioconda -c conda-forge \
  fastp fastqc multiqc seqkit \
  porechop chopper nanoplot filtlong \
  spades unicycler flye canu dragonflye racon circlator assembly-stats \
  quast mash mummer minimap2 bowtie2 bwa samtools bcftools \
  prokka prodigal panaroo roary mafft iqtree fasttree snp-sites snp-dists \
  snippy gubbins treetime \
  mlst abricate ncbi-amrfinderplus rgi mob-suite genomad \
  kleborate ectyper shigeifinder seqsero2 sistr chewbbaca \
  csvtk r-base nextflow

# 2) 长读抛光独立环境：Medaka(依赖重) 与 Trycycler(多组装一致,完成图金标准)
mamba create -y -n longread -c bioconda -c conda-forge medaka trycycler racon minimap2

# 3) CheckM2 独立环境（组装污染/完整度）
mamba create -y -n checkm2 -c bioconda -c conda-forge checkm2

# 4) GUNC 独立环境（嵌合检测，锁定 diamond 版本）
mamba create -y -n gunc -c bioconda -c conda-forge gunc

# 5) Bakta 独立环境（注释，数据库大、依赖独立）
mamba create -y -n bakta -c bioconda -c conda-forge bakta

# 6) eggNOG 独立环境（GO/KEGG/COG）
mamba create -y -n eggnog -c bioconda -c conda-forge eggnog-mapper diamond

# 7) CLEAN reads 去污染（Nextflow 流程，无需本地装，装 nextflow 即可调用）
nextflow pull rki-mf1/clean

echo "[OK] 环境：easyisolate(主) / longread(三代抛光) / checkm2 / gunc / bakta / eggnog"
echo "    随后运行 bash 00_install/download_db.sh 下载数据库"
