# 参考比对与变异检测（模块 12）

模块 12 以透明的 BAM、VCF 步骤实现参考比对路线，不再用其它工具在外部封装。它不依赖模块 03 的组装，也不同于模块 09（09 使用 snippy）：模块 09 仍是便捷的一体化核心 SNP 流程，而模块 12 把每一个中间文件都暴露出来，便于直接检查比对与基因型似然。

## 输入

模块读取 `config/my_samples.csv`。`reference` 列必须指向整批共用的单一 FASTA 参考基因组（比对路线不使用 GenBank 文件）。`platform` 列决定比对器：Illumina 与 hybrid 样本用双端短读走 BWA-MEM，ONT 与 PacBio 样本用长读走 minimap2 的 `map-ont` 或 `map-pb` 预设。

## 步骤 12.1：reads 比对到参考

参考基因组只索引一次（`samtools faidx` 与 `bwa index`）。每个样本完成比对、排序、建索引，并生成 flagstat 报告与逐位点深度表。

```bash
bash 12_mapping_pipeline/12.1.map_reads.sh
# 短读
bwa mem -t 8 -R "@RG\tID:ST001\tSM:ST001\tPL:ILLUMINA" ref.fa R1.fq.gz R2.fq.gz \
  | samtools sort -@8 -o bam/ST001.sorted.bam -
samtools index bam/ST001.sorted.bam
# 长读（ONT）
minimap2 -ax map-ont -t 8 ref.fa reads.fq.gz | samtools sort -@8 -o bam/ST001.sorted.bam -
```

`12_mapping_pipeline/qc/coverage_summary.tsv` 汇总每个样本的平均深度、1x 与 10x 覆盖宽度以及 mapped reads 百分比。覆盖宽度偏低通常说明参考基因组与样本亲缘关系过远；宽度高但深度不均，则可能提示重复区或混合污染。安装了 Qualimap 时会自动生成 BAM QC 报告。

## 步骤 12.2：联合变异检测

所有 BAM 用 bcftools 联合分型，按参考做归一化，按质量与深度过滤，并精简为低缺失的双等位 SNP 集合。

```bash
bash 12_mapping_pipeline/12.2.call_variants.sh
bcftools mpileup -q 20 -Q 20 -a AD,DP -f ref.fa -b bam.list -Ou \
  | bcftools call -mv -Oz -o calls.raw.vcf.gz
bcftools norm -f ref.fa -Oz -o calls.norm.vcf.gz calls.raw.vcf.gz
bcftools filter -e 'QUAL<20 || FMT/DP<4' -s LowQual -Oz -o calls.filt.vcf.gz calls.norm.vcf.gz
bcftools view -m2 -M2 -v snps -i 'F_MISSING<=0.1 && MAC>=2' -Oz -o snps.biallelic.vcf.gz calls.filt.vcf.gz
bcftools query -H -f '%CHROM\t%POS\t%REF\t%ALT\t[%GT\t]\n' snps.biallelic.vcf.gz > snp_geno_matrix.tsv
```

过滤阈值（最低质量、最大缺失率、最小次要等位计数）声明在脚本顶部，应按测序深度与集合规模调整。原始与归一化 VCF 保留了 indel 与多等位位点供细查，双等位 SNP VCF 则供给模块 13 与参考路线的系统发育。

## 不组装也能构建参考 SNP 树

双等位 VCF 可转换为多序列比对，直接用于最大似然树，适用于没有组装结果的场景。

```bash
zcat 12_mapping_pipeline/variants/snps.biallelic.vcf.gz > snps.vcf
vcf2phylip -i snps.vcf -f                  # 生成 snps.min4.fasta
iqtree3 -s snps.min4.fasta -m GTR+G4 -alrt 1000 -bb 1000 -pre map_snp_tree
snp-dists snps.min4.fasta > map_snp_dists.tsv
```

## 输出

| 路径 | 内容 |
| --- | --- |
| `12_mapping_pipeline/bam/{id}.sorted.bam(.bai)` | 带读组、已排序建索引的比对文件 |
| `12_mapping_pipeline/qc/{id}.flagstat` | 单样本比对统计 |
| `12_mapping_pipeline/qc/{id}.depth` | 参考各位点深度 |
| `12_mapping_pipeline/qc/coverage_summary.tsv` | 平均深度、覆盖宽度、mapped 百分比 |
| `12_mapping_pipeline/variants/calls.raw.vcf.gz` | 全部联合检测变异 |
| `12_mapping_pipeline/variants/calls.norm.vcf.gz` | 左对齐归一化后的变异 |
| `12_mapping_pipeline/variants/snps.biallelic.vcf.gz` | 供模块 13/建树的过滤后双等位 SNP |
| `12_mapping_pipeline/variants/snp_geno_matrix.tsv` | 每样本一列的基因型矩阵 |
