# 更新日志

完整变更见根目录 [CHANGELOG.md](https://github.com/LLQ95/EasyWGS/blob/main/CHANGELOG.md)。

## 0.4.0（2026-09-20）

示范面板新增 tier 4：为副溶血性弧菌、小肠结肠炎耶尔森菌、空肠/结肠弯曲菌、唐菖蒲伯克霍尔德菌、
肉毒梭菌五类专化病原各加入 3 株 accession 已核实的 Illumina 样本（共 15 株，面板扩至 44 株、
覆盖十类病原）。新增模块 04.5（FastANI 物种确认门控）、模块 06.4（基于 abricate 的自定义
毒素/表面/毒力位点筛查，含建库脚本与带来源的 curated 标记清单）、面向单物种比较模块的子集
拆分辅助脚本，以及中英双语“专化病原”指南页。

## 0.2.0（2026-09-14）

新增 11_visualization 模块（合并元数据、ggtree 静态树、GrapeTree 最小生成树、iTOL 数据集、
pheatmap 热图，以及面向 iTOL/Microreact/Phandango/GrapeTree/icytree 的离线打包）、R 包安装脚本、
可视化教程页与 README 工具分类。所有可执行脚本与配置改为纯英文，汇总总表列名改为英文。

## 0.1.0（2026-09-14）

搭建首个公开框架：编号化主流程覆盖二代 Illumina、三代 ONT/PacBio 与混合组装，
含双层去污染门控、分物种血清型、cgMLST、耐药毒力与可移动元件、泛基因组、核心
SNP 树与 TreeTime 时间树，并提供 MkDocs Material guidebook。
