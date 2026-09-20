# 工具百科：推荐、备选与经典旧代（替代关系）

本页是 EasyWGS 的“工具谱系”总表，按分析阶段收录细菌分离株全基因组测序中常见的工具，并标注每个工具的状态与替代关系。它与《工具地图（二代/三代对照）》互补：后者只列出 EasyWGS 默认使用的软件，本页则尽量覆盖该阶段在文献与实际工作中仍可能遇到的全部常见选择，方便阅读旧文献、复现历史流程，或在默认工具不适用时挑选替代品。

## 如何阅读状态

- 推荐默认（Recommended default）：EasyWGS 主流程当前采用的工具，通常在准确性、速度和维护活跃度之间较均衡。
- 活跃备选（Alternative）：仍在维护、可直接替换默认工具的选择，在特定数据或场景下可能更合适。
- 经典旧代（Legacy, still usable）：出现较早、如今多有继任者，但仍可安装运行；阅读旧文献或复现旧项目时会遇到。“替代/继任”只表示当前更推荐的方向，并不表示旧工具失效，很多旧工具至今仍被接受（例如提交公共数据库时 CheckM 与 CheckM2 均被认可）。

“替代关系（Lineage）”一列用箭头表示旧代到继任者的方向；若为 “-” 表示该工具没有单一继任者，或属于长期并存的不同路线。平台列标注其主要适用的数据类型。

## 1. 数据获取

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| SRA Toolkit (fasterq-dump) | 推荐默认 | - | shared | 下载 SRA/ENA 公共 reads |
| NCBI datasets / ENA filer | 活跃备选 | - | shared | 下载基因组/组装与 reads |
| EDirect (esearch/efetch) | 活跃备选 | - | shared | 命令行检索 NCBI |
| fastq-dump | 经典旧代（仍可运行） | -> fasterq-dump | shared | 旧版 SRA 转换，速度慢 |
| Dorado | 推荐默认 | replaces Guppy/Albacore | ONT | ONT 现行 basecaller（FASTQ 上游） |
| Guppy | 经典旧代（仍可运行） | -> Dorado | ONT | 上一代 ONT basecaller |
| Albacore | 经典旧代（仍可运行） | -> Guppy -> Dorado | ONT | 早期 ONT basecaller |
| SMRT Link / ccs (HiFi) | 活跃备选 | replaces Quiver pipeline | PacBio | PacBio HiFi 一致性生成 |

## 2. 二代质控

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| fastp | 推荐默认 | replaces Trimmomatic/Sickle in role | short | 单遍接头质量修剪与 HTML 报告 |
| FastQC + MultiQC | 推荐默认 | - | shared | 单样本质控图与汇总报告 |
| Cutadapt | 活跃备选 | - | short | 精确接头/引物修剪，仍常用 |
| AdapterRemoval v2 | 活跃备选 | - | short | 接头修剪与配对重叠合并 |
| BBDuk (BBTools) | 活跃备选 | - | short | k-mer 修剪/过滤，也可去污染 |
| Trimmomatic | 经典旧代（仍可运行） | -> fastp | short | 经典滑窗接头质量修剪 |
| Sickle | 经典旧代（仍可运行） | -> fastp | short | 简易滑窗质量修剪 |
| FASTX-Toolkit | 经典旧代（仍可运行） | -> fastp/Cutadapt | short | 旧版 reads 处理工具包 |
| PRINSEQ(-lite) | 经典旧代（仍可运行） | -> fastp | short | 旧版质控过滤与复杂度评估 |
| AfterQC / NGS QC Toolkit | 经典旧代（仍可运行） | -> fastp | short | 早期质控过滤套件 |

## 3. 三代质控

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| NanoPlot / NanoComp | 推荐默认 | - | long | 读长/质量/产量绘图 |
| chopper | 推荐默认 | replaces NanoFilt/NanoLyse in role | long | 快速质量长度过滤（Rust） |
| Filtlong | 推荐默认 | - | long | 按质量权重过滤长读 |
| Porechop_ABI | 活跃备选 | - | long | 从头识别接头修剪的活跃分支 |
| Porechop | 活跃备选 | maintenance limited | long | 经典 ONT 接头/Barcode 修剪 |
| NanoFilt / NanoLyse | 经典旧代（仍可运行） | -> chopper/Filtlong | long | 流式过滤与污染剔除 |
| NanoQC | 活跃备选 | - | long | 快速批次质量对比 |

