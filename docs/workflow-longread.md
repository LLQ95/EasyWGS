# Long-read and hybrid assembly workflow

The long-read workflow maps to `01_qc/01b.long_qc.sh` and the nanopore, pacbio and hybrid
branches of `03_assembly/03.assemble.sh`. Long reads span repeats and approach a finished
genome, but their error profile and the amplification of contamination demand extra QC and
polishing.

## Long-read QC

First remove adapters, then inspect length and quality with NanoPlot, and finally keep the
best reads with Filtlong by length, mean quality and target bases:

```bash
porechop -i ${id}_ONT.fastq.gz -o trim/${id}.fq.gz -t 16
NanoPlot -t 16 -t trim/${id}.fq.gz -o nanoplot/$id
filtlong --min_length 1000 --min_mean_q 7 --target_bases 400000000 \
         trim/${id}.fq.gz | gzip > clean/${id}_L.fq.gz
```

Set `--target_bases` from genome size and target coverage: fewer but more accurate reads
yield a clean assembly and avoid redundant coverage that slows polishing. ONT flow cells
(R9.4.1 versus R10.4.1) differ in quality distribution, so adjust thresholds accordingly.

## Long-only assembly

Flye is the default assembler; it is robust for bacterial long reads and reports
circularization itself, with Canu as a conservative alternative. Use `--pacbio-hifi` for
PacBio HiFi and `--nano-hq` or `--nano-raw` for ONT:

```bash
flye --nano-hq ${id}_L.fq.gz --genome-size 5m -t 16 --out-dir run/$id/flye
# PacBio HiFi: flye --pacbio-hifi ...
# Alternative: canu -p $id genomeSize=5m -nanopore-raw reads.fq.gz
```

## Polishing: correction should be moderate

Long-read assemblies need consensus polishing, but more polishing is not always better.
The script first aligns with minimap2 and applies two Racon self-correction rounds, then
one neural-network Medaka pass:

```bash
# Two Racon rounds (avoid more than 2–3; over-correction erases real variants)
minimap2 -ax map-ont asm.fasta reads.fq.gz > aln.sam
racon -t 16 reads.fq.gz aln.sam asm.fasta > racon1.fasta
# Medaka: the model must match the flow cell and basecaller version
medaka_consensus -i reads.fq.gz -d racon2.fasta -o medaka -t 16 \
                 -m r1041_e82_400bps_sup_v4.2.0
```

For publication-grade finished genomes, use Trycycler in the longread environment to build
a consensus across several assemblies before Racon and Medaka. This is computationally
heavier and offered as the optional high-quality route.

## Hybrid assembly

With both short and long reads, prefer `unicycler --mode bold`: long reads build the
skeleton across repeats while short reads correct bases, which is favourable for plasmids
and circularization. One Pilon pass with short reads then fills residual errors:

```bash
unicycler --mode bold -1 R1.fq.gz -2 R2.fq.gz -l L.fq.gz -o run/$id -t 16 --keep 0
bwa mem asm.fasta R1.fq.gz R2.fq.gz | samtools sort -o pilon.bam
pilon --genome asm.fasta --frags pilon.bam --fix all
```

SPAdes also offers hybrid mode (`--nanopore` or `--pacbio`) as an independent cross-check.

## Circularization

Flye marks circular contigs with the circ column in `assembly_info.txt`; the Unicycler log
states which fragments circularized; circlator standardizes circularization and fixes the
start. A finished genome should show the chromosome and each plasmid circularized without
extra short contigs.

## The particular decontamination risk of long reads

Short k-mer classifiers such as Kraken lose resolution on very long contigs, and long-read
assemblers tend to stitch every read into long fragments. Long-read and hybrid data
therefore cannot rely on Kraken alone. Move decontamination upstream to the reads and rely
on assembly-level evidence from CheckM2, GUNC and FCS-GX, aligning long reads against known
contaminant references with minimap2 when needed, as discussed in the decontamination
chapter.
