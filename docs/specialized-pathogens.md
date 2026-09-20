# Specialized pathogens: species confirmation, toxin and surface-locus typing

The first EasyWGS pathogen groups (Salmonella, Klebsiella pneumoniae,
Escherichia/Shigella and Listeria monocytogenes) each have a maintained
command-line serotyper. Several other common pathogens do not. For
*Vibrio parahaemolyticus*, *Yersinia enterocolitica*, *Campylobacter jejuni*
and *C. coli*, *Burkholderia gladioli* and *Clostridium botulinum*, serotype or
toxin type is still reported from surface-polysaccharide loci, toxin genes and
virulence markers rather than from a single unified caller. EasyWGS therefore
combines three reproducible components for these groups: FastANI whole-genome
identity confirmation (module 04.5), the seven-gene MLST sequence type from
module 06.1, and a curated abricate screen of surface, toxin and virulence
loci (module 06.4). The curated marker list with provenance is
[`examples/customdb/easywgs_markers.tsv`](https://github.com/LLQ95/EasyWGS/blob/main/examples/customdb/easywgs_markers.tsv).

Tier 4 of the demonstration panel adds three Illumina isolates from each of
these five groups, taking the panel from 29 to 44 isolates across ten pathogen
groups. All run accessions and reference genomes were verified against ENA and
NCBI; the accession table is [`examples/panel.tsv`](https://github.com/LLQ95/EasyWGS/blob/main/examples/panel.tsv).

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

## Running comparative modules on the panel

Modules 08 (pangenome), 09 (core-SNP), 10 (TreeTime), 12 (reference mapping)
and 13 (GWAS) assume one species with one shared reference. On the mixed
44-isolate panel they must be run on a single-species subset rather than on all
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
