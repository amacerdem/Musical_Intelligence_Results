#!/usr/bin/env python3
"""Inspect raw_constants_inventory_v2.csv breakdown."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
rows = list(csv.DictReader((HERE / "raw_constants_inventory_v2.csv").open()))
print("total rows:", len(rows))
print()

print("by kind:")
for k, v in Counter(r["kind"] for r in rows).most_common():
    print(f"  {k}: {v}")
print()

print("by top module:")
for k, v in Counter(r["file_path"].split("/")[0] for r in rows).most_common():
    print(f"  {k}: {v}")
print()

print("by dtype:")
for k, v in Counter(r["dtype"] for r in rows).most_common():
    print(f"  {k}: {v}")
print()

has_cit = sum(1 for r in rows if r["has_citation_in_context"] == "1")
print(f"has_citation=1: {has_cit} ({has_cit/len(rows)*100:.1f}%)")

# Check if regions are now captured
regions = [r for r in rows if r["file_path"].startswith("brain/regions/")]
print(f"\nbrain/regions/ rows: {len(regions)}")
for r in regions[:20]:
    print(f"  {r['file_path']:30s} line={r['line']:4s} name={r['name']:25s} value={r['value']:20s} kind={r['kind']}")

# neurochemicals
nc = [r for r in rows if r["file_path"].startswith("brain/neurochemicals/")]
print(f"\nbrain/neurochemicals/ rows: {len(nc)}")
for r in nc[:20]:
    print(f"  {r['file_path']:40s} line={r['line']:4s} name={r['name']:25s} value={r['value']:30s} kind={r['kind']}")

# F1 BCH
bch = [r for r in rows if "f1/mechanisms/bch" in r["file_path"]]
print(f"\nF1-BCH rows: {len(bch)}")
print("  kinds:", dict(Counter(r["kind"] for r in bch)))

# F8 (learning)
f8 = [r for r in rows if r["file_path"].startswith("brain/functions/f8")]
print(f"\nF8 total rows: {len(f8)}")
print("  kinds:", dict(Counter(r["kind"] for r in f8)))

# expr-literal breakdown by top module
expr = [r for r in rows if r["kind"] == "expr-literal"]
print(f"\nexpr-literal rows: {len(expr)}")
print("  by module:", dict(Counter(r["file_path"].split("/")[0] for r in expr)))
# among expr-literal, most common values (hand-tuned signature)
val_counter = Counter(r["value"] for r in expr)
print("\nTop 30 expr-literal values (weight fingerprint):")
for v, c in val_counter.most_common(30):
    print(f"  {v:15s} ({c})")

# Cross-check reward.py
rewardr = [r for r in rows if r["file_path"] == "brain/reward.py"]
print(f"\nbrain/reward.py rows: {len(rewardr)}")
for r in rewardr:
    print(f"  line={r['line']:4s} name={r['name']:25s} value={r['value']:20s} kind={r['kind']} cit={r['citation_author']}")
