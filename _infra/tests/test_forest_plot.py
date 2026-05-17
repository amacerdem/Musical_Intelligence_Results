"""TDD tests for `figures.forest_plot` — mech × region forest plot."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

_INFRA = Path(__file__).resolve().parent.parent
if str(_INFRA) not in sys.path:
    sys.path.insert(0, str(_INFRA))

from figures.forest_plot import render_forest_plot  # noqa: E402


def _toy_pairs(n: int, seed: int = 1729) -> list[tuple[str, float, float, float]]:
    rng = np.random.default_rng(seed)
    out: list[tuple[str, float, float, float]] = []
    for i in range(n):
        pe = rng.uniform(0.1, 0.9)
        half = rng.uniform(0.02, 0.12)
        out.append((f"mech{i:02d}×region{i:02d}", float(pe), float(pe - half), float(pe + half)))
    return out


def test_render_forest_plot_5_pairs_writes_png():
    """5-pair forest plot produces a >1 KB PNG."""
    pairs = _toy_pairs(5)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "forest5.png"
        render_forest_plot(pairs=pairs, output_path=out)
        assert out.exists()
        assert out.stat().st_size > 1024


def test_render_forest_plot_22_pairs_height_scales_with_N():
    """22-pair plot must be taller than 5-pair plot (height scales with N)."""
    pairs5 = _toy_pairs(5)
    pairs22 = _toy_pairs(22)
    with tempfile.TemporaryDirectory() as tmp:
        out5 = Path(tmp) / "forest5.png"
        out22 = Path(tmp) / "forest22.png"
        render_forest_plot(pairs=pairs5, output_path=out5)
        render_forest_plot(pairs=pairs22, output_path=out22)
        assert out22.stat().st_size > 1024
        with Image.open(out5) as im5, Image.open(out22) as im22:
            _, h5 = im5.size
            _, h22 = im22.size
        assert h22 > h5, f"Expected 22-row plot taller than 5-row, got {h22} <= {h5}"


def test_render_forest_plot_sort_false_preserves_input_order():
    """When sort=False, the y-axis labels must match input order top-to-bottom.

    Top of forest plot = first input row (i.e. labels read top→bottom).
    """
    # Use distinctly-ordered point estimates so a sorted version would differ
    pairs: list[tuple[str, float, float, float]] = [
        ("LOW", 0.10, 0.05, 0.15),
        ("MID", 0.50, 0.45, 0.55),
        ("HIGH", 0.90, 0.85, 0.95),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "forest_unsorted.png"
        labels = render_forest_plot(
            pairs=pairs, output_path=out, sort=False, return_label_order=True
        )
        # First label (top of plot) must be the first input row
        assert labels[0] == "LOW"
        assert labels[-1] == "HIGH"


def test_render_forest_plot_sort_true_orders_by_estimate_descending():
    """sort=True puts the largest point estimate at the top."""
    pairs: list[tuple[str, float, float, float]] = [
        ("LOW", 0.10, 0.05, 0.15),
        ("MID", 0.50, 0.45, 0.55),
        ("HIGH", 0.90, 0.85, 0.95),
    ]
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "forest_sorted.png"
        labels = render_forest_plot(
            pairs=pairs, output_path=out, sort=True, return_label_order=True
        )
        assert labels[0] == "HIGH"
        assert labels[-1] == "LOW"


def test_render_forest_plot_empty_pairs_raises():
    """Empty pairs list must raise ValueError."""
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "empty.png"
        with pytest.raises(ValueError):
            render_forest_plot(pairs=[], output_path=out)


def test_render_forest_plot_creates_parent_dirs():
    """Parent directories must be created automatically."""
    pairs = _toy_pairs(3)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "nested" / "deeper" / "forest.png"
        render_forest_plot(pairs=pairs, output_path=out)
        assert out.exists()
