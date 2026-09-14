# easyWGS Guidebook

easyWGS is a reproducible workflow and companion guidebook for bacterial isolate
whole-genome sequencing (WGS). It follows the numbered-directory style of
EasyMicrobiome and EasyMetagenome: each analysis stage maps to one numbered folder,
the script inside runs on a batch after editing the parameters at the top, and stages
connect through a consistent naming scheme. The workflow supports Illumina short reads,
Oxford Nanopore and PacBio long reads, and hybrid assemblies, and treats decontamination
at both the read and assembly levels as quality gates so that host reads, PhiX or other
species do not propagate into typing and phylogenetic analyses.

## What this workflow solves

Raw isolate data often contain host, PhiX or other bacterial material, and long reads can
assemble such contamination into a single long, misleading contig. Assembling and typing
such data directly produces incorrect sequence types, serotypes and phylogenetic
positions. easyWGS covers the full path from raw FASTQ to a time-scaled tree in a
fixed order and reports completeness, contamination and chimerism at the critical gates,
so that only assemblies that pass move downstream.

## Workflow overview

```text
Raw FASTQ
 ├─ Short:  fastp → CLEAN decontamination → Unicycler/SPAdes assembly
 ├─ Long:   porechop/NanoPlot/Filtlong → Flye/Canu → Racon → Medaka
 └─ Hybrid: cleaned short + long reads → Unicycler bold/SPAdes hybrid → Pilon polish
        ↓
 04 QUAST + CheckM2 + GUNC (+FCS-GX) assembly quality gate
        ↓
 05 annotation → 06 MLST/serotype/cgMLST → 07 AMR, virulence and MGEs
        ↓
 08 pangenome → 09 core-SNP phylogeny → 10 TreeTime time tree → 99 summary
```

## Scope

The typing schedules are preconfigured for the major pathogens Klebsiella pneumoniae
complex, Escherichia coli/Shigella, Salmonella enterica and Listeria monocytogenes. For
other organisms, run the generic steps with `species=other` and attach a cgMLST schema as
needed. The intended user has a Linux workstation, WSL2 or an HPC cluster; database size
and memory requirements are listed step by step in the Installation chapter.

## Where to start

First-time users should read Installation, Quick start and Inputs and samplesheet in
order. Readers who already hold assemblies and only need typing or a tree can jump
directly to the relevant module chapter. Use the language switcher in the header to
toggle between English (default) and Simplified Chinese.
