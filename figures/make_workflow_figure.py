#!/usr/bin/env python3
# Generate the EasyWGS publication workflow figure (Figure 1), styled after the
# EasyMetagenome iMeta workflow: red section headers/numbers, blue boxes, a left
# software/database column, a central pipeline, a right visualization column.
# Output: figures/EasyWGS_workflow.svg (render to PDF/PNG with a browser).
import textwrap, os

W, H = 1680, 1264
RED, BLUE, INK, GREY = "#c00000", "#1f6fb2", "#222222", "#777777"
A_BLUE, A_FILL = "#1f6fb2", "#eaf2fa"      # assembly route
B_TEAL, B_FILL = "#0f7b7b", "#e5f2f1"      # mapping route
P_PUR, P_FILL = "#6b4fa0", "#efeaf7"       # GWAS
HEAD_FILL = "#dce9f6"
FS = "Helvetica, Arial, sans-serif"
out = []

def esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
def T(x,y,s,sz=10.5,col=INK,b=False,i=False,a="start",ls=None):
    w='font-weight="bold"' if b else ''; st='font-style="italic"' if i else ''
    lsattr=f'letter-spacing="{ls}"' if ls else ''
    out.append(f'<text x="{x}" y="{y}" font-family="{FS}" font-size="{sz}" fill="{col}" {w} {st} {lsattr} text-anchor="{a}">{esc(s)}</text>')
def line(x1,y1,x2,y2,col=GREY,w=1.4,dash=None):
    d=f'stroke-dasharray="{dash}"' if dash else ''
    out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{w}" {d} stroke-linecap="round"/>')
def poly(pts,col=GREY,w=1.4,fill="none"):
    p=" ".join(f"{a},{b}" for a,b in pts)
    out.append(f'<polyline points="{p}" fill="{fill}" stroke="{col}" stroke-width="{w}" marker-end="url(#ar_{col[1:]})"/>')
def box(x,y,w,h,fill="#ffffff",stroke=BLUE,sw=1.3,rx=8,dash=None):
    d=f'stroke-dasharray="{dash}"' if dash else ''
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {d}/>')
def circ(x,y,r,fill=RED,stroke=RED):
    out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}"/>')
def wrap(s,n): return textwrap.wrap(s,n)

def node(x,y,w,h,title,body,otext,stroke,fill,tcol=None):
    box(x,y,w,h,fill=fill,stroke=stroke,sw=1.5)
    T(x+12,y+19,title,11.5,RED,b=True)
    yy=y+37
    for ln in body:
        T(x+12,yy,ln,9.8,INK); yy+=14
    if otext:
        T(x+w-10,y+h-8,otext,9,RED,i=True,a="end")
    return {"x":x,"y":y,"w":w,"h":h,"cx":x+w/2,"top":y,"bot":y+h,"L":x,"R":x+w}

def panel(x,y,w,h,title):
    box(x,y,w,h,fill="#ffffff",stroke=RED,sw=1.4,rx=10,dash="6,4")
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="26" rx="10" fill="{RED}"/>')
    out.append(f'<rect x="{x}" y="{y+13}" width="{w}" height="13" fill="{RED}"/>')
    T(x+w/2,y+18,title,12,"#ffffff",b=True,a="middle")

def soft_group(x,y,title,items,colsw=282):
    T(x,y,title,9.6,RED,b=True); yy=y+15
    for kind,txt in items:
        c = RED if kind=="db" else BLUE
        circ(x+4,yy-3.4,2.6,fill=c,stroke=c)
        # simple wrap inside left column
        j=0
        for seg in textwrap.wrap(txt,46):
            T(x+12,yy,seg,8.8,c); yy+=12.2; j+=1
        if j==0: yy+=12.2
    return yy+6

# ---------- markers ----------
for c in [GREY[1:],A_BLUE[1:],B_TEAL[1:],P_PUR[1:]]:
    out.append(f'<marker id="ar_{c}" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L7,3 L0,6 Z" fill="#{c}"/></marker>')

out.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')

# ================= top numbered bands =================
stages=[(36,"1  Installation &amp; setup"),(330,"2  QC &amp; two-layer decontamination"),
        (800,"3  Two parallel routes + genomic GWAS"),(1254,"4  Integration, visualization &amp; reporting")]
