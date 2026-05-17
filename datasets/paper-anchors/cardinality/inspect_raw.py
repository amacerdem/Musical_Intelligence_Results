#!/usr/bin/env python3
"""Quick inspection script for raw_constants_inventory.csv."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
rows = list(csv.DictReader((HERE / "raw_constants_inventory.csv").open()))
print("total rows:", len(rows))

# by top-level module
tops = Counter(r["file_path"].split("/")[0] for r in rows)
print("by top module:", dict(tops))

# by dtype
print("by dtype:", dict(Counter(r["dtype"] for r in rows)))

# citations
has_cit = sum(1 for r in rows if r["has_citation_in_context"] == "1")
has_todo = sum(1 for r in rows if r["has_todo_fixme"] == "1")
print(f"has_citation=1: {has_cit} ({has_cit/len(rows)*100:.1f}%)")
print(f"has_todo=1: {has_todo}")

# ear subtree breakdown
ear_rows = [r for r in rows if r["file_path"].startswith("ear/")]
print("\near rows:", len(ear_rows))
print("ear subdirs:", dict(Counter("/".join(r["file_path"].split("/")[:3]) for r in ear_rows)))

brain_rows = [r for r in rows if r["file_path"].startswith("brain/")]
print("\nbrain rows:", len(brain_rows))
print("brain subdirs:", dict(Counter("/".join(r["file_path"].split("/")[:3]) for r in brain_rows)))

# F1-F9 function breakdown
func_rows = [r for r in rows if r["file_path"].startswith("brain/functions/")]
print("\nbrain/functions rows:", len(func_rows))
print("functions:", dict(Counter(r["file_path"].split("/")[2] for r in func_rows)))

# region rows
region_rows = [r for r in rows if r["file_path"].startswith("brain/regions/")]
print("\nbrain/regions rows:", len(region_rows))

# neurochem rows
nc_rows = [r for r in rows if r["file_path"].startswith("brain/neurochemicals/")]
print("brain/neurochemicals rows:", len(nc_rows))

# beliefs
belief_rows = [r for r in rows if "beliefs" in r["file_path"].lower()]
print("any 'beliefs' in path rows:", len(belief_rows))

# sample name counts
name_counter = Counter(r["name"] for r in rows)
print("\ntop 30 names:", name_counter.most_common(30))

# unique files with constants
print("\nunique files:", len({r["file_path"] for r in rows}))

# config / contracts
for prefix in ("config/", "contracts/", "utils/", "data/"):
    pr = [r for r in rows if r["file_path"].startswith(prefix)]
    print(f"{prefix} rows: {len(pr)}")
