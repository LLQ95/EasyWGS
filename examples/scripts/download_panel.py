#!/usr/bin/env python3
"""Download the EasyWGS demonstration panel.

Reads are fetched by run accession from the ENA public FASTQ mirror (which also
mirrors DRR and SRR runs), paired Illumina reads are downsampled to a fixed
number of read pairs so the tutorial runs on an ordinary server, and ONT reads
are kept whole because module 01b applies Filtlong target-base filtering.
Reference genomes are the accession-verified RefSeq complete genomes listed in
panel.tsv; both genomic FASTA and GenBank (.gbff -> .gbk) are fetched from NCBI.

The script is resumable: existing final files are skipped and a partial cache
is reused. It needs network access plus seqkit (easywgs conda env) for the
Illumina downsampling step.

Usage:
  python download_panel.py [tier] [--reads] [--refs] [--pairs N]
"""
import csv, gzip, os, shutil, subprocess, sys, time, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PANEL = os.path.join(HERE, "..", "panel.tsv")
RAW = os.path.join(ROOT, "00_rawdata")
REF = os.path.join(ROOT, "ref")
CACHE = os.path.join(HERE, "..", ".cache")
ENA = "https://www.ebi.ac.uk/ena/portal/api/filereport"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UA = {"User-Agent": "Mozilla/5.0 EasyWGS-panel"}
PAIRS = int(os.environ.get("EXAMPLE_PAIRS", "800000"))

def http_get(url, binary=False, tries=3):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            return data if binary else data.decode("utf-8", "replace")
        except Exception as e:  # transient network errors: retry with backoff
            last = e; time.sleep(3 * (k + 1))
    raise RuntimeError(f"download failed: {url}\n{last}")

def download(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return
    tmp = dest + ".part"
    data = http_get(url, binary=True)
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, dest)

