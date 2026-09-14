#!/usr/bin/env python3
# Generate the EasyWGS publication workflow figure (Figure 1), styled after the
# EasyMetagenome iMeta workflow: red section headers/numbers, blue boxes, a left
# software/database column and a wide central pipeline. The rough hand-drawn
# visualization thumbnails were removed on purpose; final deliverables (including
# the bundles for external viewers) are listed as text in the closing output band.
# Fonts are kept large and every node height is computed from its line count, and
# nodes are laid out sequentially so that nothing can overlap.
# Output: figures/EasyWGS_workflow.svg (render to PDF/PNG with a browser).
import textwrap, os, math

# ---------------- palette ----------------
RED, BLUE, INK, GREY = "#c00000", "#1f6fb2", "#1f1f1f", "#6f6f6f"
A_BLUE, A_FILL = "#1f6fb2", "#eaf2fa"      # assembly route
B_TEAL, B_FILL = "#0f7b7b", "#e4f2f1"      # mapping route
P_PUR, P_FILL = "#6b4fa0", "#efeaf7"       # GWAS
HEAD_FILL = "#dce9f6"
FS = "Helvetica, Arial, sans-serif"

# ---------------- enlarged type scale ----------------
F_TITLE, F_BAND, F_PANEL = 24, 14.5, 16
F_GROUP, F_LEFT = 13.5, 12.6
F_NODET, F_BODY, F_NOTE = 15.5, 13, 12
F_ROUTE, F_FOOT, F_LOGO = 14.5, 12.5, 36
LH = 19.6          # body line height
GAP = 12           # vertical gap between stacked nodes

W = 1780
# geometry
LX, LW = 18, 346
MX = LX + LW + 14                 # 378
MW = W - MX - 24                  # main panel width
PAD = 18
IX = MX + PAD                     # inner left
IW = MW - 2 * PAD                 # inner width
AX, AW = IX, (IW - 28) / 2
BX, BW = IX + AW + 28, (IW - 28) / 2

out = []
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def T(x, y, s, sz=11.8, col=INK, b=False, i=False, a="start"):
    w = 'font-weight="bold"' if b else ''
    st = 'font-style="italic"' if i else ''
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FS}" font-size="{sz}" fill="{col}" {w} {st} text-anchor="{a}">{esc(s)}</text>')
def line(x1, y1, x2, y2, col=GREY, w=1.5, dash=None):
    d = f'stroke-dasharray="{dash}"' if dash else ''
    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}" {d} stroke-linecap="round"/>')
def arrow(pts, col=GREY, w=1.7):
    p = " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
    out.append(f'<polyline points="{p}" fill="none" stroke="{col}" stroke-width="{w}" marker-end="url(#ar_{col[1:]})"/>')
def box(x, y, w, h, fill="#ffffff", stroke=BLUE, sw=1.5, rx=9, dash=None):
    d = f'stroke-dasharray="{dash}"' if dash else ''
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {d}/>')
def circ(x, y, r, fill=RED, stroke=RED):
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}"/>')
def wr(s, n): return textwrap.wrap(s, n)

# ---------------- PASS 1: layout (geometry only) ----------------
def node_h(n_body, has_out=True):
    return 44 + n_body * LH + (28 if has_out else 18)

y = 130
g_input = dict(x=IX, y=y, w=IW, h=58); y += g_input["h"] + GAP
g01 = dict(x=IX, y=y, w=IW, h=node_h(2)); y += g01["h"] + GAP
g02 = dict(x=IX, y=y, w=IW, h=node_h(2)); y += g02["h"] + 16
ROUTE_Y = y                      # route label band
ay = ROUTE_Y + 30

def stack(x, w, specs, top):
    yy = top; geos = []
    for n_body, has_out in specs:
        h = node_h(n_body, has_out)
        geos.append(dict(x=x, y=yy, w=w, h=h)); yy += h + GAP
    return geos, yy - GAP

