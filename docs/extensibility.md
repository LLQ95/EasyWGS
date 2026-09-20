# Beyond bacteria: viruses, fungi and probiotics

The numbered EasyWGS modules were written around a bacterial isolate, yet many
of the same steps recur when the target is a virus, a pathogenic fungus or a
probiotic strain. This page assesses how far the current design transfers,
which tools are shared and which are specific to a domain, and how the project
can be extended without forcing one linear script onto organisms with very
different genome biology. The short answer is that the architecture transfers
well because roughly half of the workflow is domain-agnostic, but the
assembly strategy, the completeness model, the annotation engine and the
typing paradigm differ enough that a single `run_all.sh` for every organism
would be misleading. The maintainable design is a shared core plus a thin
domain profile for bacteria, viruses and fungi, with probiotics treated as a
safety-and-benefit configuration layered over the appropriate track.

![Shared and domain-specific tools across bacterial, viral and fungal WGS](assets/EasyWGS_domains.png)

*Figure. A three-set comparison of analytical capabilities for bacterial
isolate WGS, virus WGS (HIV, SARS-CoV-2, norovirus) and pathogenic fungal WGS
(*Aspergillus*, *Candida*), together with a stage-by-domain matrix. Green
marks the domain-agnostic shared core, the domain hues mark paradigm-specific
programs, and grey marks a stage that does not transfer in its bacterial form.
Probiotics are a use-profile rather than a fourth biological set.*

The editable vector, a print-ready PDF and a high-resolution PNG are generated
deterministically by `python figures/make_domains_figure.py`, and the
underlying programs are catalogued in stages 26 to 31 of the
[tool encyclopedia](alternative-tools.md).

## Why one linear pipeline does not fit all domains

The three domains differ in genome architecture and in the question the
analysis is expected to answer. A bacterial isolate is usually a haploid
genome of a few megabases with a main chromosome and plasmids, and the
analysis is dominated by gene content: a seven-gene sequence type, an O/H/K
serotype, the presence or absence of acquired resistance and virulence genes,
and a core-genome phylogeny. De novo assembly and gene annotation sit at the
centre of this track. RNA viruses such as HIV (about 9.7 kb), SARS-CoV-2
(about 30 kb) and norovirus (about 7.6 kb) have tiny, highly variable genomes
that exist in a host as a cloud of related variants. Here the natural route is
reference-guided mapping to a high-quality consensus, coverage gating,
low-frequency and haplotype analysis, and assignment to a clade or subtype. A
gene-based pangenome of the bacterial kind is not meaningful, and de novo
assembly is reserved for large DNA viruses and metaviromic samples.

Pathogenic fungi such as *Aspergillus flavus* and *Aspergillus fumigatus*
have genomes of tens of megabases with introns, repetitive regions and, in
some species such as *Candida auris*, diploidy, heterozygosity and
aneuploidy. Long-read or hybrid assembly is preferred, completeness is judged
with eukaryotic single-copy orthologues rather than bacterial lineage markers,
and annotation needs an ab initio eukaryotic gene predictor trained on
protein and transcript evidence. Species confirmation cannot rely on the
prokaryotic 95% ANI rule, typing uses barcodes and SNP clades rather than
seven-gene MLST, and resistance is often driven by point mutations, gene copy
number or chromosome copy number rather than by an acquired gene. These
differences change the tools at four hand-off points (completeness,
annotation, typing and resistance), while the steps that feed them remain
shared.

## The domain-agnostic shared core

The following stages transfer almost unchanged and form the shared core that
a domain profile reuses. They are the same programs the bacterial pipeline
already installs and documents.

| Stage | Shared programs |
| --- | --- |
| Data retrieval | SRA Toolkit, NCBI datasets/ENA filer, EDirect |
| Read QC and trimming | fastp, FastQC, MultiQC, seqkit; NanoPlot, chopper, Filtlong for long reads |
| Host and contaminant read removal | minimap2, BWA, Bowtie2, BBMap, KneadData, samtools (the engine is shared; the reference differs) |
| Reference mapping and BAM handling | BWA-MEM/BWA-MEM2, minimap2, Bowtie2, samtools |
| Variant calling | bcftools, freebayes, GATK |
| Coverage and assembly statistics | mosdepth, QUAST, seqkit, assembly-stats |
| Sequence alignment | MAFFT, MUSCLE, MUMmer, BLAST/DIAMOND |
| Genome distance and dereplication | Mash, skani (coarse screening across domains) |
| Phylogenetic inference | IQ-TREE 3, RAxML-NG, FastTree |
| Dated trees (when a clock signal exists) | TreeTime, BEAST 2, TempEst |
| Tree visualisation | iTOL, ggtree, Microreact, FigTree, Nextstrain Auspice |
| Functional annotation | DIAMOND, eggNOG-mapper, InterProScan, BLAST |
| Workflow and reporting | Conda/Mamba, Snakemake, Nextflow, MultiQC |

