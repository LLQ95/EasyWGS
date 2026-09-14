#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
11_visualization/make_metadata.py
Merge the samplesheet and 99_report/master_table.tsv into one tidy annotation
table (11_visualization/merged_metadata.csv) shared by every visualization step.

Usage: python3 make_metadata.py [EasyIsolate root]   (default = parent of this dir)
Only the Python standard library is required.
"""
import csv, glob, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(HERE)
CFG = os.path.join(ROOT, "config")
OUT = os.path.join(HERE, "merged_metadata.csv")

# --- locate the active samplesheet (my_samples.csv first, then the template) ---
sheet = os.path.join(CFG, "my_samples.csv")
if not os.path.exists(sheet):
    sheet = os.path.join(CFG, "samplesheet.csv")

rows = []
if os.path.exists(sheet):
    with open(sheet, newline="", encoding="utf-8", errors="ignore") as fh:
        clean = (ln for ln in fh if not ln.lstrip().startswith("#"))
        rows = list(csv.DictReader(clean))
else:
    print("[warn] no samplesheet found under config/; metadata will be empty")

# --- master table produced by 99_report/merge_results.py ---
master = {}
mpath = os.path.join(ROOT, "99_report", "master_table.tsv")
if os.path.exists(mpath):
    with open(mpath, newline="", encoding="utf-8", errors="ignore") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            master[r.get("sample_id", "")] = r

FIXED = ["id", "platform", "species", "ST", "mlst_scheme", "serotype",
         "date", "country", "phenotype", "length_bp", "gc_percent",
         "completeness_pct", "contamination_pct"]

def serotype_of(m):
    o = m.get("O_type", "") or ""
    h = m.get("H_type", "") or ""
    oh = (o + ":" + h).strip(":")
    if oh:
        return oh
    for k, v in m.items():
        if k.lower().endswith(("k_type", "o_type")) and v:
            return v
    return ""

records, extra_cols = [], []
for r in rows:
    sid = r.get("id", "").strip()
    if not sid:
        continue
    m = master.get(sid, {})
    rec = {
        "id": sid,
        "platform": r.get("platform", ""),
        "species": r.get("species", ""),
        "ST": m.get("ST", ""),
        "mlst_scheme": m.get("mlst_scheme", ""),
        "serotype": serotype_of(m),
        "date": r.get("date", ""),
        "country": r.get("country", ""),
        "phenotype": r.get("phenotype", ""),
        "length_bp": m.get("length_bp", ""),
        "gc_percent": m.get("gc_percent", ""),
        "completeness_pct": m.get("completeness_pct", ""),
        "contamination_pct": m.get("contamination_pct", ""),
    }
    # keep dynamic abricate hit-count columns for completeness
    for k, v in m.items():
        if k.startswith("hits_"):
            rec[k] = v
            if k not in extra_cols:
                extra_cols.append(k)
    records.append(rec)

cols = FIXED + extra_cols
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for rec in records:
        w.writerow(rec)

print(f"[done] wrote {OUT} with {len(records)} isolates; columns: {len(cols)}")
