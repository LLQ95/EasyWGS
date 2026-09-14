# FAQ

## Contamination is slightly above 1%. What should I do

First identify its source: use FCS-GX or BlobToolKit to locate foreign contigs, remove them
and rerun the 04 assessment. If contamination is embedded inside target contigs and cannot
be removed cleanly by contig, return to 02, strengthen read cleaning and reassemble; do not
carry internal chimerism into typing.

## Are long-only results reliable

After a high-quality ONT run with Flye, limited Racon rounds and Medaka, structure and
circularization are reliable, but base-level accuracy still benefits from short-read Pilon
polishing. Without short reads, recheck base-level claims such as resistance genes and point
mutations with a second tool. PacBio HiFi has high per-read accuracy and usually needs
little polishing.

## How many Racon or Medaka rounds

Limit Racon to two or three rounds, since more causes over-correction and erases real
variants. One Medaka pass is enough, provided the model matches the flow cell and basecaller
version. Stacking polishing rounds is not a reliable way to improve quality.

## Why is the hybrid assembly worse

Hybrid assembly also amplifies contamination in the short reads, because long reads assemble
foreign material into complete fragments. Decontaminate the short reads in 02 first and
recheck in 04 with CheckM2/GUNC.

## cgMLST and the core-SNP tree disagree

They operate at different scales: cgMLST allele differences fit close outbreaks and the SNP
tree fits cross-clonal comparisons. If they conflict within one transmission cluster, first
check reference choice, recombination removal and sample contamination before discussing
biology.

## The FCS-GX database is too large to run locally

Without roughly 512 GB RAM, keep CheckM2 and GUNC, run FCS-GX online on usegalaxy.org by
uploading the assembly, and place the cleaned FASTA back into the 04 folder to continue.

## How to reproduce an old project

Record environment versions (`conda list --explicit`), database versions and the samplesheet.
With the same samplesheet and database versions, the step-number argument in run_all
reproduces results from any stage.
