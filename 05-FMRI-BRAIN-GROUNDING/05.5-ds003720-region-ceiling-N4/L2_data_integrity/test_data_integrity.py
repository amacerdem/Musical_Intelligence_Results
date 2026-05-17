"""L2 — Cycle-17 ckpt_bold + cycle-17 encoder r CSV present."""
from __future__ import annotations
import numpy as np
import pytest

COHORT_N4 = ["sub-001", "sub-003", "sub-004", "sub-005"]


def test_ckpt_bold_dir_exists(ckpt_bold_dir):
    assert ckpt_bold_dir.exists(), f"ckpt_bold dir not found: {ckpt_bold_dir}"


def test_per_subject_runs_complete(ckpt_bold_dir):
    """Each subject must have 15 runs × (410, 26) BOLD."""
    for sub in COHORT_N4:
        files = sorted(ckpt_bold_dir.glob(f"{sub}_*.npy"))
        assert len(files) == 15, f"{sub}: expected 15 runs, got {len(files)}"


def test_bold_shape_per_run(ckpt_bold_dir):
    for sub in COHORT_N4:
        f0 = sorted(ckpt_bold_dir.glob(f"{sub}_*.npy"))[0]
        a = np.load(f0)
        assert a.shape == (410, 26), f"{sub}: bad shape {a.shape}"


def test_per_subject_encoder_csv(per_subject_per_region_csv):
    assert per_subject_per_region_csv.exists()