T(W/2,34,"EasyWGS: a reproducible cross-platform workflow for bacterial isolate whole-genome sequencing",
  17,RED,b=True,a="middle")
for x,lab in stages:
    circ(x,64,12); T(x,68.5,lab.split()[0],12,"#fff",b=True,a="middle")
    T(x+18,68.5," ".join(lab.split()[1:]).replace("&amp;","&"),10.6,INK,b=True)

# ================= LEFT panel: software & databases =================
panel(16,86,296,H-170,"Software & database installation  (module 00)")
lx=30; ly=128
ly=soft_group(lx,ly,"Conda / mamba environments",[("s","easywgs (main), longread, checkm2, gunc, bakta, eggnog")])
ly=soft_group(lx,ly,"Acquisition & read QC",[("s","fastp, FastQC, MultiQC"),("s","porechop, chopper, Filtlong, NanoPlot"),("s","NCBI datasets, SRA toolkit")])
ly=soft_group(lx,ly,"Two-layer decontamination",[("s","CLEAN, Kraken2/Bracken, BBDuk"),("s","CheckM2, GUNC, FCS-GX, BlobToolKit"),("db","k2_standard & FCS-GX databases")])
ly=soft_group(lx,ly,"Assembly & polishing",[("s","Unicycler, SPAdes, Flye, Canu, dragonflye"),("s","Trycycler, minimap2+Racon, Medaka, Pilon"),("s","circlator, QUAST, seqkit, assembly-stats")])
ly=soft_group(lx,ly,"Annotation & typing",[("s","Prokka, Bakta, Prodigal, eggNOG-mapper"),("s","mlst; chewBBACA (cgMLST)"),("s","Kleborate/Kaptive, ECTyper, ShigEiFinder"),("s","SeqSero2, SISTR"),("db","PubMLST & species cgMLST schemas")])
ly=soft_group(lx,ly,"AMR / virulence / MGE",[("s","abricate (ResFinder/VFDB/CARD/MEGARes)"),("s","AMRFinderPlus, RGI, PointFinder"),("s","mob-suite, PlasmidFinder, IntegronFinder"),("s","ISEScan, mobileOG, genomad, PhiSpy, CRISPRCasFinder"),("db","PLSDB, ResFinder, VFDB, CARD")])
ly=soft_group(lx,ly,"Comparison & evolution",[("s","Panaroo, Roary; mash, cd-hit"),("s","snippy, Gubbins, snp-sites, snp-dists"),("s","IQ-TREE 3, FastTree, MAFFT, MUMmer"),("s","TreeTime (clock, ancestors, mugration)")])
ly=soft_group(lx,ly,"Mapping & genomic GWAS",[("s","BWA, minimap2, samtools/bcftools, htslib"),("s","Qualimap, vcf2phylip, tabix"),("s","Scoary, PLINK, pyseer; R (BH/Bonferroni)")])
ly=soft_group(lx,ly,"Visualization",[("s","GrapeTree; iTOL datasets; ggtree"),("s","ComplexHeatmap; ggplot2")])
T(lx,1100,"Workflow drivers",9.6,RED,b=True)
T(lx,1115,"run_assembly.sh / run_mapping.sh",8.8,BLUE)
T(lx,1129,"run_all.sh chains every stage; 99_report merges results",8.4,GREY)
T(lx,H-96,"Legend",9.6,RED,b=True)
circ(lx+4,H-82,2.6,fill=BLUE,stroke=BLUE); T(lx+12,H-79,"software",8.8,BLUE)
circ(lx+96,H-82,2.6,fill=RED,stroke=RED); T(lx+104,H-79,"database",8.8,RED)
line(lx,H-66,lx+16,H-66,GREY,1.6); T(lx+22,H-62,"data flow",8.8,GREY)

# ================= CENTRAL pipeline panel =================
MX, MW = 328, 904
panel(MX,86,MW,H-170,"Data analysis pipeline  (modules 01–13, 99)")

