# EasyIsolate

**English** | [简体中文](README.zh-CN.md)

EasyIsolate is a reproducible, numbered-directory workflow for bacterial isolate
whole-genome sequencing (WGS). It covers Illumina short reads, Oxford Nanopore and
PacBio long reads, and hybrid assembly, and it chains quality control, two-layer
decontamination, assembly and polishing, assembly QC, annotation, MLST, species-specific
serotyping, cgMLST, resistance/virulence/mobile-element screening, the pangenome, a core-SNP
phylogeny and a TreeTime time-scaled tree. The layout follows the teaching-oriented style of
EasyMicrobiome and EasyMetagenome: edit the parameters at the top of each numbered script and
run the stages in order.

Full documentation: https://easyisolate.readthedocs.io (English by default, switchable to
Simplified Chinese).

## Workflow by sequencing platform

```text
Illumina short reads
  01 QC(fastp) -> 02 read decontamination(CLEAN) -> 03 Unicycler (SPAdes alt) -> 04 QC gate -> ...
ONT / PacBio long reads
  01b long QC(porechop + NanoPlot + Filtlong) -> 03 Flye -> Racon -> Medaka (optional Trycycler) -> ...
Hybrid
  01 + 01b -> 02 (clean short reads) -> 03 Unicycler --mode bold / SPAdes hybrid + Pilon -> ...

04  QUAST + CheckM2 + GUNC + (optional) FCS-GX assembly-level decontamination gate
05  Prokka/Bakta, Prodigal, eggNOG (GO/KEGG/COG)
06  6.1 MLST, 6.2 species-specific serotyping, 6.3 chewBBACA cgMLST
07  abricate databases + AMRFinder/RGI/PointFinder + geNomad/Mob-suite/IntegronFinder
08  Panaroo (Roary alternative) pangenome
09  snippy -> Gubbins -> IQ-TREE -> snp-dists core-SNP phylogeny
10  TreeTime clock filtering, time tree, ancestral reconstruction, homoplasy, migration
99  merged master table and figures
```

## Quick start

```bash
bash 00_install/install_env.sh      # create conda environments (incl. the longread one)
bash 00_install/download_db.sh      # download databases once
cp config/samplesheet.csv config/my_samples.csv   # edit paths, platform and species
bash run_all.sh config/my_samples.csv             # run everything
bash run_all.sh config/my_samples.csv 06          # or resume from a given step
```

The samplesheet field `platform` is one of illumina / nanopore / pacbio / hybrid and selects
the assembly route; `species` is one of kpsc / ecoli / salm / listeria / other and selects the
typing schedule. Final assemblies are standardized to `03_assembly/genomes/{id}.fasta`
(fragments shorter than 200 nt removed), which every later module consumes.

## Species-specific typing schedule (module 06)

| Group | 7-gene MLST | Serotype / surface antigens | cgMLST schema |
| --- | --- | --- | --- |
| K. pneumoniae complex (kpsc) | mlst | Kleborate (built-in Kaptive, K/O antigens) | INNUENDO or custom |
| E. coli / Shigella (ecoli) | mlst | ECTyper (O:H) + ShigEiFinder (Shigella/EIEC) | EnteroBase E./Shigella |
| Salmonella (salm) | mlst | SeqSero2 + SISTR | INNUENDO cgMLST99 |
| L. monocytogenes (listeria) | mlst | molecular serogroup via cgMLST | Pasteur cgMLST |
| other | mlst auto-detect | extend as needed | PrepExternalSchema |

## WGS tool catalog

Platform column: S = mainly short reads, L = mainly long reads, A = applies to both/assemblies.
Every link was checked against the upstream repository or official site. These are the tools
used or recommended by EasyIsolate, organized by analysis stage.

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
| Flye | L | long-read assembler with circular contig flags | [GitHub](https://github.com/mikolmogorov/Flye) |
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

### Pangenome, phylogeny and molecular dating

| Tool | P | Purpose | Source |
| --- | --- | --- | --- |
| Panaroo | A | graph-based pangenome clustering | [GitHub](https://github.com/gtonkinhill/panaroo) |
| Roary | A | traditional pangenome pipeline | [GitHub](https://github.com/sanger-pathogens/Roary) |
| snippy | A | rapid core-SNP calling against a reference | [GitHub](https://github.com/tseemann/snippy) |
| Gubbins | A | detect and mask recombination | [GitHub](https://github.com/nickjcroucher/gubbins) |
| snp-sites | A | extract variable SNP sites from an alignment | [GitHub](https://github.com/tseemann/snp-sites) |
| snp-dists | A | pairwise SNP distance matrix | [GitHub](https://github.com/tseemann/snp-dists) |
| IQ-TREE 2 | A | maximum-likelihood phylogeny | [GitHub](https://github.com/iqtree/iqtree2) |
| FastTree | A | fast approximate ML tree for preview | [official site](http://www.microbesonline.org/fasttree/) |
| MAFFT | A | multiple sequence alignment | [official site](https://mafft.cbrc.jp/alignment/software/) |
| TreeTime | A | molecular clock, time tree, ancestors and migration | [GitHub](https://github.com/neherlab/treetime) |

### Data retrieval and workflow engine

| Tool | P | Purpose | Source |
| --- | --- | --- | --- |
| NCBI datasets | A | download genomes, genes and metadata | [GitHub](https://github.com/ncbi/datasets) |
| SRA toolkit | A | fetch and convert Sequence Read Archive data | [GitHub](https://github.com/ncbi/sra-tools) |
| Nextflow | A | workflow engine used to run CLEAN | [GitHub](https://github.com/nextflow-io/nextflow) |

## Hardware note

A local FCS-GX run needs roughly 470 GB of reference data and about 512 GB RAM. On an ordinary
server, keep CheckM2 and GUNC as the gate and run FCS-GX on usegalaxy.org instead. Long-read
polishing environments (Medaka, Trycycler) are kept in a separate `longread` conda environment
to avoid dependency conflicts.

## Repository layout

Numbered folders hold the runnable scripts; `docs/` holds the bilingual MkDocs Material
guidebook; `.github/workflows/` builds the documentation. The workflow consolidates hands-on
practice from LLQ95/Practical-Encyclopedia-of-Whole-Genome-Analysis and adds a two-layer
decontamination gate, pathogen-specific serotyping, a complete long-read polishing chain and a
closed TreeTime loop.

## Contributing, license, citation

See [CONTRIBUTING.md](CONTRIBUTING.md) and [CHANGELOG.md](CHANGELOG.md). Released under the
MIT license; citation metadata is in [CITATION.cff](CITATION.cff). When adding a tool, update
the numbered script, the install script and this catalog together, and keep the English and
Chinese README pages in sync.
