# Tool encyclopedia: recommended, alternative and legacy tools

This page is the tool-lineage catalog of EasyWGS. It lists, for every analysis stage, the tools commonly encountered in bacterial isolate whole-genome sequencing and marks the status and lineage of each. It complements the short/long-read Tool map, which lists only the software used by default in EasyWGS. This catalog aims to cover the choices still seen in the literature and in practice, so that older papers remain readable, legacy pipelines can be reproduced, and a substitute can be chosen when the default does not fit.

## How to read the status

- Recommended default is what the numbered EasyWGS modules use; these tools currently balance accuracy, speed and active maintenance.
- Alternative marks actively maintained tools that can replace the default and may be preferable for particular data or constraints.
- Legacy (still usable) marks older tools that usually have a named successor but still install and run; they appear in older papers and in reproducibility work. A lineage arrow indicates the currently favored direction, not that the old tool is invalid; several legacy tools remain accepted, for example both CheckM and CheckM2 are accepted for public genome submission.

In the lineage column an arrow runs from the older generation toward its successor; a dash means there is no single successor or that distinct approaches coexist. The platform column gives the data type each tool mainly serves.

## 1. Data acquisition

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| SRA Toolkit (fasterq-dump) | Recommended default | - | shared | download public SRA/ENA reads |
| NCBI datasets / ENA filer | Alternative | - | shared | download genomes, assemblies and reads |
| EDirect (esearch/efetch) | Alternative | - | shared | scripted NCBI queries |
| fastq-dump | Legacy (still usable) | -> fasterq-dump | shared | older SRA extraction, slower single-thread |
| Dorado | Recommended default | replaces Guppy/Albacore | ONT | current ONT basecaller (upstream of FASTQ) |
| Guppy | Legacy (still usable) | -> Dorado | ONT | previous ONT basecaller |
| Albacore | Legacy (still usable) | -> Guppy -> Dorado | ONT | early ONT basecaller |
| SMRT Link / ccs (HiFi) | Alternative | replaces Quiver pipeline | PacBio | PacBio HiFi consensus generation |

## 2. Short-read QC

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| fastp | Recommended default | replaces Trimmomatic/Sickle in role | short | one-pass adapter/quality/length trim plus HTML report |
| FastQC + MultiQC | Recommended default | - | shared | per-sample QC plots and aggregate report |
| Cutadapt | Alternative | - | short | precise adapter/primer trimming, still widely used |
| AdapterRemoval v2 | Alternative | - | short | adapter trim and paired-read overlap merging |
| BBDuk (BBTools) | Alternative | - | short | k-mer trim/filter, also used for decontam |
| Trimmomatic | Legacy (still usable) | -> fastp | short | classic sliding-window adapter/quality trim |
| Sickle | Legacy (still usable) | -> fastp | short | simple sliding-window quality trim |
| FASTX-Toolkit | Legacy (still usable) | -> fastp/Cutadapt | short | older read manipulation and QC |
| PRINSEQ(-lite) | Legacy (still usable) | -> fastp | short | older QC, filtering and complexity |
| AfterQC / NGS QC Toolkit | Legacy (still usable) | -> fastp | short | early QC/filtering suites |

## 3. Long-read QC

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| NanoPlot / NanoComp | Recommended default | - | long | read length/quality/yield plots |
| chopper | Recommended default | replaces NanoFilt/NanoLyse in role | long | fast quality/length filtering (Rust) |
| Filtlong | Recommended default | - | long | quality-weighted long-read filtering |
| Porechop_ABI | Alternative | - | long | ab-initio adapter/barcode trimming fork |
| Porechop | Alternative | maintenance limited | long | classic ONT adapter/barcode trimmer |
| NanoFilt / NanoLyse | Legacy (still usable) | -> chopper/Filtlong | long | streaming filter and contaminant removal |
| NanoQC | Alternative | - | long | quick per-run quality comparison |

## 4. Read-level decontamination

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| CLEAN | Recommended default | - | short/long/FASTA | keep-by-target contamination removal |
| Kraken2 + Bracken | Recommended default | Kraken2 replaces Kraken1 | mainly short | taxonomic composition scouting before cleaning |
| BBDuk / BBsplit | Alternative | - | short | remove or bin reads against references |
| HoCoRT / deacon | Alternative | - | short | host-read removal |
| KneadData | Alternative | - | short | integrated QC plus host removal pipeline |
| FastQ Screen | Alternative | - | short | check whether reads match multiple genomes |
| Kraken 1 | Legacy (still usable) | -> Kraken2 | short | first-generation exact k-mer classifier |
| DeconSeq | Legacy (still usable) | -> BBDuk/CLEAN | short | early host/contaminant read remover |

