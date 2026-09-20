# Two-layer decontamination and quality gates

Contamination is the most error-prone part of isolate analysis. EasyWGS sets one gate
at the read level and another at the assembly level: the first removes non-target reads
before assembly, and the second quantifies and removes residual foreign fragments after
assembly.

## Layer one: read decontamination (module 02)

The main tool is CLEAN, which handles short reads, long reads and FASTA, keeps sequences
that match the target taxon and uses conservative settings to limit the erroneous removal
of close relatives:

```bash
nextflow run rki-mf1/clean -profile docker \
  --single_end false --reads "clean/*_R{1,2}.fq.gz" \
  --taxonomy "Klebsiella pneumoniae" --keep_taxon true --outdir clean_out
```

A Kraken2 profile first estimates the contamination fraction and its source organisms:

```bash
kraken2 --db $K2_DB --paired R1.fq.gz R2.fq.gz --threads 16 \
        --report k2.report.txt --output - >/dev/null
```

BBDuk (removal by adapter, rRNA or known references), HoCoRT and deacon are auxiliary
options. When close relatives coexist, do not aim to remove every non-target read;
over-aggressive deletion erodes conserved regions of the target genome.

## Layer two: assembly assessment and cleaning (module 04)

After assembly, QUAST reports structural metrics, CheckM2 computes completeness and
contamination, and GUNC detects chimeras where two species were merged into one genome.
For thorough foreign-fragment removal, add NCBI FCS-GX or BlobToolKit:

```bash
# --database_path is optional; module 04 fills it from $CHECKM2_DB or $DBROOT/checkm2_db
checkm2 predict --threads 16 --input genomes/ --output-directory checkm2 -x fasta \
  --database_path "$CHECKM2_DB"
gunc run genomes/${id}.fasta -d $GUNC_DB --threads 16 -o gunc
# FCS-GX (about 470 GB database, large RAM; run on usegalaxy.org otherwise)
fcs.py screen genome --fasta ${id}.fasta --out-dir fcs --gx-db $GXDB
fcs.py clean genome  --fasta ${id}.fasta --action-report fcs/*.txt --output cleaned.fasta
```

`CHECKM2_DB` may be the `uniref100.KO.1.dmnd` file or its `CheckM2_database` directory,
which lets the workflow reuse a shared database; when it is unset, module 04 looks under
`$DBROOT/checkm2_db` and otherwise falls back to the location registered with
`checkm2 database --setdblocation`.

## Species confirmation with FastANI (module 04.5)

Completeness and contamination scores do not by themselves prove that an assembly is the
intended species. On a mixed multi-species panel, module 04.5 screens every assembly against
all panel references with FastANI and keeps the highest-ANI match in
`04_asm_qc/fastani/fastani_best.tsv`. An ANI of at least 95% to the expected reference
confirms the species, 90 to 95% indicates a congeneric close relative and a missing
species-level reference, and a lower or empty result flags a possible sample-label error or
residual contamination. FastANI reports no pair below roughly 80% ANI, so an unrelated
contaminant yields an empty result rather than a misleading low score. This gate is the
identity counterpart of CheckM2 and GUNC; its use for the specialized pathogen groups is
described on the [Specialized pathogens](specialized-pathogens.md) page.

## Gate criteria and actions

Only assemblies with high completeness, contamination below about 1% and no GUNC clade
separation move directly downstream. For mild contamination, remove foreign contigs and
rerun the 04 assessment; for heavy contamination or clear chimerism, return to 02, increase
cleaning stringency and reassemble rather than typing a contaminated genome. The gate
results are written to a batch QC table to support the methods and data-quality section of a
paper.

## Why long reads depend more on the assembly gate

Short k-mer classification on ultra-long contigs produces partial hits and overall
misclassification, and long-read assemblers tend to concatenate all observed sequences into
long fragments. Long-read and hybrid data therefore cannot rely on Kraken alone and should
use assembly-level evidence from CheckM2, GUNC and FCS-GX, supplemented when needed by
minimap2 alignment of long reads against known contaminant references.

## Cross-check with typing

Even when the numeric gate passes, use the 06 MLST and serotype results as a reverse check.
Two high-confidence STs from one isolate, or two homozygous alleles at the same
housekeeping locus, often signal residual contamination or a mixed sample. Return to this
layer instead of forcing one of the two results.
