# Visualization and interactive exploration

Module 11 sits downstream of typing, the pangenome, the SNP phylogeny and the time tree. It
turns their outputs into readable figures and into upload bundles for web viewers, following a
split between static publication figures made locally and interactive figures made in the
browser:

- Static figures with R: `ggtree` for annotated trees and `pheatmap` for distance and gene
  matrices. These render without a network connection and are the versions used in a paper.
- Minimum spanning trees with GrapeTree on cgMLST profiles or the core alignment.
- Interactive web exploration with iTOL, Microreact, Phandango and icytree. Module 11 only
  prepares the files; the upload itself is a manual step.

## Step 11.1 merged annotation table

`make_metadata.py` joins the samplesheet with `99_report/master_table.tsv` into one
`11_visualization/merged_metadata.csv` (species, ST, serotype, date, country, phenotype,
completeness and per-database hit counts). Every later script reads this single table, so edit
it in one place if a label or grouping must change.

```bash
bash 11_visualization/11.1.build_metadata.sh
```

## Static trees with ggtree (11.2)

`plot_trees.R` reads the module-09 core-SNP tree, the optional module-08 core-gene tree and the
module-10 time-calibrated tree, and writes rectangular and circular versions in both PDF and
PNG under `11_visualization/figures/`. Tip points are colored by species and stacked color
strips show ST, country, phenotype and serotype when those columns are populated. The time tree
uses a year axis.

```bash
Rscript 00_install/install_R_packages.R     # once: ape, ggtree, treeio, pheatmap, ...
bash 11_visualization/11.2.plot_trees.sh
```

Tip labels must equal the isolate `id`. If a tree is drawn without annotation while metadata
exists, the upstream headers (for example snippy-core sample names) do not match the samplesheet
ids; rename consistently rather than editing the figure.

## Minimum spanning tree with GrapeTree (11.3)

GrapeTree builds an MSTreeV2 network from the chewBBACA cgMLST allele matrix, or directly from
the recombination-filtered core alignment, and copies a matching metadata table for coloring:

```bash
bash 11_visualization/11.3.grapetree.sh
# output: 11_visualization/grapetree/*.nwk + grapetree_metadata.csv
```

Open the Newick file and metadata table at the [GrapeTree web app](https://achtman-lab.github.io/GrapeTree)
for an interactive network, or run `grapetree --website` locally. cgMLST networks are the usual
choice for outbreak clustering; the core-SNP network is a cross-check of the module-09 tree.

## iTOL annotation datasets (11.4)

`make_itol_datasets.py` writes iTOL text files under `11_visualization/itol/`: color strips for
species, ST, country, phenotype and serotype, plus a binary track of which abricate databases
have a hit. Upload a Newick tree at [iTOL](https://itol.embl.de), then drag these files onto the
tree. This is the most flexible route for a tree carrying many annotation tracks.

## Heatmaps (11.5)

`heatmaps.R` produces three clustered heatmaps in PDF and PNG: the pairwise SNP distance matrix,
abricate hit counts per database, and a gene-by-isolate presence/absence matrix for the forty
most frequent genes. Row and column side bars follow the merged metadata. Set
`RSCRIPT=/path/to/Rscript` to use a specific R installation.

```bash
bash 11_visualization/11.5.heatmaps.sh
```

For larger gene matrices or finer alignment with a tree, use ComplexHeatmap in place of
pheatmap; both are installed by `install_R_packages.R`.

## Interactive web bundles (11.6)

`11.6.online_bundle.sh` collects the trees, merged metadata, iTOL datasets, pangenome
gene-presence table and abricate summary into `11_visualization/online_bundle/` without
connecting to the network:

| Viewer | What to upload | Best for |
| --- | --- | --- |
| [iTOL](https://itol.embl.de) | tree plus `itol/*.txt` | densely annotated, publication-styled trees |
| [Microreact](https://microreact.org) | Newick plus `merged_metadata.csv` | tree with map and timeline; add latitude/longitude columns for the map |
| [Phandango](https://phandango.net) | tree plus `gene_presence_absence.csv` | tree aligned with the pangenome |
| [GrapeTree](https://achtman-lab.github.io/GrapeTree) | MST Newick plus metadata | cgMLST outbreak networks |
| [icytree](https://icytree.org) | one tree file | quick inspection, no account |

## Tool map

| Tool | Role | Source |
| --- | --- | --- |
| ggtree / ggtreeExtra / treeio | annotated R trees and I/O | [YuLab-SMU](https://github.com/YuLab-SMU/ggtree) |
| ape / phangorn | R tree handling and phylogenetics | [ape](https://github.com/emmanuelparadis/ape) |
| GrapeTree | MST/NJ networks | [achtman-lab/GrapeTree](https://github.com/achtman-lab/GrapeTree) |
| pheatmap / ComplexHeatmap | clustered matrices | [pheatmap](https://github.com/raivokolde/pheatmap) |
| FigTree | desktop tree viewer | [rambaut/figtree](https://github.com/rambaut/figtree) |
| iTOL / Microreact / Phandango / icytree | interactive web viewers | linked above |

Static and interactive figures should tell the same story. Keep the same color encoding for a
variable across figures, and state the tree source (core SNP, core gene or cgMLST) in every
legend so that a network layout is never read as a phylogenetic branch-length tree.