## 5. Short/hybrid assembly

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| SPAdes | Recommended default | replaces Velvet/IDBA in role | short/hybrid | de Bruijn isolate assembler (--isolate) |
| Unicycler | Recommended default | - | short/hybrid | bold hybrid assembly, tends to circularize |
| Shovill | Alternative | - | short | faster SPAdes wrapper with normalized options |
| SKESA | Alternative | - | short | NCBI conservative strategic-k-mer assembler |
| MEGAHIT | Alternative | - | short/meta | very memory-efficient de Bruijn assembler |
| MaSuRCA | Alternative | - | hybrid | hybrid OLC/de Bruijn assembler |
| ABySS | Alternative | - | short | scalable paired-end assembler |
| A5-miseq | Legacy (still usable) | -> SPAdes/Unicycler | short | turnkey MiSeq assembler |
| IDBA / IDBA-UD | Legacy (still usable) | -> SPAdes/MEGAHIT | short/meta | iterative k-mer assembler |
| Velvet (+VelvetOptimiser) | Legacy (still usable) | -> SPAdes | short | original de Bruijn assembler |
| SOAPdenovo2 | Legacy (still usable) | -> SPAdes | short | large-genome short-read assembler |
| MIRA / Edena / CISA | Legacy (still usable) | -> SPAdes/Unicycler | short | early overlap/consensus and merge tools |

## 6. Long-read assembly

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| Flye | Recommended default | - | long | repeat-aware long-read/metagenome assembler |
| Trycycler | Recommended default | - | long | consensus across multiple assemblies, finished standard |
| Canu | Alternative | replaces Celera Assembler | long | conservative OLC long-read assembler |
| hifiasm | Alternative | - | PacBio HiFi | fast HiFi assembler with phasing |
| wtdbg2 | Alternative | - | long | fast fuzzy de Bruijn long-read assembler |
| Raven | Alternative | - | long | fast OLC assembler derived from miniasm |
| dragonflye | Alternative | - | long | SPAdes-style pipeline wrapping Flye/Raven |
| NextDenovo / NECAT | Alternative | - | long | efficient correction-then-assemble pipelines |
| miniasm | Legacy (still usable) | -> Flye/Trycycler | long | ultrafast raw layout, needs Racon polishing |
| SMARTdenovo | Legacy (still usable) | -> Flye/Canu | long | early OLC long-read assembler |
| Celera Assembler | Legacy (still usable) | -> Canu | long | original Sanger/long-read assembler |
| HGAP / FALCON | Legacy (still usable) | -> Canu/hifiasm (HiFi) | PacBio CLR | old PacBio SMRT assembly pipelines |

## 7. Polishing

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| Medaka | Recommended default | replaces Nanopolish in convenience | ONT | neural consensus polish, no FAST5 needed |
| Racon | Recommended default | - | long | partial-order long-read self-correction (2-3 rounds) |
| Pilon | Recommended default | - | short/hybrid | short-read error correction and gap filling |
| NextPolish | Alternative | - | short/long | two-mode short/long polisher |
| Polypolish / POLCA | Alternative | - | short | short-read polishers limiting error introduction |
| ntEdit / Sealer | Alternative | - | short | bloom-filter correction and gap closing |
| Apollo | Alternative | - | shared | large-genome assembly polishing |
| Nanopolish | Legacy (still usable) | -> Medaka | ONT | signal-level polish requiring FAST5 |
| Quiver / Arrow (GCpp) | Legacy (still usable) | -> ccs/DeepVariant (HiFi) | PacBio | old PacBio consensus polishers |

