#!/usr/bin/env bash
# =============================================================================
# run_all.sh —— EasyIsolate 总控：按编号顺序执行整条流程
# 用法：bash run_all.sh config/my_samples.csv [起始步骤]
# 可从指定步骤恢复，如 bash run_all.sh config/my_samples.csv 06
# =============================================================================
set -euo pipefail
PROJECT=$(cd "$(dirname "$0")" && pwd); export PROJECT
SHEET=${1:-$PROJECT/config/my_samples.csv}
START=${2:-00}
[[ -f "$SHEET" ]] || { echo "找不到样本表 $SHEET"; exit 1; }
export -f true 2>/dev/null || true
echo "项目目录=$PROJECT 样本表=$SHEET 起始步骤=$START"

run_step () {  # $1=步骤号(用于与START比较) $2..=命令
  local num=$1; shift
  if [[ "$num" > "$START" || "$num" == "$START" || "$START" == "00" ]]; then
    echo "==================== 步骤 $num: $* ===================="
    "$@"
  fi
}

run_step 01 bash "$PROJECT/01_qc/01.fastp.sh"
# 三代(ONT/PacBio)/混合样本的长读质控；纯二代无长读时脚本会自动跳过
run_step 01 bash "$PROJECT/01_qc/01b.long_qc.sh"
run_step 02 bash "$PROJECT/02_decontam_reads/02.clean_reads.sh"
run_step 03 bash "$PROJECT/03_assembly/03.assemble.sh"
run_step 04 bash "$PROJECT/04_asm_qc/04.asm_qc_decontam.sh"
run_step 05 bash "$PROJECT/05_annotation/05.annotate.sh"
run_step 06 bash "$PROJECT/06_typing/06.1.mlst.sh"
run_step 06 bash "$PROJECT/06_typing/06.2.serotype.sh"
run_step 06 bash "$PROJECT/06_typing/06.3.cgmlst.sh"
run_step 07 bash "$PROJECT/07_amr_vf_mge/07.amr_vf_mge.sh"
run_step 08 bash "$PROJECT/08_pangenome/08.panaroo.sh"
run_step 09 bash "$PROJECT/09_phylogeny/09.snp_tree.sh"
run_step 10 bash "$PROJECT/10_treetime/10.treetime.sh"
python3 "$PROJECT/99_report/merge_results.py" "$PROJECT"

echo "全部完成。总表：99_report/master_table.tsv；时间树：10_timetree/02_timetree/timetree.nexus"
