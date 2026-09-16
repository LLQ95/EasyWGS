#!/usr/bin/env python3
# EasyWGS technical implementation figure (Figure 3).
#
# Complements the conceptual overview (Figure 1) with the engineering view that a
# reader needs to reproduce the work: the numbered project layout and key files
# (left), the assembly route commands and outputs (middle) and the reference
# mapping route (right), both fed by one QC/decontamination layer and sitting on
# a conda/database/orchestration layer. Geometry is grid-based; enlarge fonts by
# growing the canvas, so nothing overlaps. Output: figures/EasyWGS_technical.svg
import os

FS = "Helvetica, Arial, sans-serif"
MONO = "Menlo, Consolas, monospace"
INK, SUB, CMD_C, FILE_C = "#1d1d1d", "#33383d", "#0b3d66", "#5b4a12"

F_TITLE, F_COL, F_CARD, F_CMD, F_FILE, F_TREE, F_LAYER = 21, 15.5, 13.3, 10.6, 10.4, 10.8, 12.6
W = 1760
TOP = 78
CARD_H, GAP = 86, 13
# column x and width (layout tree, route A, route B)
LX, LW = 36, 408
AX, AW = 472, 618
BX, BW = 1112, 612

C_IN  = ("#eaf1fb", "#b7cbe8", "#4f78b5", "#f8fbff")
C_A   = ("#eef6ef", "#a9cfb0", "#3f8a4f", "#f7fcf8")
C_B   = ("#e8f4f4", "#9ccac9", "#257f7f", "#f5fbfb")
C_GWAS= ("#f1ebf8", "#c4b1e0", "#7353a6", "#faf8fe")
C_OUT = ("#fbf5df", "#e4d085", "#c6a03d", "#fffdf2")
C_TREE= ("#f4f5f7", "#c7ccd6", "#8a909c", "#ffffff")
C_LAY = ("#f3f4f7", "#c7ccd6", "#6a707c", "#ffffff")

out = []
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def T(x, y, s, sz=F_CARD, col=INK, b=False, fam=FS, a="middle"):
    w = 'font-weight="bold"' if b else ''
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{sz}" fill="{col}" {w} text-anchor="{a}">{esc(s)}</text>')
def rect(x, y, w, h, fill, stroke, sw=1.5, rx=10, dash=None):
    d = f'stroke-dasharray="{dash}"' if dash else ''
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {d}/>')
def line(x1, y1, x2, y2, col="#333a44", w=1.6, dash=None):
    d = f'stroke-dasharray="{dash}"' if dash else ''
    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}" {d} stroke-linecap="round"/>')
def poly(pts, col="#333a44", w=1.6, arrow=True):
    p = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    m = ' marker-end="url(#ar)"' if arrow else ''
    out.append(f'<polyline points="{p}" fill="none" stroke="{col}" stroke-width="{w}"{m} stroke-linejoin="round"/>')
out.append('<marker id="ar" markerWidth="10" markerHeight="10" refX="7.6" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8,3.2 L0,6.4 Z" fill="#333a44"/></marker>')

def card(x, y, w, h, pal, title, cmds, fname=None):
    _, _, ns, nf = pal
    rect(x, y, w, h, nf, ns, sw=1.6, rx=10)
    T(x + 14, y + 21, title, F_CARD, INK, b=True, a="start")
    cy = y + 40
    for c in cmds:
        T(x + 14, cy, c, F_CMD, CMD_C, fam=MONO, a="start"); cy += 15
    if fname:
        T(x + 14, y + h - 9, fname, F_FILE, FILE_C, fam=MONO, a="start")

T(W / 2, 36, "EasyWGS technical implementation: project layout, two execution routes and engineering layer",
  F_TITLE, "#c00000", b=True)

