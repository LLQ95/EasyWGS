#!/usr/bin/env Rscript
# =============================================================================
# 11_visualization/plot_trees.R
# Static, publication-oriented tree figures with ggtree for:
#   - 09_phylogeny core-SNP ML tree (rectangular + circular/fan)
#   - 08_pangenome optional core-gene tree
#   - 10_treetime time-calibrated tree (year axis)
# Tip annotations (species / ST / country / phenotype / serotype) come from
# 11_visualization/merged_metadata.csv produced by 11.1.build_metadata.sh
# Usage: Rscript plot_trees.R [EasyWGS root]
# =============================================================================
suppressPackageStartupMessages({
  need <- c("ape", "ggplot2", "ggtree", "treeio")
  miss <- need[!vapply(need, requireNamespace, logical(1), quietly = TRUE)]
})
if (length(miss)) {
  cat("[skip] R packages missing:", paste(miss, collapse = ", "),
      "; run Rscript 00_install/install_R_packages.R\n")
  quit(save = "no", status = 0)
}
suppressPackageStartupMessages({ library(ape); library(ggplot2); library(ggtree); library(treeio) })

args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) >= 1) args[1] else normalizePath(getwd())
here <- file.path(root, "11_visualization")
figdir <- file.path(here, "figures")
dir.create(figdir, showWarnings = FALSE, recursive = TRUE)

metap <- file.path(here, "merged_metadata.csv")
if (!file.exists(metap)) {
  cat("[skip] merged_metadata.csv not found; run 11.1.build_metadata.sh first\n")
  quit(save = "no", status = 0)
}
meta <- read.csv(metap, stringsAsFactors = FALSE, check.names = FALSE)
meta$label <- meta$id
nonempty <- function(x) !is.null(x) && any(!x %in% c("", "NA"))

read_any <- function(p) {
  if (grepl("\\.(nex|nexus)$", p, ignore.case = TRUE)) read.nexus(p) else read.tree(p)
}

save_pair <- function(pr, tag, n_tips, circular) {
  h <- max(5, 0.13 * n_tips + 2)
  w <- if (circular) max(9, 0.10 * n_tips + 4) else 12
  ggsave(file.path(figdir, paste0(tag, if (circular) "_circular.pdf" else "_rect.pdf")),
         pr, width = w, height = h, limitsize = FALSE)
  ggsave(file.path(figdir, paste0(tag, if (circular) "_circular.png" else "_rect.png")),
         pr, width = w, height = h, dpi = 300, limitsize = FALSE)
}

draw_tree <- function(treepath, tag, time_axis = FALSE) {
  if (!file.exists(treepath)) return(invisible(FALSE))
  tr <- tryCatch(read_any(treepath),
                 error = function(e) { cat("[skip] cannot read", treepath, "-", conditionMessage(e), "\n"); NULL })
  if (is.null(tr)) return(invisible(FALSE))

  ann <- meta[!duplicated(meta$label), ]
  rownames(ann) <- ann$label
  common <- intersect(tr$tip.label, ann$label)
  if (!length(common)) {
    cat("[info]", tag, ": no tip labels match metadata; drawing an unannotated tree\n")
  }
  strip_cols <- intersect(c("ST", "country", "phenotype", "serotype"), names(ann))
  strip_cols <- strip_cols[vapply(strip_cols, function(c) nonempty(ann[[c]]), logical(1))]

  build <- function(layout) {
    p <- ggtree(tr, layout = layout, size = 0.3)
    if (nonempty(ann$species) && length(common)) {
      p <- p %<+% ann + geom_tippoint(aes(color = species), size = 1.6, na.rm = TRUE)
    }
    p <- p + geom_tiplab(size = 2, align = TRUE, linesize = 0.15)
    off <- 0.03
    for (cc in strip_cols) {
      d <- ann[match(tr$tip.label, ann$label), cc, drop = FALSE]
      rownames(d) <- tr$tip.label
      p <- tryCatch(
        gheatmap(p, d, width = 0.07, offset = off, color = NA,
                 colnames_angle = 40, colnames_offset_y = 0.6, font.size = 2.4),
        error = function(e) p)
      off <- off + 0.09
    }
    p <- p + ggtitle(tag) + theme(plot.title = element_text(size = 9, face = "bold"))
    if (time_axis) p <- p + theme_tree2() + xlab("time (years from node-date scaling)")
    p
  }

  save_pair(build("rectangular"), tag, length(tr$tip.label), FALSE)
  save_pair(build("circular"), tag, length(tr$tip.label), TRUE)
  cat("[done] tree figures for", tag, "->", figdir, "\n")
  invisible(TRUE)
}

draw_tree(file.path(root, "09_phylogeny", "core_iqtree.treefile"), "coreSNP_IQTREE")
draw_tree(file.path(root, "09_phylogeny", "core_fasttree.tre"), "coreSNP_FastTree")
draw_tree(file.path(root, "08_pangenome", "core_gene_tree.treefile"), "coreGene")
draw_tree(file.path(root, "10_treetime", "02_timetree", "timetree.nexus"), "timetree", time_axis = TRUE)

cat("[done] plot_trees.R finished\n")
