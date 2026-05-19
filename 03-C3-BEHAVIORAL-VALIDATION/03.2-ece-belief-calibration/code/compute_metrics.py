#!/usr/bin/env python3
"""V6 A2 — Compute pre-registered metrics on extracted belief traces.

Inputs:  Science/V6/results/A2_traces/song_{ID}.npz × 5
Outputs:
  - Science/V6/results/A2_per_cell_ece.csv    — 40 cells with ECE
  - Science/V6/results/A2_circular_null.csv   — 10K-perm null per cell + pooled
  - Science/V6/results/A2_brier_decomp.csv    — per-cell Brier components
  - Science/V6/results/A2_reliability_data.npz — bin-level data for reliability diagrams
  - Science/V6/results/A2_summary.json        — headline numbers + pass/fail

Tests (frozen in V6/01-pre-registration.md §A2):
  T1: per-cell ECE breakdown (40 cells)
  T2: reliability diagrams with 1K bootstrap CIs (per-belief)
  T3: circular-shift permutation null within song (10K perms)
  T4: Brier decomposition (reliability + resolution + uncertainty)

Pass criteria (all three):
  P1: median per-cell ECE < 0.10
  P2: pooled ECE < 5th percentile of permutation null
  P3: pooled reliability/uncertainty < 1.0
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

# V-Reproduction layout: this file lives at 03-C3-BEHAVIORAL-VALIDATION/03.2-ece-belief-calibration/code/
_REPRO_ROOT = Path(__file__).resolve().parents[1]  # 03-C3-BEHAVIORAL-VALIDATION/03.2-ece-belief-calibration/
TRACES_DIR = _REPRO_ROOT / "results/traces"
RESULTS_DIR = _REPRO_ROOT / "results"

SEED = 2026050502  # frozen in pre-reg §5
N_BOOTSTRAP = 1000
N_PERMUTATIONS = 10_000
ECE_THRESHOLD = 0.10
N_BINS = 10
HELD_OUT_SONG_IDS = [1034, 1508, 1777, 1896, 1923]

# Paper's 8 beliefs (V2/T-R3-08) — these reproduce paper's ECE = 0.079
PAPER_BELIEF_NAMES = {
    "F1_HarmonicStability", "F1_PitchProminence", "F1_PitchIdentity", "F1_TimbralCharacter",
    "F2_PredictionHierarchy", "F2_PredictionAccuracy", "F2_SequenceMatch", "F2_InformationContent",
}


def equal_mass_ece(pi_pred: np.ndarray, y_continuous: np.ndarray, n_bins: int = N_BINS) -> Tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    """ECE with equal-mass binning. Returns (ece, bin_pp, bin_acc, bin_n)."""
    n = len(pi_pred)
    if n < n_bins:
        return float("nan"), np.zeros(n_bins), np.zeros(n_bins), np.zeros(n_bins)
    sorted_idx = np.argsort(pi_pred)
    bin_edges = np.linspace(0, n, n_bins + 1).astype(int)
    bin_pp = np.zeros(n_bins)
    bin_acc = np.zeros(n_bins)
    bin_n = np.zeros(n_bins)
    for i in range(n_bins):
        idx = sorted_idx[bin_edges[i]:bin_edges[i+1]]
        if len(idx) == 0:
            continue
        bin_pp[i] = pi_pred[idx].mean()
        bin_acc[i] = y_continuous[idx].mean()
        bin_n[i] = len(idx)
    ece = float(np.sum((bin_n / n) * np.abs(bin_pp - bin_acc)))
    return ece, bin_pp, bin_acc, bin_n


def brier_decomposition(pi_pred: np.ndarray, y_continuous: np.ndarray, n_bins: int = N_BINS) -> Dict[str, float]:
    """Murphy 1973: Brier = reliability − resolution + uncertainty."""
    n = len(pi_pred)
    obar = float(y_continuous.mean())  # base rate
    uncertainty = obar * (1 - obar)  # variance of o
    sorted_idx = np.argsort(pi_pred)
    bin_edges = np.linspace(0, n, n_bins + 1).astype(int)
    reliability = 0.0
    resolution = 0.0
    for i in range(n_bins):
        idx = sorted_idx[bin_edges[i]:bin_edges[i+1]]
        if len(idx) == 0:
            continue
        nk = len(idx)
        f_k = pi_pred[idx].mean()
        o_k = y_continuous[idx].mean()
        reliability += (nk / n) * (f_k - o_k) ** 2
        resolution += (nk / n) * (o_k - obar) ** 2
    brier = float(np.mean((pi_pred - y_continuous) ** 2))
    return {
        "brier": brier,
        "reliability": reliability,
        "resolution": resolution,
        "uncertainty": uncertainty,
        "rel_minus_res_plus_unc": reliability - resolution + uncertainty,  # should ≈ brier
    }


def circular_shift_null(pi_pred: np.ndarray, y_continuous: np.ndarray, n_perms: int, rng: np.random.Generator) -> np.ndarray:
    """Circular-shift permutation null on pi_pred labels (within-song)."""
    n = len(pi_pred)
    null_eces = np.zeros(n_perms)
    for i in range(n_perms):
        shift = int(rng.integers(1, n))
        shifted_pp = np.roll(pi_pred, shift)
        ece, _, _, _ = equal_mass_ece(shifted_pp, y_continuous)
        null_eces[i] = ece
    return null_eces


def main() -> int:
    rng = np.random.default_rng(SEED)

    # ── 1. Load all traces ────────────────────────────────────────
    print(f"[A2-metrics] loading 5 song traces from {TRACES_DIR}")
    cells: List[Dict] = []  # 40 cells
    for sid in HELD_OUT_SONG_IDS:
        path = TRACES_DIR / f"song_{sid}.npz"
        npz = np.load(path)
        # Recover belief names from key prefixes
        belief_keys = sorted(set(k.split("__")[0] for k in npz.files))
        for bkey in belief_keys:
            cells.append({
                "song_id": sid,
                "belief": bkey,
                "pi_pred": npz[f"{bkey}__pi_pred"],
                "y_continuous": npz[f"{bkey}__y_continuous"],
                "pe": npz[f"{bkey}__pe"],
            })
        npz.close()
    paper_cells = [c for c in cells if c["belief"] in PAPER_BELIEF_NAMES]
    extension_cells = [c for c in cells if c["belief"] not in PAPER_BELIEF_NAMES]
    print(f"[A2-metrics]   loaded {len(cells)} cells: {len(paper_cells)} paper-set + {len(extension_cells)} extension-set")
    assert len(paper_cells) == 40, f"Expected 40 paper cells, got {len(paper_cells)}"
    assert len(extension_cells) == 30, f"Expected 30 extension cells, got {len(extension_cells)}"

    # ── 2. Per-cell ECE + Brier ────────────────────────────────────
    print(f"[A2-metrics] T1+T4: per-cell ECE + Brier decomposition...")
    per_cell_rows = []
    bin_data = {}  # for reliability diagrams
    for c in cells:
        ece, bin_pp, bin_acc, bin_n = equal_mass_ece(c["pi_pred"], c["y_continuous"])
        brier = brier_decomposition(c["pi_pred"], c["y_continuous"])
        per_cell_rows.append({
            "song_id": c["song_id"],
            "belief": c["belief"],
            "n_frames": int(len(c["pi_pred"])),
            "mean_pi_pred": float(c["pi_pred"].mean()),
            "mean_y_continuous": float(c["y_continuous"].mean()),
            "mean_abs_pe": float(np.abs(c["pe"]).mean()),
            "ece": ece,
            "brier": brier["brier"],
            "reliability": brier["reliability"],
            "resolution": brier["resolution"],
            "uncertainty": brier["uncertainty"],
            "rel_over_unc": brier["reliability"] / max(brier["uncertainty"], 1e-9),
        })
        bin_data[f"{c['song_id']}_{c['belief']}_bin_pp"] = bin_pp
        bin_data[f"{c['song_id']}_{c['belief']}_bin_acc"] = bin_acc
        bin_data[f"{c['song_id']}_{c['belief']}_bin_n"] = bin_n

    # Pooled ECE — TWO pools: paper's 8 (replication of 0.079) + extension's 6 (V6 novel)
    paper_pp = np.concatenate([c["pi_pred"] for c in paper_cells])
    paper_y = np.concatenate([c["y_continuous"] for c in paper_cells])
    paper_pooled_ece, _, _, _ = equal_mass_ece(paper_pp, paper_y)
    paper_pooled_brier = brier_decomposition(paper_pp, paper_y)

    ext_pp = np.concatenate([c["pi_pred"] for c in extension_cells])
    ext_y = np.concatenate([c["y_continuous"] for c in extension_cells])
    ext_pooled_ece, _, _, _ = equal_mass_ece(ext_pp, ext_y)
    ext_pooled_brier = brier_decomposition(ext_pp, ext_y)

    # Use paper-pool for null/composite; extension reported separately
    all_pp = paper_pp
    all_acc = paper_y
    pooled_ece = paper_pooled_ece
    pooled_brier = paper_pooled_brier

    # ── 3. Per-belief reliability diagrams + 1K bootstrap CIs ──────
    print(f"[A2-metrics] T2: reliability diagrams + 1K bootstrap CIs (per-belief, songs as blocks)...")
    belief_names = sorted(set(c["belief"] for c in cells))
    reliability_diagrams: Dict[str, Dict] = {}
    for bname in belief_names:
        belief_cells = [c for c in cells if c["belief"] == bname]
        # Pool across 5 songs for this belief
        bb_pp = np.concatenate([c["pi_pred"] for c in belief_cells])
        bb_acc = np.concatenate([c["y_continuous"] for c in belief_cells])
        ece_pooled, bin_pp, bin_acc, bin_n = equal_mass_ece(bb_pp, bb_acc)
        # Bootstrap CIs: resample songs (5) with replacement, recompute bin_acc
        boot_bin_acc = np.zeros((N_BOOTSTRAP, N_BINS))
        for b in range(N_BOOTSTRAP):
            song_idx = rng.integers(0, len(belief_cells), size=len(belief_cells))
            boot_pp = np.concatenate([belief_cells[i]["pi_pred"] for i in song_idx])
            boot_acc = np.concatenate([belief_cells[i]["y_continuous"] for i in song_idx])
            _, _, ba, _ = equal_mass_ece(boot_pp, boot_acc)
            boot_bin_acc[b] = ba
        ci_lo = np.percentile(boot_bin_acc, 2.5, axis=0)
        ci_hi = np.percentile(boot_bin_acc, 97.5, axis=0)
        reliability_diagrams[bname] = {
            "bin_pp": bin_pp,
            "bin_acc": bin_acc,
            "bin_n": bin_n,
            "ci_lo": ci_lo,
            "ci_hi": ci_hi,
            "ece_pooled": ece_pooled,
            "n_total": len(bb_pp),
        }
        print(f"[A2-metrics]   {bname:30s}: pooled ECE={ece_pooled:.4f}, n={len(bb_pp)}")

    # ── 4. Circular-shift permutation null (per cell + pooled) ─────
    print(f"[A2-metrics] T3: circular-shift null within song (10K perms × 40 cells)...")
    null_summary = []
    for i, c in enumerate(cells):
        null = circular_shift_null(c["pi_pred"], c["y_continuous"], N_PERMUTATIONS, rng)
        observed_ece = per_cell_rows[i]["ece"]
        percentile = float((null < observed_ece).mean() * 100)  # what % of null is BELOW observed
        null_summary.append({
            "song_id": c["song_id"],
            "belief": c["belief"],
            "observed_ece": observed_ece,
            "null_mean": float(null.mean()),
            "null_5th": float(np.percentile(null, 5)),
            "null_95th": float(np.percentile(null, 95)),
            "percentile_of_observed": percentile,
        })
        if i % 10 == 0:
            print(f"[A2-metrics]   cell {i+1}/{len(cells)}: {c['song_id']} {c['belief']}, "
                  f"obs={observed_ece:.4f}, null_5th={np.percentile(null, 5):.4f}, "
                  f"pct={percentile:.1f}")

    # Pooled circular-shift null on paper's 8 beliefs only (composite)
    print(f"[A2-metrics]   pooled null on paper-8 (composite)...")
    pooled_null = np.zeros(N_PERMUTATIONS)
    for i in range(N_PERMUTATIONS):
        shifted_chunks = []
        for c in paper_cells:
            n = len(c["pi_pred"])
            shift = int(rng.integers(1, n))
            shifted_chunks.append(np.roll(c["pi_pred"], shift))
        shifted_pp = np.concatenate(shifted_chunks)
        ece, _, _, _ = equal_mass_ece(shifted_pp, all_acc)
        pooled_null[i] = ece
    pooled_null_5th = float(np.percentile(pooled_null, 5))
    pooled_pct = float((pooled_null < pooled_ece).mean() * 100)

    # ── 5. Pass criteria — paper's 8 beliefs only (replication target) ──
    paper_eces = [r["ece"] for r in per_cell_rows if r["belief"] in PAPER_BELIEF_NAMES]
    extension_eces = [r["ece"] for r in per_cell_rows if r["belief"] not in PAPER_BELIEF_NAMES]
    median_ece = float(np.median(paper_eces))
    iqr_ece = (float(np.percentile(paper_eces, 25)),
               float(np.percentile(paper_eces, 75)))
    max_ece = float(max(paper_eces))
    ext_median_ece = float(np.median(extension_eces))
    ext_max_ece = float(max(extension_eces))
    rel_over_unc = pooled_brier["reliability"] / max(pooled_brier["uncertainty"], 1e-9)

    p1_median_below_10 = median_ece < 0.10
    p2_pooled_below_5th = pooled_ece < pooled_null_5th
    p3_rel_below_unc = rel_over_unc < 1.0
    composite_pass = p1_median_below_10 and p2_pooled_below_5th and p3_rel_below_unc

    summary = {
        "paper_8_replication": {
            "pooled_ece": pooled_ece,
            "pooled_brier": pooled_brier,
            "median_per_cell_ece": median_ece,
            "iqr_per_cell_ece": list(iqr_ece),
            "max_per_cell_ece": max_ece,
            "n_cells_below_010": int(sum(1 for e in paper_eces if e < 0.10)),
            "n_cells_total": len(paper_eces),
            "paper_published_pooled_ece": 0.079,
            "deviation_from_paper": pooled_ece - 0.079,
        },
        "extension_6_novel": {
            "pooled_ece": ext_pooled_ece,
            "pooled_brier": ext_pooled_brier,
            "median_per_cell_ece": ext_median_ece,
            "max_per_cell_ece": ext_max_ece,
            "n_cells_below_010": int(sum(1 for e in extension_eces if e < 0.10)),
            "n_cells_total": len(extension_eces),
            "outlier_belief": [r["belief"] for r in per_cell_rows if r["ece"] == ext_max_ece][0],
        },
        "null_test_paper_8": {
            "pooled_null_5th_percentile": pooled_null_5th,
            "pooled_observed_percentile_in_null": pooled_pct,
            "rel_over_unc_ratio": rel_over_unc,
        },
        "P1_median_paper_8_below_010": p1_median_below_10,
        "P2_pooled_below_null_5th": p2_pooled_below_5th,
        "P3_reliability_below_uncertainty": p3_rel_below_unc,
        "composite_pass": composite_pass,
        "verdict": "PASS" if composite_pass else "FAIL",
    }

    # ── 6. Save outputs ───────────────────────────────────────────
    import csv

    with open(RESULTS_DIR / "A2_per_cell_ece.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(per_cell_rows[0].keys()))
        w.writeheader()
        w.writerows(per_cell_rows)

    with open(RESULTS_DIR / "A2_circular_null.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(null_summary[0].keys()))
        w.writeheader()
        w.writerows(null_summary)

    np.savez_compressed(RESULTS_DIR / "A2_reliability_data.npz", **bin_data,
                        **{f"belief_{k}__{kk}": v
                           for k, d in reliability_diagrams.items()
                           for kk, v in d.items() if isinstance(v, np.ndarray)})

    with open(RESULTS_DIR / "A2_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)

    # ── 7. Print headline ─────────────────────────────────────────
    print("\n" + "="*70)
    print(f"[A2-metrics] HEADLINE — V6 A2 calibration audit (paper-aligned methodology)")
    print("="*70)
    print(f"\n  PRIMARY (paper's 8 beliefs, F1×4 + F2×4):")
    print(f"    pooled ECE:          {pooled_ece:.4f}   (paper published: 0.079, deviation: {pooled_ece-0.079:+.4f})")
    print(f"    median per-cell ECE: {median_ece:.4f}   (IQR: {iqr_ece[0]:.4f}-{iqr_ece[1]:.4f}, max: {max_ece:.4f})")
    print(f"    cells with ECE<0.10: {summary['paper_8_replication']['n_cells_below_010']} / {summary['paper_8_replication']['n_cells_total']}")
    print(f"    pooled null 5th:     {pooled_null_5th:.4f}")
    print(f"    rel/uncertainty:     {rel_over_unc:.4f}")
    print()
    print(f"  EXTENSION (V6 novel — 6 beliefs F3-F8 NOT in paper's 8):")
    print(f"    pooled ECE:          {ext_pooled_ece:.4f}")
    print(f"    median per-cell ECE: {ext_median_ece:.4f} (max: {ext_max_ece:.4f})")
    print(f"    cells with ECE<0.10: {summary['extension_6_novel']['n_cells_below_010']} / {summary['extension_6_novel']['n_cells_total']}")
    print(f"    outlier belief:      {summary['extension_6_novel']['outlier_belief']}")
    print()
    print(f"  P1 median paper-8 ECE<0.10: {'PASS' if p1_median_below_10 else 'FAIL'}")
    print(f"  P2 pooled<null 5th-pct:     {'PASS' if p2_pooled_below_5th else 'FAIL'}")
    print(f"  P3 rel/unc<1:               {'PASS' if p3_rel_below_unc else 'FAIL'}")
    print(f"  COMPOSITE A2:               {summary['verdict']}")
    print("="*70)
    return 0 if composite_pass else 1  # nonzero exit if FAIL (pre-reg negative)


if __name__ == "__main__":
    sys.exit(main())
