# Inputs and samplesheet

All batch scheduling is driven by one samplesheet, with the template at
`config/samplesheet.csv`. Copy it to `config/my_samples.csv` for use. The header is fixed
and the column order should not change:

```text
id,platform,species,R1,R2,longreads,reference,date,country,phenotype
```

## Columns

| Column | Required | Values and meaning |
| --- | --- | --- |
| id | yes | Unique sample identifier; no spaces or repeated dots; used in all downstream names |
| platform | yes | illumina / nanopore / pacbio / hybrid; selects the QC and assembly route |
| species | yes | kpsc / ecoli / salm / listeria / other; selects the 06 typing schedule |
| R1,R2 | conditional | Paired short-read paths; leave empty for long-only |
| longreads | conditional | Long-read path; required for nanopore, pacbio and hybrid |
| reference | for 09 | Common reference for core-SNP phylogeny in GenBank format, shared by the batch |
| date | for 10 | Sampling date as YYYY-MM-DD or a decimal year, used by TreeTime |
| country | no | Sampling country or region for state migration (mugration) |
| phenotype | no | Drug-susceptibility or phenotype label for later genotype association |

## Filling by platform

For short reads, fill only R1/R2; for long-only set platform to nanopore or pacbio and
fill only longreads; for hybrid fill R1/R2 and longreads. The three types can be mixed in
one sheet because the 03 script dispatches per row and the project does not need to be
split.

## Naming conventions

The id is reused as a sequence prefix by several tools, so avoid spaces, non-ASCII
characters and consecutive dots. A scheme such as species abbreviation plus year plus
serial number (for example KP2023_001) works well. Whatever the assembly route, the final
result is always written to `03_assembly/genomes/{id}.fasta`, and every module from 04
onward reads only this folder.

## Choosing a reference

The core-SNP analysis in 09 requires one close, complete and well-annotated reference for
the whole batch. A reference that is too distant creates many missing sites and erroneous
alignments. Use mash to identify the closest public genome to the samples before fixing
the reference. Keep reference files in the project under `ref/` (ignored by git) rather
than hard-coding them in scripts.

## Dates and metadata

TreeTime is sensitive to sampling dates; missing or clearly wrong dates appear as outliers
in the clock regression. Use a full date when known and a decimal year (such as 2021.5)
when only the year is certain. The country and phenotype columns are optional and are left
blank for the main chain; they are used only in state migration or genotype–phenotype work.
