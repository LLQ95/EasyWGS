# 工具地图（二代/三代对照）

下表把流程涉及的工具按阶段汇总，并标注主要适用的测序平台。「共用」表示对二代、
三代与混合组装结果同样适用。脚本位置即对应编号目录。

## 数据获取与质控

| 工具 | 平台 | 阶段 | 作用 |
| --- | --- | --- | --- |
| fastp | 二代/三代单端 | 01 | 去接头、质量修剪、报告 |
| FastQC/MultiQC | 共用 | 01 | 质控视图与批次汇总 |
| porechop/chopper | 三代 | 01b | 长读去接头、按长度质量切分 |
| NanoPlot | 三代 | 01b | 长度/质量分布 |
| Filtlong | 三代 | 01b | 长读择优过滤 |
| NCBI datasets/SRA toolkit | 共用 | 数据获取 | 下载公开读段与组装 |

## 去污染

| 工具 | 平台 | 阶段 | 作用 |
| --- | --- | --- | --- |
| CLEAN | 二代/三代/fasta | 02 | reads 层按目标类群保留 |
| Kraken2/Bracken | 二代优先 | 02 | 物种成分侦察 |
| BBDuk/HoCoRT/deacon | 二代 | 02 | 参考序列/接头剔除 |
| CheckM2 | 组装 | 04 | 完整度、污染率 |
| GUNC | 组装 | 04 | 嵌合基因组检测 |
| FCS-GX/BlobToolKit | 组装 | 04 | 外源片段净化与可视化 |

## 组装与抛光

| 工具 | 平台 | 阶段 | 作用 |
| --- | --- | --- | --- |
| Unicycler | 二代/混合 | 03 | 单菌组装、bold 混合、倾向成环 |
| SPAdes | 二代/混合 | 03 | --isolate、--nanopore/--pacbio |
| Flye | 三代 | 03 | 长读组装与成环标记 |
| Canu | 三代 | 03 | 保守长读组装 |
| dragonflye | 三代 | 03 | SPAdes 式长读流水线（备选） |
| Trycycler | 三代 | 03 | 多组装一致，完成图金标准 |
| minimap2+Racon | 三代 | 03 | 长读自校正（限 2–3 轮） |
| Medaka | 三代 ONT | 03 | 神经网络一致性抛光 |
| Pilon | 混合/二代 | 03 | 短读回填纠错 |
| circlator | 组装 | 03 | 成环与起点固定 |
| QUAST/seqkit/assembly-stats | 共用 | 03/04 | 组装统计 |

## 注释与分型

| 工具 | 平台 | 阶段 | 作用 |
| --- | --- | --- | --- |
| Prokka/Bakta/Prodigal | 共用 | 05 | 结构注释 |
| eggNOG-mapper | 共用 | 05 | GO/KEGG/COG |
| mlst | 共用 | 06 | 7 基因 MLST |
| Kleborate(Kaptive) | 共用 | 06 | 肺克 ST、K/O 抗原、耐药毒力 |
| ECTyper/ShigEiFinder | 共用 | 06 | 大肠 O:H、志贺/EIEC |
| SeqSero2/SISTR | 共用 | 06 | 沙门抗原与血清变种 |
| chewBBACA | 共用 | 06 | cgMLST 全流程 |

## 耐药、毒力与可移动元件（07）

| 类别 | 工具 |
| --- | --- |
| 耐药/毒力库 | abricate(ResFinder/VFDB/CARD/MEGARes/ecoli_vf)、AMRFinderPlus、RGI |
| 点突变 | PointFinder |
| 质粒 | mob-suite、PlasmidFinder、PLSDB、PlasFlow |
| 整合子/插入序列/ICE | IntegronFinder、ISEScan/ISfinder、mobileOG、MGEfinder、oriT/relaxase 库 |
| 噬菌体/基因组岛 | VirSorter2、PhiSpy、IslandPath、PHASTER、genomad |
| CRISPR | CRISPRCasFinder |

## 比较、进化与去冗余

| 工具 | 阶段 | 作用 |
| --- | --- | --- |
| Panaroo/Roary | 08 | 泛基因组 |
| snippy/Gubbins/snp-sites/IQ-TREE/FastTree/snp-dists | 09 | 核心 SNP 树与距离 |
| TreeTime | 10 | 分子钟、时间树、祖先、迁移 |
| mash/dereplicator/cd-hit | 辅助 | 基因组去冗余与快速聚类 |
| MAFFT/MUMmer | 辅助 | 比对与共线性 |

## 扩展主题（非默认步骤）

基因组 GWAS/Post-GWAS、TWAS、RNA-seq、HUMAnN/MetaPhlAn 等属于转录组、关联或
宏基因组范畴，本仓库在 guidebook 预留章节说明与 WGS 主流程的衔接点，但不在
run_all 默认链路中，避免把分离株流程与无关分析混杂。
