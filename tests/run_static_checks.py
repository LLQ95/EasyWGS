#!/usr/bin/env python3
"""Repository-wide static checks for EasyWGS, with no third-party dependencies.

Run:  python tests/run_static_checks.py

Checks:
  1. every shell script passes `bash -n` syntax validation (skipped without bash)
  2. every Python file compiles
  3. every R script parses (skipped without Rscript)
  4. scripts (*.sh/*.py/*.R) contain ASCII only, and English Markdown contains
     no CJK characters (Chinese lives only in *.zh.md / README.zh-CN.md)
  5. reference/tool_catalog.tsv has the expected schema and valid status codes
  6. the generated encyclopedia pages are up to date (render is idempotent)

A skipped optional tool is not a failure. The exit code is non-zero if any real
check fails, so this can gate continuous integration.
"""
import csv
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PRUNE_DIRS = {".git", "site", "__pycache__", "node_modules", ".mypy_cache",
              "results", "work", "generated", "00_rawdata", "ref", "clean",
              "run", "trim", "locks"}
def _cjk_pattern():
    # CJK punctuation, extension A, unified ideographs and compatibility
    # ideographs; built from code points so this checker stays ASCII-only.
    runs = ((0x3000, 0x303F), (0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF))
    chars = "".join(chr(c) for lo, hi in runs for c in range(lo, hi + 1))
    return re.compile("[" + chars + "]")


CJK = _cjk_pattern()
LANG_LINK = re.compile(r"\[[^\]]*\]\([^)]*zh[^)]*\)", re.IGNORECASE)
REPO_RE = re.compile(r"^[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+$")
VALID_STATUS = {"R", "A", "L"}
EXPECTED_COLUMNS = ["order", "stage_en", "stage_zh", "tool", "status",
                    "lineage", "platform", "role_en", "role_zh", "repo"]

failures, skipped = [], []


def fail(msg):
    failures.append(msg)
    print("  FAIL " + msg)


def info(msg):
    print("  " + msg)


def walk_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in PRUNE_DIRS]
        for fn in filenames:
            yield os.path.join(dirpath, fn)


def check_scripts_and_encoding(files):
    print("[1-4] syntax and encoding")
    bash = shutil.which("bash")
    rscript = shutil.which("Rscript") or shutil.which("Rscript.exe")
    n_sh = n_py = n_r = n_md = 0
    for path in files:
        rel = os.path.relpath(path, ROOT)
        low = path.lower()
        if low.endswith(".sh"):
            n_sh += 1
            if bash:
                p = subprocess.run([bash, "-n", path], capture_output=True, text=True)
                if p.returncode != 0:
                    fail(f"bash -n: {rel}\n{p.stderr.strip()}")
            _require_ascii(path, rel)
        elif low.endswith(".py"):
            n_py += 1
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            try:
                compile(src, rel, "exec")
            except SyntaxError as exc:
                fail(f"python syntax: {rel}: {exc}")
            _require_ascii(path, rel)
        elif low.endswith(".r") or low.endswith(".rscript"):
            n_r += 1
            _require_ascii(path, rel)
            if rscript:
                p = subprocess.run([rscript, "-e", f"parse('{rel.replace(os.sep, '/')}')"],
                                   cwd=ROOT, capture_output=True, text=True)
                if p.returncode != 0:
                    fail(f"R parse: {rel}\n{p.stderr.strip()[:400]}")
        elif low.endswith(".md"):
            base = os.path.basename(path)
            if ".zh" in base or "zh-cn" in base.lower():
                continue
            n_md += 1
            with open(path, encoding="utf-8") as fh:
                for i, line in enumerate(fh, 1):
                    # The only Chinese allowed in a default-English page is the
                    # visible label of the language-switch link to a .zh page.
                    if CJK.search(LANG_LINK.sub("", line)):
                        fail(f"CJK in English doc {rel}:{i}; move Chinese to a .zh.md page")
                        break
    if not bash:
        skipped.append("bash -n (bash not found)")
    if not rscript:
        skipped.append("R parse (Rscript not found)")
    info(f"checked {n_sh} shell, {n_py} python, {n_r} R scripts, {n_md} English markdown files")


def _require_ascii(path, rel):
    with open(path, encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            try:
                line.encode("ascii")
            except UnicodeEncodeError:
                ch = next(c for c in line if ord(c) > 127)
                fail(f"non-ASCII in script {rel}:{i} (U+{ord(ch):04X}); keep scripts English-only")
                return


def check_catalog():
    print("[5] tool catalog schema")
    path = os.path.join(ROOT, "reference", "tool_catalog.tsv")
    if not os.path.exists(path):
        fail("reference/tool_catalog.tsv missing")
        return
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh, delimiter="\t")
        header = next(reader)
        if header != EXPECTED_COLUMNS:
            fail(f"catalog columns changed: {header}")
            return
        n = 0
        for ln, row in enumerate(reader, 2):
            if not row or (len(row) == 1 and row[0] == ""):
                continue
            if len(row) != len(EXPECTED_COLUMNS):
                fail(f"catalog line {ln}: expected {len(EXPECTED_COLUMNS)} fields, got {len(row)}")
                continue
            order, stage_en, _zh, tool, status, _lin, _plat, role_en, _rz, repo = row
            if not tool.strip():
                fail(f"catalog line {ln}: empty tool name")
            if status not in VALID_STATUS:
                fail(f"catalog line {ln} ({tool}): status '{status}' not in R/A/L")
            r = repo.strip()
            if r and not (REPO_RE.match(r) or r.startswith(("http://", "https://", "git@"))):
                fail(f"catalog line {ln} ({tool}): repo '{r}' is neither owner/name nor a URL")
            n += 1
    info(f"{n} tools catalogued")


def check_render_idempotent():
    print("[6] generated encyclopedia pages are up to date")
    git = shutil.which("git")
    script = os.path.join(ROOT, "reference", "render_alternative_tools.py")
    if not git:
        skipped.append("render idempotence (git not found)")
        return
    before = subprocess.run([git, "-C", ROOT, "rev-parse", "--show-toplevel"],
                            capture_output=True, text=True)
    if before.returncode != 0:
        skipped.append("render idempotence (not a git work tree)")
        return
    p = subprocess.run([sys.executable, script], capture_output=True, text=True)
    if p.returncode != 0:
        fail("render_alternative_tools.py failed:\n" + p.stderr.strip()[:500])
        return
    diff = subprocess.run(
        [git, "-C", ROOT, "diff", "--name-only", "--",
         "docs/alternative-tools.md", "docs/alternative-tools.zh.md"],
        capture_output=True, text=True)
    changed = [d for d in diff.stdout.splitlines() if d.strip()]
    if changed:
        fail("generated pages are stale; rerun reference/render_alternative_tools.py and commit: "
             + ", ".join(changed))
    else:
        info("generated encyclopedia pages are current")


def main():
    files = list(walk_files())
    check_scripts_and_encoding(files)
    check_catalog()
    check_render_idempotent()
    print("")
    if skipped:
        print("skipped (optional): " + "; ".join(sorted(set(skipped))))
    if failures:
        print(f"\nSTATIC CHECKS FAILED: {len(failures)} problem(s)")
        return 1
    print("STATIC CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