## 8. Assembly QC and contamination

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| QUAST | Recommended default | - | shared | N50, contiguity and misassembly metrics |
| seqkit / assembly-stats | Recommended default | - | shared | sequence statistics and manipulation |
| CheckM2 | Recommended default | replaces CheckM1 | assembly | ML completeness/contamination, fast and lineage-robust |
| GUNC | Recommended default | - | assembly | chimeric-genome / taxonomic inconsistency detection |
| FCS-GX | Recommended default | - | assembly | NCBI foreign-fragment contamination screener |
| BlobToolKit (BlobTools2) | Alternative | - | assembly | coverage/taxonomy/GC interactive contamination view |
| BUSCO | Alternative | - | shared | single-copy ortholog completeness (mainly eukaryotes) |
| Merqury | Alternative | - | assembly | k-mer based consensus QV |
| CheckM (v1) | Alternative | succeeded by CheckM2 | assembly | lineage-marker quality, still accepted and interpretable |
| RefineM | Legacy (still usable) | -> CheckM2/GUNC | assembly | older bin/contamination refinement |
| proDeGe | Legacy (still usable) | -> FCS-GX/CheckM2 | assembly | early contamination removal for genomes/MAGs |

## 9. Structural/functional annotation

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| Bakta | Recommended default | modern successor in role to Prokka | shared | standardized annotation with stable RefSeq/UniRef IDs |
| Prodigal | Recommended default | replaces Glimmer in role | shared | prokaryotic gene/CDS caller |
| eggNOG-mapper | Recommended default | - | shared | COG/GO/KEGG functional assignment |
| DIAMOND | Recommended default | - | shared | fast BLAST-like protein search |
| Prokka | Alternative | succeeded in role by Bakta | shared | rapid classic annotation, CLI-compatible with Bakta |
| PGAP (NCBI) | Alternative | - | shared | NCBI submission-grade annotation pipeline |
| DFAST | Alternative | - | shared | web/CLI annotation with DDBJ support |
| InterProScan | Alternative | - | shared | protein domain and GO mapping |
| BLAST+ | Alternative | - | shared | reference sequence similarity search |
| barrnap | Recommended default | replaces RNAmmer in role | shared | fast rRNA gene prediction |
| tRNAscan-SE | Recommended default | - | shared | tRNA gene prediction |
| Aragorn / Infernal+Rfam | Alternative | - | shared | tmRNA/tRNA and ncRNA annotation |
| RAST / RASTtk | Legacy (still usable) | -> Bakta/PGAP | shared | older web annotation server |
| Glimmer3 / GeneMarkS | Legacy (still usable) | -> Prodigal | shared | older gene callers (GeneMark license restricted) |
| RNAmmer | Legacy (still usable) | -> barrnap | shared | older HMM rRNA predictor |
| KAAS / GhostKOALA | Legacy (still usable) | -> eggNOG-mapper | shared | older KEGG orthology web assignment |

## 10. MLST

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| mlst (tseemann) | Recommended default | - | shared | seven-gene ST from assemblies |
| PubMLST / BIGSdb | Alternative | - | shared | curated scheme database and platform |
| StringMLST / MentaLiST | Alternative | - | shared | k-mer MLST directly from reads |
| CGE MLST finder (web) | Alternative | - | shared | web-based MLST caller |
| SRST2 | Legacy (still usable) | -> mlst/ARIBA in role | short | read-based MLST/AMR typing |

## 11. Serotyping

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| Kleborate (+Kaptive) | Recommended default | - | shared | Klebsiella ST, K/O, AMR and virulence score |
| ECTyper | Recommended default | - | shared | E. coli O:H / phylogroup typing |
| ShigEiFinder | Recommended default | - | shared | Shigella/EIEC discrimination and serotype |
| SeqSero2 | Recommended default | replaces SeqSero | shared | Salmonella O/H antigen prediction |
| SISTR | Recommended default | - | shared | Salmonella in silico serovar prediction |
| SerotypeFinder (CGE) | Alternative | - | shared | E. coli O/H from genes |
| Kaptive (standalone) | Alternative | - | shared | surface polysaccharide locus typing |
| LisSero / emm typer | Alternative | - | shared | Listeria serogroup and Streptococcus emm |
| SeqSero | Legacy (still usable) | -> SeqSero2 | shared | first-generation Salmonella serotyper |

## 12. cg/wgMLST

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| chewBBACA | Recommended default | - | shared | allele calling and cg/wgMLST workflow |
| PubMLST/BIGSdb | Alternative | - | shared | curated cgMLST schemes and comparison |
| MentaLiST | Alternative | - | shared | scalable k-mer cgMLST caller |
| Ridom SeqSphere+ | Alternative | commercial | shared | commercial cgMLST suite used in surveillance |

