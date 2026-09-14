#!/usr/bin/env bash
# =============================================================================
# 07_amr_vf_mge/07.amr_vf_mge.sh - resistance, virulence, point mutations, MGEs
#   abricate multi-DB (CARD/ResFinder/NCBI/VFDB/PlasmidFinder/ISfinder/mobileOG/BacMet)
#   AMRFinderPlus, RGI (CARD), PointFinder chromosomal point mutations
#   geNomad (plasmid/prophage), Mob-suite (plasmid reconstruction),
#   antiSMASH (secondary-metabolite BGC, optional)
# =============================================================================
set -euo pipefail
THREADS=8
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
GEN="$PROJECT/03_assembly/genomes"
OUT="$PROJECT/07_amr_vf_mge"; mkdir -p "$OUT"/{abricate,amrfinder,rgi,pointfinder,genomad,mobsuite,antismash}
DBROOT=${DBROOT:-$HOME/easyWGS_db}

# ---- 1) abricate batch annotation over multiple databases + summary ----
for db in card resfinder ncbi vfdb plasmidfinder ISfinder mobileOG BacMet2_EXP_database; do
  echo ">>> abricate --db $db"
  for f in "$GEN"/*.fasta; do abricate --threads "$THREADS" --db "$db" "$f"; done \
      | tee >(awk 'NR==1 || $0 !~ /^#File/' > "$OUT/abricate/${db}.tab") >/dev/null
done
abricate --summary "$OUT"/abricate/*.tab > "$OUT/abricate/summary.tab"

# ---- 2) AMRFinderPlus (genes + chromosomal mutations; -p protein optional, nucleotide here) ----
amrfinder --force_update -d "$DBROOT/amrfinder_db" || true
for f in "$GEN"/*.fasta; do
  id=$(basename "$f" .fasta)
  amrfinder -n "$f" -o "$OUT/amrfinder/${id}.tsv" --threads "$THREADS" --mutation_all "$OUT/amrfinder/${id}_mut.tsv"
done

# ---- 3) RGI (CARD, protein homology, DIAMOND accelerated) ----
for f in "$GEN"/*.fasta; do
  id=$(basename "$f" .fasta)
  rgi main --input_sequence "$f" --output_file "$OUT/rgi/$id" \
           --local --clean -a DIAMOND --threads "$THREADS"
done

# ---- 4) PointFinder chromosomal point mutations (set species via -s; avoid underscores/dots in names) ----
SPECIES=${SPECIES:-salmonella}   # ecoli / klebsiella / campylobacter ...
for f in "$GEN"/*.fasta; do
  id=$(basename "$f" .fasta)
  python3 PointFinder.py -i "$f" -o "$OUT/pointfinder/$id" \
          -p "$DBROOT/pointfinder_db" -s "$SPECIES" -m blastn \
          -m_p "$(which blastn)" || echo "PointFinder needs a separate DB download and a valid -s species"
done

# ---- 5) geNomad: plasmid / prophage / integrative elements ----
for f in "$GEN"/*.fasta; do
  id=$(basename "$f" .fasta)
  genomad end-to-end --cleanup --splits "$THREADS" "$f" "$OUT/genomad/$id" "$DBROOT/genomad_db"
done

# ---- 6) Mob-suite plasmid reconstruction and typing ----
for f in "$GEN"/*.fasta; do
  id=$(basename "$f" .fasta)
  mob_recon -i "$f" -o "$OUT/mobsuite/$id" -t "$THREADS"
done

# ---- 7) antiSMASH secondary-metabolite BGCs (on demand, slow; input gbk) ----
# for gbk in "$PROJECT"/05_annotation/prokka/*/*.gbk; do
#   id=$(basename "$gbk" .gbk)
#   antismash "$gbk" --output-dir "$OUT/antismash/$id" --asf --pfam2go --fullhmmer --cpus "$THREADS"
# done
echo "[done] AMR/virulence/MGE results: $OUT (summary.tab is the abricate hit summary across DBs)"
