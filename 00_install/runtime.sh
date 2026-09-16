#!/usr/bin/env bash
# =============================================================================
# 00_install/runtime.sh - shared, overridable runtime configuration for EasyWGS
#
# Source this from any module script, for example:
#   PROJECT=$(cd "$(dirname "$0")/.." && pwd)
#   source "$PROJECT/00_install/runtime.sh"
#
# Every value can be overridden from the environment before running, e.g.
#   export DBROOT=/data/shared/easywgs_db
#   export CHECKM2_DB=/db/student/metagenome/checkm_db/checkm2_database/CheckM2_database/uniref100.KO.1.dmnd
#   export BAKTA_DB=/db/student/metagenome/bakta_db/db
#   export EGGNOG_DB=/db/student/metagenome/eggnog_db
#   export GUNC_DB=/db/student/metagenome/gunc_db/progenomes_2.1/gunc_db.dmnd
#   export EASYWGS_ENV=easywgs
#
# CHECKM2_DB may point either at the uniref100.KO.1.dmnd file itself or at the
# CheckM2_database directory that contains it, which lets a workstation reuse a
# shared CheckM2 database instead of downloading it again. BAKTA_DB points at the
# folder with version.json (or its parent), EGGNOG_DB at the folder with eggnog.db,
# and GUNC_DB at the gunc_db.dmnd file (or its folder).
# =============================================================================
export EASYWGS_ENV="${EASYWGS_ENV:-easywgs}"
export DBROOT="${DBROOT:-$HOME/easywgs_db}"

# Print the resolved CheckM2 diamond database file (uniref100.KO.1.dmnd), or an
# empty string when no usable database is found.
easywgs_resolve_checkm2_db() {
  local p="${CHECKM2_DB:-}"
  if [ -z "$p" ]; then
    for cand in "$DBROOT/checkm2_db/CheckM2_database/uniref100.KO.1.dmnd" \
                "$DBROOT/checkm2_db/uniref100.KO.1.dmnd"; do
      if [ -f "$cand" ]; then p="$cand"; break; fi
    done
  elif [ -d "$p" ]; then
    if [ -f "$p/uniref100.KO.1.dmnd" ]; then p="$p/uniref100.KO.1.dmnd"; fi
  fi
  printf '%s' "$p"
}

# Print the Bakta database directory (the folder that contains version.json and
# bakta.db), or an empty string when it is missing. BAKTA_DB may point at that
# folder directly or at its parent (the downloader creates a db/ subfolder).
easywgs_resolve_bakta_db() {
  local p="${BAKTA_DB:-}"
  local cand=""
  if [ -n "$p" ] && [ -d "$p" ]; then
    if [ -f "$p/version.json" ]; then cand="$p"
    elif [ -f "$p/db/version.json" ]; then cand="$p/db"; fi
  fi
  if [ -z "$cand" ]; then
    for c in "$DBROOT/bakta_db/db" "$DBROOT/bakta_db"; do
      if [ -f "$c/version.json" ]; then cand="$c"; break; fi
    done
  fi
  printf '%s' "$cand"
}

# Print the eggNOG-mapper data directory (the folder that contains eggnog.db),
# or an empty string when it is missing. EGGNOG_DB points at that folder.
easywgs_resolve_eggnog_db() {
  local p="${EGGNOG_DB:-}"
  local cand=""
  if [ -n "$p" ] && [ -d "$p" ] && [ -f "$p/eggnog.db" ]; then cand="$p"; fi
  if [ -z "$cand" ] && [ -f "$DBROOT/eggnog_db/eggnog.db" ]; then cand="$DBROOT/eggnog_db"; fi
  printf '%s' "$cand"
}

# Print the GUNC diamond database file (gunc_db.dmnd), or an empty string when it
# is missing. GUNC_DB may be the file itself or the directory that contains it.
easywgs_resolve_gunc_db() {
  local p="${GUNC_DB:-}"
  local cand=""
  if [ -n "$p" ]; then
    if [ -f "$p" ]; then cand="$p"
    elif [ -d "$p" ]; then cand=$(find "$p" -name 'gunc_db.dmnd' 2>/dev/null | head -n1 || true); fi
  fi
  if [ -z "$cand" ] && [ -d "$DBROOT/gunc_db" ]; then
    cand=$(find "$DBROOT/gunc_db" -name 'gunc_db.dmnd' 2>/dev/null | head -n1 || true)
    if [ -z "$cand" ]; then
      cand=$(ls "$DBROOT"/gunc_db/*progenomes*.dmnd 2>/dev/null | head -n1 || true)
    fi
  fi
  printf '%s' "$cand"
}
