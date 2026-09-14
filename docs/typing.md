# MLST, serotyping and cgMLST

Module 06 has three steps: seven-gene MLST, species-specific serotyping or surface antigens,
and core-genome multilocus sequence typing (cgMLST). The scripts are `06.1.mlst.sh`,
`06.2.serotype.sh` and `06.3.cgmlst.sh`.

## Seven-gene MLST

The mlst tool bundles PubMLST databases and calls sequence types on a batch of assemblies:

```bash
mlst --label $id genomes/${id}.fasta >> mlst_all.tsv
```

The output reports both species and ST. A conflicting species call or mixed allele peaks in
one sample points back to the decontamination gate.

## Species-specific serotyping schedule

The script selects tools by the species column so that the wrong database is never applied.

For the Klebsiella pneumoniae complex, Kleborate v3 uses a preset and integrates Kaptive,
returning ST, K capsule and O lipopolysaccharide antigens, and resistance and virulence
markers:

```bash
kleborate -a genomes/*.fasta -o kleborate_out -p kpsc --trim_headers
# K. oxytoca complex uses -p kosc; Escherichia can use -p escherichia; older v2 uses --all
```

For E. coli/Shigella, ECTyper calls O:H and ShigEiFinder distinguishes Shigella from
enteroinvasive E. coli:

```bash
ectyper -i genomes/ -o ectyper_out --cores 16
ShigEiFinder --input genomes --output shigeifinder_out   # check flags with --help per version
```

For Salmonella, SeqSero2 derives the antigenic formula and SISTR reports serovars with its
own cgMLST:

```bash
seqsero2_assembly -t 16 -m k -i ${id}.fasta -o seqsero2/$id
sistr -i ${id}.fasta -p cgmlst_profiles -n novel_alleles -o sistr/$id
```

Listeria monocytogenes has no classical O/H serotype and uses molecular serogroups together
with cgMLST.

## cgMLST unified through chewBBACA

For every organism, cgMLST follows schema creation, allele calling, core extraction and
quality evaluation. A public schema is loaded when available, otherwise PrepExternalSchema
builds one:

```bash
chewBBACA.py CreateSchema     -i allele_fasta/ --ptf training/.trn -o schema
chewBBACA.py AlleleCall       -i genomes/ -g schema -o calls --ptf training.trn --cpu 16
chewBBACA.py ExtractCgMLST    -i calls/cgmlst.tsv -o cg --r 0.95
chewBBACA.py AlleleCallEvaluator -g schema -i calls --ptf training.trn -o eval
```

The core allele matrix yields pairwise allele distances and a minimum spanning tree for
outbreak tracing. It complements the core-SNP tree of module 09: cgMLST fits closely
related, short-term outbreaks, whereas the SNP tree fits cross-clonal or longer
timescales.

## Interpreting the results

MLST identifies the clonal lineage, serotyping identifies surface-antigen type, and cgMLST
quantifies how many core alleles separate samples. An outbreak call usually requires very
few cgMLST allele differences together with concordant epidemiology and a time tree; a
single typing result alone is not sufficient.
