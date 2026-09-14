# 二代 Illumina 分析流程

对应脚本：`01_qc/01.fastp.sh`、`02_decontam_reads/02.clean_reads.sh`、
`03_assembly/03.assemble.sh`（platform=illumina 分支）。

## 质控与修剪

fastp 同时完成接头识别、滑动窗口质量修剪、过短读段剔除，并输出 HTML 报告。细菌
分离株一般采用温和阈值，避免把保守但 GC 偏高的区域误删：

```bash
fastp -i ${id}_R1.fastq.gz -I ${id}_R2.fastq.gz \
      -o clean/${id}_R1.fq.gz -O clean/${id}_R2.fq.gz \
      -q 20 -l 50 -w 8 -h qc/${id}.html -j qc/${id}.json \
      --detect_adapter_for_pe --correction
```

FastQC 与 MultiQC 在批次层面汇总，重点看接头残留、读段长度分布与重复率。

## reads 层去污染

修剪后的双端进入 02 模块，默认用 CLEAN 按目标类群保留读段，另可用 Kraken2 先做
一次成分侦察判断污染比例。近缘物种共存时调低激进程度，避免把同源序列误删，详见
[双层去污染与质量门控](decontamination.md)。

## 组装

对单个分离株，脚本默认使用 Unicycler。它在单菌数据上通常比直接跑 SPAdes 更干净，
对质粒更友好且倾向输出成环结果；需要在大量样本上统一参数或处理高覆盖数据时，可
切换到 `spades.py --isolate`：

```bash
# 默认：Unicycler
unicycler -1 ${id}_R1.fq.gz -2 ${id}_R2.fq.gz -o run/$id -t 16 --min_fasta_length 200

# 备选：SPAdes 单菌模式
spades.py --isolate -1 R1 -2 R2 -o run/$id -t 16 -m 128
```

组装后统一去除 200 nt 以下短片段，落到 `03_assembly/genomes/{id}.fasta`，并用
seqkit / assembly-stats 统计 contig 数、N50、总长度与 GC。

## 这一步要达到的标准

同种分离株的基因组大小、GC 应落在一个较窄区间，偏离过大往往提示污染或混合。二代
草图通常有数十至上百个 contig，关键不在 contig 最少，而在没有错误拼接，这由 04
模块用完整度、污染率与嵌合分进一步判断。

## 常见问题

覆盖度过低（低于约 30 倍）时组装碎片化明显，可在样本表标记后补测；重复区导致的
断裂属正常，不要为了减少 contig 数盲目合并。二代数据无法可靠区分高度重复的质粒
与染色体片段，需要质粒结构时改用混合组装或长读。