## 13. AMR and virulence

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| abricate | Recommended default | - | shared | screen against ResFinder/CARD/VFDB/PlasmidFinder |
| NCBI AMRFinderPlus | Recommended default | - | shared | curated AMR plus hidden-hit adjustment |
| CARD / RGI | Recommended default | - | shared | resistance ontology and gene/allele matching |
| ResFinder + PointFinder | Recommended default | - | shared | acquired genes and chromosomal point mutations |
| Mykrobe | Alternative | - | short | rapid k-mer AMR (Mtb, S. aureus etc.) |
| TB-Profiler | Alternative | - | shared | M. tuberculosis lineage and resistance |
| VirulenceFinder / VFDB | Alternative | - | shared | virulence gene databases and callers |
| KMA | Alternative | - | short | k-mer alignment used by newer CGE services |
| DeepARG | Alternative | - | shared | ML-based ARG prediction |
| ARIBA | Legacy (still usable) | -> abricate/ResFinder | short | local-cluster read-based AMR |
| ARG-ANNOT | Legacy (still usable) | -> ResFinder/CARD | shared | older resistance database, no longer updated |
| KmerResistance | Legacy (still usable) | -> ResFinder (KMA) | short | older k-mer AMR caller |

## 14. Plasmids and MGE

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| mob-suite | Recommended default | - | assembly | plasmid reconstruction, typing and mobility |
| PlasmidFinder | Recommended default | - | shared | replicon incompatibility typing |
| PLSDB | Alternative | - | shared | curated plasmid database and search |
| IntegronFinder | Recommended default | - | shared | integron and attC detection |
| ISEScan | Recommended default | - | shared | insertion sequence annotation |
| MGEfinder / mobileOG-db | Alternative | - | shared | MGE insertion and functional annotation |
| ICEberg / oriTfinder | Alternative | - | shared | ICE and origin-of-transfer resources |
| mlplasmids / PlasFlow | Alternative | - | shared | classify chromosome versus plasmid contigs |
| PLACNETw | Alternative | - | shared | graph-based plasmid reconstruction web tool |
| cBar / Recycler | Legacy (still usable) | -> mob-suite | assembly | older plasmid binning from assemblies |

## 15. Prophage, GI, CRISPR

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| geNomad | Recommended default | - | shared | virus/plasmid element classifier |
| PhiSpy | Recommended default | - | shared | prophage region caller |
| VirSorter2 | Recommended default | replaces VirSorter1 | shared | viral/prophage sequence identification |
| CRISPRCasFinder | Recommended default | - | shared | CRISPR array and cas typing |
| IslandViewer4 / IslandPath-DIMOB | Alternative | - | shared | genomic island prediction |
| MinCED | Alternative | - | shared | CRISPR repeat mining (CRT-derived) |
| PHASTER (web) | Alternative | replaces PHAST | shared | interactive prophage annotation web server |
| VirSorter 1 | Legacy (still usable) | -> VirSorter2 | shared | first-generation viral classifier |
| PHAST | Legacy (still usable) | -> PHASTER | shared | older prophage web server |
| CRT / PILER-CR | Legacy (still usable) | -> CRISPRCasFinder/MinCED | shared | early CRISPR repeat finders |

## 16. Pangenome

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| Panaroo | Recommended default | addresses Roary fragmentation | shared | error-correcting graph pangenome for draft assemblies |
| PPanGGOLiN | Alternative | - | shared | core/shell/cloud partition and partitions |
| PEPPAN / ggCaller | Alternative | - | shared | fragmentation-robust and graph gene-calling pangenomes |
| PIRATE / panX | Alternative | - | shared | pangenome clustering and interactive exploration |
| Roary | Alternative | still a fast baseline | shared | rapid classic pangenome pipeline |
| GET_HOMOLOGUES | Alternative | - | shared | multi-algorithm ortholog clustering |
| OrthoFinder / SonicParanoid | Alternative | - | shared | orthogroup inference (broadly used) |
| anvi'o pangenome | Alternative | - | shared | interactive pangenome workbench |
| Panstripe | Alternative | companion to Panaroo | shared | gene gain/loss rate comparison |
| PGAP (pangenome) / BPGA | Legacy (still usable) | -> Panaroo/PPanGGOLiN | shared | older pangenome pipelines |
| OrthoMCL | Legacy (still usable) | -> OrthoFinder/PPanGGOLiN | shared | early MCL ortholog clustering |

