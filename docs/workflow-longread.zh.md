# 三代与混合组装流程

三代流程对应 `01_qc/01b.long_qc.sh` 与 `03_assembly/03.assemble.sh` 的
nanopore、pacbio、hybrid 分支。长读的优势是跨过重复区、接近完成图，但错误率与
污染放大问题也更突出，需要额外的质控与抛光。

## 长读质控

先去接头，再用 NanoPlot 观察长度与质量分布，最后用 Filtlong 按长度、平均质量与
目标碱基数择优保留：

```bash
porechop -i ${id}_ONT.fastq.gz -o trim/${id}.fq.gz -t 16
NanoPlot -t 16 -t trim/${id}.fq.gz -o nanoplot/$id
filtlong --min_length 1000 --min_mean_q 7 --target_bases 400000000 \
         trim/${id}.fq.gz | gzip > clean/${id}_L.fq.gz
```

`--target_bases` 按基因组大小与目标覆盖度设置，用更少但更准的读段换取干净组装，
避免冗余覆盖拖慢抛光。ONT 不同芯片（R9.4.1、R10.4.1）质量分布不同，阈值随之微调。

## 纯长读组装

Flye 是默认组装器，对细菌长读稳定且自带成环判断；Canu 作为备选，适合覆盖不均或
需要更保守拼接的数据。PacBio HiFi 用 `--pacbio-hifi`，ONT 用 `--nano-hq` 或
`--nano-raw`：

```bash
flye --nano-hq ${id}_L.fq.gz --genome-size 5m -t 16 --out-dir run/$id/flye
# PacBio HiFi：flye --pacbio-hifi ...
# 备选：canu -p $id genomeSize=5m -nanopore-raw reads.fq.gz
```

## 抛光：校正要适度

长读组装需要一致性抛光，但抛光不是越多越好。脚本先用 minimap2 比对、Racon 做两
轮自校正，再用 Medaka 用神经网络做一轮一致性修正：

```bash
# Racon 两轮（不建议超过 2–3 轮，过多会过校正、抹掉真实变异）
minimap2 -ax map-ont asm.fasta reads.fq.gz > aln.sam
racon -t 16 reads.fq.gz aln.sam asm.fasta > racon1.fasta
# Medaka：模型必须匹配芯片与碱基识别版本
medaka_consensus -i reads.fq.gz -d racon2.fasta -o medaka -t 16 \
                 -m r1041_e82_400bps_sup_v4.2.0
```

追求发表级完成图时，建议在 longread 环境用 Trycycler 对多个组装做聚类、一致化，
再串联 Racon、Medaka；这一步计算量较大，作为可选高质量路径。

## 混合组装

同时有短读和长读时，优先 `unicycler --mode bold`：长读搭骨架跨越重复区，短读
负责碱基级纠错，对质粒与成环更有利；之后用短读跑一轮 Pilon 回填残余错误：

```bash
unicycler --mode bold -1 R1.fq.gz -2 R2.fq.gz -l L.fq.gz -o run/$id -t 16 --keep 0
bwa mem asm.fasta R1.fq.gz R2.fq.gz | samtools sort -o pilon.bam
pilon --genome asm.fasta --frags pilon.bam --fix all
```

SPAdes 也提供混合模式（`--nanopore` 或 `--pacbio`），作为交叉验证的备选。

## 成环判断

Flye 的 `assembly_info.txt` 用 circ 列标注环状 contig；Unicycler 日志会写明哪些
片段成环；需要标准化的成环与起点固定可用 circlator。完成图应看到染色体与各质粒
分别成环、无多余短 contig。

## 三代去污染的特殊风险

三代 contig 很长，基于短 k-mer 的 Kraken 在长读或组装层面分辨力下降，杂菌序列
容易被拼进一条完整 contig。因此三代数据的去污染要前置到 reads 层并结合组装层
FCS-GX 判断，且混合组装前务必先清洁短读，这一点在[去污染](decontamination.md)
展开。