def read_panel(tier):
    rows = []
    with open(PANEL, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            rows.append(line.split("\t"))
    header, data = rows[0], rows[1:]
    out = [dict(zip(header, r)) for r in data]
    return [r for r in out if int(r["tier"]) <= tier]

def ena_fastqs(run):
    q = urllib.parse.urlencode({
        "accession": run, "result": "read_run",
        "fields": "fastq_ftp,fastq_bytes", "format": "tsv", "download": "false"})
    txt = http_get(ENA + "?" + q)
    lines = [l for l in txt.splitlines() if l and not l.startswith("run_accession")]
    if not lines:
        return []
    cols = lines[0].split("\t")
    ftps = cols[1].split(";") if len(cols) > 1 else []
    return ["https://" + p.replace("ftp.sra.ebi.ac.uk", "ftp.sra.ebi.ac.uk")
            if p.startswith("ftp.") else p for p in ftps if p]

def have(*paths):
    return all(os.path.exists(p) and os.path.getsize(p) > 0 for p in paths)

def downsample_pair(c1, c2, o1, o2, n):
    """Subsample n matched pairs. Prefer seqkit sample2 (paired-aware); fall
    back to two same-seed sample calls for older seqkit releases."""
    if have(o1, o2):
        return
    help_txt = subprocess.run(["seqkit", "sample2", "-h"], capture_output=True,
                              text=True).stdout + subprocess.run(
        ["seqkit", "sample2", "-h"], capture_output=True, text=True).stderr
    if "sample2" in help_txt:
        cmd = ["seqkit", "sample2", "-n", str(n), "-s", "11",
               "-1", c1, "-2", c2, "-O", o1, "-o", o2]
    else:
        subprocess.run(f"seqkit sample -n {n} -s 11 {c1} -o {o1}",
                       shell=True, check=True)
        subprocess.run(f"seqkit sample -n {n} -s 11 {c2} -o {o2}",
                       shell=True, check=True)
        return
    subprocess.run(cmd, check=True)

def fetch_reads(panel):
    os.makedirs(RAW, exist_ok=True); os.makedirs(CACHE, exist_ok=True)
    for r in panel:
        sid = r["id"]
        if r["illumina_run"]:
            o1 = os.path.join(RAW, f"{sid}_R1.fastq.gz")
            o2 = os.path.join(RAW, f"{sid}_R2.fastq.gz")
            if not have(o1, o2):
                urls = ena_fastqs(r["illumina_run"])
                u1 = [u for u in urls if u.endswith("_1.fastq.gz")]
                u2 = [u for u in urls if u.endswith("_2.fastq.gz")]
                if not u1 or not u2:
                    print(f"  [warn] no paired ENA FASTQ for {r['illumina_run']}; "
                          f"use fasterq-dump (see README)"); continue
                c1 = os.path.join(CACHE, f"{r['illumina_run']}_1.fastq.gz")
                c2 = os.path.join(CACHE, f"{r['illumina_run']}_2.fastq.gz")
                print(f"[reads] {sid} Illumina {r['illumina_run']}")
                download(u1[0], c1); download(u2[0], c2)
                downsample_pair(c1, c2, o1, o2, PAIRS)
                for c in (c1, c2):
                    os.remove(c) if os.environ.get("KEEP_CACHE") != "1" else None
        if r["ont_run"]:
            oL = os.path.join(RAW, f"{sid}_ONT.fastq.gz")
            if not have(oL):
                urls = ena_fastqs(r["ont_run"])
                urls = [u for u in urls if u.endswith(".fastq.gz")]
                print(f"[reads] {sid} ONT {r['ont_run']} ({len(urls)} file)")
                parts = []
                for i, u in enumerate(urls):
                    cp = os.path.join(CACHE, f"{r['ont_run']}_{i}.fastq.gz")
                    download(u, cp); parts.append(cp)
                with open(oL, "wb") as out:
                    for cp in parts:
                        with open(cp, "rb") as fh:
                            shutil.copyfileobj(fh, out)
                if os.environ.get("KEEP_CACHE") != "1":
                    for cp in parts: os.remove(cp)

def esummary(acc):
    import json
    s = http_get(EUTILS + "/esearch.fcgi?db=assembly&retmode=json&term="
                 + urllib.parse.quote(f"{acc}[AssemblyAccession]"))
    ids = json.loads(s)["esearchresult"]["idlist"]
    if not ids:
        raise RuntimeError(f"assembly not found: {acc}")
    s = http_get(EUTILS + f"/esummary.fcgi?db=assembly&retmode=json&id={ids[0]}")
    return json.loads(s)["result"][ids[0]]

def gunzip(gz, out):
    if have(out): return
    with gzip.open(gz, "rb") as fi, open(out, "wb") as fo:
        shutil.copyfileobj(fi, fo)

def fetch_refs(panel):
    os.makedirs(REF, exist_ok=True)
    seen = {}
    for r in panel:
        seen[r["ref_label"]] = r["reference_gcf"]
    for label, gcf in seen.items():
        fna = os.path.join(REF, label.replace(".gbk", ".fna"))
        gbk = os.path.join(REF, label)
        if have(fna, gbk):
            print(f"[ref] {label} exists"); continue
        print(f"[ref] {label} <- {gcf}")
        d = esummary(gcf)
        ftp = d.get("ftppath_refseq") or d.get("ftppath_genbank")
        base = ftp.replace("ftp://", "https://")
        stem = os.path.basename(base)
        cg = os.path.join(CACHE, stem + "_genomic.fna.gz")
        bg = os.path.join(CACHE, stem + "_genomic.gbff.gz")
        download(base + "/" + stem + "_genomic.fna.gz", cg)
        download(base + "/" + stem + "_genomic.gbff.gz", bg)
        gunzip(cg, fna); gunzip(bg, gbk)
        for c in (cg, bg):
            os.remove(c) if os.environ.get("KEEP_CACHE") != "1" else None

def main():
    args = sys.argv[1:]
    tier = 1
    if args and args[0].isdigit():
        tier = int(args.pop(0))
    do_reads = "--refs" not in args
    do_refs = "--reads" not in args
    panel = read_panel(tier)
    print(f"EasyWGS panel tier {tier}: {len(panel)} samples; "
          f"Illumina downsampling to {PAIRS} pairs")
    if do_refs: fetch_refs(panel)
    if do_reads: fetch_reads(panel)
    print("Done. Reads in 00_rawdata/, references in ref/.")

if __name__ == "__main__":
    main()
