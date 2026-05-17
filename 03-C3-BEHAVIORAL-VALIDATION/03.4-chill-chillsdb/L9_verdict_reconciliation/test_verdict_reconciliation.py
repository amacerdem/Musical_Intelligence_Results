"""L9 — Verdict reconciliation against paper-time baseline.

After all primary tests run (L4 + L5-L8 if available), this layer reconciles
the locally produced results against the frozen paper-time baseline JSON.

It produces a final verdict block in REPORT.md and asserts that the headline
finding (MMP P2 Bonferroni-pass) is reproduced within tolerance.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest


def test_l4_result_csv_present(suite_root):
    """L4 must have produced its result CSV."""
    csv = suite_root / "L4_tc005_primary_verdict" / "results" / "tc005_single_channel_aggregate.csv"
    assert csv.exists(), (
        f"L4 result CSV missing at {csv}\n"
        f"Run L4 first: python3 run_all.py L4"
    )


def test_headline_finding_within_tolerance(suite_root, paper_baseline):
    """MMP P2 Bonferroni-pass within paper-time tolerance."""
    csv = suite_root / "L4_tc005_primary_verdict" / "results" / "tc005_single_channel_aggregate.csv"
    if not csv.exists():
        pytest.skip("L4 result CSV missing — run L4 first")
    df = pd.read_csv(csv)
    mmp_row = df[(df["channel"] == "MECH_MMP__P2:familiarity") & (df["audio"] == "afftdn")]
    assert not mmp_row.empty, "MMP P2 row missing from L4 result CSV"
    mmp = mmp_row.iloc[0]

    primary = paper_baseline["primary_verdict_tc005_clean7_afftdn"]
    expected_rb = next(c["rank_biserial_mean"] for c in primary["headline_channels"]
                       if c["channel"] == "MECH_MMP__P2:familiarity")
    expected_p = next(c["p_bonf"] for c in primary["headline_channels"]
                      if c["channel"] == "MECH_MMP__P2:familiarity")
    tol_rb = paper_baseline["tolerance"]["rank_biserial_abs"]
    tol_p = paper_baseline["tolerance"]["p_bonf_abs"]

    rb_drift = abs(mmp["mean_rank_biserial"] - expected_rb)
    p_drift = abs(mmp["bonf_p"] - expected_p)

    assert rb_drift < tol_rb, (
        f"Headline MMP P2 rb drift outside tolerance:\n"
        f"  expected: {expected_rb:+.4f}\n"
        f"  actual:   {mmp['mean_rank_biserial']:+.4f}\n"
        f"  drift:    {rb_drift:.4f}\n"
        f"  tol:      ±{tol_rb}"
    )
    assert p_drift < tol_p, (
        f"Headline MMP P2 bonf_p drift outside tolerance:\n"
        f"  expected: {expected_p:.4f}\n"
        f"  actual:   {mmp['bonf_p']:.4f}\n"
        f"  drift:    {p_drift:.4f}\n"
        f"  tol:      ±{tol_p}"
    )


def test_engine_sha_consistent(engine_pin):
    """Reconciliation requires the engine SHA pin be the canonical paper-time one."""
    expected = "482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88"
    assert engine_pin["content_aggregate_sha256"] == expected, (
        f"Pin manifest declares different engine SHA than paper-time baseline."
    )
