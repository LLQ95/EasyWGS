# Annotation, AMR, virulence and mobile elements

This stage corresponds to modules 05 and 07. Module 05 provides structural and functional
annotation, and module 07 scans for antimicrobial resistance, virulence and mobile genetic
elements; together they support epidemiological and transmission-mechanism interpretation.

## Structural and functional annotation (05)

Prokka is convenient for rapid batches, Bakta uses newer databases and annotates resistance
and plasmid segments in more detail, and eggNOG-mapper supplies GO, KEGG and COG:

```bash
prokka --outdir prokka/$id --prefix $id --cpus 16 --kingdom Bacteria genomes/$id.fasta
bakta --db $BAKTA_DB --threads 16 --output bakta/$id genomes/$id.fasta
emapper.py -i prokka/$id.faa -o $id --cpu 16 -m diamond
```

Prodigal outputs protein-coding genes on its own for custom-database searches and pangenome
work.

## Resistance, virulence and point mutations (07)

abricate scans several databases in one pass, AMRFinderPlus and RGI (CARD) cross-check, and
PointFinder addresses chromosome point-mutation resistance:

```bash
for db in resfinder vfdb card ncbi ecoli_vf megares; do abricate --threads 16 --db $db genomes/$id.fasta; done
amrfinder -n genomes/$id.fasta -d $AMR_DB --threads 16
rgi main -i genomes/$id.fasta -o rgi/$id -t contig -a DIAMOND --local
```

Custom databases can add bacmet2 (biocide/metal tolerance), ICE, oriT, relaxase, SGI-1,
fljAB and ecoh markers; abricate points to the custom folder with `--datadir`. PointFinder
is sensitive to file names, so sample and output names should avoid extra symbols beyond
underscores, and the script uses safe names.

## Plasmids

mob-suite calls replicons, relaxases, mobility and typing; PlasmidFinder identifies
replicons; PLSDB searches known plasmids for provenance; PlasFlow separates chromosomal from
plasmid segments by sequence features:

```bash
mob_typer --infile genomes/$id.fasta --outdir mobsuite/$id
abricate --db plasmidfinder genomes/$id.fasta
mash dist plsdb.msh genomes/$id.fasta
```

For plasmid-level transmission, extract plasmid sequences, align and build a plasmid tree,
then compare it with the chromosome tree to distinguish vertical inheritance from
horizontal transfer.

## Integrons, insertion sequences and ICE

IntegronFinder identifies integrons and gene cassettes; ISfinder/ISEScan identify insertion
sequences; mobileOG annotates mobile-element functions; MGEfinder and the oriT/relaxase
libraries locate conjugative elements and ICE boundaries; genomad identifies plasmid and
phage segments together:

```bash
integron_finder --local --cpu 16 genomes/$id.fasta
# ISfinder is online/licensed; ISEScan runs locally; mobileOG uses diamond against its proteins
genomad run -t 16 genomes/$id.fasta genomad/$id $GENOMAD_DB
```

## Phages and CRISPR

For temperate phages, IslandPath shows genomic islands, VirSorter2 identifies prophages and
PhiSpy locates boundaries, with PHASTER as an online cross-check. CRISPRCasFinder identifies
CRISPR arrays and cas systems. Plot these elements, resistance and virulence genes together
on a circular map to see whether they sit on the same mobile background.

## Integrating results

All module 07 hits are collected in a long table of sample, element type, database, gene,
position, coverage and identity, and merged into the master table by module 99. Databases
differ in naming conventions, so keep the original gene identifier and source database to
preserve traceability rather than storing only one unified name.
