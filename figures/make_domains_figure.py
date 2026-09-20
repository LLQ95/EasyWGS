#!/usr/bin/env python3
"""Fig. 5 (cross-domain): can the EasyWGS design extend beyond bacteria?

Left: a three-set Venn of the analytical capabilities shared by bacterial
isolate WGS, virus WGS (HIV, SARS-CoV-2, norovirus) and pathogenic fungal WGS
(Aspergillus, Candida), with representative programs in each region.
Probiotics are drawn as a use-profile (they reuse the bacterial track, with an
EFSA QPS safety/benefit lens; Saccharomyces boulardii follows the fungal track)
rather than as a fourth biological set.

Right: a stage-by-domain matrix giving the dominant paradigm and one or two
representative programs per cell. Green marks the domain-agnostic shared core,
the domain hues mark paradigm-specific tools, and grey marks a stage that does
not transfer in its bacterial form.

The figure is hand-laid for legibility (no third-party Venn package) and is
regenerated deterministically. Outputs figures/EasyWGS_domains.{svg,pdf,png}
and copies into docs/assets/. ASCII only.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FIG = os.path.join(ROOT, "figures")
DOCS_ASSETS = os.path.join(ROOT, "docs", "assets")

C_B, C_V, C_F = "#4393c3", "#d6604d", "#7b3294"   # bacteria, virus, fungi
C_CORE = "#5aae61"                                # shared core
C_NA = "#e6e6e6"
TXT = "#1a1a1a"


def venn(ax):
    ax.set_xlim(-2.55, 2.55)
    ax.set_ylim(-2.35, 2.30)
    ax.axis("off")
    ax.set_aspect("equal")

    d = 1.38
    hx = d / 2.0
    hy = d / (2.0 * 3.0 ** 0.5)
    cB = (-hx, hy)
    cF = (hx, hy)
    cV = (0.0, -d / 3.0 ** 0.5)
    r = 1.28

    for (cx, cy), col, name in (
        (cB, C_B, "Bacteria"),
        (cF, C_F, "Fungi"),
        (cV, C_V, "Viruses"),
    ):
        ax.add_patch(Circle((cx, cy), r, facecolor=col, alpha=0.16,
                            edgecolor=col, lw=2.2, zorder=1))

    # set titles (outside the circles)
    ax.text(-1.55, 1.80, "Bacteria", color=C_B, fontsize=15,
            fontweight="bold", ha="center")
    ax.text(1.55, 1.80, "Fungi", color=C_F, fontsize=15,
            fontweight="bold", ha="center")
    ax.text(0.0, -2.06, "Viruses", color=C_V, fontsize=15,
            fontweight="bold", ha="center")

    def region(x, y, title, tcol, body, fs=8.2, tfs=9.4, dy=0.15,
               ls=1.30):
        ax.text(x, y + 0.13, title, color=tcol, fontsize=tfs,
                fontweight="bold", ha="center", va="center", zorder=4)
        ax.text(x, y - 0.03, body, color=TXT, fontsize=fs,
                ha="center", va="top", zorder=4, linespacing=ls)

    # three-way shared core (capability words; program names live in matrix)
    region(0.0, 0.24, "Shared core", C_CORE,
           "QC and trimming\n"
           "mapping / BAM\n"
           "variant calling\n"
           "coverage, assembly stats\n"
           "alignment, ML trees\n"
           "dating*, tree visualisation\n"
           "function, workflow engine",
           fs=8.2, tfs=9.8)

    # bacteria only (upper-left outer lobe)
    region(-1.20, 0.92, "Bacteria only", C_B,
           "MLST, O/H/K serology\n"
           "CheckM2, GUNC, FastANI\n"
           "Roary, Snippy, Gubbins\n"
           "ResFinder, VFDB\n"
           "MOB-suite, gene GWAS",
           fs=7.8, tfs=9.2)

    # fungi only (upper-right outer lobe)
    region(1.20, 0.92, "Fungi only", C_F,
           "BUSCO fungi, ITSx\n"
           "BRAKER3, funannotate\n"
           "AAFTF, long / hybrid\n"
           "OrthoFinder\n"
           "nPhase, run_dbcan",
           fs=7.8, tfs=9.2)

    # virus only (bottom outer lobe)
    region(0.0, -1.30, "Viruses only", C_V,
           "CheckV, VADR\n"
           "iVar, ViralConsensus\n"
           "Nextclade, Pangolin\n"
           "HAPHPIPE, HIV-TRACE\n"
           "HyPhy, HIVDB / HyDRA",
           fs=7.8, tfs=9.2)

    # bacteria + fungi lens (top)
    region(0.0, 1.02, "Bacteria + fungi", "#3b6e8f",
           "de novo assembly\n"
           "gene annotation\n"
           "BGCs, long reads",
           fs=7.4, tfs=8.8)

    # bacteria + virus lens (lower-left)
    region(-0.95, -0.42, "Bacteria + viruses", "#b0553c",
           "core SNP\n"
           "dating\n"
           "epi clusters",
           fs=7.4, tfs=8.6)

    # fungi + virus lens (lower-right)
    region(0.95, -0.42, "Fungi + viruses", "#6d3a78",
           "host removal\n"
           "within-host\n"
           "variation",
           fs=7.4, tfs=8.6)

    ax.text(0.0, -2.30,
            "* dating applies when a molecular clock / temporal signal "
            "exists (weak for many fungi).",
            fontsize=7.4, ha="center", style="italic", color="#444444")


def matrix(ax):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 13)
    ax.axis("off")

    x_stage = 2.30
    w = (10.0 - x_stage) / 4.0
    cols = [("Stage", 0.0, x_stage, "#2f3b44", "white"),
            ("Bacteria", x_stage + 0 * w, x_stage + 1 * w, C_B, "white"),
            ("Viruses", x_stage + 1 * w, x_stage + 2 * w, C_V, "white"),
            ("Fungi", x_stage + 2 * w, x_stage + 3 * w, C_F, "white"),
            ("Probiotic profile", x_stage + 3 * w, 10.0, "#1b7837", "white")]
    for name, x0, x1, col, tc in cols:
        ax.add_patch(Rectangle((x0, 12.0), x1 - x0, 1.0, facecolor=col,
                               edgecolor="white", lw=1.2))
        ax.text((x0 + x1) / 2.0, 12.5, name, ha="center", va="center",
                fontsize=10.5, fontweight="bold", color=tc)

    # each row: stage, bacteria, virus, fungi, probiotic; tag = core|B|V|F|NA|mix
    rows = [
        ("Read QC",
         ("fastp, FastQC, MultiQC", "core"),
         ("fastp, FastQC, MultiQC", "core"),
         ("fastp, NanoPlot / chopper", "core"),
         ("same as bacteria", "core")),
        ("Host / contaminant removal",
         ("CLEAN, Kraken2, FCS-GX", "B"),
         ("map to host, KneadData, CheckV", "V"),
         ("map to host, BlobToolKit", "F"),
         ("same as bacteria", "B")),
        ("Assembly strategy",
         ("SPAdes, Unicycler, Flye", "B"),
         ("map + consensus (iVar,\nViralConsensus); metaSPAdes for DNA", "V"),
         ("Flye / Canu / HybridSPAdes,\nNextPolish", "F"),
         ("same as bacteria", "B")),
        ("Completeness / QC gate",
         ("CheckM2, GUNC", "B"),
         ("CheckV", "V"),
         ("BUSCO fungi, FGMP", "F"),
         ("CheckM2", "B")),
        ("Gene annotation",
         ("Bakta / Prokka, Prodigal", "B"),
         ("VADR, VIGOR, VAPiD", "V"),
         ("BRAKER3, funannotate, MAKER", "F"),
         ("Bakta + run_dbcan, antiSMASH", "mix")),
        ("Species / strain identity",
         ("FastANI, mlst", "B"),
         ("VADR, lineage, Nextclade", "V"),
         ("ITSx / UNITE, TEF1, SNP, skani", "F"),
         ("FastANI, EFSA taxonomic unit", "mix")),
        ("Typing / subtype",
         ("MLST, serotype, cgMLST", "B"),
         ("clade / subtype: Pangolin,\nNextclade, HIV subtype, noro VP1/RdRp", "V"),
         ("SNP clade, ITS, MLST / MLVA", "F"),
         ("strain MLST", "B")),
        ("Resistance / virulence",
         ("abricate, RGI, ResFinder, VFDB", "B"),
         ("HIVDB / HyDRA, HyPhy selection", "V"),
         ("cyp51A / ERG11 / FKS SNPs,\nCNV / aneuploidy", "F"),
         ("acquired AMR absent and\nnon-mobile, toxin absent (EFSA)", "mix")),
        ("Pangenome / homology",
         ("Roary, Panaroo, PIRATE", "B"),
         ("whole-genome alignment,\nNextalign (no gene pangenome)", "V"),
         ("OrthoFinder, GET_HOMOLOGUES", "F"),
         ("Panaroo", "B")),
        ("Variant / SNP calling",
         ("Snippy, Gubbins, bcftools", "B"),
         ("iVar / bcftools, low-frequency", "V"),
         ("GATK / freebayes, nPhase phasing", "F"),
         ("Snippy / bcftools", "B")),
        ("Phylogeny / dating",
         ("IQ-TREE 3, TreeTime, BactDating", "B"),
         ("IQ-TREE, UShER, TreeTime, BEAST", "V"),
         ("IQ-TREE / RAxML-NG on orthologs", "F"),
         ("IQ-TREE, TreeTime", "B")),
        ("Genotype-phenotype GWAS",
         ("pyseer, Scoary, PLINK", "B"),
         ("limited: large N, strong linkage", "NA"),
         ("hard: clonal, small samples", "NA"),
         ("optional trait association", "B")),
    ]

    fill = {"core": "#e7f4ec", "B": "#e3eef7", "V": "#f9e7e3",
            "F": "#efe6f4", "mix": "#fdf3e0", "NA": C_NA}
    edge = {"core": C_CORE, "B": C_B, "V": C_V, "F": C_F,
            "mix": "#e08e0b", "NA": "#b3b3b3"}

    y = 12.0
    rh = 1.0
    for stage, *cells in rows:
        y -= rh
        ax.add_patch(Rectangle((0.0, y), x_stage, rh, facecolor="#f4f6f8",
                               edgecolor="white", lw=1.0))
        ax.text(0.10, y + rh / 2.0, stage, ha="left", va="center",
                fontsize=9.0, fontweight="bold", color="#2f3b44")
        for (text, tag), (_, x0, x1, _, _) in zip(cells, cols[1:]):
            ax.add_patch(Rectangle((x0, y), x1 - x0, rh,
                                   facecolor=fill[tag],
                                   edgecolor=edge[tag], lw=1.0))
            tc = "#666666" if tag == "NA" else TXT
            ax.text((x0 + x1) / 2.0, y + rh / 2.0, text, ha="center",
                    va="center", fontsize=7.7, color=tc, linespacing=1.25)


def main():
    fig = plt.figure(figsize=(17.5, 10.6))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.28], wspace=0.06,
                          left=0.02, right=0.985, top=0.93, bottom=0.07)
    axV = fig.add_subplot(gs[0, 0])
    axM = fig.add_subplot(gs[0, 1])
    venn(axV)
    matrix(axM)
    fig.suptitle("Extending EasyWGS beyond bacteria: shared core versus "
                 "domain-specific tools",
                 fontsize=17, fontweight="bold", x=0.5, y=0.975)
    fig.text(0.5, 0.943,
             "Bacterial isolate WGS, virus WGS (HIV, SARS-CoV-2, norovirus) "
             "and pathogenic fungal WGS (Aspergillus, Candida) share a "
             "domain-agnostic core but differ in assembly, completeness, "
             "annotation and typing.",
             ha="center", fontsize=10.5, color="#333333")
    fig.text(0.5, 0.025,
             "Probiotics are a use-profile, not a fourth domain: bacterial "
             "probiotics reuse the bacterial track with an EFSA QPS "
             "safety/benefit lens, while Saccharomyces boulardii follows the "
             "fungal track.",
             ha="center", fontsize=9.5, style="italic", color="#1b7837")

    os.makedirs(FIG, exist_ok=True)
    import shutil
    for ext in ("png", "pdf", "svg"):
        out = os.path.join(FIG, "EasyWGS_domains.%s" % ext)
        fig.savefig(out, dpi=300, bbox_inches="tight")
        os.makedirs(DOCS_ASSETS, exist_ok=True)
        shutil.copy(out, os.path.join(DOCS_ASSETS, os.path.basename(out)))
    print("wrote EasyWGS_domains.{png,pdf,svg}")


if __name__ == "__main__":
    main()
