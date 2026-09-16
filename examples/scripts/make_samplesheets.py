#!/usr/bin/env python3
"""Generate EasyWGS config files for each demonstration tier from panel.tsv.

Tiers are nested: tier 1 is the small core (one short-read isolate plus one
hybrid isolate per pathogen, 10 samples), tier 2 adds typing breadth (three
short-read isolates per pathogen, 20 samples) and tier 3 adds the full
12-isolate Salmonella temporal collection used for pangenome, core-SNP,
TreeTime and GWAS demonstrations (29 samples).

Outputs are written to examples/generated/ and copied into config/ by
01_run_panel.sh. No sequencing data are fabricated: dates and countries are
the ENA collection metadata, and the only derived trait is a binary
country-of-origin flag used to demonstrate the association layer.
"""
import csv, os, datetime, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PANEL = os.path.join(HERE, "..", "panel.tsv")
OUT = os.path.join(HERE, "..", "generated")

def read_panel():
    rows = []
    with open(PANEL, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            rows.append(line.split("\t"))
    header, data = rows[0], rows[1:]
    return [dict(zip(header, r)) for r in data]

def decimal_year(date):
    """ENA dates may be YYYY, YYYY-MM or YYYY-MM-DD. Year-only records are
    placed at mid-year, the standard convention, and flagged as such."""
    parts = date.split("-")
    y = int(parts[0])
    if len(parts) == 1:
        return f"{y + 0.5:.3f}", "year"
    if len(parts) == 2:
        m = int(parts[1])
        return f"{y + (m - 0.5) / 12:.3f}", "month"
    d = datetime.date(y, int(parts[1]), int(parts[2]))
    start = datetime.date(y, 1, 1)
    end = datetime.date(y + 1, 1, 1)
    frac = (d - start).days / (end - start).days
    return f"{y + frac:.3f}", "day"

def main():
    tier = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    os.makedirs(OUT, exist_ok=True)
    panel = [r for r in read_panel() if int(r["tier"]) <= tier]

    ss = os.path.join(OUT, f"samplesheet.tier{tier}.csv")
    with open(ss, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id","platform","species","R1","R2","longreads","reference",
                    "date","country","phenotype"])
        for r in panel:
            sid = r["id"]
            r1 = r2 = lr = ""
            if r["illumina_run"]:
                r1 = f"00_rawdata/{sid}_R1.fastq.gz"
                r2 = f"00_rawdata/{sid}_R2.fastq.gz"
            if r["ont_run"]:
                lr = f"00_rawdata/{sid}_ONT.fastq.gz"
            w.writerow([sid, r["platform"], r["species_code"], r1, r2, lr,
                        f"ref/{r['ref_label']}", r["date"],
                        r["country"].split(":")[0], "NA"])

    dates = os.path.join(OUT, f"metadata_dates.tier{tier}.csv")
    with open(dates, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "date", "date_precision"])
        for r in panel:
            dy, prec = decimal_year(r["date"])
            w.writerow([r["id"], dy, prec])

    # Demonstration binary trait: Italian vs non-Italian origin. This is real,
    # reproducible sample metadata and gives the Salmonella temporal set a
    # two-class trait for Scoary/PLINK/pyseer. It is NOT a measured phenotype;
    # derive_mdr_traits.py adds a genotype-based MDR trait after module 07.
    traits = os.path.join(OUT, f"traits.tier{tier}.csv")
    with open(traits, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Name", "origin_Italy", "MDR_genotypic"])
        for r in panel:
            italy = 1 if r["country"].split(":")[0] == "Italy" else 0
            w.writerow([r["id"], italy, "NA"])

    groups = {}
    for r in panel:
        groups[r["group"]] = groups.get(r["group"], 0) + 1
    print(f"tier {tier}: {len(panel)} samples; by group {groups}")
    print("wrote", os.path.relpath(ss), os.path.relpath(dates),
          os.path.relpath(traits))

if __name__ == "__main__":
    main()
