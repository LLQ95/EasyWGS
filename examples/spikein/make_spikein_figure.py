#!/usr/bin/env python3
"""Render the controlled decontamination spike-in figure (manuscript Fig. 4).

Reads examples/spikein/results/spikein_metrics.tsv and draws four panels:
residual contaminant fraction and target retention after read-level cleaning,
and CheckM2 contamination/completeness of baseline, spiked-10% and cleaned-10%
assemblies. Panels whose module has not run are marked rather than estimated.
"""
import csv, os, shutil
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RES = os.path.join(HERE, "results")
MET = os.path.join(RES, "spikein_metrics.tsv")
CONTAMS = ["phix", "klebsiella"]
COLORS = {"phix": "#2c7fb8", "klebsiella": "#d95f0e"}

def load():
    d = {}
    if not os.path.exists(MET):
        return d
    for r in csv.DictReader(open(MET), delimiter="\t"):
        try: v = float(r["value"])
        except ValueError: v = None
        d[(r["contaminant"], float(r["spike_pct"]), r["condition"], r["metric"])] = v
    return d

def get(d, *k):
    return d.get(k, None)

def empty(ax, title):
    ax.text(0.5, 0.5, "not available until the spike-in run completes",
            ha="center", va="center", transform=ax.transAxes, fontsize=9)
    ax.set_title(title, fontsize=11)

def main():
    d = load()
    fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
    levels = [0.01, 0.05, 0.10]

    ax = axes[0][0]
    any_pt = False
    for c in CONTAMS:
        xs_s, ys_s, xs_c, ys_c = [], [], [], []
        for lv in levels:
            ts = get(d, c, lv, "spiked", "target_pairs")
            cs = get(d, c, lv, "spiked", "contaminant_pairs")
            tc = get(d, c, lv, "cleaned", "target_pairs")
            cc = get(d, c, lv, "cleaned", "contaminant_pairs")
            if ts is not None and cs is not None and ts + cs > 0:
                xs_s.append(lv * 100); ys_s.append(100 * cs / (ts + cs)); any_pt = True
            if tc is not None and cc is not None and tc + cc > 0:
                xs_c.append(lv * 100); ys_c.append(100 * cc / (tc + cc)); any_pt = True
        if xs_s: ax.plot(xs_s, ys_s, "o--", color=COLORS[c], alpha=0.5, label=f"{c} spiked")
        if xs_c: ax.plot(xs_c, ys_c, "o-", color=COLORS[c], label=f"{c} cleaned")
    if any_pt:
        ax.set_xlabel("spiked contaminant (%)"); ax.set_ylabel("residual contaminant reads (%)")
        ax.legend(fontsize=8); ax.set_title("A. Read-level contaminant removal", fontsize=11)
    else: empty(ax, "A. Read-level contaminant removal")

    ax = axes[0][1]
    any_pt = False
    for c in CONTAMS:
        xs, ys = [], []
        for lv in levels:
            ts = get(d, c, lv, "spiked", "target_pairs")
            tc = get(d, c, lv, "cleaned", "target_pairs")
            if ts and tc: xs.append(lv * 100); ys.append(100 * tc / ts); any_pt = True
        if xs: ax.plot(xs, ys, "o-", color=COLORS[c], label=c)
    if any_pt:
        ax.set_xlabel("spiked contaminant (%)"); ax.set_ylabel("target reads retained (%)")
        ax.set_ylim(0, 105); ax.legend(fontsize=8)
        ax.set_title("B. Target read retention after cleaning", fontsize=11)
    else: empty(ax, "B. Target read retention after cleaning")

    for ax, metric, ylab, title in (
            (axes[1][0], "checkm2_contamination", "contamination (%)",
             "C. Assembly contamination at 10% spike"),
            (axes[1][1], "checkm2_completeness", "completeness (%)",
             "D. Assembly completeness at 10% spike")):
        labels, vals, cols = [], [], []
        bv = get(d, "none", 0.0, "baseline", metric)
        if bv is not None: labels.append("baseline"); vals.append(bv); cols.append("#7f7f7f")
        for c in CONTAMS:
            for cond, mk in (("spiked", 0.6), ("cleaned", 0.9)):
                v = get(d, c, 0.10, cond, metric)
                if v is not None:
                    labels.append(f"{c}\n{cond}"); vals.append(v)
                    cols.append(COLORS[c] if cond == "cleaned" else "#bdbdbd")
        if vals:
            ax.bar(range(len(vals)), vals, color=cols)
            ax.set_xticks(range(len(vals))); ax.set_xticklabels(labels, fontsize=7)
            ax.set_ylabel(ylab); ax.set_title(title, fontsize=11)
        else:
            empty(ax, title)

    fig.tight_layout()
    os.makedirs(RES, exist_ok=True)
    for ext in ("png", "pdf", "svg"):
        out = os.path.join(RES, f"Fig_spikein.{ext}")
        fig.savefig(out, dpi=300, bbox_inches="tight")
    print("wrote Fig_spikein.{png,pdf,svg} in", os.path.relpath(RES))

    # Publish a version-controlled copy alongside the other manuscript figures
    # only when real metrics exist, never the all-panels-empty placeholder.
    if d:
        for dest_dir in (os.path.join(ROOT, "figures"),
                         os.path.join(ROOT, "docs", "assets")):
            os.makedirs(dest_dir, exist_ok=True)
            for ext in ("png", "pdf", "svg"):
                src = os.path.join(RES, f"Fig_spikein.{ext}")
                dst = os.path.join(dest_dir, f"EasyWGS_spikein.{ext}")
                shutil.copyfile(src, dst)
        print("copied EasyWGS_spikein.{png,pdf,svg} to figures/ and docs/assets/")

if __name__ == "__main__":
    main()
