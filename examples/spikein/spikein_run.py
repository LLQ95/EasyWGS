#!/usr/bin/env python3
"""Controlled two-layer decontamination spike-in for EasyWGS.

This answers the question the project starts from: after read-level cleaning,
how much contaminant is removed and how much of the target genome is retained,
and does cleaning rescue the assembly and genome-quality scores?

Two contaminant classes are spiked into one target isolate (E. coli EC_BE_2015):
  phix      technical control, reads simulated with art_illumina from NC_001422
  klebsiella a real, phylogenetically distant isolate (K. pneumoniae KP_GR_2011)
Each is added at 1, 5 and 10 percent of target read pairs. For every mixture we
report the read-level fraction mapping to target and contaminant before
(spiked) and after (cleaned) a transparent map-and-filter removal step, plus
assembly size/N50 and CheckM2/GUNC scores for baseline, spiked-10% and cleaned-10%.

The transparent bwa/samtools removal is the auditable benchmark; in production
module 02 applies CLEAN (and FCS-GX at the assembly level), which implement the
same reference/k-mer principle with maintained databases. Tools or databases
that are absent are recorded as NA rather than stopping the experiment.
"""
import gzip, os, shutil, subprocess, sys, urllib.request, csv

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
SP = os.path.join(ROOT, "examples", "spikein")
WORK = os.path.join(SP, "work"); RES = os.path.join(SP, "results"); REFS = os.path.join(SP, "refs")
TARGET_ID = "EC_BE_2015"; NEIGHBOUR_ID = "KP_GR_2011"
LEVELS = [0.01, 0.05, 0.10]
THREADS = os.environ.get("THREADS", "16"); MEM = os.environ.get("MEM", "64")
DBROOT = os.path.expanduser(os.environ.get("DBROOT", "~/easywgs_db"))
ROWS = []

def log(m): print("[spikein]", m, flush=True)
def have(cmd): return shutil.which(cmd) is not None

def run(cmd, check=False, env=None):
    p = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True,
                       text=True, env=env)
    if check and p.returncode != 0:
        sys.stderr.write(p.stdout + p.stderr); raise SystemExit(f"failed: {cmd}")
    return p

def opener(p):
    return gzip.open(p, "rt") if p.endswith(".gz") else open(p, "rt")

def count_pairs(p):
    n = 0
    with opener(p) as f:
        for _ in f: n += 1
    return n // 4

def take_pairs(in1, in2, n, out1, out2):
    """Copy the first n read pairs from in1/in2 to gzipped out1/out2."""
    with opener(in1) as a, opener(in2) as b, \
         gzip.open(out1, "wt") as oa, gzip.open(out2, "wt") as ob:
        for _ in range(n):
            r1 = [a.readline() for _ in range(4)]
            r2 = [b.readline() for _ in range(4)]
            if len(r1[0]) == 0: break
            oa.write("".join(r1)); ob.write("".join(r2))

def mix(add1, add2, n_add, out1, out2):
    """All target pairs (cached as _t1/_t2) plus n_add contaminant pairs."""
    t1c, t2c = os.path.join(WORK, "_t1.fq.gz"), os.path.join(WORK, "_t2.fq.gz")
    if n_add > 0 and add1:
        take_pairs(add1, add2, n_add, os.path.join(WORK, "_c1.fq.gz"),
                   os.path.join(WORK, "_c2.fq.gz"))
        with gzip.open(out1, "wt") as o:
            for p in (t1c, WORK + "/_c1.fq.gz"):
                with gzip.open(p, "rt") as f: shutil.copyfileobj(f, o)
        with gzip.open(out2, "wt") as o:
            for p in (t2c, WORK + "/_c2.fq.gz"):
                with gzip.open(p, "rt") as f: shutil.copyfileobj(f, o)
    else:
        shutil.copy(t1c, out1); shutil.copy(t2c, out2)

def bwa_index(ref):
    if not os.path.exists(ref + ".bwt"):
        run(f'bwa index "{ref}"')

def mapped_pairs(reads1, reads2, ref):
    """Count read pairs with at least one read mapping to ref (bwa mem)."""
    if not (have("bwa") and have("samtools")): return None
    bwa_index(ref)
    cmd = (f'bwa mem -t {THREADS} "{ref}" "{reads1}" "{reads2}" | '
           f'samtools view -h -F 2308 - | samtools view -c -F 4 -')
    p = run(cmd)
    try: return int(p.stdout.strip()) // 2
    except ValueError: return None

def mapfilter_remove(reads1, reads2, contam_ref, out1, out2):
    """Keep read pairs where neither read maps to the contaminant reference."""
    bwa_index(contam_ref)
    cmd = (f'bwa mem -t {THREADS} "{contam_ref}" "{reads1}" "{reads2}" | '
           f'samtools collate -u -O - | samtools fastq -f 12 -0 /dev/null '
           f'-1 "{out1}" -2 "{out2}" -s /dev/null -')
    return run(cmd).returncode == 0

