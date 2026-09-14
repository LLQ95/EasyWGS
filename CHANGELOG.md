# Changelog

本项目遵循语义化版本，日期使用 ISO 格式。

## [0.1.0] - 2026-09-14

### Added

- 编号化主流程 00–10、99，覆盖质控、双层去污染、组装、组装评估、注释、
  MLST、分物种血清型、cgMLST、耐药/毒力/可移动元件、泛基因组、核心 SNP
  系统发育与 TreeTime 时间树。
- 同时支持二代 Illumina、三代 ONT/PacBio 与 hybrid 混合组装：长读质控
  （porechop/NanoPlot/Filtlong）、Flye/Canu 组装、Racon 有限轮数校正、
  Medaka 抛光、Unicycler bold/SPAdes 混合与 Pilon 回填。
- MkDocs Material guidebook 框架与 Read the Docs 配置，含二代/三代工具对照。

### Notes

- 首个公开框架版本；数据库下载脚本与各模块参数仍在持续校验中。
