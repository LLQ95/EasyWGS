# 双层去污染与质量门控

分离株分析最容易出错的环节是污染。EasyWGS 在 reads 与 assembly 两个层面各设
一道关卡，前者在组装前剔除非目标读段，后者在组装后量化并移除残留杂菌片段。

## 第一层：reads 去污染（02 模块）

主工具是 CLEAN，它对短读、长读与 fasta 都可处理，按指定目标类群保留序列，并用
保守策略减少近缘误删。典型用法：

```bash
nextflow run rki-mf1/clean -profile docker \
  --single_end false --reads "clean/*_R{1,2}.fq.gz" \
  --taxonomy "Klebsiella pneumoniae" --keep_taxon true --outdir clean_out
```

先用 Kraken2 做一次成分侦察，能快速判断污染比例与来源物种：

```bash
kraken2 --db $K2_DB --paired R1.fq.gz R2.fq.gz --threads 16 \
        --report k2.report.txt --output - >/dev/null
```

辅助手段还有 BBDuk（按接头、rRNA、已知参考序列剔除）、HoCoRT、deacon。近缘菌
共存时不要追求把非目标读段清零，过度剔除会损失目标基因组的保守区。

## 第二层：组装评估与净化（04 模块）

组装后用 QUAST 看结构指标，用 CheckM2 算完整度与污染率，用 GUNC 判断「两个物种
被拼成一套基因组」式的嵌合；需要更彻底的外源片段清除时，再用 NCBI FCS-GX 或
BlobToolKit：

```bash
# --database_path 为可选项；模块 04 会用 $CHECKM2_DB 或 $DBROOT/checkm2_db 自动填入
checkm2 predict --threads 16 --input genomes/ --output-directory checkm2 -x fasta \
  --database_path "$CHECKM2_DB"
gunc run genomes/${id}.fasta -d $GUNC_DB --threads 16 -o gunc
# FCS-GX（库约470GB，需要大内存；条件不足时传 usegalaxy.org 在线运行）
fcs.py screen genome --fasta ${id}.fasta --out-dir fcs --gx-db $GXDB
fcs.py clean genome  --fasta ${id}.fasta --action-report fcs/*.txt --output cleaned.fasta
```

`CHECKM2_DB` 可以指向 `uniref100.KO.1.dmnd` 文件或其 `CheckM2_database` 目录，从而直接
复用共享数据库；未设置时模块 04 会在 `$DBROOT/checkm2_db` 下查找，再退回通过
`checkm2 database --setdblocation` 注册的默认位置。

## 门控判据与处理

完整度高、污染率低于约 1%、GUNC 无 clade 分离的组装才直接进入下游。污染轻微时
移除外源 contig 后回到 03 重新评估；污染较重或明显嵌合时回到 02 提高清洁强度再
重组装，而不是带着污染继续分型。门控结果写入批次 QC 表，作为论文方法学与数据
质控的依据。

## 为什么长读更依赖组装层门控

短 k-mer 分类在超长 contig 上会出现局部命中、整体误判，三代组装又倾向把读到的
所有序列都拼成长片段，因此三代与混合数据不能只靠 Kraken，要以 CheckM2、GUNC、
FCS-GX 的组装层证据为准，必要时结合 minimap2 对已知杂菌参考做长读比对定位污染段。

## 与分型结果交叉验证

即使门控数值通过，也要用 06 的 MLST 与血清型结果反向核对：一份分离株出现两个
高置信 ST、或同一管家基因出现两套纯合等位，往往是残留污染或混合样本的信号，应
回到本层排查而不是强行选择其中一个结果。
