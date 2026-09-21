# 更新日志

完整变更见根目录 [CHANGELOG.md](https://github.com/LLQ95/EasyWGS/blob/main/CHANGELOG.md)。

## 0.7.0（2026-09-21）

本版本让流程在没有集群、不下载数据库的情况下也可测试、可复现。持续集成现在在每次推送与拉取请求时
运行两个作业：其一是静态检查，校验 shell、Python、R 语法，强制脚本与默认英文页面仅含英文，核对工具百科
的表头并确认自动生成页面为最新，随后严格构建 guidebook；其二是功能冒烟测试，在小规模、固定随机种子的
合成数据上运行真实的 fastp、参考比对、变异检测与去污染模块。去污染示例新增自包含的合成 spike-in：在装有
bwa/samtools 时使用与生产一致的比对引擎，否则使用内置的 k-mer 分类器，并以预期结果规则区分“尚未运行”
与“实测违例”。软件栈现由可移植环境清单、最小 CI 清单、导出逐机精确锁定的脚本、数据库在运行时挂载而非
内置的 Docker 镜像，以及面向 HPC 的 Apptainer/Singularity 定义共同描述，镜像发布到 GitHub Container
Registry。固定种子的降采样辅助脚本可在真实数据上快速冒烟；两篇中英双语指南页分别说明测试与容器配置、
以及在公共面板上的有序集群运行。需要大型数据库的步骤仍在真实面板上验证，而不放入持续集成。

## 0.6.0（2026-09-20）

新增跨域扩展性评估与中英双语指南页“超越细菌：病毒、真菌与益生菌”。该页给出以比对和共识为中心的
病毒轨道（SARS-CoV-2 用 iVar、Nextclade、Pangolin、UShER；HIV 用 HAPHPIPE/V-pipe、HIV-TRACE、
HyPhy、HIVdb；诺如病毒用 VADR 与 ORF1/ORF2 双分型），面向致病真菌的长读/混合真核轨道（AAFTF、
BUSCO、funannotate/BRAKER3、ITSx/UNITE、OrthoFinder、Control-FREEC 与 antiSMASH 真菌模式），
以及叠加在细菌轨道上的益生菌安全与有益性配置（EFSA QPS/FEEDAP、获得性耐药可转移性检查、BAGEL4）；
并提供共享核心表、韦恩图与“阶段 × 类群”矩阵图（EasyWGS_domains）以及分阶段路线。工具百科由
235 条扩至 276 条、覆盖 31 个阶段（新增第 26–31 阶段），生态图与中英 README 同步重生成。本版本
仅落地可行性评估与工具选型；可运行的病毒/真菌模块待公共数据面板验证后按路线推进。

## 0.5.0（2026-09-20）

示范面板新增 tier 5：为金黄色葡萄球菌、阪崎克罗诺杆菌、痢疾志贺菌、霍乱弧菌、炭疽杆菌、
蜡样芽胞杆菌、鼻疽伯克霍尔德菌、结核分枝杆菌、羊种布鲁菌九类病原各加入 3 株 accession 已核实的
Illumina 样本（共 27 株，面板扩至 71 株、覆盖 19 类病原）。九类复用 FastANI 门控（04.5）、
MLST（06.1）与自定义标记筛查（06.4）；模块 06.2 补充 spaTyper/SCCmecFinder、BTyper3、
TB-Profiler/Mykrobe 等可选专用工具说明。新增 47 个 curated 标记、预期结果规则 P24–P39、专用工具
条目，以及 CheckM2/eggNOG/Bakta/GUNC 共享库路径与 CheckM2 手动 setdblocation 说明。结核与布鲁菌
没有七基因 MLST scheme，改用 FastANI 加专门谱系工具；高后果病原仅覆盖公开数据的 in silico 教学。

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
