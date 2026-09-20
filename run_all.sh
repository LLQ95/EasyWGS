#!/usr/bin/env bash
# =============================================================================
# run_all.sh - EasyWGS master runner: execute the whole pipeline in order
# Usage: bash run_all.sh config/my_samples.csv [start step]
# Resume from a given step, e.g. bash run_all.sh config/my_samples.csv 06
# =============================================================================
set -euo pipefail
PROJECT=$(cd "$(dirname "$0")" && pwd); export PROJECT
SHEET=${1:-$PROJECT/config/my_samples.csv}
START=${2:-00}
[[ -f "$SHEET" ]] || { echo "Samplesheet not found: $SHEET"; exit 1; }
echo "PROJECT=$PROJECT SAMPLESHEET=$SHEET START=$START"

run_step () {  # $1=step id compared with START, $2..=command
  local num=$1; shift
  if [[ "$num" > "$START" || "$num" == "$START" || "$START" == "00" ]]; then
    echo "==================== Step $num: $* ===================="
    "$@"
  fi
}

run_step 01 bash "$PROJECT/01_qc/01.fastp.sh"
# Long-read QC for ONT/PacBio/hybrid samples; auto-skipped for pure Illumina runs
run_step 01 bash "$PROJECT/01_qc/01b.long_qc.sh"
run_step 02 bash "$PROJECT/02_decontam_reads/02.clean_reads.sh"
run_step 03 bash "$PROJECT/03_assembly/03.assemble.sh"
run_step 04 bash "$PROJECT/04_asm_qc/04.asm_qc_decontam.sh"
# Whole-genome ANI species confirmation for the mixed multi-species panel (FastANI)
run_step 04 bash "$PROJECT/04_asm_qc/04.5.fastani_identity.sh"
run_step 05 bash "$PROJECT/05_annotation/05.annotate.sh"
run_step 06 bash "$PROJECT/06_typing/06.1.mlst.sh"
run_step 06 bash "$PROJECT/06_typing/06.2.serotype.sh"
run_step 06 bash "$PROJECT/06_typing/06.3.cgmlst.sh"
# Custom surface-antigen / toxin / virulence-locus screen for groups without a CLI serotyper
run_step 06 bash "$PROJECT/06_typing/06.4.surface_toxin_loci.sh"
run_step 07 bash "$PROJECT/07_amr_vf_mge/07.amr_vf_mge.sh"
run_step 08 bash "$PROJECT/08_pangenome/08.panaroo.sh"
run_step 09 bash "$PROJECT/09_phylogeny/09.snp_tree.sh"
run_step 10 bash "$PROJECT/10_treetime/10.treetime.sh"

# Parallel reference-based route (module 12): map cleaned reads to a shared FASTA
# reference into BAM files and call variants with bcftools. It does not need
# assemblies and runs alongside modules 03-10. To run ONLY this route use run_mapping.sh.
run_step 12 bash "$PROJECT/12_mapping_pipeline/12.run_mapping.sh"

# Microbial GWAS / post-GWAS (module 13): Scoary (pangenome genes, needs module 08),
# PLINK (module-12 SNPs) and pyseer (genes/SNPs with a distance kernel), then the
# shared R correction/plotting step. Select the phenotype column with TRAIT=<name>.
run_step 13 bash "$PROJECT/13_gwas/13.run_gwas.sh"

# Merge per-module results into one master table consumed by module 11
python3 "$PROJECT/99_report/merge_results.py" "$PROJECT"

# Downstream visualization (merged metadata, static R plots, GrapeTree MST,
# iTOL datasets, heatmaps and bundles for interactive web viewers)
run_step 11 bash "$PROJECT/11_visualization/11.1.build_metadata.sh"
run_step 11 bash "$PROJECT/11_visualization/11.2.plot_trees.sh"
run_step 11 bash "$PROJECT/11_visualization/11.3.grapetree.sh"
run_step 11 bash "$PROJECT/11_visualization/11.4.itol_datasets.sh"
run_step 11 bash "$PROJECT/11_visualization/11.5.heatmaps.sh"
run_step 11 bash "$PROJECT/11_visualization/11.6.online_bundle.sh"

echo "All done. Master table: 99_report/master_table.tsv; time tree: 10_treetime/02_timetree/timetree.nexus; figures and bundles: 11_visualization/"
