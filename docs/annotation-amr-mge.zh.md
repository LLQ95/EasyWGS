# 注释、耐药、毒力与可移动元件

本阶段对应 05 与 07 模块。05 完成结构与功能注释，07 在其上扫描耐药、毒力与各类
可移动遗传元件，这些结果共同支撑流行病学与传播机制解读。

## 结构与功能注释（05）

Prokka 适合快速批量注释，Bakta 数据库更新、对耐药与质粒片段标注更细，eggNOG
mapper 提供 GO、KEGG、COG：

```bash
prokka --outdir prokka/$id --prefix $id --cpus 16 --kingdom Bacteria genomes/$id.fasta
bakta --db $BAKTA_DB --threads 16 --output bakta/$id genomes/$id.fasta
emapper.py -i prokka/$id.faa -o $id --cpu 16 -m diamond
```

Prodigal 单独输出蛋白编码基因，供下游自建库比对与 pan 分析使用。

## 耐药、毒力与点突变（07）

abricate 用多个数据库做一次批量扫描，AMRFinderPlus 与 RGI(CARD) 交叉验证，
PointFinder 负责染色体点突变介导的耐药：

```bash
for db in resfinder vfdb card ncbi ecoli_vf megares; do abricate --threads 16 --db $db genomes/$id.fasta; done
amrfinder -n genomes/$id.fasta -d $AMR_DB --threads 16
rgi main -i genomes/$id.fasta -o rgi/$id -t contig -a DIAMOND --local
```

自建库可加入 bacmet2（抗菌剂/金属耐受）、ICE、oriT、relaxase、SGI-1、fljAB、
ecoh 等特异标志，abricate 用 `--datadir` 指向自建库目录即可。PointFinder 对文件名
敏感，样本与输出目录不要用下划线之外的多余符号，脚本已做安全命名。

## 质粒

mob-suite 判定复制子、松弛酶与迁移类型并分型；PlasmidFinder 识别复制子；PLSDB
做已知质粒比对溯源；PlasFlow 按序列特征区分染色体与质粒片段：

```bash
mob_typer --infile genomes/$id.fasta --outdir mobsuite/$id
abricate --db plasmidfinder genomes/$id.fasta
mash dist plsdb.msh genomes/$id.fasta
```

需要质粒层面的传播关系时，可把质粒序列单独抽出、对齐、建树，与染色体树对比判断
是垂直遗传还是水平转移。

## 整合子、插入序列与 ICE

IntegronFinder 找整合子与基因盒；ISfinder/ISEScan 识别插入序列；mobileOG 给可
移动元件功能注释；MGEfinder、oriT/relaxase 库用于定位接合元件与 ICE 边界，genomad
可一并识别质粒与噬菌体片段：

```bash
integron_finder --local --cpu 16 genomes/$id.fasta
# ISfinder 为在线/授权库，ISEScan 可本地批量；mobileOG 用 diamond 比对其蛋白库
genomad run -t 16 genomes/$id.fasta genomad/$id $GENOMAD_DB
```

## 噬菌体与 CRISPR

温和噬菌体用 IslandPath 看基因组岛、VirSorter2 识别前噬菌体、PhiSpy 做边界定位，
PHASTER 提供在线复核；CRISPRCasFinder 鉴定 CRISPR 阵列与 cas 系统。这些元件的
位置建议在圈图上与耐药、毒力基因叠加展示，判断是否位于同一可移动背景上。

## 结果整合

07 的所有命中以「样本、元件类型、数据库、基因、位置、覆盖度、身份值」的长表
汇总，由 99 模块并入主表。不同数据库命名口径不同，合并时保留原始基因号与库来源，
避免只留一个统一名而丢失可追溯性。
