#!/usr/bin/env bash
# =============================================================================
# 00_install/download_db.sh - database download (once only; comment out what you do not need)
# =============================================================================
set -euo pipefail
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
source "$SCRIPT_DIR/runtime.sh"
mkdir -p "$DBROOT" && cd "$DBROOT"
source "$(conda info --base)/etc/profile.d/conda.sh"

# ---- CheckM2 database ----
# Reuse a shared copy when CHECKM2_DB is set (the uniref100.KO.1.dmnd file or its
# CheckM2_database directory); otherwise download with a resumable transfer, since
# the Zenodo file is about 1.7 GB and the built-in one-shot download can break.
conda activate checkm2
CHECKM2_DMND=$(easywgs_resolve_checkm2_db)
if [ -n "$CHECKM2_DMND" ] && [ -f "$CHECKM2_DMND" ]; then
  echo "[skip] CheckM2 database found at $CHECKM2_DMND"
  checkm2 database --setdblocation "$(dirname "$CHECKM2_DMND")" || true
else
  mkdir -p "$DBROOT/checkm2_db"
  CK2_URL="https://zenodo.org/api/records/14897628/files/checkm2_database.tar.gz/content"
  CK2_TAR="$DBROOT/checkm2_db/checkm2_database.tar.gz"
  echo "[info] downloading CheckM2 database (resumable; rerun this script to continue) ..."
  if wget -c -O "$CK2_TAR" "$CK2_URL"; then
    tar -xzf "$CK2_TAR" -C "$DBROOT/checkm2_db"
    CHECKM2_DMND=$(find "$DBROOT/checkm2_db" -name uniref100.KO.1.dmnd | head -n1 || true)
    if [ -n "$CHECKM2_DMND" ]; then
      checkm2 database --setdblocation "$(dirname "$CHECKM2_DMND")" || true
    fi
  else
    echo "[warn] resumable wget failed; falling back to the built-in downloader" >&2
    checkm2 database --download --path "$DBROOT/checkm2_db" || \
      echo "[error] CheckM2 DB incomplete. Re-run this script, or export CHECKM2_DB to a shared uniref100.KO.1.dmnd" >&2
  fi
fi
conda deactivate

# ---- GUNC database (default progenomes2.1, about 13 GB) ----
conda activate gunc
GUNC_DMND=$(easywgs_resolve_gunc_db)
if [ -n "$GUNC_DMND" ] && [ -f "$GUNC_DMND" ]; then
  echo "[skip] GUNC database found at $GUNC_DMND"
  export GUNC_DB="$GUNC_DMND"
else
  mkdir -p "$DBROOT/gunc_db"
  gunc download_db "$DBROOT/gunc_db"
  GUNC_DMND=$(easywgs_resolve_gunc_db)
  [ -n "$GUNC_DMND" ] && export GUNC_DB="$GUNC_DMND"
fi
conda deactivate

# ---- Bakta database (full, sizable) ----
conda activate bakta
BAKTA_DIR=$(easywgs_resolve_bakta_db)
if [ -n "$BAKTA_DIR" ] && [ -f "$BAKTA_DIR/version.json" ]; then
  echo "[skip] Bakta database found at $BAKTA_DIR"
  export BAKTA_DB="$BAKTA_DIR"
else
  bakta_db download --output "$DBROOT/bakta_db" --type full
  BAKTA_DIR=$(easywgs_resolve_bakta_db)
  [ -n "$BAKTA_DIR" ] && export BAKTA_DB="$BAKTA_DIR"
fi
conda deactivate

# ---- eggNOG database ----
conda activate eggnog
EGG_DIR=$(easywgs_resolve_eggnog_db)
if [ -n "$EGG_DIR" ] && [ -f "$EGG_DIR/eggnog.db" ]; then
  echo "[skip] eggNOG database found at $EGG_DIR"
else
  mkdir -p "$DBROOT/eggnog_db"
  download_eggnog_data.py -y --data_dir "$DBROOT/eggnog_db"
fi
conda deactivate

# ---- PubMLST offline refresh (bundled with mlst, periodic) ----
conda activate "${EASYWGS_ENV:-easywgs}"
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
