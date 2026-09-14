# Two parallel analysis strategies

easyWGS supports two parallel main routes that start from the same cleaned
reads but answer different questions: an assembly-based route that reconstructs
each genome de novo, and a reference-based route that aligns reads directly to
one finished genome into BAM files and calls variants with bcftools. Both routes
feed the same typing, reporting and visualization layers, and they can be run
separately or together so that conclusions can be cross-checked.

## Assembly-based route (de novo)

The route driven by `run_assembly.sh` proceeds as QC (module 01), read-level
decontamination (02), platform-specific assembly (03), an assembly QC and
decontamination gate (04), annotation (05), typing (06), resistance/virulence/
mobile-element screening (07), pangenome clustering (08), a core-SNP phylogeny
built from the assemblies (09), molecular dating (10), the merged report (99)
and the visualization layer (11). Every later step consumes the standardized
files in `03_assembly/genomes/{id}.fasta`.

Because each genome is rebuilt without a reference, the assembly route recovers
the full gene content of an isolate, including genes that a chosen reference
does not carry: accessory genes, plasmids, prophages, integrons, genomic islands
and large insertions or deletions. It is therefore the natural choice for
annotation, pangenome studies, species-wide or phylogenetically diverse
collections, plasmid and mobile-element work, and any project that lacks a
single close, finished reference.

## Reference-based route (read mapping)

The route driven by `run_mapping.sh` proceeds as QC and decontamination (01 to
02), reference mapping in module 12 (BWA-MEM for Illumina, minimap2 for ONT/
PacBio, followed by samtools sorting/indexing and coverage statistics), joint
variant calling in module 12.2 with bcftools into raw, filtered and bi-allelic
VCFs and a genotype matrix, and then microbial GWAS in module 13. An optional
reference-based SNP tree can be built from the bi-allelic VCF and handed to
module 10 for dating, as shown at the top of `run_mapping.sh`.

Every genome is projected onto the same reference coordinates, so sites are
directly comparable across a large number of isolates, calling is sensitive even
at moderate depth, and the computational cost per genome is low. This route is
well suited to clonal outbreak tracing and surveillance, to panels with a
high-quality close reference such as a finished outbreak index genome, to rapid
and uniform SNP/indel tables, and to allele-frequency or low-depth analyses that
de novo assembly cannot provide.

## When to use which

| Dimension | Assembly-based (`run_assembly.sh`) | Reference-based (`run_mapping.sh`) |
| --- | --- | --- |
| Close finished reference | Not required | Strongly recommended |
| Primary output | Contigs, genes, pangenome | BAM, VCF, SNP matrix in one coordinate system |
| Accessory genes / plasmids / MGEs / gene gain-loss | Recovered directly | Restricted to what aligns to the reference |
| SNP/indel sensitivity at moderate depth | Limited by assemblability | High, with per-base depth and genotype quality |
| Uniform cross-sample coordinates | After pangenome/alignment | Native |
| Speed and cost for very large clonal panels | Higher | Lower |
| Outbreak / transmission clustering | Yes (core-SNP on assemblies) | Yes, fastest when a close reference exists |
| Phylogenetically diverse or novel lineage sets | Preferred | Biased by reference choice |
| Structural content and genome size | Recovered | Not directly |
| GWAS feature layer | Gene presence/absence (Scoary, pyseer genes) | SNPs (PLINK, pyseer SNP/VKF) |

In practice the two routes are complementary rather than exclusive. For a
clonal outbreak with a finished index genome, the mapping route gives the
fastest, most sensitive SNP distances, while the assembly route confirms gene
content, resistance determinants and plasmid structure. For a species-wide or
uncharacterized collection, the assembly route is the backbone and the mapping
route is used where a representative reference is available. Running
`run_all.sh` executes both; running only one driver is useful when a project
has a clearly single objective.
