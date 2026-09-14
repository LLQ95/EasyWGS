# 00_install/install_R_packages.R
# Install the R packages used by module 11 (static tree plots and heatmaps).
# Works with the conda r-base from install_env.sh or a system R (e.g. R 4.x).
# Run once:  Rscript 00_install/install_R_packages.R
options(repos = c(CRAN = "https://cloud.r-project.org"))

cran_pkgs <- c("ape", "ggplot2", "dplyr", "tidyr", "pheatmap",
               "RColorBrewer", "remotes")
bioc_pkgs <- c("ggtree", "treeio", "ComplexHeatmap")

install_cran <- function(p) {
  if (!requireNamespace(p, quietly = TRUE)) install.packages(p, quiet = TRUE)
}

for (p in cran_pkgs) install_cran(p)

if (!requireNamespace("BiocManager", quietly = TRUE)) install.packages("BiocManager", quiet = TRUE)
for (p in bioc_pkgs) {
  if (!requireNamespace(p, quietly = TRUE)) BiocManager::install(p, update = FALSE, ask = FALSE)
}

# Optional: extra aligned annotation layers next to a ggtree object
if (!requireNamespace("ggtreeExtra", quietly = TRUE)) {
  try(BiocManager::install("ggtreeExtra", update = FALSE, ask = FALSE), silent = TRUE)
}

cat("[done] R package check finished. Missing (if any):\n")
missing <- setdiff(c(cran_pkgs, bioc_pkgs), rownames(installed.packages()))
if (length(missing)) cat(paste(" -", missing, collapse = "\n"), "\n") else cat(" all required packages present.\n")