## 4. 读长层去污染

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| CLEAN | 推荐默认 | - | short/long/FASTA | 保留目标、剔除污染的去污染 |
| Kraken2 + Bracken | 推荐默认 | Kraken2 replaces Kraken1 | mainly short | 清洗前核查物种构成 |
| BBDuk / BBsplit | 活跃备选 | - | short | 按参考剔除或分箱 reads |
| HoCoRT / deacon | 活跃备选 | - | short | 宿主 reads 剔除 |
| KneadData | 活跃备选 | - | short | 质控+去宿主一体化流程 |
| FastQ Screen | 活跃备选 | - | short | 检查 reads 是否匹配多个基因组 |
| Kraken 1 | 经典旧代（仍可运行） | -> Kraken2 | short | 一代精确 k-mer 分类器 |
| DeconSeq | 经典旧代（仍可运行） | -> BBDuk/CLEAN | short | 早期去宿主/污染工具 |

## 5. 二代与混合组装

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| SPAdes | 推荐默认 | replaces Velvet/IDBA in role | short/hybrid | de Bruijn 分离株组装器 |
| Unicycler | 推荐默认 | - | short/hybrid | 混合组装并倾向成环 |
| Shovill | 活跃备选 | - | short | SPAdes 加速封装 |
| SKESA | 活跃备选 | - | short | NCBI 保守策略 k-mer 组装 |
| MEGAHIT | 活跃备选 | - | short/meta | 极省内存的组装器 |
| MaSuRCA | 活跃备选 | - | hybrid | 混合 OLC/de Bruijn 组装 |
| ABySS | 活跃备选 | - | short | 可扩展双端组装 |
| A5-miseq | 经典旧代（仍可运行） | -> SPAdes/Unicycler | short | 开箱即用 MiSeq 组装 |
| IDBA / IDBA-UD | 经典旧代（仍可运行） | -> SPAdes/MEGAHIT | short/meta | 迭代 k-mer 组装器 |
| Velvet (+VelvetOptimiser) | 经典旧代（仍可运行） | -> SPAdes | short | 最早的 de Bruijn 组装器 |
| SOAPdenovo2 | 经典旧代（仍可运行） | -> SPAdes | short | 大基因组二代组装器 |
| MIRA / Edena / CISA | 经典旧代（仍可运行） | -> SPAdes/Unicycler | short | 早期重叠一致与合并工具 |

## 6. 三代组装

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| Flye | 推荐默认 | - | long | 感知重复的长读组装器 |
| Trycycler | 推荐默认 | - | long | 多组装一致性，完成图金标准 |
| Canu | 活跃备选 | replaces Celera Assembler | long | 保守 OLC 长读组装器 |
| hifiasm | 活跃备选 | - | PacBio HiFi | 快速 HiFi 组装并可分型 |
| wtdbg2 | 活跃备选 | - | long | 快速模糊 de Bruijn 组装 |
| Raven | 活跃备选 | - | long | miniasm 衍生快速组装 |
| dragonflye | 活跃备选 | - | long | 类 SPAdes 的长读流程封装 |
| NextDenovo / NECAT | 活跃备选 | - | long | 高效纠错后组装 |
| miniasm | 经典旧代（仍可运行） | -> Flye/Trycycler | long | 超快原始布局，需 Racon 打磨 |
| SMARTdenovo | 经典旧代（仍可运行） | -> Flye/Canu | long | 早期 OLC 长读组装 |
| Celera Assembler | 经典旧代（仍可运行） | -> Canu | long | 最早的长读组装器 |
| HGAP / FALCON | 经典旧代（仍可运行） | -> Canu/hifiasm (HiFi) | PacBio CLR | 旧 PacBio 组装流程 |