# Route A (assembly) body line counts
A_specs = [(4, 1), (3, 1), (2, 1), (4, 1), (4, 1), (1, 1), (2, 1)]
gA, A_bot = stack(AX, AW, A_specs, ay)
# Route B (mapping): 3 nodes + a plain "when to choose" note sized to balance column
B_specs = [(4, 1), (4, 1), (2, 1)]
gB, B_bot0 = stack(BX, BW, B_specs, ay)
note_top = B_bot0 + GAP
note_body = wr("Clonal outbreak tracing and large surveillance sets where a high-quality close reference exists: one common coordinate system, sensitive SNP and indel calls at moderate depth, and no assembly step. Choose Route A for accessory genes, plasmids, mobile elements and broad lineage diversity.", 80)
gBnote = dict(x=BX, y=note_top, w=BW, h=40 + len(note_body) * LH + 22)
# a symmetric "when to choose assembly" note fills the lower part of column B
chooseA_top = gBnote["y"] + gBnote["h"] + GAP
chooseA_body = wr("Use Route A when no close reference exists, when plasmids and mobile elements matter, for species-level or cross-lineage comparisons, and whenever a standalone annotated genome is the intended deliverable.", 80)
gChooseA = dict(x=BX, y=chooseA_top, w=BW, h=40 + len(chooseA_body) * LH + 18)
B_bot = gChooseA["y"] + gChooseA["h"]
COL_BOT = max(A_bot, B_bot)
ev_y = COL_BOT + 18
g_ev = dict(x=IX, y=ev_y, w=IW, h=116)
gw_y = ev_y + 116 + 14
g_gw = dict(x=IX, y=gw_y, w=IW, h=150)
out_y = gw_y + 150 + 14
g_out = dict(x=IX, y=out_y, w=IW, h=180)
MAIN_BOT = out_y + 168
PANEL_TOP, PANEL_BOT = 96, MAIN_BOT + 16
H = PANEL_BOT + 78

# ---------------- PASS 2: render ----------------
for c in [GREY[1:], A_BLUE[1:], B_TEAL[1:], P_PUR[1:]]:
    out.append(f'<marker id="ar_{c}" markerWidth="10" markerHeight="10" refX="7.5" refY="3.2" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8,3.2 L0,6.4 Z" fill="#{c}"/></marker>')
out.append(f'<rect width="{W}" height="{H:.0f}" fill="#ffffff"/>')

# ---- title + numbered stage bands ----
T(W / 2, 42, "EasyWGS: a reproducible cross-platform workflow for bacterial isolate whole-genome sequencing",
  F_TITLE, RED, b=True, a="middle")
stages = [(44, "1", "Installation and setup"),
          (360, "2", "QC and two-layer decontamination"),
          (870, "3", "Two parallel routes plus genomic GWAS"),
          (1430, "4", "Integration and reporting")]
for x, num, lab in stages:
    circ(x, 74, 13.5); T(x, 79.5, num, 14, "#fff", b=True, a="middle")
    T(x + 21, 79, lab, F_BAND, INK, b=True)

# ---- panels ----
def panel(x, y, w, h, title):
    box(x, y, w, h, fill="#ffffff", stroke=RED, sw=1.6, rx=12, dash="7,5")
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="30" rx="12" fill="{RED}"/>')
    out.append(f'<rect x="{x}" y="{y+15}" width="{w}" height="15" fill="{RED}"/>')
    T(x + w / 2, y + 21, title, F_PANEL, "#ffffff", b=True, a="middle")

panel(LX, PANEL_TOP, LW, PANEL_BOT - PANEL_TOP, "Software and databases (module 00)")
panel(MX, PANEL_TOP, MW, PANEL_BOT - PANEL_TOP, "Data analysis pipeline (modules 01 to 13, 99)")

# ---- LEFT column: software/database inventory ----
def soft_group(x, y, title, items, width_chars=40):
    T(x, y, title, F_GROUP, RED, b=True); yy = y + 21
    for kind, txt in items:
        c = RED if kind == "db" else BLUE
        segs = wr(txt, width_chars)
        circ(x + 4, yy - 4, 3.1, fill=c, stroke=c)
        for seg in segs:
            T(x + 14, yy, seg, F_LEFT, c); yy += 17.4
        if not segs: yy += 17.4
    return yy + 8

