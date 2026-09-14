# Contributing to EasyIsolate

感谢参与。本仓库由可执行脚本（编号目录）与 guidebook（docs/）两部分组成。

## 提交规范

- 一个 PR 只解决一个问题，标题写清模块号，例如 `06: add Klebsiella oxytoca preset`。
- 所有脚本须能在 Linux / WSL2 / HPC 的 bash 下运行，顶部保持与现有脚本一致的
  `set -euo pipefail` 与 `PROJECT` 定位逻辑，不硬编码个人路径。
- 新增外部工具时，同步更新三处：对应编号脚本、`00_install/install_env.sh`、
  `docs/toolmap.md` 的工具对照行。
- 不改动工具产生的数值结果口径；参数变更需在脚本注释与 `CHANGELOG.md` 写明理由。

## 本地预览文档

```bash
pip install -r requirements-doc.txt
mkdocs serve        # 浏览器打开 http://127.0.0.1:8000
```

## 报告问题

提 issue 时请附上：平台（illumina/nanopore/pacbio/hybrid）、报错命令、完整日志、
对应软件版本（`tool --version`）。
