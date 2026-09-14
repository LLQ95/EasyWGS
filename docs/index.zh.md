# EasyWGS Guidebook

EasyWGS 是一套面向细菌分离株全基因组测序（WGS）的可复现分析流程与配套教程，
组织方式参考 EasyMicrobiome、EasyMetagenome：每个分析阶段对应一个编号目录，
目录内脚本改顶部参数即可批量运行，阶段之间用统一命名衔接。它同时支持二代
Illumina、三代 Oxford Nanopore / PacBio，以及短读加长读的混合组装，并把 reads
与 assembly 两个层面的去污染做成质量门控，避免杂菌或宿主序列进入分型与进化分析。

## 这套流程解决什么问题

分离株测序的原始数据里常混入宿主、PhiX、其他菌种，三代长读还会把污染片段拼成
一条很长的错误 contig；如果直接组装并分型，会得到错误的 ST、血清型和进化位置。
EasyWGS 用一套固定顺序覆盖从原始 fastq 到时间树的完整链路，并在关键节点给出
完整度、污染率、嵌合度的量化判断，只有通过门控的组装才进入下游。

## 流程总览

```text
原始 fastq
 ├─ 二代: fastp → CLEAN 去污染 → Unicycler/SPAdes 组装
 ├─ 三代: porechop/NanoPlot/Filtlong → Flye/Canu → Racon→Medaka
 └─ 混合: 上述短读+长读 → Unicycler bold/SPAdes hybrid → Pilon 回填
        ↓
 04 QUAST + CheckM2 + GUNC (+FCS-GX) 组装质量门控
        ↓
 05 注释  →  06 MLST/血清型/cgMLST  →  07 耐药·毒力·元件
        ↓
 08 泛基因组  →  09 核心SNP系统发育  →  10 TreeTime 时间树  →  99 汇总
```

## 适用范围

流程默认针对肺炎克雷伯复合群、大肠埃希/志贺、沙门菌、单核增生李斯特菌等主要
致病菌做了分型调度，其他菌种可通过 `species=other` 跑通用步骤并按需挂载 cgMLST
schema。流程面向有一台 Linux 工作站、WSL2 或 HPC 的使用者，数据库体积与内存
要求在[安装](installation.md)一章逐项说明。

## 从哪里开始

第一次使用按顺序阅读[安装](installation.md)、[快速开始](quickstart.md)与
[输入与样本表](samplesheet.md)；已经有组装结果、只想做分型或建树的读者，可直接
跳到对应分析模块章节。
