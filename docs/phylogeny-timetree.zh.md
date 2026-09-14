# 系统发育与时间树

09 模块构建核心 SNP 系统树，10 模块在其上用 TreeTime 做分子钟定年与祖先状态推断。

## 核心 SNP 系统树（09）

以样本表中统一指定的参考为基准，snippy 逐样本找变异，snippy-core 合并全位点对齐；
重组会制造大量假 SNP，用 Gubbins 去除后再抽恒定信息位点：

```bash
snippy --cpus 16 --ref ref.gbk --out snippy/$id --R1 R1.fq.gz --R2 R2.fq.gz   # 或 --ctgs 组装
snippy-core --ref ref.gbk snippy/*
run_gubbins.py --prefix gubbins core.full.aln
snp-sites -c gubbins.filtered_polymorphic_sites.fasta > core_snps.fasta
iqtree2 -s core_snps.fasta -m GTR+G4 -bb 1000 -nt 16
snp-dists core.full.aln > snp_distance.tsv
```

近缘暴发分析同时报告两两 SNP 距离矩阵，用于界定传播簇。模型可用 ModelFinder
自动选择；样本量很大时 FastTree 用于快速预览，正式成稿用 IQ-TREE。

## 时间树（10，TreeTime）

树要带采样日期才有定年意义，日期取自样本表 date 列。先做分子钟回归排查离群，
再推断时间树、祖先序列、同源突变与状态迁移：

```bash
treetime clock       --tree nwk --aln aln --dates metadata_dates.csv --clock-filter 3
treetime             --tree nwk --aln aln --dates metadata_dates.csv --reroot least-squares
treetime ancestral   --tree nwk --aln aln --outdir ancestral
treetime homoplasy   --tree nwk --aln aln --outdir homoplasy
treetime mugration  --tree nwk --states country.csv --attribute country --outdir geo
```

时钟回归中明显偏离的样本先核对采样日期与分支位置，不要直接删除；弱时钟信号
（根到端距离与日期相关性低）时，时间树结论要弱化，只报告相对顺序而非绝对年代。

## 结果解读与配图

系统树用 SNP 距离、克隆群、血清型、耐药表型与采样地多轨注释；时间树在时间轴上
展示最近共同祖先年代与地理迁移。传播结论需要树拓扑、SNP/cgMLST 距离与流行病学
时间线三者一致，单凭树的相邻关系不足以判定直接传播。
