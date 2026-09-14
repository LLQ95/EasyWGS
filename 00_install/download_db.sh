#!/usr/bin/env bash
# =============================================================================
# 00_install/download_db.sh —— 数据库下载（只需一次；按需注释掉不需要的库）
# =============================================================================
set -euo pipefail
DBROOT=${DBROOT:-$HOME/EasyIsolate_db}
mkdir -p "$DBROOT" && cd "$DBROOT"
source "$(conda info --base)/etc/profile.d/conda.sh"

# ---- CheckM2 数据库 ----
conda activate checkm2
checkm2 database --download --path "$DBROOT/checkm2_db"
conda deactivate

# ---- GUNC 数据库（默认 progenomes2.1，约13GB）----
conda activate gunc
gunc download_db "$DBROOT/gunc_db"
conda deactivate

# ---- Bakta 数据库（全量，体积较大）----
conda activate bakta
bakta_db download --output "$DBROOT/bakta_db" --type full
conda deactivate

# ---- eggNOG 数据库 ----
conda activate eggnog
download_eggnog_data.py -y --data_dir "$DBROOT/eggnog_db"
conda deactivate

# ---- PubMLST 离线库更新（mlst 自带，周期性更新）----
conda activate easyisolate
mlst-download_pub_mlst -j 8 -d "$(dirname "$(which mlst)")/../db/pubmlst" || true

# ---- abricate 自带库更新 + 列出可用库 ----
abricate-get_db --force || true
abricate --list
# 自建库方法（mobileOG/BacMet/IS/Tn 等）：fasta 放入 abricate/db/库名/，改写表头后：
#   abricate --setupdb

# ---- AMRFinderPlus 数据库 ----
amrfinder_update --force_update --database "$DBROOT/amrfinder_db"

# ---- CARD/RGI 数据库 ----
mkdir -p "$DBROOT/card" && cd "$DBROOT/card"
wget -q https://card.mcmaster.ca/latest/data -O card-data.tar.bz2 || true
tar -xjf card-data.tar.bz2 || true
cd "$DBROOT"

# ---- chewBBACA cgMLST schema（按研究类群下载，示例为沙门INNUENDO/李斯特Pasteur）----
mkdir -p "$DBROOT/chewie" && cd "$DBROOT/chewie"
# schema 需从对应机构获取：
#  沙门 enterica INNUENDO cgMLST99、李斯特 Pasteur cgMLST：
#  https://zenodo.org 搜索 "INNUENDO cgMLST" / "Listeria Pasteur cgMLST" 下载并解压
#  肺克/大肠可用 chewBBACA.py PrepExternalSchema 由公开等位库构建（见06.3脚本注释）
cd "$DBROOT"

# ---- Kraken2 标准库（可选，02模块侦察用，约100GB+）----
# mkdir -p "$DBROOT/k2_standard"
# kraken2-build --standard --threads 16 --db "$DBROOT/k2_standard"
# bracken-build -d "$DBROOT/k2_standard" -k 35 -t 16

# ---- FCS-GX（可选，约470GB，需大内存机器；见前序对话说明）----
# mkdir -p "$DBROOT/fcs" && cd "$DBROOT/fcs"
# curl -LO https://github.com/ncbi/fcs/raw/main/dist/fcs.py
# python3 fcs.py db get --mft https://ncbi-fcs-gx.s3.amazonaws.com/gxdb/latest/all.manifest --dir "$DBROOT/fcs_gx_db"

echo "数据库目录：$DBROOT ，请把该路径写入各模块脚本顶部 DBROOT"