## 17. Read mapping

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| BWA-MEM (BWA 0.7.x) | Recommended default | - | short | standard short-read aligner |
| minimap2 | Recommended default | replaces BWA-SW/minimap/BLASR in role | long/short | fast aligner for long and noisy reads |
| samtools | Recommended default | - | shared | sort/index/mpileup and BAM handling |
| BWA-MEM2 | Alternative | - | short | SIMD-accelerated BWA-MEM, same output |
| Bowtie2 | Alternative | - | short | fast gapped short-read aligner |
| pbmm2 / ngmlr | Alternative | - | PacBio/long | PacBio minimap2 wrapper and SV-oriented aligner |
| Novoalign | Alternative | - | short | high-accuracy commercial aligner |
| NextGenMap | Alternative | - | short | flexible short-read aligner |
| Bowtie 1 | Legacy (still usable) | -> Bowtie2 | short | ungapped first-generation aligner |
| SMALT / Stampy | Legacy (still usable) | -> BWA-MEM/minimap2 | short | older sensitive hybrid aligners |
| BLASR / GraphMap | Legacy (still usable) | -> minimap2/pbmm2 | long | early long-read aligners |

## 18. Variants, core SNP, recombination

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| bcftools (mpileup/call) | Recommended default | - | shared | variant calling, filtering and VCF maths |
| Snippy (+snippy-core) | Recommended default | - | short/assembly | rapid core-SNP pipeline |
| snp-sites | Recommended default | - | shared | extract SNP sites from a multi-FASTA alignment |
| Gubbins | Recommended default | - | shared | detect and mask recombinant regions |
| vcf2phylip | Recommended default | - | shared | convert filtered VCF to alignment |
| FreeBayes | Alternative | - | short | haplotype-aware Bayesian caller |
| GATK (HaplotypeCaller) | Alternative | - | short | broadly used variant caller (best practices workflow) |
| ClonalFrameML | Alternative | - | shared | clonal genealogy with recombination |
| Parsnp (Harvest) | Alternative | - | shared | rapid core-genome alignment/SNP |
| kSNP3 / kSNP4 | Alternative | - | shared | reference-free SNP discovery |
| VarScan2 | Legacy (still usable) | -> bcftools/GATK | short | older pileup-based caller |
| Lyve-SET / CFSAN-SNP / NASP / RedDog | Legacy (still usable) | -> Snippy/Parsnp | short | older outbreak core-SNP pipelines |

## 19. Sequence alignment

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| MAFFT | Recommended default | - | shared | fast accurate multiple sequence alignment |
| MUMmer4 (nucmer/dnadiff) | Recommended default | - | shared | whole-genome pairwise alignment and SNPs |
| MUSCLE (v5) | Alternative | - | shared | accurate MSA, modern v5 rewrite |
| Clustal Omega | Alternative | - | shared | progressive profile MSA |
| LAST | Alternative | - | shared | sensitive large-scale aligner |
| progressiveMauve / Mauve | Alternative | maintenance limited | shared | whole-genome alignment and synteny view |
| T-Coffee | Alternative | - | shared | high-accuracy but slower MSA |
| ClustalW | Legacy (still usable) | -> MAFFT/Clustal Omega | shared | classic early progressive aligner |

## 20. Distance, ANI, dereplication

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| FastANI | Recommended default | - | shared | fast whole-genome ANI |
| Mash | Recommended default | - | shared | MinHash genome/reads distance |
| snp-dists | Recommended default | - | shared | pairwise SNP distance matrix |
| dRep | Recommended default | - | shared | genome/MAG dereplication and selection |
| skani | Alternative | - | shared | sensitive fast ANI on draft genomes |
| pyani (ANIm/ANIb) | Alternative | - | shared | ANI with alignment and plots |
| CD-HIT | Alternative | - | shared | cluster proteins/reads/sequences |
| JSpeciesWS / OrthoANI | Legacy (still usable) | -> FastANI/skani | shared | older/web ANI calculators |

## 21. Phylogenetic inference

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| IQ-TREE 3 (iqtree3/2/1) | Recommended default | major versions iqtree -> iqtree2 -> iqtree3 | shared | ML phylogeny with ModelFinder/UFBoot2 |
| RAxML-NG | Alternative | replaces RAxML 8 | shared | next-generation ML phylogenetics |
| FastTree 2 | Alternative | - | shared | very fast approximate ML for large sets |
| PhyML | Alternative | - | shared | ML phylogeny with model selection |
| MEGA (11) | Alternative | - | shared | GUI phylogenetics and alignment |
| MrBayes | Alternative | - | shared | Bayesian phylogenetic inference |
| RAxML 8 | Legacy (still usable) | -> RAxML-NG | shared | prior-generation ML tree builder |

