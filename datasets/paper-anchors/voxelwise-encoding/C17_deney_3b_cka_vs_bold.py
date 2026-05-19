#!/usr/bin/env python3
"""
Cycle 17 Deney 3b: CKA between encoders and per-subject BOLD (the meaningful H2 test).

Deney 3 showed CKA(MI-full, MI-naive) = 0.994 at the 26-D feature level — near-identical
representational geometry in the abstract. But Deney 1 showed MI-full has 2.6× higher
shuffle-null effect size than MI-naive at the BOLD-prediction level (0.049 vs 0.019).

The resolution: MI-full's ARCHITECTURAL ROUTING matches brain regional responses, even
when the underlying 26-D representation is similar to MI-naive. The meaningful H2 test
is whether CKA(MI-full, BOLD) > CKA(MI-naive, BOLD) per subject.

Method:
  For each subject (N=4 when sub-005 lands, N=3 now):
    bold: (540, V) per-clip per-voxel BOLD (from cached bold_per_clip)
    mi_full: (540, 26), mi_naive: (540, 26), subset by clip_indices
    Compute CKA(mi_full, bold) and CKA(mi_naive, bold)
    Δ CKA = CKA(MI-full, BOLD) - CKA(MI-naive, BOLD)

Also test MERT, CLAP, Random as reference.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

FEATURES = Path("<PAPER_TIME_SCIENCE_ROOT>/Science/Bold-fMRI/ds003720/05_features")
ROI = Path("<PAPER_TIME_SCIENCE_ROOT>/Science/Bold-fMRI/ds003720/04_roi_extraction")
OUT = Path("<PAPER_TIME_SCIENCE_ROOT>/Science/Bold-fMRI/ds003720/06_encoding")

SUBJECTS = ["sub-001", "sub-003", "sub-004", "sub-005"]


def linear_cka(X: np.ndarray, Y: np.ndarray) -> float:
    """Linear CKA using n×n Gram matrices (memory-safe when V >> n).

    CKA(X, Y) = HSIC(X, Y) / sqrt(HSIC(X, X) * HSIC(Y, Y))
    HSIC using linear kernels = ||K_X^c K_Y^c||_F^2 where K_X^c = H @ X @ X.T @ H,
    H = I - 1/n·J (centering matrix). Equivalent: K_Xc = Xc @ Xc.T where Xc is
    column-centered X. For n=540, this is a 540×540 matrix = ~1MB. Safe.
    """
    n = X.shape[0]
    Xc = X - X.mean(axis=0, keepdims=True)
    Yc = Y - Y.mean(axis=0, keepdims=True)
    K = Xc @ Xc.T  # (n, n)
    L = Yc @ Yc.T  # (n, n)
    hsic_xy = float((K * L).sum())
    hsic_xx = float((K * K).sum())
    hsic_yy = float((L * L).sum())
    return hsic_xy / np.sqrt(hsic_xx * hsic_yy + 1e-12)


def main():
    print("Loading encoder features...")
    mi_full = np.load(FEATURES / "mi_ram_26d.npy").astype(np.float32)  # (720, 26)
    mi_naive = np.load(FEATURES / "mi_naive_26d.npy").astype(np.float32)
    mert = np.load(FEATURES / "mert_768d.npy").astype(np.float32)
    clap = np.load(FEATURES / "clap_music_512d.npy").astype(np.float32)
    rand26 = np.load(FEATURES / "random_26d.npy").astype(np.float32)

    rows = []
    for subj in SUBJECTS:
        bold_path = ROI / f"{subj}_bold_per_clip.npy"
        ci_path = ROI / f"{subj}_clip_indices.npy"
        if not bold_path.exists() or not ci_path.exists():
            print(f"SKIP {subj}")
            continue
        bold = np.load(bold_path).astype(np.float32)  # (540, V)
        idx = np.load(ci_path)
        print(f"{subj}: bold {bold.shape}, idx shape {idx.shape}")

        for enc_name, enc in [("MI-full", mi_full), ("MI-naive", mi_naive),
                               ("MERT", mert), ("CLAP", clap), ("Random-26", rand26)]:
            X = enc[idx, :].astype(np.float32)  # (540, D)
            cka = linear_cka(X, bold)
            rows.append({
                "subject": subj, "encoder": enc_name,
                "D": X.shape[1], "V": bold.shape[1],
                "cka_vs_bold": cka,
            })
            print(f"  {enc_name:<12} CKA vs BOLD = {cka:.4f}")

        # Free subject BOLD
        del bold

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "C17_deney_3b_cka_vs_bold.csv", index=False)

    # Paired Δ CKA (MI-full - MI-naive) per subject
    print("\n" + "="*80)
    print("Δ CKA (MI-full - MI-naive) per subject")
    print("="*80)
    pvt = df.pivot(index="subject", columns="encoder", values="cka_vs_bold")
    pvt["delta_full_vs_naive"] = pvt["MI-full"] - pvt["MI-naive"]
    pvt["delta_full_vs_mert"] = pvt["MI-full"] - pvt["MERT"]
    pvt["delta_full_vs_random"] = pvt["MI-full"] - pvt["Random-26"]
    print(pvt[["MI-full", "MI-naive", "MERT", "CLAP", "Random-26",
               "delta_full_vs_naive", "delta_full_vs_mert", "delta_full_vs_random"]].round(4).to_string())

    # Summary
    delta_naive = pvt["delta_full_vs_naive"].values
    print("\n" + "="*80)
    print("R5 H2 Floor Check (REVISED: CKA vs BOLD)")
    print("="*80)
    print(f"Per-subject Δ CKA(MI-full vs BOLD) - CKA(MI-naive vs BOLD):")
    for subj, d in zip(pvt.index, delta_naive):
        print(f"  {subj}: Δ = {d:+.4f} {'PASS' if d >= 0.02 else 'FAIL'}")
    mean_delta = np.mean(delta_naive)
    print(f"\nMean Δ across subjects: {mean_delta:+.4f}")
    print(f"R5 H2 original floor: Δ CKA ≥ 0.02")
    pass_count = int((delta_naive >= 0.02).sum())
    print(f"Subjects passing Δ ≥ 0.02: {pass_count}/{len(delta_naive)}")

    # Provenance
    (OUT / "C17_deney_3b_provenance.json").write_text(json.dumps({
        "experiment": "C17_deney_3b_cka_vs_bold",
        "subjects": list(pvt.index),
        "mean_delta_cka_full_minus_naive": float(mean_delta),
        "n_subjects_pass_h2_floor": pass_count,
    }, indent=2))

    print(f"\nArtifacts → {OUT}/C17_deney_3b_cka_vs_bold.csv")


if __name__ == "__main__":
    main()
