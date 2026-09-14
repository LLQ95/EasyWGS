#!/usr/bin/env bash
# =============================================================================
# 06_typing/06.2.serotype.sh —— 分物种血清型/表面抗原分型（按 samplesheet.species 调度）
#   kpsc 肺克 : Kleborate(内置Kaptive, 给 K/O 抗原、ST、耐药与毒力得分)
#   ecoli     : ECTyper(O:H 抗原、物种、stx) + ShigEiFinder(志贺/EIEC 分型)
#   salm 沙门 : SeqSero2(O/H) + SISTR(血清变种预测, 内含 cgMLST)
#   listeria  : 分子血清群（这里仅占位，主要分型走 06.3 cgMLST）
# 参考：Kleborate v3 用 -p 预设；v2 等价于 kleborate --all
# =============================================================================
set -euo pipefail
THREADS=8
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
GEN="$PROJECT/03_assembly/genomes"
OUT="$PROJECT/06_typing/serotype"; mkdir -p "$OUT"
SHEET="$PROJECT/config/my_samples.csv"

while IFS=',' read -r id species r1 r2 lr ref date country pheno taxid; do
  [[ "$id" == "id" || "$id" == \#* || -z "$id" ]] && continue
  f="$GEN/${id}.fasta"; [[ -f "$f" ]] || { echo "缺少组装 $f"; continue; }
  echo ">>> $id [$species]"
  case "$species" in
    kpsc)
      # 肺炎克雷伯复合群：Kleborate v3（集成 Kaptive 的 K 荚膜/O 脂多糖位点）
      mkdir -p "$OUT/kleborate"
      kleborate -a "$f" -o "$OUT/kleborate/${id}" -p kpsc --trim_headers --threads "$THREADS"
      # 若需要独立 Kaptive 详细 K/O 位点（Kaptive v3）：
      # kaptive get-loci --kaptive-table / kaptive assembly KpSC ... 见其 --help
      ;;
    ecoli)
      mkdir -p "$OUT/ectyper" "$OUT/shigeifinder"
      ectyper -i "$f" -o "$OUT/ectyper/$id" --cores "$THREADS"
      # 志贺/肠侵袭性大肠分型（组装模式；双端reads可用 -1/-2）
      shigeifinder -i "$f" -o "$OUT/shigeifinder/${id}.tsv" --threads "$THREADS" || \
        echo "  ShigEiFinder 参数随版本有差异，用 shigeifinder --help 核对"
      ;;
    salm)
      mkdir -p "$OUT/seqsero2" "$OUT/sistr"
      # -m k 为组装(k-mer)模式；输入reads时改 -m allele
      SeqSero2_package.py -m k -t "$THREADS" -i "$f" -d "$OUT/seqsero2/$id"
      sistr -i "$f" -f csv -o "$OUT/sistr/${id}.csv" -p CGMLST_PROFILES -n NOVEL_ALLELES
      ;;
    listeria)
      echo "  李斯特传统血清型意义有限，分子分型见 06.3.cgmlst.sh（Pasteur schema）" ;;
    other)
      echo "  other：跳过血清型，可用 abricate 自行扩展" ;;
    *) echo "  未知 species=$species（应为 kpsc/ecoli/salm/listeria/other）" ;;
  esac
done < "$SHEET"

# 同类工具结果汇总
cat "$OUT"/kleborate/*/*.txt 2>/dev/null | awk '!a[$1]++' > "$OUT/Kleborate_all.tsv" || true
find "$OUT/ectyper" -name output.csv -exec cat {} \; 2>/dev/null | awk '!a[$0]++' > "$OUT/ECTyper_all.csv" || true
find "$OUT/sistr"  -name '*.csv'      -exec cat {} \; 2>/dev/null > "$OUT/SISTR_all.csv" || true
echo "[完成] 血清型结果：$OUT（按工具分目录，_all 为合并表）"
