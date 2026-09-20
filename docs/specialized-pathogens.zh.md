# 专化病原：物种确认、毒素与表面位点分型

EasyWGS 最早纳入的几类病原（沙门菌、肺炎克雷伯菌、大肠埃希菌/志贺菌、单增李斯特菌）都有持续维护的命令行血清型工具，而另外几类常见病原并非如此。对于副溶血性弧菌、小肠结肠炎耶尔森菌、空肠/结肠弯曲菌、唐菖蒲伯克霍尔德菌和肉毒梭菌，血清型或毒素型别仍主要依据表面多糖位点、毒素基因和毒力标记来判定，缺少统一的分型软件。EasyWGS 因此为这些病原组合了三个可复现的环节：FastANI 全基因组物种确认（模块 04.5）、模块 06.1 的七基因 MLST 序列型，以及模块 06.4 基于 abricate 的表面位点、毒素与毒力位点筛查。带权威来源的标记清单见
[`examples/customdb/easywgs_markers.tsv`](https://github.com/LLQ95/EasyWGS/blob/main/examples/customdb/easywgs_markers.tsv)。

示范面板的第 4 层（tier 4）为这五类病原各加入 3 株 Illumina 样本，使整个面板从 29 株扩展到 44 株、覆盖十个病原类群。所有测序登录号和参考基因组均已在 ENA 与 NCBI 核实， accession 表见
[`examples/panel.tsv`](https://github.com/LLQ95/EasyWGS/blob/main/examples/panel.tsv)。

## 用 FastANI 做物种确认（模块 04.5）

混合的多物种面板在进行任何单物种比较之前，需要一次明确的物种身份核对。模块 04.5 用 [FastANI](https://github.com/ParBLiSS/FastANI) 将每个组装对 `ref/` 下的全部面板参考基因组逐一计算 ANI，并保留 ANI 最高的匹配。它紧跟在组装质检与去污染门控之后运行，结果写入 `04_asm_qc/fastani/fastani_best.tsv`，包含期望参考、最佳匹配参考、最高 ANI 和状态标签。

```bash
PROJECT=$PWD bash 04_asm_qc/04.5.fastani_identity.sh
```

对期望参考的 ANI 不低于 95% 判为同一物种；90% 到 95% 之间表示同属近缘种，通常意味着缺少物种级参考；低于 90%、结果为空或最佳匹配与期望参考不一致时，需要核对样本标签或排查残留污染。FastANI 对约 80% ANI 以下的配对不输出结果，因此无关污染会产生空的单样本文件，而不是一个误导性的低分。面板把这一行为作为教学点：两株空肠弯曲菌对 NCTC 11168 得到物种确认，而结肠弯曲菌落在近缘种区间，这正是“种内分析需要补充结肠弯曲菌参考”的正确提示。

FastANI 安装在主环境 `easywgs` 中。当 FastANI 或参考基因组缺失时，模块会写出空表并继续运行，与 CheckM2、GUNC 的优雅降级方式一致。

## 构建自定义标记数据库（模块 06.4）

模块 06.4 用 [abricate](https://github.com/tseemann/abricate) 对名为 `easywgs_markers` 的小型数据库进行筛查。标记序列既不随 git 分发，也不自动下载，因为表面抗原和毒素等位基因带有型别特异的参考集合以及数据库许可限制；仓库改为提供带来源的 curated 清单。建库时，从清单所列的 RefSeq 参考基因组、VFDB 或 PubMLST 记录获取每个位点或等位基因的序列，拼接成一个多 FASTA 文件，文件头以 `marker_id` 开头，然后运行建库脚本。

```bash
# 文件头约定：>marker_id|allele 自由说明
MARKER_FASTA=/path/to/easywgs_markers.fa bash 00_install/build_custom_db.sh
PROJECT=$PWD bash 06_typing/06.4.surface_toxin_loci.sh
```

建库脚本默认把数据库放在 `~/.abricate/db/easywgs_markers`，可用 `EASYWGS_ABRICATE_DIR` 更改；也可用 `EASYWGS_MARKER_DIR` 让模块 06.4 直接指向已建好的目录。输出为 `06_typing/surface_toxin/custom_markers_all.tab` 以及存在性矩阵 `custom_markers_summary.tab`。通用基因标记只能判断有无；O/K 群、Penner 荚膜型和 BoNT 亚型需要型别特异的参考等位，按每个型别一条序列加入（例如 `CB_bont|A`、`CB_bont|B`）。

## 各病原分型要点

### 副溶血性弧菌（Vibrio parahaemolyticus）

参考为 RIMD 2210633（GCF_000196095；NCBI taxid 670），`mlst` 使用副溶血性弧菌 scheme。物种特异的不耐热溶血素基因 `tlh`（也称 `ldh`）几乎在所有分离株中都存在，兼作物种标记。致病潜力通过 `tdh`（耐热直接溶血素）、`trh`（含 `trh1`、`trh2` 变体）、T3SS2 区域（`vtrB`、`vscN2`）以及大流行 O3:K6/ST3 克隆标记 `orf8` 评估。经典 O 群和 K 型分别由 `wzx/wzy` 与 `wza/wzb/wzc` 位点编码，但判定具体 O/K 群需要型别特异的参考等位，单条通用序列无法定型；清单中以 `surface_O` 和 `surface_K` 类别标注。

### 小肠结肠炎耶尔森菌（Yersinia enterocolitica）

参考为 8081 株（GCF_000009345；taxid 630）。`mlst` 使用覆盖该种的耶尔森菌属级 scheme。染色体标记包括黏附侵袭位点 `ail`、耐热肠毒素变体 `ystA` 与 `ystB`、侵袭素 `inv` 和铁草铵膦受体 `foxA`。毒力质粒 pYV 通过 `yadA` 和转录激活因子 `virF`（也称 `lcrF`）追踪。`caf1`（F1 荚膜）与 `pla` 是鼠疫耶尔森菌的鉴别标记，在小肠结肠炎耶尔森菌中应为阴性。生物型（1A、1B 以及 2 至 5 型）没有纯 WGS 的统一命令行判定工具，宜结合这些标记、MLST 和表型记录综合判断。

### 空肠弯曲菌与结肠弯曲菌（Campylobacter jejuni / C. coli）

共用参考为 NCTC 11168（GCF_000009085；空肠弯曲菌 taxid 197，结肠弯曲菌 taxid 195）。两者在 `mlst` 中共用弯曲菌 scheme；PubMLST 的 jejuni-coli cgMLST scheme 可按模块 06.3 的说明用 `PrepExternalSchema` 适配给 chewBBACA。毒力标记包括细胞膨胀毒素（`cdtA`、`cdtB`、`cdtC`）、纤连蛋白结合黏附素 `cadF`、鞭毛蛋白 `flaA`、侵袭抗原 `ciaB` 和主要外膜蛋白 `porA`。Penner（HS）荚膜血清型没有统一维护的开源命令行工具，其决定区域是包含 `hddA` 等 O-甲基磷酰胺修饰基因的荚膜生物合成位点，定型需要完整的型别特异荚膜参考。`gyrA` 和 23S rRNA 上与氟喹诺酮、大环内酯耐药相关的点突变由模块 07 的 PointFinder 环节处理，不在本标记筛查中。

### 唐菖蒲伯克霍尔德菌与产米酵菌酸致病型

模式株参考为 ATCC 10248（GCF_000959725；taxid 28095）。`mlst` 数据库中没有唐菖蒲伯克霍尔德菌的经典七基因 MLST scheme，因此物种身份依靠 FastANI 和其多复制子的基因组大小确认，而非 ST。两个毒素位点具有临床重要性：米酵菌酸生物合成簇（`bon`，含 `bonJ`、`bonF` 等；Moebius 等，2012）见于与发酵椰子、玉米食物中毒相关的椰毒致病变型 pv. *cocovenenans*，普通临床株通常缺失；毒黄素簇（`tox`，以 `toxA` 代表）与近缘的唐菖蒲/颖壳伯克霍尔德菌共有。因此，示范用临床株得到空的 `bon` 结果属于预期，而非流程失败；出现阳性 `bon` 命中时，应进一步检查基因簇覆盖度和 contig 上下文加以确认。

### 肉毒梭菌（Clostridium botulinum）

参考为 ATCC 3502 株（GCF_000063585；taxid 1491），`mlst` 使用肉毒梭菌 scheme。肉毒神经毒素位点 `bont`（也注释为 `cnt`）决定 A 至 G 型、嵌合毒素及众多亚型；标记筛查只能判断有无，型别需要为每个亚型加入一条 curated 参考等位。其侧翼的无毒非血凝素 `ntnh`、血凝素组分 `ha33` 和毒素簇调控因子 `botR` 可提供基因簇上下文。亚型级毒素判定的一个成熟替代方案是 Bactopia 项目的 GAMMA 模块，配合 curated 的神经毒素参考集。由于 `bont` 可位于染色体或质粒上，模块 07 已运行 [MOB-suite](https://github.com/phac-nml/mob-suite) 重建并分型质粒 contig，标记结果应与该重建结果一起判读。

## 在面板上运行比较模块

模块 08（泛基因组）、09（核心 SNP）、10（TreeTime）、12（参考比对）和 13（GWAS）都假定单一物种和一个共享参考。在混合的 44 株面板上，这些模块应在单物种子集上运行，而不是一次性对全部样本运行。辅助脚本
[`examples/scripts/subset_samplesheet.py`](https://github.com/LLQ95/EasyWGS/blob/main/examples/scripts/subset_samplesheet.py)
按 `species_code`（默认）或面板 `group` 过滤指定层级生成的样本表、日期和性状文件，并打印后续复制与运行命令。

```bash
python examples/scripts/make_samplesheets.py 4
python examples/scripts/subset_samplesheet.py 4 campylobacter
cp examples/generated/subset_species_campylobacter/samplesheet.csv  config/my_samples.csv
cp examples/generated/subset_species_campylobacter/metadata_dates.csv config/metadata_dates.csv
cp examples/generated/subset_species_campylobacter/traits.csv         config/traits.csv
bash run_all.sh config/my_samples.csv 08
```

按 `species_code` 过滤会把大肠埃希菌和志贺菌保留在一起，这与志贺菌在物种上归属于大肠埃希菌的事实一致；若只需要某一个面板分组，可改用 `--by group`。逐样本模块（质控、组装、去污染、注释、MLST、FastANI 和标记筛查）无需子集化，可直接在完整的混合面板上运行。

## 范围与局限

自定义筛查是基于透明、用户自备参考序列的存在性判断层，不能替代 PubMLST 等 curated 服务在权威定型或监测报送中的作用。型别特异的判定（O/K、Penner、BoNT 亚型）需要相应参考等位，并需人工检查覆盖度与位点上下文。毒素基因阳性只代表基因型层面的潜能，必须结合表型、质粒或染色体定位以及相关生物安全规定共同解释。示范样本来自公开监测或临床株，并不保证为产毒株；流程报告的是基因型，不直接断言产毒表型。
