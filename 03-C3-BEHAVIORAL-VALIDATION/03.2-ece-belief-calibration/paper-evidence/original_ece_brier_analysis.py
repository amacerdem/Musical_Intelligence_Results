#!/usr/bin/env python3
"""T-R3-08 Phase B — ECE + Brier post-processing on captured belief traces.

Input:  computing-phase/T-R3-08/belief_traces_T-R3-08.npz
        (saved by compute_ece_brier.py; keys = "{sid}__{belief}__{field}",
        field ∈ {obs, pred, pe, pi_obs, pi_pred, gain, posterior})

Procedure (per belief, pooled across 5 songs):
    1. Drop warm-up frames 0..15 (PRECISION_WINDOW=16; pi_pred is the
       default 0.5 floor before the PE buffer fills).
    2. Define outcome y_t = 1 − clip(|PE_t|, 0, 1) ∈ [0, 1].
       High y = small PE = well-predicted frame → the directly
       comparable proxy to declared pi_pred (confidence).
    3. Equal-frequency 10-bin pi_pred binning.
       ECE = Σ_bin |mean(pi_pred)_bin − mean(y)_bin| × (n_bin / n_total).
    4. Brier = mean((pi_pred − y)²).
    5. Baselines:
         - Uniform:   π = 0.5 for all frames.
         - Marginal:  π = mean(y) pooled across belief's frames.
    6. Reliability curve per belief (PNG under figures/).

Outputs:
    computing-phase/T-R3-08/ece_result.json
    computing-phase/T-R3-08/ece_brier_summary.md
    computing-phase/T-R3-08/figures/reliability_<belief>.png
    computing-phase/T-R3-08/figures/reliability_pooled.png
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Dict, List

import numpy as np

HERE = Path(__file__).resolve().parent
NPZ_PATH = HERE / "belief_traces_T-R3-08.npz"
OUT_JSON = HERE / "ece_result.json"
OUT_MD = HERE / "ece_brier_summary.md"
FIG_DIR = HERE / "figures"
FIG_DIR.mkdir(exist_ok=True)

PRECISION_WINDOW = 16
N_BINS = 10

BELIEF_ORDER = [
    "harmonic_stability",
    "pitch_prominence",
    "pitch_identity",
    "timbral_character",
    "prediction_hierarchy",
    "prediction_accuracy",
    "sequence_match",
    "information_content",
]


def equal_frequency_bins(x: np.ndarray, n_bins: int = N_BINS) -> np.ndarray:
    """Return integer bin assignment 0..n_bins-1 using equal-frequency edges."""
    quantiles = np.linspace(0, 1, n_bins + 1)
    edges = np.quantile(x, quantiles)
    # strict-monotonize to handle ties
    edges = np.maximum.accumulate(edges)
    edges[0] -= 1e-9
    edges[-1] += 1e-9
    return np.clip(np.searchsorted(edges, x, side="right") - 1, 0, n_bins - 1)


def compute_ece(conf: np.ndarray, y: np.ndarray, n_bins: int = N_BINS):
    """Equal-frequency 10-bin ECE = Σ_bin |mean(conf) − mean(y)| × w_bin."""
    bins = equal_frequency_bins(conf, n_bins)
    n = len(conf)
    ece = 0.0
    bin_table = []
    for b in range(n_bins):
        mask = bins == b
        k = int(mask.sum())
        if k == 0:
            bin_table.append(dict(bin=b, n=0, mean_conf=None, mean_y=None, gap=None))
            continue
        mc = float(conf[mask].mean())
        my = float(y[mask].mean())
        gap = abs(mc - my)
        ece += gap * (k / n)
        bin_table.append(dict(bin=b, n=k, mean_conf=mc, mean_y=my, gap=gap))
    return float(ece), bin_table


def compute_brier(conf: np.ndarray, y: np.ndarray) -> float:
    return float(np.mean((conf - y) ** 2))


def load_traces(npz_path: Path) -> Dict[int, Dict[str, Dict[str, np.ndarray]]]:
    data = np.load(npz_path)
    out: Dict[int, Dict[str, Dict[str, np.ndarray]]] = {}
    for k in data.files:
        sid_s, belief, field = k.split("__")
        sid = int(sid_s)
        out.setdefault(sid, {}).setdefault(belief, {})[field] = data[k]
    return out


def reliability_plot(conf: np.ndarray, y: np.ndarray, title: str, path: Path, ece: float, brier: float):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    bins = equal_frequency_bins(conf, N_BINS)
    xs, ys, ns = [], [], []
    for b in range(N_BINS):
        mask = bins == b
        if mask.sum() == 0:
            continue
        xs.append(conf[mask].mean())
        ys.append(y[mask].mean())
        ns.append(int(mask.sum()))

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot([0, 1], [0, 1], ls="--", c="gray", lw=1, label="perfect calibration")
    ax.plot(xs, ys, "o-", c="tab:blue", label=f"observed (ECE={ece:.3f})")
    ax.set_xlabel("reported confidence  π_pred (bin mean)")
    ax.set_ylabel("empirical outcome   y = 1 − |PE|  (bin mean)")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title(f"{title}\nECE={ece:.3f}  Brier={brier:.3f}  n={len(conf)}")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def main() -> int:
    print(f"Loading traces from {NPZ_PATH.name} ...", flush=True)
    traces = load_traces(NPZ_PATH)
    song_ids = sorted(traces.keys())
    print(f"  {len(song_ids)} songs: {song_ids}", flush=True)

    per_belief: Dict[str, dict] = {}
    pooled_conf: List[np.ndarray] = []
    pooled_y: List[np.ndarray] = []

    for belief in BELIEF_ORDER:
        conf_parts, y_parts = [], []
        warmup_dropped = 0
        total_frames = 0
        for sid in song_ids:
            b = traces[sid][belief]
            pi_pred = np.asarray(b["pi_pred"], dtype=np.float64).ravel()
            pe = np.asarray(b["pe"], dtype=np.float64).ravel()
            T = len(pi_pred)
            total_frames += T
            if T > PRECISION_WINDOW:
                pi_pred = pi_pred[PRECISION_WINDOW:]
                pe = pe[PRECISION_WINDOW:]
                warmup_dropped += PRECISION_WINDOW
            y = 1.0 - np.clip(np.abs(pe), 0.0, 1.0)
            conf_parts.append(pi_pred)
            y_parts.append(y)
        conf = np.concatenate(conf_parts)
        y = np.concatenate(y_parts)

        ece, bin_table = compute_ece(conf, y)
        brier = compute_brier(conf, y)

        # Baselines
        marginal = np.full_like(conf, y.mean())
        uniform = np.full_like(conf, 0.5)
        brier_marginal = compute_brier(marginal, y)
        brier_uniform = compute_brier(uniform, y)
        ece_marginal, _ = compute_ece(marginal, y)
        ece_uniform, _ = compute_ece(uniform, y)

        # Reliability plot
        fig_path = FIG_DIR / f"reliability_{belief}.png"
        reliability_plot(conf, y, title=f"T-R3-08 calibration — {belief}", path=fig_path, ece=ece, brier=brier)

        per_belief[belief] = {
            "n_frames_post_warmup": int(len(conf)),
            "n_frames_total": total_frames,
            "warmup_dropped": warmup_dropped,
            "mean_pi_pred": float(conf.mean()),
            "std_pi_pred": float(conf.std()),
            "mean_y": float(y.mean()),
            "std_y": float(y.std()),
            "mean_abs_pe": float((1.0 - y).mean()),
            "ece": ece,
            "brier": brier,
            "baselines": {
                "marginal": {"ece": ece_marginal, "brier": brier_marginal},
                "uniform":  {"ece": ece_uniform,  "brier": brier_uniform},
            },
            "bin_table": bin_table,
            "reliability_fig": str(fig_path.relative_to(HERE)),
        }
        pooled_conf.append(conf)
        pooled_y.append(y)
        print(f"  {belief:22s} n={len(conf):7d}  ECE={ece:.3f}  Brier={brier:.3f}", flush=True)

    # Pooled across all 8 beliefs
    p_conf = np.concatenate(pooled_conf)
    p_y = np.concatenate(pooled_y)
    pooled_ece, _ = compute_ece(p_conf, p_y)
    pooled_brier = compute_brier(p_conf, p_y)
    reliability_plot(p_conf, p_y, title="T-R3-08 calibration — pooled (8 beliefs × 5 songs)",
                     path=FIG_DIR / "reliability_pooled.png",
                     ece=pooled_ece, brier=pooled_brier)

    result = {
        "meta": {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "songs": song_ids,
            "n_songs": len(song_ids),
            "n_beliefs": len(BELIEF_ORDER),
            "precision_window": PRECISION_WINDOW,
            "n_bins": N_BINS,
            "deam_selection_seed": 42,
            "deam_selection_filter": "song_id > 1000 (held-out from F5 N=200 calibration)",
        },
        "per_belief": per_belief,
        "pooled": {
            "n_frames": int(len(p_conf)),
            "mean_pi_pred": float(p_conf.mean()),
            "mean_y": float(p_y.mean()),
            "ece": pooled_ece,
            "brier": pooled_brier,
        },
    }

    with open(OUT_JSON, "w") as fh:
        json.dump(result, fh, indent=2)
    print(f"Wrote {OUT_JSON.name}", flush=True)

    # Markdown summary
    lines = []
    lines.append("# T-R3-08 Phase B — ECE + Brier Summary")
    lines.append("")
    lines.append(f"**Generated:** {result['meta']['timestamp']}")
    lines.append(f"**Songs:** {song_ids} (DEAM, seed=42, id>1000)")
    lines.append(f"**Warm-up frames dropped per song:** {PRECISION_WINDOW}")
    lines.append(f"**Bins:** {N_BINS} equal-frequency")
    lines.append("")
    lines.append("## Per-belief calibration")
    lines.append("")
    lines.append("| Belief | N (post-warmup) | mean π_pred | mean y | **ECE** | Brier | ECE (marginal) | ECE (uniform) |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for b in BELIEF_ORDER:
        r = per_belief[b]
        lines.append(
            f"| {b} | {r['n_frames_post_warmup']:,} | {r['mean_pi_pred']:.3f} | {r['mean_y']:.3f} | "
            f"**{r['ece']:.3f}** | {r['brier']:.3f} | {r['baselines']['marginal']['ece']:.3f} | "
            f"{r['baselines']['uniform']['ece']:.3f} |"
        )
    lines.append("")
    lines.append("## Pooled (8 beliefs × 5 songs)")
    lines.append("")
    lines.append(f"- **Pooled ECE:** {pooled_ece:.3f}")
    lines.append(f"- **Pooled Brier:** {pooled_brier:.3f}")
    lines.append(f"- **N frames pooled:** {len(p_conf):,}")
    lines.append(f"- **mean π_pred (pooled):** {p_conf.mean():.3f}")
    lines.append(f"- **mean y (pooled):** {p_y.mean():.3f}")
    lines.append("")
    lines.append("## Verdict against Q-R3-08 thresholds")
    lines.append("")
    lines.append("- ECE < 0.10  → CLOSED (Bayesian label defensible)")
    lines.append("- 0.10 ≤ ECE < 0.20 → CLOSED-AT-RUNG-3 (softened language)")
    lines.append("- ECE ≥ 0.20 → HONEST-CONCESSION (GT-0041 relabel)")
    lines.append("")
    if pooled_ece < 0.10:
        verdict = "CLOSED"
    elif pooled_ece < 0.20:
        verdict = "CLOSED-AT-RUNG-3"
    else:
        verdict = "HONEST-CONCESSION"
    lines.append(f"**Pooled-ECE verdict:** {verdict}")
    lines.append("")
    with open(OUT_MD, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"Wrote {OUT_MD.name}", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
