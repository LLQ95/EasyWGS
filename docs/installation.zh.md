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
| easyisolate | 主环境，含质控、二/三代组装、分型、比较、系统发育工具 |
| longread | Medaka 抛光与 Trycycler 多组装一致（依赖较重，单独隔离） |
| checkm2 | 组装完整度与污染评估 |
| gunc | 组装嵌合检测 |
| bakta | 基因组注释（数据库大） |
| eggnog | GO/KEGG/COG 功能注释 |

CLEAN 是 Nextflow 流程，主环境装好 nextflow 后由脚本执行 `nextflow pull rki-mf1/clean`，
不需要单独建环境。

## 3. 下载数据库

```bash
# 先打开脚本，把 DBROOT 改成自己的数据库存放盘（建议大盘、只读共享）
bash 00_install/download_db.sh
```

数据库只需下载一次，可在多个项目间共享。主要包括 abricate 各库、AMRFinder 库、
Kraken2 库、CheckM2 模型、GUNC 参考集、Bakta 与 eggNOG 库、chewBBACA schema。

## 4. 硬件与可选组件

常规几百个分离株的二代分析，16 线程、64 GB 内存即可。组装 Flye、运行 CheckM2 时
内存占用上升，建议 128 GB。需要本地运行 NCBI FCS-GX 时要注意其参考库约 470 GB、
官方建议 512 GB 内存；不具备条件时保留 CheckM2 与 GUNC 门控，把组装上传
usegalaxy.org 在线运行 FCS-GX 即可，流程已预留这一路径。

## 5. 验证安装

```bash
conda activate easyisolate
fastp --version; unicycler --version; flye --version; mlst --version
conda activate checkm2 && checkm2 --version
```

逐个返回版本号即说明主链路可用。工具的具体版本不需要与教程完全一致，但三代抛光
链（Medaka、Racon）与组装器建议记录在项目日志里，方便结果复现。
