"""L4 — Label rating distribution sanity + paper-time channel route validation.

Eerola has NO per-rater LOSO ceiling (mean ratings only on public deposit).
This layer instead checks:
  1. Per-label rating distributions are non-degenerate (sane variance)
  2. All 8 paper-time top channels resolve via pooled.csv route
  3. Engine cache duration is sane (~15s Eerola clips)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def test_set2_label_distributions(eerola_ratings_set2):
    df = pd.read_csv(eerola_ratings_set2)
    df.columns = [c.lower().strip() for c in df.columns]
    for label in ["valence", "energy", "tension", "anger", "fear", "happy", "sad", "tender"]:
        if label not in df.columns:
            continue
        vals = df[label].astype(float).values
        assert np.isfinite(vals).all(), f"{label} contains non-finite values"
        assert np.std(vals) > 0.3, f"{label} variance too low: std={np.std(vals):.3f}"
        # Likert 1-9 range bounds
        assert vals.min() >= 0.5 and vals.max() <= 10.5, (
            f"{label} out of Likert range: [{vals.min()}, {vals.max()}]"
        )


def test_paper_top_channels_resolve_in_pooled_csv(pooled_csv_set2, paper_baseline):
    pooled_cols = pd.read_csv(pooled_csv_set2, nrows=1).columns.tolist()
    s2_labels = paper_baseline["primary_verdict_set2"]["labels"]
    missing = []
    for label, spec in s2_labels.items():
        ch = spec["top_channel"]
        cls = ch[len("MECH_"):].split("__", 1)[0]
        class_cols = [c for c in pooled_cols if c.startswith(f"MECH_{cls}__")]
        if ch not in class_cols:
            missing.append((label, ch))
    assert not missing, f"Paper-time top channels missing from cache: {missing}"


def test_engine_duration_set2(engine_cache_set2):
    """Eerola film clips are ~15s; engine output should reflect that."""
    ENGINE_HZ = 172.265625
    durations = []
    for p in sorted(engine_cache_set2.glob("*.npz"))[:10]:
        z = np.load(p, allow_pickle=True)
        durations.append(z["r3"].shape[0] / ENGINE_HZ)
    assert min(durations) > 3, "Some Eerola clips suspiciously short"
    assert max(durations) < 30, "Some Eerola clips suspiciously long"
