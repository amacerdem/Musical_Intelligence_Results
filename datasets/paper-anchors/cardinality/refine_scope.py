#!/usr/bin/env python3
"""
Scope refinement: separate engine-frozen-code constants from scripts/ utilities.

The R3/R1 concern is about the ENGINE's declared constants. Python files
under scripts/ are training/utility scripts and are not part of the frozen
engine surface; they're excluded from the headline count in the honest
accounting table (but counted separately in a scripts row).

Also produces per-bucket per-top-level-module breakdown.
"""
from __future__ import annotations
import csv
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
rows = list(csv.DictReader((HERE / "parameter_provenance_table.csv").open()))

# Engine scope = everything except scripts/
engine_rows = [r for r in rows if not r["file_path"].startswith("scripts/")]
script_rows = [r for r in rows if r["file_path"].startswith("scripts/")]

print(f"Engine rows: {len(engine_rows)}")
print(f"Script rows: {len(script_rows)}")

print("\nEngine bucket counts:")
eb = Counter(r["bucket"] for r in engine_rows)
total = sum(eb.values())
for b, c in eb.most_common():
    print(f"  {b:15s} {c:6d}  {100*c/total:5.1f}%")

print("\nScript bucket counts:")
sb = Counter(r["bucket"] for r in script_rows)
for b, c in sb.most_common():
    print(f"  {b:15s} {c}")

# Per top-module engine breakdown
print("\nEngine bucket counts per top-level module:")
per_mod: defaultdict[str, Counter] = defaultdict(Counter)
for r in engine_rows:
    top = r["file_path"].split("/")[0]
    per_mod[top][r["bucket"]] += 1
for mod, cc in sorted(per_mod.items()):
    print(f"\n  {mod}:")
    tot = sum(cc.values())
    for b, c in cc.most_common():
        print(f"    {b:15s} {c:5d}  {100*c/tot:5.1f}%")

# Engine HAND-TUNED breakdown by file type
print("\n\nEngine HAND-TUNED by file category:")
cat_counts: Counter = Counter()
for r in engine_rows:
    if r["bucket"] != "HAND-TUNED":
        continue
    p = r["file_path"]
    if "/beliefs/" in p:
        cat_counts["C3 beliefs/*"] += 1
    elif "/mechanisms/" in p:
        cat_counts["C3 mechanisms/*"] += 1
    elif p.startswith("ear/r3/"):
        cat_counts["R3"] += 1
    elif p.startswith("ear/h3/"):
        cat_counts["H3"] += 1
    elif p.startswith("brain/reward") or p.startswith("brain/executor") or p.startswith("brain/beliefs"):
        cat_counts["C3 core (reward/executor/beliefs)"] += 1
    elif p.startswith("brain/dimensions/"):
        cat_counts["C3 dimensions"] += 1
    elif p.startswith("brain/regions/"):
        cat_counts["C3 regions"] += 1
    elif p.startswith("brain/neurochemicals/"):
        cat_counts["C3 neurochemicals"] += 1
    elif p.startswith("brain/functions/") and "/functions/" in p:
        cat_counts["C3 functions (other)"] += 1
    elif p.startswith("contracts/"):
        cat_counts["contracts"] += 1
    elif p.startswith("data/"):
        cat_counts["data"] += 1
    else:
        cat_counts[f"other:{p}"] += 1
for cat, c in cat_counts.most_common():
    print(f"  {c:5d}  {cat}")

# Per F1-F8 function
print("\nEngine HAND-TUNED by F{1..9}:")
fn_counts: Counter = Counter()
for r in engine_rows:
    if r["bucket"] != "HAND-TUNED":
        continue
    p = r["file_path"]
    import re
    m = re.search(r"brain/functions/(f\d+)/", p)
    if m:
        fn_counts[m.group(1)] += 1
    else:
        fn_counts["non-function"] += 1
for f, c in sorted(fn_counts.items()):
    print(f"  {f:15s} {c}")

# Same for CALIB-BOWLING
print("\nEngine CALIB-BOWLING by file category:")
cb_cats: Counter = Counter()
for r in engine_rows:
    if r["bucket"] != "CALIB-BOWLING":
        continue
    if "f1/mechanisms/bch" in r["file_path"]:
        cb_cats["F1-BCH"] += 1
    elif "ear/r3/groups/a_consonance" in r["file_path"]:
        cb_cats["R3-Group-A"] += 1
    else:
        cb_cats[f"other:{r['file_path']}"] += 1
for c, n in cb_cats.most_common():
    print(f"  {n:5d}  {c}")

# Write engine-only table
out_engine = HERE / "parameter_provenance_table_engine_only.csv"
with out_engine.open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(list(rows[0].keys()))
    for r in engine_rows:
        w.writerow([r[k] for k in rows[0].keys()])
print(f"\nEngine-only table: {out_engine} ({len(engine_rows)} rows)")

# Aggregate headline CSV
agg_out = HERE / "provenance_summary.csv"
with agg_out.open("w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["bucket", "engine_count", "pct_of_engine", "script_count", "total_count"])
    total_engine = len(engine_rows)
    total = len(rows)
    all_buckets = sorted(set(r["bucket"] for r in rows))
    for b in all_buckets:
        ec = sum(1 for r in engine_rows if r["bucket"] == b)
        sc = sum(1 for r in script_rows if r["bucket"] == b)
        w.writerow([b, ec, f"{100*ec/total_engine:.2f}%", sc, ec + sc])
    w.writerow(["TOTAL", total_engine, "100.00%", len(script_rows), total])
print(f"summary: {agg_out}")