# ---- shared preprocessing band (top) ----
pre_y = TOP
pre = [
    ("00  Raw data", ["00_rawdata/{id}_R1/_R2.fastq.gz", "{id}_ONT.fastq.gz"], "config/my_samples.csv"),
    ("01  Read QC", ["fastp (short); NanoPlot,", "Porechop, Filtlong (long)"], "01_qc/clean, 01_qc/long/clean"),
    ("02  Decontamination", ["CLEAN --host/--control/--own", "Kraken2+Bracken scout (optional)"], "02_decontam_reads/clean"),
]
pw = (W - 72 - 2 * 40) / 3
pre_cards = []
for i, (ti, cm, fo) in enumerate(pre):
    x = 36 + i * (pw + 40)
    card(x, pre_y, pw, 92, C_IN if i == 0 else C_LAY, ti, cm, fo)
    pre_cards.append((x, pre_y, pw, 92))
for a, b in zip(pre_cards[:-1], pre_cards[1:]):
    poly([(a[0] + a[2], a[1] + 46), (b[0], b[1] + 46)])

# ---- column headers ----
hy = pre_y + 92 + 30
T(LX + LW / 2, hy - 18, "Project layout (numbered modules)", F_COL, "#111", b=True)
T(AX + AW / 2, hy - 18, "Route A. de novo assembly (default for isolates)", F_COL, C_A[2], b=True)
T(BX + BW / 2, hy - 18, "Route B. reference mapping (surveillance / known clone)", F_COL, C_B[2], b=True)

col_top = hy
# GWAS row starts below the tallest route (Route B has six stacked cards)
gwas_y = col_top + 6 * (CARD_H + GAP) + 18
# ---- left: directory tree ----
tree = [
    "EasyWGS/",
    "|-- 00_rawdata/",
    "|-- 01_qc/            fastp, NanoPlot, MultiQC",
    "|-- 02_decontam_reads/  CLEAN, Kraken2 scout",
    "|-- 03_assembly/      Unicycler, Flye, Trycycler",
    "|-- 04_asm_qc/        CheckM2, GUNC, QUAST, FCS-GX",
    "|-- 05_annotation/    Bakta, Prokka, eggNOG",
    "|-- 06_typing/        mlst, serotype, chewBBACA",
    "|-- 07_amr_vf_mge/    abricate, AMRFinder, RGI, mob",
    "|-- 08_pangenome/     Panaroo, Roary",
    "|-- 09_phylogeny/     snippy, Gubbins, IQ-TREE 3",
    "|-- 10_timetree/      TreeTime clock, mugration",
    "|-- 12_mapping/       bwa/minimap2, bcftools",
    "|-- 13_gwas/          Scoary, PLINK, pyseer",
    "|-- 11_visualization/ GrapeTree, iTOL, ggtree",
    "|-- 99_report/        merge_results.py, master_table",
    "|-- config/           samplesheet, traits, dates",
    "|-- reference/        tool_catalog.tsv (230 tools)",
    "|-- examples/         panel, spike-in, expected",
    "`-- run_all.sh        resume by step number",
]
tree_h = col_top + 0
# height sized to match right columns later; draw panel first as placeholder then text
tree_box_y = col_top
tree_box_h = (gwas_y + CARD_H + 8) - col_top
rect(LX, tree_box_y, LW, tree_box_h, C_TREE[3], C_TREE[1], sw=1.6, rx=12)
ty = tree_box_y + 26
for ln in tree:
    col = "#111" if ln.endswith("/") or ln.startswith("EasyWGS") else SUB
    T(LX + 16, ty, ln, F_TREE, col, fam=MONO, a="start"); ty += 21

