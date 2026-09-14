#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
99_report/merge_results.py
Merge per-module, per-isolate results into one master table master_table.tsv:
MLST / serotype (Kleborate/ECTyper/SISTR) / CheckM2 / GUNC / assembly stats / abricate hit counts
Usage: python3 merge_results.py [easyWGS root], default = parent directory of this script
"""
import csv, glob, os, sys, collections

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "99_report", "master_table.tsv")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

def read_tsv(path, delim="\t"):
    with open(path, newline="", encoding="utf-8", errors="ignore") as fh:
        return list(csv.DictReader(fh, delimiter=delim))

def id_of(path):
    return os.path.basename(path).split(".")[0].replace("_R1", "")

master = collections.defaultdict(dict)

# Assembly statistics
f = os.path.join(ROOT, "03_assembly", "genome_stats.tsv")
if os.path.exists(f):
    for r in read_tsv(f):
        master[r.get("file","")].update({"length_bp": r.get("sum_len",""), "gc_percent": r.get("avg_gc","")})

# MLST (no header: file scheme ST alleles ...)
f = os.path.join(ROOT, "06_typing", "mlst", "pubmlst.tab")
if os.path.exists(f):
    for line in open(f):
        p = line.split()
        if len(p) >= 3:
            master[id_of(p[0])].update({"mlst_scheme": p[1], "ST": p[2]})

# CheckM2
f = os.path.join(ROOT, "04_asm_qc", "checkm2", "quality_report.tsv")
if os.path.exists(f):
    for r in read_tsv(f):
        master[r.get("Name","")].update({"completeness_pct": r.get("Completeness",""),
                                         "contamination_pct": r.get("Contamination","")})

# Kleborate merge (many columns; keep ST/clonal group/K/O loci/scores; header names vary by version)
f = os.path.join(ROOT, "06_typing", "serotype", "Kleborate_all.tsv")
if os.path.exists(f):
    rows = read_tsv(f)
    for r in rows:
        key = next((v for k,v in r.items() if k.lower()=="genome" or "assembly" in k.lower()), "")
        keep = {k: r[k] for k in r if k.lower() in
                ("st","clone","clonal group","k_locus","o_locus","o locus","k_type","o_type",
                 "resistance score","virulence score") or "locus" in k.lower()}
        master[id_of(key)].update({f"Kleborate/{k}": v for k,v in keep.items()})

# ECTyper
f = os.path.join(ROOT, "06_typing", "serotype", "ECTyper_all.csv")
if os.path.exists(f):
    for r in read_tsv(f, delim=","):
        name = r.get("Name","")
        master[id_of(name)].update({"O_type": r.get("O-type",""), "H_type": r.get("H-type",""),
                                    "ectyper_species": r.get("Species","")})

# Per-database abricate hit counts
for tab in glob.glob(os.path.join(ROOT, "07_amr_vf_mge", "abricate", "*.tab")):
    db = os.path.basename(tab).replace(".tab","")
    n = collections.Counter()
    for r in read_tsv(tab):
        n[id_of(r.get("#FILE",""))] += 1
    for k,v in n.items():
        master[k][f"hits_{db}"] = v

# Write out
allcols, seen = [], set()
for row in master.values():
    for k in row:
        if k not in seen: seen.add(k); allcols.append(k)
cols = ["sample_id"] + allcols
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", extrasaction="ignore")
    w.writeheader()
    for sid, row in sorted(master.items()):
        row["sample_id"] = sid; w.writerow(row)
print("Wrote", OUT, "with", len(master), "isolates")
