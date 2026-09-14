#!/usr/bin/env bash
# =============================================================================
# run_mapping.sh - REFERENCE-BASED pipeline (read mapping / BAM route)
# One of two parallel main routes. Maps cleaned reads directly to ONE close
# finished reference, calls variants with bcftools into multi-sample VCFs, then
# runs microbial GWAS and the shared reporting/visualization layer:
#   QC -> decontam -> map reads (BAM) -> joint calling (VCF/SNP matrix) ->
#   GWAS/post-GWAS (Scoary needs the optional pangenome from module 08) ->
#   merged report -> visualization
#
# Usage: TRAIT=MDR bash run_mapping.sh config/my_samples.csv [start step]
# Choose this route for clonal outbreak tracing with a high-quality close
# reference, when fast uniform SNP coordinates matter, or for large panels where
# per-isolate assembly is costly. Cross-check key conclusions with run_assembly.sh.
#
# Optional reference-based phylogeny (no assembly required), after 12.2:
#   zcat 12_mapping_pipeline/variants/snps.biallelic.vcf.gz > s.vcf
#   vcf2phylip -i s.vcf -f        # -> s.min4.fasta  (or use snp-sites/IQ-TREE)
#   iqtree3 -s s.min4.fasta -m GTR+G4 -alrt 1000 -bb 1000 -pre map_snp_tree
#   # then run module 10 TreeTime with config/metadata_dates.csv
# =============================================================================
set -euo pipefail
PROJECT=$(cd "$(dirname "$0")" && pwd); export PROJECT
SHEET=${1:-$PROJECT/config/my_samples.csv}; START=${2:-00}
[[ -f "$SHEET" ]] || { echo "Samplesheet not found: $SHEET"; exit 1; }
step () { local n=$1; shift; if [[ "$n" > "$START" || "$n" == "$START" || "$START" == "00" ]]; then echo "== [mapping route] $n: $* =="; "$@"; fi; }

step 01 bash "$PROJECT/01_qc/01.fastp.sh"
step 01 bash "$PROJECT/01_qc/01b.long_qc.sh"
step 02 bash "$PROJECT/02_decontam_reads/02.clean_reads.sh"
step 12 bash "$PROJECT/12_mapping_pipeline/12.run_mapping.sh"
# Gene-based Scoary/panseer need a pangenome; run module 08 to enable that layer.
[[ -d "$PROJECT/08_pangenome" ]] || echo "[note] run 08_pangenome to enable the gene-based Scoary layer of module 13."
step 13 bash "$PROJECT/13_gwas/13.run_gwas.sh"
python3 "$PROJECT/99_report/merge_results.py" "$PROJECT"
step 11 bash "$PROJECT/11_visualization/11.1.build_metadata.sh"
step 11 bash "$PROJECT/11_visualization/11.2.plot_trees.sh"
step 11 bash "$PROJECT/11_visualization/11.5.heatmaps.sh"
step 11 bash "$PROJECT/11_visualization/11.6.online_bundle.sh"
echo "[done] reference-based route. BAM/VCF in 12_mapping_pipeline/, GWAS in 13_gwas/."
