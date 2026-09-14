#!/usr/bin/env bash
# =============================================================================
# run_assembly.sh - ASSEMBLY-BASED pipeline (de novo route)
# One of two parallel main routes. Builds de novo assemblies first and derives
# every result from them: QC -> decontam -> assemble -> assembly QC gate ->
# annotation -> typing -> AMR/MGE -> pangenome -> core-SNP phylogeny (on
# assemblies) -> molecular dating -> merged report -> visualization.
#
# Usage: bash run_assembly.sh config/my_samples.csv [start step]
# Choose this route when no close finished reference exists, when gene content /
# accessory genome / plasmids / MGEs matter, or for phylogenetically diverse sets.
# =============================================================================
set -euo pipefail
PROJECT=$(cd "$(dirname "$0")" && pwd); export PROJECT
SHEET=${1:-$PROJECT/config/my_samples.csv}; START=${2:-00}
[[ -f "$SHEET" ]] || { echo "Samplesheet not found: $SHEET"; exit 1; }
step () { local n=$1; shift; if [[ "$n" > "$START" || "$n" == "$START" || "$START" == "00" ]]; then echo "== [assembly route] $n: $* =="; "$@"; fi; }

step 01 bash "$PROJECT/01_qc/01.fastp.sh"
step 01 bash "$PROJECT/01_qc/01b.long_qc.sh"
step 02 bash "$PROJECT/02_decontam_reads/02.clean_reads.sh"
step 03 bash "$PROJECT/03_assembly/03.assemble.sh"
step 04 bash "$PROJECT/04_asm_qc/04.asm_qc_decontam.sh"
step 05 bash "$PROJECT/05_annotation/05.annotate.sh"
step 06 bash "$PROJECT/06_typing/06.1.mlst.sh"
step 06 bash "$PROJECT/06_typing/06.2.serotype.sh"
step 06 bash "$PROJECT/06_typing/06.3.cgmlst.sh"
step 07 bash "$PROJECT/07_amr_vf_mge/07.amr_vf_mge.sh"
step 08 bash "$PROJECT/08_pangenome/08.panaroo.sh"
step 09 bash "$PROJECT/09_phylogeny/09.snp_tree.sh"      # uses --ctgs (assemblies)
step 10 bash "$PROJECT/10_treetime/10.treetime.sh"
python3 "$PROJECT/99_report/merge_results.py" "$PROJECT"
step 11 bash "$PROJECT/11_visualization/11.1.build_metadata.sh"
step 11 bash "$PROJECT/11_visualization/11.2.plot_trees.sh"
step 11 bash "$PROJECT/11_visualization/11.3.grapetree.sh"
step 11 bash "$PROJECT/11_visualization/11.4.itol_datasets.sh"
step 11 bash "$PROJECT/11_visualization/11.5.heatmaps.sh"
step 11 bash "$PROJECT/11_visualization/11.6.online_bundle.sh"
echo "[done] assembly-based route. See 99_report/master_table.tsv and 11_visualization/."
