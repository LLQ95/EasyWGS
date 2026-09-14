#!/usr/bin/env Rscript
# =============================================================================
# 13_gwas/13.4.post_gwas.R - shared post-GWAS processing for module 13.
# Reads whatever association results exist (Scoary, PLINK, pyseer), applies
# Benjamini-Hochberg and Bonferroni correction (if not already present),
# draws QQ and Manhattan/locus plots, and writes tables of FDR-significant hits.
#
# Usage: Rscript 13.4.post_gwas.R [project_root]
# Looks under 13_gwas/scoary, 13_gwas/plink, 13_gwas/pyseer and writes to
# 13_gwas/post/. Optional annotation: 05_annotation/*/*.gff is used to label
# gene hits when present, but the script also runs without it.
# =============================================================================
args <- commandArgs(trailingOnly = TRUE)
# Default assumes the script is launched from inside 13_gwas (parent = project root)
PROJECT <- if (length(args) >= 1) args[1] else normalizePath(file.path(getwd(), ".."), mustWork = FALSE)
G <- file.path(PROJECT, "13_gwas"); OUT <- file.path(G, "post"); dir.create(OUT, showWarnings = FALSE, recursive = TRUE)
FDR <- 0.05
suppressMessages(library(ggplot2))
neglog <- function(p) -log10(p)
write_top <- function(d, pcol, file) {
  d$p_bh <- p.adjust(d[[pcol]], method = "BH")
  d$p_bonf <- p.adjust(d[[pcol]], method = "bonferroni")
  d <- d[order(d[[pcol]]), ]
  write.csv(d, file, row.names = FALSE)
  d[!is.na(d$p_bh) & d$p_bh < FDR, , drop = FALSE]
}
qq_plot <- function(p, name) {
  p <- p[is.finite(p) & p > 0 & p <= 1]; if (length(p) < 5) return(invisible())
  o <- sort(p); exp <- (seq_along(o) - 0.5) / length(o)
  q <- data.frame(observed = neglog(o), expected = neglog(exp))
  ggplot(q, aes(expected, observed)) +
    geom_abline(slope = 1, intercept = 0, linetype = "dashed", colour = "grey50") +
    geom_point(size = 0.8, colour = "#2166ac") +
    labs(title = paste0("QQ plot - ", name), x = "Expected -log10(P)", y = "Observed -log10(P)") +
    theme_bw(base_size = 11)
  ggsave(file.path(OUT, paste0("qq_", name, ".pdf")), width = 5, height = 5)
  ggsave(file.path(OUT, paste0("qq_", name, ".png")), width = 5, height = 5, dpi = 300)
}

# ---- 1) pyseer: gene and SNP tables (columns: variant, ..., lrt-pvalue, beta ...) ----
for (kind in c("genes", "snps")) {
  f <- file.path(G, "pyseer", paste0("assoc_", kind, ".txt"))
  if (file.exists(f)) {
    d <- tryCatch(read.csv(f, sep = "\t", check.names = FALSE), error = function(e) NULL)
    if (!is.null(d) && nrow(d) > 0) {
      pcol <- if ("lrt-pvalue" %in% names(d)) "lrt-pvalue" else grep("pvalue|p-value|^p$", names(d), value = TRUE)[1]
      if (!is.na(pcol)) {
        top <- write_top(d, pcol, file.path(OUT, paste0("pyseer_", kind, "_all.csv")))
        write.csv(top, file.path(OUT, paste0("pyseer_", kind, "_FDRhits.csv")), row.names = FALSE)
        qq_plot(d[[pcol]], paste0("pyseer_", kind))
        if (kind == "snps") {               # Manhattan for position-coded SNPs
          loc <- do.call(rbind, strsplit(as.character(d$variant), "[:_ |]+"))
          if (ncol(loc) >= 2) {
            d$chr <- loc[, 1]; d$pos <- suppressWarnings(as.numeric(loc[, 2]))
            d <- d[!is.na(d$pos), ]; d$mlp <- neglog(d[[pcol]])
            p <- ggplot(d, aes(pos, mlp)) + geom_point(size = 0.7, aes(colour = chr), show.legend = FALSE) +
              geom_hline(yintercept = -log10(FDR / nrow(d)), linetype = "dashed", colour = "red") +
              facet_grid(~ chr, scales = "free_x", space = "free_x") +
              labs(title = "Manhattan - pyseer SNPs", x = "Reference position", y = "-log10(P)") +
              theme_bw(base_size = 11)
            ggsave(file.path(OUT, "manhattan_pyseer_snps.pdf"), p, width = 9, height = 4)
            ggsave(file.path(OUT, "manhattan_pyseer_snps.png"), p, width = 9, height = 4, dpi = 300)
          }
        }
      }
    }
  }
}

