#!/usr/bin/env python3
# EasyWGS publication workflow figure (Figure 1), swimlane style.
#
# The figure follows the compact "numbered horizontal swimlane" layout used by
# the EasyMicrobiome/EasyMetagenome guides: each analysis stage is a pale dashed
# band with a bold stage label on the left, and every tool is a small rounded
# node that carries a bold title plus one bracketed tool line. Nodes are joined
# by dark orthogonal arrows; the assembly route (A, green) and the reference
# mapping route (B, teal) run as two parallel rows inside one band and merge
# into comparative genomics. Geometry is computed in a first pass and rendered
# in a second pass, so enlarging fonts only grows the canvas and never overlaps.
#
# Output: figures/EasyWGS_workflow.svg (render PDF/PNG with a browser).
import os

FS = "Helvetica, Arial, sans-serif"
INK, SUB, ARROW_C = "#1d1d1d", "#404040", "#333a44"

# ---- type scale (kept at normal reading size) ----
F_TITLE, F_LANE, F_NODE, F_TOOL = 21, 16.5, 14, 11.8
F_TAG, F_FOOT, F_LOGO = 11.5, 11.5, 30

W = 1680
TOP = 64
LANE_GAP = 14
PAD = 16
NODE_H, NODE_H2, NODE_H3 = 60, 68, 78      # one / two / three tool lines
# node area and side rails
NX0, NX1 = 300, 1640
NW = NX1 - NX0
RAIL_L, RAIL_R = 276, 1652

# lane palette: band fill, band edge, node stroke, node fill
C_IN   = ("#eaf1fb", "#b7cbe8", "#4f78b5", "#f8fbff")
C_PRE  = ("#fdf1e1", "#e7c38c", "#cf8744", "#fffaf3")
C_BOX  = ("#f3f4f7", "#c7ccd6", "#8a909c", "#ffffff")
C_A    = ("#f3f4f7", "#c7ccd6", "#4e9a5c", "#f2faf3")   # route A nodes
C_B    = ("#f3f4f7", "#c7ccd6", "#2e8f8f", "#f0f9f8")   # route B nodes
C_CMP  = ("#e6f4f3", "#92cfc9", "#2f8f86", "#f6fbfa")
C_GWAS = ("#f1ebf8", "#c4b1e0", "#7353a6", "#faf8fe")
C_VIZ  = ("#fbf5df", "#e4d085", "#c6a03d", "#fffdf2")

out = []
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def T(x, y, s, sz=F_TOOL, col=SUB, b=False, i=False, a="middle"):
    w = 'font-weight="bold"' if b else ''
    st = 'font-style="italic"' if i else ''
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FS}" font-size="{sz}" fill="{col}" {w} {st} text-anchor="{a}">{esc(s)}</text>')
def rect(x, y, w, h, fill, stroke, sw=1.5, rx=10, dash=None):
    d = f'stroke-dasharray="{dash}"' if dash else ''
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {d}/>')
def line(x1, y1, x2, y2, col=ARROW_C, w=1.6, dash=None):
    d = f'stroke-dasharray="{dash}"' if dash else ''
    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}" {d} stroke-linecap="round"/>')
def poly(pts, col=ARROW_C, w=1.6, arrow=True):
    p = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    m = ' marker-end="url(#ar)"' if arrow else ''
    out.append(f'<polyline points="{p}" fill="none" stroke="{col}" stroke-width="{w}"{m} stroke-linejoin="round"/>')

# arrow marker (single dark style)
out.append('<marker id="ar" markerWidth="10" markerHeight="10" refX="7.6" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8,3.2 L0,6.4 Z" fill="' + ARROW_C + '"/></marker>')

# ---------- PASS 1: lane geometry ----------
def lane_h(rows):  # rows = list of node heights inside the band
    return PAD * 2 + sum(rows) + max(0, len(rows) - 1) * 20

lanes = []
y = TOP
specs = [
    ("1. Data Input", C_IN, [NODE_H]),
    ("2. Preprocessing and QC", C_PRE, [NODE_H]),
    ("3. Two parallel routes (A assembly, B mapping)", C_BOX, [NODE_H3, NODE_H2]),
    ("4. Comparative genomics and evolution", C_CMP, [NODE_H]),
    ("5. Microbial genomic GWAS", C_GWAS, [NODE_H]),
    ("6. Visualization and reporting", C_VIZ, [NODE_H]),
]
for title, pal, rows in specs:
    h = lane_h(rows)
    lanes.append(dict(title=title, pal=pal, rows=rows, y=y, h=h))
    y += h + LANE_GAP
H = y - LANE_GAP + 58

def row_geos(lane, ri, n, gap=44):
    """Return node geometry for row ri of a lane, n equal nodes across node area."""
    if len(lane["rows"]) == 1:
        top = lane["y"] + PAD
    else:
        top = lane["y"] + PAD + ri * (lane["rows"][0] + 20)
    nh = lane["rows"][ri]
    w = (NW - (n - 1) * gap) / n
    return [dict(x=NX0 + i * (w + gap), y=top, w=w, h=nh) for i in range(n)]