# input strip
box(MX+16,120,MW-32,44,fill=HEAD_FILL,stroke=BLUE,sw=1.3)
T(MX+30,140,"Raw reads + metadata (config/samplesheet.csv):   Illumina paired-end   |   Oxford Nanopore   |   PacBio   |   hybrid",10.6,INK,b=True)
T(MX+30,156,"per-isolate id, platform, species, R1/R2, long reads, reference, date, country, phenotype",9,GREY,i=True)
T(MX+MW-24,140,"config/traits.csv",9,P_PUR,i=True,a="end")

# QC and decontam (full-width nodes)
n01=node(MX+16,176,MW-32,58,"01  Quality control",
   ["Short reads: fastp adapter/quality trimming and report     Long reads: porechop/chopper, Filtlong, NanoPlot"],
   "trimmed FASTQ + FastQC/MultiQC",A_BLUE,A_FILL)
n02=node(MX+16,248,MW-32,58,"02  Read-level decontamination  (layer 1: keep-by-target)",
   ["CLEAN retains only target-taxon reads; Kraken2/Bracken scouts composition; BBDuk removes reference/adapter hits"],
   "clean, single-source reads (FASTQ)",A_BLUE,A_FILL)
poly([(n01["cx"],n01["bot"]),(n01["cx"],n02["top"])],GREY,1.6)

# route labels
AX, AW = MX+16, 432
BX, BW = MX+16+AW+24, MW-32-AW-24
T(AX+AW/2,328,"ROUTE A — assembly-based (modules 03–09)",11,A_BLUE,b=True,a="middle")
T(BX+BW/2,328,"ROUTE B — reference mapping (module 12)",11,B_TEAL,b=True,a="middle")
poly([(n02["cx"],n02["bot"]),(n02["cx"],340),(AX+AW/2,340),(AX+AW/2,352)],A_BLUE,1.6)
poly([(n02["cx"],340),(BX+BW/2,340),(BX+BW/2,352)],B_TEAL,1.6)

# ---- Route A nodes ----
ay=352; gap=8
a03=node(AX,ay,AW,82,"03  Assemble & polish",
   wrap("Unicycler/SPAdes for short & hybrid; Flye/Canu/Trycycler for long; minimap2+Racon, Medaka, Pilon polish; circlator circularizes",78),
   "contigs FASTA",A_BLUE,A_FILL); ay+=82+gap
a04=node(AX,ay,AW,64,"04  Assembly QC & decontam (layer 2)",
   wrap("QUAST/seqkit stats; CheckM2 completeness/contamination; GUNC chimerism; FCS-GX removes foreign contigs/fragments",78),
   "clean genome FASTA",A_BLUE,A_FILL); ay+=64+gap
a05=node(AX,ay,AW,56,"05  Structural & functional annotation",
   ["Prokka/Bakta/Prodigal genes; eggNOG-mapper GO/KEGG/COG"],"GFF, GenBank, proteins",A_BLUE,A_FILL); ay+=56+gap
a06=node(AX,ay,AW,78,"06  Typing: MLST, serotype, cgMLST",
   wrap("mlst seven-gene ST; Kleborate/Kaptive (Klebsiella K/O), ECTyper/ShigEiFinder (E. coli–Shigella), SeqSero2/SISTR (Salmonella); chewBBACA cgMLST alleles",78),
   "ST / serotype / allele profiles",A_BLUE,A_FILL); ay+=78+gap
a07=node(AX,ay,AW,78,"07  AMR, virulence & mobile elements",
   wrap("abricate/AMRFinderPlus/RGI/PointFinder; plasmid (mob-suite, PlasmidFinder/PLSDB); integron, IS, ICE, phage/GI, CRISPR",78),
   "resistance & MGE tables",A_BLUE,A_FILL); ay+=78+gap
a08=node(AX,ay,AW,56,"08  Pangenome",
   ["Panaroo (Roary): core/accessory partition and graph"],"gene presence–absence matrix",A_BLUE,A_FILL); ay+=56+gap
a09=node(AX,ay,AW,58,"09A  Core SNPs from assemblies",
   ["snippy/Gubbins recombinant masking, snp-sites, snp-dists"],"core alignment, SNP distance",A_BLUE,A_FILL)
