# Software versions and currency

easyWGS does not pin tools to a single release: the installer resolves the current build from Bioconda, and the scripts call stable command interfaces so that newer releases work without edits. The table below records the current upstream release of every external tool used by the workflow, checked on 2026-09-14 against each project's official GitHub repository (latest release or newest version tag). R packages are distributed through CRAN or Bioconductor and do not carry GitHub release tags; web tools have no local version.

Use this page to audit an existing installation. To reproduce the check, `git ls-remote --tags <repo>` lists every tag, or open the repository releases page linked in the README tool list.

## Read processing and quality control

| Tool | Current release | Upstream |
|---|---|---|
| fastp | 1.3.7 | OpenGene/fastp |
| FastQC | 0.12.1 | s-andrews/FastQC |
| MultiQC | 1.35 | MultiQC/MultiQC |
| SeqKit | 2.13.0 | shenwei356/seqkit |
| chopper | 0.14.1 | wdecoster/chopper |
| NanoPlot | 1.48.0 | wdecoster/NanoPlot |
| Porechop | 0.2.4 | rrwick/Porechop (original repo; community forks exist) |
| Filtlong | 0.3.1 | rrwick/Filtlong |

## Decontamination and assembly assessment

| Tool | Current release | Upstream |
|---|---|---|
| Kraken2 | 2.17.1 | DerrickWood/kraken2 |
| Bracken | 3.1 | jenniferlu717/Bracken |
| CLEAN | 1.2.0 | rki-mf1/clean |
| BBMap | 36.20 (GitHub tag; later builds on SourceForge) | BioInfoTools/BBMap |
| NCBI FCS-GX | 0.5.5 | ncbi/fcs |
| CheckM2 | 1.1.0 | chklovski/CheckM2 |
| GUNC | 1.1.1 | grp-bork/gunc |
| BlobToolKit | 4.5.5 | genomehubs/blobtoolkit |
| Mash | 2.3 | marbl/Mash |
| QUAST | 5.3.0 | ablab/quast |

## Assembly and polishing

| Tool | Current release | Upstream |
|---|---|---|
| SPAdes | 4.3.0 | ablab/spades |
| Unicycler | 0.5.1 | rrwick/Unicycler |
| Flye | 2.9.6 | mikolmogorov/Flye |
| Canu | 2.3 | marbl/canu |
| Dragonflye | 1.2.1 | rpetit3/dragonflye |
| Trycycler | 0.5.6 | rrwick/Trycycler |
| minimap2 | 2.31 (r1302) | lh3/minimap2 |
| Racon | 1.5.0 | lbcb-sci/racon |
| Medaka | 2.2.2 | nanoporetech/medaka |
| Pilon | 1.24 | broadinstitute/pilon |
| Circlator | 1.5.5 | sanger-pathogens/circlator |
| MUMmer | 4.0.1 | mummer4/mummer |
| cd-hit | 4.8.1 | weizhongli/cdhit |

## Annotation

| Tool | Current release | Upstream |
|---|---|---|
| Prokka | 1.15.6 | tseemann/prokka |
| Bakta | 1.12.1 | oschwengers/bakta |
| Prodigal | 2.60 | hyattpd/Prodigal |
| eggNOG-mapper | 2.1.15 | jhcepas/eggnog-mapper |

## Typing (MLST, serotyping, cgMLST)

| Tool | Current release | Upstream |
|---|---|---|
| mlst | 2.35.0 | tseemann/mlst |
| Kleborate | 3.2.4 | klebgenomics/Kleborate |
| ECTyper | 2.0.0 | phac-nml/ecoli_serotyping |
| ShigEiFinder | 1.3.5 | LanLab/ShigEiFinder |
| SeqSero2 | 1.3.2 | denglab/SeqSero2 |
| SISTR | 1.1.3 | phac-nml/sistr_cmd |
| chewBBACA | 3.5.4 | B-UMMI/chewBBACA |

## AMR, virulence and mobile genetic elements