llx = LX + 20
lly = PANEL_TOP + 46
lly = soft_group(llx, lly, "Conda / mamba environments", [("s", "easywgs (main), longread, checkm2, gunc, bakta, eggnog")])
lly = soft_group(llx, lly, "Acquisition and read QC", [("s", "fastp, FastQC, MultiQC"), ("s", "Porechop, chopper, Filtlong, NanoPlot"), ("s", "NCBI datasets, SRA Toolkit")])
lly = soft_group(llx, lly, "Two-layer decontamination", [("s", "CLEAN, Kraken2/Bracken, BBDuk"), ("s", "CheckM2, GUNC, FCS-GX, BlobToolKit"), ("db", "k2_standard and FCS-GX databases")])
lly = soft_group(llx, lly, "Assembly and polishing", [("s", "Unicycler, SPAdes, Flye, Canu, dragonflye"), ("s", "Trycycler, minimap2 + Racon, Medaka, Pilon"), ("s", "Circlator, QUAST, SeqKit, assembly-stats")])
lly = soft_group(llx, lly, "Annotation and typing", [("s", "Prokka, Bakta, Prodigal, eggNOG-mapper"), ("s", "mlst; chewBBACA (cgMLST)"), ("s", "Kleborate/Kaptive, ECTyper, ShigEiFinder"), ("s", "SeqSero2, SISTR"), ("db", "PubMLST and species cgMLST schemas")])
lly = soft_group(llx, lly, "AMR / virulence / MGE", [("s", "abricate (ResFinder/VFDB/CARD/MEGARes)"), ("s", "AMRFinderPlus, RGI, PointFinder"), ("s", "mob-suite, PlasmidFinder, IntegronFinder"), ("s", "ISEScan, mobileOG, geNomad, PhiSpy, CRISPRCasFinder"), ("db", "PLSDB, ResFinder, VFDB, CARD")])
lly = soft_group(llx, lly, "Comparison and evolution", [("s", "Panaroo, Roary; Mash, CD-HIT"), ("s", "snippy, Gubbins, snp-sites, snp-dists"), ("s", "IQ-TREE 3, FastTree, MAFFT, MUMmer"), ("s", "TreeTime (clock, ancestors, mugration)")])
lly = soft_group(llx, lly, "Mapping and genomic GWAS", [("s", "BWA, minimap2, samtools/bcftools, htslib"), ("s", "Qualimap, vcf2phylip, tabix"), ("s", "Scoary, PLINK, pyseer; R (BH/Bonferroni)")])
lly = soft_group(llx, lly, "External viewers (bundles exported)", [("s", "GrapeTree, iTOL datasets, ggtree"), ("s", "ComplexHeatmap, ggplot2, Microreact")])
# drivers + legend pinned near bottom of left panel
T(llx, PANEL_BOT - 96, "Workflow drivers", F_GROUP, RED, b=True)
T(llx, PANEL_BOT - 76, "run_assembly.sh / run_mapping.sh", F_LEFT, BLUE)
T(llx, PANEL_BOT - 58, "run_all.sh chains every stage; 99_report merges results", 10.8, GREY)
T(llx, PANEL_BOT - 36, "Legend", F_GROUP, RED, b=True)
circ(llx + 4, PANEL_BOT - 20, 3.1, fill=BLUE, stroke=BLUE); T(llx + 14, PANEL_BOT - 16, "software", F_LEFT, BLUE)
circ(llx + 118, PANEL_BOT - 20, 3.1, fill=RED, stroke=RED); T(llx + 128, PANEL_BOT - 16, "database", F_LEFT, RED)

# ---- node renderer ----
def draw_node(g, title, body, otext, stroke, fill, title_col=None, wrapn=84):
    x, y, w, h = g["x"], g["y"], g["w"], g["h"]
    box(x, y, w, h, fill=fill, stroke=stroke, sw=1.6)
    T(x + 14, y + 24, title, F_NODET, title_col or RED, b=True)
    yy = y + 46
    for raw in body:
        for seg in wr(raw, wrapn):
            T(x + 14, yy, seg, F_BODY, INK); yy += LH
    if otext:
        T(x + w - 12, y + h - 11, otext, F_NOTE, stroke, i=True, a="end")

