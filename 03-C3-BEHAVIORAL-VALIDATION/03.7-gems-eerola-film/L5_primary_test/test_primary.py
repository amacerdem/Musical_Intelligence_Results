"""L5 — PRIMARY: Eerola Set 2 inline re-run of 8 GEMS labels.

Aggregates engine per-clip (mean over duration), computes cross-clip Spearman
between MECH channel and mean rating for each of 8 labels, then verifies:
  - Top channel for each label matches paper baseline (exact match)
  - Top ρ within tolerance
  - At least 6 of 8 labels Bonferroni-pass at top channel
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats as scistats

LABEL_TO_POOL = {
    "valence":  "VALENCE-15",
    "energy":   "AROUSAL-19",
    "tension":  "TENSION-15",
    "anger":    "ANGER-16",
    "fear":     "FEAR-17",
    "happy":    "HAPPY-16",
    "sad":      "SADNESS-15",
    "tender":   "TENDERNESS-15",
}

POOLS_JSON_REL = "Science/c3-cognitive-signals/_prereg/pools.json"


def aggregate_clip(npz_path, mech_key, idx):
    z = np.load(npz_path, allow_pickle=True)
    arr = z[mech_key]
    seg = arr[:, idx] if arr.ndim > 1 else arr
    if len(seg) > 200:
        seg = seg[172:]
    return float(np.nanmean(seg))


def _build_route(pool_channels, pooled_csv):
    pooled_cols = pd.read_csv(pooled_csv, nrows=1).columns.tolist()
    route, valid = {}, []
    for ch in pool_channels:
        cls = ch[len("MECH_"):].split("__", 1)[0]
        class_cols = [c for c in pooled_cols if c.startswith(f"MECH_{cls}__")]
        if ch in class_cols:
            route[ch] = (f"mech_{cls}", class_cols.index(ch))
            valid.append(ch)
    return route, valid


def _load_pool(project_root, pool_name):
    candidates = [
        project_root / "c3-cognitive-signals" / "_prereg" / "pools.json",
        project_root / "Science" / "c3-cognitive-signals" / "_prereg" / "pools.json",
    ]
    for c in candidates:
        if c.exists():
            with open(c) as f:
                return json.load(f)["pools"][pool_name]["channels"]
    raise FileNotFoundError(f"pools.json not found in candidates: {candidates}")


@pytest.fixture(scope="module")
def set2_results(eerola_ratings_set2, engine_cache_set2, pooled_csv_set2, project_root):
    df = pd.read_csv(eerola_ratings_set2)
    df.columns = [c.lower().strip() for c in df.columns]
    df["clip_id"] = df["number"].apply(lambda x: f"{int(x):03d}")

    clip_ids = [cid for cid in df["clip_id"] if (engine_cache_set2 / f"{cid}.npz").exists()]
    df = df[df["clip_id"].isin(clip_ids)].reset_index(drop=True)

    results = {}
    for label, pool_name in LABEL_TO_POOL.items():
        if label not in df.columns:
            continue
        pool = _load_pool(project_root, pool_name)
        route, valid_pool = _build_route(pool, pooled_csv_set2)
        k = len(valid_pool)
        label_vec = df[label].astype(float).values

        rows = []
        for ch in valid_pool:
            mech_key, idx = route[ch]
            mech_vec = np.array([
                aggregate_clip(engine_cache_set2 / f"{cid}.npz", mech_key, idx)
                for cid in df["clip_id"]
            ])
            if np.std(mech_vec) < 1e-9:
                continue
            rho, p = scistats.spearmanr(mech_vec, label_vec)
            rows.append({"channel": ch, "rho": float(rho), "p": float(p)})
        res = pd.DataFrame(rows)
        res["p_bonf"] = np.clip(res["p"] * k, 0, 1)
        res = res.sort_values("rho", key=lambda s: s.abs(), ascending=False)
        results[label] = {"k": k, "df": res}
    return results


def test_set2_top_channels_match_baseline(set2_results, paper_baseline):
    s2_labels = paper_baseline["primary_verdict_set2"]["labels"]
    mismatches = []
    for label, spec in s2_labels.items():
        if label not in set2_results:
            continue
        top = set2_results[label]["df"].iloc[0]
        expected = spec["top_channel"]
        if top["channel"] != expected:
            mismatches.append(f"{label}: got {top['channel']}, expected {expected}")
    assert not mismatches, f"Top-channel mismatches: {mismatches}"


def test_set2_top_rho_tolerances(set2_results, paper_baseline):
    s2_labels = paper_baseline["primary_verdict_set2"]["labels"]
    tol = paper_baseline["tolerance"]["rho_abs_set2"]
    drifts = []
    for label, spec in s2_labels.items():
        if label not in set2_results:
            continue
        top = set2_results[label]["df"].iloc[0]
        expected = spec["rho"]
        if abs(top["rho"] - expected) > tol:
            drifts.append(f"{label}: got {top['rho']:+.4f}, expected {expected:+.4f}")
    assert not drifts, f"Top-rho drifts beyond tolerance ({tol}): {drifts}"


def test_set2_bonferroni_breadth(set2_results, paper_baseline):
    """At least 6 of 8 labels must have Bonferroni-pass top channel."""
    expected_min = paper_baseline["tolerance"]["n_bonferroni_pass_min_set2_total"]
    n_pass = 0
    for label, spec in set2_results.items():
        top = spec["df"].iloc[0]
        if top["p_bonf"] < 0.05:
            n_pass += 1
    assert n_pass >= expected_min, (
        f"Only {n_pass}/{len(set2_results)} labels have Bonferroni-pass top channel "
        f"(expected ≥{expected_min})"
    )
