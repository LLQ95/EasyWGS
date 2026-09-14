# Changelog

This project follows semantic versioning; dates use ISO format.

## [0.3.0] - 2026-09-14

### Added

- Two parallel main routes with dedicated drivers: `run_assembly.sh`
  (de novo assembly route) and `run_mapping.sh` (reference-based BAM/VCF
  route), and a guidebook page comparing when each applies.
- Module 12_mapping_pipeline: BWA-MEM (Illumina) and minimap2 (ONT/PacBio)
  alignment to sorted/indexed BAM with coverage statistics (12.1), and joint
  bcftools calling into raw/filtered/bi-allelic VCF and a genotype matrix
  (12.2), plus an optional reference-only SNP tree path through vcf2phylip.
- Module 13_gwas microbial GWAS: Scoary gene-based pan-GWAS (13.1), PLINK SNP
  association with IBS/MDS structure control (13.2), pyseer gene/SNP tests
  with a distance-kernel mixed model (13.3), and a shared R post-GWAS step
  for BH/Bonferroni correction, QQ and Manhattan plots and ranked hit tables
  (13.4); a `config/traits.csv` phenotype template is provided.
- conda packages scoary, plink, pyseer, tabix, qualimap and vcf2phylip in the
  main environment; bilingual guidebook pages for the two strategies, the
  mapping route and GWAS/post-GWAS, plus matching README catalog sections and
  software-version rows.

## [0.2.0] - 2026-09-14

### Added

- Module 11_visualization for downstream figures: a merged annotation table
  (11.1), ggtree static trees in rectangular and circular layout (11.2),
  GrapeTree minimum spanning trees from cgMLST profiles and the core alignment
  (11.3), iTOL color-strip and binary datasets (11.4), pheatmap distance and
  gene-presence heatmaps (11.5), and offline upload bundles for iTOL,
  Microreact, Phandango, GrapeTree and icytree (11.6).
- R package installer 00_install/install_R_packages.R (ape, ggtree, treeio,
  ggtreeExtra, pheatmap, ComplexHeatmap and dependencies); grapetree added to
  the main conda environment.
- Bilingual guidebook page on visualization and a categorized visualization
  tool catalog in both README files.

### Changed

- All runnable scripts and configs are English-only by default; comments and
  console messages were translated without changing command behavior.
- merge_results.py master-table columns switched to English names
  (sample_id, length_bp, gc_percent, completeness_pct, contamination_pct,
  hits_<database>) consumed directly by module 11.
- run_all.sh runs 99_report merge before module 11 and then executes the six
  visualization steps.

## [0.1.0] - 2026-09-14

### Added

- Numbered main workflow 00 through 10 and 99, covering QC, two-layer
  decontamination, assembly, assembly assessment, annotation, MLST,
  species-specific serotyping, cgMLST, resistance/virulence/mobile elements,
  the pangenome, the core-SNP phylogeny and the TreeTime time tree.
- Support for Illumina short reads, ONT/PacBio long reads and hybrid assembly:
  long-read QC (porechop/NanoPlot/Filtlong), Flye/Canu assembly, capped Racon
  correction, Medaka polishing, Unicycler bold/SPAdes hybrid assembly and
  Pilon filling.
- MkDocs Material guidebook scaffold and Read the Docs configuration, with a
  short-read/long-read tool comparison.

### Notes

- First public framework release; database download scripts and per-module
  parameters continue to be validated.
