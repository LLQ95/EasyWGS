#!/usr/bin/env bash
# =============================================================================
# 07_amr_vf_mge/07.amr_vf_mge.sh —— 耐药、毒力、点突变、可移动元件
#   abricate 多库(CARD/ResFinder/NCBI/VFDB/PlasmidFinder/ISfinder/mobileOG/BacMet)
#   AMRFinderPlus、RGI(CARD)、PointFinder 染色体点突变
#   genomad(质粒/噬菌体)、Mob-suite(质粒重建)、antiSMASH(次级代谢BGC,可选)
# =============================================================================
set -euo pipefail
THREADS=8
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
GEN="$PROJECT/03_assembly/genomes"
OUT="$PROJECT/07_amr_vf_mge"; mkdir -p "$OUT"/{abricate,amrfinder,rgi,pointfinder,genomad,mobsuite,antismash}
DBROOT=${DBROOT:-$HOME/EasyIsolate_db}

# ---- 1) abricate 多数据库批量注释 + 汇总 ----
for db in card resfinder ncbi vfdb plasmidfinder ISfinder mobileOG BacMet2_EXP_database; do
  echo ">>> abricate --db $db"
  for f in "$GEN"/*.fasta; do abricate --threads "$THREADS" --db "$db" "$f"; done \
      | tee >(awk 'NR==1 || $0 !~ /^#File/' > "$OUT/abricate/${db}.tab") >/dev/null
done
abricate --summary "$OUT"/abricate/*.tab > "$OUT/abricate/summary.tab"

# ---- 2) AMRFinderPlus（基因 + 染色体突变，-p 蛋白可选；这里直接核酸）----
amrfinder --force_update -d "$DBROOT/amrfinder_db" || true
for f in "$GEN"/*.fasta; do
  id=$(basename "$f" .fasta)
  amrfinder -n "$f" -o "$OUT/amrfinder/${id}.tsv" --threads "$THREADS" --mutation_all "$OUT/amrfinder/${id}_mut.tsv"
done

# ---- 3) RGI(CARD, 蛋白同源, DIAMOND 加速)----
for f in "$GEN"/*.fasta; do
  id=$(basename "$f" .fasta)
  rgi main --input_sequence "$f" --output_file "$OUT/rgi/$id" \
           --local --clean -a DIAMOND --threads "$THREADS"
done

# ---- 4) PointFinder 染色体点突变（按物种 -s；文件名禁用下划线/多余点）----
SPECIES=${SPECIES:-salmonella}   # ecoli / klebsiella / campylobacter ...
for f in "$GEN"/*.fasta; do
  id=$(basename "$f" .fasta)
  python3 PointFinder.py -i "$f" -o "$OUT/pointfinder/$id" \
          -p "$DBROOT/pointfinder_db" -s "$SPECIES" -m blastn \
          -m_p "$(which blastn)" || echo "PointFinder 需单独下载并指定 -s 物种"
done

# ---- 5) genomad：质粒/前噬菌体/整合元件 ----
for f in "$GEN"/*.fasta; do
  id=$(basename "$f" .fasta)
  genomad end-to-end --cleanup --splits "$THREADS" "$f" "$OUT/genomad/$id" "$DBROOT/genomad_db"
done

# ---- 6) Mob-suite 质粒重建与分型 ----
for f in "$GEN"/*.fasta; do
  id=$(basename "$f" .fasta)
  mob_recon -i "$f" -o "$OUT/mobsuite/$id" -t "$THREADS"
done

# ---- 7) antiSMASH 次级代谢基因簇（按需，运行慢；输入 gbk）----
# for gbk in "$PROJECT"/05_annotation/prokka/*/*.gbk; do
#   id=$(basename "$gbk" .gbk)
#   antismash "$gbk" --output-dir "$OUT/antismash/$id" --asf --pfam2go --fullhmmer --cpus "$THREADS"
# done
echo "[完成] 耐药/毒力/元件结果：$OUT（summary.tab 为 abricate 各库命中汇总）"
