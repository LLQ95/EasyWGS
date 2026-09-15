# Workflow overview (Figure 1)

![EasyWGS end-to-end workflow](assets/EasyWGS_workflow.png)

*Figure 1. End-to-end EasyWGS workflow for bacterial isolate whole-genome
sequencing, drawn as numbered horizontal swimlanes in the style of the
EasyMicrobiome and EasyMetagenome guides.*

The figure is organized as six numbered horizontal swimlanes that are read from
top to bottom. Each swimlane is a pale dashed band with a bold stage name at the
left, and every tool set is a compact node that pairs a bold title with the
programs it calls in brackets. Dark orthogonal arrows show how data move,
branch and merge. Lane 1 holds the raw short reads (Illumina) and long reads
(ONT/PacBio). Lane 2 performs short-read QC together with the read-level
keep-by-target decontamination (fastp, CLEAN, Kraken2/Bracken, BBDuk) and
long-read trimming and profiling (Porechop, chopper, Filtlong, NanoPlot). Lane 3
contains the two parallel routes. The green assembly route (A) runs assembly
and polishing, the assembly quality gate of QUAST, CheckM2, GUNC and FCS-GX
(the second decontamination layer), Prokka/Bakta annotation, and MLST,
serotype and cgMLST typing with AMR and mobile-element screening. The teal
mapping route (B) aligns reads with BWA or minimap2, calls and filters variants
with bcftools and builds the core-SNP matrix. Both routes merge into lane 4,
where Panaroo builds the pangenome and snippy, Gubbins, snp-sites and IQ-TREE 3
produce the phylogeny that TreeTime dates and annotates with ancestral states
and traits. Lane 5 runs microbial genomic GWAS with Scoary, PLINK and pyseer,
followed by R-based post-GWAS, and lane 6 collects the integrated, reproducible
outputs and the tree/annotation bundles exported for MultiQC, GrapeTree, iTOL,
ggtree and Microreact.

Colour is used consistently: green marks the assembly route, teal the
reference-mapping route and purple the GWAS stage, while each remaining lane
uses its own pale hue and red is reserved for the title and for stage numbering
in the manuscript.

The editable vector source, a print-ready PDF and a high-resolution PNG live in
`figures/` (`EasyWGS_workflow.svg/.pdf/.png`). The figure is regenerated
deterministically by running `python figures/make_workflow_figure.py`, so labels
can be edited and re-exported without a drawing program.
