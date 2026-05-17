#!/usr/bin/env python3
"""Deep inspection of provenance classification."""
from __future__ import annotations
import csv
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
rows = list(csv.DictReader((HERE / "parameter_provenance_table.csv").open()))
print(f"Total: {len(rows)}")

by_bucket: defaultdict[str, list] = defaultdict(list)
for r in rows:
    by_bucket[r["bucket"]].append(r)

print("\n== HAND-TUNED breakdown ==")
ht = by_bucket["HAND-TUNED"]
print(f"total: {len(ht)}")
print("by kind:", dict(Counter(r["kind"] for r in ht)))
print("by top-module:", dict(Counter(r["file_path"].split("/")[0] for r in ht)))
print("by bucket_reason:", dict(Counter(r["bucket_reason"] for r in ht)))

# For expr-literal-in-compute-no-citation, show sample + check if the file has
# a module-level docstring with citations (we missed)
el_nc = [r for r in ht if r["bucket_reason"] == "expr-literal-in-compute-no-citation"]
print(f"\nexpr-literal-in-compute-no-citation count: {len(el_nc)}")
# sample 10
for r in el_nc[:10]:
    print(f"  {r['file_path']}:{r['line']}  name={r['name']:15s} value={r['value']:10s} line='{r['context_line'][:80]}'")

# Most-common values among HAND-TUNED — this reveals the weight fingerprint
print("\nTop 20 HAND-TUNED values:")
for v, c in Counter(r["value"] for r in ht).most_common(20):
    print(f"  {v:15s} {c}")

print("\n== LIT-FROZEN breakdown ==")
lf = by_bucket["LIT-FROZEN"]
print(f"total: {len(lf)}")
print("by kind:", dict(Counter(r["kind"] for r in lf)))
print("by bucket_reason:", dict(Counter(r["bucket_reason"] for r in lf)))

print("\n== CALIB-BOWLING breakdown ==")
cb = by_bucket["CALIB-BOWLING"]
print(f"total: {len(cb)}")
print("by kind:", dict(Counter(r["kind"] for r in cb)))
print("by file:", dict(Counter(r["file_path"] for r in cb).most_common(10)))
print("by bucket_reason:", dict(Counter(r["bucket_reason"] for r in cb)))

print("\n== STRUCTURAL breakdown ==")
s = by_bucket["STRUCTURAL"]
print(f"total: {len(s)}")
print("by kind:", dict(Counter(r["kind"] for r in s)))

print("\n== NULL-FALLBACK breakdown ==")
n = by_bucket["NULL-FALLBACK"]
print(f"total: {len(n)}")
print("by kind:", dict(Counter(r["kind"] for r in n)))
print("by bucket_reason:", dict(Counter(r["bucket_reason"] for r in n)))

# F1-BCH specifically
bch = [r for r in rows if "f1/mechanisms/bch" in r["file_path"]]
print(f"\n== F1-BCH ({len(bch)} rows) ==")
print("by bucket:", dict(Counter(r["bucket"] for r in bch)))

# reward.py
rwd = [r for r in rows if r["file_path"] == "brain/reward.py"]
print(f"\n== brain/reward.py ({len(rwd)} rows) ==")
for r in rwd:
    print(f"  line={r['line']:4s} name={r['name']:25s} value={r['value']:15s} bucket={r['bucket']:15s} reason={r['bucket_reason']}")
