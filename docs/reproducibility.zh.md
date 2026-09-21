# 可复现性与测试

EasyWGS 在三个层面保证可复现：可移植的软件清单、按机器导出的精确环境锁定，以及容器镜像。在此之上，guidebook 中每一个定量结果都由纳入版本管理、固定随机种子的脚本产生，并由一套小型的“预期结果”门控判断运行是否合格。本页说明哪些检查由持续集成自动完成、哪些在集群上验证，以及如何复现。

## 软件环境

主环境 `easywgs` 的可移植、不锁版本清单是 `install/environment.yml`，与 `00_install/install_env.sh` 的包列表保持一致；更小的 `install/environment.ci.yml` 只包含合成冒烟测试所需的轻量工具。

```bash
# 真实分析用的完整环境
conda env create -f install/environment.yml
# 冒烟测试与持续集成使用的最小环境
conda env create -f install/environment.ci.yml
```

清单刻意不锁定每个包的版本，以便跨操作系统可用。若需要逐位可复现的分析环境，请在 Linux/x86_64 机器上创建环境后用 `00_install/export_locks.sh` 导出锁定文件，写入 `install/locks/`（命名为 `<env>.linux-64.yml`）并提交。

```bash
bash 00_install/install_env.sh     # 创建 easywgs、longread、checkm2、gunc、bakta、eggnog
bash 00_install/export_locks.sh    # 将精确锁定写入 install/locks/
git add install/locks/*.yml
```

用 `conda env create -f install/locks/easywgs.linux-64.yml` 即可重建被锁定的环境。

## 容器镜像

Docker 镜像在不安装本地 Conda 的情况下提供主环境，由 `.github/workflows/container.yml` 自动构建并发布到 GitHub Container Registry。EasyWGS 脚本与数据在运行时挂载，因此拉取新版本代码无需重建镜像。

```bash
docker build -t easywgs:latest -f Dockerfile .
docker run --rm -it \
  -v "$PWD":/EasyWGS -v "$HOME/easywgs_db":/opt/db:ro \
  -w /EasyWGS -e DBROOT=/opt/db easywgs:latest bash
```

在使用 Apptainer 或 Singularity 的 HPC 集群上，可用 `containers/Singularity.def` 封装同一镜像（`apptainer build easywgs.sif containers/Singularity.def`），并用 `--bind` 挂载数据库目录。

CheckM2、GUNC、Bakta、eggNOG 与 FCS-GX 等大型参考数据库不会内置进镜像，请以只读方式挂载，并通过运行时变量 `DBROOT`、`CHECKM2_DB`、`GUNC_DB`、`BAKTA_DB`、`EGGNOG_DB` 指向它们。专用的 `checkm2`、`gunc`、`bakta`、`eggnog` 环境由 `install_env.sh` 在集群上创建，不放入默认镜像。

## 持续集成运行的内容

`.github/workflows/ci.yml` 在每次向 `main` 推送和提交拉取请求时运行两个作业。

静态作业安装文档依赖，运行 `python tests/run_static_checks.py`，随后执行 `mkdocs build --clean --strict`。静态检查用 `bash -n` 校验每个 shell 脚本、编译每个 Python 文件、在装有 R 时解析每个 R 脚本，强制脚本仅含 ASCII、默认英文页面不含中文，校验 `reference/tool_catalog.tsv` 的表头与状态码，并确认自动生成的工具百科页面是最新的。严格的 MkDocs 构建会把任何失效的交叉引用或警告视为错误。

冒烟作业用 micromamba 创建 `install/environment.ci.yml`，并在完全合成的数据上运行 `bash tests/run_smoke.sh`。生成器 `tests/make_toy_data.py` 使用固定种子（20260921）构建一条 120 kb 的参考和两个菌株：一个与参考完全相同，另一个带有 48 个分散的单核苷酸改变；每个菌株约 35 倍覆盖度、150 bp 双端 reads。冒烟测试随后按顺序运行真实模块脚本：`01_qc/01.fastp.sh` 质控；`12_mapping_pipeline/12.1.map_reads.sh` 执行 `bwa mem`、生成排序并建索引的 BAM 与覆盖度汇总；`12_mapping_pipeline/12.2.call_variants.sh` 联合变异检测；以及自包含的去污染 spike-in。