def n50_len(path):
    L, lens = 0, []
    cur = 0
    with opener(path) as f:
        for line in f:
            if line.startswith(">"):
                if cur: lens.append(cur); L += cur
                cur = 0
            else: cur += len(line.strip())
    if cur: lens.append(cur); L += cur
    lens.sort(reverse=True)
    tot = sum(lens); c = 0; n50 = 0
    for x in lens:
        c += x
        if c >= tot / 2: n50 = x; break
    return L, n50, len(lens)

def assemble(r1, r2, tag):
    outdir = os.path.join(WORK, "asm_" + tag)
    fa = os.path.join(outdir, "scaffolds.fasta")
    if not os.path.exists(fa):
        if not have("spades.py"):
            return None
        run(f'spades.py --isolate -1 "{r1}" -2 "{r2}" -o "{outdir}" '
            f'-t {THREADS} -m {MEM}')
    if not os.path.exists(fa):
        # SPAdes may emit contigs.fasta even when scaffolding is skipped
        alt = os.path.join(outdir, "contigs.fasta")
        if os.path.exists(alt): shutil.copy(alt, fa)
    return fa if os.path.exists(fa) else None

def resolve_checkm2_db():
    # CHECKM2_DB may be the uniref100.KO.1.dmnd file or its CheckM2_database directory
    p = os.environ.get("CHECKM2_DB", "").strip()
    cands = []
    if p:
        cands.append(p if os.path.basename(p) == "uniref100.KO.1.dmnd"
                     else os.path.join(p, "uniref100.KO.1.dmnd"))
    cands += [
        os.path.join(DBROOT, "checkm2_db", "CheckM2_database", "uniref100.KO.1.dmnd"),
        os.path.join(DBROOT, "checkm2_db", "uniref100.KO.1.dmnd"),
    ]
    for c in cands:
        if os.path.isfile(c):
            return c
    return ""

def checkm2(fa, tag):
    db = resolve_checkm2_db()
    outd = os.path.join(WORK, "checkm2_" + tag)
    rep = os.path.join(outd, "quality_report.tsv")
    if not os.path.exists(rep) and have("conda"):
        dbarg = f' --database_path "{db}"' if db else ""
        run(f'conda run -n checkm2 checkm2 predict --input "{fa}" -o "{outd}" '
            f'-t {THREADS}{dbarg}')
    if os.path.exists(rep):
        for r in csv.DictReader(open(rep), delimiter="\t"):
            return r.get("Completeness", "NA"), r.get("Contamination", "NA")
    return "NA", "NA"

def rec(contam, level, condition, metric, value):
    ROWS.append(dict(contaminant=contam, spike_pct=level, condition=condition,
                     metric=metric, value=value))

def read_conditions(contam, cref, add1, add2, t_pairs):
    for lv in LEVELS:
        tag = f"{contam}_{int(lv*100)}"
        s1 = os.path.join(WORK, f"{tag}_spiked_R1.fq.gz")
        s2 = s1.replace("R1", "R2")
        n_add = round(t_pairs * lv / (1 - lv))
        mix(add1, add2, n_add, s1, s2)
        for cond, (a, b) in (("spiked", (s1, s2)),):
            mt = mapped_pairs(a, b, TARGET_REF); mc = mapped_pairs(a, b, cref)
            rec(contam, lv, "spiked", "target_pairs", mt if mt is not None else "NA")
            rec(contam, lv, "spiked", "contaminant_pairs", mc if mc is not None else "NA")
        c1 = os.path.join(WORK, f"{tag}_clean_RR1.fq.gz")
        c2 = c1.replace("RR1", "RR2")
        ok = mapfilter_remove(s1, s2, cref, c1, c2) if have("bwa") else False
        if ok:
            mt = mapped_pairs(c1, c2, TARGET_REF); mc = mapped_pairs(c1, c2, cref)
            rec(contam, lv, "cleaned", "target_pairs", mt if mt is not None else "NA")
            rec(contam, lv, "cleaned", "contaminant_pairs", mc if mc is not None else "NA")

