#!/usr/bin/env python3
"""V-Reproduction Phase 4 — figures (fps distribution, latency hist, memory).

Reads results/benchmark_runs.csv + results/_memory_summary.json.
Writes figures/{fps_distribution,latency_histogram,memory_trace}.png.
"""
from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
PHASE_DIR = HERE.parent
FIG_DIR = PHASE_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


PAPER_FPS = 570.0
PAPER_PEAK_MB = 465.0
PAPER_P50 = 1.753
PAPER_P95 = 1.972


def main() -> int:
    rows = []
    with open(PHASE_DIR / "results" / "benchmark_runs.csv") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    fps = np.array([float(r["fps"]) for r in rows])
    lat = np.array([float(r["latency_ms_per_frame"]) for r in rows])
    walls = np.array([float(r["wall_seconds"]) for r in rows])

    # ── Figure 1: FPS distribution ─────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(fps, bins=10, color="#3070C0", edgecolor="black")
    ax.axvline(np.median(fps), color="red", linestyle="--",
               label=f"median = {np.median(fps):.1f} fps")
    ax.axvline(PAPER_FPS, color="gray", linestyle=":",
               label=f"paper = {PAPER_FPS} fps (M2 Max 64GB)")
    ax.set_xlabel("fps")
    ax.set_ylabel("count")
    ax.set_title(f"Phase 4 fps distribution (15 × 30s runs, M2 8GB)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fps_distribution.png", dpi=120)
    plt.close(fig)
    print(f"  wrote {FIG_DIR / 'fps_distribution.png'}")

    # ── Figure 2: Latency histogram ────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(lat, bins=10, color="#C03070", edgecolor="black")
    ax.axvline(np.median(lat), color="red", linestyle="--",
               label=f"p50 = {np.median(lat):.3f} ms")
    ax.axvline(np.percentile(lat, 95), color="orange", linestyle="--",
               label=f"p95 = {np.percentile(lat, 95):.3f} ms")
    ax.axvline(PAPER_P50, color="gray", linestyle=":",
               label=f"paper p50 = {PAPER_P50} ms")
    ax.axvline(5.805, color="black", linestyle="-",
               label="real-time line = 5.805 ms")
    ax.set_xlabel("ms / frame")
    ax.set_ylabel("count")
    ax.set_title("Phase 4 per-frame latency (wall ÷ T_frames per run)")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "latency_histogram.png", dpi=120)
    plt.close(fig)
    print(f"  wrote {FIG_DIR / 'latency_histogram.png'}")

    # ── Figure 3: Memory trace (per-run wall vs run idx) ──────────────
    with open(PHASE_DIR / "results" / "_memory_summary.json") as f:
        mem = json.load(f)
    fig, ax = plt.subplots(figsize=(8, 4))
    run_idx = np.arange(1, len(walls) + 1)
    ax.plot(run_idx, walls, "o-", color="#208030",
            label=f"per-run wall (median {np.median(walls):.2f}s)")
    ax.set_xlabel("run idx")
    ax.set_ylabel("wall seconds (30s clip)")
    ax.set_title(
        f"Phase 4 per-run wall time + peak RSS = {mem['peak_mb']:.1f} MB "
        f"(paper {PAPER_PEAK_MB} MB on M2 Max 64GB)"
    )
    ax.axhline(30 / 3.31, color="gray", linestyle=":",
               label=f"paper wall (3.31× rtr) = {30/3.31:.2f}s")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "memory_trace.png", dpi=120)
    plt.close(fig)
    print(f"  wrote {FIG_DIR / 'memory_trace.png'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
