#!/usr/bin/env python3
"""V-Reproduction Phase 4 — 15-run sequential benchmark.

Runs `run_engine()` 15 times on distinct audio clips (each truncated to 30 s
by the engine's `MAX_DURATION_S` cap), measures wall time per run, and writes
`results/benchmark_runs.csv`.

Single-threaded, sequential, no warm-up exclusion (paper convention).
"""
from __future__ import annotations

import csv
import json
import os
import random
import sys
import time
from pathlib import Path

# Pin BLAS threads BEFORE numpy/torch imports
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = Path(__file__).resolve().parent
PHASE_DIR = HERE.parent
VREPRO_ROOT = PHASE_DIR.parent
INFRA = VREPRO_ROOT / "_infra"
SCIENCE_ROOT = VREPRO_ROOT.parent
REPO_ROOT = SCIENCE_ROOT.parent

# Prefer vendored engine; runner.py also does vendored-first resolution.
if str(INFRA) not in sys.path:
    sys.path.insert(0, str(INFRA))
import _engine_path  # noqa: E402,F401

from engine.runner import run_engine, FRAME_RATE, MAX_DURATION_S  # noqa: E402


SEED = 2026050604
N_RUNS = 15

LEGACY_AUDIO = SCIENCE_ROOT / "datasets" / "real-music"
DEAM_AUDIO = SCIENCE_ROOT / "datasets" / "emotion" / "DEAM" / "audio" / "MEMD_audio"


def select_clips() -> list[Path]:
    """Deterministic 15-clip selection: 6 Science/datasets/real-music + 9 DEAM random sample."""
    legacy_wavs = sorted(p for p in LEGACY_AUDIO.glob("*.wav"))
    if len(legacy_wavs) < 6:
        raise RuntimeError(f"expected ≥6 Science/datasets/real-music WAVs, found {len(legacy_wavs)}")
    legacy_pick = legacy_wavs[:6]

    deam_mp3s = sorted(p for p in DEAM_AUDIO.glob("*.mp3"))
    if len(deam_mp3s) < 9:
        raise RuntimeError(f"expected ≥9 DEAM mp3s, found {len(deam_mp3s)}")
    rng = random.Random(SEED)
    deam_pick = rng.sample(deam_mp3s, 9)

    return legacy_pick + deam_pick


def main() -> int:
    import librosa  # lazy

    clips = select_clips()
    assert len(clips) == N_RUNS, f"expected {N_RUNS} clips, got {len(clips)}"

    print(f"  Phase 4 benchmark: {N_RUNS} sequential runs, single-threaded")
    print(f"  Engine MAX_DURATION_S = {MAX_DURATION_S}, FRAME_RATE = {FRAME_RATE} Hz")

    out_csv = PHASE_DIR / "results" / "benchmark_runs.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    header = [
        "run_idx", "clip_name", "duration_s_processed", "n_frames",
        "wall_seconds", "fps", "real_time_ratio", "latency_ms_per_frame",
    ]
    rows = []

    for i, clip_path in enumerate(clips):
        # Cap duration to engine's MAX_DURATION_S
        try:
            clip_dur = float(librosa.get_duration(path=str(clip_path)))
        except Exception as e:
            print(f"  WARN failed to read duration for {clip_path}: {e!r}")
            continue
        duration_processed = min(clip_dur, MAX_DURATION_S)
        n_frames = int(duration_processed * FRAME_RATE)

        t0 = time.perf_counter()
        out = run_engine(
            clip_path,
            return_layers=("r3", "h3", "c3", "ram", "neuro", "beliefs"),
            seed=SEED,
        )
        wall = time.perf_counter() - t0

        fps = n_frames / wall
        rtr = duration_processed / wall
        lat_ms = (wall * 1000.0) / n_frames

        # If engine truncated, the actual T from r3 is the source of truth
        actual_T = out["r3"].shape[0] if "r3" in out else n_frames
        # Re-derive on actual_T for honesty
        fps = actual_T / wall
        lat_ms = (wall * 1000.0) / actual_T

        row = [
            i + 1,
            clip_path.name,
            round(duration_processed, 4),
            int(actual_T),
            round(wall, 6),
            round(fps, 3),
            round(rtr, 4),
            round(lat_ms, 6),
        ]
        rows.append(row)
        print(f"  run {i+1:2d}/{N_RUNS}: {clip_path.name[:50]:50s}  "
              f"T={actual_T:5d}  wall={wall:6.3f}s  fps={fps:7.2f}  "
              f"rtr={rtr:5.3f}×  lat={lat_ms:5.3f}ms")

        # Free memory
        del out

    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  wrote {out_csv}")

    # Summary numbers for downstream aggregator
    fps_vals = sorted(r[5] for r in rows)
    rtr_vals = sorted(r[6] for r in rows)
    lat_vals = sorted(r[7] for r in rows)

    def median(xs):
        n = len(xs); s = sorted(xs)
        return (s[n // 2] + s[(n - 1) // 2]) / 2.0

    def percentile(xs, p):
        s = sorted(xs); n = len(s)
        idx = max(0, min(n - 1, int(round((p / 100.0) * (n - 1)))))
        return s[idx]

    summary = {
        "n_runs": len(rows),
        "fps_median": median(fps_vals),
        "fps_mean": sum(fps_vals) / len(fps_vals),
        "rtr_median": median(rtr_vals),
        "rtr_mean": sum(rtr_vals) / len(rtr_vals),
        "lat_p50_ms": percentile(lat_vals, 50),
        "lat_p95_ms": percentile(lat_vals, 95),
        "lat_p99_ms": percentile(lat_vals, 99),
        "wall_total_s": sum(r[4] for r in rows),
        "clip_list": [r[1] for r in rows],
    }
    summary_path = PHASE_DIR / "results" / "_benchmark_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"  wrote {summary_path}")
    print(f"\n  median fps = {summary['fps_median']:.2f}, "
          f"median rtr = {summary['rtr_median']:.3f}×")
    print(f"  lat p50 = {summary['lat_p50_ms']:.3f} ms, "
          f"p95 = {summary['lat_p95_ms']:.3f} ms, "
          f"p99 = {summary['lat_p99_ms']:.3f} ms")

    return 0


if __name__ == "__main__":
    sys.exit(main())
