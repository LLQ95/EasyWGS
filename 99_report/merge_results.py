#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
99_report/merge_results.py
把各模块逐样本结果按样本ID合并成一张总表 master_table.tsv：
MLST / 血清型(Kleborate/ECTyper/Sistr) / CheckM2 / GUNC / 组装统计 / abricate命中数
用法：python3 merge_results.py [EasyIsolate根目录]，默认脚本上级目录
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

# 组装统计
f = os.path.join(ROOT, "03_assembly", "genome_stats.tsv")
if os.path.exists(f):
    for r in read_tsv(f):
        master[r.get("file","")].update({"长度": r.get("sum_len",""), "GC%": r.get("avg_gc","")})

# MLST（mlst 无表头：file scheme ST alleles...）
f = os.path.join(ROOT, "06_typing", "mlst", "pubmlst.tab")
if os.path.exists(f):
    for line in open(f):
        p = line.split()
        if len(p) >= 3:
            master[id_of(p[0])].update({"MLST方案": p[1], "ST": p[2]})

# CheckM2
f = os.path.join(ROOT, "04_asm_qc", "checkm2", "quality_report.tsv")
if os.path.exists(f):
    for r in read_tsv(f):
        master[r.get("Name","")].update({"完整度%": r.get("Completeness",""),
                                          "污染度%": r.get("Contamination","")})

# Kleborate 汇总（列较多，取 ST/克隆群/K/O 抗原/耐药毒力分；表头列名随版本）
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
        master[id_of(name)].update({"O抗原": r.get("O-type",""), "H抗原": r.get("H-type",""),
                                    "ECTyper物种": r.get("Species","")})

# 各 abricate 库命中数
for tab in glob.glob(os.path.join(ROOT, "07_amr_vf_mge", "abricate", "*.tab")):
    db = os.path.basename(tab).replace(".tab","")
    n = collections.Counter()
    for r in read_tsv(tab):
        n[id_of(r.get("#FILE",""))] += 1
    for k,v in n.items():
        master[k][f"命中数/{db}"] = v

# 写出
allcols, seen = [], set()
for row in master.values():
    for k in row:
        if k not in seen: seen.add(k); allcols.append(k)
cols = ["样本ID"] + allcols
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", extrasaction="ignore")
    w.writeheader()
    for sid, row in sorted(master.items()):
        row["样本ID"] = sid; w.writerow(row)
print("已写出", OUT, "样本数", len(master))