for a,b in [(a03,a04),(a04,a05),(a05,a06),(a06,a07),(a07,a08),(a08,a09)]:
    poly([(a["cx"],a["bot"]),(b["cx"],b["top"])],A_BLUE,1.5)

# ---- Route B nodes ----
by=352
b121=node(BX,by,BW,96,"12.1  Map reads to a common reference",
   wrap("BWA-MEM for Illumina/hybrid, minimap2 -ax map-ont/map-pb for long reads; samtools sort/index, flagstat, depth -a; coverage breadth/depth; Qualimap BAM QC",82),
   "sorted+indexed BAM, coverage summary",B_TEAL,B_FILL); by+=96+gap
b122=node(BX,by,BW,96,"12.2  Joint variant calling & filtering",
   wrap("bcftools mpileup (-q20 -Q20) | call -mv | norm | filter QUAL/DP; keep bi-allelic SNPs (missingness, MAC); bgzip+tabix",82),
   "raw/filtered/bi-allelic VCF",B_TEAL,B_FILL); by+=96+gap
bmat=node(BX,by,BW,64,"SNP matrix & alignment-free check",
   ["vcf2phylip core alignment; snp-dists pairwise matrix; mash for rapid neighbors"],"genotype matrix / SNP distances",B_TEAL,B_FILL); by+=64+gap
buse=box(BX,by,BW,108,fill="#fbfdfd",stroke=B_TEAL,sw=1.2,rx=8)
T(BX+12,by+18,"When to choose mapping",10.5,B_TEAL,b=True)
for k,ln in enumerate(wrap("Clonal outbreak tracing and large surveillance sets with a high-quality close reference; one common coordinate system, sensitive SNP/indel calls at moderate depth, no assembly step.",84)):
    T(BX+12,by+36+k*14,ln,9.3,INK)
T(BX+12,by+96,"Route A is preferred for accessory genes, plasmids, MGE and broad lineage diversity",9.1,RED,i=True)
for a,b in [(b121,b122),(b122,bmat)]:
    poly([(a["cx"],a["bot"]),(b["cx"],b["top"])],B_TEAL,1.5)
poly([(bmat["cx"],bmat["bot"]),(bmat["cx"],by)],B_TEAL,1.3)  # matrix -> applicability note

# ---- convergence: evolution ----
ey=952
box(AX,ey,AW+24+BW,78,fill="#f4f8fc",stroke=BLUE,sw=1.6)
T(AX+14,ey+20,"Comparative genomics & evolution  (modules 09–10)",11.5,RED,b=True)
T(AX+14,ey+40,"Core/accessory calls, cgMLST alleles and core-SNP alignments/distances converge into one phylogeny:",9.6,INK)
T(AX+14,ey+58,"IQ-TREE 3 (FastTree for quick look)  →  10 TreeTime: molecular clock, dated time tree,",10,BLUE,b=True)
T(AX+14,ey+72,"ancestral sequence reconstruction and trait mugration (country/host/phenotype)",10,BLUE,b=True)
poly([(a09["cx"],a09["bot"]),(a09["cx"],ey)],A_BLUE,1.6)
poly([(bmat["cx"],by+108),(bmat["cx"],ey-30),(AX+AW+24+BW/2,ey-30),(AX+AW+24+BW/2,ey)],B_TEAL,1.6)

# ---- GWAS band ----
gy=1046
box(AX,gy,AW+24+BW,100,fill=P_FILL,stroke=P_PUR,sw=1.6)
T(AX+14,gy+20,"13  Microbial genomic GWAS & post-GWAS  (input: gene presence–absence from 08, VCF from 12, traits.csv)",11,P_PUR,b=True)
cw=(AW+24+BW-28)/3
for k,(t,d) in enumerate([("13.1 Scoary","gene-level pan-GWAS, Fisher + permutation, pairwise correction"),
                          ("13.2 PLINK","SNP logistic/linear model with IBS/MDS population covariates"),
                          ("13.3 pyseer","mixed model with SNP/mash distance kernel; gene, SNP, optional k-mer")]):
    cx=AX+10+k*(cw+4); box(cx,gy+30,cw,44,fill="#ffffff",stroke=P_PUR,sw=1.2,rx=6)
    T(cx+8,gy+47,t,9.8,P_PUR,b=True)
    for j,seg in enumerate(wrap(d,52)): T(cx+8,gy+60+j*11,seg,8.4,INK)