## 7. 组装打磨

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| Medaka | 推荐默认 | replaces Nanopolish in convenience | ONT | 神经网络一致性打磨，无需 FAST5 |
| Racon | 推荐默认 | - | long | 偏序长读自纠错（2-3 轮） |
| Pilon | 推荐默认 | - | short/hybrid | 短读纠错与补洞 |
| NextPolish | 活跃备选 | - | short/long | 双模式短/长读打磨 |
| Polypolish / POLCA | 活跃备选 | - | short | 减少引入新错误的短读打磨 |
| ntEdit / Sealer | 活跃备选 | - | short | 布隆过滤纠错与补洞 |
| Apollo | 活跃备选 | - | shared | 大基因组组装打磨 |
| Nanopolish | 经典旧代（仍可运行） | -> Medaka | ONT | 需电信号 FAST5 的打磨 |
| Quiver / Arrow (GCpp) | 经典旧代（仍可运行） | -> ccs/DeepVariant (HiFi) | PacBio | 旧 PacBio 一致性打磨 |

## 8. 组装质检与去污染

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| QUAST | 推荐默认 | - | shared | N50、连续性与错装指标 |
| seqkit / assembly-stats | 推荐默认 | - | shared | 序列统计与处理 |
| CheckM2 | 推荐默认 | replaces CheckM1 | assembly | 机器学习完整度/污染，快速稳健 |
| GUNC | 推荐默认 | - | assembly | 嵌合基因组/谱系不一致检测 |
| FCS-GX | 推荐默认 | - | assembly | NCBI 外源片段污染筛查 |
| BlobToolKit (BlobTools2) | 活跃备选 | - | assembly | 覆盖度/分类/GC 交互排查 |
| BUSCO | 活跃备选 | - | shared | 单拷贝直系同源完整度（真核为主；真菌用 fungi_odb10/ascomycota_odb10） |
| Merqury | 活跃备选 | - | assembly | 基于 k-mer 的一致性 Q 值 |
| CheckM (v1) | 活跃备选 | succeeded by CheckM2 | assembly | 谱系 marker 质检，仍可用可解释 |
| RefineM | 经典旧代（仍可运行） | -> CheckM2/GUNC | assembly | 旧版 bin/污染精炼 |
| proDeGe | 经典旧代（仍可运行） | -> FCS-GX/CheckM2 | assembly | 早期污染剔除工具 |

## 9. 结构与功能注释

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| Bakta | 推荐默认 | modern successor in role to Prokka | shared | 标准化注释，稳定 RefSeq/UniRef ID |
| Prodigal | 推荐默认 | replaces Glimmer in role | shared | 原核基因/CDS 预测 |
| eggNOG-mapper | 推荐默认 | - | shared | COG/GO/KEGG 功能注释 |
| DIAMOND | 推荐默认 | - | shared | 快速类 BLAST 蛋白比对 |
| Prokka | 活跃备选 | succeeded in role by Bakta | shared | 快速经典注释，与 Bakta 命令兼容 |
| PGAP (NCBI) | 活跃备选 | - | shared | NCBI 提交级注释流程 |
| DFAST | 活跃备选 | - | shared | DDBJ 支持的注释工具 |
| InterProScan | 活跃备选 | - | shared | 蛋白结构域与 GO 注释 |
| BLAST+ | 活跃备选 | - | shared | 参考序列相似性搜索 |
| barrnap | 推荐默认 | replaces RNAmmer in role | shared | 快速 rRNA 预测 |
| tRNAscan-SE | 推荐默认 | - | shared | tRNA 预测 |
| Aragorn / Infernal+Rfam | 活跃备选 | - | shared | tmRNA/tRNA 与 ncRNA 注释 |
| RAST / RASTtk | 经典旧代（仍可运行） | -> Bakta/PGAP | shared | 早期网页注释服务 |
| Glimmer3 / GeneMarkS | 经典旧代（仍可运行） | -> Prodigal | shared | 旧基因预测（GeneMark 许可受限） |
| RNAmmer | 经典旧代（仍可运行） | -> barrnap | shared | 旧 HMM rRNA 预测 |
| KAAS / GhostKOALA | 经典旧代（仍可运行） | -> eggNOG-mapper | shared | 旧 KEGG 在线注释 |

## 10. 多位点序列分型

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| mlst (tseemann) | 推荐默认 | - | shared | 从组装做七基因 ST |
| PubMLST / BIGSdb | 活跃备选 | - | shared | 权威 scheme 数据库平台 |
| StringMLST / MentaLiST | 活跃备选 | - | shared | 直接从 reads 的 k-mer MLST |
| CGE MLST finder (web) | 活跃备选 | - | shared | 在线 MLST 分型 |
| SRST2 | 经典旧代（仍可运行） | -> mlst/ARIBA in role | short | 基于 reads 的 MLST/耐药分型 |

