# 泛基因组

泛基因组分析对应 08 模块，用 Panaroo 在多个分离株间聚类同源基因，输出核心、附属
与独有基因；Roary 作为备选，适合规模较小、注释一致的数据集。

## 输入准备

Panaroo 直接读取各样本 Prokka 产出的 GFF，要求注释版本与遗传代码一致。把每个
样本的 GFF 放到同一目录或用通配符列出：

```bash
panaroo -i prokka/*/*.gff -o panaroo_out --clean-mode strict \
        --core_threshold 0.98 -a core --threads 16
```

strict 模式合并错误较少，适合近缘克隆群；样本差异较大时可用 moderate。分析前先用
mash 或 CheckM2 剔除污染、用 dereplicator/cd-hit 对高度冗余的基因组去重，避免
近重复样本主导核心基因估计。

## 输出与下游

`gene_presence_absence.csv` 给出每个基因簇在各样本中的分布，`core_gene_alignment`
是核心基因比对，可直接送 09 模块或单独建树。对核心/附属比例随样本数的增长做
累积曲线，可判断采样是否达到泛基因组饱和。

## 与系统发育的关系

核心基因比对适合中高变异度样本，核心 SNP 适合近缘暴发样本，两条线在 09 交汇。
泛基因组的附属基因存在/缺失矩阵还可与表型做关联，是后续 GWAS 的输入之一，但关联
分析需要足够样本量与多重检验校正，不属于本流程的默认步骤。
