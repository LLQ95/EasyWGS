#!/usr/bin/env python3
"""Derive a genotype-based MDR trait after module 07 for the GWAS demonstration.

Measured MICs or susceptibility results are not available for the public panel,
so no phenotype is invented. Following the standard epidemiological definition,
an isolate is flagged MDR_genotypic=1 when acquired AMR genes span at least
three distinct AMRFinderPlus drug Classes (AMR Element type only; metal, biocide,
stress and virulence elements are excluded). This is a genotype proxy and must
be reported as such; replace it with measured phenotypes for a real study.

Updates the MDR_genotypic column of examples/generated/traits.tierN.csv and, if
present, config/traits.csv, then module 13 can be rerun with TRAIT=MDR_genotypic.
"""
import csv, glob, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
MIN_CLASSES = 3

def classes_per_isolate():
    out = collections.defaultdict(set)
    pats = ["07_amr_vf_mge/**/amrfinder/**/*.tsv",
            "07_amr_vf_mge/**/*amrfinder*.tsv",
            "07_amr_vf_mge/**/AMRFinder*.tsv"]
    files = [f for p in pats for f in glob.glob(os.path.join(ROOT, p), recursive=True)]
    for path in {os.path.abspath(f) for f in files}:
        sid = os.path.basename(path).split(".")[0]
        try:
            with open(path, newline="", encoding="utf-8", errors="ignore") as fh:
                rows = list(csv.DictReader(fh, delimiter="\t"))
        except Exception:
            continue
        if not rows:
            continue
        etype = next((c for c in rows[0] if c.strip().lower() == "element type"), "")
        eclass = next((c for c in rows[0] if c.strip() == "Class"), "")
        for r in rows:
            if etype and r.get(etype, "").strip().upper() != "AMR":
                continue
            if eclass and r.get(eclass, "").strip():
                out[sid].add(r[eclass].strip())
    return out

def update(path, mdr):
    if not os.path.exists(path):
        return
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh)); fields = fh and list(rows[0].keys()) if rows else []
    if not rows or "Name" not in rows[0]:
        return
    if "MDR_genotypic" not in rows[0]:
        fields.append("MDR_genotypic")
    for r in rows:
        if r["Name"] in mdr:
            r["MDR_genotypic"] = mdr[r["Name"]]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
    print("updated", os.path.relpath(path, ROOT))

def main():
    tier = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].isdigit() else "3"
    cls = classes_per_isolate()
    if not cls:
        print("No AMRFinderPlus reports found yet (run module 07 first); leaving traits unchanged.")
        return
    mdr = {sid: (1 if len(c) >= MIN_CLASSES else 0) for sid, c in cls.items()}
    for sid, c in sorted(cls.items()):
        print(f"  {sid}: {len(c)} drug classes -> MDR_genotypic={mdr[sid]}")
    update(os.path.join(ROOT, "examples", "generated", f"traits.tier{tier}.csv"), mdr)
    update(os.path.join(ROOT, "config", "traits.csv"), mdr)

if __name__ == "__main__":
    main()
