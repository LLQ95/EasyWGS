#!/usr/bin/env bash
# =============================================================================
# 00_install/export_locks.sh - export exact, reproducible conda environment locks
#
# Run this ONCE on the same Linux/x86_64 system where the environments were
# created (for example the HPC login or build node), then commit the resulting
# install/locks/*.yml. The unpinned install/environment.yml is portable across
# operating systems; the locks record the exact versions and builds that were
# validated, so a later run can reproduce them bit for bit.
#
# Recreate a locked environment with:
#   conda env create -f install/locks/easywgs.linux-64.yml
#
# Environments that have not been created are skipped with a warning rather than
# aborting, so the script also works when only the main environment exists.
# =============================================================================
set -euo pipefail
PROJECT=$(cd "$(dirname "$0")/.." && pwd)
LOCKDIR="$PROJECT/install/locks"
mkdir -p "$LOCKDIR"

EASYWGS_ENV="${EASYWGS_ENV:-easywgs}"
ENVS=("$EASYWGS_ENV" longread checkm2 gunc bakta eggnog)

echo "[info] exporting ${#ENVS[@]} environments into $LOCKDIR"

for env in "${ENVS[@]}"; do
  if ! conda env list | awk '{print $1}' | grep -qx "$env"; then
    echo "[skip] environment '$env' does not exist yet; run 00_install/install_env.sh first"
    continue
  fi
  out="$LOCKDIR/${env}.linux-64.yml"
  echo "[export] $env -> $(basename "$out")"
  conda env export -n "$env" --no-builds | grep -v '^prefix:' > "$out"
done

echo "[done] lock files written to install/locks/"
echo "       review and commit them: git add install/locks/*.yml"
