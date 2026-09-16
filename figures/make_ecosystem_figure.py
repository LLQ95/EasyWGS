#!/usr/bin/env python3
"""Fig. 2: EasyWGS software, platform and database ecosystem.

Data-driven from reference/tool_catalog.tsv (one row per tool) and the install
scripts, so the figure is regenerated whenever the catalogue changes. Status
follows the catalogue: R = recommended default, A = maintained alternative,
L = legacy/superseded tool retained as an alternative choice.
Outputs figures/EasyWGS_ecosystem.{svg,pdf,png} and copies into docs/assets/.
"""
import csv, os, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CAT = os.path.join(ROOT, "reference", "tool_catalog.tsv")
INSTALL = os.path.join(ROOT, "00_install", "install_env.sh")
FIG = os.path.join(ROOT, "figures")
DOCS_ASSETS = os.path.join(ROOT, "docs", "assets")

C_R, C_A, C_L = "#2166ac", "#92c5de", "#bdbdbd"
STATUS_LABEL = {"R": "Recommended", "A": "Alternative", "L": "Legacy / superseded"}

def load():
    with open(CAT, encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def platform_group(v):
    v = v.strip()
    if v == "shared":
        return "Shared / any input"
    if "long" in v or "ONT" in v or "PacBio" in v:
        return "Long-read focused"
    if "short" in v:
        return "Short-read focused"
    if "assembly" in v:
        return "Assembly / FASTA input"
    return "Shared / any input"

def main():
    rows = load()
    stages = {}
    for r in rows:
        stages.setdefault(r["stage_en"], {"order": int(r["order"]), "R": 0, "A": 0, "L": 0})
        stages[r["stage_en"]][r["status"]] += 1
    ordered = sorted(stages, key=lambda s: stages[s]["order"])

    fig = plt.figure(figsize=(14, 11))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.25, 1.0], hspace=0.34, wspace=0.32)
    axA = fig.add_subplot(gs[0, :])
    y = np.arange(len(ordered))
    for st, col, off in (("R", C_R, None), ("A", C_A, "R"), ("L", C_L, ("R", "A"))):
        vals = np.array([stages[s][st] for s in ordered])
        left = np.zeros(len(ordered))
        if isinstance(off, tuple):
            left = np.array([stages[s]["R"] + stages[s]["A"] for s in ordered])
        elif off == "R":
            left = np.array([stages[s]["R"] for s in ordered])
        axA.barh(y, vals, left=left, color=col, edgecolor="white", linewidth=0.4,
                 label=STATUS_LABEL[st])
    axA.set_yticks(y); axA.set_yticklabels(ordered, fontsize=8.5)
    axA.invert_yaxis()
    axA.set_xlabel("number of tools catalogued", fontsize=10)
    axA.set_title("A. Tools across 25 workflow stages (recommended, alternative and legacy)",
                  fontsize=12, loc="left")
    axA.legend(fontsize=9, ncol=3, loc="lower right", frameon=False)
    for sp in ("top", "right"): axA.spines[sp].set_visible(False)

    # B: status composition
    axB = fig.add_subplot(gs[1, 0])
    counts = [sum(stages[s][k] for s in ordered) for k in ("R", "A", "L")]
    wedges, _ = axB.pie(counts, colors=[C_R, C_A, C_L], startangle=90,
                        wedgeprops=dict(width=0.42, edgecolor="white"))
    axB.text(0, 0.08, str(sum(counts)), ha="center", va="center", fontsize=20,
             fontweight="bold")
    axB.text(0, -0.16, "tools", ha="center", va="center", fontsize=10)
    axB.legend(wedges, [f"{STATUS_LABEL[k]} ({n})" for k, n in
                        zip(("R", "A", "L"), counts)], loc="lower center",
               bbox_to_anchor=(0.5, -0.18), fontsize=8, frameon=False, ncol=1)
    axB.set_title("B. Recommendation status", fontsize=12, loc="left")

    # C: platform support
    axC = fig.add_subplot(gs[1, 1])
    pg = {}
    for r in rows:
        g = platform_group(r["platform"]); pg[g] = pg.get(g, 0) + 1
    order_p = ["Short-read focused", "Long-read focused", "Assembly / FASTA input",
               "Shared / any input"]
    vals = [pg.get(k, 0) for k in order_p]
    cols_p = ["#4393c3", "#d6604d", "#7b3294", "#5aae61"]
    axC.barh(range(len(order_p)), vals, color=cols_p)
    for i, v in enumerate(vals): axC.text(v + 1, i, str(v), va="center", fontsize=9)
    axC.set_yticks(range(len(order_p))); axC.set_yticklabels(order_p, fontsize=8.5)
    axC.invert_yaxis(); axC.set_xlabel("number of tools", fontsize=10)
    axC.set_title("C. Sequencing platform coverage", fontsize=12, loc="left")
    for sp in ("top", "right"): axC.spines[sp].set_visible(False)

    # D: environments and databases
    axD = fig.add_subplot(gs[1, 2]); axD.axis("off")
    n_env = len(re.findall(r"mamba create -y -n (\S+)", open(INSTALL, encoding="utf-8").read()))
    required_db = ["CheckM2", "GUNC (proGenomes 2.1)", "Bakta (full)", "eggNOG",
                   "PubMLST", "abricate databases", "AMRFinderPlus", "CARD / RGI",
                   "chewBBACA schemas"]
    optional_db = ["Kraken2 standard (optional)", "NCBI FCS-GX (optional)"]
    lines = [(f"Conda environments ({n_env})", "title")]
    lines.append((f"Required databases ({len(required_db)})", "title"))
    for d in required_db: lines.append((d, "db"))
    lines.append(("Optional large databases (2)", "title"))
    for d in optional_db: lines.append((d, "db"))
    y0 = 0.99
    for text, kind in lines:
        if kind == "title":
            axD.text(0.0, y0, text, fontsize=10.5, fontweight="bold", va="top")
            y0 -= 0.10
        else:
            axD.text(0.06, y0, "- " + text, fontsize=8.6, va="top"); y0 -= 0.063
    axD.set_title("D. Environments and databases", fontsize=12, loc="left")

    os.makedirs(FIG, exist_ok=True)
    for ext in ("png", "pdf", "svg"):
        out = os.path.join(FIG, f"EasyWGS_ecosystem.{ext}")
        fig.savefig(out, dpi=300, bbox_inches="tight")
        os.makedirs(DOCS_ASSETS, exist_ok=True)
        shutil_copy(out, os.path.join(DOCS_ASSETS, os.path.basename(out)))
    print("wrote EasyWGS_ecosystem.{png,pdf,svg}; tools =", len(rows),
          "; conda envs =", n_env)

def shutil_copy(a, b):
    import shutil; shutil.copy(a, b)

if __name__ == "__main__":
    main()
