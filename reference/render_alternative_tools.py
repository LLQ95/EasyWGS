#!/usr/bin/env python3
"""Regenerate the bilingual tool-lineage encyclopedia pages from data files.

Inputs  (do not edit the generated Markdown by hand):
  reference/tool_catalog.tsv  one row per tool, ordered by stage
  reference/catalog_text.tsv  all prose/headings/labels in English and Chinese
Outputs:
  docs/alternative-tools.md      English (default)
  docs/alternative-tools.zh.md   Chinese

This script intentionally contains ASCII only: every non-English string is
read from catalog_text.tsv so that repository scripts stay language-neutral.

Usage:  python reference/render_alternative_tools.py
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs")

STATUS_KEY = {"R": "stR", "A": "stA", "L": "stL"}


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.reader(fh, delimiter="\t"))


def load_text():
    text = {}
    for row in read_tsv(os.path.join(HERE, "catalog_text.tsv")):
        if not row or row[0] == "key":
            continue
        text[row[0]] = (row[1], row[2])
    return text


def load_tools():
    rows = []
    for row in csv.DictReader(
        open(os.path.join(HERE, "tool_catalog.tsv"), encoding="utf-8", newline=""),
        delimiter="\t",
    ):
        rows.append(row)
    return rows


def render(lang, text, tools):
    i = 0 if lang == "en" else 1

    def t(key):
        return text[key][i]

    out = [t("title"), "", t("p_intro"), "", t("h_legend"), "",
           t("l_rec"), t("l_alt"), t("l_leg"), "", t("l_lineage"), ""]

    order = []
    groups = {}
    for r in tools:
        o = int(r["order"])
        if o not in groups:
            groups[o] = []
            order.append(o)
        groups[o].append(r)

    headers = [t("th1"), t("th2"), t("th3"), t("th4"), t("th5")]
    role_col = "role_en" if lang == "en" else "role_zh"
    stage_col = "stage_en" if lang == "en" else "stage_zh"

    for o in order:
        grp = groups[o]
        out.append("## %d. %s" % (o, grp[0][stage_col]))
        out.append("")
        out.append("| " + " | ".join(headers) + " |")
        out.append("| " + " | ".join(["---"] * 5) + " |")
        for r in grp:
            status = t(STATUS_KEY[r["status"]])
            lineage = r["lineage"].strip() or "-"
            out.append("| %s | %s | %s | %s | %s |" % (
                r["tool"], status, lineage, r["platform"], r[role_col]))
        out.append("")

    out += [t("h_select"), "", t("p_select"), "", t("p_data"), ""]
    return "\n".join(out).rstrip() + "\n"


def main():
    text = load_text()
    tools = load_tools()
    targets = {
        "alternative-tools.md": render("en", text, tools),
        "alternative-tools.zh.md": render("zh", text, tools),
    }
    for name, content in targets.items():
        with open(os.path.join(DOCS, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
        print("wrote", name, len(content), "chars")
    en = targets["alternative-tools.md"]
    non_ascii = sorted({c for c in en if ord(c) > 127})
    print("English page non-ASCII characters:", non_ascii)
    print("tools:", len(tools), "stages:", len({r["order"] for r in tools}))


if __name__ == "__main__":
    main()
