#!/usr/bin/env python3
"""Self-contained synthetic fixture for the decontamination spike-in.

The real spike-in (spikein_run.py without --synthetic) needs the downloaded
tier-1 reads, SPAdes and the CheckM2/GUNC databases. This fixture removes those
dependencies so the read-layer decontamination logic can be validated anywhere,
including continuous integration and a laptop, in a few seconds.

Three independent, seeded genomes are generated (no shared long k-mers by
construction): one target and two contaminants that play the role of the PhiX
technical control ("phix") and a phylogenetically distant bacterium
("klebsiella"). They are synthetic stand-ins, not the real PhiX or K. pneumoniae
genomes. Contaminant read pairs are spiked at 1, 5 and 10 percent, and a
transparent map-and-filter removal is evaluated before and after cleaning.

Two interchangeable backends compute the same metrics:
  * bwa + samtools when available (the same engine used by the production route)
  * a dependency-free k-mer classifier otherwise (k=21 membership fraction), so
    the example still runs where bwa is absent

Only the read layer is exercised here; assembly and CheckM2/GUNC panels are
produced by the real, cluster-run spike-in and are left as NA by design.
"""
import gzip
import os
import random
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
WORK = os.path.join(HERE, "work", "synthetic")
RES = os.path.join(HERE, "results")

SEED = 20260921
READ_LEN = 150
INSERT_MEAN = 350
INSERT_SD = 60
ERROR_RATE = 0.002
TARGET_PAIRS = 12000
CONTAM_PAIRS = 2500
LEVELS = [0.01, 0.05, 0.10]
K = 21
KMER_STEP = 3
MAP_FRAC = 0.5

# role, length, GC, random seed offset
GENOMES = [
    ("target", 120000, 0.51, 0),
    ("phix", 12000, 0.44, 100),
    ("klebsiella", 100000, 0.58, 200),
]

COMP = {"A": "T", "T": "A", "C": "G", "G": "C", "N": "N"}


def revcomp(seq):
    return "".join(COMP[b] for b in reversed(seq))


def random_genome(length, gc, seed):
    rng = random.Random(SEED + seed)
    p_gc, p_at = gc / 2.0, (1.0 - gc) / 2.0
    cum, alphabet, acc = [], "ATCG", 0.0
    for w in (p_at, p_at, p_gc, p_gc):
        acc += w
        cum.append(acc)
    out = []
    for _ in range(length):
        r = rng.random()
        chosen = "G"
        for i, c in enumerate(cum):
            if r <= c:
                chosen = alphabet[i]
                break
        out.append(chosen)
    return "".join(out)


def add_errors(seq, rng):
    return "".join(rng.choice([x for x in "ATCG" if x != b]) if rng.random() < ERROR_RATE else b
                  for b in seq)


def simulate_blocks(genome, n_pairs, seed_int, tag):
    """Return two parallel lists of 4-line FASTQ blocks (R1, R2)."""
    rng = random.Random(SEED + seed_int)
    length = len(genome)
    r1_blocks, r2_blocks = [], []
    qual = "F" * READ_LEN
    for i in range(n_pairs):
        insert = min(length, max(2 * READ_LEN + 20,
                                 int(rng.gauss(INSERT_MEAN, INSERT_SD))))
        start = rng.randint(0, length - insert)
        frag = genome[start:start + insert]
        s1 = add_errors(frag[:READ_LEN], rng)
        s2 = add_errors(revcomp(frag[-READ_LEN:]), rng)
        r1_blocks.append(f"@{tag}:{i+1}/1\n{s1}\n+\n{qual}\n")
        r2_blocks.append(f"@{tag}:{i+1}/2\n{s2}\n+\n{qual}\n")
    return r1_blocks, r2_blocks


def write_fasta(path, name, seq, width=70):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f">{name}\n")
        for i in range(0, len(seq), width):
            fh.write(seq[i:i + width] + "\n")


def write_pairs(path1, path2, b1, b2):
    with gzip.open(path1, "wt", newline="\n") as f1, \
         gzip.open(path2, "wt", newline="\n") as f2:
        f1.write("".join(b1))
        f2.write("".join(b2))


def kmer_set(seq):
    rc = revcomp(seq)
    ks = set()
    for i in range(0, len(seq) - K + 1):
        ks.add(seq[i:i + K])
        ks.add(rc[i:i + K])
    return ks


def read_maps(seq, ks):
    """A read maps when at least half of its sampled k-mers hit the reference."""
    if len(seq) < K:
        return False
    hits, total = 0, 0
    for i in range(0, len(seq) - K + 1, KMER_STEP):
        total += 1
        if seq[i:i + K] in ks:
            hits += 1
    return total > 0 and hits / total >= MAP_FRAC


def block_seq(block, line_index=1):
    return block.split("\n")[line_index]


def run(cmd):
    return subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True)


def have_bwa():
    return shutil.which("bwa") is not None and shutil.which("samtools") is not None


def bwa_index(ref):
    if not os.path.exists(ref + ".bwt"):
        run(f'bwa index "{ref}"')


def bwa_mapped_pairs(r1, r2, ref, threads):
    bwa_index(ref)
    cmd = (f'bwa mem -t {threads} "{ref}" "{r1}" "{r2}" | '
           f'samtools view -h -F 2308 - | samtools view -c -F 4 -')
    p = run(cmd)
    try:
        return int(p.stdout.strip()) // 2
    except ValueError:
        return None


