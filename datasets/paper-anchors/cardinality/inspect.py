#!/usr/bin/env python3
"""Inspect raw_constants_inventory.csv (v3)."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
rows = list(csv.DictReader((HERE / "raw_constants_inventory.csv").open()))
print("total rows:", len(rows))
print()

print("by kind:")
for k, v in Counter(r["kind"] for r in rows).most_common():
    print(f"  {k:25s} {v}")
print()

print("by top module:")
for k, v in Counter(r["file_path"].split("/")[0] for r in rows).most_common():
    print(f"  {k:15s} {v}")
print()

has_cit = sum(1 for r in rows if r["has_citation_in_context"] == "1")
print(f"has_citation=1: {has_cit} ({has_cit/len(rows)*100:.1f}%)")

# Link weights
links = [r for r in rows if r["kind"].startswith("link-weight")]
print(f"\nlink-weight rows: {len(links)}")
# Breakdown by Call name
print("  by call:", dict(Counter(r["name"].split(".")[0] for r in links)))

# regions
regions = [r for r in rows if r["file_path"].startswith("brain/regions/")]
print(f"\nregions rows: {len(regions)}")

# neurochem (channel assigns etc.)
nc = [r for r in rows if r["file_path"].startswith("brain/neurochemicals/")]
print(f"neurochem rows: {len(nc)}")

# F1 BCH
bch = [r for r in rows if "f1/mechanisms/bch" in r["file_path"]]
print(f"F1-BCH rows: {len(bch)}")
print("  kinds:", dict(Counter(r["kind"] for r in bch)))

# Expr-literal
el = [r for r in rows if r["kind"] == "expr-literal"]
print(f"\nexpr-literal rows: {len(el)}")

# Spec-numeric (LayerSpec, H3DemandSpec, _h3)
sp = [r for r in rows if r["kind"].startswith("spec-numeric")]
print(f"spec-numeric rows: {len(sp)}")

# Citation-call
cc = [r for r in rows if r["kind"].startswith("citation-call")]
print(f"citation-call rows: {len(cc)}")

# Top values
print("\nTop 20 values overall:")
for v, c in Counter(r["value"] for r in rows).most_common(20):
    print(f"  {v:20s} {c}")

# Scope-count
scope_counts = Counter(r["scope"].split("::")[-1] if "::" in r["scope"] else r["scope"] for r in rows)
print("\nTop 15 scopes (last segment):")
for s, c in scope_counts.most_common(15):
    print(f"  {s:40s} {c}")