## 11. 血清型分型

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| Kleborate (+Kaptive) | 推荐默认 | - | shared | 肺克 ST、K/O、耐药与毒力评分 |
| ECTyper | 推荐默认 | - | shared | 大肠 O:H 与系统群分型 |
| ShigEiFinder | 推荐默认 | - | shared | 志贺/EIEC 鉴别与血清型 |
| SeqSero2 | 推荐默认 | replaces SeqSero | shared | 沙门 O/H 抗原预测 |
| SISTR | 推荐默认 | - | shared | 沙门血清型预测 |
| SerotypeFinder (CGE) | 活跃备选 | - | shared | 基于基因的大肠 O/H |
| Kaptive (standalone) | 活跃备选 | - | shared | 表面多糖位点分型 |
| LisSero / emm typer | 活跃备选 | - | shared | 李斯特血清群与链球菌 emm |
| SeqSero | 经典旧代（仍可运行） | -> SeqSero2 | shared | 一代沙门血清型工具 |
| spaTyper (CGE) | 活跃备选 | - | shared | 金葡 spa 重复序列排序与 spa 型 |
| SCCmecFinder (CGE) | 活跃备选 | - | shared | 金葡 SCCmec 盒与 mec 复合体（staphopia-sccmec 为开源替代） |
| BTyper3 | 活跃备选 | - | shared | 蜡样芽胞杆菌群 panC 系统群、毒力与次级代谢位点 |
| fast-lineage-caller | 活跃备选 | - | shared | 结核基于组装/VCF 的快速谱系分型 |
| MTBseq | 活跃备选 | - | short | 结核基于 reads 的谱系、耐药与 SNP/indel 流程 |

## 12. 核心/全基因组 MLST

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| chewBBACA | 推荐默认 | - | shared | 等位调用与 cg/wgMLST 流程 |
| PubMLST/BIGSdb | 活跃备选 | - | shared | 权威 cgMLST scheme 与比较 |
| MentaLiST | 活跃备选 | - | shared | 可扩展 k-mer cgMLST |
| Ridom SeqSphere+ | 活跃备选 | commercial | shared | 监测常用商业 cgMLST 套件 |

## 13. 耐药与毒力

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| abricate | 推荐默认 | - | shared | 多数据库耐药毒力筛查 |
| NCBI AMRFinderPlus | 推荐默认 | - | shared | 权威 AMR 注释与隐藏命中校正 |
| CARD / RGI | 推荐默认 | - | shared | 耐药本体与基因/等位匹配 |
| ResFinder + PointFinder | 推荐默认 | - | shared | 获得性基因与染色体点突变 |
| Mykrobe | 活跃备选 | - | short | 快速 k-mer 耐药预测 |
| TB-Profiler | 活跃备选 | - | shared | 结核谱系与耐药预测 |
| VirulenceFinder / VFDB | 活跃备选 | - | shared | 毒力基因库与检测 |
| KMA | 活跃备选 | - | short | 新版 CGE 服务所用 k-mer 比对 |
| DeepARG | 活跃备选 | - | shared | 机器学习耐药基因预测 |
| ARIBA | 经典旧代（仍可运行） | -> abricate/ResFinder | short | 局部聚类的 reads 耐药分析 |
| ARG-ANNOT | 经典旧代（仍可运行） | -> ResFinder/CARD | shared | 旧耐药数据库，已停止更新 |
| KmerResistance | 经典旧代（仍可运行） | -> ResFinder (KMA) | short | 旧 k-mer 耐药检测 |

## 14. 质粒与可移动元件

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| mob-suite | 推荐默认 | - | assembly | 质粒重建、分型与可迁移性 |
| PlasmidFinder | 推荐默认 | - | shared | 复制子不相容群分型 |
| PLSDB | 活跃备选 | - | shared | 质粒数据库与检索 |
| IntegronFinder | 推荐默认 | - | shared | 整合子与 attC 检测 |
| ISEScan | 推荐默认 | - | shared | 插入序列注释 |
| MGEfinder / mobileOG-db | 活跃备选 | - | shared | MGE 插入与功能注释 |
| ICEberg / oriTfinder | 活跃备选 | - | shared | 整合接合元件与转移起点资源 |
| mlplasmids / PlasFlow | 活跃备选 | - | shared | 区分染色体与质粒 contig |
| PLACNETw | 活跃备选 | - | shared | 图论质粒重建网页工具 |
| cBar / Recycler | 经典旧代（仍可运行） | -> mob-suite | assembly | 旧版质粒分箱 |

