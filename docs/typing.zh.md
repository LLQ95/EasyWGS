# MLST、血清型与 cgMLST

06 模块分三步：7 基因 MLST、分物种的血清型/表面抗原、全基因组核心多位点序列
分型（cgMLST）。对应 `06.1.mlst.sh`、`06.2.serotype.sh`、`06.3.cgmlst.sh`。

## 7 基因 MLST

mlst 工具内置 PubMLST 数据库，可对组装批量识别序列型：

```bash
mlst --label $id genomes/${id}.fasta >> mlst_all.tsv
```

结果同时给出物种判定与 ST；当一份样本报告冲突的物种或出现混合等位峰时，回到
去污染门控排查。

## 分物种血清型调度

脚本按样本表 species 列选择工具，避免对错误类群套错误数据库。

肺炎克雷伯复合群用 Kleborate，其 v3 通过 preset 调用并集成 Kaptive，同时给出 ST、
K 荚膜与 O 脂多糖抗原、耐药与毒力标志：

```bash
kleborate -a genomes/*.fasta -o kleborate_out -p kpsc --trim_headers
# 变栖克雷伯复合群用 -p kosc，埃希菌可用 -p escherichia；旧版 v2 用 --all
```

大肠埃希/志贺用 ECTyper 识别 O:H，并叠加 ShigEiFinder 区分志贺与肠侵袭性大肠：

```bash
ectyper -i genomes/ -o ectyper_out --cores 16
ShigEiFinder --input genomes --output shigeifinder_out   # 具体参数随版本 --help 核对
```

沙门菌用 SeqSero2 做抗原公式、SISTR 给出血清变种并自带 cgMLST：

```bash
seqsero2_assembly -t 16 -m k -i ${id}.fasta -o seqsero2/$id
sistr -i ${id}.fasta -p cgmlst_profiles -n novel_alleles -o sistr/$id
```

单核增生李斯特菌没有传统 O/H 血清型，走分子血清群与 cgMLST。

## cgMLST 统一用 chewBBACA

无论哪类菌，cgMLST 都遵循「建 schema → 等位调用 → 提取核心 → 质量评估」三步。
有公开 schema 时直接装载，没有时用 PrepExternalSchema 自建：

```bash
chewBBACA.py CreateSchema     -i allele_fasta/ --ptf training/.trn -o schema
chewBBACA.py AlleleCall       -i genomes/ -g schema -o calls --ptf training.trn --cpu 16
chewBBACA.py ExtractCgMLST    -i calls/cgmlst.tsv -o cg --r 0.95
chewBBACA.py AlleleCallEvaluator -g schema -i calls --ptf training.trn -o eval
```

核心等位矩阵可直接算两两等位差异数做最小生成树，用于暴发溯源；与 09 的核心 SNP
树互为印证，cgMLST 适合近缘、短期暴发尺度，SNP 树适合跨克隆群或更长时间尺度。

## 结果怎么解读

MLST 回答属于哪个克隆群，血清型回答表面抗原型，cgMLST 回答样本间相差多少个核心
等位。暴发判定通常要求 cgMLST 等位差异落在极低阈值内，且与流行病学、时间树结果
一致，单凭单一分型结果下结论要谨慎。
