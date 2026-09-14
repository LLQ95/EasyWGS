# 流程总览图（Figure 1）

![EasyWGS 端到端工作流程](assets/EasyWGS_workflow.png)

*图 1. 面向细菌分离株全基因组测序的 EasyWGS 端到端流程，版式参考 EasyMicrobiome 与 EasyMetagenome 系列指南。*

全图按顶部四个编号组成展开。左列列出模块 00 安装的 conda 环境、软件与参考数据库，蓝点表示软件、红点表示数据库。中列是分析主流程：原始 reads 与样本表先经过模块 01 的读长质控和模块 02 的读长层“保留目标物种”去污染，随后清洁 reads 进入两条并行路线。蓝色的组装路线（Route A）依次完成组装与打磨、以 CheckM2/GUNC/FCS-GX 进行第二层组装级去污染、注释、MLST/血清型/cgMLST 分型、耐药/毒力/可移动元件筛查、泛基因组与核心 SNP 分析；青色的参考比对路线（Route B）用 BWA 或 minimap2 把 reads 比对到统一参考，生成排序建索引的 BAM、覆盖度统计，并用 bcftools 检测得到过滤后的 VCF 与基因型矩阵。两条路线在比较与进化层汇合，把核心/附属基因、cgMLST 等位与核心 SNP 比对送入 IQ-TREE 3 系统树与 TreeTime 时间树。紫色的基因组 GWAS 层（模块 13）以泛基因组矩阵、VCF 和表型表为输入，运行 Scoary、PLINK 与 pyseer，再用 R 完成 post-GWAS。右列汇集模块 11 的可视化与模块 99 合并出的可复现结果。

颜色在全教程中保持一致：蓝色代表组装路线，青色代表参考比对路线，紫色代表 GWAS/post-GWAS，红色用于分区标题与输入/输出数据类型。

可编辑的矢量源、可直接投稿的 PDF 与高分辨率 PNG 位于 `figures/`（`EasyWGS_workflow.svg/.pdf/.png`）。该图由 `python figures/make_workflow_figure.py` 确定性生成，可直接改标签后重新导出，无需绘图软件。