## 15. 前噬菌体/基因岛/CRISPR

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| geNomad | 推荐默认 | - | shared | 病毒/质粒元件分类器 |
| PhiSpy | 推荐默认 | - | shared | 前噬菌体区域预测 |
| VirSorter2 | 推荐默认 | replaces VirSorter1 | shared | 病毒/前噬菌体序列识别 |
| CRISPRCasFinder | 推荐默认 | - | shared | CRISPR 阵列与 cas 分型 |
| IslandViewer4 / IslandPath-DIMOB | 活跃备选 | - | shared | 基因岛预测 |
| MinCED | 活跃备选 | - | shared | CRISPR 重复挖掘 |
| PHASTER (web) | 活跃备选 | replaces PHAST | shared | 交互式前噬菌体网页注释 |
| VirSorter 1 | 经典旧代（仍可运行） | -> VirSorter2 | shared | 一代病毒序列分类器 |
| PHAST | 经典旧代（仍可运行） | -> PHASTER | shared | 旧版前噬菌体网页服务 |
| CRT / PILER-CR | 经典旧代（仍可运行） | -> CRISPRCasFinder/MinCED | shared | 早期 CRISPR 重复发现工具 |

## 16. 泛基因组

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| Panaroo | 推荐默认 | addresses Roary fragmentation | shared | 纠错型图泛基因组，适合草稿组装 |
| PPanGGOLiN | 活跃备选 | - | shared | 核心/外壳/云基因组划分 |
| PEPPAN / ggCaller | 活跃备选 | - | shared | 抗片段化与图基因调用泛基因组 |
| PIRATE / panX | 活跃备选 | - | shared | 泛基因组聚类与交互探索 |
| Roary | 活跃备选 | still a fast baseline | shared | 快速经典泛基因组流程 |
| GET_HOMOLOGUES | 活跃备选 | - | shared | 多算法直系同源聚类 |
| OrthoFinder / SonicParanoid | 活跃备选 | - | shared | 直系同源群推断 |
| anvi'o pangenome | 活跃备选 | - | shared | 交互式泛基因组平台 |
| Panstripe | 活跃备选 | companion to Panaroo | shared | 基因获得/丢失速率比较 |
| PGAP (pangenome) / BPGA | 经典旧代（仍可运行） | -> Panaroo/PPanGGOLiN | shared | 旧版泛基因组流程 |
| OrthoMCL | 经典旧代（仍可运行） | -> OrthoFinder/PPanGGOLiN | shared | 早期 MCL 直系同源聚类 |

## 17. reads 比对

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| BWA-MEM (BWA 0.7.x) | 推荐默认 | - | short | 标准短读比对器 |
| minimap2 | 推荐默认 | replaces BWA-SW/minimap/BLASR in role | long/short | 长读/噪声读快速比对 |
| samtools | 推荐默认 | - | shared | 排序索引与 BAM 处理 |
| BWA-MEM2 | 活跃备选 | - | short | SIMD 加速、结果等价 |
| Bowtie2 | 活跃备选 | - | short | 快速带空隙短读比对 |
| pbmm2 / ngmlr | 活跃备选 | - | PacBio/long | PacBio 封装与面向 SV 比对 |
| Novoalign | 活跃备选 | - | short | 高精度商业比对器 |
| NextGenMap | 活跃备选 | - | short | 灵活短读比对 |
| Bowtie 1 | 经典旧代（仍可运行） | -> Bowtie2 | short | 一代无空隙比对器 |
| SMALT / Stampy | 经典旧代（仍可运行） | -> BWA-MEM/minimap2 | short | 旧版高敏混合比对器 |
| BLASR / GraphMap | 经典旧代（仍可运行） | -> minimap2/pbmm2 | long | 早期长读比对器 |

