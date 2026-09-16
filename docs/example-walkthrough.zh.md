# 实战示例：多病原公共数据面板

本章用真实、公开的细菌分离株数据跑通整个 EasyWGS 流程，使配套论文 Application
部分的每一项结果都能用少量命令复现。面板刻意做到小而全：覆盖五大类常见病原，而
不是只针对单一物种；既包含二代样本，也包含 Illumina 与 Oxford Nanopore 严格配对
的 hybrid 样本；另外加入一个含 12 株沙门菌、跨年份的时间序列集合，用于演示单基
因组无法完成的集合级分析（泛基因组、核心 SNP 系统发育、时间树、基因型与表型关联）。

仓库中不存储任何测序读段。[`examples/panel.tsv`](https://github.com/LLQ95/EasyWGS/blob/main/examples/panel.tsv)
中的所有 accession 均已通过 ENA Portal 与 NCBI 核实，读段按需下载后再下采样，因此
本教程可在普通分析服务器上运行。

## 面板设计

| 病原类群 | `species` 代码 | Tier-1 二代 | Hybrid 配对 | Tier-2 二代 | Tier-3 扩展 |
| --- | --- | --- | --- | --- | --- |
| *Salmonella enterica*（沙门菌） | `salm` | SE_IT_2011_1 | SE_HY_JP_2010 | 3 | 12 株 1992-2017 时间序列（意大利、日本） |
| *Klebsiella pneumoniae*（肺克） | `kpsc` | KP_GR_2011 | KP_HY_JP_2015 | 3 | - |
| *Escherichia coli*（大肠埃希菌） | `ecoli` | EC_BE_2015 | EC_HY_JP_2015 | 3（含 O26） | - |
| *Listeria monocytogenes*（单增李斯特菌） | `listeria` | LM_AT_2013 | LM_HY_DE_2019 | 3 | - |
| *Shigella*（志贺菌属） | `ecoli` | SS_FR_2010（宋内志贺菌） | SD_HY_HU_1954（痢疾志贺菌） | 3（宋内、福氏） | - |

三个 tier 是同一面板的嵌套子集。

- Tier 1 含 10 个样本，每类病原 1 株二代与 1 株 hybrid，速度最快，可跑通每个单菌
  模块以及两条分析路线。
- Tier 2 含 20 个样本，每类病原 3 株二代，能在五类病原上展示更真实的血清型、MLST
  与耐药结果广度。
- Tier 3 含 29 个样本。其中 13 个沙门菌基因组（12 株跨 1992 至 2017 年的二代样本加
  1 株 hybrid）用于驱动泛基因组、核心 SNP、TreeTime 分子钟与祖先地重建，以及 GWAS
  演示。

`panel.tsv` 的每一行记录 Illumina 与 ONT 的 run accession、用于证明 hybrid 配对来自
同一分离株的 BioSample、国家、采集日期、学名，以及经 accession 核实的 RefSeq 完成
图参考。

## 前置准备

按[安装](installation.md)一章，先创建软件环境并一次性下载数据库。

```bash
bash 00_install/install_env.sh
DBROOT=$HOME/easywgs_db bash 00_install/download_db.sh
```

本面板需要 CheckM2、GUNC 与 Bakta 数据库。Kraken 2 标准库与 FCS-GX 在本示例中为可
选项，模块 02 在缺少它们时仍可运行，只是跳过物种组成侦察。spike-in 实验使用
`art_illumina`（Bioconda 包名为 `art`）与 `bwa`，二者均已包含在 `easywgs` 环境中。
若集群上已有相关数据库，可在运行 `download_db.sh` 前按需导出 `CHECKM2_DB`、
`BAKTA_DB`、`EGGNOG_DB`、`GUNC_DB` 以跳过下载，模块 04、05 与 spike-in 会直接使用这些
共享库（各变量应指向的路径见[安装](installation.md)一章）；该章也给出了断点续传方式。

## 运行面板

```bash
# 1. 生成各 tier 配置，下载读段与参考，并对 Illumina 数据下采样
EXAMPLE_PAIRS=800000 bash examples/00_download_panel.sh 1

# 2. 端到端运行质控、去污染、组装、质量门控、注释、分型、耐药、泛基因组、
#    系统发育、定年、GWAS 与结果汇总
bash examples/01_run_panel.sh 1

# 3. 运行受控的双层去污染验证（论文图 4）
bash examples/02_run_spikein.sh
```

把命令末尾的 `1` 换成 `2` 或 `3` 即可运行更大的 tier。`EXAMPLE_PAIRS` 设置每个
Illumina 样本保留的配对读段数（默认 800,000 对，对 5 Mb 基因组、150 bp 读长约为 50
倍）；如需满深度组装可调高。ONT 读段全部保留，因为模块 01b 会用 Filtlong 按目标碱
基数过滤。下载过程可断点续跑，已完成的文件会自动跳过。

如果某个 ENA run 在你所在地区没有直接的 FASTQ 镜像，可对该 accession 改用 SRA
toolkit：

```bash
fasterq-dump --threads 8 --outdir 00_rawdata <RUN_ACCESSION>
gzip 00_rawdata/<RUN_ACCESSION>_*.fastq
# 然后重命名为 00_rawdata/<id>_R1.fastq.gz 与 00_rawdata/<id>_R2.fastq.gz
```

## 输出与预期结果检查

- `99_report/master_table.tsv` 由 `99_report/merge_results.py` 汇总每个分离株的组装、
  MLST、血清型、CheckM2 与耐药结果。
- `examples/results/panel_metrics.tsv` 把面板元数据与关键单菌指标连接起来；
  `collection_stats.tsv` 与 `panel_summary.md` 给出集合级数字，如泛基因组核心与独有
  基因簇数、核心 SNP 比对长度、成对 SNP 范围、分子钟回归直线与 GWAS 命中。
- `examples/results/expected_check.tsv` 依据
  `examples/expected/expected_results.tsv` 报告 PASS、WARN 或 FAIL。WARN 表示某模块
  尚未运行，FAIL 表示实测值落在预期区间之外。

指标汇总脚本对任何尚未运行的模块写入 NA，而不会估算数值，因此论文与指南中的数字应
在真实运行后引用这些文件，而非使用占位数字。

## 去污染 spike-in 实验

目标样本是 tier-1 的大肠埃希菌 EC_BE_2015。按目标读段数的 1%、5%、10% 分别掺入两类
污染：PhiX（NC_001422），其读段用 ART 模拟，以还原 Illumina 技术对照；以及肺克
KP_GR_2011 的真实读段，作为更难去除的近缘来源污染。对每种混合，流程分别报告在透明
的 bwa/samtools 比对并过滤去除前后，比对到目标与污染的读段比例，并给出基线、掺入
10% 与清洗后 10% 三种文库的组装大小、N50 与 CheckM2 评分。该比对过滤步骤是便于审计
的基准；生产环境的去污染在模块 02 使用 CLEAN、在组装层面使用 FCS-GX，它们以持续维
护的数据库实现相同的参考与 k-mer 原理。四面板图输出到
`examples/spikein/results/Fig_spikein.{png,pdf,svg}`。

## Tier 3 的集合级分析

12 株二代沙门菌来自同一研究（PRJDB6430），跨 1992 至 2017 年、来自日本与意大利，因
此具有真实的时间与国家结构。模块 08 构建泛基因组，模块 09 调用核心 SNP 并构建系统
发育，模块 10 用 TreeTime 估计分子钟与祖先地理位置，模块 13 运行 Scoary、PLINK 与
pyseer。ENA 中只有年份的日期在 `metadata_dates.csv` 中按年中处理，并在
`date_precision` 列中标注。

可直接使用的二元性状是“是否来自意大利”，这是一个真实、可复现的元数据字段，可为关
联分析提供两个类别，但它不是实测表型。模块 07 之后，
`scripts/derive_mdr_traits.py` 会添加 `MDR_genotypic`，当获得性耐药基因跨越至少三个
不同的 AMRFinderPlus 药物类别时记为 1；随后可用 `TRAIT=MDR_genotypic` 重跑模块
13。在真实研究中，应在 `config/traits.csv` 中用实测药敏结果替换这两个性状。

## 使用你自己的分离株

把读段放入 `00_rawdata/`，命名为 `<id>_R1.fastq.gz`、`<id>_R2.fastq.gz`，hybrid 或
长读段再加 `<id>_ONT.fastq.gz`，然后按[输入与样本表](samplesheet.md)的列说明编辑
`config/my_samples.csv`。构建泛基因组与关联检验时，每次集合级运行应保持同一物种。

## 数据来源

| 类群 | 来源研究 |
| --- | --- |
| 沙门菌时间序列与 hybrid | PRJDB6430 / DRP004007（DDBJ/ENA） |
| 肺克 | PRJDB4948 / DRP004119 |
| 大肠埃希菌 | PRJDB5579、PRJDB5136、PRJDB3552 / DRP004119 |
| 单增李斯特菌 | PRJEB56155 / ERP150987 |
| 志贺菌属 | PRJEB12097、PRJEB71076、PRJEB73590 / SRP292271 |

参考基因组与 PhiX 对照的 RefSeq、GenBank accession 列于
[`examples/panel.tsv`](https://github.com/LLQ95/EasyWGS/blob/main/examples/panel.tsv)。
除 EasyWGS 外，请同时引用原始研究与 ENA/SRA accession。包含每个输出文件的完整逐步
说明维护在
[`examples/README.md`](https://github.com/LLQ95/EasyWGS/blob/main/examples/README.md)。