# input strip
box(g_input["x"], g_input["y"], g_input["w"], g_input["h"], fill=HEAD_FILL, stroke=BLUE)
T(IX + 14, g_input["y"] + 25, "Raw reads and metadata (config/samplesheet.csv):  Illumina paired-end   |   Oxford Nanopore   |   PacBio   |   hybrid", 13.4, INK, b=True)
T(IX + 14, g_input["y"] + 47, "per-isolate id, platform, species, R1/R2, long reads, reference, date, country, phenotype          config/traits.csv", 12, GREY, i=True)

draw_node(g01, "01  Quality control",
          ["Short reads: fastp adapter/quality trimming and HTML report.",
           "Long reads: Porechop/chopper, Filtlong and NanoPlot for length and quality."],
          "trimmed FASTQ plus FastQC/MultiQC", A_BLUE, A_FILL, wrapn=150)
draw_node(g02, "02  Read-level decontamination (layer 1, keep-by-target)",
          ["CLEAN retains only target-taxon reads; Kraken2/Bracken scouts the taxonomic composition.",
           "BBDuk removes reference and adapter hits, leaving clean single-source reads."],
          "clean single-source reads (FASTQ)", A_BLUE, A_FILL, wrapn=150)
arrow([(g01["x"] + g01["w"] / 2, g01["y"] + g01["h"]), (g01["x"] + g01["w"] / 2, g02["y"])])

# route labels
T(AX + AW / 2, ROUTE_Y + 8, "ROUTE A - assembly-based (modules 03 to 09)", F_ROUTE, A_BLUE, b=True, a="middle")
T(BX + BW / 2, ROUTE_Y + 8, "ROUTE B - reference mapping (module 12)", F_ROUTE, B_TEAL, b=True, a="middle")
cx02 = g02["x"] + g02["w"] / 2
arrow([(cx02, g02["y"] + g02["h"]), (cx02, ROUTE_Y + 20), (AX + AW / 2, ROUTE_Y + 20), (AX + AW / 2, ay - 2)], A_BLUE)
arrow([(cx02, ROUTE_Y + 20), (BX + BW / 2, ROUTE_Y + 20), (BX + BW / 2, ay - 2)], B_TEAL)

# Route A
A_titles = ["03  Assemble and polish",
            "04  Assembly QC and decontamination (layer 2)",
            "05  Structural and functional annotation",
            "06  Typing: MLST, serotype, cgMLST",
            "07  AMR, virulence and mobile elements",
            "08  Pangenome",
            "09A  Core SNPs from assemblies"]
A_bodies = [
    ["Unicycler/SPAdes for short and hybrid reads; Flye, Canu and Trycycler for long reads.",
     "minimap2 plus Racon, then Medaka and short-read Pilon; Circlator fixes the origin."],
    ["QUAST/SeqKit statistics; CheckM2 completeness and contamination; GUNC chimerism.",
     "FCS-GX removes foreign contigs and fragments that survived read-level cleaning."],
    ["Prokka/Bakta/Prodigal call genes; eggNOG-mapper assigns GO, KEGG and COG terms."],
    ["mlst seven-gene ST; Kleborate/Kaptive for Klebsiella K/O; ECTyper/ShigEiFinder for E. coli-Shigella.",
     "SeqSero2/SISTR for Salmonella; chewBBACA calls cgMLST alleles."],
    ["abricate, AMRFinderPlus, RGI and PointFinder for resistance and point mutations.",
     "Plasmid, integron, IS, ICE, prophage/genomic island and CRISPR annotation."],
    ["Panaroo (Roary retained as a fast baseline): core/accessory partition and graph."],
    ["snippy and Gubbins mask recombinant segments; snp-sites and snp-dists finish the set."],
]
A_outs = ["contigs FASTA", "clean genome FASTA", "GFF, GenBank, proteins",
          "ST / serotype / allele profiles", "resistance and MGE tables",
          "gene presence-absence matrix", "core alignment, SNP distance"]
for i, g in enumerate(gA):
    draw_node(g, A_titles[i], A_bodies[i], A_outs[i], A_BLUE, A_FILL, wrapn=82)
for i in range(len(gA) - 1):
    arrow([(gA[i]["x"] + gA[i]["w"] / 2, gA[i]["y"] + gA[i]["h"]),
           (gA[i + 1]["x"] + gA[i + 1]["w"] / 2, gA[i + 1]["y"])], A_BLUE, 1.6)