## 18. 变异/核心SNP/重组

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| bcftools (mpileup/call) | 推荐默认 | - | shared | 变异检测、过滤与 VCF 处理 |
| Snippy (+snippy-core) | 推荐默认 | - | short/assembly | 快速核心 SNP 流程 |
| snp-sites | 推荐默认 | - | shared | 从多 FASTA 比对提取 SNP |
| Gubbins | 推荐默认 | - | shared | 检测并屏蔽重组区 |
| vcf2phylip | 推荐默认 | - | shared | 过滤 VCF 转比对矩阵 |
| FreeBayes | 活跃备选 | - | short | 单倍型感知贝叶斯检测 |
| GATK (HaplotypeCaller) | 活跃备选 | - | short | 广泛使用的变异检测 |
| ClonalFrameML | 活跃备选 | - | shared | 克隆谱系与重组估计 |
| Parsnp (Harvest) | 活跃备选 | - | shared | 快速核心基因组比对/SNP |
| kSNP3 / kSNP4 | 活跃备选 | - | shared | 无参考 SNP 发现 |
| VarScan2 | 经典旧代（仍可运行） | -> bcftools/GATK | short | 旧版基于 pileup 的检测 |
| Lyve-SET / CFSAN-SNP / NASP / RedDog | 经典旧代（仍可运行） | -> Snippy/Parsnp | short | 旧疫情核心 SNP 流程 |

## 19. 序列比对

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| MAFFT | 推荐默认 | - | shared | 快速准确多序列比对 |
| MUMmer4 (nucmer/dnadiff) | 推荐默认 | - | shared | 全基因组两两比对与 SNP |
| MUSCLE (v5) | 活跃备选 | - | shared | 高精度多序列比对（v5 重写） |
| Clustal Omega | 活跃备选 | - | shared | 渐进式多序列比对 |
| LAST | 活跃备选 | - | shared | 高敏大规模比对 |
| progressiveMauve / Mauve | 活跃备选 | maintenance limited | shared | 全基因组比对与共线性查看 |
| T-Coffee | 活跃备选 | - | shared | 高精度但较慢 |
| ClustalW | 经典旧代（仍可运行） | -> MAFFT/Clustal Omega | shared | 经典早期渐进比对 |

## 20. 距离/ANI/去冗余

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| FastANI | 推荐默认 | - | shared | 快速全基因组 ANI；模块 04.5 物种确认门控 |
| Mash | 推荐默认 | - | shared | MinHash 基因组距离 |
| snp-dists | 推荐默认 | - | shared | 两两 SNP 距离矩阵 |
| dRep | 推荐默认 | - | shared | 基因组去冗余与代表挑选 |
| skani | 活跃备选 | - | shared | 草稿基因组敏感快速 ANI |
| pyani (ANIm/ANIb) | 活跃备选 | - | shared | ANI 计算与作图 |
| CD-HIT | 活跃备选 | - | shared | 蛋白/序列聚类 |
| JSpeciesWS / OrthoANI | 经典旧代（仍可运行） | -> FastANI/skani | shared | 旧版/在线 ANI 计算 |

## 21. 系统发育树

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| IQ-TREE 3 (iqtree3/2/1) | 推荐默认 | major versions iqtree -> iqtree2 -> iqtree3 | shared | 极大似然建树，含选模与超快自展 |
| RAxML-NG | 活跃备选 | replaces RAxML 8 | shared | 新一代极大似然建树 |
| FastTree 2 | 活跃备选 | - | shared | 快速近似 ML，适合大树 |
| PhyML | 活跃备选 | - | shared | 极大似然建树与选模 |
| MEGA (11) | 活跃备选 | - | shared | 图形界面建树比对 |
| MrBayes | 活跃备选 | - | shared | 贝叶斯系统发育推断 |
| RAxML 8 | 经典旧代（仍可运行） | -> RAxML-NG | shared | 上一代 ML 建树 |

## 22. 分子定年

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| TreeTime | 推荐默认 | - | shared | 快速分子钟定年与祖先重建 |
| BactDating | 活跃备选 | - | shared | 细菌 ML/贝叶斯祖先定年 |
| BEAST 2 | 活跃备选 | - | shared | 完整贝叶斯系统动力学，较重 |
| LSD / LSD2 | 活跃备选 | - | shared | 最小二乘末端定年 |
| TempEst | 活跃备选 | - | shared | 分子钟信号检查 |
| BEAST 1 | 经典旧代（仍可运行） | -> BEAST 2 / TreeTime | shared | 一代贝叶斯定年平台 |

