#!/usr/bin/env bash
# =============================================================================
# 06_typing/06.3.cgmlst.sh - chewBBACA core-genome MLST (cgMLST)
# Flow: CreateSchema/PrepExternalSchema -> AlleleCall -> ExtractCgMLST ->
#   AlleleCallEvaluator
# Output: cgMLST allele matrix, directly usable by GrapeTree / PHYLOViZ to draw
#   a minimum spanning tree
# =============================================================================
set -euo pipefail
THREADS=8
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
GEN="$PROJECT/03_assembly/genomes"
OUT="$PROJECT/06_typing/cgmlst"; mkdir -p "$OUT"
DBROOT=${DBROOT:-$HOME/easywgs_db/chewie}

# Choose the cgMLST schema by study group (samplesheet species column)
# Schema sources are in 00_install/download_db.sh: INNUENDO (Salmonella) /
# Pasteur (Listeria) / EnteroBase Escherichia-Shigella / public Klebsiella alleles
pick_schema () {
  case "$1" in
    salm)     echo "$DBROOT/salmonella/Salmonella_enterica_INNUENDO_cgMLST" ;;
    listeria) echo "$DBROOT/listeria/Listeria_monocytogenes_Pasteur_cgMLST" ;;
    ecoli)    echo "$DBROOT/ecoli/Escherichia_Shigella_EnteroBase_cgMLST" ;;
    kpsc)     echo "$DBROOT/kpsc/Klebsiella_cgMLST" ;;
    *)        echo "" ;;
  esac
}

while IFS=',' read -r id species rest; do
  [[ "$id" == "id" || "$id" == \#* || -z "$id" ]] && continue
  schema=$(pick_schema "$species")
  [[ -z "$schema" || ! -d "$schema" ]] && { echo "[$id] no cgMLST schema for $species, skip (build one with PrepExternalSchema)"; continue; }
  wd="$OUT/$species"; mkdir -p "$wd"
  echo ">>> cgMLST $id ($species) <- $schema"
  chewBBACA.py AlleleCall -i "$GEN" -g "$schema" -o "$wd/AlleleCall" \
               --cpu "$THREADS" --mode 1
  chewBBACA.py ExtractCgMLST -i "$wd/AlleleCall/results_alleles.tsv" -o "$wd/ExtractCgMLST"
  chewBBACA.py AlleleCallEvaluator -i "$wd/AlleleCall" -g "$schema" \
               -o "$wd/AlleleCallEvaluator" --cpu "$THREADS"
done < "$PROJECT/config/my_samples.csv"

# If only a raw fasta allele set is available, adapt it once into a schema:
# chewBBACA.py PrepExternalSchema -g raw_alleles -o built_schema --cpu 16
# Feed the cgMLST matrix ($OUT/*/ExtractCgMLST/cgMLST.tsv) to GrapeTree for an MST:
# grapetree pg -i cgMLST.tsv -o cgmlst_tree.nw
echo "[done] cgMLST: $OUT/<species>/ExtractCgMLST/cgMLST.tsv (visualize with GrapeTree)"
