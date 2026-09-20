# Changelog

This project follows semantic versioning; dates use ISO format.

## [0.6.0] - 2026-09-20

### Added

- Cross-domain extension assessment and a bilingual guidebook page,
  "Beyond bacteria: viruses, fungi and probiotics" (`docs/extensibility.md`
  and `docs/extensibility.zh.md`), covering a mapping/consensus-first viral
  track, a long/hybrid eukaryotic fungal track and a probiotic safety-and-benefit
  profile, with a shared-core table and a phased roadmap.
- Viral track tool selection for SARS-CoV-2 (iVar, ARTIC fieldbioinformatics,
  ViralConsensus, Nextclade, Pangolin, UShER, augur/Auspice, Freyja), HIV
  (HAPHPIPE, V-pipe, shiver, CliqueSNV, HIV-TRACE/tn93, HyPhy, HIVdb/HyDRA) and
  norovirus (VADR, dual ORF1/ORF2 typing), plus CheckV, VAPiD, VIGOR and
  nf-core/viralrecon as references.
- Fungal track tool selection for *Aspergillus* and *Candida* (AAFTF, BUSCO,
  funannotate, BRAKER3, MAKER, ITSx/UNITE, OrthoFinder, GET_HOMOLOGUES, nPhase,
  Control-FREEC, antiSMASH fungal mode, run_dbcan) and probiotic resources
  (EFSA QPS/FEEDAP, EUCAST, BAGEL4, Probio).
- `figures/make_domains_figure.py` and the EasyWGS_domains Venn plus
  stage-by-domain matrix figure (PNG, PDF, SVG), copied into `docs/assets/`.
- Catalogue stages 26 to 31, expanding `reference/tool_catalog.tsv` from 235 to
  276 entries across 31 stages; the tool encyclopedia and the ecosystem figure
  (31 stages, six conda environments) are regenerated.
- Bilingual README cross-domain sections and the MkDocs navigation entry.

### Notes

- This release documents feasibility and tool selection only; runnable viral and
  fungal modules are deferred to the phased roadmap and require validated public
  panels. Cross-domain material is for in silico teaching on public data, and
  genotype calls are not a substitute for phenotypic, regulatory or clinical
  judgement.

## [0.5.0] - 2026-09-20

### Added

- Tier 5 of the worked-example panel: 27 accession-verified Illumina isolates
  across nine further pathogen groups (*S. aureus*, *C. sakazakii*,
  *S. dysenteriae*, *V. cholerae*, *B. anthracis*, *B. cereus*, *B. mallei*,
  *M. tuberculosis* and *B. melitensis*), extending the panel to 71 isolates
  across 19 groups.
- The tier-5 groups reuse the FastANI identity gate (04.5), MLST (06.1) and
  custom marker screen (06.4) without new workflow logic; module 06.2 now
  dispatches the new species codes and documents spaTyper/SCCmecFinder for
  *S. aureus*, BTyper3 for the *B. cereus* group, and TB-Profiler/Mykrobe for
  *M. tuberculosis* as optional external tools.
- 47 curated markers in `easywgs_markers` (species, toxin, surface, resistance,
  plasmid and secretion loci, including the pXO1/pXO2 plasmids), expected-result
  rules P24 to P39, and tool-catalog rows for the optional specialized callers.
- Shared-database support documented for CheckM2, eggNOG, Bakta and GUNC,
  including manual CheckM2 `setdblocation` paths for clusters where the one-click
  download is interrupted; bilingual specialized-pathogen, walkthrough and
  README updates.

### Notes

- *M. tuberculosis* and *Brucella* have no classic seven-gene MLST scheme in the
  mlst database; they are confirmed by FastANI and analyzed with dedicated
  lineage or cgMLST tools. High-consequence pathogens are covered for in silico
  teaching on public data only, with genotype-not-phenotype and biosecurity
  caveats in the guidebook.

## [0.4.0] - 2026-09-20

### Added

- Tier 4 of the worked-example panel: 15 accession-verified Illumina isolates
  across five specialized pathogen groups (*V. parahaemolyticus*,
  *Y. enterocolitica*, *C. jejuni/C. coli*, *B. gladioli* and *C. botulinum*),
  extending the panel to 44 isolates across ten groups.
- Module 04.5 FastANI whole-genome ANI species-confirmation gate for mixed
  multi-species panels, writing `fastani_best.tsv` with confirmed,
  close-relative, review and no-hit status labels.
- Module 06.4 custom abricate screen of toxin, surface and virulence loci
  (`easywgs_markers`), with `00_install/build_custom_db.sh` and the curated
  `examples/customdb` marker list carrying authoritative sources.
- `examples/scripts/subset_samplesheet.py` to split a tier by `species_code` or
  panel `group` for the single-species comparative modules (08 to 13).
- Bilingual Specialized pathogens guidebook page and matching README,
  installation, typing, decontamination and walkthrough updates; FastANI added
  to the main conda environment and the tool catalog.

### Fixed

- Modules 06.2 and 06.3 now read the samplesheet with the `platform` column, so
  species dispatch and cgMLST schema selection apply the intended species.

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
