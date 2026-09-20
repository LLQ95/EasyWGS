#!/usr/bin/env python3
"""Subset a generated tier panel to one species_code or group for comparative runs.

Modules 08 (pangenome), 09 (core-SNP), 10 (TreeTime), 12 (reference mapping) and
13 (GWAS) assume a single species with one shared reference, so on the mixed
multi-pathogen panel they must be run on a single-species subset. This helper
filters the generated samplesheet, dates and traits files for one tier and
writes a self-contained subset directory that can be copied into config/.

Examples:
  python examples/scripts/subset_samplesheet.py 4 campylobacter
  python examples/scripts/subset_samplesheet.py 3 salmonella
  python examples/scripts/subset_samplesheet.py 4 shigella --by group

Outputs (examples/generated/subset_<by>_<key>/):
  samplesheet.csv, metadata_dates.csv, traits.csv
"""
import csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "..", "generated")
PANEL = os.path.join(HERE, "..", "panel.tsv")


def read_panel():
    rows = []
    with open(PANEL, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            rows.append(line.split("\t"))
    header, data = rows[0], rows[1:]
    return [dict(zip(header, r)) for r in data]


def filter_csv(path, id_col, keep):
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = [r for r in reader if r[id_col] in keep]
        return reader.fieldnames, rows


def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        w.writerows(rows)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    tier = int(sys.argv[1])
    key = sys.argv[2]
    by = "species"
    if "--by" in sys.argv:
        by = sys.argv[sys.argv.index("--by") + 1]
    field = "group" if by == "group" else "species_code"

    panel = [r for r in read_panel()
             if int(r["tier"]) <= tier and r[field] == key]
    keep = {r["id"] for r in panel}
    if not keep:
        sys.exit(f"no tier-{tier} isolates with {field}={key}")

    out = os.path.join(GEN, f"subset_{by}_{key}")
    os.makedirs(out, exist_ok=True)
    jobs = [
        (f"samplesheet.tier{tier}.csv", "id", "samplesheet.csv"),
        (f"metadata_dates.tier{tier}.csv", "name", "metadata_dates.csv"),
        (f"traits.tier{tier}.csv", "Name", "traits.csv"),
    ]
    for src, id_col, dst in jobs:
        header, rows = filter_csv(os.path.join(GEN, src), id_col, keep)
        write_csv(os.path.join(out, dst), header, rows)

    refs = sorted({r["ref_label"] for r in panel})
    print(f"subset {by}={key}: {len(keep)} isolates -> {os.path.relpath(out)}")
    print("reference(s):", ", ".join(refs))
    print("next:")
    print(f"  cp {os.path.relpath(out)}/samplesheet.csv config/my_samples.csv")
    print(f"  cp {os.path.relpath(out)}/metadata_dates.csv config/metadata_dates.csv")
    print(f"  cp {os.path.relpath(out)}/traits.csv config/traits.csv")
    print("  bash run_all.sh config/my_samples.csv 08")


if __name__ == "__main__":
    main()
