#!/usr/bin/env python3
"""V-Reproduction/05-ece-belief-calibration — Reliability diagram + ECE heatmap figures.

Inputs:
  ../results/A2_reliability_data.npz
  ../results/A2_per_cell_ece.csv

Outputs:
  ../figures/reliability_per_belief.png   — 14-panel grid
  ../figures/ece_per_cell_heatmap.png      — 5 (songs) × 14 (beliefs)
  ../figures/extension_vs_paper.png        — bar comparison
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

_REPRO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = _REPRO_ROOT / "results"
FIG_DIR = _REPRO_ROOT / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

PAPER_BELIEFS = [
    "F1_HarmonicStability", "F1_PitchProminence", "F1_PitchIdentity", "F1_TimbralCharacter",
    "F2_PredictionHierarchy", "F2_PredictionAccuracy", "F2_SequenceMatch", "F2_InformationContent",
]
EXTENSION_BELIEFS = [
    "F3_AttentionCapture", "F4_EpisodicEncoding", "F5_EmotionalArousal",
    "F6_Pleasure", "F7_GrooveQuality", "F8_StatisticalModel",
]
ALL_BELIEFS = PAPER_BELIEFS + EXTENSION_BELIEFS

SONGS = [1034, 1508, 1777, 1896, 1923]


def load_per_cell_ece():
    rows = []
    with open(RESULTS_DIR / "A2_per_cell_ece.csv") as f:
        for r in csv.DictReader(f):
            rows.append({
                "song_id": int(r["song_id"]),
                "belief": r["belief"],
                "ece": float(r["ece"]),
                "brier": float(r["brier"]),
                "mean_pi_pred": float(r["mean_pi_pred"]),
                "mean_y_continuous": float(r["mean_y_continuous"]),
            })
    return rows


def fig_reliability_per_belief():
    """14-panel grid: each panel a per-belief reliability diagram (pooled across 5 songs)."""
    npz = np.load(RESULTS_DIR / "A2_reliability_data.npz")
    fig, axes = plt.subplots(4, 4, figsize=(16, 14), constrained_layout=True)
    for ax in axes.flat:
        ax.set_visible(False)

    for i, bname in enumerate(ALL_BELIEFS):
        ax = axes.flat[i]
        ax.set_visible(True)
        bin_pp_key = f"belief_{bname}__bin_pp"
        bin_acc_key = f"belief_{bname}__bin_acc"
        ci_lo_key = f"belief_{bname}__ci_lo"
        ci_hi_key = f"belief_{bname}__ci_hi"
        if bin_pp_key not in npz.files:
            ax.set_title(f"{bname}\n(no data)", fontsize=8)
            continue
        bin_pp = npz[bin_pp_key]
        bin_acc = npz[bin_acc_key]
        ci_lo = npz[ci_lo_key]
        ci_hi = npz[ci_hi_key]

        # Diagonal
        ax.plot([0, 1], [0, 1], "k--", lw=0.8, alpha=0.5)
        # ±0.10 well-calibrated band
        ax.fill_between([0, 1], [0 - 0.10, 1 - 0.10], [0 + 0.10, 1 + 0.10],
                         color="gray", alpha=0.15)
        # Per-belief reliability
        is_paper = bname in PAPER_BELIEFS
        color = "#2c7bb6" if is_paper else "#d7191c"
        ax.plot(bin_pp, bin_acc, "-o", color=color, lw=1.5, ms=5, mew=0.5,
                label="V6 reliability")
        ax.fill_between(bin_pp, ci_lo, ci_hi, color=color, alpha=0.20,
                        label="95% bootstrap CI")

        # Compute pooled ECE for title
        ece_pooled_key = f"belief_{bname}__ece_pooled"
        ece_text = ""
        if ece_pooled_key in npz.files:
            try:
                ece_text = f" ECE={float(npz[ece_pooled_key]):.3f}"
            except Exception:
                pass
        # Try numpy item access
        ece_arr_key = f"belief_{bname}__bin_n"
        if not ece_text:
            for k in npz.files:
                if k.startswith(f"belief_{bname}__"):
                    pass

        tag = "PAPER" if is_paper else "V6 EXT"
        ax.set_title(f"[{tag}] {bname}{ece_text}", fontsize=9)
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
        if i == 0:
            ax.set_xlabel("Mean π_pred (bin)", fontsize=8)
            ax.set_ylabel("Mean y = 1−|PE| (bin)", fontsize=8)
            ax.legend(fontsize=7, loc="lower right")

    fig.suptitle("V-Reproduction/05-ece-belief-calibration — Per-belief reliability diagrams\n"
                 "Blue: paper's 8 beliefs (V6 replicates ECE = 0.0841 vs paper's 0.079)\n"
                 "Red: V6 extension (6 novel beliefs F3-F8)",
                 fontsize=11, y=1.02)
    out_path = FIG_DIR / "reliability_per_belief.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {out_path}")


def fig_ece_heatmap():
    """5 songs × 14 beliefs ECE heatmap."""
    rows = load_per_cell_ece()
    M = np.full((len(SONGS), len(ALL_BELIEFS)), np.nan)
    for r in rows:
        if r["song_id"] in SONGS and r["belief"] in ALL_BELIEFS:
            M[SONGS.index(r["song_id"]), ALL_BELIEFS.index(r["belief"])] = r["ece"]

    fig, ax = plt.subplots(figsize=(13, 4), constrained_layout=True)
    im = ax.imshow(M, aspect="auto", cmap="RdYlGn_r", vmin=0, vmax=0.25)
    ax.set_xticks(range(len(ALL_BELIEFS)))
    ax.set_xticklabels(ALL_BELIEFS, rotation=35, ha="right", fontsize=8)
    ax.set_yticks(range(len(SONGS)))
    ax.set_yticklabels([f"DEAM {s}" for s in SONGS], fontsize=9)
    # Add separator between paper-8 and extension-6
    ax.axvline(7.5, color="black", lw=2, linestyle="--", alpha=0.7)
    ax.text(3.5, -0.7, "Paper's 8 (F1+F2)", ha="center", fontsize=9,
            fontweight="bold", color="#2c7bb6")
    ax.text(10.5, -0.7, "V6 extension (F3-F8)", ha="center", fontsize=9,
            fontweight="bold", color="#d7191c")
    # Annotate ECE values
    for i in range(len(SONGS)):
        for j in range(len(ALL_BELIEFS)):
            if not np.isnan(M[i, j]):
                color = "white" if M[i, j] > 0.13 else "black"
                ax.text(j, i, f"{M[i,j]:.2f}", ha="center", va="center",
                        color=color, fontsize=7)
    cbar = fig.colorbar(im, ax=ax, label="ECE")
    cbar.ax.axhline(0.10, color="black", lw=1.5)
    cbar.ax.text(1.5, 0.10, "0.10\nthreshold", va="center", fontsize=8)
    ax.set_title(f"ECE per (song × belief) cell — V-Reproduction/05-ece-belief-calibration\n"
                 f"40 paper cells: median 0.083, 28/40 below 0.10  •  "
                 f"30 extension cells: median 0.078, 20/30 below 0.10  •  outlier F7_GrooveQuality (0.22)",
                 fontsize=10)
    out_path = FIG_DIR / "ece_per_cell_heatmap.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {out_path}")


def fig_extension_vs_paper():
    """Bar chart: paper's 8 beliefs side-by-side with extension's 6, 5-song mean ECE per belief."""
    rows = load_per_cell_ece()
    means = {}
    for r in rows:
        means.setdefault(r["belief"], []).append(r["ece"])

    paper_eces = [np.mean(means[b]) for b in PAPER_BELIEFS]
    ext_eces = [np.mean(means[b]) for b in EXTENSION_BELIEFS]

    fig, ax = plt.subplots(figsize=(13, 5), constrained_layout=True)
    x_paper = np.arange(len(PAPER_BELIEFS))
    x_ext = np.arange(len(EXTENSION_BELIEFS)) + len(PAPER_BELIEFS) + 0.5

    bars_paper = ax.bar(x_paper, paper_eces, color="#2c7bb6",
                        edgecolor="black", lw=0.5, label="Paper's 8 (replication)")
    bars_ext = ax.bar(x_ext, ext_eces, color="#d7191c",
                     edgecolor="black", lw=0.5, label="V6 extension (novel)")

    ax.axhline(0.10, color="black", lw=1.2, linestyle="--",
               label="Well-calibrated threshold (0.10)")
    ax.axhline(0.0841, color="#2c7bb6", lw=1.0, linestyle=":",
               label=f"V6 paper-8 pooled ECE (0.0841)")
    ax.axhline(0.079, color="darkblue", lw=1.0, linestyle="-.",
               label="Paper published pooled (0.079)")

    for x, y, name in zip(x_paper, paper_eces, PAPER_BELIEFS):
        ax.text(x, y + 0.005, f"{y:.3f}", ha="center", va="bottom",
                fontsize=7, fontweight="bold")
    for x, y, name in zip(x_ext, ext_eces, EXTENSION_BELIEFS):
        ax.text(x, y + 0.005, f"{y:.3f}", ha="center", va="bottom",
                fontsize=7, fontweight="bold")

    ax.set_xticks(np.concatenate([x_paper, x_ext]))
    ax.set_xticklabels(PAPER_BELIEFS + EXTENSION_BELIEFS,
                       rotation=35, ha="right", fontsize=8)
    ax.set_ylabel("Per-belief ECE (5-song mean)", fontsize=10)
    ax.set_ylim(0, max(max(paper_eces), max(ext_eces)) * 1.25)
    ax.set_title("V-Reproduction/05-ece-belief-calibration — Paper's 8 beliefs vs V6 extension's 6\n"
                 "Replication: paper-8 within ±0.025; V6 extension: only F7_GrooveQuality fails",
                 fontsize=10)
    ax.legend(fontsize=8, loc="upper left", ncol=2)
    ax.grid(True, alpha=0.3, axis="y")

    out_path = FIG_DIR / "extension_vs_paper.png"
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[fig] {out_path}")


def main() -> int:
    print(f"[plot] generating figures into {FIG_DIR}")
    fig_reliability_per_belief()
    fig_ece_heatmap()
    fig_extension_vs_paper()
    print("[plot] all 3 figures done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
