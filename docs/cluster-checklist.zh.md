# 真实面板集群运行清单

本清单指导在 Linux 高性能集群上对公共细菌分离株面板运行 EasyWGS，并产出支撑手稿的实测结果。它与合成的持续集成测试互为补充：后者在无数据、无数据库时验证代码可运行，本页则在真实 reads 上验证完整的组装、质控、注释、分型与系统发育路线。请按顺序执行，在预期结果门控不再出现 `FAIL` 之前不要进入下一 tier。

下文以 `/db/student/metagenome` 开头的路径来自某一台集群的示例，请替换为你所在集群共享数据库的实际位置。

## 1. 获取代码并创建环境

克隆仓库并一次性创建六个 Conda 环境。主环境名为 `easywgs`，其余环境用于隔离依赖较重或相互冲突的工具。

```bash
git clone https://github.com/LLQ95/EasyWGS.git
cd EasyWGS
bash 00_install/install_env.sh
```

如果模块报错 `EnvironmentNameNotFound: Could not find conda environment: easywgs`，说明安装未成功完成，请先重新运行安装脚本。系统在装有 mamba 时会自动使用 mamba，否则回退到 conda。libmamba 关于 Anaconda 服务条款的提示仅为告知；本流程使用 conda-forge 与 bioconda 频道。

## 2. 指向已有数据库

流程不会假设数据库位于家目录。运行模块前先 source 运行时辅助脚本并导出共享数据库位置。下面的取值复用集群上已存在的数据库，避免重复下载数 GB 的数据。

```bash
source 00_install/runtime.sh

# CheckM2 diamond 数据库（指向文件本身或其所在目录）
export CHECKM2_DB=/db/student/metagenome/checkm_db/checkm2_database/CheckM2_database/uniref100.KO.1.dmnd
# Bakta 完整数据库（含 bakta.db 与 version.json 的目录）
export BAKTA_DB=/db/student/metagenome/bakta_db/db
# eggNOG-mapper 数据目录（含 eggnog.db 的目录）
export EGGNOG_DB=/db/student/metagenome/eggnog_db
# GUNC 数据库；若不存在见下方下载步骤
export GUNC_DB=/db/student/metagenome/gunc_db/progenomes_2.1/gunc_db.dmnd
```

把已有 CheckM2 数据库注册到专用环境：

```bash
conda run -n checkm2 checkm2 database --setdblocation "$(dirname "$CHECKM2_DB")"
```

在已经具备 CheckM2、Bakta 与 eggNOG 的集群上，GUNC 的 progenomes 2.1 数据库是唯一仍需下载的大型数据库。请下载到共享区域（约 13 GB；若 `/db` 只读，可改用可写位置如 `$HOME/easywgs_db`）：

```bash
mkdir -p /db/student/metagenome/gunc_db
conda run -n gunc gunc download_db /db/student/metagenome/gunc_db
export GUNC_DB=$(find /db/student/metagenome/gunc_db -name 'gunc_db.dmnd' | head -n1)
```

如果 CheckM2 从 Zenodo 下载时因 `IncompleteRead` 中断，不要在安装器里从零重试。可以像上面那样把 `CHECKM2_DB` 指向共享副本；也可以用支持断点续传的客户端（`wget -c` 或 `curl -C -`）把压缩包下载一次，解压到 `$DBROOT/checkm2_db`，再对解压目录执行 `checkm2 database --setdblocation`。其余未共享的数据库可在修改 `DBROOT` 后运行 `bash 00_install/download_db.sh`，并注释掉不需要的部分。

## 3. 不依赖数据先验证安装

下载任何数据之前，先运行静态检查与自包含冒烟测试。静态检查只需 Python；冒烟测试使用最小环境或主环境。

```bash
python tests/run_static_checks.py

conda activate easywgs
bash tests/run_smoke.sh
SYNTHETIC=1 bash examples/02_run_spikein.sh
```

冒烟测试会创建一个临时合成项目，运行 fastp、参考比对与变异检测，并校验覆盖度与 SNP 恢复。合成 spike-in 在此处使用 `bwa` 引擎（环境中已安装），S1 至 S5 每条规则都应显示 `PASS`。

## 4. 下载公共面板

面板定义在 `examples/panel.tsv`，把菌株划分为五个 tier，从一个小而典型的集合开始，逐步扩展到完整的多物种集合。先下载 tier 1 并检查生成的样本表。

```bash
bash examples/00_download_panel.sh 1
# 生成的样本表与元数据位于 examples/generated/（被 git 忽略）
ls -lh 00_rawdata
```

reads 放在 `00_rawdata/`，该目录不纳入 git。若某个 accession 下载失败，重新运行脚本即可，下载器会跳过已存在的文件。

## 5. 真实数据迷你冒烟

在运行完整 tier 之前，先为每株抽取固定 reads 对数并运行组装路线，可在数分钟内暴露绝大多数路径与接线错误。

