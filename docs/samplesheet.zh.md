# 输入与样本表

所有批量调度都由一张样本表驱动，模板为 `config/samplesheet.csv`，使用时复制为
`config/my_samples.csv`。表头固定，顺序不要改：

```text
id,platform,species,R1,R2,longreads,reference,date,country,phenotype
```

## 字段说明

| 列 | 必填 | 取值与含义 |
| --- | --- | --- |
| id | 是 | 样本唯一编号，不含空格与多余点号，下游目录与文件都以它命名 |
| platform | 是 | illumina / nanopore / pacbio / hybrid，决定组装与质控路线 |
| species | 是 | kpsc / ecoli / salm / listeria / other，决定 06 的分型调度 |
| R1,R2 | 视平台 | 二代双端路径；纯三代可留空 |
| longreads | 视平台 | 三代长读路径；nanopore、pacbio、hybrid 必填 |
| reference | 09 需要 | 核心 SNP 系统发育的统一参考，GenBank 格式，全批次一致 |
| date | 10 需要 | 采样日期，YYYY-MM-DD 或小数年，供 TreeTime 分子钟使用 |
| country | 否 | 采样国家/地区，供状态迁移（mugration）分析 |
| phenotype | 否 | 药敏或表型标签，供后续与基因型关联 |

## 不同平台怎么填

二代只填 R1/R2；纯三代把 platform 设为 nanopore 或 pacbio、只填 longreads；混合
组装填齐 R1/R2 与 longreads。三类样本可以混在同一张表里，03 组装脚本会按每行的
platform 自动分流，不需要拆成多个项目。

## 命名约定

样本 id 会被多个工具当作序列前缀，避免空格、中文、连续点号，建议用「菌种缩写+
年份+流水号」，例如 KP2023_001。组装完成后，无论哪条路线，最终结果都统一写成
`03_assembly/genomes/{id}.fasta`，04 之后所有模块只读取这个目录。

## 参考基因组的选择

09 的核心 SNP 分析要求全批次使用同一个近缘、完整、注释齐全的参考。参考与样本
亲缘过远会产生大量参考缺失位点和错误比对；可先用 mash 估计与样本最近缘的公开
基因组，再确定参考。参考文件随项目放在 `ref/`（已被 git 忽略），不要写死到脚本里。

## 日期与元数据

TreeTime 对采样日期敏感，缺失或明显错误的日期会在时钟回归中表现为离群。能确定到
具体日期就写日期，只知道年份可用小数年（如 2021.5）。country、phenotype 为可选
列，留空不影响主流程，只在状态迁移或基因型表型关联时使用。
