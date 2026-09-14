# 软件版本与时效性

EasyWGS 不把工具锁死在单一版本：安装脚本从 Bioconda 解析当前构建，分析脚本只调用稳定的命令接口，因此新版本一般无需改动即可使用。下表登记流程所用全部外部工具的当前上游版本，核验日期为 2026-09-14，依据各项目官方 GitHub 仓库的最新 release 或最新版本标签。R 包通过 CRAN 或 Bioconductor 发布，没有 GitHub release 标签；在线工具不存在本地版本。

可用本页审查已有安装环境。复现核查的方法是对仓库执行 `git ls-remote --tags <repo>` 列出全部标签，或打开 README 工具表中的 releases 页面。

## 读段处理与质控

| 工具 | 当前版本 | 上游仓库 |
|---|---|---|
| fastp | 1.3.7 | OpenGene/fastp |
| FastQC | 0.12.1 | s-andrews/FastQC |
| MultiQC | 1.35 | MultiQC/MultiQC |
| SeqKit | 2.13.0 | shenwei356/seqkit |
| chopper | 0.14.1 | wdecoster/chopper |
| NanoPlot | 1.48.0 | wdecoster/NanoPlot |
| Porechop | 0.2.4 | rrwick/Porechop（原始仓库，另有社区分支） |
| Filtlong | 0.3.1 | rrwick/Filtlong |

## 去污染与组装评估

| 工具 | 当前版本 | 上游仓库 |
|---|---|---|
| Kraken2 | 2.17.1 | DerrickWood/kraken2 |
| Bracken | 3.1 | jenniferlu717/Bracken |
| CLEAN | 1.2.0 | rki-mf1/clean |
| BBMap | 36.20（GitHub 标签；更新构建见 SourceForge） | BioInfoTools/BBMap |
| NCBI FCS-GX | 0.5.5 | ncbi/fcs |
| CheckM2 | 1.1.0 | chklovski/CheckM2 |
| GUNC | 1.1.1 | grp-bork/gunc |
| BlobToolKit | 4.5.5 | genomehubs/blobtoolkit |
| Mash | 2.3 | marbl/Mash |
| QUAST | 5.3.0 | ablab/quast |

## 组装与打磨

| 工具 | 当前版本 | 上游仓库 |
|---|---|---|
| SPAdes | 4.3.0 | ablab/spades |
| Unicycler | 0.5.1 | rrwick/Unicycler |
| Flye | 2.9.6 | mikolmogorov/Flye |
| Canu | 2.3 | marbl/canu |
| Dragonflye | 1.2.1 | rpetit3/dragonflye |
| Trycycler | 0.5.6 | rrwick/Trycycler |
| minimap2 | 2.31 (r1302) | lh3/minimap2 |
| Racon | 1.5.0 | lbcb-sci/racon |
| Medaka | 2.2.2 | nanoporetech/medaka |
| Pilon | 1.24 | broadinstitute/pilon |
| Circlator | 1.5.5 | sanger-pathogens/circlator |
| MUMmer | 4.0.1 | mummer4/mummer |
| cd-hit | 4.8.1 | weizhongli/cdhit |

## 注释

| 工具 | 当前版本 | 上游仓库 |
|---|---|---|
| Prokka | 1.15.6 | tseemann/prokka |
| Bakta | 1.12.1 | oschwengers/bakta |
| Prodigal | 2.60 | hyattpd/Prodigal |
| eggNOG-mapper | 2.1.15 | jhcepas/eggnog-mapper |

## 分型（MLST、血清型、cgMLST）

| 工具 | 当前版本 | 上游仓库 |
|---|---|---|
| mlst | 2.35.0 | tseemann/mlst |
| Kleborate | 3.2.4 | klebgenomics/Kleborate |
| ECTyper | 2.0.0 | phac-nml/ecoli_serotyping |
| ShigEiFinder | 1.3.5 | LanLab/ShigEiFinder |
| SeqSero2 | 1.3.2 | denglab/SeqSero2 |
| SISTR | 1.1.3 | phac-nml/sistr_cmd |
| chewBBACA | 3.5.4 | B-UMMI/chewBBACA |

## 耐药、毒力与可移动遗传元件

