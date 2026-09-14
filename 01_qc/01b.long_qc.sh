#!/usr/bin/env bash
# =============================================================================
# 01_qc/01b.long_qc.sh —— 三代长读(ONT/PacBio)质控：去接头 → 质控视图 → 按质量/长度过滤
# 输入：samplesheet 中 platform 为 nanopore/pacbio/hybrid 样本的 longreads 列
# 说明：三代下机必须先去接头；NanoPlot 看长度/质量分布，Filtlong 保留高质量读段
# =============================================================================
set -euo pipefail
THREADS=16
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
SHEET="$PROJECT/config/my_samples.csv"
OUT="$PROJECT/01_qc/long"; mkdir -p "$OUT"/{raw_nanoplot,trim,clean}

# ONT 质量阈值（按需放宽/收紧）
MIN_LEN=1000          # 最短保留长度
MIN_QUAL=7            # 平均读段质量（Q7 对应约 80% 准确率，HiFi 可提到 12）
KEEP=400000000        # filtlong 目标保留碱基数(约覆盖基因组80x@5Mb)；0 表示不设目标

tail -n +2 "$SHEET" | while IFS=',' read -r id platform species r1 r2 lr rest; do
  [[ -z "$id" || "$id" == \#* ]] && continue
  case "$platform" in
    nanopore|pacbio|hybrid) ;;
    *) continue ;;
  esac
  L="$PROJECT/$lr"; [[ -f "$L" ]] || { echo "缺长读 $L，跳过 $id"; continue; }
  echo ">>> 长读质控 $id ($platform)"

  # 1) 原始读段质控视图
  NanoPlot --threads "$THREADS" -t "$L" -o "$OUT/raw_nanoplot/$id" --prefix raw_ || true

  # 2) 去接头（porechop；fastp 单端亦可：fastp -i in -o out）
  porechop -i "$L" -o "$OUT/trim/${id}.trim.fq.gz" --threads "$THREADS"

  # 3) 按长度+质量过滤；--target_bases 按总碱基数择优保留（留高质量、降冗余覆盖）
  if [[ "$KEEP" -gt 0 ]]; then
    filtlong --min_length "$MIN_LEN" --min_mean_q "$MIN_QUAL" \
             --target_bases "$KEEP" "$OUT/trim/${id}.trim.fq.gz" \
             | gzip > "$OUT/clean/${id}_L.fq.gz"
  else
    filtlong --min_length "$MIN_LEN" --min_mean_q "$MIN_QUAL" \
             "$OUT/trim/${id}.trim.fq.gz" | gzip > "$OUT/clean/${id}_L.fq.gz"
  fi

  # 4) 过滤后再出一次质控图，便于对比
  NanoPlot --threads "$THREADS" -t "$OUT/clean/${id}_L.fq.gz" \
           -o "$OUT/raw_nanoplot/$id" --prefix clean_ || true
done
echo "[完成] 干净长读：$OUT/clean/{id}_L.fq.gz（03 组装自动读取）"
