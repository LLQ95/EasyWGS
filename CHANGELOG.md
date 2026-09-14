# Changelog

This project follows semantic versioning; dates use ISO format.

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
