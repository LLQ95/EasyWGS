#!/usr/bin/env bash
# =============================================================================
# 00_install/download_db.sh - database download (once only; comment out what you do not need)
# =============================================================================
set -euo pipefail
DBROOT=${DBROOT:-$HOME/EasyIsolate_db}
mkdir -p "$DBROOT" && cd "$DBROOT"
source "$(conda info --base)/etc/profile.d/conda.sh"

# ---- CheckM2 database ----
conda activate checkm2
checkm2 database --download --path "$DBROOT/checkm2_db"
conda deactivate

# ---- GUNC database (default progenomes2.1, about 13 GB) ----
conda activate gunc
gunc download_db "$DBROOT/gunc_db"
conda deactivate

# ---- Bakta database (full, sizable) ----
conda activate bakta
bakta_db download --output "$DBROOT/bakta_db" --type full
conda deactivate

# ---- eggNOG database ----
conda activate eggnog
download_eggnog_data.py -y --data_dir "$DBROOT/eggnog_db"
conda deactivate

# ---- PubMLST offline refresh (bundled with mlst, periodic) ----
conda activate easyisolate
mlst-download_pub_mlst -j 8 -d "$(dirname "$(which mlst)")/../db/pubmlst" || true

# ---- Update built-in abricate databases and list the available ones ----
abricate-get_db --force || true
abricate --list
# To build a custom DB (mobileOG/BacMet/IS/Tn): place fasta under abricate/db/<name>/, rewrite headers, then:
#   abricate --setupdb

# ---- AMRFinderPlus database ----
amrfinder_update --force_update --database "$DBROOT/amrfinder_db"

# ---- CARD/RGI database ----
mkdir -p "$DBROOT/card" && cd "$DBROOT/card"
wget -q https://card.mcmaster.ca/latest/data -O card-data.tar.bz2 || true
tar -xjf card-data.tar.bz2 || true
cd "$DBROOT"

# ---- chewBBACA cgMLST schemas (download per group; examples: Salmonella INNUENDO / Listeria Pasteur) ----
mkdir -p "$DBROOT/chewie" && cd "$DBROOT/chewie"
# Schemas are obtained from the corresponding providers:
#  Salmonella enterica INNUENDO cgMLST99, Listeria Pasteur cgMLST:
#  search https://zenodo.org for "INNUENDO cgMLST" / "Listeria Pasteur cgMLST", download and unpack
#  Klebsiella/E. coli schemas can be built from public alleles with
#  chewBBACA.py PrepExternalSchema (see notes in 06.3)
cd "$DBROOT"

# ---- Kraken2 standard DB (optional, for module-02 scouting, 100 GB+) ----
# mkdir -p "$DBROOT/k2_standard"
# kraken2-build --standard --threads 16 --db "$DBROOT/k2_standard"
# bracken-build -d "$DBROOT/k2_standard" -k 35 -t 16

# ---- FCS-GX (optional, about 470 GB, needs a large-RAM machine; see earlier notes) ----
# mkdir -p "$DBROOT/fcs" && cd "$DBROOT/fcs"
# curl -LO https://github.com/ncbi/fcs/raw/main/dist/fcs.py
# python3 fcs.py db get --mft https://ncbi-fcs-gx.s3.amazonaws.com/gxdb/latest/all.manifest --dir "$DBROOT/fcs_gx_db"

echo "Database directory: $DBROOT ; write this path into DBROOT at the top of each module script"