# Route B
B_titles = ["12.1  Map reads to a common reference",
            "12.2  Joint variant calling and filtering",
            "SNP matrix and alignment-free check"]
B_bodies = [
    ["BWA-MEM for Illumina/hybrid reads, minimap2 -ax map-ont/map-pb for long reads.",
     "samtools sort/index, flagstat and depth; coverage breadth and depth; Qualimap BAM QC."],
    ["bcftools mpileup, call -mv, norm and filter on QUAL/DP; retain bi-allelic SNPs.",
     "Control missingness and minor allele count, then bgzip and tabix the result."],
    ["vcf2phylip core alignment; snp-dists pairwise matrix; Mash for a quick neighbour check."],
]
B_outs = ["sorted/indexed BAM, coverage summary", "raw/filtered/bi-allelic VCF", "genotype matrix / SNP distances"]
for i, g in enumerate(gB):
    draw_node(g, B_titles[i], B_bodies[i], B_outs[i], B_TEAL, B_FILL, wrapn=84)
for i in range(len(gB) - 1):
    arrow([(gB[i]["x"] + gB[i]["w"] / 2, gB[i]["y"] + gB[i]["h"]),
           (gB[i + 1]["x"] + gB[i + 1]["w"] / 2, gB[i + 1]["y"])], B_TEAL, 1.6)

def draw_note(g, head, lines, headcol, tail=None):
    x, y, w, h = g["x"], g["y"], g["w"], g["h"]
    box(x, y, w, h, fill="#fbfdfd", stroke=headcol, sw=1.4)
    T(x + 14, y + 24, head, F_NODET - 1, headcol, b=True); yy = y + 46
    for seg in lines:
        T(x + 14, yy, seg, F_BODY - 0.4, INK); yy += LH
    if tail:
        T(x + 14, y + h - 11, tail, F_NOTE, RED, i=True)
draw_note(gBnote, "When to choose mapping", note_body, B_TEAL,
          tail="Route A is preferred for accessory genes, plasmids, MGE and broad diversity")
draw_note(gChooseA, "When to choose assembly", chooseA_body, A_BLUE)
arrow([(gB[-1]["x"] + gB[-1]["w"] / 2, gB[-1]["y"] + gB[-1]["h"]),
       (gBnote["x"] + gBnote["w"] / 2, gBnote["y"])], B_TEAL, 1.4)

# convergence: comparative genomics & evolution
box(g_ev["x"], g_ev["y"], g_ev["w"], g_ev["h"], fill="#f4f8fc", stroke=BLUE, sw=1.8)
T(IX + 16, g_ev["y"] + 27, "Comparative genomics and evolution (modules 09 to 10)", F_NODET + 0.5, RED, b=True)
T(IX + 16, g_ev["y"] + 55, "Core/accessory calls, cgMLST alleles and core-SNP alignments converge into one comparative framework:", F_BODY + 0.4, INK)
T(IX + 16, g_ev["y"] + 82, "IQ-TREE 3 maximum-likelihood phylogeny (FastTree for a quick preview), then module 10 TreeTime", 13.4, BLUE, b=True)
T(IX + 16, g_ev["y"] + 104, "for molecular-clock dating, a dated time tree, ancestral sequence reconstruction and trait mugration (country/host/phenotype).", 13.4, BLUE)
arrow([(gA[-1]["x"] + gA[-1]["w"] / 2, gA[-1]["y"] + gA[-1]["h"]), (gA[-1]["x"] + gA[-1]["w"] / 2, g_ev["y"])], A_BLUE, 1.7)
arrow([(gBnote["x"] + gBnote["w"] / 2, gBnote["y"] + gBnote["h"]), (gBnote["x"] + gBnote["w"] / 2, g_ev["y"] - 14),
       (g_ev["x"] + g_ev["w"] * 0.78, g_ev["y"] - 14), (g_ev["x"] + g_ev["w"] * 0.78, g_ev["y"])], B_TEAL, 1.7)
arrow([(gChooseA["x"] + gChooseA["w"] / 2, gChooseA["y"] + gChooseA["h"]), (gChooseA["x"] + gChooseA["w"] / 2, g_ev["y"] - 14)], B_TEAL, 1.4)

