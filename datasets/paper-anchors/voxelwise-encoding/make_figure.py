#!/usr/bin/env python3
"""
make_figure.py — first-pass encoding result figure.

Bar chart: top-5% voxel mean r per (subject × encoder).
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

BASE = Path("<PAPER_TIME_SCIENCE_ROOT>/Science/Bold-fMRI")
OUT = BASE / "ds003720" / "06_encoding"
FIG = BASE / "ds003720" / "09_reports" / "figures"
FIG.mkdir(parents=True, exist_ok=True)


def main():
    df = pd.read_csv(OUT / "results_voxel_top5pct.csv")
    subs = sorted(df["subject"].unique())
    encs = ["mi_ram_26d", "mert_768d", "random_26d", "random_768d", "mi_naive_26d"]
    colors = {"mi_ram_26d": "#2a7de1", "mert_768d": "#e17a2a", "random_26d": "#c0c0c0",
              "random_768d": "#a0a0a0", "mi_naive_26d": "#6aadf5"}
    n_sub = len(subs)
    n_enc = len(encs)
    width = 0.15
    x = np.arange(n_sub)

    fig, ax = plt.subplots(figsize=(10, 5))
    for i, enc in enumerate(encs):
        vals = [df[(df["subject"] == s) & (df["encoder"] == enc)]["top5pct_mean_r"].iloc[0] for s in subs]
        ax.bar(x + (i - n_enc/2 + 0.5) * width, vals, width, label=enc, color=colors[enc])
    ax.set_xticks(x)
    ax.set_xticklabels(subs)
    ax.set_ylabel("top-5% voxel mean Pearson r")
    ax.set_title("ds003720 first-pass encoding: MI vs MERT vs Random\nridge(α=100), 5-fold LOSO, seed 20260424")
    ax.axhline(0, color="k", lw=0.5)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG / "per_region_r_bars.pdf", dpi=150)
    plt.savefig(FIG / "per_region_r_bars.png", dpi=150)
    print(f"[fig] saved {FIG}/per_region_r_bars.pdf + .png")


if __name__ == "__main__":
    main()