# ---- 2) PLINK: fast .assoc and logistic/linear regression ----
for (pf in list.files(file.path(G, "plink"), pattern = "\\.assoc(\\.logistic|\\.linear)?$", full.names = TRUE)) {
  d <- tryCatch(read.table(pf, header = TRUE, stringsAsFactors = FALSE), error = function(e) NULL)
  if (is.null(d) || nrow(d) == 0) next
  pcol <- if ("P" %in% names(d)) "P" else grep("^P$", names(d), value = TRUE)[1]
  if (is.na(pcol)) next
  tag <- sub("\\.assoc(\\.logistic|\\.linear)?$", "", basename(pf))
  d <- d[d$TEST %in% c(NA, "ADD") | !"TEST" %in% names(d), , drop = FALSE]
  top <- write_top(d, pcol, file.path(OUT, paste0("plink_", tag, "_all.csv")))
  write.csv(top, file.path(OUT, paste0("plink_", tag, "_FDRhits.csv")), row.names = FALSE)
  qq_plot(d[[pcol]], paste0("plink_", tag))
  if (all(c("BP", "CHR") %in% names(d))) {
    d$mlp <- neglog(d[[pcol]])
    p <- ggplot(d, aes(BP, mlp)) + geom_point(size = 0.7, aes(colour = factor(CHR)), show.legend = FALSE) +
      geom_hline(yintercept = 5e-8, linetype = "dashed", colour = "grey40") +
      geom_hline(yintercept = -log10(FDR / nrow(d)), linetype = "dashed", colour = "red") +
      facet_grid(~ CHR, scales = "free_x", space = "free_x") +
      labs(title = paste("Manhattan - PLINK", tag), x = "Reference position", y = "-log10(P)") +
      theme_bw(base_size = 11)
    ggsave(file.path(OUT, paste0("manhattan_plink_", tag, ".pdf")), p, width = 9, height = 4)
    ggsave(file.path(OUT, paste0("manhattan_plink_", tag, ".png")), p, width = 9, height = 4, dpi = 300)
  }
}

# ---- 3) Scoary: per-trait gene tables (Naive_p, BH_p ...) ----
sdir <- file.path(G, "scoary")
if (dir.exists(sdir)) {
  for (f in list.files(sdir, pattern = "\\.csv$", full.names = TRUE)) {
    d <- tryCatch(read.csv(f, check.names = FALSE), error = function(e) NULL)
    if (is.null(d) || nrow(d) == 0) next
    pcol <- if ("Naive_p" %in% names(d)) "Naive_p" else grep("p$|P$", names(d), value = TRUE)[1]
    if (is.na(pcol)) next
    tag <- sub("\\.csv$", "", basename(f))
    top <- write_top(d, pcol, file.path(OUT, paste0("scoary_", tag, "_all.csv")))
    write.csv(top, file.path(OUT, paste0("scoary_", tag, "_FDRhits.csv")), row.names = FALSE)
    qq_plot(d[[pcol]], paste0("scoary_", tag))
  }
}

# ---- 4) Combined ranked hit list (FDR significant across all methods) ----
hits <- list.files(OUT, pattern = "_FDRhits\\.csv$", full.names = TRUE)
comb <- do.call(rbind, lapply(hits, function(f) {
  d <- read.csv(f, check.names = FALSE); if (nrow(d) == 0) return(NULL)
  label <- sub("_FDRhits\\.csv$", "", basename(f))
  idcol <- intersect(c("Gene", "variant", "SNP"), names(d))[1]
  data.frame(method = label, feature = as.character(d[[idcol]]),
             p_bh = d$p_bh, stringsAsFactors = FALSE)
}))
if (!is.null(comb) && nrow(comb) > 0) {
  comb <- comb[order(comb$p_bh), ]; write.csv(comb, file.path(OUT, "combined_FDRhits.csv"), row.names = FALSE)
  cat(nrow(comb), "FDR-significant features written to combined_FDRhits.csv\n")
} else {
  cat("No FDR-significant hits at FDR =", FDR, "(this is common for small clonal panels).\n")
}
cat("[done] post-GWAS tables and figures in", OUT, "\n")
