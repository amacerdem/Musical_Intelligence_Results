"""L2 — Eerola Set 2 + Set 1 ratings CSVs + engine .npz files present."""
from __future__ import annotations
import pandas as pd
import pytest


def test_set2_ratings_csv_exists(eerola_ratings_set2):
    assert eerola_ratings_set2.exists(), f"Set 2 ratings CSV not found: {eerola_ratings_set2}"


def test_set1_ratings_csv_exists(eerola_ratings_set1):
    assert eerola_ratings_set1.exists(), f"Set 1 ratings CSV not found: {eerola_ratings_set1}"


def test_set2_ratings_complete(eerola_ratings_set2):
    df = pd.read_csv(eerola_ratings_set2)
    assert len(df) >= 110, f"Set 2 ratings has {len(df)} rows, expected ≥110"
    # Column normalization (Set 2 has Title Case)
    cols_lower = [c.lower().strip() for c in df.columns]
    required_labels = {"valence", "energy", "tension", "anger", "fear", "happy", "sad", "tender"}
    assert required_labels.issubset(set(cols_lower)), (
        f"Set 2 missing labels: {required_labels - set(cols_lower)}"
    )


def test_set1_ratings_complete(eerola_ratings_set1):
    df = pd.read_csv(eerola_ratings_set1)
    assert len(df) >= 360, f"Set 1 ratings has {len(df)} rows, expected ≥360"


def test_engine_cache_set2_present(engine_cache_set2):
    npzs = sorted(engine_cache_set2.glob("*.npz"))
    assert len(npzs) >= 110, f"Set 2 engine cache has {len(npzs)} npz, expected ≥110"


def test_engine_cache_set1_present(engine_cache_set1):
    npzs = sorted(engine_cache_set1.glob("*.npz"))
    assert len(npzs) >= 360, f"Set 1 engine cache has {len(npzs)} npz, expected ≥360"


def test_pooled_csv_set2(pooled_csv_set2):
    assert pooled_csv_set2.exists(), f"Set 2 pooled.csv not found: {pooled_csv_set2}"