T(AX+14,gy+92,"13.4 post-GWAS in R: BH/Bonferroni correction, QQ & Manhattan plots, merged hit table",9.4,P_PUR,b=True)
# GWAS inputs (gene P/A from 08, VCF from 12, traits.csv) are stated in the band header;
# no long cross-bending connectors are drawn so the convergence layer stays uncluttered.

# ================= RIGHT panel: visualization & reporting =================
RX,RW=1252,412
panel(RX,86,RW,H-170,"Statistics, visualization & reporting  (11, 99)")
def card(x,y,w,h,title,mini):
    box(x,y,w,h,fill="#ffffff",stroke=BLUE,sw=1.2,rx=7)
    T(x+8,y+16,title,9.4,RED,b=True)
    mini(x+10,y+24,w-20,h-34)

def m_tree(x,y,w,h):
    base=x+8
    for yy in (y+6,y+18,y+30): line(base,yy,base+18,yy,BLUE,1.3)
    line(base,y+6,base,y+30,BLUE,1.3); line(base+18,y+6,base+18,y+18,BLUE,1.3)
    line(base+18,y+18,x+w-8,y+18,BLUE,1.3);line(base+18,y+30,x+w-8,y+30,BLUE,1.3)
def m_time(x,y,w,h):
    for yy in(y+8,y+22,y+34): line(x+6,yy,x+w*0.5,yy,BLUE,1.2)
    line(x+6,y+8,x+6,y+34,BLUE,1.2)
    line(x+w*0.5,y+8,x+w*0.55,y+22,BLUE,1.2);line(x+w*0.55,y+22,x+w-6,y+22,BLUE,1.2)
    line(x+w*0.5,y+34,x+w-6,y+34,BLUE,1.2)
    line(x+4,y+h-4,x+w-4,y+h-4,GREY,1.1)
    for k,yr in enumerate(["2010","2018","2026"]): T(x+4+k*(w-8)/2,y+h+1,yr,7,GREY,a="start")
def m_mst(x,y,w,h):
    pts=[(x+14,y+12),(x+w*0.45,y+8),(x+w-14,y+14),(x+w*0.5,y+h-10),(x+w*0.25,y+h-14)]
    for i in range(len(pts)):
        for j in range(i+1,len(pts)):
            if abs(i-j) in (1,2): line(pts[i][0],pts[i][1],pts[j][0],pts[j][1],GREY,1.0)
    cols=[BLUE,"#c00000",BLUE,"#0f7b7b",BLUE]
    for (px,py),c in zip(pts,cols): circ(px,py,4,fill=c,stroke=c)
def m_ring(x,y,w,h):
    cx,cy=x+w/2,y+h/2;r=min(w,h)/2-4
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{BLUE}" stroke-width="5"/>')
    import math
    for k in range(14):
        a0=k/14*6.283;a1=(k+0.8)/14*6.283
        col=[RED,BLUE,"#0f7b7b",P_PUR][k%4]
        out.append(f'<path d="M {cx+(r-7)*math.cos(a0):.1f} {cy+(r-7)*math.sin(a0):.1f} A {r-7} {r-7} 0 0 1 {cx+(r-7)*math.cos(a1):.1f} {cy+(r-7)*math.sin(a1):.1f}" fill="none" stroke="{col}" stroke-width="4"/>')
def m_ggtree(x,y,w,h):
    m_tree(x,y,w,h*0.6)
    gx=x+w*0.62
    for r in range(3):
        for c in range(6):
            col=["#eaf2fa","#bcd6ea","#1f6fb2","#f3d2d2","#efeaf7","#dff0ee"][(r+c)%6]
            out.append(f'<rect x="{gx+c*((w-gx)/6)}" y="{y+2+r*13}" width="{(w-gx)/6}" height="11" fill="{col}" stroke="#fff" stroke-width="0.6"/>')
