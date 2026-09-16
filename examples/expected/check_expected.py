#!/usr/bin/env python3
"""Check a panel run against examples/expected/expected_results.tsv.

Prints and writes examples/results/expected_check.tsv with PASS / WARN / FAIL per
rule and target. A metric that is absent because the module has not run is WARN,
not FAIL; the script exits non-zero only when a real, measured value violates a
rule. Run it after examples/01_run_panel.sh.
"""
import csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
RES = os.path.join(ROOT, "examples", "results")
RULES = os.path.join(HERE, "expected_results.tsv")

def read_tsv(p):
    if not os.path.exists(p): return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))

def is_na(v):
    return v is None or str(v).strip() in ("", "NA", "nan", "None")

def num(v):
    try: return float(str(v).replace(",", ""))
    except (TypeError, ValueError): return None

def compare(op, thr, val):
    """Return PASS/FAIL for a present value."""
    if op in (">=", "<=", "=="):
        x, t = num(val), num(thr)
        if x is None or t is None: return "FAIL" if str(val) != str(thr) else "PASS"
        if op == ">=": return "PASS" if x >= t else "FAIL"
        if op == "<=": return "PASS" if x <= t else "FAIL"
        return "PASS" if abs(x - t) < 1e-9 else "FAIL"
    if op == "in_range":
        lo, hi = [float(x) for x in thr.split("..")]; x = num(val)
        return "PASS" if x is not None and lo <= x <= hi else "FAIL"
    if op == "exists":
        return "PASS" if not is_na(val) else "FAIL"
    if op == "nonempty":
        return "PASS" if not is_na(val) else "FAIL"
    if op == "equals":
        return "PASS" if str(val).strip().lower() == thr.strip().lower() else "FAIL"
    return "FAIL"

def read_rules(p):
    if not os.path.exists(p): return []
    import io
    with open(p, encoding="utf-8") as f:
        lines = [l for l in f if l.strip() and not l.startswith("#")]
    return list(csv.DictReader(io.StringIO("".join(lines)), delimiter="\t"))

def main():
    per = read_tsv(os.path.join(RES, "panel_metrics.tsv"))
    cs = {r["metric"]: r["value"] for r in
          read_tsv(os.path.join(RES, "collection_stats.tsv"))}
    rules = read_rules(RULES)
    out = []
    counts = {"PASS": 0, "WARN": 0, "FAIL": 0}

    for rule in rules:
        cid, scope, group, metric, op, thr = (
            rule["check_id"], rule["scope"], rule["group"], rule["metric"],
            rule["operator"], rule["threshold"])
        if scope == "per_isolate":
            targets = [r for r in per if group == "all" or r.get("group") == group]
            if not targets:
                out.append((cid, "-", "WARN", "panel_metrics.tsv not found; run the panel first"))
                counts["WARN"] += 1; continue
            for r in targets:
                val = r.get(metric, "")
                if is_na(val):
                    st, detail = "WARN", f"{metric} not produced yet"
                else:
                    st = compare(op, thr, val)
                    detail = f"{metric}={val} {op} {thr}"
                out.append((cid, r["sample_id"], st, detail)); counts[st] += 1
        else:
            val = cs.get(metric)
            if is_na(val):
                st, detail = "WARN", f"{metric} not produced yet"
            else:
                st = compare(op, thr, val); detail = f"{metric}={val} {op} {thr}"
            out.append((cid, "collection", st, detail)); counts[st] += 1

    os.makedirs(RES, exist_ok=True)
    with open(os.path.join(RES, "expected_check.tsv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["check_id", "target", "status", "detail"]); w.writerows(out)
    for cid, tgt, st, detail in out:
        print(f"[{st}] {cid:4s} {tgt:16s} {detail}")
    print(f"\nPASS={counts['PASS']} WARN={counts['WARN']} FAIL={counts['FAIL']}")
    print("WARN means the corresponding module has not run yet; FAIL needs attention.")
    sys.exit(1 if counts["FAIL"] else 0)

if __name__ == "__main__":
    main()