# ---------- render helpers ----------
def draw_lane(lane):
    bf, be, _, _ = lane["pal"]
    rect(20, lane["y"], W - 40, lane["h"], bf, be, sw=1.6, rx=14, dash="7,5")
    # stage title, wrapped and vertically centered in the label gutter
    words, lines, cur = lane["title"].split(), [], ""
    limit = 28
    for wd in words:
        t = (cur + " " + wd).strip()
        if len(t) > limit and cur:
            lines.append(cur); cur = wd
        else:
            cur = t
    if cur: lines.append(cur)
    cy = lane["y"] + lane["h"] / 2 - (len(lines) - 1) * 10
    for k, ln in enumerate(lines):
        T(34, cy + k * 20 + 5, ln, F_LANE, "#111111", b=True, a="start")

def draw_node(g, title, tools, pal, tag=None):
    _, _, ns, nf = pal
    rect(g["x"], g["y"], g["w"], g["h"], nf, ns, sw=1.7, rx=11)
    cx = g["x"] + g["w"] / 2
    if isinstance(tools, str): tools = [tools]
    k = len(tools)
    if k == 1:
        T(cx, g["y"] + 24, title, F_NODE, INK, b=True)
        T(cx, g["y"] + 45, tools[0], F_TOOL, SUB)
    elif k == 2:
        ty = g["y"] + (g["h"] - 49) / 2 + 12.5
        T(cx, ty, title, F_NODE, INK, b=True)
        T(cx, ty + 19, tools[0], F_TOOL, SUB)
        T(cx, ty + 35, tools[1], F_TOOL, SUB)
    else:
        T(cx, g["y"] + 20, title, F_NODE, INK, b=True)
        T(cx, g["y"] + 38, tools[0], F_TOOL, SUB)
        T(cx, g["y"] + 53, tools[1], F_TOOL, SUB)
        T(cx, g["y"] + 68, tools[2], F_TOOL, SUB)
    if tag:
        T(g["x"] + 10, g["y"] + 16, tag, F_TAG, ns, b=True, a="start")
    return g

def cx(g): return g["x"] + g["w"] / 2
def top(g): return (cx(g), g["y"])
def bot(g): return (cx(g), g["y"] + g["h"])

# ---------- title ----------
T(W / 2, 36, "EasyWGS: end-to-end workflow for bacterial isolate whole-genome sequencing",
  F_TITLE, "#c00000", b=True)

# ---------- PASS 2: lanes and nodes ----------
L1, L2, L3, L4, L5, L6 = lanes
for ln in lanes: draw_lane(ln)

# Lane 1: inputs
r1 = row_geos(L1, 0, 2, gap=70)
draw_node(r1[0], "Raw Short Reads", "[Illumina paired-end]", C_IN)
draw_node(r1[1], "Raw Long Reads", "[ONT / PacBio]", C_IN)

# Lane 2: preprocessing
r2 = row_geos(L2, 0, 2, gap=70)
draw_node(r2[0], "Short-read QC and read-level decontamination",
          "[fastp, CLEAN, Kraken2/Bracken, BBDuk]", C_PRE)
draw_node(r2[1], "Long-read QC and trimming",
          "[Porechop, chopper, Filtlong, NanoPlot]", C_PRE)

# Lane 3: two parallel routes
rA = row_geos(L3, 0, 4, gap=42)
rB = row_geos(L3, 1, 3, gap=46)
draw_node(rA[0], "A1  Assembly and polishing",
          ["Unicycler/SPAdes (short, hybrid);", "Flye/Canu -> Trycycler -> Racon/Medaka,", "Pilon short-read polishing"], C_A)
draw_node(rA[1], "A2  Assembly quality gate",
          ["second-layer decontamination;", "QUAST, CheckM2, GUNC, FCS-GX"], C_A)
draw_node(rA[2], "A3  Annotation",
          ["Prokka, Bakta, Prodigal,", "eggNOG-mapper"], C_A)
draw_node(rA[3], "A4  Typing, AMR and MGEs",
          ["mlst, chewBBACA, Kleborate, ECTyper;", "abricate, AMRFinderPlus, mob-suite"], C_A)
draw_node(rB[0], "B1  Map to reference",
          ["BWA, minimap2,", "samtools sort/index"], C_B)
draw_node(rB[1], "B2  Joint variant calling",
          ["bcftools mpileup/call/filter,", "Qualimap coverage QC"], C_B)
draw_node(rB[2], "B3  Core-SNP matrix",
          ["vcf2phylip, snp-dists,", "Mash distance check"], C_B)
T(236, rA[0]["y"] + rA[0]["h"] / 2 + 4, "Route A", 11.5, C_A[2], b=True, a="start")
T(236, rB[0]["y"] + rB[0]["h"] / 2 + 4, "Route B", 11.5, C_B[2], b=True, a="start")

