# Workflow overview (Figure 1)

![EasyWGS end-to-end workflow](assets/EasyWGS_workflow.png)

*Figure 1. End-to-end EasyWGS workflow for bacterial isolate whole-genome
sequencing, styled after the EasyMicrobiome and EasyMetagenome guides.*

The figure is organized into the four numbered parts shown across the top. The
left column lists the conda environments, software and reference databases that
module 00 installs, where a blue dot marks software and a red dot marks a
database. The central column is the analysis pipeline itself. Raw reads and the
sample sheet first pass through read QC (module 01) and the read-level
keep-by-target decontamination layer (module 02). Clean reads then follow one of
two parallel routes. The assembly-based route (Route A, blue) runs assembly and
polishing, a second assembly-level decontamination gate with CheckM2, GUNC and
FCS-GX, annotation, MLST/serotype/cgMLST typing, resistance/virulence/mobile
element screening, the pangenome and core-SNP calls. The reference-mapping
route (Route B, teal) maps reads to a common reference with BWA or minimap2 into
sorted/indexed BAM files, reports coverage and calls variants with bcftools into
a filtered VCF and genotype matrix. Both routes converge in the comparative and
evolutionary layer, where core/accessory calls, cgMLST alleles and core-SNP
alignments feed an IQ-TREE 3 phylogeny and a TreeTime time-scaled tree. The
genomic GWAS layer (purple, module 13) draws on the pangenome matrix, the VCF and
the trait table and runs Scoary, PLINK and pyseer, followed by R-based
post-GWAS. A closing band lists the integrated, reproducible outputs merged by
module 99, including the tree and annotation bundles exported for GrapeTree,
iTOL, ggtree and Microreact. Two plain text notes state when each route is the
better choice.

Route colour is used consistently throughout the guide: blue for the assembly
route, teal for the reference-mapping route and purple for GWAS/post-GWAS, with
red reserved for section titles and for input/output data types.

The editable vector source, a print-ready PDF and a high-resolution PNG live in
`figures/` (`EasyWGS_workflow.svg/.pdf/.png`). The figure is regenerated
deterministically by running `python figures/make_workflow_figure.py`, so labels
can be edited and re-exported without a drawing program.
