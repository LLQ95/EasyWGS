#!/usr/bin/env Rscript
# =============================================================================
# 11_visualization/heatmaps.R
# Clustered heatmaps for:
#   - 09_phylogeny/snp_dists.tsv            pairwise core-SNP distance
#   - 07 .../abricate/summary.tab           per-DB resistance/virulence hit counts
#   - 07 .../abricate/*.tab (per hit)       gene-by-isolate presence/absence (top genes)
# Row/column annotations come from merged_metadata.csv.
# Usage: Rscript heatmaps.R [EasyWGS root]
# =============================================================================
suppressPackageStartupMessages({
  need <- c("pheatmap", "RColorBrewer")
  miss <- need[!vapply(need, requireNamespace, logical(1), quietly = TRUE)]
})
if (length(miss)) {
  cat("[skip] R packages missing:", paste(miss, collapse = ", "),
      "; run Rscript 00_install/install_R_packages.R\n")
  quit(save = "no", status = 0)
}
suppressPackageStartupMessages(library(pheatmap)); suppressPackageStartupMessages(library(RColorBrewer))

args <- commandArgs(trailingOnly = TRUE)
root <- if (length(args) >= 1) args[1] else normalizePath(getwd())
here <- file.path(root, "11_visualization")
figdir <- file.path(here, "figures"); dir.create(figdir, showWarnings = FALSE, recursive = TRUE)
metap <- file.path(here, "merged_metadata.csv")
if (!file.exists(metap)) {
  cat("[skip] merged_metadata.csv not found; run 11.1.build_metadata.sh first\n")
  quit(save = "no", status = 0)
}
meta <- read.csv(metap, stringsAsFactors = FALSE, check.names = FALSE)
rownames(meta) <- meta$id

iso_id <- function(x) sub("\\.(fasta|fa)$", "", basename(x))

save_hm <- function(ph, fname, w = 9, h = 7) {
  pdf(file.path(figdir, paste0(fname, ".pdf")), width = w, height = h); print(ph); dev.off()
  png(file.path(figdir, paste0(fname, ".png")), width = w, height = h, units = "in", res = 300)
  print(ph); dev.off()
}

row_annot <- function(names_needed) {
  cols <- intersect(c("species", "country", "phenotype"), names(meta))
  ids <- iso_id(names_needed)
  hit <- match(ids, meta$id)
  d <- meta[hit, cols, drop = FALSE]
  rownames(d) <- names_needed
  d <- d[, vapply(cols, function(c) any(!d[[c]] %in% c("", "NA")), logical(1)), drop = FALSE]
  if (ncol(d)) d else NA
}

# ---- 1) pairwise SNP distance ----
snpf <- file.path(root, "09_phylogeny", "snp_dists.tsv")
if (file.exists(snpf)) {
  m <- as.matrix(read.table(snpf, header = TRUE, row.names = 1, sep = "\t", check.names = FALSE))
  storage.mode(m) <- "numeric"
  ann <- row_annot(rownames(m))
  pal <- colorRampPalette(rev(brewer.pal(9, "RdYlBu")))(50)
  ph <- pheatmap(m, color = pal, annotation_row = ann, annotation_col = ann,
                 display_numbers = nrow(m) <= 30, number_color = "grey20",
                 fontsize_number = 6, main = "Pairwise core-SNP distance", silent = TRUE)
  save_hm(ph, "snp_distance_heatmap", w = max(7, 0.28 * nrow(m) + 4), h = max(6, 0.28 * nrow(m) + 3))
  cat("[done] SNP distance heatmap\n")
} else cat("[info] snp_dists.tsv missing; skip SNP heatmap\n")

# ---- 2) abricate per-database hit counts ----
sumf <- file.path(root, "07_amr_vf_mge", "abricate", "summary.tab")
if (file.exists(sumf)) {
  a <- read.table(sumf, header = TRUE, row.names = 1, sep = "\t", check.names = FALSE)
  m <- as.matrix(a); storage.mode(m) <- "numeric"
  rownames(m) <- iso_id(rownames(m))
  ann <- row_annot(rownames(m))
  ph <- pheatmap(m, color = colorRampPalette(brewer.pal(9, "Blues"))(20),
                 annotation_row = ann, cluster_cols = FALSE, display_numbers = TRUE,
                 number_color = "grey20", fontsize_number = 7,
                 main = "abricate hit counts per database", silent = TRUE)
  save_hm(ph, "abricate_summary_heatmap", w = 8, h = max(5, 0.3 * nrow(m) + 2))
  cat("[done] abricate summary heatmap\n")
} else cat("[info] abricate summary.tab missing; skip summary heatmap\n")

# ---- 3) gene-by-isolate presence/absence from per-hit abricate tables ----
tabs <- list.files(file.path(root, "07_amr_vf_mge", "abricate"),
                   pattern = "\\.tab$", full.names = TRUE)
tabs <- setdiff(tabs, sumf)
if (length(tabs)) {
  pa <- list()
  for (tf in tabs) {
    d <- tryCatch(read.table(tf, header = TRUE, sep = "\t", quote = "",
                             comment.char = "", fill = TRUE, check.names = FALSE),
                  error = function(e) NULL)
    if (is.null(d) || nrow(d) == 0 || !"GENE" %in% names(d)) next
    sid <- iso_id(d[[1]])
    for (i in seq_len(nrow(d))) {
      g <- as.character(d$GENE[i]); s <- sid[i]
      if (is.na(g) || g == "") next
      if (is.null(pa[[g]])) pa[[g]] <- c()
      pa[[g]] <- unique(c(pa[[g]], s))
    }
  }
  if (length(pa)) {
    all_iso <- sort(unique(unlist(pa)))
    mat <- matrix(0L, nrow = length(pa), ncol = length(all_iso),
                  dimnames = list(names(pa), all_iso))
    for (g in names(pa)) mat[g, pa[[g]]] <- 1L
    freq <- sort(rowSums(mat), decreasing = TRUE)
    top <- names(head(freq, 40))
    mat <- mat[top, , drop = FALSE]
    ann <- row_annot(colnames(mat)); if (is.logical(ann)) ann <- NA
    ph <- pheatmap(mat, color = c("white", "#d7301f"), legend_breaks = c(0, 1),
                   legend_labels = c("absent", "present"),
                   annotation_col = ann, cluster_cols = TRUE, cluster_rows = TRUE,
                   fontsize_row = 7, main = "Resistance/virulence gene presence (top 40)",
                   silent = TRUE)
    save_hm(ph, "gene_presence_heatmap", w = max(8, 0.25 * ncol(mat) + 4), h = 9)
    cat("[done] gene presence/absence heatmap\n")
  }
} else cat("[info] no per-hit abricate tables; skip gene-presence heatmap\n")

cat("[done] heatmaps.R finished\n")
