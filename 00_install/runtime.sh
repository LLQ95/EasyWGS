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
#   export EASYWGS_ENV=easywgs
#
# CHECKM2_DB may point either at the uniref100.KO.1.dmnd file itself or at the
# CheckM2_database directory that contains it, which lets a workstation reuse a
# shared CheckM2 database instead of downloading it again.
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
