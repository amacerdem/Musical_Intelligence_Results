#!/usr/bin/env python3
"""Deep inspection of final classification."""
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

for b, rs in by_bucket.items():
    print(f"\n== {b} ({len(rs)}) ==")
    print("  by reason:", dict(Counter(r["bucket_reason"] for r in rs)))
    print("  by kind:", dict(Counter(r["kind"] for r in rs).most_common(5)))
    print("  top files:", dict(Counter(r["file_path"] for r in rs).most_common(5)))

# HAND-TUNED deep dive - the most alarming list for R3
print("\n\n=== HAND-TUNED constants (the R3 concession list) ===")
ht = by_bucket["HAND-TUNED"]
print(f"Total: {len(ht)}")
# By file
ht_by_file = Counter(r["file_path"] for r in ht)
print("\nTop 20 HAND-TUNED files:")
for f, c in ht_by_file.most_common(20):
    print(f"  {c:4d}  {f}")
# Sample specific examples
print("\nSample 20 HAND-TUNED examples:")
for r in ht[:20]:
    print(f"  [{r['bucket_reason'][:30]:30s}] {r['file_path']}:{r['line']}  {r['name']:25s} = {r['value']:12s}  line='{r['context_line'][:70]}'")

# Most salient: reward.py + named-token reward weights
reward_ht = [r for r in ht if r["bucket_reason"].startswith("reward-handtuned")]
print(f"\nreward-named HAND-TUNED: {len(reward_ht)}")
reward_unique = Counter(r["name"] for r in reward_ht)
print("  unique names:", dict(reward_unique.most_common(15)))

# Top-10 most-alarming HAND-TUNED list (ordered by salience: reward + module-level + named)
print("\n\n=== TOP HAND-TUNED constants (alarming list for R3) ===")
# Sort: prefer reward-named, then module-assign with names, then per-file distinct
salience: list[tuple[str, dict]] = []
for r in ht:
    score = 0
    if "W_" in r["name"] or "reward" in r["bucket_reason"]:
        score += 10
    if r["kind"] in ("module-assign", "class-attr", "ann-assign"):
        score += 5
    if "TAU" in r["name"]:
        score += 3
    salience.append((score, r))
salience.sort(key=lambda p: -p[0])

seen_names: set[str] = set()
top10: list[dict] = []
for score, r in salience:
    key = (r["file_path"], r["name"])
    if key in seen_names:
        continue
    seen_names.add(key)
    top10.append(r)
    if len(top10) >= 20:
        break

for r in top10:
    print(f"  {r['file_path']}:{r['line']}  {r['name']:28s} = {r['value']:12s}  ctx='{r['context_line'][:70]}'")
