"""L2 — PMEmo per-rater CSVs + engine .npz files present."""
from __future__ import annotations
import pytest


def test_pmemo_arousal_dir_exists(pmemo_annotations_arousal):
    assert pmemo_annotations_arousal.exists(), f"PMEmo arousal dir not found: {pmemo_annotations_arousal}"


def test_pmemo_valence_dir_exists(pmemo_annotations_valence):
    assert pmemo_annotations_valence.exists(), f"PMEmo valence dir not found: {pmemo_annotations_valence}"


def test_arousal_csvs_present(pmemo_annotations_arousal):
    csvs = sorted(pmemo_annotations_arousal.glob("*-A.csv"))
    assert len(csvs) >= 700, f"Expected ≥700 arousal CSVs, got {len(csvs)}"


def test_valence_csvs_present(pmemo_annotations_valence):
    csvs = sorted(pmemo_annotations_valence.glob("*-V.csv"))
    assert len(csvs) >= 700, f"Expected ≥700 valence CSVs, got {len(csvs)}"


def test_engine_cache_dir_exists(engine_cache_dir):
    assert engine_cache_dir.exists(), f"Engine cache not found: {engine_cache_dir}"


def test_engine_npz_present(engine_cache_dir):
    npzs = sorted(engine_cache_dir.glob("*.npz"))
    assert len(npzs) >= 700, f"Expected ≥700 engine .npz, got {len(npzs)}"


def test_csv_engine_pair_consistency(pmemo_annotations_arousal, engine_cache_dir):
    """Most arousal CSV clip ids must have corresponding engine cache."""
    a_ids = {f.stem.split("-")[0] for f in pmemo_annotations_arousal.glob("*-A.csv")}
    cache_ids = {f.stem for f in engine_cache_dir.glob("*.npz")}
    common = a_ids & cache_ids
    assert len(common) >= 700, f"Only {len(common)} clips have both arousal CSV + npz"


def test_pooled_csv_exists(pooled_csv):
    assert pooled_csv.exists(), f"pooled.csv not found: {pooled_csv}"