## 22. Molecular dating

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| TreeTime | Recommended default | - | shared | fast clock dating, ancestral states, mugration |
| BactDating | Alternative | - | shared | ML/Bayesian ancestor-dated trees for bacteria |
| BEAST 2 | Alternative | - | shared | full Bayesian phylodynamics (complementary, heavy) |
| LSD / LSD2 | Alternative | - | shared | least-squares tip dating |
| TempEst | Alternative | - | shared | clock-like signal/temporal structure check |
| BEAST 1 | Legacy (still usable) | -> BEAST 2 / TreeTime | shared | first-generation Bayesian dating platform |

## 23. Microbial GWAS and post-GWAS

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| Scoary | Recommended default | - | shared | gene presence/absence pan-GWAS with population correction |
| pyseer | Recommended default | Python reimplementation/extension of SEER | shared | mixed-model k-mer/SNP/gene GWAS |
| PLINK 1.9 | Recommended default | PLINK 2 available | shared | SNP GWAS, IBS/MDS covariates and QC |
| DBGWAS | Alternative | - | short | unitig/graph k-mer bacterial GWAS |
| treeWAS / hogwash | Alternative | - | shared | phylogeny-aware association tests |
| bugwas | Alternative | - | shared | lineage-effect bacterial GWAS |
| PLINK 2 | Alternative | replaces PLINK 1.9 in role | shared | rewritten scalable GWAS engine |
| GEMMA / FaST-LMM | Alternative | - | shared | linear mixed model engines |
| fsm-lite / dsk / panfeed | Alternative | - | shared | informative k-mer counting for pyseer |
| SEER | Legacy (still usable) | -> pyseer | shared | original C++ sequence-element GWAS |

## 24. Visualization

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| ggtree / treeio (R) | Recommended default | - | shared | programmatic tree annotation and layer plots |
| iTOL | Recommended default | - | shared | web tree annotation with datasets |
| GrapeTree | Recommended default | - | shared | MST/network trees from cgMLST or SNPs |
| ComplexHeatmap (R) | Recommended default | - | shared | annotated heatmaps for matrices |
| Microreact | Alternative | - | shared | web geographic/time/tree viewer |
| Phandango | Alternative | - | shared | interactive tree plus pangenome/metadata |
| Nextstrain / Auspice | Alternative | - | shared | phylodynamic interactive visualization |
| Dendroscope | Alternative | - | shared | large-tree desktop viewer |
| FigTree | Legacy (still usable) | -> iTOL/ggtree | shared | older desktop tree viewer, maintenance limited |

## 25. Workflow engines and reporting

| Tool | Status | Lineage | Platform | Role |
| --- | --- | --- | --- | --- |
| MultiQC | Recommended default | - | shared | aggregate QC reports across samples |
| Snakemake | Alternative | - | shared | reproducible workflow language |
| Nextflow | Alternative | - | shared | portable workflow language with containers |
| Conda / Mamba (Bioconda) | Recommended default | - | shared | package and environment management |
| GNU parallel | Alternative | - | shared | simple per-sample parallelization |

## Selection notes

For new projects, start from the recommended defaults to limit maintenance and compatibility cost. To reproduce a published study or a legacy pipeline, keep its original tools and versions instead of swapping them, since silent substitutions can create differences that are hard to trace. For highly fragmented short-read drafts, Panaroo and PPanGGOLiN are more robust to fragmentation while Roary remains a fast baseline; for completeness and contamination, CheckM2 is a practical default and keeping CheckM output aids comparison with historical data. Long reads are usually self-corrected for a limited number of Racon rounds and then consensus-polished with Medaka, with short-read finishing added for hybrid data, and the less accurate polisher should not be placed last. Choices for alignment, variant calling and tree building follow the assembly-versus-mapping design and depend on reference availability and sample size.

The machine-readable master data live in `reference/tool_catalog.tsv`; after adding or correcting a tool, rerun `python reference/render_alternative_tools.py` to regenerate this page and its Chinese counterpart.
