#!/usr/bin/env python3
"""V-Reproduction Phase 4 — Per-frame latency profile.

Operationalization (per 00-METHODOLOGY.md §6):
The frozen engine returns full (T, D) arrays in a single batched call; no
per-frame timing hook exists. We approximate per-frame latency as
`wall_per_run / n_frames_per_run`, then aggregate across the 15 benchmark
runs to extract p50, p95, p99 percentiles.

Reads: `results/_benchmark_summary.json` (produced by benchmark.py)
       `results/benchmark_runs.csv` (per-run latencies)
Writes: `results/latency_per_frame.csv`
        `results/_latency_summary.json`
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

# Pin BLAS threads
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = Path(__file__).resolve().parent
PHASE_DIR = HERE.parent

REAL_TIME_LINE_MS = 1000.0 / 172.265625  # = 5.805... ms (paper Table)


def percentile(xs, p):
    s = sorted(xs); n = len(s)
    if n == 0:
        return float("nan")
    idx = max(0, min(n - 1, int(round((p / 100.0) * (n - 1)))))
    return s[idx]


def main() -> int:
    bench_csv = PHASE_DIR / "results" / "benchmark_runs.csv"
    if not bench_csv.exists():
        print(f"  ERR: missing {bench_csv}; run benchmark.py first")
        return 2

    rows = []
    with open(bench_csv) as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append(row)

    lat_vals = [float(r["latency_ms_per_frame"]) for r in rows]
    p50 = percentile(lat_vals, 50)
    p95 = percentile(lat_vals, 95)
    p99 = percentile(lat_vals, 99)
    margin = REAL_TIME_LINE_MS / p95 if p95 > 0 else float("inf")

    out_csv = PHASE_DIR / "results" / "latency_per_frame.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value_ms"])
        w.writerow(["p50_latency_ms_per_frame", round(p50, 6)])
        w.writerow(["p95_latency_ms_per_frame", round(p95, 6)])
        w.writerow(["p99_latency_ms_per_frame", round(p99, 6)])
        w.writerow(["real_time_line_ms", round(REAL_TIME_LINE_MS, 6)])
        w.writerow(["p95_margin_factor", round(margin, 4)])
        w.writerow(["n_runs", len(lat_vals)])
        w.writerow(["min_latency_ms", round(min(lat_vals), 6)])
        w.writerow(["max_latency_ms", round(max(lat_vals), 6)])
        w.writerow(["mean_latency_ms", round(sum(lat_vals) / len(lat_vals), 6)])
    print(f"  p50 = {p50:.4f} ms, p95 = {p95:.4f} ms, p99 = {p99:.4f} ms")
    print(f"  real-time line = {REAL_TIME_LINE_MS:.4f} ms; p95 margin = {margin:.3f}×")
    print(f"  wrote {out_csv}")

    summary = {
        "p50_ms": p50,
        "p95_ms": p95,
        "p99_ms": p99,
        "real_time_line_ms": REAL_TIME_LINE_MS,
        "p95_margin_factor": margin,
        "n_runs": len(lat_vals),
        "all_latencies_ms": lat_vals,
        "approximation_note": (
            "Per-frame latency = wall_per_run / n_frames_per_run, aggregated "
            "across 15 runs. Engine returns batched (T, D) arrays; no per-frame "
            "timing hook exists in the frozen API. See 00-METHODOLOGY.md §6."
        ),
    }
    with open(PHASE_DIR / "results" / "_latency_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
