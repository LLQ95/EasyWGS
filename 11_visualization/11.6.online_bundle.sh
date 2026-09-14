#!/usr/bin/env bash
# =============================================================================
# 11_visualization/11.6.online_bundle.sh
# Collect trees, metadata and matrices into online_bundle/ for interactive web
# viewers. This step only organizes files and never connects to the network.
#
#   iTOL       https://itol.embl.de      upload trees/coreSNP.nwk, drag itol/*.txt
#   Microreact https://microreact.org   upload tree + merged_metadata.csv (add lat/long for maps)
#   Phandango  https://phandango.net    drag tree + gene_presence_absence.csv
#   GrapeTree  https://achtman-lab.github.io/GrapeTree  MST Newick + grapetree_metadata.csv
#   icytree    https://icytree.org      quick unannotated tree viewer
# =============================================================================
set -euo pipefail
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
B="$PROJECT/11_visualization/online_bundle"
mkdir -p "$B/trees" "$B/itol" "$B/pangenome" "$B/amr"

cp_if () { [[ -f "$1" ]] && cp "$1" "$2" && echo "  + $2/$(basename "$1")"; }

cp_if "$PROJECT/09_phylogeny/core_iqtree.treefile"            "$B/trees"
cp_if "$PROJECT/09_phylogeny/core_fasttree.tre"               "$B/trees"
cp_if "$PROJECT/08_pangenome/core_gene_tree.treefile"         "$B/trees"
cp_if "$PROJECT/10_treetime/02_timetree/timetree.nexus"       "$B/trees"
find "$PROJECT/11_visualization/grapetree" -name "*.nwk" 2>/dev/null -exec cp {} "$B/trees" \;
cp_if "$PROJECT/11_visualization/merged_metadata.csv"         "$B"
cp_if "$PROJECT/08_pangenome/panaroo/gene_presence_absence.csv" "$B/pangenome"
cp_if "$PROJECT/07_amr_vf_mge/abricate/summary.tab"           "$B/amr"
find "$PROJECT/11_visualization/itol" -name "*.txt" 2>/dev/null -exec cp {} "$B/itol" \;

cat <<'EOF'
[done] online_bundle ready. Interactive options:
  iTOL       https://itol.embl.de      : upload trees/coreSNP.nwk, then drag itol/*.txt onto the tree
  Microreact https://microreact.org   : upload a Newick tree together with merged_metadata.csv
  Phandango  https://phandango.net    : drag a tree and pangenome/gene_presence_absence.csv
  GrapeTree  https://achtman-lab.github.io/GrapeTree : open an MST .nwk with the metadata table
  icytree    https://icytree.org      : fast tree-only inspection (no upload account needed)
EOF