def bwa_filter(r1, r2, contam_ref, c1, c2, threads):
    """Keep pairs in which neither read maps to the contaminant."""
    bwa_index(contam_ref)
    cmd = (f'bwa mem -t {threads} "{contam_ref}" "{r1}" "{r2}" | '
           f'samtools collate -u -O - | samtools fastq -f 12 -0 /dev/null '
           f'-1 "{c1}" -2 "{c2}" -s /dev/null -')
    return run(cmd).returncode == 0


def kmer_counts(b1, b2, ks_target, ks_contam):
    """Return (pairs mapping to target, pairs mapping to contaminant)."""
    t_reads = c_reads = 0
    for blocks in (b1, b2):
        for blk in blocks:
            seq = block_seq(blk)
            if read_maps(seq, ks_target):
                t_reads += 1
            if read_maps(seq, ks_contam):
                c_reads += 1
    return t_reads // 2, c_reads // 2


def kmer_filter(b1, b2, ks_contam):
    o1, o2 = [], []
    for x, y in zip(b1, b2):
        if not read_maps(block_seq(x), ks_contam) and not read_maps(block_seq(y), ks_contam):
            o1.append(x)
            o2.append(y)
    return o1, o2


def run_synthetic(threads=2):
    """Return metric rows in the same schema as spikein_run.py."""
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(RES, exist_ok=True)
    seqs = {name: random_genome(length, gc, off)
            for name, length, gc, off in GENOMES}
    refs = {}
    for name in seqs:
        p = os.path.join(WORK, f"{name}.fasta")
        write_fasta(p, name, seqs[name])
        refs[name] = p

    t1, t2 = simulate_blocks(seqs["target"], TARGET_PAIRS, 300, "target")
    contam_reads = {}
    for role, seed_off in (("phix", 400), ("klebsiella", 500)):
        contam_reads[role] = simulate_blocks(seqs[role], CONTAM_PAIRS, seed_off, role)

    use_bwa = have_bwa()
    backend = "bwa" if use_bwa else "kmer"
    with open(os.path.join(RES, "spikein_backend.txt"), "w", encoding="utf-8") as fh:
        fh.write(backend + "\n")

    ks = {name: (None if use_bwa else kmer_set(seqs[name]))
          for name in seqs}
    rows = []

    def rec(contaminant, level, condition, metric, value):
        rows.append(dict(contaminant=contaminant, spike_pct=level,
                         condition=condition, metric=metric, value=value))

    rec("none", 0.0, "baseline", "target_pairs", TARGET_PAIRS)

    for role in ("phix", "klebsiella"):
        c1_blocks, c2_blocks = contam_reads[role]
        for lv in LEVELS:
            n_add = round(TARGET_PAIRS * lv / (1 - lv))
            n_add = min(n_add, CONTAM_PAIRS)
            tag = f"{role}_{int(lv * 100)}"
            s1 = t1 + c1_blocks[:n_add]
            s2 = t2 + c2_blocks[:n_add]

            if use_bwa:
                sp1, sp2 = os.path.join(WORK, f"{tag}_spiked_R1.fq.gz"), \
                           os.path.join(WORK, f"{tag}_spiked_R2.fq.gz")
                write_pairs(sp1, sp2, s1, s2)
                mt = bwa_mapped_pairs(sp1, sp2, refs["target"], threads)
                mc = bwa_mapped_pairs(sp1, sp2, refs[role], threads)
                rec(role, lv, "spiked", "target_pairs", mt if mt is not None else "NA")
                rec(role, lv, "spiked", "contaminant_pairs", mc if mc is not None else "NA")
                cp1, cp2 = os.path.join(WORK, f"{tag}_clean_RR1.fq.gz"), \
                           os.path.join(WORK, f"{tag}_clean_RR2.fq.gz")
                if bwa_filter(sp1, sp2, refs[role], cp1, cp2, threads):
                    tc = bwa_mapped_pairs(cp1, cp2, refs["target"], threads)
                    cc = bwa_mapped_pairs(cp1, cp2, refs[role], threads)
                    rec(role, lv, "cleaned", "target_pairs", tc if tc is not None else "NA")
                    rec(role, lv, "cleaned", "contaminant_pairs", cc if cc is not None else "NA")
            else:
                mt, mc = kmer_counts(s1, s2, ks["target"], ks[role])
                rec(role, lv, "spiked", "target_pairs", mt)
                rec(role, lv, "spiked", "contaminant_pairs", mc)
                o1, o2 = kmer_filter(s1, s2, ks[role])
                tc, cc = kmer_counts(o1, o2, ks["target"], ks[role])
                rec(role, lv, "cleaned", "target_pairs", tc)
                rec(role, lv, "cleaned", "contaminant_pairs", cc)

    print(f"[synthetic spike-in] backend={backend}; "
          f"target_pairs={TARGET_PAIRS}; levels={LEVELS}")
    return rows


if __name__ == "__main__":
    import csv
    out_rows = run_synthetic()
    out = os.path.join(RES, "spikein_metrics.tsv")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["contaminant", "spike_pct",
                                          "condition", "metric", "value"],
                           delimiter="\t")
        w.writeheader()
        w.writerows(out_rows)
    print("wrote", os.path.relpath(out, ROOT))
