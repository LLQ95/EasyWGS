# EasyIsolate：细菌分离株全基因组分析实用流程（Easy WGS Pipeline）

面向主要致病菌（肺炎克雷伯、大肠/志贺、沙门、单核增生李斯特等）的一站式 WGS 流程，
组织方式参考 EasyMicrobiome / EasyMetagenome：按编号目录顺序执行，改顶部路径即可用。
同时覆盖二代 Illumina、三代 ONT/PacBio 与 hybrid 混合组装，串联质控、双层去污染、
组装与打磨、组装评估、注释、MLST、分物种血清型、cgMLST、耐药/毒力/可移动元件、
泛基因组、核心 SNP 系统发育，以及 TreeTime 时间树。

完整图文教程见 Read the Docs：https://easyisolate.readthedocs.io 。Guidebook 为中英双语，
英文为默认版本，页头语言切换器可切到简体中文；本地用 `mkdocs serve` 预览。
仓库地址 https://github.com/LLQ95/EasyIsolate 。

## 一、三类测序场景与分析主线

```
二代 Illumina 双端：
  01_qc(fastp) → 02 去污染(CLEAN) → 03(Unicycler优先/SPAdes备选) → 04 质检门控 → …
三代 ONT/PacBio：
  01b 长读QC(porechop+NanoPlot+Filtlong) → 03(Flye→Racon→Medaka，可选Trycycler) → …
混合 hybrid：
  01+01b → 02(短读去污染) → 03(Unicycler --mode bold / SPAdes hybrid，Pilon回填) → …

04_asm_qc  QUAST+CheckM2+GUNC+(可选)FCS-GX 组装层去污染门控
05_annotation  Prokka/Bakta、Prodigal、eggNOG(GO/KEGG/COG)
06_typing   6.1 MLST；6.2 分物种血清型；6.3 chewBBACA cgMLST
07_amr_vf_mge  abricate多库+AMRFinder/RGI/PointFinder+genomad/Mob-suite/integronfinder/antiSMASH
08_pangenome   Panaroo(备选Roary)
09_phylogeny   snippy→Gubbins→IQ-TREE→snp-dists
10_treetime    clock离群、时间树、祖先重建、同源突变、状态迁移
99_report      汇总主表与出图
```

## 二、快速开始

```bash
bash 00_install/install_env.sh      # 建环境（含长读 longread 环境）
bash 00_install/download_db.sh      # 数据库，仅一次
# 数据放 00_rawdata/，复制并填写样本表（platform 决定二/三/混合路线）
cp config/samplesheet.csv config/my_samples.csv
bash run_all.sh config/my_samples.csv           # 一键
bash run_all.sh config/my_samples.csv 06        # 或从指定步骤恢复
```

样本表关键字段：platform 取 illumina / nanopore / pacbio / hybrid；species 取
kpsc / ecoli / salm / listeria / other，决定 06 的血清型与 cgMLST 调度。

## 三、分物种分型调度（06 模块）

| 类群 | 7基因MLST | 血清型/表面抗原 | cgMLST schema |
| --- | --- | --- | --- |
| kpsc 肺克复合群 | mlst | Kleborate(集成Kaptive，K/O 抗原) | INNUENDO/自建 |
| ecoli 大肠/志贺 | mlst | ECTyper(O:H)+ShigEiFinder(志贺/EIEC) | EnteroBase E./Shigella |
| salm 沙门 | mlst | SeqSero2+SISTR | INNUENDO cgMLST99 |
| listeria 李斯特 | mlst | 分子血清群(走cgMLST) | Pasteur cgMLST |
| other | mlst 自动识别 | 按需扩展 | PrepExternalSchema |

## 四、命名与硬件约定

组装统一落到 `03_assembly/genomes/{id}.fasta`（已去 <200nt 短 contig），04 起都对该目录批量处理。
文件名避免空格与多余点号。FCS-GX 库约 470 GB、建议 512 GB 内存，普通机器可跳过本地、
改在 usegalaxy.org 在线运行，04 仍保留 CheckM2/GUNC 门控。

## 五、仓库结构与文档

编号目录即可执行脚本；docs/ 为 Read the Docs guidebook 源（MkDocs Material）；
.github/ 提供文档自动构建。本流程整合 LLQ95/Practical-Encyclopedia-of-Whole-Genome-Analysis
的成熟经验，补入双层去污染、肺克/大肠志贺血清型、三代完整打磨链与 TreeTime 闭环。
