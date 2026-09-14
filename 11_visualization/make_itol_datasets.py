#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
11_visualization/make_itol_datasets.py
Generate iTOL (https://itol.embl.de) annotation datasets from merged_metadata.csv
and the abricate summary table. Upload a Newick/Nexus tree to iTOL, then drag the
generated text files onto the tree to add color strips and a binary AMR track.

Usage: python3 make_itol_datasets.py [easyWGS root]
Only the Python standard library is required.
"""
import csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(HERE)
OUTD = os.path.join(HERE, "itol")
os.makedirs(OUTD, exist_ok=True)

PALETTE = ["#4e79a7","#f28e2b","#59a14f","#e15759","#76b7b2","#edc948",
           "#b07aa1","#ff9da7","#9c755f","#bab0ac","#1f77b4","#ff7f0e",
           "#2ca02c","#d62728","#9467bd","#8c564b","#e377c2","#7f7f7f",
           "#bcbd22","#17becf"]
BIN_COLORS = ["#e41a1c","#377eb8","#4daf4a","#984ea3","#ff7f00",
              "#ffff33","#a65628","#f781bf","#66c2a5","#fc8d62"]

def load_csv(path, delim=","):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8", errors="ignore") as fh:
        return list(csv.DictReader(fh, delimiter=delim))

def color_map(values):
    uniq = sorted({v for v in values if v not in ("", "NA", None)})
    return {v: PALETTE[i % len(PALETTE)] for i, v in enumerate(uniq)}, uniq

def write_colorstrip(field, label, records, outdir):
    pairs = [(r["id"], (r.get(field) or "").strip()) for r in records if r.get("id")]
    pairs = [(i, v) for i, v in pairs if v not in ("", "NA")]
    if not pairs:
        return
    cmap, uniq = color_map([v for _, v in pairs])
    lines = ["DATASET_COLORSTRIP", "SEPARATOR COMMA",
             f"DATASET_LABEL,{label}", "COLOR,#cccccc",
             f"FIELD_LABELS,{label}", f"LEGEND_TITLE,{label}",
             "LEGEND_SHAPES," + ",".join("1" for _ in uniq),
             "LEGEND_COLORS," + ",".join(cmap[v] for v in uniq),
             "LEGEND_LABELS," + ",".join(uniq),
             "STRIP_WIDTH,40", "BORDER_WIDTH,0.5", "DATA"]
    for sid, v in pairs:
        lines.append(f"{sid},{cmap[v]},{v}")
    path = os.path.join(outdir, f"itol_colorstrip_{field}.txt")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"[done] {path}")

def isolate_id(raw):
    base = os.path.basename(raw or "")
    return base.replace(".fasta", "").replace(".fa", "").replace("_R1", "")

def write_binary(records, outdir):
    # abricate --summary: first column #FILE, remaining columns are per-DB hit counts
    summ = os.path.join(ROOT, "07_amr_vf_mge", "abricate", "summary.tab")
    if not os.path.exists(summ):
        print("[info] no abricate summary.tab; skip binary AMR track")
        return
    with open(summ, newline="", encoding="utf-8", errors="ignore") as fh:
        srows = list(csv.reader(fh, delimiter="\t"))
    if len(srows) < 2:
        return
    header = [h.strip() for h in srows[0]]
    dbs = header[1:]
    present = {r["id"]: {} for r in records if r.get("id")}
    for row in srows[1:]:
        if not row:
            continue
        sid = isolate_id(row[0])
        vec = present.setdefault(sid, {})
        for j, db in enumerate(dbs):
            try:
                vec[db] = 1 if int(float(row[j + 1] if j + 1 < len(row) else 0)) > 0 else 0
            except ValueError:
                vec[db] = 0
    if not dbs:
        return
    lines = ["DATASET_BINARY", "SEPARATOR COMMA",
             "DATASET_LABEL,Abricate DB hits", "COLOR,#000000",
             "FIELD_LABELS," + ",".join(dbs),
             "FIELD_COLORS," + ",".join(BIN_COLORS[i % len(BIN_COLORS)] for i in range(len(dbs))),
             "FIELD_SHAPES," + ",".join("1" for _ in dbs),
             "LEGEND_TITLE,Abricate DB hits",
             "LEGEND_SHAPES," + ",".join("1" for _ in dbs),
             "LEGEND_COLORS," + ",".join(BIN_COLORS[i % len(BIN_COLORS)] for i in range(len(dbs))),
             "LEGEND_LABELS," + ",".join(dbs),
             "DASHED_LINES,1", "BORDER_WIDTH,0.5", "DATA"]
    for sid, vec in present.items():
        lines.append(",".join([sid] + [str(vec.get(db, 0)) for db in dbs]))
    path = os.path.join(outdir, "itol_binary_abricate.txt")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"[done] {path}")

def main():
    meta = load_csv(os.path.join(HERE, "merged_metadata.csv"))
    if not meta:
        print("[warn] merged_metadata.csv missing; run 11.1.build_metadata.sh first")
        return
    for field, label in (("species", "Species"), ("ST", "ST"),
                         ("country", "Country"), ("phenotype", "Phenotype"),
                         ("serotype", "Serotype")):
        write_colorstrip(field, label, meta, OUTD)
    write_binary(meta, OUTD)
    print(f"[done] iTOL datasets are in {OUTD}; drag them onto a tree at https://itol.embl.de")

if __name__ == "__main__":
    main()
