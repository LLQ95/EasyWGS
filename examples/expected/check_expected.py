#!/usr/bin/env python3
"""Check EasyWGS runs against their expected-result rules.

Two independent rule sets are supported:
  panel    examples/results/panel_metrics.tsv  vs expected_results.tsv
  spikein  examples/spikein/results/spikein_metrics.tsv vs expected_spikein.tsv

Choose with --mode panel|spikein|all (default all, for backward compatibility).
Each run prints and writes an expected_check.tsv with PASS / WARN / FAIL per
rule. A metric that is absent because the module has not run is WARN, not FAIL;
the script exits non-zero only when a real, measured value violates a rule.
"""
import argparse
import csv
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PANEL_RES = os.path.join(ROOT, "examples", "results")
SPIKE_RES = os.path.join(ROOT, "examples", "spikein", "results")


def read_tsv(p):
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def is_na(v):
    return v is None or str(v).strip() in ("", "NA", "nan", "None")


def num(v):
    try:
        return float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return None


def compare(op, thr, val):
    """Return PASS/FAIL for a present value."""
    if op in (">=", "<=", "=="):
        x, t = num(val), num(thr)
        if x is None or t is None:
            return "FAIL" if str(val) != str(thr) else "PASS"
        if op == ">=":
            return "PASS" if x >= t else "FAIL"
        if op == "<=":
            return "PASS" if x <= t else "FAIL"
        return "PASS" if abs(x - t) < 1e-9 else "FAIL"
    if op == "in_range":
        lo, hi = [float(x) for x in thr.split("..")]
        x = num(val)
        return "PASS" if x is not None and lo <= x <= hi else "FAIL"
    if op in ("exists", "nonempty"):
        return "PASS" if not is_na(val) else "FAIL"
    if op == "equals":
        return "PASS" if str(val).strip().lower() == thr.strip().lower() else "FAIL"
    return "FAIL"


def read_rules(p):
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        lines = [l for l in f if l.strip() and not l.startswith("#")]
    return list(csv.DictReader(io.StringIO("".join(lines)), delimiter="\t"))


def write_check(path, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["check_id", "target", "status", "detail"])
        w.writerows(rows)


def check_panel():
    per = read_tsv(os.path.join(PANEL_RES, "panel_metrics.tsv"))
    cs = {r["metric"]: r["value"] for r in
          read_tsv(os.path.join(PANEL_RES, "collection_stats.tsv"))}
    rules = read_rules(os.path.join(HERE, "expected_results.tsv"))
    out, counts = [], {"PASS": 0, "WARN": 0, "FAIL": 0}

    for rule in rules:
        cid, scope, group, metric, op, thr = (
            rule["check_id"], rule["scope"], rule["group"], rule["metric"],
            rule["operator"], rule["threshold"])
        if scope == "per_isolate":
            targets = [r for r in per if group == "all" or r.get("group") == group]
            if not targets:
                out.append((cid, "-", "WARN", "panel_metrics.tsv not found; run the panel first"))
                counts["WARN"] += 1
                continue
            for r in targets:
                val = r.get(metric, "")
                if is_na(val):
                    st, detail = "WARN", f"{metric} not produced yet"
                else:
                    st, detail = compare(op, thr, val), f"{metric}={val} {op} {thr}"
                out.append((cid, r["sample_id"], st, detail))
                counts[st] += 1
        else:
            val = cs.get(metric)
            if is_na(val):
                st, detail = "WARN", f"{metric} not produced yet"
            else:
                st, detail = compare(op, thr, val), f"{metric}={val} {op} {thr}"
            out.append((cid, "collection", st, detail))
            counts[st] += 1

    write_check(os.path.join(PANEL_RES, "expected_check.tsv"), out)
    for cid, tgt, st, detail in out:
        print(f"[{st}] {cid:4s} {tgt:16s} {detail}")
    print(f"[panel] PASS={counts['PASS']} WARN={counts['WARN']} FAIL={counts['FAIL']}")
    return counts


