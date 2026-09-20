# Custom marker database for module 06.4

Module `06_typing/06.4.surface_toxin_loci.sh` screens assemblies with
[abricate](https://github.com/tseemann/abricate) against a small curated
database named `easywgs_markers`. It covers surface-antigen loci, toxin genes
and virulence markers for pathogen groups that do not have a single maintained
command-line serotyper: *Vibrio parahaemolyticus*, *Yersinia enterocolitica*,
*Campylobacter jejuni/coli*, *Burkholderia gladioli* and *Clostridium
botulinum*.

The marker sequences are not shipped in git and are not downloaded
automatically. Surface-antigen and toxin alleles carry type-specific reference
sets and database licences, so the repository ships the curated marker list
with provenance instead of redistributing sequences.

## Files

- `easywgs_markers.tsv`: marker list with the gene symbol, locus class,
  interpretation and the authoritative sequence source for every marker.

## Build the database

1. Open `easywgs_markers.tsv` and fetch each locus or allele sequence from the
   cited RefSeq reference genome, VFDB or PubMLST record.
2. Concatenate the sequences into one multi-FASTA. Each header must start with
   the `marker_id`, optionally followed by `|allele` and free text:

   ```text
   >VP_tdh|reference thermostable direct hemolysin, RIMD 2210633
   ATGAAACACC...
   >CB_bont|A botulinum neurotoxin type A reference
   ATGCCATTTG...
   ```

3. Build the abricate database (the default location is per-user):

   ```bash
   MARKER_FASTA=/path/to/easywgs_markers.fa bash 00_install/build_custom_db.sh
   ```

4. Run the typing module, or the whole workflow; module 06.4 now reports
   `custom_markers_all.tab` and `custom_markers_summary.tab` under
   `06_typing/surface_toxin/`.

Override the database directory with `EASYWGS_ABRICATE_DIR` at build time or
point module 06.4 at a pre-built directory with `EASYWGS_MARKER_DIR`. If the
database is absent, module 06.4 writes empty tables, prints a warning and
continues, matching the graceful-degradation behaviour of CheckM2 and GUNC.

## Typing limitation

Generic gene markers establish presence or absence only. O/K groups of
*V. parahaemolyticus*, the Penner (HS) capsule type of *Campylobacter* and the
BoNT toxin type/subtype of *C. botulinum* require type-specific reference
alleles. Add one sequence per type (for example `CB_bont|A`, `CB_bont|B`) and
interpret the hit allele, or use the dedicated resources named in the
guidebook page "Specialized pathogens". The bongkrekic-acid `bon` cluster is
expected only in *B. gladioli* pv. *cocovenenans*; ordinary clinical
*B. gladioli* isolates are usually negative, so an empty `bon` result on the
demonstration isolates is the expected outcome rather than a pipeline failure.
