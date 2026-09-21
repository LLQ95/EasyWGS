#!/usr/bin/env python3
"""Generate a tiny, deterministic synthetic dataset for the EasyWGS smoke test.

The smoke test must run anywhere with no download and no large database, so the
input data are simulated rather than fetched. A fixed random seed makes every
run byte-for-byte reproducible. Two isolates are emitted against one reference:

  toy  identical to the reference (the clean control, should call no variants)
  mut  carries a fixed set of scattered single-nucleotide changes (should be
       recovered by the reference-mapping and variant-calling route)

Usage:
    python tests/make_toy_data.py OUTDIR

It creates, under OUTDIR (which can be a temporary directory used as PROJECT):
    ref/toy.fasta
    00_rawdata/{toy,mut}_R{1,2}.fastq.gz
    config/my_samples.csv  (R1/R2 point at the module-01 fastp outputs)

Only the Python standard library is used.
"""
import gzip
import os
import random
import sys

SEED = 20260921
GENOME_LEN = 120000
GC = 0.50
READ_LEN = 150
INSERT_MEAN = 350
INSERT_SD = 60
ERROR_RATE = 0.002
N_PAIRS = 14000          # ~35x for a 120 kb genome at 2 x 150 bp
N_MUT = 48               # fixed SNPs introduced into the mut isolate
MIN_SNP_GAP = 800

COMP = {"A": "T", "T": "A", "C": "G", "G": "C", "N": "N"}


def revcomp(seq):
    return "".join(COMP[b] for b in reversed(seq))


def random_genome(length, gc, rng):
    """Return an unambiguous haploid sequence with the requested GC fraction."""
    bases = []
    p_gc = gc / 2.0
    p_at = (1.0 - gc) / 2.0
    weights = [p_at, p_at, p_gc, p_gc]  # A, T, C, G
    cum = []
    acc = 0.0
    for w in weights:
        acc += w
        cum.append(acc)
    alphabet = "ATCG"
    for _ in range(length):
        r = rng.random()
        for i, c in enumerate(cum):
            if r <= c:
                bases.append(alphabet[i])
                break
        else:
            bases.append("G")
    return "".join(bases)


def introduce_snps(genome, n_snps, gap, rng):
    """Spread n_snps substitutions roughly evenly, never closer than gap bases."""
    seq = list(genome)
    length = len(seq)
    positions = []
    candidate = list(range(2000, length - 2000, gap))
    rng.shuffle(candidate)
    for pos in candidate:
        if len(positions) >= n_snps:
            break
        if all(abs(pos - p) >= gap for p in positions):
            alt = rng.choice([b for b in "ATCG" if b != seq[pos]])
            seq[pos] = alt
            positions.append(pos)
    positions.sort()
    if len(positions) < n_snps:
        raise RuntimeError("could not place the requested number of SNPs")
    return "".join(seq), positions


def add_errors(seq, rate, rng):
    out = []
    for b in seq:
        if rng.random() < rate:
            out.append(rng.choice([x for x in "ATCG" if x != b]))
        else:
            out.append(b)
    return "".join(out)


def write_fasta(path, name, seq, width=70):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f">{name}\n")
        for i in range(0, len(seq), width):
            fh.write(seq[i:i + width] + "\n")


def simulate_pairs(genome, n_pairs, prefix, out1, out2, rng):
    """Simulate paired-end reads from random fragment positions."""
    length = len(genome)
    with gzip.open(out1, "wt", newline="\n") as f1, \
         gzip.open(out2, "wt", newline="\n") as f2:
        for i in range(n_pairs):
            insert = max(2 * READ_LEN + 20,
                         int(rng.gauss(INSERT_MEAN, INSERT_SD)))
            insert = min(insert, length)
            start = rng.randint(0, length - insert)
            frag = genome[start:start + insert]
            r1 = add_errors(frag[:READ_LEN], ERROR_RATE, rng)
            r2 = add_errors(revcomp(frag[-READ_LEN:]), ERROR_RATE, rng)
            q = "F" * READ_LEN     # Phred Q37, constant quality
            f1.write(f"@{prefix}:{i+1}/1\n{r1}\n+\n{q}\n")
            f2.write(f"@{prefix}:{i+1}/2\n{r2}\n+\n{q}\n")


def write_samplesheet(path):
    rows = [
        "id,platform,species,R1,R2,longreads,reference,date,country,phenotype",
        "toy,illumina,toy,01_qc/clean/toy_R1.fq.gz,01_qc/clean/toy_R2.fq.gz,,ref/toy.fasta,2024,Toyland,0",
        "mut,illumina,toy,01_qc/clean/mut_R1.fq.gz,01_qc/clean/mut_R2.fq.gz,,ref/toy.fasta,2024,Toyland,1",
    ]
    with open(path, "w", newline="\n", encoding="utf-8") as fh:
        fh.write("\n".join(rows) + "\n")


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python tests/make_toy_data.py OUTDIR")
    outdir = os.path.abspath(sys.argv[1])
    raw = os.path.join(outdir, "00_rawdata")
    ref = os.path.join(outdir, "ref")
    cfg = os.path.join(outdir, "config")
    for d in (raw, ref, cfg):
        os.makedirs(d, exist_ok=True)

    rng = random.Random(SEED)
    reference = random_genome(GENOME_LEN, GC, rng)
    mutant, snp_positions = introduce_snps(reference, N_MUT, MIN_SNP_GAP, rng)
    write_fasta(os.path.join(ref, "toy.fasta"), "toy_ref", reference)

    rng_toy = random.Random(SEED + 1)
    simulate_pairs(reference, N_PAIRS, "toy",
                   os.path.join(raw, "toy_R1.fastq.gz"),
                   os.path.join(raw, "toy_R2.fastq.gz"), rng_toy)
    rng_mut = random.Random(SEED + 2)
    simulate_pairs(mutant, N_PAIRS, "mut",
                   os.path.join(raw, "mut_R1.fastq.gz"),
                   os.path.join(raw, "mut_R2.fastq.gz"), rng_mut)
    write_samplesheet(os.path.join(cfg, "my_samples.csv"))

    print(f"[toy] reference length   : {GENOME_LEN} bp")
    print(f"[toy] SNPs in mut isolate: {len(snp_positions)} at {snp_positions[:5]} ...")
    print(f"[toy] pairs per isolate  : {N_PAIRS} (~{2 * READ_LEN * N_PAIRS / GENOME_LEN:.0f}x)")
    print(f"[toy] wrote {outdir}")


if __name__ == "__main__":
    main()
