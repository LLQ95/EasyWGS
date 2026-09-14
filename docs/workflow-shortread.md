# Short-read (Illumina) workflow

Scripts: `01_qc/01.fastp.sh`, `02_decontam_reads/02.clean_reads.sh`, and the
platform=illumina branch of `03_assembly/03.assemble.sh`.

## QC and trimming

fastp performs adapter detection, sliding-window quality trimming and short-read removal
in one pass and writes an HTML report. For bacterial isolates, use moderate thresholds so
that conserved but GC-rich regions are not removed:

```bash
fastp -i ${id}_R1.fastq.gz -I ${id}_R2.fastq.gz \
      -o clean/${id}_R1.fq.gz -O clean/${id}_R2.fq.gz \
      -q 20 -l 50 -w 8 -h qc/${id}.html -j qc/${id}.json \
      --detect_adapter_for_pe --correction
```

FastQC and MultiQC summarize the batch; focus on residual adapters, read-length
distribution and duplication rate.

## Read-level decontamination

Trimmed paired reads enter module 02. CLEAN keeps reads that match the target taxon by
default, and Kraken2 can first profile the composition to judge the contamination
fraction. When close relatives coexist, use less aggressive settings so homologous reads
are not deleted. See Two-layer decontamination and quality gates for detail.

## Assembly

For a single isolate the script uses Unicycler by default. On isolate data it usually
returns a cleaner assembly than running SPAdes directly, handles plasmids better and tends
to circularize. For uniform parameters across many samples or high-coverage data, switch
to `spades.py --isolate`:

```bash
# Default: Unicycler
unicycler -1 ${id}_R1.fq.gz -2 ${id}_R2.fq.gz -o run/$id -t 16 --min_fasta_length 200

# Alternative: SPAdes isolate mode
spades.py --isolate -1 R1 -2 R2 -o run/$id -t 16 -m 128
```

After assembly, fragments shorter than 200 nt are removed and the result is standardized
to `03_assembly/genomes/{id}.fasta`. seqkit or assembly-stats reports contig count, N50,
total length and GC.

## What this stage should achieve

Genome size and GC of conspecific isolates fall within a narrow range; a large deviation
often indicates contamination or a mixture. A short-read draft usually has tens to a few
hundred contigs. The goal is not the smallest contig count but the absence of misjoins,
which module 04 assesses through completeness, contamination and chimerism.

## Common issues

Coverage below roughly 30-fold gives a fragmented assembly; flag the sample and sequence
more. Breaks caused by repeats are normal, so do not merge contigs merely to reduce their
count. Short reads cannot reliably separate highly repeated plasmid and chromosomal
segments; use hybrid or long-read assembly when plasmid structure matters.