# ---- middle: Route A steps (two sub-columns, 8 cards) ----
A_steps = [
    ("03  Assemble", ["Unicycler --mode bold (short/hybrid)", "Flye+Racon+Medaka (long)"], "03_assembly/genomes/{id}.fasta"),
    ("04  Assembly QC", ["CheckM2 predict; GUNC run", "QUAST; FCS-GX screen (assembly)"], "04_asm_qc/checkm2/quality_report.tsv"),
    ("05  Annotate", ["Bakta --db bakta_db", "Prokka fallback; eggNOG-mapper"], "05_annotation/{id}.gff3"),
    ("06  Typing", ["mlst; Kleborate/ECTyper/SeqSero2", "SISTR; ShigEiFinder; chewBBACA"], "06_typing/mlst/pubmlst.tab"),
    ("07  AMR / VF / MGE", ["abricate (ResFinder, VFDB, CARD)", "AMRFinderPlus; RGI; mob-suite"], "07_amr_vf_mge/abricate/*.tab"),
    ("08  Pangenome", ["panaroo-run --clean-mode strict", "Roary as fast baseline"], "08_pangenome/panaroo/gene_presence_absence.csv"),
    ("09  Core-SNP tree", ["snippy-core; Gubbins; snp-sites", "iqtree3 -m MFP -bb 1000 -alrt 1000"], "09_phylogeny/core.treefile"),
    ("10  Dated tree", ["treetime clock; ancestral", "mugration --country"], "10_timetree/results/timetree.nexus"),
    ("11  Visualization", ["GrapeTree; iTOL upload", "ggtree; Microreact"], "11_visualization/"),
    ("20  ANI / dereplication", ["FastANI, skani", "Mash triangle; dereplicate"], "distance matrices and clusters"),
]
sub_gap = 16
subw = (AW - sub_gap) / 2
for idx, (ti, cm, fo) in enumerate(A_steps):
    row, sc = divmod(idx, 2)
    x = AX + sc * (subw + sub_gap)
    y = col_top + row * (CARD_H + GAP)
    card(x, y, subw, CARD_H, C_A, ti, cm, fo)
# snake chain: left->right within a row, then bend from right card to the
# left card of the next row
nrows_a = 5
for row in range(nrows_a):
    yy = col_top + row * (CARD_H + GAP) + CARD_H / 2
    poly([(AX + subw, yy), (AX + subw + sub_gap, yy)])          # left -> right
    if row < nrows_a - 1:
        xright = AX + subw + sub_gap + subw / 2
        xleft = AX + subw / 2
        ytop = col_top + row * (CARD_H + GAP) + CARD_H
        ybot = col_top + (row + 1) * (CARD_H + GAP)
        poly([(xright, ytop), (xright, (ytop + ybot) / 2),
              (xleft, (ytop + ybot) / 2), (xleft, ybot)])

# ---- right: Route B steps (single column, 6 cards) ----
B_steps = [
    ("12.1  Map reads", ["bwa mem (Illumina)", "minimap2 -ax map-ont (long)"], "12_mapping/{id}.sorted.bam"),
    ("12.2  BAM QC", ["samtools sort/index/stat", "qualimap bamqc; coverage stats"], "12_mapping/qualimap/{id}/"),
    ("12.3  Call variants", ["bcftools mpileup | call -mv", "bcftools filter (QUAL/DP)"], "12_mapping/{id}.flt.vcf.gz"),
    ("12.4  Merge and mask", ["bcftools merge; vcf2phylip", "mask recombination / mobile regions"], "12_mapping/core.vcf.gz"),
    ("12.5  SNP distances", ["snp-dists core.aln", "Mash screen sanity check"], "12_mapping/snp-dists.tsv"),
    ("09  Shared phylogeny", ["snp-sites; iqtree3", "feeds the same IQ-TREE / TreeTime"], "09_phylogeny/mapping.treefile"),
]
bw = BW
bh = CARD_H
for idx, (ti, cm, fo) in enumerate(B_steps):
    y = col_top + idx * (bh + GAP)
    card(BX, y, bw, bh, C_B, ti, cm, fo)
    if idx < len(B_steps) - 1:
        xc = BX + bw / 2
        poly([(xc, y + bh), (xc, y + bh + GAP)])

# Both routes feed the GWAS row from below; no cross-route arrow is drawn so
# cards are never crossed (the shared phylogeny step on route B also feeds 09/10).

