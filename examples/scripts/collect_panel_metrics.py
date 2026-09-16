#!/usr/bin/env python3
"""Collect headline metrics from a real EasyWGS panel run.

This never invents values. It joins the curated panel metadata with the files
produced by the numbered modules; any module that has not run is recorded as
NA rather than estimated. Outputs in examples/results/:
  panel_metrics.tsv   one row per isolate (assembly, QC, typing, resistance)
  collection_stats.tsv collection-level summaries (pangenome, SNPs, dating, GWAS)
  panel_summary.md    the same numbers in prose form, for the manuscript
"""
import csv, glob, os, sys, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PANEL = os.path.join(ROOT, "examples", "panel.tsv")
RES = os.path.join(ROOT, "examples", "results")

def tsv(path, delim="\t"):
    try:
        with open(path, newline="", encoding="utf-8", errors="ignore") as f:
            return list(csv.DictReader(f, delimiter=delim))
    except Exception:
        return []

def panel_rows(tier):
    rows, header = [], None
    with open(PANEL, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            vals = line.split("\t")
            if header is None:
                header = vals
            elif int(vals[header.index("tier")]) <= tier:
                rows.append(dict(zip(header, vals)))
    return rows

def first(pattern):
    g = sorted(glob.glob(os.path.join(ROOT, pattern), recursive=True))
    return g[0] if g else ""

def fnum(x):
    try:
        return f"{float(x):.2f}"
    except Exception:
        return "NA"

def main():
    tier = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 3
    os.makedirs(RES, exist_ok=True)
    panel = panel_rows(tier)

    stats = {os.path.basename(r.get("file", "")).split(".")[0]: r
             for r in tsv("03_assembly/genome_stats.tsv")}
    master = {}
    for r in tsv("99_report/master_table.tsv"):
        master[r.get("sample_id", "")] = r
    gunc = {}
    g = first("04_asm_qc/**/*.maxCSS_level.tsv")
    for r in tsv(g):
        key = os.path.basename(r.get("genome", "")).split(".")[0]
        gunc[key] = r.get("pass_GUNC", "NA")

    cols = ["sample_id", "group", "species_code", "platform", "country", "year",
            "num_contigs", "length_bp", "N50", "gc_percent",
            "completeness_pct", "contamination_pct", "GUNC_pass",
            "mlst_scheme", "ST", "O_type", "H_type"]
    per = []
    for p in panel:
        sid = p["id"]
        st = stats.get(sid, {})
        mt = master.get(sid, {})
        per.append({
            "sample_id": sid, "group": p["group"], "species_code": p["species_code"],
            "platform": p["platform"], "country": p["country"].split(":")[0],
            "year": p["date"][:4],
            "num_contigs": st.get("num_seqs", "NA"), "length_bp": st.get("sum_len", "NA"),
            "N50": st.get("N50", "NA"), "gc_percent": fnum(st.get("avg_gc", "")),
            "completeness_pct": mt.get("completeness_pct", "NA"),
            "contamination_pct": mt.get("contamination_pct", "NA"),
            "GUNC_pass": gunc.get(sid, "NA"),
            "mlst_scheme": mt.get("mlst_scheme", "NA"), "ST": mt.get("ST", "NA"),
            "O_type": mt.get("O_type", "NA"), "H_type": mt.get("H_type", "NA")})
    with open(os.path.join(RES, "panel_metrics.tsv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t", extrasaction="ignore")
        w.writeheader(); w.writerows(per)

    cs = []
    def add(k, v): cs.append((k, str(v)))
    add("panel_tier", tier)
    add("n_samples", len(panel))
    for grp in sorted({p["group"] for p in panel}):
        add(f"n_{grp}", sum(1 for p in panel if p["group"] == grp))
    add("n_hybrid", sum(1 for p in panel if p["platform"] == "hybrid"))

    comp = [float(r["completeness_pct"]) for r in per
            if r["completeness_pct"] not in ("NA", "")]
    cont = [float(r["contamination_pct"]) for r in per
            if r["contamination_pct"] not in ("NA", "")]
    if comp: add("completeness_median", f"{statistics.median(comp):.2f}")
    if cont: add("contamination_max", f"{max(cont):.2f}")

    # Pangenome (Panaroo): "No. isolates" column distinguishes core/accessory
    pg = first("08_pangenome/**/gene_presence_absence.csv")
    if pg:
        rows = list(csv.reader(open(pg, encoding="utf-8", errors="ignore")))
        hdr, body = rows[0], rows[1:]
        sample_cols = [i for i, h in enumerate(hdr) if i >= 14]
        n = len(sample_cols) or 1
        ni = hdr.index("No. isolates") if "No. isolates" in hdr else None
        core = sing = 0
        for row in body:
            try: k = int(row[ni]) if ni is not None else sum(1 for i in sample_cols if row[i])
            except ValueError: k = 0
            if k == n: core += 1
            if k == 1: sing += 1
        add("pangenome_gene_clusters", len(body)); add("pangenome_core", core)
        add("pangenome_singleton", sing); add("pangenome_n_genomes", n)

    # Core-SNP alignment and pairwise distances
    aln = first("09_phylogeny/**/core.aln") or first("09_phylogeny/**/*.aln")
    if aln:
        try:
            seqs = {}
            name = None
            for line in open(aln, encoding="utf-8", errors="ignore"):
                if line.startswith(">"):
                    name = line[1:].strip().split()[0]; seqs[name] = ""
                elif name is not None:
                    seqs[name] += line.strip()
            add("core_aln_sequences", len(seqs))
            if seqs: add("core_aln_length_bp", len(next(iter(seqs.values()))))
        except Exception:
            pass
    dm = first("09_phylogeny/**/*dist*.tsv") or first("09_phylogeny/**/*dist*.tab")
    if dm:
        rows = tsv(dm)
        vals = []
        for i, r in enumerate(rows):
            for j, c in enumerate(list(r.values())[1:]):
                if j > i:
                    try: vals.append(float(c))
                    except ValueError: pass
        if vals:
            add("snp_distance_min", f"{min(vals):.0f}")
            add("snp_distance_max", f"{max(vals):.0f}")

    # Time tree (TreeTime writes a clock rate into its results directory)
    rate = ""
    for pat in ["10_timetree/**/results/*.txt", "10_timetree/**/*.log",
                "10_timetime/**/results/*dates.tsv"]:
        for path in glob.glob(os.path.join(ROOT, pat), recursive=True):
            for line in open(path, encoding="utf-8", errors="ignore"):
                if "clock rate" in line.lower() or "rate:" in line.lower():
                    rate = line.strip()[:120]; break
            if rate: break
        if rate: break
    add("timetree_rate_line", rate or "NA")

    # GWAS smallest p value / BH-significant hits (pyseer output)
    py = first("13_gwas/**/*.pyseer*.txt") or first("13_gwas/**/pyseer*.tsv")
    if py:
        rows = tsv(py)
        if rows:
            pcol = next((c for c in rows[0] if c.lower() in ("pvalue", "p-value", "p")), "")
            bhcol = next((c for c in rows[0] if "BH" in c or "adjust" in c.lower()), "")
            if pcol:
                pv = [float(r[pcol]) for r in rows if r.get(pcol, "").replace(".", "", 1).isdigit()]
                if pv: add("gwas_min_pvalue", f"{min(pv):.2e}")
            if bhcol:
                add("gwas_BH_sig", sum(1 for r in rows if _safe_lt(r.get(bhcol), 0.05)))

    with open(os.path.join(RES, "collection_stats.tsv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t"); w.writerow(["metric", "value"]); w.writerows(cs)

    lines = ["# EasyWGS panel run summary (auto-generated; NA = module not run)", ""]
    for k, v in cs:
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("Per-isolate values are in panel_metrics.tsv. Replace NA by rerunning the "
                 "missing numbered module before quoting any number in the manuscript.")
    open(os.path.join(RES, "panel_summary.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("wrote examples/results/panel_metrics.tsv, collection_stats.tsv, panel_summary.md")

def _safe_lt(x, t):
    try: return float(x) < t
    except Exception: return False

if __name__ == "__main__":
    main()