## 23. 微生物 GWAS 与后分析

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| Scoary | 推荐默认 | - | shared | 基因存在缺失泛基因组关联 |
| pyseer | 推荐默认 | Python reimplementation/extension of SEER | shared | 混合模型 k-mer/SNP/基因 GWAS |
| PLINK 1.9 | 推荐默认 | PLINK 2 available | shared | SNP GWAS、IBS/MDS 协变量 |
| DBGWAS | 活跃备选 | - | short | unitig/图 k-mer 细菌 GWAS |
| treeWAS / hogwash | 活跃备选 | - | shared | 系统发育感知关联检验 |
| bugwas | 活跃备选 | - | shared | 谱系效应细菌 GWAS |
| PLINK 2 | 活跃备选 | replaces PLINK 1.9 in role | shared | 重写的可扩展 GWAS 引擎 |
| GEMMA / FaST-LMM | 活跃备选 | - | shared | 线性混合模型引擎 |
| fsm-lite / dsk / panfeed | 活跃备选 | - | shared | 为 pyseer 统计信息 k-mer |
| SEER | 经典旧代（仍可运行） | -> pyseer | shared | 初代 C++ 序列元件 GWAS |

## 24. 可视化

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| ggtree / treeio (R) | 推荐默认 | - | shared | 编程式系统树注释图层 |
| iTOL | 推荐默认 | - | shared | 在线系统树注释与数据图层 |
| GrapeTree | 推荐默认 | - | shared | cgMLST/SNP 最小生成树 |
| ComplexHeatmap (R) | 推荐默认 | - | shared | 矩阵注释热图 |
| Microreact | 活跃备选 | - | shared | 在线地图/时间/系统树 |
| Phandango | 活跃备选 | - | shared | 交互树+泛基因组/元数据 |
| Nextstrain / Auspice | 活跃备选 | - | shared | 系统动力学交互可视化 |
| Dendroscope | 活跃备选 | - | shared | 大系统树桌面查看 |
| FigTree | 经典旧代（仍可运行） | -> iTOL/ggtree | shared | 旧桌面系统树查看，维护少 |

## 25. 流程引擎与报告

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| MultiQC | 推荐默认 | - | shared | 跨样本汇总质控报告 |
| Snakemake | 活跃备选 | - | shared | 可复现流程语言 |
| Nextflow | 活跃备选 | - | shared | 可移植容器化流程语言 |
| Conda / Mamba (Bioconda) | 推荐默认 | - | shared | 包与环境管理 |
| GNU parallel | 活跃备选 | - | shared | 简单的多样本并行 |

## 26. 跨域覆盖度与完整度

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| mosdepth | 推荐默认 | - | shared | 面向映射、病毒与真菌的快速覆盖度统计 |
| CheckV | 推荐默认 | - | viral | 病毒基因组完整度与宿主/前病毒污染 |
| vClean | 活跃备选 | - | viral | MIUViG 标准下病毒基因组污染与质量评估 |

## 27. 病毒共识、谱系与注释

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| nf-core/viralrecon | 推荐默认 | - | viral | 病毒 WGS 参考流程（二代/三代，域模板） |
| iVar | 推荐默认 | - | viral | 扩增子引物修剪、变异与共识检测 |
| artic (fieldbioinformatics) | 推荐默认 | - | viral | ONT 平铺扩增子共识流程 |
| ViralConsensus | 推荐默认 | - | viral | 从 BAM 快速生成共识序列 |
| ViralMSA | 活跃备选 | - | viral | 参考引导的病毒多序列比对 |
| Nextclade / Nextalign | 推荐默认 | - | viral | 分支判定、突变检测与序列质控 |
| Pangolin | 推荐默认 | - | viral | 新冠病毒谱系判定 |
| UShER / matUtils | 活跃备选 | - | viral | 突变注释树上的超快样本放置 |
| augur (Nextstrain) | 活跃备选 | - | viral | 面向 Auspice 的系统动力学流程构建 |
| Freyja | 活跃备选 | - | viral | 污水与混合样本的谱系去卷积 |
| VADR | 推荐默认 | - | viral | GenBank 级病毒注释与提交质控 |
| VAPiD | 活跃备选 | - | viral | 轻量病毒基因组注释与鉴定 |
| VIGOR | 活跃备选 | - | viral | 病毒基因与蛋白注释 |
| SnpEff / SnpSift | 活跃备选 | - | shared | 小基因组或自定义库的变异效应注释 |

