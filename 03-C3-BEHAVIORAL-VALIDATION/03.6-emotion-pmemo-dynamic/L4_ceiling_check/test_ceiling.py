"""L4 — Reproduce PMEmo dynamic LOSO ceilings (arousal +0.171, valence +0.158).

Re-runs compute_pmemo_loso_ceiling.py logic inline (compact form) and checks
both arousal and valence ceilings match paper-time baseline within tolerance.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import stats as scistats


def fisher_z(r):
    r = np.clip(r, -0.999999, 0.999999)
    return 0.5 * np.log((1 + r) / (1 - r))


def fisher_z_inv(z):
    return (np.exp(2 * z) - 1) / (np.exp(2 * z) + 1)


def parse_pmemo_rater_csv(path: Path):
    raters = []
    with open(path) as f:
        for line in f:
            parts = line.strip().split(',')
            if not parts[0].isdigit():
                continue
            dyn = np.array([float(x) for x in parts[2:]], dtype=np.float64)
            raters.append(dyn)
    return raters


def _compute_dynamic_ceiling(annot_dir: Path):
    trial_rhos = []
    n_clips = 0
    csvs = sorted(annot_dir.glob("*.csv"))
    for csv in csvs:
        raters = parse_pmemo_rater_csv(csv)
        if len(raters) < 2:
            continue
        min_len = min(len(r) for r in raters)
        if min_len < 8:
            continue
        trajs = [r[:min_len] for r in raters]
        clip_trials = []
        for i in range(len(trajs)):
            others = trajs[:i] + trajs[i + 1:]
            consensus = np.mean(others, axis=0)
            held = trajs[i]
            if np.std(consensus) < 1e-6 or np.std(held) < 1e-6:
                continue
            try:
                r, _ = scistats.spearmanr(consensus, held)
            except Exception:
                continue
            if not np.isnan(r):
                clip_trials.append(float(r))
                trial_rhos.append(float(r))
        if clip_trials:
            n_clips += 1
    if not trial_rhos:
        return float("nan"), 0, 0
    point = fisher_z_inv(np.mean([fisher_z(r) for r in trial_rhos]))
    return point, len(trial_rhos), n_clips


def test_arousal_ceiling_reproduces(pmemo_annotations_arousal, paper_baseline):
    point, n_trials, n_clips = _compute_dynamic_ceiling(pmemo_annotations_arousal)
    expected = paper_baseline["loso_ceiling_arousal"]["point_estimate"]
    tol = paper_baseline["tolerance"]["ceiling_abs_arousal"]
    assert abs(point - expected) < tol, (
        f"Arousal ceiling drift outside tolerance:\n"
        f"  expected: {expected:.4f}\n  actual: {point:.4f}\n"
        f"  diff:     {abs(point - expected):.4f}\n  tol: {tol}"
    )
    assert n_trials >= 5000, f"Only {n_trials} LOSO trials (expected ≥5000)"
    assert n_clips >= 700, f"Only {n_clips} clips processed (expected ≥700)"


def test_valence_ceiling_reproduces(pmemo_annotations_valence, paper_baseline):
    point, n_trials, n_clips = _compute_dynamic_ceiling(pmemo_annotations_valence)
    expected = paper_baseline["loso_ceiling_valence"]["point_estimate"]
    tol = paper_baseline["tolerance"]["ceiling_abs_valence"]
    assert abs(point - expected) < tol, (
        f"Valence ceiling drift outside tolerance:\n"
        f"  expected: {expected:.4f}\n  actual: {point:.4f}\n"
        f"  diff:     {abs(point - expected):.4f}\n  tol: {tol}"
    )
    assert n_trials >= 5000, f"Only {n_trials} LOSO trials (expected ≥5000)"
    assert n_clips >= 700, f"Only {n_clips} clips processed (expected ≥700)"
