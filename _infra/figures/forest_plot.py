"""Forest plot renderer for mechanism × region encoding panels.

Used by Phase 11 mech×region (BH-FDR forest panel). Each (label, point, lo, hi)
becomes a horizontal CI segment with a point marker. Headless backend.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402


def render_forest_plot(
    *,
    pairs: list[tuple[str, float, float, float]],
    output_path: Path | str,
    title: str = "Mechanism × Region",
    sort: bool = True,
    figsize: tuple[float, float] | None = None,
    color: str = "#2D5DAB",
    point_color: str = "#1A1A1A",
    return_label_order: bool = False,
) -> list[str] | None:
    """Render forest plot of (label, point_estimate, ci_lo, ci_hi) rows.

    Returns the list of labels in the rendered top→bottom order if
    `return_label_order` is True; else returns None.
    """
    if len(pairs) == 0:
        raise ValueError("`pairs` must be a non-empty list.")

    rows = list(pairs)
    if sort:
        rows.sort(key=lambda r: r[1], reverse=True)

    # Top→bottom display order = list order; matplotlib's larger-y is up
    n = len(rows)
    # Default figsize: width 6.0", height ~ 0.32" per row + 1.0" padding
    if figsize is None:
        height = max(2.0, 0.32 * n + 1.0)
        figsize = (6.0, height)

    fig, ax = plt.subplots(figsize=figsize)

    # y positions: top of plot = first row → larger y values
    y_positions = list(range(n, 0, -1))
    labels = [r[0] for r in rows]

    for y, (_, pe, lo, hi) in zip(y_positions, rows):
        ax.hlines(y=y, xmin=lo, xmax=hi, color=color, linewidth=1.4)
        ax.plot([pe], [y], marker="o", markersize=4.5, color=point_color, zorder=3)

    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_ylim(0.5, n + 0.5)
    ax.set_xlabel("estimate", fontsize=9)
    ax.set_title(title, fontsize=11)
    ax.tick_params(axis="x", labelsize=8)
    ax.grid(axis="x", linestyle=":", linewidth=0.5, alpha=0.6)

    fig.tight_layout()

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150, format="png")
    plt.close(fig)

    if return_label_order:
        return labels
    return None
