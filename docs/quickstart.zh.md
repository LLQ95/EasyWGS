# 快速开始

本章用一个最小例子走通整条链路。假设工作目录就是仓库根目录。

## 1. 放置原始数据

把原始 fastq 放入 `00_rawdata/`。二代双端命名为 `样本ID_R1.fastq.gz`、
`样本ID_R2.fastq.gz`；三代长读命名为 `样本ID_ONT.fastq.gz` 或自定并在样本表写明。

## 2. 填写样本表

```bash
cp config/samplesheet.csv config/my_samples.csv
```

模板里每列的含义见[输入与样本表](samplesheet.md)。`config/my_samples.csv` 已在
`.gitignore` 中，不会误提交私有路径。

## 3. 一键运行或分步运行

```bash
# 一键：从质控跑到汇总
bash run_all.sh config/my_samples.csv

# 从指定步骤恢复，例如只重跑 06 分型之后
bash run_all.sh config/my_samples.csv 06
```

也可以进入单个目录手动执行，便于调试：

```bash
bash 01_qc/01.fastp.sh
bash 01_qc/01b.long_qc.sh     # 仅有三代/混合样本时实际工作，纯二代自动跳过
bash 02_decontam_reads/02.clean_reads.sh
bash 03_assembly/03.assemble.sh
```

## 4. 查看关键产物

| 阶段 | 关键输出 | 看什么 |
| --- | --- | --- |
| 03 组装 | `03_assembly/genomes/{id}.fasta`、genome_stats.tsv | contig 数、N50、总长度是否符合同种预期 |
| 04 门控 | CheckM2 完整度/污染、GUNC 嵌合分 | 完整度、污染率、CSS 与 clade 分离 |
| 06 分型 | MLST、血清型、cgMLST 等位文件 | ST、K/O 或 O:H、等位谱 |
| 09–10 | 系统树、时间树 | 拓扑、分子钟离群、采样日期一致性 |
| 99 | `99_report/master_table.tsv` | 每样本一行的合并总表 |

## 5. 一个纯二代例子

样本表中 `platform=illumina`、提供 R1/R2 即可，流程默认用 Unicycler 组装（单菌
场景对质粒更友好、倾向成环），必要时在 03 脚本里切换到 `spades.py --isolate`。

## 6. 一个混合组装例子

`platform=hybrid` 且同时提供双端与 longreads，流程用 `unicycler --mode bold` 以
长读搭骨架、短读纠错，并用 Pilon 再回填一轮。混合组装通常最接近完成图，但前提是
短读先经过去污染，否则长读会把污染放大成完整的错误 contig。
