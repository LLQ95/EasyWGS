#!/usr/bin/env bash
# =============================================================================
# 03_assembly/03.assemble.sh —— 按 platform 分流的二代/三代/混合组装与打磨
#   illumina : Unicycler 优先(单菌效果好、善处理质粒、倾向环化)；SPAdes --isolate 备选
#   nanopore : Flye 首选(Canu备选) → minimap2+Racon 2轮(慎用,防过校正) → Medaka 抛光
#   pacbio   : Flye --pacbio-hifi（HiFi）或 --pacbio-raw（CLR）
#   hybrid  : Unicycler --mode bold（推荐）或 SPAdes --nanopore/--pacbio；短读 Pilon 回填
# 可选：长读完成图用 longread 环境的 Trycycler 做多组装一致（见文末注释）
# 统一输出：03_assembly/genomes/{id}.fasta（已去除<200nt短contig）
# =============================================================================
set -euo pipefail
THREADS=16; MEM=128; MIN_CTG=200
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
SR="$PROJECT/01_qc/clean"                     # 二代干净读段
[[ -d "$PROJECT/02_decontam_reads/clean" ]] && SR="$PROJECT/02_decontam_reads/clean"
LR_DIR="$PROJECT/01_qc/long/clean"           # 三代干净长读（01b 产出）
SHEET="$PROJECT/config/my_samples.csv"
OUT="$PROJECT/03_assembly"; mkdir -p "$OUT/run" "$OUT/genomes"
source "$(conda info --base)/etc/profile.d/conda.sh"

polish_pilon () {  # $1=待抛光asm $2=R1 $3=R2 $4=outdir/前缀
  local asm=$1 r1=$2 r2=$3 pre=$4
  bwa index "$asm"
  bwa mem -t "$THREADS" "$asm" "$r1" "$r2" | samtools view -Sb - \
      | samtools sort -@ "$THREADS" -o "$pre.bam"
  samtools index "$pre.bam"
  # bioconda 版 pilon 为可执行脚本；jar 版请改用 java -jar pilon.jar
  pilon --genome "$asm" --frags "$pre.bam" --fix all --changes \
        --threads "$THREADS" --output "${pre}_pilon" --outdir "$(dirname "$pre")"
}

racon_rounds () {   # $1=asm $2=长读 $3=输出 $4=轮数(默认2)
  local asm=$1 reads=$2 out=$3 rounds=${4:-2} cur=$asm
  for ((i=1;i<=rounds;i++)); do
    minimap2 -ax map-ont -t "$THREADS" "$cur" "$reads" > "$OUT/run/tmp_$i.sam"
    racon -t "$THREADS" "$reads" "$OUT/run/tmp_$i.sam" "$cur" > "$OUT/run/racon_$i.fasta"
    cur="$OUT/run/racon_$i.fasta"; rm -f "$OUT/run/tmp_$i.sam"
  done
  cp "$cur" "$out"
}

tail -n +2 "$SHEET" | while IFS=',' read -r id platform species r1 r2 lr rest; do
  [[ -z "$id" || "$id" == \#* ]] && continue
  wd="$OUT/run/$id"; mkdir -p "$wd"; echo ">>> 组装 $id [$platform]"
  case "$platform" in
    illumina)
      # 单菌二代：优先 Unicycler；需要大样本/复杂时换 spades.py --isolate
      unicycler -1 "$SR/${id}_R1.fq.gz" -2 "$SR/${id}_R2.fq.gz" \
                -o "$wd" -t "$THREADS" --min_fasta_length "$MIN_CTG"
      cp "$wd/assembly.fasta" "$OUT/genomes/${id}.fasta"
      # 备选：spades.py --isolate -1 R1 -2 R2 -o wd -t T -m MEM && cp wd/scaffolds.fasta ;;
      ;;
    nanopore|pacbio)
      conda activate easyisolate
      L="$LR_DIR/${id}_L.fq.gz"; [[ -f "$L" ]] || L="$PROJECT/$lr"
      if [[ "$platform" == "pacbio" ]]; then
        flye --pacbio-hifi "$L" --genome-size 5m --threads "$THREADS" --out-dir "$wd/flye"
      else
        flye --nano-hq "$L" --genome-size 5m --threads "$THREADS" --out-dir "$wd/flye"
      fi
      # Racon 两轮（长读自校正，勿过多以防过校正）
      racon_rounds "$wd/flye/assembly.fasta" "$L" "$wd/racon.fasta" 2
      # Medaka 一致性抛光（独立环境；ONT 用 r941/r1041 对应模型，按芯片选 -m）
      conda activate longread
      medaka_consensus -i "$L" -d "$wd/racon.fasta" -o "$wd/medaka" -t "$THREADS" \
                       -m r1041_e82_400bps_sup_v4.2.0
      conda deactivate
      cp "$wd/medaka/consensus.fasta" "$OUT/genomes/${id}.raw.fasta" 2>/dev/null \
        || cp "$wd/racon.fasta" "$OUT/genomes/${id}.raw.fasta"
      seqkit seq -m "$MIN_CTG" "$OUT/genomes/${id}.raw.fasta" > "$OUT/genomes/${id}.fasta"
      ;;
    hybrid)
      conda activate easyisolate
      L="$LR_DIR/${id}_L.fq.gz"; [[ -f "$L" ]] || L="$PROJECT/$lr"
      # 推荐：Unicycler bold，长读 scaffold、短读校正，质粒/环化友好
      unicycler --mode bold -1 "$SR/${id}_R1.fq.gz" -2 "$SR/${id}_R2.fq.gz" -l "$L" \
                -o "$wd" -t "$THREADS" --min_fasta_length "$MIN_CTG" --keep 0
      # 用短读再做一轮 Pilon 回填纠错
      polish_pilon "$wd/assembly.fasta" "$SR/${id}_R1.fq.gz" "$SR/${id}_R2.fq.gz" "$wd/pilon"
      cp "$wd/pilon_pilon.fasta" "$OUT/genomes/${id}.fasta" 2>/dev/null \
        || cp "$wd/assembly.fasta" "$OUT/genomes/${id}.fasta"
      # 备选(SPAdes 混合)：spades.py --isolate -1 R1 -2 R2 --nanopore L -o wd2 -t T -m MEM
      ;;
    *) echo "未知 platform=$platform（应 illumina/nanopore/pacbio/hybrid）"; continue ;;
  esac
  # 统一去短 contig（若上游未处理）并统计
  seqkit seq -m "$MIN_CTG" "$OUT/genomes/${id}.fasta" > "$OUT/genomes/${id}.tmp" \
    && mv "$OUT/genomes/${id}.tmp" "$OUT/genomes/${id}.fasta"
done

seqkit stats -a -T -j "$THREADS" "$OUT/genomes"/*.fasta > "$OUT/genome_stats.tsv"
# 成环判断：Flye 见 run/*/flye/assembly_info.txt(circ=Y)；Unicycler 日志含 circular
# 完成图金标准(可选)：conda activate longread; trycycler cluster/reconcile/msa/partition/consensus
echo "[完成] 统一组装：$OUT/genomes/{id}.fasta；统计：genome_stats.tsv"
