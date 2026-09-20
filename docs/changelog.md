# Changelog

See the root CHANGELOG.md for the full history.

## 0.6.0 (2026-09-20)

Added a cross-domain extension assessment and a bilingual guidebook page,
"Beyond bacteria: viruses, fungi and probiotics". The page sets out a mapping- and
consensus-first viral track (SARS-CoV-2 with iVar, Nextclade, Pangolin and UShER; HIV
with HAPHPIPE/V-pipe, HIV-TRACE, HyPhy and HIVdb; norovirus with VADR and dual ORF
typing), a long/hybrid eukaryotic track for pathogenic fungi (AAFTF, BUSCO,
funannotate/BRAKER3, ITSx/UNITE, OrthoFinder, Control-FREEC and the fungal mode of
antiSMASH), and a probiotic safety-and-benefit profile layered over the bacterial track
(EFSA QPS/FEEDAP, acquired-resistance mobility checks and BAGEL4). It includes a
shared-core table, a Venn and stage-by-domain matrix figure (EasyWGS_domains) and a
phased roadmap. The tool catalogue grows from 235 to 276 entries across 31 stages (new
stages 26 to 31), and the ecosystem figure and the bilingual README are regenerated.
This release documents feasibility and tool selection; runnable viral and fungal modules
are deferred to the roadmap pending validated public panels.

## 0.5.0 (2026-09-20)

Tier 5 of the panel adds nine further pathogen groups (27 Illumina isolates, 71 in total):
*S. aureus*, *C. sakazakii*, *S. dysenteriae*, *V. cholerae*, *B. anthracis*, *B. cereus*,
*B. mallei*, *M. tuberculosis* and *B. melitensis*. They reuse the FastANI gate (04.5), MLST
(06.1) and custom marker screen (06.4); module 06.2 documents spaTyper/SCCmecFinder, BTyper3
and TB-Profiler/Mykrobe as optional callers. Added 47 curated markers, expected-result rules
P24 to P39, specialized tool rows, and shared-database (CheckM2/eggNOG/Bakta/GUNC) paths with
manual CheckM2 database setup. *M. tuberculosis* and *Brucella* have no seven-gene MLST scheme
and use FastANI plus dedicated lineage tools; high-consequence pathogens are covered for in
silico teaching on public data only.

## 0.4.0 (2026-09-20)

Tier 4 of the panel adds five specialized pathogen groups (15 Illumina isolates, 44 in
total): *V. parahaemolyticus*, *Y. enterocolitica*, *C. jejuni/C. coli*, *B. gladioli* and
*C. botulinum*. Added module 04.5 (FastANI species-confirmation gate), module 06.4 (a
custom abricate toxin/surface/virulence-locus screen with a database builder and a curated
marker list), a single-species subset helper for the comparative modules, and a bilingual
Specialized pathogens guidebook page.

## 0.2.0 (2026-09-14)

Added module 11_visualization (merged metadata, ggtree static trees, GrapeTree minimum spanning
trees, iTOL datasets, pheatmap heatmaps and offline bundles for iTOL/Microreact/Phandango/
GrapeTree/icytree), an R package installer, a visualization guidebook page and README tool
category. All runnable scripts and configs are now English-only; the master table uses English
column names.

## 0.1.0 (2026-09-14)

First public framework. The numbered main chain covers Illumina short reads, ONT/PacBio
long reads and hybrid assembly, with two-layer decontamination gates, species-specific
serotyping, cgMLST, resistance/virulence/mobile-element annotation, pangenome, core-SNP
phylogeny and a TreeTime time tree, together with a bilingual (English default, Simplified
Chinese) MkDocs Material guidebook.
