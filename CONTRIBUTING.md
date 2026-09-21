# Contributing to EasyWGS

Thanks for your interest in improving EasyWGS. The repository has two parts that
should stay in sync: the executable, numbered-directory scripts and the MkDocs
guidebook under `docs/`.

The full contributor guide, including the coding conventions and the steps for
adding a new tool or a new pathogen profile, is maintained in the guidebook:

- English: <https://easywgs.readthedocs.io/en/latest/contributing/>
- Chinese: <https://easywgs.readthedocs.io/zh/latest/contributing/>

The source files are `docs/contributing.md` (English, default) and
`docs/contributing.zh.md` (Chinese).

## Short checklist

- Keep one pull request focused on one problem and name the affected module in
  the title, for example `06: add Klebsiella oxytoca preset`.
- Scripts must run under bash on Linux, WSL2 or an HPC cluster. Keep the
  `set -euo pipefail` header and the `PROJECT` resolution used by the existing
  scripts, and do not hard-code personal paths.
- Scripts are English-only (ASCII). User-facing prose for the guidebook is added
  in English first, with a Chinese counterpart in a `.zh.md` page.
- When adding an external tool, update the numbered script,
  `00_install/install_env.sh` (or the matching environment file), and
  `reference/tool_catalog.tsv`, then rerun
  `python reference/render_alternative_tools.py`.
- Do not change the numerical output conventions of a tool. When a parameter
  changes, record the reason in the script comments and in `CHANGELOG.md`.
- Before opening a pull request, run `python tests/run_static_checks.py` and,
  where the lightweight bioinformatics tools are installed,
  `bash tests/run_smoke.sh`. Continuous integration runs both.

## Preview the guidebook locally

```bash
pip install -r requirements-doc.txt
mkdocs serve        # then open http://127.0.0.1:8000
```

## Reporting an issue

Please include the platform (illumina, nanopore, pacbio or hybrid), the exact
command that failed, the full log, and the tool versions reported by
`tool --version`.
