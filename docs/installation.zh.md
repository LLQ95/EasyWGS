# 安装

流程在 Linux、WSL2 与 HPC 上运行，依赖通过 conda（推荐 mamba）管理。为避免
数据库与重依赖互相冲突，安装脚本按用途拆成多个独立环境。

## 1. 准备 conda

若还没有 conda，先安装 Miniforge 或 Miniconda，之后建议把 `conda` 替换为更快的
`mamba`。配置 bioconda 与 conda-forge 频道：

```bash
conda config --add channels conda-forge
conda config --add channels bioconda
```

## 2. 创建环境

```bash
bash 00_install/install_env.sh
```

脚本会创建这些环境：

| 环境 | 用途 |
| --- | --- |
| easywgs | 主环境，含质控、二/三代组装、分型、比较、系统发育工具 |
| longread | Medaka 抛光与 Trycycler 多组装一致（依赖较重，单独隔离） |
| checkm2 | 组装完整度与污染评估 |
| gunc | 组装嵌合检测 |
| bakta | 基因组注释（数据库大） |
| eggnog | GO/KEGG/COG 功能注释 |

CLEAN 是 Nextflow 流程，主环境装好 nextflow 后由脚本执行 `nextflow pull rki-mf1/clean`，
不需要单独建环境。

安装脚本是幂等的：重复运行会跳过已经存在的环境，只创建缺失的环境，适合安装中断后
补齐。主环境名默认为 `easywgs`，可用 `EASYWGS_ENV` 覆盖；每个模块激活的都是
`${EASYWGS_ENV:-easywgs}`，因此如果工作站把主要工具装在另一个环境里，可让流程直接
使用它（例如 `EASYWGS_ENV=isolateqc bash 00_install/install_env.sh`）。

## 3. 下载数据库或指向已有共享库

数据库只需下载一次，可在多个项目间共享。运行前建议把 `DBROOT` 指向大容量、最好是
共享的磁盘（默认为 `~/easywgs_db`）：

```bash
DBROOT=/data/shared/easywgs_db bash 00_install/download_db.sh
```

下载内容包括 abricate 各库、AMRFinder 库、CheckM2 模型、GUNC 参考集、Bakta 与
eggNOG 库、chewBBACA schema。脚本可重复运行，已完成的项目会自动跳过。

### 复用已有的共享数据库

每个大型数据库都可以通过环境变量指向已有的共享副本，下载脚本会自动跳过，对应模块
也会直接使用该副本。仍需下载的内容则放到 `DBROOT` 指定的共享根目录：

| 变量 | 指向 | 使用模块 |
| --- | --- | --- |
| `CHECKM2_DB` | `uniref100.KO.1.dmnd` 文件或其 `CheckM2_database` 目录 | 模块 04、spike-in |
| `BAKTA_DB` | 含 `version.json` 的 Bakta 目录（或其父目录） | 模块 05 |
| `EGGNOG_DB` | 含 `eggnog.db` 的 eggNOG 目录 | 模块 05 |
| `GUNC_DB` | `gunc_db.dmnd` 文件或包含它的目录 | 模块 04 |

例如，集群上已在 `/db/student/metagenome` 下备好 CheckM2、Bakta 与 eggNOG，并希望把
GUNC 也下载到同一区域：

```bash
export DBROOT=/db/student/metagenome
export CHECKM2_DB=/db/student/metagenome/checkm_db/checkm2_database/CheckM2_database/uniref100.KO.1.dmnd
export BAKTA_DB=/db/student/metagenome/bakta_db/db
export EGGNOG_DB=/db/student/metagenome/eggnog_db
# GUNC_DB 不设置，下载脚本会把 GUNC 下载到 $DBROOT/gunc_db
bash 00_install/download_db.sh
```

下载脚本对找到的数据库会打印 `[skip]`，只下载缺失的部分（本例为 GUNC 以及较小的
AMRFinder、CARD、abricate 数据）。建议把这些 `export` 写入 `~/.bashrc`，或在每次运行前
导出，模块 04、05 即会自动使用。运行时若某个数据库确实缺失，对应模块会给出明确警告并
把相关结果记为 NA，而不是让整个流程中断。

CheckM2 数据库约 1.7 GB，Zenodo 的一次性下载在网络不稳时容易中断；没有共享副本时，可
用下一小节的断点续传方式下载。

### 没有共享库时使用断点续传下载

下载脚本改用 `wget -c` 拉取 CheckM2，中断后重复运行同一命令即可续传；随后自动解压并
通过 `checkm2 database --setdblocation` 注册路径。也可以手动完成：

```bash
conda activate checkm2
wget -c -O checkm2_database.tar.gz \
  https://zenodo.org/api/records/14897628/files/checkm2_database.tar.gz/content
tar -xzf checkm2_database.tar.gz
checkm2 database --setdblocation "$PWD/CheckM2_database"
```

其他大型数据库同理：把 `DBROOT` 指向共享位置，只补缺失的部分；也可以在网络更好的
机器上下载 GUNC、Bakta、eggNOG 后，把目录拷贝到 `DBROOT`。

### 自定义毒素与表面位点数据库（模块 06.4）

tier 4 与 tier 5 的 14 类专化病原使用一个名为 `easywgs_markers` 的小型 abricate 数据库，覆盖表面抗原、
毒素、毒力、耐药与质粒位点。其序列不自动下载，需依据 `examples/customdb/easywgs_markers.tsv`
中的 curated 清单（给出基因符号与权威来源）一次性构建：把获取到的序列拼接成一个
多 FASTA 文件，文件头以 `marker_id` 开头，然后运行：

```bash
MARKER_FASTA=/path/to/easywgs_markers.fa bash 00_install/build_custom_db.sh
```

模块 04.5 用于物种确认的 FastANI 已随主环境自动安装，无需单独数据库；自定义库缺失
时模块 06.4 会写出空表并继续。

## 4. 硬件与可选组件

常规几百个分离株的二代分析，16 线程、64 GB 内存即可。组装 Flye、运行 CheckM2 时
内存占用上升，建议 128 GB。需要本地运行 NCBI FCS-GX 时要注意其参考库约 470 GB、
官方建议 512 GB 内存；不具备条件时保留 CheckM2 与 GUNC 门控，把组装上传
usegalaxy.org 在线运行 FCS-GX 即可，流程已预留这一路径。

少数分病原专用的分型工具为可选项，不进入核心环境：金葡可用 spaTyper 与 SCCmecFinder
（开源替代为 staphopia-sccmec），蜡样群可用 BTyper3，结核可用 TB-Profiler、Mykrobe、
fast-lineage-caller 或 MTBseq。仅在处理相应病原时安装；模块 06 在缺少它们时记为 NA，
指南保证流程在不安装这些工具时仍可运行。

## 5. 验证安装

```bash
conda activate easywgs
fastp --version; unicycler --version; flye --version; mlst --version; fastANI --version
conda activate checkm2 && checkm2 --version
```

逐个返回版本号即说明主链路可用。工具的具体版本不需要与教程完全一致，但三代抛光
链（Medaka、Racon）与组装器建议记录在项目日志里，方便结果复现。