def assembly_block(contam, cref, add1, add2, t_pairs):
    lv = 0.10; tag = f"{contam}_10"
    sets = {"baseline": (T1, T2)}
    n_add = round(t_pairs * lv / (1 - lv))
    s1, s2 = os.path.join(WORK, f"{tag}_spiked_R1.fq.gz"), os.path.join(WORK, f"{tag}_spiked_R2.fq.gz")
    if not os.path.exists(s1): mix(add1, add2, n_add, s1, s2)
    sets["spiked"] = (s1, s2)
    c1, c2 = os.path.join(WORK, f"{tag}_clean_RR1.fq.gz"), os.path.join(WORK, f"{tag}_clean_RR2.fq.gz")
    if os.path.exists(c1): sets["cleaned"] = (c1, c2)
    for cond, (a, b) in sets.items():
        fa = assemble(a, b, f"{tag}_{cond}")
        if not fa:
            rec(contam, lv, cond, "assembly", "NA"); continue
        L, n50, nctg = n50_len(fa)
        rec(contam, lv, cond, "assembly_length_bp", L)
        rec(contam, lv, cond, "assembly_N50", n50)
        rec(contam, lv, cond, "assembly_contigs", nctg)
        comp, contam_q = checkm2(fa, f"{tag}_{cond}")
        rec(contam, lv, cond, "checkm2_completeness", comp)
        rec(contam, lv, cond, "checkm2_contamination", contam_q)

def phix_reads(n):
    ref = os.path.join(REFS, "phix.fna")
    if not os.path.exists(ref):
        os.makedirs(REFS, exist_ok=True)
        url = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
               "db=nuccore&id=NC_001422&rettype=fasta&retmode=text")
        urllib.request.urlretrieve(url, ref)
    if not have("art_illumina"):
        log("art_illumina not found; install 'art' (bioconda) to simulate PhiX")
        return None, None
    base = os.path.join(WORK, "phix")
    if not os.path.exists(base + "1.fq.gz"):
        run(f'art_illumina -ss HS25 -i "{ref}" -p -l 150 -f {n + 1000} '
            f'-m 350 -s 40 -o "{base}"')
        for i in (1, 2):
            if os.path.exists(f"{base}{i}.fq"):
                with open(f"{base}{i}.fq", "rb") as fi, gzip.open(f"{base}{i}.fq.gz", "wb") as fo:
                    shutil.copyfileobj(fi, fo)
    return base + "1.fq.gz", base + "2.fq.gz"

def main():
    for d in (WORK, RES, REFS): os.makedirs(d, exist_ok=True)
    global T1, T2, TARGET_REF
    T1 = os.path.join(ROOT, "01_qc", "clean", f"{TARGET_ID}_R1.fq.gz")
    T2 = os.path.join(ROOT, "01_qc", "clean", f"{TARGET_ID}_R2.fq.gz")
    TARGET_REF = os.path.join(ROOT, "ref", "Ec_ref.fna")
    if not os.path.exists(T1):
        sys.exit("Target cleaned reads not found; run modules 00-01 for tier 1 first.")
    t_pairs = count_pairs(T1)
    shutil.copy(T1, os.path.join(WORK, "_t1.fq.gz"))
    shutil.copy(T2, os.path.join(WORK, "_t2.fq.gz"))
    rec("none", 0.0, "baseline", "target_pairs", t_pairs)
    log(f"target {TARGET_ID}: {t_pairs} pairs")

    # Baseline assembly and quality
    fa = assemble(T1, T2, "baseline")
    if fa:
        L, n50, nctg = n50_len(fa)
        rec("none", 0.0, "baseline", "assembly_length_bp", L)
        rec("none", 0.0, "baseline", "assembly_N50", n50)
        rec("none", 0.0, "baseline", "assembly_contigs", nctg)
        comp, ct = checkm2(fa, "baseline")
        rec("none", 0.0, "baseline", "checkm2_completeness", comp)
        rec("none", 0.0, "baseline", "checkm2_contamination", ct)

    # Layer 1: PhiX technical control
    p1, p2 = phix_reads(round(t_pairs * 0.12))
    if p1:
        read_conditions("phix", os.path.join(REFS, "phix.fna"), p1, p2, t_pairs)
        assembly_block("phix", os.path.join(REFS, "phix.fna"), p1, p2, t_pairs)

    # Layer 2: real distant isolate (Klebsiella) as near-source contamination
    k1 = os.path.join(ROOT, "01_qc", "clean", f"{NEIGHBOUR_ID}_R1.fq.gz")
    k2 = os.path.join(ROOT, "01_qc", "clean", f"{NEIGHBOUR_ID}_R2.fq.gz")
    kref = os.path.join(ROOT, "ref", "Kp_ref.fna")
    if os.path.exists(k1):
        read_conditions("klebsiella", kref, k1, k2, t_pairs)
        assembly_block("klebsiella", kref, k1, k2, t_pairs)
    else:
        log(f"neighbour {NEIGHBOUR_ID} cleaned reads missing; skipping klebsiella layer")

    out = os.path.join(RES, "spikein_metrics.tsv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["contaminant", "spike_pct", "condition",
                                          "metric", "value"], delimiter="\t")
        w.writeheader(); w.writerows(ROWS)
    log("wrote " + os.path.relpath(out, ROOT))

if __name__ == "__main__":
    main()