# preprocessing -> both route heads and tree
pre_mid = pre_cards[1]
bus_y = pre_y + 92 + 8
line(pre_mid[0] + pre_mid[2] / 2, pre_y + 92, pre_mid[0] + pre_mid[2] / 2, bus_y)
line(AX + AW / 2, bus_y, BX + BW / 2, bus_y)
poly([(AX + AW / 2, bus_y), (AX + AW / 2, col_top)])
poly([(BX + BW / 2, bus_y), (BX + BW / 2, col_top)])
line(pre_mid[0] + pre_mid[2] / 2, bus_y, LX + LW / 2, bus_y)
poly([(LX + LW / 2, bus_y), (LX + LW / 2, col_top)], arrow=True)

# ---- GWAS and report rows under the two routes ----
gwas = ("13  Microbial GWAS and post-GWAS",
        ["Scoary (gene pan-GWAS); PLINK --logistic/--linear, MDS; pyseer --phenotypes --kmers",
         "BH/Bonferroni correction; QQ and Manhattan plots in R"],
        "13_gwas/results/{trait}_hits.tsv")
card(AX, gwas_y, AW + BW + (BX - AX - AW), CARD_H + 8, C_GWAS, gwas[0], gwas[1], gwas[2])
# route A core-SNP/pangenome (down the sub-column gutter) and route B core VCF
# both enter the GWAS row from above
x_a = AX + AW / 2
poly([(x_a, col_top + 4 * (CARD_H + GAP) - GAP), (x_a, gwas_y)], col=C_GWAS[2])
x_b = BX + BW / 2
poly([(x_b, col_top + 6 * (CARD_H + GAP) - GAP), (x_b, gwas_y)], col=C_GWAS[2])

rep_y = gwas_y + CARD_H + 8 + 22
card(36, rep_y, W - 72, 84, C_OUT,
     "99  Integrated, reproducible reporting",
     ["run_all.sh resumes by step number; every module is a standalone bash script; MultiQC aggregates QC",
      "merge_results.py writes 99_report/master_table.tsv; examples/collect_panel_metrics.py fills the manuscript tables"],
     "99_report/master_table.tsv ; examples/results/panel_metrics.tsv")

# ---- engineering layer band ----
lay_y = rep_y + 84 + 22
lay_h = 96
rect(36, lay_y, W - 72, lay_h, C_LAY[3], C_LAY[1], sw=1.6, rx=12, dash="7,5")
T(56, lay_y + 24, "Engineering and data layer", F_LAYER, "#111", b=True, a="start")
chunks = [
    ("6 conda environments", "easywgs, longread, checkm2, gunc, bakta, eggnog"),
    ("databases (~/easywgs_db)", "CheckM2, GUNC, Bakta, eggNOG, AMRFinder, CARD, PubMLST, chewBBACA; Kraken2 / FCS-GX optional"),
    ("workflow engines", "bash master runner with resume; CLEAN via Nextflow; Docker profile; Snakemake-style numbered modules"),
    ("quality gates", "set -euo pipefail; expected-result checks; examples spike-in; CI docs build"),
]
cw = (W - 72 - 24 - 3 * 18) / 4
for i, (h1, h2) in enumerate(chunks):
    x = 48 + i * (cw + 18)
    T(x, lay_y + 48, h1, 12.4, C_LAY[2], b=True, a="start")
    # wrap h2 into at most two mono lines
    words, lines, cur = h2.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if len(t) > 62 and cur:
            lines.append(cur); cur = wd
        else:
            cur = t
    if cur: lines.append(cur)
    for k, ln in enumerate(lines[:2]):
        T(x, lay_y + 66 + k * 15, ln, 10.2, SUB, fam=MONO, a="start")

H = lay_y + lay_h + 56
# footer
T(W / 2, H - 26, "github.com/LLQ95/EasyWGS  .  easywgs.readthedocs.io  .  Illumina / ONT / PacBio / hybrid",
  11.5, "#666")

svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}">\n' + "\n".join(out) + "\n</svg>\n"
here = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(here, "EasyWGS_technical.svg")
open(p, "w", encoding="utf-8").write(svg)
print("wrote", p, len(svg), "bytes; canvas", W, "x", round(H))
