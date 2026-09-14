# Tool map (short/long-read reference)

The table summarizes tools by stage and marks the sequencing platform to which each mainly
applies. "Shared" means it applies to short-read, long-read and hybrid assemblies alike. The
script location is the numbered folder.

## Data acquisition and QC

| Tool | Platform | Stage | Role |
| --- | --- | --- | --- |
| fastp | short / single long | 01 | adapter removal, quality trimming, report |
| FastQC/MultiQC | shared | 01 | QC view and batch summary |
| porechop/chopper | long | 01b | long-read adapter removal, length/quality split |
| NanoPlot | long | 01b | length/quality distribution |
| Filtlong | long | 01b | quality-based long-read filtering |
| NCBI datasets/SRA toolkit | shared | acquisition | download public reads and assemblies |

## Decontamination

| Tool | Platform | Stage | Role |
| --- | --- | --- | --- |
| CLEAN | short/long/FASTA | 02 | read-level keep-by-target |
| Kraken2/Bracken | mainly short | 02 | taxonomic composition scout |
| BBDuk/HoCoRT/deacon | short | 02 | reference/adapter removal |
| CheckM2 | assembly | 04 | completeness, contamination |
| GUNC | assembly | 04 | chimeric-genome detection |
| FCS-GX/BlobToolKit | assembly | 04 | foreign-fragment cleaning and visualization |

## Assembly and polishing

| Tool | Platform | Stage | Role |
| --- | --- | --- | --- |
| Unicycler | short/hybrid | 03 | isolate assembly, bold hybrid, tends to circularize |
| SPAdes | short/hybrid | 03 | --isolate, --nanopore/--pacbio |
| Flye | long | 03 | long-read assembly and circularization flags |
| Canu | long | 03 | conservative long-read assembly |
| dragonflye | long | 03 | SPAdes-style long-read pipeline (alternative) |
| Trycycler | long | 03 | multi-assembly consensus, finished-genome gold standard |
| minimap2+Racon | long | 03 | long-read self-correction (2–3 rounds max) |
| Medaka | ONT | 03 | neural-network consensus polishing |
| Pilon | hybrid/short | 03 | short-read error filling |
| circlator | assembly | 03 | circularization and origin fixing |
| QUAST/seqkit/assembly-stats | shared | 03/04 | assembly statistics |

## Annotation and typing

| Tool | Platform | Stage | Role |
| --- | --- | --- | --- |
| Prokka/Bakta/Prodigal | shared | 05 | structural annotation |
| eggNOG-mapper | shared | 05 | GO/KEGG/COG |
| mlst | shared | 06 | seven-gene MLST |
| Kleborate(Kaptive) | shared | 06 | Klebsiella ST, K/O antigens, AMR and virulence |
| ECTyper/ShigEiFinder | shared | 06 | E. coli O:H, Shigella/EIEC |
| SeqSero2/SISTR | shared | 06 | Salmonella antigen and serovar |
| chewBBACA | shared | 06 | full cgMLST workflow |

## AMR, virulence and mobile elements (07)

| Category | Tools |
| --- | --- |
| AMR/virulence databases | abricate (ResFinder/VFDB/CARD/MEGARes/ecoli_vf), AMRFinderPlus, RGI |
| Point mutations | PointFinder |
| Plasmids | mob-suite, PlasmidFinder, PLSDB, PlasFlow |
| Integrons/IS/ICE | IntegronFinder, ISEScan/ISfinder, mobileOG, MGEfinder, oriT/relaxase |
| Phages/genomic islands | VirSorter2, PhiSpy, IslandPath, PHASTER, genomad |
| CRISPR | CRISPRCasFinder |

## Comparison, evolution and dereplication

| Tool | Stage | Role |
| --- | --- | --- |
| Panaroo/Roary | 08 | pangenome |
| snippy/Gubbins/snp-sites/IQ-TREE/FastTree/snp-dists | 09 | core-SNP tree and distances |
| TreeTime | 10 | clock, time tree, ancestors, migration |
| mash/dereplicator/cd-hit | support | genome dereplication and fast clustering |
| MAFFT/MUMmer | support | alignment and synteny |

## Extended topics (not default steps)

Genomic GWAS/post-GWAS, TWAS, RNA-seq and HUMAnN/MetaPhlAn belong to transcriptomics,
association or metagenomics. The guidebook reserves chapters that describe how they connect
to the WGS main chain, but they are not part of the run_all default chain so that the isolate
workflow is not mixed with unrelated analyses.