Molecular dating is shared in principle but not in practice for every
organism. RNA viruses and many outbreak bacteria carry enough temporal signal
for TreeTime or BEAST to be informative, whereas the signal is frequently weak
or absent in fungi and should be checked with TempEst before dating is
attempted.

## Viruses: a mapping- and consensus-first track

Clinical viral sequencing is dominated by host RNA and DNA, so the first
domain-specific step is aggressive host-read removal followed by mapping to a
small reference rather than assembly. For amplicon schemes, primer sequences
are trimmed and over-depth regions are normalised before a consensus is
called, and a coverage threshold (commonly a minimum depth and a maximum
proportion of ambiguous bases) decides whether a genome is accepted. The
consensus, the low-frequency variant table and the clade assignment are the
primary outputs; there is no bacterial-style gene pangenome. The mature
[nf-core/viralrecon](https://github.com/nf-core/viralrecon) workflow is a
useful reference implementation for both Illumina and ONT and is treated as
the template for a viral domain profile rather than as something to recreate.

For SARS-CoV-2, reads are mapped to the Wuhan-Hu-1 reference (MN908947), the
consensus is produced with iVar, the ARTIC field-bioinformatics workflow for
ONT or ViralConsensus, and lineages and clades are assigned with Nextclade
and Pangolin, with optional placement on the global tree by UShER and
interactive presentation through augur and Auspice. Freyja is added for
wastewater or other mixed samples where several lineages coexist. For HIV,
host depletion is followed by HAPHPIPE or V-pipe, with shiver as an alternative
that builds a sample-specific reference before mapping; intrahost haplotypes
are reconstructed with CliqueSNV, transmission clusters are defined from
TN93 distances with HIV-TRACE, selection and recombination are tested with
HyPhy, and drug-resistance mutations are interpreted against the Stanford
HIVdb Sierra service or Quasitools HyDRA. Subtyping is most often handled by
phylogeny or a curated web service (COMET, SCUEAL, REGA). For norovirus, VADR
provides annotation and submission QC, and typing combines an ORF1/RdRp
phylogeny (the P-type) with an ORF2/VP1 phylogeny (the genogroup and
genotype, GI to GX); the RIVM NoroNet typing service is commonly used because
no single local command-line tool unifies the dual nomenclature. Large DNA
viruses and metaviromic samples instead use the viral modes of SPAdes
(`--metaviral`), CheckV for completeness and proviral/host contamination, and
VIGOR or VAPiD for annotation.

| Tool | Role in the viral track | Source |
| --- | --- | --- |
| nf-core/viralrecon | Reference Illumina/ONT viral workflow and domain template | [nf-core/viralrecon](https://github.com/nf-core/viralrecon) |
| iVar | Amplicon primer trimming, variants and consensus | [andersen-lab/ivar](https://github.com/andersen-lab/ivar) |
| ARTIC fieldbioinformatics | ONT tiling-amplicon consensus workflow | [artic-network/fieldbioinformatics](https://github.com/artic-network/fieldbioinformatics) |
| ViralConsensus | Fast consensus generation directly from a BAM | [niemasd/ViralConsensus](https://github.com/niemasd/ViralConsensus) |
| ViralMSA | Reference-guided viral multiple alignment | [niemasd/ViralMSA](https://github.com/niemasd/ViralMSA) |
| Nextclade / Nextalign | Clade assignment, mutation calling and QC | [nextstrain/nextclade](https://github.com/nextstrain/nextclade) |
| Pangolin | SARS-CoV-2 lineage assignment | [cov-lineages/pangolin](https://github.com/cov-lineages/pangolin) |
| UShER / matUtils | Placement on a mutation-annotated tree | [yatisht/usher](https://github.com/yatisht/usher) |
| augur / Auspice | Phylodynamic build and interactive view | [nextstrain/augur](https://github.com/nextstrain/augur) |
| Freyja | Lineage deconvolution of wastewater and mixed samples | [andersen-lab/Freyja](https://github.com/andersen-lab/Freyja) |
| CheckV | Viral completeness and host/proviral contamination | [chklovski/CheckV](https://github.com/chklovski/CheckV) |
| VADR | GenBank-grade viral annotation and submission QC | [ncbi/vadr](https://github.com/ncbi/vadr) |
| VAPiD | Lightweight viral genome annotation | [rcs333/VAPiD](https://github.com/rcs333/VAPiD) |
| VIGOR | Viral gene and protein annotation (JCVI) | JCVI distribution (web/download) |
| SnpEff / SnpSift | Variant-effect annotation on small or custom genomes | [pcingola/SnpEff](https://github.com/pcingola/SnpEff) |
| mosdepth | Genome and amplicon coverage summaries | [brentp/mosdepth](https://github.com/brentp/mosdepth) |
| HAPHPIPE | HIV haplotype reconstruction and phylodynamics | [gwcbi/haphpipe](https://github.com/gwcbi/haphpipe) |
| V-pipe | Intrahost diversity and quasispecies workflow | [cbg-ethz/V-pipe](https://github.com/cbg-ethz/V-pipe) |
| shiver | HIV/HCV/RSV host removal, assembly and consensus | [ChrisHIV/shiver](https://github.com/ChrisHIV/shiver) |
| HIV-TRACE / tn93 | TN93 distances and transmission clusters | [veg/hivtrace](https://github.com/veg/hivtrace) |
| HyPhy | Selection (SLAC/FEL/MEME/FUBAR) and recombination (GARD) | [veg/hyphy](https://github.com/veg/hyphy) |
| CliqueSNV | Intrahost haplotype reconstruction from linked variants | [vtsyvina/CliqueSNV](https://github.com/vtsyvina/CliqueSNV) |
| Stanford HIVdb / HyDRA | Web HIV drug-resistance mutation scoring | [hivdb.stanford.edu](https://hivdb.stanford.edu/) and [hydra.canada.ca](https://hydra.canada.ca/) |
| Phyloscanner | Within- and between-host contamination and transmission | ChrisHIV distribution |
| vClean | Viral contamination and quality under MIUViG standards | Described in the 2025 publication |

## Pathogenic fungi: long/hybrid assembly and eukaryotic annotation

Fungal WGS inverts several bacterial defaults. Short reads alone rarely resolve
repetitive, sometimes heterozygous genomes, so Flye or Canu for long reads and
HybridSPAdes, MaSuRCA or AAFTF for hybrid data, followed by NextPolish or
Medaka and Pilon, are the preferred starting point. Completeness is assessed
with BUSCO against a fungal lineage set such as `fungi_odb10` or
`ascomycota_odb10`, with FGMP as a complementary estimate; CheckM2 and GUNC
are bacterial lineage tools and are not appropriate here. Annotation then uses
a eukaryotic pipeline, funannotate or BRAKER3 (which combines GeneMark-ETP,
AUGUSTUS and miniprot), with MAKER as an established alternative, because
Prodigal and Bakta model prokaryotic genes without introns. Species and strain
identity uses the ITS barcode extracted with ITSx and compared against UNITE,
augmented by protein-coding loci such as TEF1, calmodulin and beta-tubulin and
by SNP phylogeny or skani/Mash distance; the 95% FastANI threshold that gates
bacterial species is not defined for fungi.

Comparative genomics and typing also change shape. OrthoFinder and
GET_HOMOLOGUES replace the prokaryotic graph pangenome tools for orthologous
gene families; long-read heterozygous samples can be phased with nPhase, and
copy-number variation and aneuploidy, which are clinically important in
*Candida*, are profiled with Control-FREEC from mapped reads. Resistance is
read from mutations and copy number rather than from an acquired gene:
*A. fumigatus* azole resistance is associated with cyp51A promoter and coding
changes such as TR34/L98H and TR46/Y121F/T289A, and *C. auris* combines SNP
clades with ERG11, FKS1 and TAC1B variants and frequent aneuploidy. There is
no unified command-line equivalent of abricate for these rules, so the route
is mapping with GATK or freebayes followed by curated, versioned rule tables,
and a genotypic call always needs confirmation by phenotypic MIC testing.
Secondary metabolism is a first-class question for filamentous fungi: the
fungal mode of antiSMASH detects biosynthetic gene clusters including the
aflatoxin cluster of *A. flavus*, SMURF provides a web-based alternative, and
run_dbcan annotates carbohydrate-active enzymes. Two worked configurations
illustrate the spread. A filamentous ascomycete such as *A. flavus* or
*A. fumigatus* follows long/hybrid assembly, BUSCO, funannotate or BRAKER3,
antiSMASH and cyp51A rules. A clonal yeast pathogen such as *C. auris* follows
reference mapping, joint variant calling, SNP-clade assignment, ERG11/FKS1
interrogation and Control-FREEC aneuploidy profiling.

| Tool | Role in the fungal track | Source |
| --- | --- | --- |
| AAFTF | Haploid fungal assembly, vector filtering and polishing | [stajichlab/AAFTF](https://github.com/stajichlab/AAFTF) |
| Flye / Canu / NextPolish | Long-read and hybrid assembly and polishing | see the main pipeline modules |
| BUSCO | Eukaryotic single-copy orthologue completeness | [gitlab.com/ezlab/busco](https://gitlab.com/ezlab/busco) |
| FGMP | Fungal completeness from coding and non-coding markers | Project distribution |
| funannotate | Fungal annotation, comparison and submission preparation | [nextgenusfs/funannotate](https://github.com/nextgenusfs/funannotate) |
| BRAKER3 | Eukaryotic gene prediction (GeneMark-ETP/AUGUSTUS/miniprot) | [Gaius-Augustus/BRAKER](https://github.com/Gaius-Augustus/BRAKER) |
| MAKER / MAKER2 | Evidence-driven eukaryotic annotation | Yandell lab distribution |
| FunGAP | Fungal gene annotation with evidence scoring | Project distribution |
| ITSx | Extraction of ITS1/5.8S/ITS2 barcode regions | [microbiology.se/software/itsx](https://microbiology.se/software/itsx) |
| UNITE | Curated ITS reference database | [unite.ut.ee](https://unite.ut.ee/) |
| OrthoFinder | Orthogroup inference for fungal pangenomes | [davidemms/OrthoFinder](https://github.com/davidemms/OrthoFinder) |
| GET_HOMOLOGUES | Multi-algorithm ortholog clustering | [eead-csic-compbio/get_homologues](https://github.com/eead-csic-compbio/get_homologues) |
| nPhase | Ploidy-agnostic long-read haplotype phasing | Project distribution |
| Control-FREEC | Copy-number and aneuploidy detection | [BoevaLab/FREEC](https://github.com/BoevaLab/FREEC) |
| antiSMASH (fungal mode) | Secondary-metabolite biosynthetic gene clusters | [antismash/antismash](https://github.com/antismash/antismash) |
| run_dbcan | CAZyme and CAZyme gene cluster annotation | [linnabrown/run_dbcan](https://github.com/linnabrown/run_dbcan) |
| SMURF | Web prediction of fungal secondary-metabolite clusters | Web service |

## Probiotics: a safety and benefit profile over the bacterial track

Probiotics are not a fourth biological domain. Bacterial probiotics, including
the reclassified lactobacilli (for example *Lacticaseibacillus* and
*Ligilactobacillus*), bifidobacteria, *Streptococcus thermophilus*,
*Bacillus subtilis* and *Bacillus coagulans*, and *Escherichia coli* Nissle,
run on the bacterial track with an added regulatory safety and benefit
lens. The yeast *Saccharomyces boulardii* instead follows the fungal track.
The relevant regulatory frame in Europe is the EFSA FEEDAP guidance on the
characterisation of microorganisms used as feed additives or as production
organisms, together with the Qualified Presumption of Safety (QPS) list and
its updates; equivalent national or regional frameworks apply elsewhere.

Safety assessment asks a focused set of questions that repurpose existing
modules. Taxonomic identity must be resolved to the strain with FastANI and
MLST. Acquired antimicrobial-resistance genes should be absent, and any
resistance determinant should be checked for mobility by examining its
flanking context with MOB-suite, IntegronFinder and ISEScan, because an
intrinsic, non-transferable determinant is interpreted differently from an
acquired one; AMRFinderPlus, RGI and abricate supply the determinant calls.
Known virulence factors should be absent, and *Bacillus* candidates are
screened for toxin production, reusing the *B. cereus* group cereulide and
enterotoxin markers already covered by BTyper3 in the specialized-pathogens
module. A genomic screen does not authorise a strain on its own: a safety
conclusion still requires phenotypic MIC values against EFSA or EUCAST
breakpoints and toxicological evidence. On the benefit side, the same
annotation layer supports carbohydrate-use analysis with run_dbcan,
bacteriocin and ribosomal-peptide mining with antiSMASH and the BAGEL4 web
server, CRISPR characterisation with CRISPRCasFinder, and metabolic pathway
inspection with eggNOG-mapper. The Probio and ProbioMinServer platforms
collect many of these in silico safety and functional checks in one place.

| Resource | Role in the probiotic profile | Source |
| --- | --- | --- |
| EFSA FEEDAP guidance (2018, updated 2025) | Characterisation, acquired resistance and risk-assessment frame | [efsa.europa.eu](https://www.efsa.europa.eu/) |
| EFSA QPS list and updates | Taxonomy, safety and toxigenicity status by group | [efsa.europa.eu](https://www.efsa.europa.eu/) |
| EUCAST breakpoints | Phenotypic susceptibility reference for MIC interpretation | [eucast.org](https://www.eucast.org/) |
| Probio / ProbioMinServer | In silico probiotic safety and functional platform | Described in Bioinformatics Advances (2023) |
| BAGEL4 | Web bacteriocin and RiPP mining | MolGen web service |
| run_dbcan, antiSMASH, CRISPRCasFinder, MOB-suite | Benefit and transferability evidence | see stages 14, 15 and 30 |

## Stage-by-stage transferability

The matrix in the figure summarises the practical mapping. Read QC, host
removal, mapping, variant calling, coverage, alignment, maximum-likelihood
phylogeny and reporting transfer directly. Assembly, completeness and
annotation transfer as concepts but not as programs: SPAdes and CheckM2 give
way to viral consensus tools and CheckV for viruses, and to long/hybrid
assemblers, BUSCO and funannotate or BRAKER3 for fungi. Typing and resistance
are the least portable stages. Seven-gene MLST, O/H/K serology, gene-presence
resistance and a prokaryotic pangenome are bacterial constructs; viruses use
clades, subtypes, intrahost haplotypes and curated resistance-mutation rules;
fungi use barcodes, SNP clades, ortholog pangenomes and copy-number-aware
resistance calls. Microbial GWAS transfers best to bacteria, is possible for
very large viral datasets with strong control of linkage, and is generally
underpowered in clonal, small-sample fungal collections.

## Feasibility assessment and extension roadmap

The assessment is positive. The project is already data-driven, with numbered
modules, isolated Conda environments, external references and marker paths,
expected-result gates and two parallel strategies, so a domain profile can
reuse the shared core and override only the hand-off stages rather than fork
the code base. This also matches the wider ecosystem. nf-core already
provides a mature viral workflow (viralrecon) and bacterial assembly
workflows, which validates the viral tool choices here, while a comparably
standardised whole-genome workflow for pathogenic fungi, and a single
bilingual guide that covers bacteria, viruses, fungi and probiotic safety in
one frame, is less well covered. That gap is the clearest point of
differentiation for a methods paper.

The recommended order of work keeps each phase independently testable.
Phase 0 abstracts the shared core, adds a `domain` field to the sample sheet
and configuration, splits the Conda environments into core, viral and fungal
sets, and externalises all reference genomes and rule tables with explicit
version pins. Phase 1 implements the viral profile on public data, starting
with SARS-CoV-2 because the reference and expected outputs are standardised,
then HIV with HAPHPIPE or V-pipe, HIV-TRACE and HyPhy/HyDRA, then norovirus
with VADR and dual ORF1/ORF2 typing. Phase 2 implements the fungal profile on
*A. flavus* or *A. fumigatus* long/hybrid data and on a *C. auris*
mapping-based panel, each with its own completeness and resistance gates.
Phase 3 adds the probiotic profile as a bacterial configuration plus the
EFSA/QPS safety and benefit checklist, routing *S. boulardii* through the
fungal profile. Phase 4 unifies the catalogue, adds one worked-example panel
and an expected-results file per domain, and distributes container images so
that every profile is reproducible in continuous integration. The profiles
should first live in this repository under a `domains/` directory; once the
viral and fungal tracks are mature and independently useful they can be split
into sister pipelines, following the way the EasyAmplicon and EasyMetagenome
guides are maintained as separate, domain-focused resources.

## Scope, biosafety and interpretation limits

As with the bacterial panels, the cross-domain material is designed for
teaching and for analysis of public, already-sequenced data in silico. It does
not describe isolation, culture or wet-laboratory handling of HIV, SARS-CoV-2,
norovirus or high-consequence fungi, and users must follow their institutional
biosafety and data-governance rules. Genotype is not phenotype. HIV
drug-resistance rule sets are updated frequently and must be queried against
the current release; fungal and probiotic resistance calls require phenotypic
MIC confirmation; and eukaryotic annotation depends on licensed or trained
gene predictors and on substantially more compute than bacterial assembly.
The guidebook documents the programs and their decision points, but it does
not replace clinical, regulatory or food-safety judgement.