def m_man(x,y,w,h):
    import random; random.seed(7)
    for k in range(46):
        xx=x+4+k*(w-8)/46; yy=y+h-6-random.random()*(h-10)*(0.25 if k%9 else 1)
        col=RED if yy<y+h*0.45 else BLUE
        out.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="1.7" fill="{col}"/>')
    line(x+4,y+h*0.4,x+w-4,y+h*0.4,RED,1.0,dash="3,2")
def m_heat(x,y,w,h):
    for r in range(6):
        for c in range(10):
            import math
            v=(math.sin(r*1.3+c*0.9)+1)/2
            col=f"rgb({int(234-v*150)},{int(242-v*120)},{int(250-v*40)})"
            out.append(f'<rect x="{x+4+c*(w-8)/10}" y="{y+2+r*(h-8)/6}" width="{(w-8)/10}" height="{(h-8)/6}" fill="{col}" stroke="#fff" stroke-width="0.5"/>')
def m_map(x,y,w,h):
    out.append(f'<path d="M{x+6},{y+h-8} q10,-26 30,-20 q14,-16 34,-6 q20,-12 30,8 q16,2 14,20 Z" fill="#eef4fa" stroke="{BLUE}" stroke-width="1"/>')
    for px,py in [(x+24,y+h-18),(x+52,y+h-26),(x+78,y+h-16),(x+40,y+h-12)]: circ(px,py,3,fill=RED,stroke=RED)
def m_rep(x,y,w,h):
    for r in range(5): line(x+6,y+6+r*8,x+w-6,y+6+r*8,GREY,0.9)
    out.append(f'<rect x="{x+6}" y="{y+2}" width="{w-12}" height="6" fill="{HEAD_FILL}" stroke="{BLUE}" stroke-width="0.8"/>')

cards=[("Phylogeny (ggtree, IQ-TREE 3)",m_tree),("Time-scaled tree (TreeTime)",m_time),
       ("GrapeTree / MST clusters",m_mst),("iTOL annotated rings",m_ring),
       ("ggtree annotation panels",m_ggtree),("GWAS QQ & Manhattan (13.4)",m_man),
       ("AMR / allele heatmaps",m_heat),("Metadata maps & timeline",m_map),
       ("99 merged, typed report",m_rep)]
cw2=(RW-30)/2; chh=128; cx0=RX+12; cy0=122
for k,(t,m) in enumerate(cards):
    r,c=divmod(k,2)
    card(cx0+c*(cw2+6),cy0+r*(chh+10),cw2,chh,t,m)
sy=cy0+5*(chh+10)+12
box(RX+12,sy,RW-24,1180-sy-12,fill="#fcfdff",stroke=RED,sw=1.3,rx=8)
T(RX+22,sy+22,"Integrated, reproducible outputs (99_report)",10,RED,b=True)
outs=["Clean single-source reads and assemblies (FASTQ/FASTA)","ST, species serotype and cgMLST allele profiles",
      "AMR, virulence, plasmid and MGE annotations","Pangenome, core-SNP and cgMLST distance matrices",
      "Sorted/indexed BAM, coverage metrics and filtered VCF","IQ-TREE 3 phylogeny and TreeTime-dated time tree",
      "GWAS hits with BH/Bonferroni, QQ and Manhattan plots","GrapeTree/iTOL/ggtree bundles and merged report"]
for k,o in enumerate(outs):
    yy=sy+44+k*20; circ(RX+24,yy-3.4,2.4,fill=BLUE,stroke=BLUE); T(RX+32,yy,o,8.8,INK)

# ================= footer logotype =================
fy=H-58
out.append(f'<text x="{W/2}" y="{fy}" text-anchor="middle" font-family="{FS}" font-size="30" font-weight="bold"><tspan fill="{BLUE}">Easy</tspan><tspan fill="{RED}">WGS</tspan></text>')
T(W/2,H-26,"github.com/LLQ95/EasyWGS  ·  easywgs.readthedocs.io  ·  MIT license  ·  Illumina / Nanopore / PacBio / hybrid",10,GREY,a="middle")

svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">\n'+"\n".join(out)+"\n</svg>\n"
here=os.path.dirname(os.path.abspath(__file__))
p=os.path.join(here,"EasyWGS_workflow.svg")
open(p,"w",encoding="utf-8").write(svg)
print("wrote",p,len(svg),"bytes")
