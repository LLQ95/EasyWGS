#!/usr/bin/env bash
# =============================================================================
# 04_asm_qc/04.5.fastani_identity.sh - whole-genome ANI species confirmation
#
# Each assembly is screened against EVERY panel reference in ref/ with FastANI
# and the highest-ANI match is kept. This is the species-identity gate for a
# mixed multi-species panel: it separates close relatives (for example
# C. jejuni versus C. coli), confirms that an assembly matches the reference
# named in the samplesheet, and flags possible mislabelling or residual
# contamination before the single-species pangenome/SNP/mapping steps.
#
# Interpretation of the ANI to the closest reference:
#   ANI >= 95% and best reference == expected reference : confirmed species
#   90% <= ANI < 95%                                    : congeneric close
#            relative; add a species-level reference for within-species work
#   ANI < 90%, no hit, or best reference != expected    : review identity/contamination
# FastANI reports no row for pairs below roughly 80% ANI, so an unrelated
# contaminant yields an empty per-sample file rather than a spurious low score.
#
# Input : 03_assembly/genomes/*.fasta and ref/*.fna
# Output: 04_asm_qc/fastani/<id>.ani and the merged fastani_best.tsv
# =============================================================================
set -euo pipefail
THREADS=${THREADS:-8}
PROJECT=${PROJECT:-$(cd "$(dirname "$0")/.." && pwd)}
GEN="$PROJECT/03_assembly/genomes"
REFD="$PROJECT/ref"
OUT="$PROJECT/04_asm_qc/fastani"; mkdir -p "$OUT"
SHEET="$PROJECT/config/my_samples.csv"
source "$PROJECT/00_install/runtime.sh"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$EASYWGS_ENV"

RL="$OUT/ref_list.txt"
: > "$OUT/fastani_best.tsv"
if ! ls "$REFD"/*.fna >/dev/null 2>&1; then
  echo "[warn] no references under ref/ (run examples/00_download_panel.sh --refs); skipping FastANI" >&2
  echo -e "id\texpected_ref\tbest_ref\tbest_ANI\tstatus" > "$OUT/fastani_best.tsv"
  exit 0
fi
if ! command -v fastANI >/dev/null 2>&1 && ! command -v fastani >/dev/null 2>&1; then
  echo "[warn] fastani not installed in $EASYWGS_ENV; skipping module 04.5" >&2
  echo -e "id\texpected_ref\tbest_ref\tbest_ANI\tstatus" > "$OUT/fastani_best.tsv"
  exit 0
fi
FASTANI=$(command -v fastANI || command -v fastani)
ls "$REFD"/*.fna | sort > "$RL"

shopt -s nullglob
for f in "$GEN"/*.fasta; do
  id=$(basename "$f" .fasta)
  o="$OUT/${id}.ani"
  [[ -s "$o" ]] && continue
  "$FASTANI" -q "$f" --rl "$RL" -o "$o" -t "$THREADS" || true
done

# Keep the best ANI hit per assembly and compare it with the samplesheet reference.
python3 - "$SHEET" "$OUT" <<'PY'
import csv, glob, os, sys
sheet, outdir = sys.argv[1], sys.argv[2]
expected = {}
with open(sheet, newline="") as fh:
    for r in csv.DictReader(fh):
        expected[r["id"]] = os.path.basename(r.get("reference", "")).replace(".gbk", ".fna")
rows = []
for p in sorted(glob.glob(os.path.join(outdir, "*.ani"))):
    sid = os.path.basename(p)[:-4]
    best = None
    try:
        with open(p) as fh:
            for line in fh:
                c = line.rstrip("\n").split("\t")
                if len(c) >= 3:
                    ani = float(c[2])
                    if best is None or ani > best[0]:
                        best = (ani, os.path.basename(c[1]))
    except ValueError:
        best = None
    exp = expected.get(sid, "")
    if best is None:
        rows.append((sid, exp, "no_hit_above_80pct", "NA", "review_identity"))
    else:
        ani, ref = best
        if ani >= 95.0 and ref == exp:
            status = "confirmed"
        elif ani >= 90.0:
            status = "close_relative_check_reference"
        else:
            status = "review_identity_or_contamination"
        rows.append((sid, exp, ref, f"{ani:.3f}", status))
with open(os.path.join(outdir, "fastani_best.tsv"), "w", newline="") as fh:
    w = csv.writer(fh, delimiter="\t")
    w.writerow(["id", "expected_ref", "best_ref", "best_ANI", "status"])
    w.writerows(rows)
for r in rows:
    print("\t".join(r))
PY
echo "[done] FastANI species confirmation: $OUT/fastani_best.tsv"
