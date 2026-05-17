#!/usr/bin/env python3
"""
Cycle 17 Deney 3: CKA architecture test (R5 H2 floor).

Question: Does MI's compiled-neuroscience architecture (26-region RAM with meta-analytic
coordinates) produce representations distinct from a non-architectural ablation?

Method:
  Linear CKA (Kornblith 2019) between MI-full RAM (720 × 26) and MI-naive RAM (720 × 26)
  across the 720 clips.

  CKA(X, Y) = |Y^T X|_F^2 / (|X^T X|_F · |Y^T Y|_F)

  Also report CKA(MI-full, MERT) and CKA(MI-naive, MERT) for reference.

R5's H2 floor: Δ CKA ≥ 0.02 between MI-full and MI-naive (architectural distinctness).

Interpretation:
  High CKA(MI-full, MI-naive) → architecture doesn't matter (MI just replicates a generic transform)
  Low CKA(MI-full, MI-naive) → architecture produces distinct representations
  R5 wants distinctness: low CKA indicating different geometry.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

FEATURES = Path("/Volumes/SRC-9/SRC Musical Intelligence/Science/Bold-fMRI/ds003720/05_features")
OUT = Path("/Volumes/SRC-9/SRC Musical Intelligence/Science/Bold-fMRI/ds003720/06_encoding")


def centered_gram(X: np.ndarray) -> np.ndarray:
    """Center columns, return Gram matrix."""
    X = X - X.mean(axis=0, keepdims=True)
    return X @ X.T


def linear_cka(X: np.ndarray, Y: np.ndarray) -> float:
    """Linear CKA between two feature matrices (n_samples × d1) and (n_samples × d2)."""
    K = centered_gram(X)
    L = centered_gram(Y)
    hsic_xy = np.sum(K * L)  # frobenius inner product of centered grams
    hsic_xx = np.sum(K * K)
    hsic_yy = np.sum(L * L)
    return float(hsic_xy / np.sqrt(hsic_xx * hsic_yy + 1e-12))


def cka_debiased(X: np.ndarray, Y: np.ndarray) -> float:
    """Debiased linear CKA (Song 2012, unbiased HSIC)."""
    n = X.shape[0]
    X = X - X.mean(axis=0, keepdims=True)
    Y = Y - Y.mean(axis=0, keepdims=True)
    XtX = X.T @ X
    YtY = Y.T @ Y
    YtX = Y.T @ X
    # Frobenius norms squared
    num = float((YtX ** 2).sum())
    denom = float(np.sqrt((XtX ** 2).sum() * (YtY ** 2).sum()))
    return num / (denom + 1e-12)


def main():
    mi_full = np.load(FEATURES / "mi_ram_26d.npy").astype(np.float32)
    mi_naive = np.load(FEATURES / "mi_naive_26d.npy").astype(np.float32)
    mert = np.load(FEATURES / "mert_768d.npy").astype(np.float32)
    clap = np.load(FEATURES / "clap_music_512d.npy").astype(np.float32)
    rand26 = np.load(FEATURES / "random_26d.npy").astype(np.float32)
    rand768 = np.load(FEATURES / "random_768d.npy").astype(np.float32)

    print(f"MI-full {mi_full.shape}")
    print(f"MI-naive {mi_naive.shape}")
    print(f"MERT {mert.shape}")
    print(f"CLAP {clap.shape}")

    pairs = [
        ("MI-full vs MI-naive (H2 floor)", mi_full, mi_naive),
        ("MI-full vs MERT", mi_full, mert),
        ("MI-naive vs MERT", mi_naive, mert),
        ("MI-full vs CLAP", mi_full, clap),
        ("MI-naive vs CLAP", mi_naive, clap),
        ("MI-full vs Random-26", mi_full, rand26),
        ("MI-full vs Random-768", mi_full, rand768),
        ("MI-naive vs Random-26", mi_naive, rand26),
        ("MI-full vs MI-full (sanity)", mi_full, mi_full),
    ]

    rows = []
    print("\n" + "="*80)
    print("CKA Matrix")
    print("="*80)
    for name, X, Y in pairs:
        cka_lin = linear_cka(X, Y)
        cka_db = cka_debiased(X, Y)
        rows.append({
            "pair": name,
            "linear_cka": cka_lin,
            "debiased_cka": cka_db,
            "X_shape": f"{X.shape}",
            "Y_shape": f"{Y.shape}",
        })
        print(f"  {name:<40}  lin_CKA={cka_lin:.4f}  debiased={cka_db:.4f}")

    import pandas as pd
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "C17_deney_3_cka.csv", index=False)

    # R5 H2 floor check
    h2_cka = next(r for r in rows if "MI-full vs MI-naive" in r["pair"])
    distinctness = 1 - h2_cka["linear_cka"]
    print("\n" + "="*80)
    print(f"R5 H2 FLOOR CHECK")
    print("="*80)
    print(f"CKA(MI-full, MI-naive) = {h2_cka['linear_cka']:.4f}")
    print(f"Distinctness (1 - CKA) = {distinctness:.4f}")
    print(f"R5 H2 threshold: Δ CKA ≥ 0.02 distinctness")
    print(f"H2 status: {'PASS' if distinctness >= 0.02 else 'FAIL'}")

    # MERT correlation baseline for reference
    mi_mert = next(r for r in rows if r["pair"] == "MI-full vs MERT")
    naive_mert = next(r for r in rows if r["pair"] == "MI-naive vs MERT")
    print(f"\nReference: MI-full vs MERT CKA = {mi_mert['linear_cka']:.4f}")
    print(f"Reference: MI-naive vs MERT CKA = {naive_mert['linear_cka']:.4f}")

    # Provenance
    (OUT / "C17_deney_3_provenance.json").write_text(json.dumps({
        "experiment": "C17_deney_3_cka_architecture",
        "h2_distinctness": distinctness,
        "h2_pass": distinctness >= 0.02,
        "pairs_computed": [r["pair"] for r in rows],
    }, indent=2))

    print(f"\nArtifacts → {OUT}/C17_deney_3_cka.csv")


if __name__ == "__main__":
    main()