# Lane 4: comparative
r4 = row_geos(L4, 0, 3, gap=46)
draw_node(r4[0], "08  Pangenome", "[Panaroo; Roary as baseline]", C_CMP)
draw_node(r4[1], "09  Core-SNP / cgMLST phylogeny", "[snippy, Gubbins, snp-sites, IQ-TREE 3]", C_CMP)
draw_node(r4[2], "10  Dated time tree and evolution", "[TreeTime: clock, ancestors, mugration]", C_CMP)

# Lane 5: GWAS
r5 = row_geos(L5, 0, 4, gap=42)
draw_node(r5[0], "13.1  Scoary", "gene pan-GWAS [pan-matrix]", C_GWAS)
draw_node(r5[1], "13.2  PLINK", "SNP regression [VCF, MDS]", C_GWAS)
draw_node(r5[2], "13.3  pyseer", "mixed model [SNP/k-mer]", C_GWAS)
draw_node(r5[3], "Post-GWAS in R", "BH/Bonferroni, QQ, Manhattan", C_GWAS)

# Lane 6: reporting (single centered node)
g6 = dict(x=(W - 840) / 2, y=L6["y"] + PAD, w=840, h=NODE_H)
draw_node(g6, "99  Integrated, reproducible outputs",
          "[MultiQC  .  GrapeTree  .  iTOL  .  ggtree  .  Microreact  .  tables and logs]", C_VIZ)

# ---------- connectors ----------
# L1 -> L2 (aligned columns)
for i in range(2):
    poly([bot(r1[i]), top(r2[i])])

# L2 -> L3 : merge to a bus, enter A1 from top; route B through left rail
bus23 = L2["y"] + L2["h"] + 7
line(cx(r2[0]), bot(r2[0])[1], cx(r2[0]), bus23)
line(cx(r2[1]), bot(r2[1])[1], cx(r2[1]), bus23)
line(RAIL_L, bus23, max(cx(r2[0]), cx(r2[1])), bus23)
poly([(cx(rA[0]), bus23), top(rA[0])])                       # into A1
poly([(RAIL_L, bus23), (RAIL_L, rB[0]["y"] - 7), (cx(rB[0]), rB[0]["y"] - 7), top(rB[0])])

# within L3: A row and B row horizontal chains
def hchain(row):
    for a, b in zip(row[:-1], row[1:]):
        poly([(a["x"] + a["w"], a["y"] + a["h"] / 2), (b["x"], b["y"] + b["h"] / 2)])
hchain(rA); hchain(rB)

# L3 -> L4 : both rows exit via the right rail into a bus feeding lane 4
bus34 = L3["y"] + L3["h"] + 7
line(rA[3]["x"] + rA[3]["w"], rA[3]["y"] + rA[3]["h"] / 2, RAIL_R, rA[3]["y"] + rA[3]["h"] / 2)
line(rB[2]["x"] + rB[2]["w"], rB[2]["y"] + rB[2]["h"] / 2, RAIL_R, rB[2]["y"] + rB[2]["h"] / 2)
line(RAIL_R, rA[3]["y"] + rA[3]["h"] / 2, RAIL_R, bus34)
line(cx(r4[0]), bus34, RAIL_R, bus34)
for g in r4:
    poly([(cx(g), bus34), top(g)])

# within L4 chain
hchain(r4)

# L4 -> L5 : bus across, feed all four GWAS nodes
bus45 = L4["y"] + L4["h"] + 7
line(cx(r4[0]), bot(r4[0])[1], cx(r4[0]), bus45)
line(cx(r4[2]), bot(r4[2])[1], cx(r4[2]), bus45)
line(cx(r5[0]), bus45, cx(r5[3]), bus45)
for g in r5:
    poly([(cx(g), bus45), top(g)])
hchain(r5)

# L5 -> L6 : from last GWAS node, bend to centered report node
bus56 = L5["y"] + L5["h"] + 7
poly([bot(r5[3]), (cx(r5[3]), bus56), (cx(g6), bus56), top(g6)])

# ---------- footer ----------
fy = H - 34
out.append(f'<text x="{W/2}" y="{fy}" text-anchor="middle" font-family="{FS}" font-size="{F_LOGO}" font-weight="bold"><tspan fill="#1f6fb2">Easy</tspan><tspan fill="#c00000">WGS</tspan><tspan fill="#666" font-size="{F_FOOT}" font-weight="normal">    github.com/LLQ95/EasyWGS  .  easywgs.readthedocs.io  .  Illumina / ONT / PacBio / hybrid</tspan></text>')

svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}">\n' + "\n".join(out) + "\n</svg>\n"
here = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(here, "EasyWGS_workflow.svg")
open(p, "w", encoding="utf-8").write(svg)
print("wrote", p, len(svg), "bytes; canvas", W, "x", round(H))