```bash
bash examples/scripts/downsample_panel.sh examples/generated/samplesheet_tier1.csv 200000
bash run_assembly.sh config/my_samples.mini.csv
```

迷你样本表使用 `mini_` 前缀，便于清理抽样文件。若高 GC 基因组在默认深度下组装不佳，可提高 reads 对数。

## 6. 按顺序运行各 tier

以批次方式运行每个 tier，从 tier 1 开始，只有在预期结果门控干净后才进入下一级。可选的第二个参数可从指定样本 id 续跑，适合任务被抢占后恢复。

```bash
bash examples/01_run_panel.sh 1
python examples/expected/check_expected.py --mode panel
# 依次运行 tier 2 到 5
bash examples/01_run_panel.sh 2
# ……
bash examples/01_run_panel.sh 5
python examples/expected/check_expected.py --mode all
```

在调度式集群上，应把每个 tier 作为独立作业提交，而不是在交互式 shell 里连续运行数天。一个最简的 Slurm 包装可为每个任务分配 16 线程、32 GB 内存与较长墙钟时间，并把第 2 步的数据库导出写入作业脚本；具体数值按队列调整。

```bash
# 示例：sbatch --cpus-per-task=16 --mem=32G --time=24:00:00 \
#   --wrap='source 00_install/runtime.sh; export CHECKM2_DB=...; bash examples/01_run_panel.sh 1'
```

这些数值是规划建议，而非实测基准。五兆碱基基因组的短读 SPAdes 组装通常远低于 16 GB 内存，而混合/长读组装、Bakta 与 CheckM2 更吃资源。请从调度器记录实际峰值内存与运行时间，并报告这些实测值而非估计值。把菌株作为可并行的数组任务运行，通常比共用一个大节点更简单。

## 7. 运行真实去污染 spike-in

真实 spike-in 向 tier 1 菌株中加入模拟 PhiX 与远缘细菌污染，评估 reads 层去除效果，并同时给出组装与 CheckM2/GUNC 污染面板。它需要 `art_illumina`（主环境的 `art` 包）以及 CheckM2、GUNC 数据库。

```bash
export THREADS=16
export MEM=32
bash examples/02_run_spikein.sh
python examples/expected/check_expected.py --mode spikein
```

这一步会填入合成运行留空的组装与 CheckM2/GUNC 面板，并重新生成 `Fig_spikein` 以及发布到 `figures/`、`docs/assets/` 的副本。

## 8. 预期结果门控与需要归档的内容

门控区分“尚未运行”（`WARN`）与“实测违例”（`FAIL`）。一次完整且可接受的运行不应有 `FAIL`；只有明确不在范围内的模块才允许保留 `WARN`。

```bash
python examples/expected/check_expected.py --mode all
```

请归档并在合适情况下提交支撑手稿的小型派生表：`examples/results/panel_metrics.tsv`、`examples/results/collection_stats.tsv`、`examples/results/expected_check.tsv`、`examples/spikein/results/spikein_metrics.tsv` 以及 spike-in 的 expected-check 文件。原始 reads、BAM 与大型组装文件不纳入 git；若目标期刊要求，请通过公共数据库或归档库发布。

## 9. 锁定已验证环境并完善手稿

完整面板通过后，导出生成结果时所用的确切环境并提交锁定文件，便于审稿人重建。

```bash
bash 00_install/export_locks.sh
git add install/locks/*.yml
```

随后用实测值替换手稿中的临时性表述：面板规模与 tier 构成、组装质控分布、两种 spike-in 模式的污染与保留率、分型与耐药结果、时间树的替换速率与定年、实测运行时间与内存。图片必须由纳入版本管理的脚本重新生成，而不是手工修改。合成 spike-in 应表述为确定性的 in silico 对照；组装层面的污染结论来自真实 spike-in 与面板门控。

## 常见故障

缺少 `easywgs` 环境意味着跳过了第 1 步。模块 12 会拒绝指向 GenBank 文件（`.gb` 或 `.gbk`）的 reference 列，它需要 FASTA 参考，请先转换或下载 FASTA。R 包安装失败只影响模块 11 的静态图片，可单独重跑 `Rscript 00_install/install_R_packages.R`。因网络限制导致 `nextflow pull rki-mf1/clean` 失败不会阻断流程，FCS-GX 与 CheckM2 门控仍会运行，CLEAN 可稍后补充。若在共享 `/db` 路径下出现权限错误，说明该位置只读；对必须自建的数据库（如 GUNC）把 `DBROOT` 设为可写目录，只读的共享数据库仍通过各自的环境变量指向。

## 范围与负责任使用

实战示例仅使用公开、去标识的测序 accession，且完全为 in silico 分析，不包含培养或湿实验。对耐药、血清型或毒力的基因型预测不能替代表型检测或临床实验室报告。
