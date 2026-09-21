# EasyWGS

**English** | [简体中文](README.zh-CN.md)

EasyWGS is a reproducible, numbered-directory workflow for bacterial isolate
whole-genome sequencing (WGS). It covers Illumina short reads, Oxford Nanopore and
PacBio long reads, and hybrid assembly, and it chains quality control, two-layer
decontamination, assembly and polishing, assembly QC, annotation, MLST, species-specific
serotyping, cgMLST, resistance/virulence/mobile-element screening, the pangenome, a core-SNP
phylogeny and a TreeTime time-scaled tree. The layout follows the teaching-oriented style of
EasyMicrobiome and EasyMetagenome: edit the parameters at the top of each numbered script and
run the stages in order.

Full documentation: https://easywgs.readthedocs.io (English by default, switchable to
Simplified Chinese).

[![CI](https://github.com/LLQ95/EasyWGS/actions/workflows/ci.yml/badge.svg)](https://github.com/LLQ95/EasyWGS/actions/workflows/ci.yml)
[![Documentation Status](https://readthedocs.org/projects/easywgs/badge/?version=latest)](https://easywgs.readthedocs.io/en/latest/?badge=latest)
[![Container image](https://github.com/LLQ95/EasyWGS/actions/workflows/container.yml/badge.svg)](https://github.com/LLQ95/EasyWGS/pkgs/container/easywgs)

![EasyWGS end-to-end workflow](figures/EasyWGS_workflow.png)

The workflow above runs two parallel routes after QC and two-layer
decontamination: an assembly-based route (03 to 09) and a reference-mapping
route (12), which converge on phylogeny and the TreeTime time tree, with a
genomic GWAS/post-GWAS layer (13) and shared visualization (11) and reporting
(99). Editable SVG, print-ready PDF and the generator script are in
[`figures/`](figures/).

## Workflow by sequencing platform

Two parallel main routes share the same QC and reporting layers. The assembly
route (`run_assembly.sh`) reconstructs genomes de novo and derives gene content,
pangenome and core-SNP phylogeny from contigs; the reference route
(`run_mapping.sh`) maps reads to one close FASTA reference into BAM/VCF and then
runs microbial GWAS. `run_all.sh` runs both. See the guidebook page
[Two parallel strategies](https://easywgs.readthedocs.io/en/latest/pipelines-strategies/).

```text
Illumina short reads
  01 QC(fastp) -> 02 read decontamination(CLEAN) -> 03 Unicycler (SPAdes alt) -> 04 QC gate -> ...
ONT / PacBio long reads
  01b long QC(porechop + NanoPlot + Filtlong) -> 03 Flye -> Racon -> Medaka (optional Trycycler) -> ...
Hybrid
  01 + 01b -> 02 (clean short reads) -> 03 Unicycler --mode bold / SPAdes hybrid + Pilon -> ...

04  QUAST + CheckM2 + GUNC + (optional) FCS-GX assembly-level decontamination gate
04.5 FastANI whole-genome ANI species confirmation for the mixed multi-species panel
05  Prokka/Bakta, Prodigal, eggNOG (GO/KEGG/COG)
06  6.1 MLST, 6.2 species-specific serotyping, 6.3 chewBBACA cgMLST, 6.4 custom toxin/surface-locus screen
07  abricate databases + AMRFinder/RGI/PointFinder + geNomad/Mob-suite/IntegronFinder
08  Panaroo (Roary alternative) pangenome
09  snippy -> Gubbins -> IQ-TREE -> snp-dists core-SNP phylogeny
10  TreeTime clock filtering, time tree, ancestral reconstruction, homoplasy, migration
12  parallel reference route: BWA/minimap2 -> sorted indexed BAM -> bcftools VCF and SNP matrix
13  microbial GWAS: Scoary (pangenome genes), PLINK (SNPs), pyseer (distance-kernel LMM),
    then R post-GWAS with BH/Bonferroni correction, QQ and Manhattan plots
11  visualization: merged metadata, ggtree trees, GrapeTree MST, iTOL datasets, heatmaps, web bundles
99  merged master table (consumed by module 11)
```

## Quick start

```bash
bash 00_install/install_env.sh      # create conda environments (incl. the longread one)
bash 00_install/download_db.sh      # download databases once
cp config/samplesheet.csv config/my_samples.csv   # edit paths, platform and species
bash run_all.sh config/my_samples.csv             # run both routes and every module
bash run_assembly.sh config/my_samples.csv        # assembly-based route only
TRAIT=MDR bash run_mapping.sh config/my_samples.csv   # reference mapping + GWAS only
bash run_all.sh config/my_samples.csv 06          # or resume from a given step
```

The samplesheet field `platform` is one of illumina / nanopore / pacbio / hybrid and selects
the assembly route; `species` is one of kpsc / ecoli / salm / listeria / vibrio / yersinia /
campylobacter / burkholderia / clostridium / saureus / cronobacter / cholerae /
anthracis / cereus / mallei / mtuberculosis / brucella / other and selects the
typing schedule. Final assemblies are standardized to `03_assembly/genomes/{id}.fasta`
(fragments shorter than 200 nt removed), which every later module consumes.

## Reproducibility, tests and containers

Every push and pull request runs continuous integration (`.github/workflows/ci.yml`).
Static checks validate shell/Python/R syntax, enforce ASCII-only scripts and English-only
default pages, check the tool catalog and confirm the generated pages are current, then
build the guidebook in strict mode. A functional smoke test runs the real fastp, mapping,
variant-calling and decontamination modules on a small, seeded synthetic dataset with no
downloaded databases. The heavy database-backed steps (SPAdes panel runs, CheckM2, GUNC,
Bakta, eggNOG) are validated on the real public panel instead.

```bash
python tests/run_static_checks.py    # static checks, no bioinformatics tools needed
bash tests/run_smoke.sh              # end-to-end functional test on synthetic data
SYNTHETIC=1 bash examples/02_run_spikein.sh   # decontamination spike-in and its gates
```

The software environment is provided as a portable manifest (`install/environment.yml`),
exact per-machine locks (`00_install/export_locks.sh`), and a container image that is built
weekly and on Dockerfile changes. Databases are mounted at run time rather than baked in.

```bash
docker build -t easywgs:latest -f Dockerfile .
docker run --rm -it -v "$PWD":/EasyWGS -v "$HOME/easywgs_db":/opt/db:ro \
  -w /EasyWGS -e DBROOT=/opt/db easywgs:latest bash
```

See the guidebook pages [Reproducibility and tests](https://easywgs.readthedocs.io/en/latest/reproducibility/)
and [Cluster checklist](https://easywgs.readthedocs.io/en/latest/cluster-checklist/) for the
full test scope, the Apptainer/Singularity definition and the step-by-step real-panel run.

## Worked example on a multi-pathogen public panel

[`examples/`](examples/) runs the complete workflow end to end on real, accession-verified
public isolates spanning 19 pathogen groups (the ten tier 1-4 groups plus
S. aureus, C. sakazakii, S. dysenteriae, V. cholerae, B. anthracis, B. cereus,
B. mallei, M. tuberculosis and B. melitensis), with a twelve-isolate temporal
Salmonella collection, five matched Illumina/Nanopore hybrid isolates and
fourteen specialized groups, organized as nested tiers of 10, 20, 29, 44 and
71 samples. Tier 4 adds FastANI species confirmation (module 04.5) and a custom
toxin/surface-locus screen (module 06.4); tier 5 extends both to nine further
pathogen groups, with dedicated lineage callers for M. tuberculosis and the
B. cereus group, and the comparative modules are run on single-species subsets.
Reads are downloaded from ENA/NCBI on demand and downsampled so the tutorial runs on an ordinary
server; an expected-result checker reports PASS/WARN/FAIL and a controlled PhiX plus
near-neighbour spike-in validates the two decontamination layers.

```bash
EXAMPLE_PAIRS=800000 bash examples/00_download_panel.sh 1   # download tier 1 and references
bash examples/01_run_panel.sh 1                             # run every module end to end
bash examples/02_run_spikein.sh                             # decontamination validation (Fig. 4)
```

See [`examples/README.md`](examples/README.md) and the bilingual guidebook page
[Worked example (public panel)](https://easywgs.readthedocs.io/en/latest/example-walkthrough/)
for the panel accessions, outputs and collection-level analysis.

## Species-specific typing schedule (module 06)

| Group | 7-gene MLST | Serotype / surface antigens | cgMLST schema |
| --- | --- | --- | --- |
| K. pneumoniae complex (kpsc) | mlst | Kleborate (built-in Kaptive, K/O antigens) | INNUENDO or custom |
| E. coli / Shigella (ecoli) | mlst | ECTyper (O:H) + ShigEiFinder (Shigella/EIEC) | EnteroBase E./Shigella |
| Salmonella (salm) | mlst | SeqSero2 + SISTR | INNUENDO cgMLST99 |
| L. monocytogenes (listeria) | mlst | molecular serogroup via cgMLST | Pasteur cgMLST |
| V. parahaemolyticus (vibrio) | mlst (Vibrio) | module 06.4 tlh/tdh/trh/orf8, T3SS2 and O/K loci | PubMLST via PrepExternalSchema |
| Y. enterocolitica (yersinia) | mlst (Yersinia) | module 06.4 ail/yst, pYV yadA/virF | PrepExternalSchema |
| C. jejuni / C. coli (campylobacter) | mlst (Campylobacter) | module 06.4 cdt/cadF/flaA and capsule locus | PubMLST jejuni-coli |
| B. gladioli (burkholderia) | none; FastANI identity | module 06.4 bongkrekic-acid bon and toxoflavin tox | PrepExternalSchema |
| C. botulinum (clostridium) | mlst (C. botulinum) | module 06.4 bont/ntnh; MOB-suite locus location | PrepExternalSchema |
| S. aureus (saureus) | mlst (S. aureus) | module 06.4 nuc/mecA/PVL/tst; spaTyper and SCCmecFinder optional | PubMLST Staph |
| C. sakazakii (cronobacter) | mlst (Cronobacter genus) | module 06.4 ompA/zpx/cpa; PubMLST O-antigen resources | PrepExternalSchema |
| S. dysenteriae (ecoli) | mlst (E. coli) | ECTyper + ShigEiFinder; module 06.4 ipaH/stxA/virF | EnteroBase E./Shigella |
| V. cholerae (cholerae) | mlst (V. cholerae) | module 06.4 ompW/ctx/tcpA and O1/O139 loci | PubMLST Vibrio |
| B. anthracis (anthracis) | mlst (B. cereus group) | module 06.4 pXO1 pag/cya/lef and pXO2 cap; BTyper3 optional | PrepExternalSchema |
| B. cereus (cereus) | mlst (B. cereus group) | module 06.4 nhe/hbl/cytK/ces; BTyper3 panC optional | PrepExternalSchema |
| B. mallei (mallei) | mlst (B. pseudomallei group) | module 06.4 bimA/bsa; curated SNP phylogeny for species split | PrepExternalSchema |
| M. tuberculosis (mtuberculosis) | none; FastANI identity | map to H37Rv then TB-Profiler/Mykrobe; module 06.4 esx auxiliary | lineage callers |
| B. melitensis (brucella) | none; FastANI identity | module 06.4 bcsp31/IS711/omp2b/wbkA; external cgMLST/MLVA | Brucella cgMLST |
| other | mlst auto-detect | extend as needed | PrepExternalSchema |

## WGS tool catalog

Platform column: S = mainly short reads, L = mainly long reads, A = applies to both/assemblies.
Every link was checked against the upstream repository or official site. These are the tools
used or recommended by EasyWGS, organized by analysis stage. The current upstream release of
each tool and the check date are kept on the
[Software versions](https://easywgs.readthedocs.io/en/latest/versions/) page of the guidebook.
Beyond the defaults below, the
[Tool encyclopedia](https://easywgs.readthedocs.io/en/latest/alternative-tools/) lists actively
maintained alternatives and older but still usable legacy tools for every stage, with the
successor of each legacy tool marked (for example Trimmomatic to fastp, CheckM to CheckM2,
Prokka to Bakta, Roary to Panaroo, SEER to pyseer). The machine-readable table is
`reference/tool_catalog.tsv`. The guidebook also evaluates how the same design transfers
beyond bacteria in
[Beyond bacteria: viruses, fungi and probiotics](https://easywgs.readthedocs.io/en/latest/extensibility/),
with a Venn comparison of shared and domain-specific tools and profiles for viruses
(HIV, SARS-CoV-2, norovirus), pathogenic fungi (*Aspergillus*, *Candida*) and probiotic
safety assessment (catalogue stages 26 to 31).

### Quality control and read processing

| Tool | P | Purpose | Source |
| --- | --- | --- | --- |
| fastp | S/L | adapter trimming, quality filtering and QC report | [GitHub](https://github.com/OpenGene/fastp) |
| FastQC | S | per-file read quality reports | [GitHub](https://github.com/s-andrews/FastQC) |
| MultiQC | A | aggregate QC reports across a batch | [GitHub](https://github.com/MultiQC/MultiQC) |
| seqkit | A | fasta/fastq parsing, stats and subsampling | [GitHub](https://github.com/shenwei356/seqkit) |
| Porechop | L | long-read adapter and barcode removal | [GitHub](https://github.com/rrwick/Porechop) |
| chopper | L | long-read length/quality filtering | [GitHub](https://github.com/wdecoster/chopper) |
| NanoPlot | L | long-read length and quality plots | [GitHub](https://github.com/wdecoster/NanoPlot) |
| Filtlong | L | quality-weighted long-read filtering | [GitHub](https://github.com/rrwick/Filtlong) |

### Decontamination and taxonomic screening

| Tool | P | Purpose | Source |
| --- | --- | --- | --- |
| Kraken2 | S | k-mer taxonomic classification and contamination scout | [GitHub](https://github.com/DerrickWood/kraken2) |
| Bracken | S | refine Kraken2 abundance estimates | [GitHub](https://github.com/jenniferlu717/Bracken) |
| CLEAN | S/L/A | read- or assembly-level keep-by-target decontamination | [GitHub](https://github.com/rki-mf1/clean) |
| BBMap / BBDuk | S | reference/adapter/PhiX sequence removal | [GitHub](https://github.com/BioInfoTools/BBMap) |
| CheckM2 | A | assembly completeness and contamination | [GitHub](https://github.com/chklovski/CheckM2) |
| GUNC | A | chimeric (mixed-species) genome detection | [GitHub](https://github.com/grp-bork/gunc) |
| FCS / FCS-GX | A | NCBI foreign-contaminant screening and cleaning | [GitHub](https://github.com/ncbi/fcs) |
| BlobToolKit | A | contig-level taxonomy/coverage interactive QC | [GitHub](https://github.com/genomehubs/blobtoolkit) |

### Assembly and polishing

| Tool | P | Purpose | Source |
| --- | --- | --- | --- |
| SPAdes | S/Hybrid | short-read and hybrid de Bruijn assembler | [GitHub](https://github.com/ablab/spades) |
| Unicycler | S/Hybrid | isolate assembler, bold hybrid mode, circularization-friendly | [GitHub](https://github.com/rrwick/Unicycler) |
| Flye | L | long-read assembler with circular contig flags | [GitHub](https://github.com/fenderglass/Flye) |
| Canu | L | conservative long-read assembler | [GitHub](https://github.com/marbl/canu) |
| Dragonflye | L | SPAdes-style pipeline for Nanopore reads | [GitHub](https://github.com/rpetit3/dragonflye) |
| Trycycler | L | multi-assembly consensus for finished-grade genomes | [GitHub](https://github.com/rrwick/Trycycler) |
| minimap2 | L/A | versatile long-read/read-to-assembly aligner | [GitHub](https://github.com/lh3/minimap2) |
| Racon | L | long-read consensus correction (limit rounds) | [GitHub](https://github.com/lbcb-sci/racon) |
| Medaka | L | ONT neural-network consensus polishing | [GitHub](https://github.com/nanoporetech/medaka) |
| Pilon | S/Hybrid | short-read base-level error filling | [GitHub](https://github.com/broadinstitute/pilon) |
| Circlator | A | circularize assemblies and fix the origin | [GitHub](https://github.com/sanger-pathogens/circlator) |

### Assembly statistics, distance and dereplication

| Tool | P | Purpose | Source |
| --- | --- | --- | --- |
| QUAST | A | assembly statistics (N50, contigs, misassemblies) | [GitHub](https://github.com/ablab/quast) |
| Mash | A | fast genome distance and clustering | [GitHub](https://github.com/marbl/Mash) |
| cd-hit | A | cluster/dereplicate similar sequences | [GitHub](https://github.com/weizhongli/cdhit) |
| MUMmer | A | whole-genome alignment and synteny | [GitHub](https://github.com/mummer4/mummer) |
| FastANI | A | whole-genome ANI species confirmation (module 04.5) | [GitHub](https://github.com/ParBLiSS/FastANI) |

### Structural and functional annotation

| Tool | P | Purpose | Source |
| --- | --- | --- | --- |
| Prokka | A | rapid prokaryotic genome annotation | [GitHub](https://github.com/tseemann/prokka) |
| Bakta | A | standardized annotation with up-to-date databases | [GitHub](https://github.com/oschwengers/bakta) |
| Prodigal | A | prokaryotic gene (protein) prediction | [GitHub](https://github.com/hyattpd/Prodigal) |
| eggNOG-mapper | A | GO / KEGG / COG functional annotation | [GitHub](https://github.com/jhcepas/eggnog-mapper) |

### Typing: MLST, serotype and cgMLST

| Tool | P | Purpose | Source |
| --- | --- | --- | --- |
| mlst | A | scan PubMLST seven-gene sequence types | [GitHub](https://github.com/tseemann/mlst) |
| Kleborate | A | Klebsiella ST, K/O antigens, AMR and virulence | [GitHub](https://github.com/klebgenomics/Kleborate) |
| ECTyper | A | Escherichia coli O:H serotyping | [GitHub](https://github.com/phac-nml/ecoli_serotyping) |
| ShigEiFinder | A | Shigella / EIEC discrimination | [GitHub](https://github.com/LanLab/ShigEiFinder) |
| SeqSero2 | A | Salmonella antigenic formula from reads or assembly | [GitHub](https://github.com/denglab/SeqSero2) |
| SISTR | A | Salmonella serovar prediction with cgMLST | [GitHub](https://github.com/phac-nml/sistr_cmd) |
| chewBBACA | A | cgMLST schema building, allele calling and evaluation | [GitHub](https://github.com/B-UMMI/chewBBACA) |
| spaTyper / SCCmecFinder | A | S. aureus spa repeat and SCCmec cassette typing (optional) | [CGE website](https://www.genomicepidemiology.org/) |
| BTyper3 | A | B. cereus group panC group and virulence typing (optional) | [GitHub](https://github.com/lmc297/BTyper3) |
| TB-Profiler | A | M. tuberculosis lineage and drug resistance (optional) | [GitHub](https://github.com/jodyphelan/TBProfiler) |
| Mykrobe | A | rapid k-mer AMR for M. tuberculosis and S. aureus (optional) | [GitHub](https://github.com/Mykrobe-tools/mykrobe) |

### Antimicrobial resistance, virulence and mobile elements

| Tool | P | Purpose | Source |
| --- | --- | --- | --- |
| abricate | A | one-pass screen of many AMR/VF databases | [GitHub](https://github.com/tseemann/abricate) |
| AMRFinderPlus | A | NCBI AMR and resistance-gene annotation | [GitHub](https://github.com/ncbi/amr) |
| RGI (CARD) | A | CARD resistance gene/allele annotation | [GitHub](https://github.com/arpcard/rgi) |
| ResFinder / PointFinder | A | acquired genes and chromosomal point mutations | [CGE website](https://www.genomicepidemiology.org/) |
| mob-suite | A | plasmid replicon, relaxase, mobility and typing | [GitHub](https://github.com/phac-nml/mob-suite) |
| PlasFlow | A | chromosome versus plasmid sequence classification | [GitHub](https://github.com/smaegol/PlasFlow) |
| mobileOG-db | A | orthology database of mobile-element proteins | [GitHub](https://github.com/clb21565/mobileOG-db) |
| MGEfinder | A | mobile genetic element discovery from isolates | [GitHub](https://github.com/bhattlab/MGEfinder) |
| IntegronFinder | A | integron and gene-cassette detection | [GitHub](https://github.com/gem-pasteur/Integron_Finder) |
| geNomad | A | virus and plasmid/MGE identification | [GitHub](https://github.com/apcamargo/genomad) |
| IslandPath-DIMOB | A | genomic island prediction | [GitHub](https://github.com/brinkmanlab/islandpath) |
| VirSorter2 | A | provirus / viral sequence detection | [GitHub](https://github.com/simroux/VirSorter2) |
| PhiSpy | A | prophage boundary prediction | [GitHub](https://github.com/linsalrob/PhiSpy) |
| CRISPRCasFinder | A | CRISPR arrays and cas systems | [official site](https://crisprcas.i2bc.paris-saclay.fr) |

### Read mapping and variant calling (reference route, module 12)

| Tool | P | Purpose | Source |
| --- | --- | --- | --- |
| BWA | S | BWA-MEM short-read alignment to a shared reference | [GitHub](https://github.com/lh3/bwa) |
| samtools | A | BAM sorting/indexing, flagstat, depth and pileup | [GitHub](https://github.com/samtools/samtools) |
| bcftools | A | joint variant calling, normalization, filtering, VCF/genotype export | [GitHub](https://github.com/samtools/bcftools) |
| htslib (tabix/bgzip) | A | compressed-VCF indexing | [GitHub](https://github.com/samtools/htslib) |
| Qualimap | A | per-BAM alignment and coverage QC | [GitHub](https://github.com/kokonech/QualiMap) |
| vcf2phylip | A | turn a SNP VCF into FASTA/Phylip for a reference-route tree | [GitHub](https://github.com/edgardomortiz/vcf2phylip) |

### Microbial GWAS and post-GWAS (module 13)

| Tool | P | Purpose | Source |
| --- | --- | --- | --- |
| Scoary | A | gene-based pan-GWAS on the Panaroo/Roary matrix (Fisher, pairwise, BH) | [GitHub](https://github.com/AdmiralenOla/Scoary) |
| PLINK | A | SNP association with IBS/MDS population-structure control | [website](https://www.cog-genomics.org/plink/) |
| pyseer | A | microbial gene/SNP/k-mer GWAS with a distance-kernel mixed model | [GitHub](https://github.com/mgalardini/pyseer) |

### Pangenome, phylogeny and molecular dating

| Tool | P | Purpose | Source |
| --- | --- | --- | --- |
| Panaroo | A | graph-based pangenome clustering | [GitHub](https://github.com/gtonkinhill/panaroo) |
| Roary | A | traditional pangenome pipeline | [GitHub](https://github.com/sanger-pathogens/Roary) |
| snippy | A | rapid core-SNP calling against a reference | [GitHub](https://github.com/tseemann/snippy) |
| Gubbins | A | detect and mask recombination | [GitHub](https://github.com/nickjcroucher/gubbins) |
| snp-sites | A | extract variable SNP sites from an alignment | [GitHub](https://github.com/tseemann/snp-sites) |
| snp-dists | A | pairwise SNP distance matrix | [GitHub](https://github.com/tseemann/snp-dists) |
| IQ-TREE 3 | A | maximum-likelihood phylogeny (IQ-TREE 2 still supported) | [GitHub](https://github.com/iqtree/iqtree3) |
| FastTree | A | fast approximate ML tree for preview | [official site](http://www.microbesonline.org/fasttree/) |
| MAFFT | A | multiple sequence alignment | [official site](https://mafft.cbrc.jp/alignment/software/) |
| TreeTime | A | molecular clock, time tree, ancestors and migration | [GitHub](https://github.com/neherlab/treetime) |

### Visualization and interactive exploration

Module 11 produces static figures locally and packages files for interactive web viewers.
Platform column: A = applies to any tree, alignment or matrix.

| Tool | P | Purpose | Source |
| --- | --- | --- | --- |
| ggtree | A | grammar-of-graphics phylogenetic tree rendering in R | [GitHub](https://github.com/YuLab-SMU/ggtree) |
| ggtreeExtra | A | aligned annotation layers (strips, bars, boxes) beside a tree | [GitHub](https://github.com/YuLab-SMU/ggtreeExtra) |
| treeio | A | read and write many tree formats (Newick, Nexus, BEAST) | [GitHub](https://github.com/YuLab-SMU/treeio) |
| ape | A | core R phylogenetics: tree I/O, handling and statistics | [GitHub](https://github.com/emmanuelparadis/ape) |
| phangorn | A | R phylogenetic estimation and tree manipulation | [GitHub](https://github.com/KlausVigo/phangorn) |
| GrapeTree | A | minimum spanning tree of cgMLST profiles or core alignments | [GitHub](https://github.com/achtman-lab/GrapeTree) |
| pheatmap | A | clustered heatmaps for SNP distance and gene matrices | [GitHub](https://github.com/raivokolde/pheatmap) |
| ComplexHeatmap | A | advanced heatmaps aligned with tree annotations | [GitHub](https://github.com/jokergoo/ComplexHeatmap) |
| ggplot2 | A | plotting grammar underlying the ggtree figures | [GitHub](https://github.com/tidyverse/ggplot2) |
| FigTree | A | desktop GUI tree viewer and exporter | [GitHub](https://github.com/rambaut/figtree) |
| iTOL | A | web tree annotation with color strips and binary tracks | [website](https://itol.embl.de) |
| Microreact | A | interactive tree with map and timeline on the web | [website](https://microreact.org) |
| Phandango | A | interactive tree against pangenome and metadata | [website](https://phandango.net) |
| icytree | A | fast browser-only tree viewer, no account needed | [website](https://icytree.org) |

### Data retrieval and workflow engine

| Tool | P | Purpose | Source |
| --- | --- | --- | --- |
| NCBI datasets | A | download genomes, genes and metadata | [GitHub](https://github.com/ncbi/datasets) |
| SRA toolkit | A | fetch and convert Sequence Read Archive data | [GitHub](https://github.com/ncbi/sra-tools) |
| Nextflow | A | workflow engine used to run CLEAN | [GitHub](https://github.com/nextflow-io/nextflow) |

### Beyond bacteria: viruses, fungi and probiotics

About half of the workflow (read QC, host removal, mapping, variant calling, coverage,
alignments, maximum-likelihood trees and reporting) is domain-agnostic. The
[Beyond bacteria](https://easywgs.readthedocs.io/en/latest/extensibility/) guidebook page
gives the full Venn comparison, the stage-by-domain matrix and a phased extension roadmap.
The representative domain-specific programs below are catalogued in stages 26 to 31; the
shared programs (minimap2, bcftools, mosdepth, IQ-TREE 3 and so on) are listed above.

| Tool | Domain | Purpose | Source |
| --- | --- | --- | --- |
| nf-core/viralrecon | Viral | reference Illumina/ONT viral workflow template | [GitHub](https://github.com/nf-core/viralrecon) |
| iVar | Viral | amplicon primer trimming and consensus | [GitHub](https://github.com/andersen-lab/ivar) |
| Nextclade / Pangolin | Viral | SARS-CoV-2 clade and lineage assignment | [GitHub](https://github.com/nextstrain/nextclade) |
| CheckV / VADR | Viral | viral completeness and reference-guided annotation | [GitHub](https://github.com/chklovski/CheckV) |
| HAPHPIPE / V-pipe | Viral | HIV intrahost haplotypes and quasispecies | [GitHub](https://github.com/gwcbi/haphpipe) |
| HIV-TRACE / HyPhy | Viral | TN93 transmission clusters and selection | [GitHub](https://github.com/veg/hivtrace) |
| AAFTF | Fungal | haploid fungal assembly and polishing | [GitHub](https://github.com/stajichlab/AAFTF) |
| BUSCO | Fungal | eukaryotic single-copy orthologue completeness | [GitLab](https://gitlab.com/ezlab/busco) |
| funannotate / BRAKER3 | Fungal | eukaryotic gene annotation with introns | [GitHub](https://github.com/nextgenusfs/funannotate) |
| ITSx / UNITE | Fungal | ITS barcode extraction and reference database | [UNITE](https://unite.ut.ee/) |
| OrthoFinder / GET_HOMOLOGUES | Fungal | orthogroup-based comparative genomics | [GitHub](https://github.com/davidemms/OrthoFinder) |
| Control-FREEC | Fungal | copy-number and aneuploidy detection | [GitHub](https://github.com/BoevaLab/FREEC) |
| antiSMASH / run_dbcan | Fungal | fungal secondary metabolites and CAZymes | [GitHub](https://github.com/antismash/antismash) |
| EFSA QPS / FEEDAP | Probiotic | strain safety frame (acquired AMR, toxigenicity) | [EFSA](https://www.efsa.europa.eu/) |
| BAGEL4 / CRISPRCasFinder | Probiotic | bacteriocin, RiPP and CRISPR benefit evidence | [BAGEL4](http://bagel4.molgenrug.nl/) |

Probiotics are a safety-and-benefit configuration over the bacterial track (the yeast
*Saccharomyces boulardii* uses the fungal track), not a fourth biological domain.

## Hardware note

A local FCS-GX run needs roughly 470 GB of reference data and about 512 GB RAM. On an ordinary
server, keep CheckM2 and GUNC as the gate and run FCS-GX on usegalaxy.org instead. Long-read
polishing environments (Medaka, Trycycler) are kept in a separate `longread` conda environment
to avoid dependency conflicts.

## Repository layout

Numbered folders hold the runnable scripts; `run_assembly.sh` and `run_mapping.sh`
are the two parallel route drivers (de novo assembly and reference BAM/VCF mapping,
the latter extended by module 13 microbial GWAS); module `11_visualization` renders
the static R figures and assembles the iTOL/Microreact/Phandango/GrapeTree upload
bundles; `docs/` holds the bilingual MkDocs Material guidebook;
`.github/workflows/` builds the documentation, runs the static and functional tests, and
publishes the container image; `tests/` holds the deterministic smoke test and static
checks. The workflow consolidates hands-on
practice from LLQ95/Practical-Encyclopedia-of-Whole-Genome-Analysis and adds a
two-layer decontamination gate, pathogen-specific serotyping, a complete long-read
polishing chain, a closed TreeTime loop, a transparent reference mapping/variant
route, microbial GWAS with post-GWAS plotting, and a unified downstream
visualization layer.

## Contributing, license, citation

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CHANGELOG.md](CHANGELOG.md). Released under the
MIT license; citation metadata is in [CITATION.cff](CITATION.cff). When adding a tool, update
the numbered script, the install script and this catalog together, and keep the English and
Chinese README pages in sync.
