# 微生物 GWAS 与 post-GWAS（模块 13）

模块 13 把 easyWGS 从特征描述拓展到基因型与表型的关联分析。它提供三层互补的细菌 GWAS：基于基因有无的 Scoary、基于 SNP 关联的 PLINK、以及显式建模克隆群体结构、同时支持基因与 SNP 的 pyseer；最后用统一的 post-GWAS 步骤完成多重检验校正、QQ 图与曼哈顿图，并汇总显著命中。细菌基因组具有很强的克隆结构，因此关联结果必须结合系统发育一起解读，不能只看原始 p 值。

## 准备表型表

表型放在 `config/traits.csv`。第一列 `Name` 必须与 samplesheet 的 `id`、以及泛基因组中的分离株名称一致；其后每一列是一个性状。Scoary 使用编码为 0/1 的二元性状，PLINK 与 pyseer 还接受数值型连续性状，未知值填 NA。当前分析的性状由 `TRAIT` 变量选择，默认 MDR。

```bash
TRAIT=ESBL bash 13_gwas/13.run_gwas.sh       # 对某一性状运行全部三层
bash 13_gwas/13.4.post_gwas.R "$(pwd)"       # 只运行 post-GWAS
```

## 13.1 基于基因的 pan-GWAS：Scoary

Scoary 对 Panaroo 或 Roary 的 `gene_presence_absence.csv` 中每个基因、针对每个二元性状做 Fisher 精确检验，补充考虑群体结构的成对比较，并用 Benjamini-Hochberg 控制错误发现率；也提供更严格的 Bonferroni 选项（`-c B`），还可通过标签置换得到经验 p 值。

```bash
bash 13_gwas/13.1.scoary.sh
scoary -t config/traits.csv -g 08_pangenome/.../gene_presence_absence.csv \
       -o 13_gwas/scoary -c BH -p 0.05 -n 1000 --threads 8
```

当表型可能由附属基因组驱动时（例如获得性耐药基因、荚膜或致病岛），基于基因的检验是首选，因为它围绕基因内容、不受参考基因组限制。

## 13.2 基于 SNP 的关联：PLINK

模块 12.2 的双等位 SNP VCF 先转换为 PLINK 二进制文件。由于克隆面板不满足人类 GWAS 的随机交配假设，脚本先构建基于 IBS 的 MDS 投影，再把 MDS 轴作为协变量纳入病例对照 logistic 回归或连续性状线性回归，同时保留一个未校正的快速等位检验用于对照。

```bash
TRAIT=MDR bash 13_gwas/13.2.plink.sh
plink --vcf snps.biallelic.vcf.gz --make-bed --double-id --allow-extra-chr \
      --set-missing-var-ids @:# --out base
plink --bfile base --allow-extra-chr --cluster --mds-plot 4 --out mds
plink --bfile base --allow-extra-chr --pheno pheno.txt --1 \
      --covar covar_mds.txt --logistic hide-covar --adjust --ci 0.95 \
      --out assoc_logistic
```

如果某信号在加入 MDS 轴后消失，或只落在单一克隆分支上，它更可能是谱系标记而非因果变异。

## 13.3 基因与 SNP 的 GWAS：pyseer

pyseer 是 SEER 框架的微生物学再实现，能用统一的统计模型接受多种特征类型。脚本基于泛基因组二元矩阵做基因层检验、基于模块 12 的 VCF 做 SNP 层检验，并用成对距离矩阵（模块 09 的 SNP 距离矩阵，或 Mash 矩阵）作为距离核，通过线性混合模型控制群体结构。脚本还以注释命令给出可选的 k-mer/unitig 路线，用于不依赖注释的因果标记发现。

```bash
TRAIT=MDR bash 13_gwas/13.3.pyseer.sh
pyseer --phenotypes pheno.tsv --presence gene_presence_absence.Rtab \
       --distances snp_dists.tsv --min-af 0.02 --max-af 0.98 --cpu 4 \
       --output assoc_genes.txt
pyseer --phenotypes pheno.tsv --vcf snps.biallelic.vcf.gz \
       --distances snp_dists.tsv --min-af 0.02 --cpu 4 --output assoc_snps.txt
```

等位频率上下限会移除近乎固定或仅出现一次、没有对比信息的特征；小面板应收紧该阈值。pyseer 输出效应量（beta）、标准误与似然比 p 值，还能估计谱系核解释的方差，作为克隆混杂的诊断。

## 13.4 统一的 post-GWAS 分析

`13.4.post_gwas.R` 读取所有存在的结果文件，重新计算 Benjamini-Hochberg 与 Bonferroni 校正 p 值，为每种方法、每层画 QQ 图，为带位置的 SNP 画曼哈顿图（含全基因组线与本研究 FDR 线），并输出按校正 p 值排序的合并显著命中表。QQ 图膨胀、整体向左偏移，提示所选校正仍未去除残余群体结构。

```bash
Rscript 13_gwas/13.4.post_gwas.R /path/to/easyWGS
```

## 结果解读与局限

小而克隆化的面板常常没有 FDR 显著命中，这是正常结果而非运行失败。一个显著结论还应有效应量支持、应独立于谱系、最好能在第二个独立集合中重复，并能结合模块 05 注释或外部数据库给出生物学机制。宿主、国家、年份、测序平台等混杂因素应在性状组间保持均衡。基因层方法（Scoary 或 pyseer 基因层）与 SNP 层方法同时命中的结果，远比单层结果更有说服力。

## 输出

| 路径 | 内容 |
| --- | --- |
| `13_gwas/scoary/<trait>.csv` | 每基因的原始、BH、成对 p 值与比值比 |
| `13_gwas/plink/*.assoc*` | 等位检验与带协变量的回归结果 |
| `13_gwas/plink/mds.mds` | 作为群体结构协变量的 IBS 轴 |
| `13_gwas/pyseer/assoc_genes.txt` / `assoc_snps.txt` | 基因与 SNP 关联，含 beta 与似然比 p |
| `13_gwas/post/qq_*.pdf` / `.png` | 各方法各层 QQ 图 |
| `13_gwas/post/manhattan_*.pdf` / `.png` | SNP 结果曼哈顿图 |
| `13_gwas/post/*_FDRhits.csv`、`combined_FDRhits.csv` | 校正后的显著命中表 |