def _spike_value(d, contam, pct, condition, metric):
    v = d.get((contam, pct, condition, metric))
    return num(v)


def check_spikein():
    metrics_path = os.path.join(SPIKE_RES, "spikein_metrics.tsv")
    rules = read_rules(os.path.join(HERE, "expected_spikein.tsv"))
    synthetic = os.path.exists(os.path.join(SPIKE_RES, "spikein_backend.txt"))
    out, counts = [], {"PASS": 0, "WARN": 0, "FAIL": 0}

    d = {}
    for r in read_tsv(metrics_path):
        try:
            pct = float(r["spike_pct"])
        except (TypeError, ValueError):
            pct = 0.0
        d[(r["contaminant"], pct, r["condition"], r["metric"])] = r.get("value", "")

    def derived(contam, pct, metric):
        if metric == "baseline_target_pairs":
            return _spike_value(d, "none", 0.0, "baseline", "target_pairs")
        ts = _spike_value(d, contam, pct, "spiked", "target_pairs")
        cs = _spike_value(d, contam, pct, "spiked", "contaminant_pairs")
        tc = _spike_value(d, contam, pct, "cleaned", "target_pairs")
        cc = _spike_value(d, contam, pct, "cleaned", "contaminant_pairs")
        if metric == "spiked_contam_fraction":
            return None if ts is None or cs is None or (ts + cs) == 0 else cs / (ts + cs)
        if metric == "cleaned_contam_fraction":
            return None if tc is None or cc is None or (tc + cc) == 0 else cc / (tc + cc)
        if metric == "target_retention":
            return None if ts in (None, 0) or tc is None else tc / ts
        return None

    for rule in rules:
        cid, mode = rule["check_id"], rule["mode"]
        if mode == "synthetic" and not synthetic:
            continue
        contams = ["phix", "klebsiella"] if rule["contaminant"] == "all" else \
                  ([] if rule["contaminant"] == "none" else [rule["contaminant"]])
        if rule["contaminant"] == "none":
            contams = ["none"]
        if rule["spike_pct"] == "all":
            pcts = [0.01, 0.05, 0.10]
        else:
            pcts = [float(rule["spike_pct"])]
        for contam in contams:
            for pct in pcts:
                tgt = f"{contam}@{pct:g}%"
                val = derived(contam, pct, rule["metric"])
                if val is None:
                    st, detail = "WARN", f"{rule['metric']} not produced yet"
                else:
                    st = compare(rule["operator"], rule["threshold"], val)
                    detail = f"{rule['metric']}={val:.4f} {rule['operator']} {rule['threshold']}"
                out.append((cid, tgt, st, detail))
                counts[st] += 1

    if not d and rules:
        out = [(rules[0]["check_id"], "-", "WARN",
                "spikein_metrics.tsv not found; run examples/02_run_spikein.sh")]
        counts["WARN"] += 1

    write_check(os.path.join(SPIKE_RES, "expected_check.tsv"), out)
    for cid, tgt, st, detail in out:
        print(f"[{st}] {cid:4s} {tgt:16s} {detail}")
    print(f"[spikein] PASS={counts['PASS']} WARN={counts['WARN']} FAIL={counts['FAIL']}"
          f" (synthetic={synthetic})")
    return counts


def main():
    ap = argparse.ArgumentParser(description="Check EasyWGS expected results")
    ap.add_argument("--mode", choices=["all", "panel", "spikein"], default="all")
    args = ap.parse_args()

    total = {"PASS": 0, "WARN": 0, "FAIL": 0}
    if args.mode in ("all", "panel"):
        for k, v in check_panel().items():
            total[k] += v
    if args.mode in ("all", "spikein"):
        for k, v in check_spikein().items():
            total[k] += v

    print(f"\nTOTAL PASS={total['PASS']} WARN={total['WARN']} FAIL={total['FAIL']}")
    print("WARN means the corresponding step has not run yet; FAIL needs attention.")
    sys.exit(1 if total["FAIL"] else 0)


if __name__ == "__main__":
    main()
