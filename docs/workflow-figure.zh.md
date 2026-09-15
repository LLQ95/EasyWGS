# 流程总览图（Figure 1）

![EasyWGS 端到端工作流程](assets/EasyWGS_workflow.png)

*图 1. 面向细菌分离株全基因组测序的 EasyWGS 端到端流程，采用与 EasyMicrobiome、EasyMetagenome 系列指南一致的编号横向泳道式排版。*

全图自上而下分为六个编号横向泳道。每条泳道是一条浅色虚线色带，左侧为加粗的阶段名；每个工具集合压缩为一个简洁节点，节点内第一行为加粗标题，第二行用方括号列出调用的程序；深色直角箭头表示数据的流动、分叉与汇合。泳道 1 放置原始短读长（Illumina）与长读长（ONT/PacBio）。泳道 2 对短读长做 fastp 质控与读长层“保留目标物种”去污染（CLEAN、Kraken2/Bracken、BBDuk），对长读长做修剪与质量评估（Porechop、chopper、Filtlong、NanoPlot）。泳道 3 容纳两条并行路线：绿色的组装路线（Route A）依次完成组装与打磨、由 QUAST/CheckM2/GUNC/FCS-GX 组成的组装质量门（即第二层去污染）、Prokka/Bakta 注释，以及 MLST、血清型、cgMLST 分型和耐药与可移动元件筛查；青色的比对路线（Route B）用 BWA 或 minimap2 比对、用 bcftools 检测并过滤变异，构建核心 SNP 矩阵。两条路线在泳道 4 汇合，由 Panaroo 构建泛基因组，snippy、Gubbins、snp-sites 与 IQ-TREE 3 生成系统树，再由 TreeTime 完成定年、祖先状态与性状重建。泳道 5 用 Scoary、PLINK、pyseer 开展微生物基因组 GWAS，并在 R 中完成 post-GWAS；泳道 6 汇总可复现的整合结果，以及导出给 MultiQC、GrapeTree、iTOL、ggtree、Microreact 的系统树与注释包。

配色保持一致：绿色表示组装路线，青色表示参考比对路线，紫色表示 GWAS 阶段，其余泳道各用一种浅色，标题与编号使用红色。

可编辑的矢量源、可直接投稿的 PDF 与高分辨率 PNG 位于 `figures/`（`EasyWGS_workflow.svg/.pdf/.png`）。该图由 `python figures/make_workflow_figure.py` 确定性生成，可直接改标签后重新导出，无需绘图软件。
