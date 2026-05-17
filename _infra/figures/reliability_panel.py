"""Reliability diagram panel renderer.

Used by Phase 5 ECE belief calibration: one diagonal-vs-observed panel per
belief, arranged in a small-multiples grid. Headless (Agg) backend.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


def render_reliability_panel(
    *,
    beliefs: list[str],
    bin_centers: dict[str, np.ndarray],
    obs_freq: dict[str, np.ndarray],
    output_path: Path | str,
    title: str = "Belief calibration",
    figsize_per: tuple[float, float] = (3.2, 3.0),
) -> None:
    """Render N-panel reliability diagrams (one per belief)."""
    if len(beliefs) == 0:
        raise ValueError("`beliefs` must be a non-empty list.")

    n = len(beliefs)
    # Grid layout: up to 4 columns
    ncols = min(4, n)
    nrows = int(np.ceil(n / ncols))

    fig_w = figsize_per[0] * ncols
    fig_h = figsize_per[1] * nrows + 0.5  # extra for suptitle
    fig, axes = plt.subplots(nrows, ncols, figsize=(fig_w, fig_h), squeeze=False)

    for idx, name in enumerate(beliefs):
        if name not in bin_centers:
            plt.close(fig)
            raise KeyError(f"`bin_centers` missing key for belief '{name}'.")
        if name not in obs_freq:
            plt.close(fig)
            raise KeyError(f"`obs_freq` missing key for belief '{name}'.")

        r, c = divmod(idx, ncols)
        ax = axes[r][c]
        x = np.asarray(bin_centers[name], dtype=float)
        y = np.asarray(obs_freq[name], dtype=float)

        # Reference diagonal y=x
        ax.plot([0.0, 1.0], [0.0, 1.0], color="#888888", linewidth=0.8, linestyle="--")
        # Observed reliability curve
        ax.plot(x, y, color="#2D5DAB", linewidth=1.4, marker="o", markersize=3)
        ax.set_xlim(0.0, 1.0)
        ax.set_ylim(0.0, 1.0)
        ax.set_xlabel(r"$\pi_{\mathrm{pred}}$", fontsize=8)
        ax.set_ylabel("observed", fontsize=8)
        ax.set_title(name, fontsize=9)
        ax.tick_params(labelsize=7)
        ax.set_aspect("equal", adjustable="box")

    # Hide unused axes
    for idx in range(n, nrows * ncols):
        r, c = divmod(idx, ncols)
        axes[r][c].set_visible(False)

    fig.suptitle(title, fontsize=11)
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.96))

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, format="png")
    plt.close(fig)
