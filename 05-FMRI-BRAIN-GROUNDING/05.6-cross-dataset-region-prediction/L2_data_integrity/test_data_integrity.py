"""L2 — Input data integrity (V-Repro 25/26 CSVs + cycle-17 encoder + MI cache)."""
from __future__ import annotations
from pathlib import Path
import pytest


def test_v_repro_25_inputs(project_root):
    """Required inputs from MI_Results 05.3 (ds002725)."""
    base = project_root / "05-FMRI-BRAIN-GROUNDING" / "05.3-ds002725-region-ceiling-N17"
    assert (base / "data" / "stage3_ceiling_ds002725.csv").exists()
    assert (base / "data" / "stage4_encoder_ds002725.csv").exists()


def test_v_repro_26_inputs(project_root):
    """Required inputs from MI_Results 05.5 (ds003720)."""
    base = project_root / "05-FMRI-BRAIN-GROUNDING" / "05.5-ds003720-region-ceiling-N4"
    assert (base / "data" / "05.5_ds003720_per_region_ceiling.csv").exists()


def test_cycle17_encoder_r_csv(project_root):
    """Cycle-17 per-subject per-region encoder r."""
    csv = project_root / "datasets" / "paper-anchors" / "voxelwise-encoding" / "per_subject_per_region_r.csv"
    assert csv.exists(), f"Cycle-17 encoder CSV not found: {csv}"


def test_mi_per_frame_cache_ds002725(project_root):
    d = project_root / "engine_outputs" / "neuroimaging" / "ds002725" / "per_frame"
    assert d.exists()
    n = len(list(d.glob("*.npz")))
    assert n >= 200, f"Expected ≥200 ds002725 MI clip files, got {n}"


def test_mi_per_frame_cache_ds003720(project_root):
    d = project_root / "engine_outputs" / "neuroimaging" / "ds003720" / "per_frame"
    assert d.exists()
    n = len(list(d.glob("*.npz")))
    assert n >= 700, f"Expected ≥700 ds003720 MI clip files, got {n}"
