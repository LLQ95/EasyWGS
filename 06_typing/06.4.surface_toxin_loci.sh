#!/usr/bin/env bash
# =============================================================================
# 06_typing/06.4.surface_toxin_loci.sh - custom surface-antigen / toxin /
#   virulence-locus screen with abricate against the easywgs_markers database
#
# Several common pathogens (Vibrio parahaemolyticus, Yersinia enterocolitica,
# Campylobacter jejuni/coli, Burkholderia gladioli and Clostridium botulinum)
# have no single maintained command-line serotyper. The reproducible approach
# used here is a curated abricate database of surface-antigen loci, toxin genes
# and virulence markers (tlh/tdh/trh/orf8, ail/yst/yadA/virF, cdt/cadF/flaA and
# the capsule locus, the bongkrekic-acid bon and toxoflavin tox clusters, and
# the bont/ntnh toxin cluster). The marker list with authoritative sources is
# examples/customdb/easywgs_markers.tsv; build the database once with
# 00_install/build_custom_db.sh.
#
# Surface and toxin TYPE assignment (O/K group, Penner capsule type, BoNT
# subtype) needs type-specific reference alleles; the generic gene markers here
# detect presence/absence only and must be interpreted with those references.
#
# Input : 03_assembly/genomes/*.fasta
# Output: 06_typing/surface_toxin/custom_markers_all.tab and _summary.tab
# The step degrades gracefully: if the database is absent it writes empty
# tables and warns, so the master runner is not interrupted.
# =============================================================================
set -euo pipefail
THREADS=${THREADS:-8}
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
GEN="$PROJECT/03_assembly/genomes"
OUT="$PROJECT/06_typing/surface_toxin"; mkdir -p "$OUT"
source "$PROJECT/00_install/runtime.sh"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$EASYWGS_ENV"

ALL="$OUT/custom_markers_all.tab"
SUM="$OUT/custom_markers_summary.tab"

# Resolve the custom database: a registered abricate name first, then an
# explicit directory (EASYWGS_MARKER_DIR), then the standard per-user location.
DBPATH=""
if abricate --list 2>/dev/null | awk 'NR>1{print $1}' | grep -qx "easywgs_markers"; then
  DBPATH="easywgs_markers"
elif [[ -n "${EASYWGS_MARKER_DIR:-}" && -f "${EASYWGS_MARKER_DIR}/sequences" ]]; then
  DBPATH="${EASYWGS_MARKER_DIR}"
elif [[ -f "$HOME/.abricate/db/easywgs_markers/sequences" ]]; then
  DBPATH="$HOME/.abricate/db/easywgs_markers"
fi

if [[ -z "$DBPATH" ]]; then
  echo "[warn] custom marker database 'easywgs_markers' not built; run 00_install/build_custom_db.sh" >&2
  echo "[warn] module 06.4 writes empty tables and continues" >&2
  : > "$ALL"; : > "$SUM"
  exit 0
fi
echo "[info] screening assemblies with abricate db: $DBPATH"

shopt -s nullglob
: > "$ALL"
for f in "$GEN"/*.fasta; do
  abricate --threads "$THREADS" --db "$DBPATH" "$f"
done | awk 'NR==1 || $0 !~ /^#File/' > "$ALL"
abricate --summary "$ALL" > "$SUM"
echo "[done] custom surface/toxin markers: $ALL (presence matrix: $SUM)"
