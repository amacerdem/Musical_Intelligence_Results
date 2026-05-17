"""TDD tests for `figures.reliability_panel` — calibration reliability diagrams."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

_INFRA = Path(__file__).resolve().parent.parent
if str(_INFRA) not in sys.path:
    sys.path.insert(0, str(_INFRA))

from figures.reliability_panel import render_reliability_panel  # noqa: E402


def _toy_panel_data(beliefs: list[str], n_bins: int = 10, seed: int = 1729):
    rng = np.random.default_rng(seed)
    bin_centers: dict[str, np.ndarray] = {}
    obs_freq: dict[str, np.ndarray] = {}
    for name in beliefs:
        centers = np.linspace(0.05, 0.95, n_bins)
        # Approx well-calibrated with a little noise
        obs = np.clip(centers + rng.normal(0, 0.04, n_bins), 0.0, 1.0)
        bin_centers[name] = centers
        obs_freq[name] = obs
    return bin_centers, obs_freq


def test_render_reliability_panel_2_panel_grid_writes_png():
    """Two-belief grid produces a PNG > 1 KB."""
    beliefs = ["B1", "B2"]
    bc, of = _toy_panel_data(beliefs)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "panel.png"
        render_reliability_panel(
            beliefs=beliefs, bin_centers=bc, obs_freq=of, output_path=out
        )
        assert out.exists()
        assert out.stat().st_size > 1024


def test_render_reliability_panel_14_panel_grid_writes_png():
    """14-belief grid (matches Phase 5 ECE expected count)."""
    beliefs = [f"B{i:02d}" for i in range(14)]
    bc, of = _toy_panel_data(beliefs)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "panel14.png"
        render_reliability_panel(
            beliefs=beliefs, bin_centers=bc, obs_freq=of, output_path=out
        )
        assert out.exists()
        assert out.stat().st_size > 1024
        # Verify image parses
        from PIL import Image

        with Image.open(out) as img:
            w, h = img.size
        # Expected dim: should be wide enough for >= 4 columns at 3.2"*150dpi each
        # We don't pin exact pixels, but sanity check shape is "panel-like"
        assert w >= 480 and h >= 300


def test_render_reliability_panel_empty_beliefs_raises():
    """Empty beliefs list must raise ValueError, NOT silently produce empty PNG."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "empty.png"
        with pytest.raises(ValueError):
            render_reliability_panel(
                beliefs=[], bin_centers={}, obs_freq={}, output_path=out
            )


def test_render_reliability_panel_missing_obs_freq_key_raises():
    """If a belief listed has no entry in obs_freq → KeyError."""
    beliefs = ["B1", "B2"]
    bc, of = _toy_panel_data(beliefs)
    del of["B2"]
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "missing.png"
        with pytest.raises(KeyError):
            render_reliability_panel(
                beliefs=beliefs, bin_centers=bc, obs_freq=of, output_path=out
            )


def test_render_reliability_panel_creates_parent_dirs():
    """Parent directories must be created automatically."""
    beliefs = ["B1"]
    bc, of = _toy_panel_data(beliefs)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "nested" / "deeper" / "panel.png"
        render_reliability_panel(
            beliefs=beliefs, bin_centers=bc, obs_freq=of, output_path=out
        )
        assert out.exists()
        assert out.stat().st_size > 1024
