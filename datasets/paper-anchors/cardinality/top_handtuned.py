#!/usr/bin/env python3
"""Top-10 most alarming HAND-TUNED constants (R3 concession list)."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
rows = list(csv.DictReader((HERE / "parameter_provenance_table_engine_only.csv").open()))

ht = [r for r in rows if r["bucket"] == "HAND-TUNED"]
print(f"Total HAND-TUNED (engine-only): {len(ht)}")

# Group by name pattern — each named group is one "free parameter group"
# that, in honest accounting, counts once at the paper level (e.g., "TAU per-belief
# temporal integration weights — 63 beliefs × 1 TAU = 63 HAND-TUNED TAU values").
print("\nBy repeated name patterns (free-parameter groups):")
name_groups = Counter(r["name"] for r in ht)
for name, c in name_groups.most_common(30):
    # sample value range
    vals = sorted({r["value"] for r in ht if r["name"] == name})
    vals_short = ", ".join(vals[:5]) + (f" ... ({len(vals)} distinct)" if len(vals) > 5 else "")
    print(f"  {c:4d} × {name:40s}  values: {vals_short}")

# Top-10 most alarming: the named free-parameter groups
top_groups = name_groups.most_common(15)
print("\n\n=== TOP-15 HAND-TUNED FREE-PARAMETER GROUPS (alarming list) ===")
for name, c in top_groups:
    vals = sorted({r["value"] for r in ht if r["name"] == name})
    sample_files = list({r["file_path"] for r in ht if r["name"] == name})[:3]
    # first example's context line
    ex = next(r for r in ht if r["name"] == name)
    print(f"\n  {name} ({c} occurrences across {len(set(r['file_path'] for r in ht if r['name']==name))} files)")
    print(f"    value range: {vals[0]} to {vals[-1]}  ({len(vals)} distinct)")
    print(f"    sample files: {sample_files[:2]}")
    print(f"    example: {ex['file_path']}:{ex['line']}  ctx='{ex['context_line'][:80]}'")