门控要求两个菌株的 1 倍深度覆盖广度至少 0.90、平均深度至少 15 倍、比对率至少 90%，并要求带突变的菌株至少恢复 20 个双等位 SNP；干净对照不应产生变异集。

同一作业还以合成模式运行 reads 层去污染 spike-in（`examples/02_run_spikein.sh --synthetic`）。脚本用固定种子生成三个基因组，分别扮演目标菌、类 PhiX 技术对照和远缘细菌，并按 1%、5%、10% 加入污染 reads。当存在 `bwa` 与 `samtools` 时使用与生产一致的比对引擎分类和过滤；否则由 `examples/spikein/synthetic_fixture.py` 内置、零依赖的 k-mer 分类器计算相同指标。`examples/expected/expected_spikein.tsv`（S1–S5）要求清洗前能检出混入污染、清洗后残留污染不超过 2%、目标 reads 保留率至少 90%，以及固定的 12,000 对基线。

## 自行运行测试

```bash
# 仅静态检查（不需要生物信息工具）
python tests/run_static_checks.py

# 完整功能冒烟（需要 environment.ci.yml 中的工具）
conda activate easywgs-ci
bash tests/run_smoke.sh

# 只跑合成 spike-in 及其门控（无 bwa 时使用 k-mer 后端）
SYNTHETIC=1 bash examples/02_run_spikein.sh
```

预期结果检查器会区分“尚未运行”和“违反规则”：缺失指标记为 `WARN`，不会导致失败；实测值超出阈值记为 `FAIL`，并返回非零退出码。

```bash
python examples/expected/check_expected.py --mode spikein   # 去污染
python examples/expected/check_expected.py --mode panel     # 真实菌株面板
python examples/expected/check_expected.py --mode all       # 两者，默认
```

## 在真实 reads 上快速冒烟

合成测试无法暴露真实测序化学特有的问题。下载公共面板后，可用每株固定 reads 对数构建可复现的迷你面板，运行不需要参考基因组的组装路线：

```bash
bash examples/00_download_panel.sh
bash examples/scripts/downsample_panel.sh examples/generated/samplesheet_tier1.csv 200000
bash run_assembly.sh config/my_samples.mini.csv
```

从 tier 1 到 tier 5 的完整验证（组装、CheckM2/GUNC、注释与真实 spike-in）在[集群运行清单](cluster-checklist.zh.md)中逐步说明。

## 自动化测试的边界

SPAdes、Unicycler 组装，CheckM2、GUNC 组装质控，Bakta、Prokka 注释，eggNOG-mapper 与 FCS-GX 被有意排除在持续集成之外。它们是成熟的第三方工具，但需要数 GB 的数据库或较长运行时间；在每次提交时运行既慢，也几乎不能为 EasyWGS 自身的回归提供额外保护。这些步骤在 `docs/cluster-checklist.md` 所述的真实公共面板上验证，其输出同样纳入预期结果门控。合成 spike-in 只验证 reads 层；其组装与 CheckM2/GUNC 面板由集群上运行的真实 spike-in 产生，在未运行时保持为空，而不是填入模拟数值。

## 重新生成图片

所有手稿与 guidebook 图片都由固定种子的确定性 Python 脚本产生：`figures/make_*_figure.py` 对应工作流与概览图，`examples/spikein/make_spikein_figure.py` 对应 spike-in 图。运行脚本会覆盖 `figures/` 与 `docs/assets/` 中的副本，因此图片始终与提交的脚本和数据一致。