## 28. 宿主体内多样性、HIV 与传播

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| HAPHPIPE | 推荐默认 | - | viral | HIV 单倍型重组与系统动力学流程 |
| V-pipe | 推荐默认 | - | viral | 宿主体内多样性与准种的 Snakemake 流程 |
| shiver | 活跃备选 | - | viral | HIV/HCV/RSV 去宿主、de novo 组装与共识 |
| HIV-TRACE / tn93 | 推荐默认 | - | viral | TN93 两两距离与传播簇识别 |
| HyPhy | 推荐默认 | - | viral | 选择压力与重组分析 |
| CliqueSNV | 活跃备选 | - | viral | 基于连锁 SNV 重组宿主体内单倍型 |
| Stanford HIVdb / HyDRA | 活跃备选 | - | viral/web | 在线 HIV 耐药突变评分 |
| Phyloscanner | 活跃备选 | - | viral | 宿主体内/间污染剔除与传播推断 |
| PredictHaplo | 经典旧代（仍可运行） | -> CliqueSNV/V-pipe | viral | 旧版准种单倍型重组 |

## 29. 真菌组装、质检与注释

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| AAFTF | 推荐默认 | - | fungal | 单倍体真菌组装、载体过滤与打磨 |
| FGMP | 活跃备选 | - | fungal | 基于编码与非编码标记的真菌完整度评估 |
| funannotate | 推荐默认 | - | fungal | 真菌基因组注释、比较与提交准备 |
| BRAKER3 | 推荐默认 | - | fungal | 基于 GeneMark-ETP/AUGUSTUS/miniprot 的真核基因预测 |
| MAKER / MAKER2 | 活跃备选 | - | fungal | 经典证据驱动的真核注释流程 |
| FunGAP | 活跃备选 | - | fungal | 基于证据模型评分的真菌基因注释 |
| ITSx | 推荐默认 | - | fungal | 提取 ITS1/5.8S/ITS2 条形码区（配 UNITE） |

## 30. 真菌比较基因组、拷贝数与代谢

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| nPhase | 活跃备选 | - | fungal | 不依赖倍性的长读单倍型定相 |
| Control-FREEC | 活跃备选 | - | fungal | 从比对读段检测拷贝数变异与非整倍体 |
| antiSMASH (fungal mode) | 推荐默认 | - | shared | 次级代谢生物合成基因簇（细菌与真菌） |
| run_dbcan | 推荐默认 | - | shared | 碳水活性酶与 CAZyme 基因簇注释 |
| SMURF | 活跃备选 | - | fungal/web | 在线真菌次级代谢基因簇预测 |

## 31. 益生菌安全与有益评价

| 工具 | 状态 | 替代/继任关系 | 平台 | 作用 |
| --- | --- | --- | --- | --- |
| EFSA QPS / FEEDAP guidance | 推荐默认 | - | shared/web | 法规框架：分类身份、获得性耐药、毒力、产毒 |
| Probio / ProbioMinServer | 活跃备选 | - | shared/web | 益生菌安全与功能在线评价平台 |
| BAGEL4 | 活跃备选 | - | shared/web | 在线细菌素与 RiPP 挖掘 |

## 选择原则

新项目优先使用“推荐默认”，以减少维护和兼容性成本；需要复现某篇文献或某个历史流程时，应沿用其原始工具与版本，而不是直接替换，以免引入难以追溯的结果差异。遇到高度片段化的二代草稿组装，泛基因组优先考虑 Panaroo、PPanGGOLiN 等对片段化更稳健的工具，Roary 适合作为快速基线；组装完整度与污染评估可用 CheckM2 为主，并保留 CheckM 结果以便与历史数据对比。长读数据通常先以 Racon 做有限轮次自纠错，再用 Medaka 做一致性打磨，混合数据再以短读工具收尾，顺序上避免把精度更低的工具放在最后。比对、变异检测和建树的选择，则取决于是否已有可靠参考基因组以及样本规模，这与“组装路线与比对路线并行”的总体设计一致。

机读主数据维护在 `reference/tool_catalog.tsv`，新增或修订工具后，可运行 `python reference/render_alternative_tools.py` 重新生成本页与英文页面。
