#!/usr/bin/env python3
"""Sample link rows to understand positional structure."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
rows = list(csv.DictReader((HERE / "raw_constants_inventory.csv").open()))

# RegionLink samples
rl = [r for r in rows if r["name"].startswith("RegionLink")]
print(f"RegionLink rows: {len(rl)}")
print("  positional distribution:", dict(Counter(r["kind"] for r in rl)))
print("  sample first 5:")
for r in rl[:5]:
    print(f"    {r['file_path']}:{r['line']}  {r['name']:25s} value={r['value']:10s}  line='{r['context_line'][:80]}'")

# NeuroLink samples
nl = [r for r in rows if r["name"].startswith("NeuroLink")]
print(f"\nNeuroLink rows: {len(nl)}")
print("  positional distribution:", dict(Counter(r["kind"] for r in nl)))
print("  sample first 10:")
for r in nl[:10]:
    print(f"    {r['file_path']}:{r['line']}  {r['name']:25s} value={r['value']:10s}  line='{r['context_line'][:80]}'")

# spec-numeric distribution — what call names
print("\nspec-numeric breakdown by call-name:")
sp_names = Counter(r["name"].split(".")[0] for r in rows if r["kind"].startswith("spec-numeric"))
for n, c in sp_names.most_common(10):
    print(f"  {n:30s} {c}")

# citation-call distribution
print("\ncitation-call breakdown by call-name:")
cc_names = Counter(r["name"].split(".")[0] for r in rows if r["kind"].startswith("citation-call"))
for n, c in cc_names.most_common(10):
    print(f"  {n:30s} {c}")

# samples of citation-call
cc = [r for r in rows if r["kind"].startswith("citation-call")]
print("\nsample 5 citation-call rows:")
for r in cc[:5]:
    print(f"  {r['file_path']}:{r['line']}  {r['name']:25s} value={r['value']:15s}  line='{r['context_line'][:80]}'")

# confidence_range tuples in metadata
cr = [r for r in rows if "confidence_range" in r["name"].lower() or "confidence_range" in r["context_line"].lower()]
print(f"\nconfidence_range rows: {len(cr)}")

# Which files have the most constants (top 20)
by_file = Counter(r["file_path"] for r in rows)
print("\nTop 20 files by count:")
for f, c in by_file.most_common(20):
    print(f"  {c:5d}  {f}")

# Check 'data/' contents
print("\ndata/ rows:")
for r in [r for r in rows if r["file_path"].startswith("data/")][:15]:
    print(f"  {r['file_path']}:{r['line']}  {r['name']:25s} value={r['value']:10s}  kind={r['kind']}")
