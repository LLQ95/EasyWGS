# Specialized pathogens: species confirmation, toxin and surface-locus typing

The first EasyWGS pathogen groups (Salmonella, Klebsiella pneumoniae,
Escherichia/Shigella and Listeria monocytogenes) each have a maintained
command-line serotyper. Many other common pathogens do not. For
*Vibrio parahaemolyticus*, *Yersinia enterocolitica*, *Campylobacter jejuni*
and *C. coli*, *Burkholderia gladioli* and *Clostridium botulinum* (the tier-4
groups), and for *Staphylococcus aureus*, *Cronobacter sakazakii*, *Shigella
dysenteriae*, *Vibrio cholerae*, *Bacillus anthracis*, *Bacillus cereus*,
*Burkholderia mallei*, *Mycobacterium tuberculosis* and *Brucella melitensis*
(the tier-5 groups), serotype, lineage or toxin type is reported from
surface-polysaccharide loci, toxin genes, virulence and resistance markers, or
from a dedicated lineage caller, rather than from one unified serotyper.
EasyWGS therefore combines three reproducible components for these groups:
FastANI whole-genome
identity confirmation (module 04.5), the seven-gene MLST sequence type from
module 06.1, and a curated abricate screen of surface, toxin and virulence
loci (module 06.4). The curated marker list with provenance is
[`examples/customdb/easywgs_markers.tsv`](https://github.com/LLQ95/EasyWGS/blob/main/examples/customdb/easywgs_markers.tsv).

Tier 4 adds three Illumina isolates from each of the five tier-4 groups and
tier 5 adds three from each of the nine tier-5 groups, taking the panel from
29 to 44 and then to 71 isolates across 19 pathogen groups. All run accessions
and reference genomes were verified against ENA and NCBI; the accession table
is [`examples/panel.tsv`](https://github.com/LLQ95/EasyWGS/blob/main/examples/panel.tsv).

## Species confirmation with FastANI (module 04.5)

A mixed multi-species panel needs an explicit identity check before any
single-species comparison. Module 04.5 screens every assembly against every
panel reference in `ref/` with [FastANI](https://github.com/ParBLiSS/FastANI)
and keeps the highest-ANI match. It runs directly after the assembly QC and
decontamination gate and writes `04_asm_qc/fastani/fastani_best.tsv` with the
expected reference, the best reference, the best ANI and a status label.

```bash
PROJECT=$PWD bash 04_asm_qc/04.5.fastani_identity.sh
```

An ANI of at least 95% to the expected reference is read as the same species.
A value between 90% and 95% indicates a congeneric close relative and usually
a missing species-level reference. A value below 90%, an empty result, or a
best hit that differs from the expected reference calls for review of the
sample label or residual contamination. FastANI does not report pairs below
roughly 80% ANI, so an unrelated contaminant produces an empty per-sample file
rather than a misleading low score. The panel uses this behaviour as a
teaching point: the two *C. jejuni* isolates confirm against NCTC 11168, while
the *C. coli* isolate scores in the close-relative range, which is the correct
signal that a *C. coli* reference is needed for within-species work.

FastANI is installed in the main `easywgs` environment. The module writes an
empty table and continues when FastANI or the references are absent, matching
the graceful-degradation behaviour of CheckM2 and GUNC.

## Building the custom marker database (module 06.4)

Module 06.4 runs [abricate](https://github.com/tseemann/abricate) against a
small database named `easywgs_markers`. Marker sequences are neither shipped
in git nor downloaded automatically, because surface-antigen and toxin
alleles carry type-specific reference sets and database licences. The
repository ships the curated list with authoritative sources instead. To
build the database, fetch each locus or allele sequence from the cited RefSeq
reference, VFDB or PubMLST record, concatenate the sequences into one
multi-FASTA whose headers start with the `marker_id`, and run the builder.

```bash
# header convention: >marker_id|allele free-text note
MARKER_FASTA=/path/to/easywgs_markers.fa bash 00_install/build_custom_db.sh
PROJECT=$PWD bash 06_typing/06.4.surface_toxin_loci.sh
```

The builder places the database under `~/.abricate/db/easywgs_markers` by
default; override this with `EASYWGS_ABRICATE_DIR`, or point module 06.4 at a
pre-built directory with `EASYWGS_MARKER_DIR`. Outputs are
`06_typing/surface_toxin/custom_markers_all.tab` and the
`custom_markers_summary.tab` presence matrix. Generic gene markers establish
presence or absence only. O/K groups, Penner capsule types and BoNT subtypes
require type-specific reference alleles, added as one sequence per type (for
example `CB_bont|A`, `CB_bont|B`).

## Per-pathogen typing notes

### Vibrio parahaemolyticus

The reference is RIMD 2210633 (GCF_000196095; NCBI taxid 670), and `mlst`
uses the *V. parahaemolyticus* scheme. The species-specific thermolabile
hemolysin gene `tlh` (also called `ldh`) is expected in essentially every
isolate and doubles as a species marker. Pathogenic potential is assessed with
`tdh` (thermostable direct hemolysin), `trh` (including the `trh1` and `trh2`
variants), the T3SS2 region (`vtrB`, `vscN2`) and the pandemic O3:K6/ST3
clonal marker `orf8`. The classical O and K surface groups are encoded by the
`wzx/wzy` and `wza/wzb/wzc` loci, but assigning an O/K group needs
type-specific reference alleles rather than a single generic sequence; these
are flagged in the marker table as `surface_O` and `surface_K`.

### Yersinia enterocolitica

The reference is strain 8081 (GCF_000009345; taxid 630). The `mlst` tool uses
the genus-level *Yersinia* scheme, which covers *Y. enterocolitica*.
Chromosomal markers include the attachment-invasion locus `ail`, the
heat-stable enterotoxin variants `ystA` and `ystB`, invasin `inv` and the
ferrioxamine receptor `foxA`. The virulence plasmid pYV is tracked with `yadA`
and the transcriptional activator `virF` (also named `lcrF`). The markers
`caf1` (F1 capsule) and `pla` are discriminators for *Y. pestis* and are
expected to be absent from *Y. enterocolitica*. Biotype assignments (1A, 1B
and biotypes 2 to 5) do not have a single WGS-only command-line caller and are
best supported by combining these markers with MLST and the phenotypic record.

### Campylobacter jejuni and Campylobacter coli

The shared reference is NCTC 11168 (GCF_000009085; *C. jejuni* taxid 197,
*C. coli* taxid 195). Both species use the *Campylobacter* MLST scheme in
`mlst`; the PubMLST jejuni-coli cgMLST scheme can be adapted for chewBBACA with
`PrepExternalSchema` as described in module 06.3. Virulence markers cover the
cytolethal distending toxin (`cdtA`, `cdtB`, `cdtC`), the fibronectin-binding
adhesin `cadF`, flagellin `flaA`, the invasion antigen `ciaB` and the major
outer-membrane protein `porA`. The Penner (HS) capsule serotype has no
single maintained open-source caller; it is encoded at the capsule
biosynthesis locus that contains the O-methyl phosphoramidate genes such as
`hddA`, and a type needs the full type-specific capsule-locus reference.
Fluoroquinolone and macrolide resistance point mutations in `gyrA` and 23S
rRNA are handled by the PointFinder step of module 07, not by the marker
screen.

### Burkholderia gladioli and the bongkrekic-acid pathovar

The type-strain reference is ATCC 10248 (GCF_000959725; taxid 28095).
*B. gladioli* has no classic seven-gene MLST scheme in the `mlst` database, so
identity is established with FastANI and the multipartite genome size rather
than an ST. Two toxin loci are clinically important. The bongkrekic-acid
biosynthesis cluster (`bon`, including `bonJ` and `bonF`; Moebius et al.,
2012) is reported in *B. gladioli* pv. *cocovenenans*, the pathovar associated
with fermented coconut and corn food poisoning, and is usually absent from
ordinary clinical isolates. The toxoflavin cluster (`tox`, represented by
`toxA`) is shared with related *B. glumae*. An empty `bon` result on the
demonstration clinical isolates is therefore the expected outcome, not a
pipeline failure, and a positive `bon` call should be confirmed by inspecting
cluster coverage and contig context.

### Clostridium botulinum

The reference is strain ATCC 3502 (GCF_000063585; taxid 1491), and `mlst`
uses the *C. botulinum* scheme. The botulinum neurotoxin locus `bont` (also
annotated `cnt`) defines toxin types A through G, chimeric toxins and many
subtypes; the marker screen detects presence, while the type is assigned by
adding one curated reference allele per subtype. The flanking non-toxic
non-haemagglutinin `ntnh`, the haemagglutinin component `ha33` and the
toxin-cluster regulator `botR` provide cluster context. An established
alternative for subtype-level toxin calling is the GAMMA module of the
Bactopia project with a curated neurotoxin reference set. Because `bont` can
reside on the chromosome or on a plasmid, module 07 already runs
[MOB-suite](https://github.com/phac-nml/mob-suite) to reconstruct and type
plasmid contigs; the marker result should be read together with that
reconstruction.

### Staphylococcus aureus

The reference is N315 (GCF_000009645; taxid 1280), an MRSA strain, and `mlst`
uses the *S. aureus* scheme. The thermostable nuclease gene `nuc` is the
species-specific marker. Methicillin resistance is read from `mecA` and its
`mecC` homologue, both carried on an SCCmec cassette; module 07 reports the
gene, while the cassette and mec complex need SCCmecFinder or the open
staphopia-sccmec alternative. Toxin markers cover the Panton-Valentine
leukocidin (`lukS-PV` together with `lukF-PV`), toxic shock toxin `tst`, the
exfoliative toxins `eta` and `etb`, and staphylococcal enterotoxin `sea`
(extended with `seb/sec/see/seg` when needed). The `spa` type is defined by the
Xr repeat succession, so a generic `spa` presence hit in module 06.4 does not
assign a type; spaTyper performs the repeat-based call. spaTyper and
SCCmecFinder are documented here rather than installed in the core environment.

### Cronobacter sakazakii

The reference is ATCC BAA-894 (GCF_000017665; taxid 28141). The `mlst` database
provides a genus-level *Cronobacter* scheme that covers *C. sakazakii* and the
other species in the genus. The outer-membrane protein `ompA`, the
genus-specific zinc metalloprotease `zpx` and the Cronobacter plasminogen
activator `cpa` are the standard identity and virulence markers in module
06.4. There is no single maintained open-source serotyper; species-level
assignment within the genus and O-antigen serogroup are best resolved by
combining the genus MLST scheme, FastANI identity and the PubMLST Cronobacter
O-antigen resources.

### Shigella dysenteriae

The reference is Sd197 (GCF_000012005), a serotype 1 strain. Shigella lies
within *Escherichia coli*, so `mlst` uses the *E. coli* scheme and module 06.2
routes these isolates through the E. coli branch, running ECTyper and
ShigEiFinder. Module 06.4 adds the multicopy invasion-plasmid marker `ipaH`,
the Shiga toxin gene `stxA` characteristic of serotype 1, the invasion
regulator `virF` and the actin-spread factor `icsA` (`virG`). ShigEiFinder
discriminates *S. dysenteriae* from the other Shigella species and EIEC. A
positive `stxA` records genotype and does not by itself establish toxin
production.

### Vibrio cholerae

The reference is the O1 El Tor strain N16961 (GCF_000006745; taxid 666), and
`mlst` uses the *V. cholerae* scheme. The outer-membrane protein `ompW` is the
species-specific marker. Cholera toxin genes `ctxA` and `ctxB`, the
toxin-coregulated pilus `tcpA` with its biotype-specific alleles, the master
regulator `toxR`, the El Tor hemolysin `hlyA` and the zonula occludens toxin
`zot` are carried partly on the CTX prophage and its associated regions. The
O1 Ogawa/Inaba determinant `wbeT` (`rfbT`) and the O139 `wbf` region are
flagged as `surface_O`; assigning an O1 subtype or O139 needs type-specific
locus references rather than one generic sequence, and no unified command-line
caller exists. A `ctxA` genotype must be interpreted with the prophage and
biotype context rather than read as proof of a toxigenic isolate.

### Bacillus anthracis and the Bacillus cereus group

The *B. anthracis* reference is Ames Ancestor (GCF_000008445; taxid 1392),
which carries both virulence plasmids, and the *B. cereus* reference is ATCC
14579 (GCF_000007825; taxid 1396). The `mlst` database uses a single *B.
cereus* group scheme for both, with no separate *B. anthracis* scheme. Classic
virulent *B. anthracis* is defined by the combination of the pXO1 toxin genes
`pagA`, `cya` and `lef` with the regulator `atxA`, and the pXO2 capsule genes
`capA`, `capB` and `capC`; requiring both plasmids separates it from most *B.
cereus* sensu lato and from the plasmid-cured Ames strain. The *B. cereus*
markers cover the non-haemolytic enterotoxin `nheA/nheC`, haemolysin BL
`hblA`, cytotoxin `cytK`, the phosphatidylinositol phospholipase `piplc` and
the cereulide peptide synthetase `cesA`, which is carried on the pCER270
plasmid of emetic isolates. BTyper3 provides the panC phylogenetic group and
virulence and secondary-metabolite calls as an optional external tool. The
pXO1/pXO2 genotype is an in silico teaching result, not a select-agent
determination.

### Burkholderia mallei

The reference is ATCC 23344 (GCF_000011705; taxid 13373). *B. mallei* is a
clonal, host-adapted relative of *B. pseudomallei*, and the `mlst` database
maps it to the *B. pseudomallei* scheme because no separate *B. mallei* scheme
exists. Module 06.4 reports the actin-based motility factor `bimA` and the bsa
type III secretion component `bsaU`. There is no single *B. mallei*-specific
WGS marker; identity is established by FastANI against the reference together
with the characteristic two-chromosome genome size and the *B. pseudomallei*
ST. Separating *B. mallei* from *B. pseudomallei* and assigning isolates below
the species level generally needs a curated SNP phylogeny rather than a
presence screen.

### Mycobacterium tuberculosis

The reference is H37Rv (GCF_000195955.2; taxid 1773). The `mlst` database has
no classic seven-gene scheme for the *M. tuberculosis* complex, so module 06.1
records no ST and identity is confirmed by FastANI against H37Rv. The
recommended route is the reference-mapping pipeline (module 12) against H37Rv
followed by TB-Profiler or Mykrobe for lineage and drug-resistance calls;
fast-lineage-caller and MTBseq are further command-line alternatives. The
RD1 antigens `esxA` (ESAT-6) and `esxB` (CFP-10) in module 06.4 are auxiliary
identity markers only. Resistance in this species is driven by SNPs and
specific alleles, so a presence/absence gene screen is not sufficient and the
SNP-aware callers should be used.

### Brucella melitensis

The reference is biovar 1 strain 16M (GCF_000250795), which has two
chromosomes. The `mlst` database has no classic seven-gene scheme for
*Brucella*, so identity is established with FastANI and the characteristic
two-chromosome genome size rather than an ST. Module 06.4 reports the
genus-specific 31-kDa protein `bcsp31`, the multicopy insertion sequence
IS711 (IS6501) used in species and biovar PCR assays, the outer-membrane
protein `omp2b`, the VirB type IV secretion component `virB5` and the smooth
LPS O-antigen gene `wbkA`. Resolving *B. melitensis* biovars or separating the
*Brucella* species is best done with published cgMLST or MLVA schemes and
IS711 assays against curated references, not with a single generic marker.

## Running comparative modules on the panel

Modules 08 (pangenome), 09 (core-SNP), 10 (TreeTime), 12 (reference mapping)
and 13 (GWAS) assume one species with one shared reference. On the mixed
71-isolate panel they must be run on a single-species subset rather than on all
isolates at once. The helper
[`examples/scripts/subset_samplesheet.py`](https://github.com/LLQ95/EasyWGS/blob/main/examples/scripts/subset_samplesheet.py)
filters the generated samplesheet, dates and traits for one tier by
`species_code` (default) or panel `group`, and prints the copy-and-run
commands.

```bash
python examples/scripts/make_samplesheets.py 4
python examples/scripts/subset_samplesheet.py 4 campylobacter
cp examples/generated/subset_species_campylobacter/samplesheet.csv  config/my_samples.csv
cp examples/generated/subset_species_campylobacter/metadata_dates.csv config/metadata_dates.csv
cp examples/generated/subset_species_campylobacter/traits.csv         config/traits.csv
bash run_all.sh config/my_samples.csv 08
```

Filtering by `species_code` keeps *E. coli* and Shigella together, which is
appropriate because Shigella lies within the *E. coli* species; use `--by
group` when a single panel group is required instead. The per-isolate modules
(QC, assembly, decontamination, annotation, MLST, FastANI and the marker
screen) run on the full mixed panel without subsetting.

## Scope and limitations

The custom screen is a presence or absence layer built from transparent,
user-provided reference sequences; it does not replace curated services such
as PubMLST for definitive type assignment or genomic surveillance submission.
Type-specific calls (O/K, Penner, BoNT subtype) require the corresponding
reference alleles and manual inspection of coverage and locus context.
Toxin-gene presence indicates genotypic potential and must be interpreted
with the phenotype, the plasmid or chromosome location and the relevant
biosecurity rules. The demonstration isolates are public surveillance or
clinical strains; they are not guaranteed toxin producers, and the workflow
reports the genotype rather than asserting toxigenicity.

Several tier-5 groups are high-consequence or select-agent pathogens, including
*B. anthracis*, *B. mallei*, *Brucella*, *M. tuberculosis*, toxigenic *V.
cholerae* and *S. dysenteriae* serotype 1. EasyWGS analyses public sequencing
data in silico for teaching and surveillance bioinformatics only; it includes
no wet-lab, culture or handling procedure, and a genotype is neither a risk
classification nor an authorization determination. Any physical work with
these organisms must follow national biosecurity and select-agent regulations.
