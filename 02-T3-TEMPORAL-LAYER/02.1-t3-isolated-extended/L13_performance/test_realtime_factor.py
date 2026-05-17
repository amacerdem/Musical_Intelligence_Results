"""L13.1 — T³ stage real-time factor on consumer M2 8GB.

Master paper §Compute profile (line 1298) reports system-wide median 570 fps,
peak resident memory 465 MB on M2 Max 64 GB. The T³ stage alone should be
considerably faster than the system-wide rate (since T³ is one of three layers).

This test measures the T³ stage's median frames-per-second on a 1024-frame
clip with the all-morphs-one-horizon demand (24 tuples). It does NOT compete
against the system-wide ceiling; it characterises T³'s share of the budget.

We assert real-time-or-better at 172.27 Hz frame rate (the documented R³
frame rate).
"""
from __future__ import annotations

import statistics
import time

import pytest


N_RUNS = 30
T_FRAMES = 1024
TARGET_FPS_MIN = 172.27  # documented frame rate floor


def test_t3_stage_above_realtime_at_24_morphs(h3_extract, stim):
    """T³ stage achieves >= 172.27 fps median across 30 runs × T=1024 × 24 morphs at H5/L0.
    Master paper systemwide claim: 570 fps median; T³ stage alone should clear realtime."""
    features = stim.stim_sinusoid(freq_hz=4.0, T=T_FRAMES, r3_dim=10)
    demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0)

    # Warm-up (don't time)
    for _ in range(3):
        h3_extract(features, demand)

    fps_observations = []
    for _ in range(N_RUNS):
        t0 = time.perf_counter()
        out = h3_extract(features, demand)
        elapsed = time.perf_counter() - t0
        fps_observations.append(T_FRAMES / elapsed)

    median_fps = statistics.median(fps_observations)
    p95_fps = sorted(fps_observations)[int(0.95 * N_RUNS)]

    print(f"\n  L13.1 median fps: {median_fps:.0f}")
    print(f"  L13.1 p95 fps:    {p95_fps:.0f}")
    print(f"  L13.1 target floor (real-time): {TARGET_FPS_MIN:.2f}")

    assert median_fps >= TARGET_FPS_MIN, (
        f"T³ stage real-time factor below 1×: median fps {median_fps:.0f} "
        f"< target {TARGET_FPS_MIN}"
    )


def test_t3_stage_with_full_horizon_sweep(h3_extract, stim):
    """All 32 horizons × 1 morph × 1 law = 32 tuples. Median fps should still
    clear realtime floor (engine reuses kernel weights per horizon)."""
    features = stim.stim_sinusoid(freq_hz=4.0, T=T_FRAMES, r3_dim=10)
    demand = stim.demand_all_horizons_one_morph(r3_idx=10, morph=0, law=0)

    for _ in range(3):
        h3_extract(features, demand)

    fps_observations = []
    for _ in range(15):  # fewer runs because Ultra horizons are slower
        t0 = time.perf_counter()
        out = h3_extract(features, demand)
        elapsed = time.perf_counter() - t0
        fps_observations.append(T_FRAMES / elapsed)

    median_fps = statistics.median(fps_observations)
    print(f"\n  L13.1' (32-horizon sweep) median fps: {median_fps:.0f}")

    assert median_fps >= TARGET_FPS_MIN, (
        f"T³ stage 32-horizon sweep below realtime: median fps {median_fps:.0f}"
    )


def test_t3_stage_warm_vs_cold_documented(h3_extract, stim):
    """Document the warm-vs-cold start gap. First call may be slower
    (e.g., torch JIT, graph build). Steady-state should be much faster."""
    features = stim.stim_sinusoid(freq_hz=4.0, T=T_FRAMES, r3_dim=10)
    demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=0)

    # Cold call
    t0 = time.perf_counter()
    h3_extract(features, demand)
    cold_time = time.perf_counter() - t0

    # Warm calls
    warm_times = []
    for _ in range(10):
        t0 = time.perf_counter()
        h3_extract(features, demand)
        warm_times.append(time.perf_counter() - t0)
    warm_median = statistics.median(warm_times)

    print(f"\n  L13.6 cold call: {cold_time*1000:.2f} ms")
    print(f"  L13.6 warm median: {warm_median*1000:.2f} ms")
    print(f"  L13.6 cold/warm ratio: {cold_time/warm_median:.1f}×")

    # Always pass — this is a characterisation test, not an assertion of
    # a specific cold-warm ratio (which depends on torch state)
    assert cold_time > 0
    assert warm_median > 0