| Tool | Current release | Upstream |
|---|---|---|
| abricate | 1.4.0 | tseemann/abricate |
| AMRFinderPlus | 4.2.7 | ncbi/amr |
| RGI (CARD) | 6.0.8 | arpcard/rgi |
| MOB-suite | 3.1.9 | phac-nml/mob-suite |
| PlasFlow | 1.1 | smaegol/PlasFlow |
| mobileOG-db | beatrix 1.0 (database) | clb21565/mobileOG-db |
| MGEfinder | 1.0.6 | bhattlab/MGEfinder |
| IntegronFinder | 2.0.6 | gem-pasteur/Integron_Finder |
| geNomad | 1.12.0 | apcamargo/genomad |
| IslandPath-DIMOB | 1.0.6 | brinkmanlab/islandpath |
| PhiSpy | 5.0.10 | linsalrob/PhiSpy |
| VirSorter2 | 2.2.3 (Bioconda; GitHub tag 2.0.alpha) | simroux/VirSorter2 |

## Reference mapping and variant calling (module 12)

| Tool | Current release | Upstream |
|---|---|---|
| BWA | 0.7.19 | lh3/bwa |
| samtools | 1.24 | samtools/samtools |
| bcftools | 1.24 | samtools/bcftools |
| htslib (tabix/bgzip) | 1.24 (tracks the samtools release) | samtools/htslib |
| Qualimap | 2.3 (Bioconda; no GitHub release tag) | kokonech/QualiMap |
| vcf2phylip | 2.8 | edgardomortiz/vcf2phylip |

## Microbial GWAS and post-GWAS (module 13)

| Tool | Current release | Upstream |
|---|---|---|
| Scoary | 1.6.9 | AdmiralenOla/Scoary |
| PLINK | 1.9 (plink-ng; PLINK 2.0 remains an alpha line) | chrchang/plink-ng |
| pyseer | 1.4.2 | mgalardini/pyseer |

## Pangenome, phylogeny and molecular clock

| Tool | Current release | Upstream |
|---|---|---|
| Panaroo | 1.8.0 | gtonkinhill/panaroo |
| Roary | 3.13.0 | sanger-pathogens/Roary |
| snippy | 4.6.0 | tseemann/snippy |
| Gubbins | 3.4.3 | nickjcroucher/gubbins |
| snp-sites | 2.3.3 | tseemann/snp-sites |
| snp-dists | 1.2.0 | tseemann/snp-dists |
| IQ-TREE 3 | 3.1.4 | iqtree/iqtree3 |
| IQ-TREE 2 (legacy) | 2.4.0 | iqtree/iqtree2 |
| TreeTime | 0.12.1 | neherlab/treetime |
| MAFFT | 7 series (project site) | mafft.cbrc.jp |
| FastTree | 2.1.11 (project site) | microbenet/FastTree |

The Bioconda package is named `iqtree` and now provides IQ-TREE 3 with the binary `iqtree3`; the same package supplied `iqtree2` under version 2. The phylogeny scripts resolve the binary in the order iqtree3, iqtree2, iqtree, so a machine that still holds version 2 runs unchanged.

## Workflow engine, data retrieval and visualization

| Tool | Current release | Upstream |
|---|---|---|
| Nextflow | 26.04.6 (stable) | nextflow-io/nextflow |
| NCBI datasets | 18.37.0 | ncbi/datasets |
| sra-tools | 3 series (Bioconda; GitHub tags follow the VDB scheme) | ncbi/sra-tools |
| GrapeTree | 1.5.0 | achtman-lab/GrapeTree |
| FigTree | 1.4.4 | rambaut/figtree |
| Phandango | 0.5.0 | jameshadfield/phandango |
| ggtree, treeio, ggtreeExtra | current Bioconductor release | YuLab-SMU |
| ape, phangorn, ggplot2, pheatmap | current CRAN release | respective CRAN pages |
| ComplexHeatmap | current Bioconductor release | jokergoo/ComplexHeatmap |
| iTOL, Microreact | web service, no local version | itol.embl.de / microreact.org |

Release dates move quickly and a table like this ages; if a tool below is older than the value shown here, update it through Bioconda and open an issue so the table can be refreshed.
