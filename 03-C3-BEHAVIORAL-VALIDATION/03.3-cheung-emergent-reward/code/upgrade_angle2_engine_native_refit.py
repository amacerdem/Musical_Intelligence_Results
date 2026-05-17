"""Phase 10 Audio-Native Upgrade — Angle 2 — Engine-native M2/M3 re-fit.

Pre-registration: ../AUDIO_NATIVE_UPGRADE.md §2 Angle 2 (frozen 2026-05-16).
Engine SHA pin: 318eb2f529d7103e8b7d80b01228357fdc4e0217.

Replaces Cheung's IDyOM IC and ENTROPY with MI's own HTP and ICEM (rhythm1 cache
from Angle 1) in the M2 interaction regression. Tests whether the published
β = −0.124 reproduces inside bootstrap 95% CI of β(MI_HTP × MI_ICEM).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats as scistats
from sklearn.model_selection import GroupKFold

PHASE_DIR = Path(__file__).resolve().parent.parent
ENGINE_ROOT = PHASE_DIR.parent.parent
PLEASURE_CSV = ENGINE_ROOT / "Science" / "datasets" / "reward" / "cheung2024" / "data_pleasure_2023.csv"
ANGLE1_PER_CHORD = PHASE_DIR / "results" / "angle1_per_chord_aligned.csv"
ANGLE3_LOSO = PHASE_DIR / "results" / "angle3_loso_ceiling.json"

OUT_DIR = PHASE_DIR / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHEUNG_PUBLISHED_BETA = -0.124
SEED = 42
N_BOOTSTRAP = 5000
N_FOLDS = 5
CONTROLS = ["valence", "arousal", "dissonance", "spectralcentroid",
            "spectralcomplexity", "Leman6"]


def file_sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def zscore(s):
    arr = np.asarray(s, dtype=np.float64)
    sd = arr.std(ddof=0)
    return (arr - arr.mean()) / sd if sd > 0 else arr - arr.mean()


def main():
    if not ANGLE1_PER_CHORD.exists():
        print(f"ERROR: {ANGLE1_PER_CHORD} missing — run Angle 1 first", file=sys.stderr)
        return 2
    if not PLEASURE_CSV.exists():
        print(f"ERROR: {PLEASURE_CSV} missing", file=sys.stderr)
        return 2

    print("Phase 10 Audio-Native Upgrade — Angle 2")
    print("=" * 70)

    # Load MI per-chord HTP/ICEM (Angle 1 output)
    mi_chord = pd.read_csv(ANGLE1_PER_CHORD)
    print(f"  MI per-chord rows: {len(mi_chord)} (across {mi_chord['song'].nunique()} songs)")

    # Load Cheung trial-level pleasure CSV — keep only rhythm=1 to match Angle 1
    df_full = pd.read_csv(PLEASURE_CSV)
    df_full.columns = [c.lstrip("﻿") for c in df_full.columns]
    df_r1 = df_full[df_full["rhythm"] == 1].copy()
    print(f"  Cheung rhythm=1 trials: {len(df_r1):,}  (VPIDs: {df_r1['VPID'].nunique()}, "
          f"songs: {df_r1['song'].nunique()})")

    # Aggregate trial-level → chord-level (mean rating across VPIDs per song,chordnumber)
    needed = ["song", "chordnumber"] + CONTROLS + ["IC", "ENTROPY", "rating"]
    df_r1_clean = df_r1.dropna(subset=needed).copy()
    chord_agg = (df_r1_clean.groupby(["song", "chordnumber"], as_index=False)
                 .agg({**{c: "mean" for c in CONTROLS},
                       "IC": "mean", "ENTROPY": "mean", "rating": "mean"}))
    print(f"  Cheung rhythm=1 chord-aggregated rows: {len(chord_agg)}")

    # Merge MI features with Cheung chord-level data
    merged = chord_agg.merge(mi_chord[["song", "chordnumber", "htp_e0_mean", "icem_e0_mean"]],
                              on=["song", "chordnumber"], how="inner")
    print(f"  After MI ⨝ Cheung merge: {len(merged)} chord-level rows")

    # Drop rows where MI features are NaN (alignment failures at boundary)
    merged = merged.dropna(subset=["htp_e0_mean", "icem_e0_mean"])
    print(f"  After dropping MI-NaN: {len(merged)} chord-level rows")

    # Z-score
    for col in ["IC", "ENTROPY", "rating", "htp_e0_mean", "icem_e0_mean"] + CONTROLS:
        merged[f"{col}_z"] = zscore(merged[col])
    merged.rename(columns={"htp_e0_mean_z": "MI_HTP_z",
                            "icem_e0_mean_z": "MI_ICEM_z"}, inplace=True)

    controls_str = " + ".join(f"{c}_z" for c in CONTROLS)

    # Cheung-style M2 (IDyOM IC × ENTROPY) — sanity reproduce
    cheung_M2 = f"rating_z ~ {controls_str} + IC_z + ENTROPY_z + IC_z:ENTROPY_z"
    res_cheung = smf.ols(cheung_M2, data=merged).fit()
    cheung_beta = float(res_cheung.params["IC_z:ENTROPY_z"])
    cheung_se = float(res_cheung.bse["IC_z:ENTROPY_z"])
    print(f"\nCheung M2 (IDyOM IC×ENT) β = {cheung_beta:+.4f}  SE={cheung_se:.4f}")

    # Engine-native M2 (MI HTP × ICEM)
    engine_M2 = f"rating_z ~ {controls_str} + MI_HTP_z + MI_ICEM_z + MI_HTP_z:MI_ICEM_z"
    res_engine = smf.ols(engine_M2, data=merged).fit()
    engine_beta = float(res_engine.params["MI_HTP_z:MI_ICEM_z"])
    engine_se = float(res_engine.bse["MI_HTP_z:MI_ICEM_z"])
    print(f"Engine M2 (MI HTP×ICEM) β = {engine_beta:+.4f}  SE={engine_se:.4f}")

    # Bootstrap engine M2 β across chord-rows
    rng = np.random.default_rng(SEED)
    boots = []
    n = len(merged)
    for _ in range(N_BOOTSTRAP):
        idx = rng.integers(0, n, size=n)
        sub = merged.iloc[idx]
        try:
            res = smf.ols(engine_M2, data=sub).fit()
            boots.append(float(res.params["MI_HTP_z:MI_ICEM_z"]))
        except Exception:
            continue
    boots = np.array(boots)
    np.save(OUT_DIR / "angle2_bootstrap_distribution.npy", boots)
    ci_lo = float(np.quantile(boots, 0.025))
    ci_hi = float(np.quantile(boots, 0.975))
    boot_mean = float(np.mean(boots))
    boot_median = float(np.median(boots))

    # Decision rule
    inside_ci = ci_lo <= CHEUNG_PUBLISHED_BETA <= ci_hi
    if inside_ci:
        verdict = "POSITIVE_ARCHITECTURAL_EMERGENCE"
    else:
        # How far outside?
        if CHEUNG_PUBLISHED_BETA < ci_lo:
            distance = ci_lo - CHEUNG_PUBLISHED_BETA
        else:
            distance = CHEUNG_PUBLISHED_BETA - ci_hi
        verdict = ("NEGATIVE_NOT_ARCHITECTURALLY_EMERGENT" if distance > 0.05
                   else "INCONCLUSIVE_BORDERLINE")

    # Held-out CV
    gkf = GroupKFold(n_splits=N_FOLDS)
    cv_engine_r = []
    cv_cheung_r = []
    for train_idx, test_idx in gkf.split(merged, groups=merged["song"]):
        train, test = merged.iloc[train_idx], merged.iloc[test_idx]
        # Engine M2
        try:
            r_eng = smf.ols(engine_M2, data=train).fit()
            pred_eng = r_eng.predict(test)
            r_eng_val = float(scistats.pearsonr(pred_eng, test["rating_z"])[0]) if pred_eng.std() > 0 else 0.0
        except Exception:
            r_eng_val = np.nan
        cv_engine_r.append(r_eng_val)
        try:
            r_che = smf.ols(cheung_M2, data=train).fit()
            pred_che = r_che.predict(test)
            r_che_val = float(scistats.pearsonr(pred_che, test["rating_z"])[0]) if pred_che.std() > 0 else 0.0
        except Exception:
            r_che_val = np.nan
        cv_cheung_r.append(r_che_val)
    cv_engine_mean = float(np.mean(cv_engine_r))
    cv_cheung_mean = float(np.mean(cv_cheung_r))

    # LOSO ceiling for ratio framing (load Angle 3)
    angle3 = json.loads(ANGLE3_LOSO.read_text())
    pleasure_ceiling = angle3["pleasure_ceiling"]["fisher_z_rho"]
    ratio_engine = cv_engine_mean / pleasure_ceiling if pleasure_ceiling > 0 else None
    ratio_cheung = cv_cheung_mean / pleasure_ceiling if pleasure_ceiling > 0 else None

    output = {
        "stage": "Phase 10 Audio-Native Upgrade — Angle 2",
        "engine_pin_commit": "318eb2f529d7103e8b7d80b01228357fdc4e0217",
        "rhythm_condition": 1,
        "n_chord_rows": int(len(merged)),
        "n_songs": int(merged["song"].nunique()),
        "cheung_published_beta": CHEUNG_PUBLISHED_BETA,
        "cheung_M2_idyom": {
            "beta_interaction": cheung_beta,
            "se": cheung_se,
            "cv_heldout_r": cv_cheung_mean,
            "cv_per_fold": [float(x) for x in cv_cheung_r],
        },
        "engine_M2_native": {
            "beta_interaction": engine_beta,
            "se": engine_se,
            "bootstrap_n": int(len(boots)),
            "bootstrap_mean": boot_mean,
            "bootstrap_median": boot_median,
            "bootstrap_ci95": [ci_lo, ci_hi],
            "cv_heldout_r": cv_engine_mean,
            "cv_per_fold": [float(x) for x in cv_engine_r],
        },
        "decision": {
            "verdict": verdict,
            "cheung_beta_inside_engine_bootstrap_CI": bool(inside_ci),
            "distance_outside_CI": (None if inside_ci else
                                     float(min(abs(CHEUNG_PUBLISHED_BETA - ci_lo),
                                                abs(CHEUNG_PUBLISHED_BETA - ci_hi)))),
        },
        "loso_relative_framing": {
            "pleasure_ceiling": pleasure_ceiling,
            "engine_M2_cv_r_div_ceiling": ratio_engine,
            "cheung_M2_cv_r_div_ceiling": ratio_cheung,
        },
        "library_versions": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": __import__("scipy").__version__,
            "statsmodels": sm.__version__,
            "sklearn": __import__("sklearn").__version__,
        },
    }
    with open(OUT_DIR / "angle2_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print()
    print("=" * 70)
    print(f"VERDICT: {verdict}")
    print(f"  Engine-native β(MI_HTP × MI_ICEM) = {engine_beta:+.4f}  SE={engine_se:.4f}")
    print(f"  Bootstrap mean = {boot_mean:+.4f}, CI95 = [{ci_lo:+.4f}, {ci_hi:+.4f}]")
    print(f"  Cheung published β = {CHEUNG_PUBLISHED_BETA:+.4f}  → "
          f"{'INSIDE' if inside_ci else 'OUTSIDE'} engine bootstrap CI")
    print()
    print(f"  Held-out CV r:  Engine M2={cv_engine_mean:+.4f}, Cheung M2={cv_cheung_mean:+.4f}")
    print(f"  vs Pleasure LOSO ceiling +{pleasure_ceiling:.4f}:")
    if ratio_engine is not None:
        print(f"    Engine ratio = {ratio_engine:.2f}× ceiling")
        print(f"    Cheung ratio = {ratio_cheung:.2f}× ceiling")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