| 工具 | 当前版本 | 上游仓库 |
|---|---|---|
| abricate | 1.4.0 | tseemann/abricate |
| AMRFinderPlus | 4.2.7 | ncbi/amr |
| RGI (CARD) | 6.0.8 | arpcard/rgi |
| MOB-suite | 3.1.9 | phac-nml/mob-suite |
| PlasFlow | 1.1 | smaegol/PlasFlow |
| mobileOG-db | beatrix 1.0（数据库） | clb21565/mobileOG-db |
| MGEfinder | 1.0.6 | bhattlab/MGEfinder |
| IntegronFinder | 2.0.6 | gem-pasteur/Integron_Finder |
| geNomad | 1.12.0 | apcamargo/genomad |
| IslandPath-DIMOB | 1.0.6 | brinkmanlab/islandpath |
| PhiSpy | 5.0.10 | linsalrob/PhiSpy |
| VirSorter2 | 2.2.3（Bioconda；GitHub 标签为 2.0.alpha） | simroux/VirSorter2 |

## 参考比对与变异检测（模块 12）

| 工具 | 现行版本 | 上游 |
|---|---|---|
| BWA | 0.7.19 | lh3/bwa |
| samtools | 1.24 | samtools/samtools |
| bcftools | 1.24 | samtools/bcftools |
| htslib（tabix/bgzip） | 1.24（随 samtools 发布） | samtools/htslib |
| Qualimap | 2.3（Bioconda；无 GitHub release 标签） | kokonech/QualiMap |
| vcf2phylip | 2.8 | edgardomortiz/vcf2phylip |

## 微生物 GWAS 与 post-GWAS（模块 13）

| 工具 | 现行版本 | 上游 |
|---|---|---|
| Scoary | 1.6.9 | AdmiralenOla/Scoary |
| PLINK | 1.9（plink-ng；PLINK 2.0 仍为 alpha 线） | chrchang/plink-ng |
| pyseer | 1.4.2 | mgalardini/pyseer |

## 泛基因组、系统发育与分子钟

| 工具 | 当前版本 | 上游仓库 |
|---|---|---|
| Panaroo | 1.8.0 | gtonkinhill/panaroo |
| Roary | 3.13.0 | sanger-pathogens/Roary |
| snippy | 4.6.0 | tseemann/snippy |
| Gubbins | 3.4.3 | nickjcroucher/gubbins |
| snp-sites | 2.3.3 | tseemann/snp-sites |
| snp-dists | 1.2.0 | tseemann/snp-dists |
| IQ-TREE 3 | 3.1.4 | iqtree/iqtree3 |
| IQ-TREE 2（旧版分支） | 2.4.0 | iqtree/iqtree2 |
| TreeTime | 0.12.1 | neherlab/treetime |
| MAFFT | 7 系列（项目官网） | mafft.cbrc.jp |
| FastTree | 2.1.11（项目官网） | microbenet/FastTree |

Bioconda 上的包名为 `iqtree`，当前提供 IQ-TREE 3，可执行文件为 `iqtree3`；在第 2 代时期同一包提供的是 `iqtree2`。建树脚本按 iqtree3、iqtree2、iqtree 的顺序解析可执行文件，因此仍装有第 2 代的机器无需修改即可运行。

## 工作流引擎、数据获取与可视化

| 工具 | 当前版本 | 上游仓库 |
|---|---|---|
| Nextflow | 26.04.6（稳定版） | nextflow-io/nextflow |
| NCBI datasets | 18.37.0 | ncbi/datasets |
| sra-tools | 3 系列（Bioconda；GitHub 标签按 VDB 方案命名） | ncbi/sra-tools |
| GrapeTree | 1.5.0 | achtman-lab/GrapeTree |
| FigTree | 1.4.4 | rambaut/figtree |
| Phandango | 0.5.0 | jameshadfield/phandango |
| ggtree、treeio、ggtreeExtra | 当前 Bioconductor 版本 | YuLab-SMU |
| ape、phangorn、ggplot2、pheatmap | 当前 CRAN 版本 | 对应 CRAN 页面 |
| ComplexHeatmap | 当前 Bioconductor 版本 | jokergoo/ComplexHeatmap |
| iTOL、Microreact | 在线服务，无本地版本 | itol.embl.de / microreact.org |

版本更新很快，本表会随时间过时；若本机工具早于表中所列，可通过 Bioconda 更新，并在仓库提 issue 以便刷新此表。
