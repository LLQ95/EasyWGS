# 可视化与交互探索

模块 11 位于分型、泛基因组、核心 SNP 系统发育和时间树的下游，把这些产物转成可读的图，
并为在线工具打包上传文件。整体分为两层：本地生成的静态出版图，以及浏览器中的交互图。

- R 静态图：用 ggtree 画带注释的树，用 pheatmap 画距离矩阵和基因矩阵。它们不依赖网络，
  也是论文中使用的版本。
- GrapeTree 最小生成树：基于 cgMLST 谱或核心比对构建。
- 在线交互：iTOL、Microreact、Phandango、icytree。模块 11 只负责准备文件，上传由人完成。

## 11.1 合并注释表

`make_metadata.py` 把样本表与 `99_report/master_table.tsv` 合并为一张
`11_visualization/merged_metadata.csv`（species、ST、serotype、date、country、phenotype、
完整度以及各数据库命中数）。后续所有脚本都读这一张表，标签或分组要改时只改这里。

```bash
bash 11_visualization/11.1.build_metadata.sh
```

## 11.2 ggtree 静态树

`plot_trees.R` 读取 09 的核心 SNP 树、08 的核心基因树（可选）和 10 的时间树，对每棵树
输出矩形和环形两个版本，PDF 与 PNG 各一份，落在 `11_visualization/figures/`。叶节点按 species
着色，ST、country、phenotype、serotype 在有值时以堆叠色条呈现；时间树使用年份横轴。

```bash
Rscript 00_install/install_R_packages.R     # 仅一次：ape、ggtree、treeio、pheatmap 等
bash 11_visualization/11.2.plot_trees.sh
```

叶节点标签必须与样本 `id` 一致。如果元数据存在却画出了无注释的树，通常是上游树文件的叶名
（例如 snippy-core 的样本名）与样本表 id 不一致，应统一命名，而不是在图上手工修改。

## 11.3 GrapeTree 最小生成树

GrapeTree 以 chewBBACA 的 cgMLST 等位矩阵，或去重组后的核心比对为输入，构建 MSTreeV2 网络，
并复制一份配套元数据表用于上色：

```bash
bash 11_visualization/11.3.grapetree.sh
# 输出：11_visualization/grapetree/*.nwk 与 grapetree_metadata.csv
```

在 [GrapeTree 网页版](https://achtman-lab.github.io/GrapeTree)打开 Newick 与元数据表即可交互，
或本地运行 `grapetree --website`。暴发聚类通常用 cgMLST 网络；核心 SNP 网络用于与 09 的树互相印证。

## 11.4 iTOL 注释数据集

`make_itol_datasets.py` 在 `11_visualization/itol/` 生成 iTOL 文本文件：species、ST、country、
phenotype、serotype 的色条，以及各 abricate 数据库是否命中的二元轨。先在 [iTOL](https://itol.embl.de)
上传 Newick 树，再把这些文本文件拖到树上。注释轨较多时，iTOL 是最灵活的方案。

## 11.5 热图

`heatmaps.R` 输出三张聚类热图的 PDF 与 PNG：两两 SNP 距离矩阵、abricate 各库命中数、出现频率
最高的 40 个基因的“基因×样本”有无矩阵；行列侧边色条取自合并元数据。要指定 R 解释器时设置
`RSCRIPT=/path/to/Rscript`。

```bash
bash 11_visualization/11.5.heatmaps.sh
```

基因矩阵很大或需要与树精细对齐时，可用 ComplexHeatmap 替换 pheatmap；二者都由
`install_R_packages.R` 安装。

## 11.6 在线交互打包

`11.6.online_bundle.sh` 把树、合并元数据、iTOL 数据集、泛基因组基因有无表和 abricate 汇总
收集到 `11_visualization/online_bundle/`，全程不联网：

| 工具 | 上传内容 | 适用场景 |
| --- | --- | --- |
| [iTOL](https://itol.embl.de) | 树加 `itol/*.txt` | 注释密集、面向出版的树 |
| [Microreact](https://microreact.org) | Newick 加 `merged_metadata.csv` | 树+地图+时间轴，地图需另加经纬度列 |
| [Phandango](https://phandango.net) | 树加 `gene_presence_absence.csv` | 树与泛基因组对齐 |
| [GrapeTree](https://achtman-lab.github.io/GrapeTree) | MST Newick 加元数据 | cgMLST 暴发网络 |
| [icytree](https://icytree.org) | 单个树文件 | 快速查看，无需账号 |

## 工具地图

| 工具 | 作用 | 来源 |
| --- | --- | --- |
| ggtree / ggtreeExtra / treeio | R 带注释树与树格式读写 | [YuLab-SMU](https://github.com/YuLab-SMU/ggtree) |
| ape / phangorn | R 树处理与系统发育方法 | [ape](https://github.com/emmanuelparadis/ape) |
| GrapeTree | 最小生成树/NJ 网络 | [achtman-lab/GrapeTree](https://github.com/achtman-lab/GrapeTree) |
| pheatmap / ComplexHeatmap | 聚类矩阵热图 | [pheatmap](https://github.com/raivokolde/pheatmap) |
| FigTree | 桌面端树查看器 | [rambaut/figtree](https://github.com/rambaut/figtree) |
| iTOL / Microreact / Phandango / icytree | 在线交互查看器 | 见上方链接 |

静态图与交互图应讲述一致的结论。同一个变量在不同图中保持同一配色，并在每个图例中写明树的
来源（核心 SNP、核心基因或 cgMLST），避免把网络布局误读成带枝长的系统发育树。
