"""Generate 3 visualisation figures from eligibility_audit.csv.

Outputs:
- figures/eligibility_matrix.png  — datasets × criteria heatmap
- figures/alignment_qualified_n_bar.png — per-dataset alignment-qualified N
- figures/exclusion_reasons_pareto.png — Pareto chart of exclusion reasons
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import numpy as np

PHASE_DIR = Path(__file__).resolve().parent.parent
CSV_IN = PHASE_DIR / "results" / "eligibility_audit.csv"
FIG_DIR = PHASE_DIR / "figures"


# Maps for binarising criteria into pass/fail/partial.
AUDIO_PASS = {"yes_in_dataset", "yes_external_DOI"}
TIMING_PASS = {"events_tsv_sub_TR", "recoverable_from_logs"}
MNI_PASS = {"present", "runnable_via_fmriprep"}


def load_rows():
    return list(csv.DictReader(CSV_IN.open()))


def fig_eligibility_matrix(rows):
    """Datasets × {audio, timing, mni, n_align>0} heatmap.

    Cell value: 1.0 = pass (green), 0.5 = partial (yellow), 0.0 = fail (red).
    """
    criteria = ["audio", "timing", "MNI", "N_align>0"]
    data = np.zeros((len(rows), len(criteria)))
    labels = []
    for i, r in enumerate(rows):
        labels.append(r["dataset_id"])
        # Audio
        if r["audio_available"] in AUDIO_PASS:
            data[i, 0] = 1.0
        elif r["audio_available"] == "summary_only":
            data[i, 0] = 0.5
        # Timing
        if r["exact_timing"] in TIMING_PASS:
            data[i, 1] = 1.0
        elif r["exact_timing"] == "events_tsv_TR_only":
            data[i, 1] = 0.5
        # MNI
        if r["mni_derivative"] in MNI_PASS:
            data[i, 2] = 1.0
        elif r["mni_derivative"] == "not_applicable":
            data[i, 2] = 0.5
        # Alignment
        try:
            n_al = int(r["n_alignment_qualified"])
            if n_al >= 1:
                data[i, 3] = 1.0
            elif n_al == 0:
                data[i, 3] = 0.0
            else:  # -1
                data[i, 3] = 0.5
        except ValueError:
            data[i, 3] = 0.0

    fig, ax = plt.subplots(figsize=(6, max(8, len(rows) * 0.22)))
    cmap = plt.get_cmap("RdYlGn")
    im = ax.imshow(data, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax.set_xticks(range(len(criteria)))
    ax.set_xticklabels(criteria, rotation=30, ha="right")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(labels, fontsize=7)
    # Mark MI-compatible row labels in bold
    for i, r in enumerate(rows):
        if r["mi_compatible"] == "True":
            ax.get_yticklabels()[i].set_fontweight("bold")
    ax.set_title("V-fMRI Eligibility Matrix\n(green=pass, yellow=partial/n.a., red=fail)")
    cbar = plt.colorbar(im, ax=ax, fraction=0.04)
    cbar.set_ticks([0.0, 0.5, 1.0])
    cbar.set_ticklabels(["fail", "n/a-partial", "pass"])
    plt.tight_layout()
    out = FIG_DIR / "eligibility_matrix.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def fig_alignment_qualified_n_bar(rows):
    """Per-dataset alignment-qualified N (descending)."""
    # Treat -1 as 0 visually but distinguish via colour
    parsed = []
    for r in rows:
        try:
            n_al = int(r["n_alignment_qualified"])
        except ValueError:
            n_al = 0
        parsed.append((r["dataset_id"], n_al, r["mi_compatible"] == "True"))
    parsed.sort(key=lambda x: (-(x[1] if x[1] >= 0 else -1), x[0]))

    labels = [p[0] for p in parsed]
    n_vals = [max(p[1], 0) for p in parsed]
    compat = [p[2] for p in parsed]
    raw_n = [p[1] for p in parsed]
    colours = [
        "#2ca02c" if c else ("#888888" if n < 0 else "#d62728")
        for c, n in zip(compat, raw_n)
    ]

    fig, ax = plt.subplots(figsize=(7, max(8, len(rows) * 0.2)))
    y_pos = np.arange(len(labels))
    ax.barh(y_pos, n_vals, color=colours)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=7)
    ax.invert_yaxis()
    ax.set_xlabel("alignment-qualified N (capped at $N_{ds}$)")
    ax.set_title(
        "Per-dataset alignment-qualified subject count\n"
        "(green = MI-compatible, red = excluded, grey = unknown / closed-access)"
    )
    # Annotate -1 (unknown) bars
    for i, n in enumerate(raw_n):
        if n < 0:
            ax.text(0.2, i, "unknown", va="center", fontsize=6)
    plt.tight_layout()
    out = FIG_DIR / "alignment_qualified_n_bar.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def fig_exclusion_pareto(rows):
    """Pareto chart of categorical exclusion-reason buckets."""
    buckets = {
        "Closed-access (pharma/PET)": 0,
        "RAM peaks-only legacy": 0,
        "EEG/MEG/iEEG (companion)": 0,
        "Behavioral / audio-only": 0,
        "Path not on disk": 0,
        "Partial download / missing events": 0,
        "TR-only timing": 0,
        "Other": 0,
    }
    for r in rows:
        if r["mi_compatible"] == "True":
            continue
        reason = r["exclusion_reason"]
        if "Closed-access" in reason or "naltrexone" in reason or "summary-only" in reason.lower() or "Subject-level data not deposited" in reason:
            buckets["Closed-access (pharma/PET)"] += 1
        elif "RAM topology" in reason or "peak" in reason:
            buckets["RAM peaks-only legacy"] += 1
        elif "EEG" in reason or "MEG" in reason or "iEEG" in reason or "companion" in reason:
            buckets["EEG/MEG/iEEG (companion)"] += 1
        elif "Behavioral" in reason or "Audio-only" in reason or "MIDI-only" in reason:
            buckets["Behavioral / audio-only"] += 1
        elif "PARTIAL DOWNLOAD" in reason or "events.tsv" in reason:
            buckets["Partial download / missing events"] += 1
        elif "TR-only" in reason or "TR_only" in reason:
            buckets["TR-only timing"] += 1
        elif "Path not on disk" in reason or "not on local disk" in reason:
            buckets["Path not on disk"] += 1
        else:
            buckets["Other"] += 1

    items = sorted(buckets.items(), key=lambda kv: -kv[1])
    items = [it for it in items if it[1] > 0]
    labels = [it[0] for it in items]
    counts = [it[1] for it in items]
    cumulative = np.cumsum(counts) / sum(counts) * 100.0

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.bar(range(len(labels)), counts, color="#1f77b4")
    ax1.set_xticks(range(len(labels)))
    ax1.set_xticklabels(labels, rotation=25, ha="right", fontsize=8)
    ax1.set_ylabel("# datasets", color="#1f77b4")
    ax1.tick_params(axis="y", labelcolor="#1f77b4")

    ax2 = ax1.twinx()
    ax2.plot(range(len(labels)), cumulative, color="#d62728", marker="o")
    ax2.set_ylabel("cumulative %", color="#d62728")
    ax2.tick_params(axis="y", labelcolor="#d62728")
    ax2.set_ylim(0, 105)

    ax1.set_title("Exclusion reasons (Pareto)")
    plt.tight_layout()
    out = FIG_DIR / "exclusion_reasons_pareto.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    a = fig_eligibility_matrix(rows)
    print(f"Wrote {a}")
    b = fig_alignment_qualified_n_bar(rows)
    print(f"Wrote {b}")
    c = fig_exclusion_pareto(rows)
    print(f"Wrote {c}")


if __name__ == "__main__":
    main()
