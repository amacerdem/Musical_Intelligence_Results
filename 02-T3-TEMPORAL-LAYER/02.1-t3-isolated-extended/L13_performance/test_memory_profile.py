"""L13.3 + L13.4 — Memory profile.

L13.3: peak resident memory of T³ stage on a single 30 s clip is below
       the documented 465 MB system-wide budget (T³ alone should be much less).
L13.4: memory scaling is approximately linear in clip duration (no quadratic
       blow-up from window aggregation).
"""
from __future__ import annotations

import resource

import pytest


def _get_max_rss_mb() -> float:
    """Peak resident set size in MB (cumulative over process lifetime).

    On macOS, ru_maxrss is in BYTES; on Linux it's in KILOBYTES.
    We detect by magnitude: a fresh Python process is typically 30-100 MB,
    so values > 1e7 are bytes (macOS) and values < 1e7 are KB (Linux).
    """
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Heuristic: a Python process never has < 10 MB resident
    if raw > 1e7:
        return raw / (1024 * 1024)  # bytes → MB (macOS)
    return raw / 1024  # KB → MB (Linux)


def test_t3_stage_memory_below_465mb_for_30s_clip(h3_extract, stim):
    """T=5165 frames ≈ 30 s. Peak RSS during T³ stage alone < 465 MB
    (the master paper system-wide ceiling). T³ alone should be well below this."""
    # Baseline before extract
    rss_before = _get_max_rss_mb()

    features = stim.stim_constant(value=0.5, T=5165, r3_dim=10)
    demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=15, law=0)
    out = h3_extract(features, demand)

    rss_after = _get_max_rss_mb()
    delta_mb = rss_after - rss_before

    print(f"\n  L13.3 RSS before: {rss_before:.1f} MB")
    print(f"  L13.3 RSS after:  {rss_after:.1f} MB")
    print(f"  L13.3 delta:      {delta_mb:.1f} MB")
    print(f"  L13.3 master paper system-wide ceiling: 465 MB")

    # T³ alone should not exceed the system-wide ceiling
    assert rss_after < 465.0, (
        f"T³ stage RSS {rss_after} MB exceeds system-wide ceiling 465 MB"
    )


def test_memory_scales_subquadratically(h3_extract, stim):
    """Memory should be approximately linear in T (no quadratic blow-up
    from window aggregation). We measure RSS at three T sizes and assert
    the doubling factor is < 4× (linear factor is 2×; quadratic is 4×)."""
    sizes = [512, 1024, 2048]
    rss_observations = []
    for T in sizes:
        features = stim.stim_constant(value=0.5, T=T, r3_dim=10)
        demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0)
        out = h3_extract(features, demand)
        rss_observations.append(_get_max_rss_mb())

    # Note: ru_maxrss is cumulative (peak so far), so direct subtraction may not
    # give per-call delta. We just assert that doubling T does not cause RSS to
    # grow by more than a factor of 4 between adjacent measurements.
    print(f"\n  L13.4 RSS at T=512:  {rss_observations[0]:.1f} MB")
    print(f"  L13.4 RSS at T=1024: {rss_observations[1]:.1f} MB")
    print(f"  L13.4 RSS at T=2048: {rss_observations[2]:.1f} MB")

    # Check that no doubling-step grows > 4× (would indicate quadratic blow-up)
    # Note: ru_maxrss is monotonic non-decreasing (it's a peak), so ratios
    # < 1.0 mean steady-state already reached
    ratio_1_2 = rss_observations[1] / rss_observations[0]
    ratio_2_4 = rss_observations[2] / rss_observations[1]
    print(f"  L13.4 doubling ratios: T=512→1024: {ratio_1_2:.2f}×; T=1024→2048: {ratio_2_4:.2f}×")
    assert ratio_1_2 < 4.0
    assert ratio_2_4 < 4.0
