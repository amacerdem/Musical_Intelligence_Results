"""L2 — TenseMusic per-rater CSVs + engine .npz files present."""
from __future__ import annotations
import pytest


def test_tensemusic_data_dir_exists(tensemusic_data_dir):
    assert tensemusic_data_dir.exists(), f"TenseMusic data dir not found: {tensemusic_data_dir}"


def test_38_csv_files_present(tensemusic_data_dir):
    csvs = sorted(tensemusic_data_dir.glob("*.csv"))
    assert len(csvs) >= 38, f"Expected 38+ CSVs, got {len(csvs)}"


def test_engine_cache_dir_exists(engine_cache_dir):
    assert engine_cache_dir.exists(), f"Engine cache not found: {engine_cache_dir}"


def test_38_engine_npz_present(engine_cache_dir):
    npzs = sorted(engine_cache_dir.glob("*.npz"))
    assert len(npzs) >= 38, f"Expected 38+ engine .npz, got {len(npzs)}"


def test_csv_engine_pair_consistency(tensemusic_data_dir, engine_cache_dir):
    csv_stems = {f.stem for f in tensemusic_data_dir.glob("*.csv")}
    npz_stems = {f.stem for f in engine_cache_dir.glob("*.npz")}
    common = csv_stems & npz_stems
    assert len(common) >= 38, f"Only {len(common)} pieces have both CSV+npz"
