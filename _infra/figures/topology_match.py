"""RAM topology match histogram renderer.

Used by Phase 9 RAM topology: histogram of coordinate distances (mm) with a
vertical threshold line (default 10 mm). Title appends 'N_pass / N_total ≤
T mm'. Headless backend.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402


def render_topology_match(
    *,
    distances_mm: np.ndarray,
    threshold: float = 10.0,
    output_path: Path | str,
    title: str = "RAM topology match",
    bins: int = 20,
    threshold_color: str = "#D55E00",
    histogram_color: str = "#2D5DAB",
) -> None:
    """Histogram of coordinate distances in mm with vertical threshold line."""
    distances_mm = np.asarray(distances_mm, dtype=float).ravel()
    if distances_mm.size == 0:
        raise ValueError("`distances_mm` must be a non-empty array.")

    n_total = int(distances_mm.size)
    n_pass = int(np.sum(distances_mm <= threshold))

    fig, ax = plt.subplots(figsize=(6.0, 4.0))
    ax.hist(
        distances_mm,
        bins=bins,
        color=histogram_color,
        edgecolor="white",
        linewidth=0.5,
        alpha=0.85,
    )
    ax.axvline(
        threshold,
        color=threshold_color,
        linewidth=1.6,
        linestyle="--",
        label=f"threshold = {threshold:g} mm",
    )

    full_title = f"{title}  —  {n_pass}/{n_total} ≤ {threshold:g} mm"
    ax.set_title(full_title, fontsize=11)
    ax.set_xlabel("distance (mm)", fontsize=9)
    ax.set_ylabel("count", fontsize=9)
    ax.tick_params(labelsize=8)
    ax.legend(fontsize=8, loc="upper right", frameon=False)
    ax.grid(axis="y", linestyle=":", linewidth=0.5, alpha=0.6)

    fig.tight_layout()

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, format="png")
    plt.close(fig)