# GWAS band
box(g_gw["x"], g_gw["y"], g_gw["w"], g_gw["h"], fill=P_FILL, stroke=P_PUR, sw=1.8)
T(IX + 16, g_gw["y"] + 28, "13  Microbial genomic GWAS and post-GWAS   (inputs: gene presence-absence from 08, VCF from 12, traits.csv)", 13.6, P_PUR, b=True)
gw_items = [("13.1  Scoary", ["gene-level pan-GWAS, Fisher and permutation", "tests with pairwise population correction"]),
            ("13.2  PLINK", ["SNP logistic/linear regression with IBS/MDS", "axes as population-structure covariates"]),
            ("13.3  pyseer", ["mixed model with a SNP/Mash distance kernel;", "gene, SNP and optional k-mer associations"])]
cw3 = (IW - 32 - 2 * 12) / 3
for k, (tt, dd) in enumerate(gw_items):
    cx = IX + 16 + k * (cw3 + 12)
    box(cx, g_gw["y"] + 42, cw3, 68, fill="#ffffff", stroke=P_PUR, sw=1.4, rx=8)
    T(cx + 12, g_gw["y"] + 66, tt, 13, P_PUR, b=True)
    T(cx + 12, g_gw["y"] + 88, dd[0], 11.8, INK)
    T(cx + 12, g_gw["y"] + 105, dd[1], 11.8, INK)
T(IX + 16, g_gw["y"] + 136, "13.4  post-GWAS in R: Benjamini-Hochberg and Bonferroni correction, QQ and Manhattan plots, merged hit table", 12.6, P_PUR, b=True)
arrow([(g_ev["x"] + g_ev["w"] / 2, g_ev["y"] + g_ev["h"]), (g_ev["x"] + g_ev["w"] / 2, g_gw["y"])], GREY, 1.7)

# integrated outputs band (text only, no thumbnails)
box(g_out["x"], g_out["y"], g_out["w"], g_out["h"], fill="#fcfdff", stroke=RED, sw=1.7)
T(IX + 16, g_out["y"] + 28, "99_report: integrated, reproducible outputs and external-viewer bundles", F_NODET + 0.5, RED, b=True)
outs = ["Clean single-source reads and assemblies (FASTQ/FASTA)",
        "ST, species serotype and cgMLST allele profiles",
        "AMR, virulence, plasmid and MGE annotations",
        "Pangenome, core-SNP and cgMLST distance matrices",
        "Sorted/indexed BAM, coverage metrics and filtered VCF",
        "IQ-TREE 3 phylogeny and TreeTime-dated time tree",
        "GWAS hits with BH/Bonferroni, QQ and Manhattan plots",
        "Tree/annotation bundles for GrapeTree, iTOL, ggtree, Microreact"]
col_w = IW / 2
for k, o in enumerate(outs):
    col = k % 2
    rowi = k // 2
    ox = IX + 18 + col * col_w
    oy = g_out["y"] + 62 + rowi * 29
    circ(ox, oy - 4, 3.4, fill=BLUE, stroke=BLUE)
    T(ox + 12, oy, o, 12.8, INK)
arrow([(g_gw["x"] + g_gw["w"] / 2, g_gw["y"] + g_gw["h"]), (g_out["x"] + g_out["w"] / 2, g_out["y"])], GREY, 1.7)

# ---- footer logotype ----
fy = H - 46
out.append(f'<text x="{W/2}" y="{fy}" text-anchor="middle" font-family="{FS}" font-size="{F_LOGO}" font-weight="bold"><tspan fill="{BLUE}">Easy</tspan><tspan fill="{RED}">WGS</tspan></text>')
T(W / 2, H - 16, "github.com/LLQ95/EasyWGS   .   easywgs.readthedocs.io   .   MIT license   .   Illumina / Nanopore / PacBio / hybrid", F_FOOT, GREY, a="middle")

svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}">\n' + "\n".join(out) + "\n</svg>\n"
here = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(here, "EasyWGS_workflow.svg")
open(p, "w", encoding="utf-8").write(svg)
print("wrote", p, len(svg), "bytes; canvas", W, "x", round(H))
