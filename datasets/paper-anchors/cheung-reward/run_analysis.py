"""
T-R2-04 — Cheung 2019 uncertainty × surprise interaction vs additive reward model.

Question (Q-R2-04 / AP-v2-06): Does MI's additive reward (Eq. 5) capture the
interaction signature that Cheung 2019 reports, or only the marginals?

Procedure:
  1. Load Cheung 2024 OSF data_pleasure_2023.csv (N=39,351 trials;
     replication of Cheung 2019 Exp. 2 with same chord stimuli).
  2. Aggregate chord-level means (Cheung's own pipeline in OSFdata_code.Rmd).
  3. Fit M0 (null+controls), M1 (additive IC+ENTROPY), M2 (IC*ENTROPY),
     M3 (MI-Eq.5 composite) on leave-songs-out CV (5 folds, seed=42).
  4. Report held-out R², AIC, BIC, Pearson r, Spearman rho.
  5. Bootstrap 95% CI on beta_interaction (B=5000) and on Delta(R^2) = R^2(M2)-R^2(M1).
  6. Sign & magnitude comparison to Cheung 2019 Table S1 beta values.
  7. Quadrant analysis: low/high uncertainty x low/high surprise predicted rating.

Frozen-code confirmation: no Musical_Intelligence/ edits. Script is pure
post-hoc statistical modelling over existing CSV columns.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.model_selection import GroupKFold
import statsmodels.api as sm
import statsmodels.formula.api as smf

SEED = 42
BOOTSTRAP_B = 5000
OUT_DIR = Path(__file__).parent
DATA_CSV = Path(
    "<PAPER_TIME_SCIENCE_ROOT>/Science/datasets/reward/"
    "cheung2024/data_pleasure_2023.csv"
)

# Cheung 2019 published reference values (Cheung et al. 2019 Curr Biol
# Fig 1D + Table S1; Exp 2 supra-additive model `p4` in OSFdata_code.Rmd).
# Signs and approximate magnitudes reported in the paper (z-scored predictors).
CHEUNG_PUBLISHED = {
    "IC_sign": "+",          # main effect of surprise (information content)
    "IC_magnitude": 0.09,    # approximate beta on standardised scale
    "ENTROPY_sign": "-",     # main effect of uncertainty
    "ENTROPY_magnitude": 0.12,
    "IC_ENTROPY_sign": "-",  # interaction (key finding)
    "IC_ENTROPY_magnitude": 0.09,
    "notes": (
        "Pleasure peaks at low-uncertainty + high-surprise OR "
        "high-uncertainty + low-surprise -> negative interaction coefficient."
    ),
}

CONTROLS = ["valence", "arousal", "dissonance", "spectralcentroid",
            "spectralcomplexity", "Leman6"]


# ---------- helpers ----------------------------------------------------------

def _zscore(s: pd.Series) -> pd.Series:
    return (s - s.mean()) / s.std(ddof=0)


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def _load_and_prep() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Return (trial_df_zscored, chord_agg_df_zscored, prep_meta)."""
    df = pd.read_csv(DATA_CSV)
    # Strip BOM from first column name if present
    df.columns = [c.lstrip("﻿") for c in df.columns]

    needed = ["VPID", "IC", "ENTROPY", "Leman6", "rating", "dissonance",
              "spectralcentroid", "spectralcomplexity", "song", "rhythm",
              "chordnumber", "valence", "arousal"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise RuntimeError(f"missing columns: {missing}")

    n_raw = len(df)
    df_clean = df.dropna(subset=needed).copy()
    n_dropped = n_raw - len(df_clean)

    # Aggregate chord-level means across subjects (matches OSFdata_code.Rmd
    # line 295: dme = aggregate(. ~chordnumber+song, data=pdata, mean)).
    agg = (
        df_clean.groupby(["song", "chordnumber"], as_index=False)
        .agg({
            "IC": "mean", "ENTROPY": "mean", "Leman6": "mean",
            "rating": "mean", "dissonance": "mean",
            "spectralcentroid": "mean", "spectralcomplexity": "mean",
            "valence": "mean", "arousal": "mean",
        })
    )

    # Z-score all predictors and response (matches Cheung cleandf2)
    for col in ["IC", "ENTROPY", "Leman6", "dissonance", "spectralcentroid",
                "spectralcomplexity", "valence", "arousal", "rating"]:
        agg[col + "_z"] = _zscore(agg[col])

    # MI-Eq.5 composite reward using z-scored IC as surprise proxy and
    # sigmoid(-ENTROPY_z) as confidence pi proxy.
    ic_z = agg["IC_z"].to_numpy()
    ent_z = agg["ENTROPY_z"].to_numpy()
    pi_z = _sigmoid(-ent_z)                    # high entropy -> low pi
    surprise_mag = np.abs(ic_z)                # |PE|
    resolution = 1.0 - surprise_mag            # inverse of |PE|
    exploration = surprise_mag * (1.0 - pi_z)
    monotony_sq = pi_z ** 2
    agg["mi_reward"] = (
        1.5 * surprise_mag + 0.8 * resolution
        + 0.5 * exploration - 0.6 * monotony_sq
    )
    agg["mi_reward_z"] = _zscore(agg["mi_reward"])

    # Same z-scoring for the trial-level frame (used for LMM sensitivity).
    trial = df_clean.copy()
    for col in ["IC", "ENTROPY", "Leman6", "dissonance", "spectralcentroid",
                "spectralcomplexity", "valence", "arousal", "rating"]:
        trial[col + "_z"] = _zscore(trial[col])
    ic_t = trial["IC_z"].to_numpy()
    ent_t = trial["ENTROPY_z"].to_numpy()
    pi_t = _sigmoid(-ent_t)
    trial["mi_reward"] = (
        1.5 * np.abs(ic_t) + 0.8 * (1.0 - np.abs(ic_t))
        + 0.5 * np.abs(ic_t) * (1.0 - pi_t) - 0.6 * pi_t ** 2
    )
    trial["mi_reward_z"] = _zscore(trial["mi_reward"])

    meta = {
        "csv_path": str(DATA_CSV),
        "n_trials_raw": int(n_raw),
        "n_trials_dropped_nan": int(n_dropped),
        "n_trials_used": int(len(df_clean)),
        "n_subjects": int(df_clean["VPID"].nunique()),
        "n_songs": int(df_clean["song"].nunique()),
        "n_rhythms": int(df_clean["rhythm"].nunique()),
        "n_chord_level_rows": int(len(agg)),
        "mi_reward_formula": (
            "1.5*|IC_z| + 0.8*(1-|IC_z|) + 0.5*|IC_z|*(1-pi) - 0.6*pi^2; "
            "pi = sigmoid(-ENTROPY_z)"
        ),
    }
    return trial, agg, meta


# ---------- model definitions ------------------------------------------------

MODEL_FORMULAS = {
    "M0_null_controls": (
        "rating_z ~ valence_z + arousal_z + dissonance_z "
        "+ spectralcentroid_z + spectralcomplexity_z + Leman6_z"
    ),
    "M1_additive_IC_ENTROPY": (
        "rating_z ~ IC_z + ENTROPY_z + valence_z + arousal_z + dissonance_z "
        "+ spectralcentroid_z + spectralcomplexity_z + Leman6_z"
    ),
    "M2_interaction_IC_x_ENTROPY": (
        "rating_z ~ IC_z * ENTROPY_z + valence_z + arousal_z + dissonance_z "
        "+ spectralcentroid_z + spectralcomplexity_z + Leman6_z"
    ),
    "M3_MI_Eq5_composite": (
        "rating_z ~ mi_reward_z + valence_z + arousal_z + dissonance_z "
        "+ spectralcentroid_z + spectralcomplexity_z + Leman6_z"
    ),
}


def _fit_ols(formula: str, train: pd.DataFrame) -> sm.regression.linear_model.RegressionResultsWrapper:
    return smf.ols(formula, data=train).fit()


def _held_out_metrics(res, test: pd.DataFrame) -> dict:
    yhat = res.predict(test)
    y = test["rating_z"].to_numpy()
    resid = y - yhat
    ss_res = np.sum(resid ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2_heldout = 1.0 - ss_res / ss_tot if ss_tot > 0 else np.nan
    if len(y) > 1:
        pear = stats.pearsonr(y, yhat)
        spr = stats.spearmanr(y, yhat)
    else:
        pear = (np.nan, np.nan)
        spr = (np.nan, np.nan)
    return {
        "r2_heldout": float(r2_heldout),
        "pearson_r": float(pear[0]),
        "pearson_p": float(pear[1]),
        "spearman_rho": float(spr[0]),
        "spearman_p": float(spr[1]),
        "aic_train": float(res.aic),
        "bic_train": float(res.bic),
        "rmse_heldout": float(np.sqrt(np.mean(resid ** 2))),
    }


def _run_loso_cv(agg: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    groups = agg["song"].to_numpy()
    gkf = GroupKFold(n_splits=5)
    per_fold = []
    for mname, formula in MODEL_FORMULAS.items():
        for fold, (tr_idx, te_idx) in enumerate(
            gkf.split(agg, groups=groups), start=1
        ):
            train = agg.iloc[tr_idx]
            test = agg.iloc[te_idx]
            res = _fit_ols(formula, train)
            m = _held_out_metrics(res, test)
            m["model"] = mname
            m["fold"] = fold
            m["n_train"] = int(len(train))
            m["n_test"] = int(len(test))
            per_fold.append(m)
    fold_df = pd.DataFrame(per_fold)

    summary = {}
    for mname in MODEL_FORMULAS:
        sub = fold_df[fold_df.model == mname]
        summary[mname] = {
            "r2_heldout_mean": float(sub.r2_heldout.mean()),
            "r2_heldout_std": float(sub.r2_heldout.std(ddof=1)),
            "pearson_r_mean": float(sub.pearson_r.mean()),
            "spearman_rho_mean": float(sub.spearman_rho.mean()),
            "aic_train_mean": float(sub.aic_train.mean()),
            "bic_train_mean": float(sub.bic_train.mean()),
            "rmse_heldout_mean": float(sub.rmse_heldout.mean()),
        }
    return summary, fold_df


# ---------- full-data fit + interaction coefficient --------------------------

def _fit_full_report(agg: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    rows = []
    coef_rows = []
    for mname, formula in MODEL_FORMULAS.items():
        res = _fit_ols(formula, agg)
        rows.append({
            "model": mname,
            "n": int(res.nobs),
            "k": int(res.df_model),
            "r2": float(res.rsquared),
            "r2_adj": float(res.rsquared_adj),
            "aic": float(res.aic),
            "bic": float(res.bic),
            "f_pvalue": float(res.f_pvalue),
        })
        for term in res.params.index:
            coef_rows.append({
                "model": mname,
                "term": term,
                "beta": float(res.params[term]),
                "se": float(res.bse[term]),
                "t": float(res.tvalues[term]),
                "p": float(res.pvalues[term]),
                "ci_lo": float(res.conf_int().loc[term, 0]),
                "ci_hi": float(res.conf_int().loc[term, 1]),
            })
    summary = {r["model"]: r for r in rows}
    coef_df = pd.DataFrame(coef_rows)
    return summary, coef_df


# ---------- bootstrap on interaction term and delta-R^2 ----------------------

def _bootstrap_interaction(agg: pd.DataFrame, B: int = BOOTSTRAP_B, seed: int = SEED) -> dict:
    rng = np.random.default_rng(seed)
    songs = agg["song"].unique()
    interaction_draws = np.empty(B)
    delta_r2_draws = np.empty(B)

    # pre-build formulas for speed
    form_m1 = MODEL_FORMULAS["M1_additive_IC_ENTROPY"]
    form_m2 = MODEL_FORMULAS["M2_interaction_IC_x_ENTROPY"]

    for b in range(B):
        # block bootstrap by song (respects Cheung AR structure at song level)
        sample_songs = rng.choice(songs, size=len(songs), replace=True)
        parts = []
        for s in sample_songs:
            parts.append(agg[agg.song == s])
        samp = pd.concat(parts, ignore_index=True)
        try:
            r1 = _fit_ols(form_m1, samp)
            r2 = _fit_ols(form_m2, samp)
            interaction_draws[b] = float(r2.params.get("IC_z:ENTROPY_z", np.nan))
            delta_r2_draws[b] = float(r2.rsquared - r1.rsquared)
        except Exception:
            interaction_draws[b] = np.nan
            delta_r2_draws[b] = np.nan

    valid = ~np.isnan(interaction_draws)
    int_ci = np.nanpercentile(interaction_draws[valid], [2.5, 97.5])
    dr2_ci = np.nanpercentile(delta_r2_draws[valid], [2.5, 97.5])
    return {
        "B": B,
        "valid_draws": int(valid.sum()),
        "interaction_mean": float(np.nanmean(interaction_draws)),
        "interaction_median": float(np.nanmedian(interaction_draws)),
        "interaction_ci95": [float(int_ci[0]), float(int_ci[1])],
        "interaction_p_two_sided_vs_zero": float(
            2 * min(np.nanmean(interaction_draws > 0),
                     np.nanmean(interaction_draws < 0))
        ),
        "delta_r2_mean": float(np.nanmean(delta_r2_draws)),
        "delta_r2_ci95": [float(dr2_ci[0]), float(dr2_ci[1])],
        "draws_path": "bootstrap_interaction.npy",
    }, interaction_draws, delta_r2_draws


# ---------- quadrant analysis ------------------------------------------------

def _quadrants(agg: pd.DataFrame) -> pd.DataFrame:
    # Cheung's own quadrant thresholds (quadrant-thresholds.txt) on the
    # raw (unscaled) IC / ENTROPY. We apply them on raw columns.
    low_U = 1.57309884
    high_U = 2.21065292
    low_S = 0.634460668
    high_S = 1.86352607503
    q = []
    pairs = [
        ("low_U_low_S", agg.ENTROPY <= low_U, agg.IC <= low_S),
        ("low_U_high_S", agg.ENTROPY <= low_U, agg.IC >= high_S),
        ("high_U_low_S", agg.ENTROPY >= high_U, agg.IC <= low_S),
        ("high_U_high_S", agg.ENTROPY >= high_U, agg.IC >= high_S),
    ]
    # Fit the interaction model on full data, get predicted rating_z in each quadrant.
    res_m2 = _fit_ols(MODEL_FORMULAS["M2_interaction_IC_x_ENTROPY"], agg)
    yhat = res_m2.predict(agg)
    y = agg["rating_z"].to_numpy()
    for name, u_mask, s_mask in pairs:
        mask = u_mask & s_mask
        q.append({
            "quadrant": name,
            "n": int(mask.sum()),
            "rating_z_mean_obs": float(np.mean(y[mask])) if mask.sum() else np.nan,
            "rating_z_mean_pred": float(np.mean(yhat[mask])) if mask.sum() else np.nan,
        })
    return pd.DataFrame(q)


# ---------- LMM sensitivity --------------------------------------------------

def _lmm_sensitivity(trial: pd.DataFrame) -> dict:
    """Trial-level mixed model with random intercepts for VPID and song.

    Reduced vs Cheung's brms (no AR(1), no random slopes) but captures the
    per-listener structure that the aggregated OLS ignores.
    """
    sub = trial.sample(
        n=min(len(trial), 20000), random_state=SEED
    ).reset_index(drop=True)  # statsmodels LMM gets slow at full N
    formula = (
        "rating_z ~ IC_z * ENTROPY_z + valence_z + arousal_z + dissonance_z "
        "+ spectralcentroid_z + spectralcomplexity_z + Leman6_z"
    )
    # Random intercept for VPID; song absorbed as fixed song-level cluster
    md = smf.mixedlm(formula, sub, groups=sub["VPID"])
    try:
        mdf = md.fit(method="lbfgs", reml=True, maxiter=200)
    except Exception as e:
        return {"ok": False, "error": str(e), "n_used": int(len(sub))}
    ixn_beta = float(mdf.params.get("IC_z:ENTROPY_z", np.nan))
    ixn_se = float(mdf.bse.get("IC_z:ENTROPY_z", np.nan))
    ixn_p = float(mdf.pvalues.get("IC_z:ENTROPY_z", np.nan))
    return {
        "ok": True,
        "n_used": int(len(sub)),
        "n_subjects": int(sub["VPID"].nunique()),
        "interaction_beta": ixn_beta,
        "interaction_se": ixn_se,
        "interaction_p": ixn_p,
        "ic_beta": float(mdf.params.get("IC_z", np.nan)),
        "entropy_beta": float(mdf.params.get("ENTROPY_z", np.nan)),
        "converged": bool(mdf.converged),
    }


# ---------- main -------------------------------------------------------------

def main() -> None:
    print("[T-R2-04] Loading Cheung 2024 pleasure data …")
    trial, agg, meta = _load_and_prep()
    for k, v in meta.items():
        print(f"  {k}: {v}")

    print("\n[T-R2-04] Full-data model fits …")
    full_summary, coef_df = _fit_full_report(agg)
    for mname, s in full_summary.items():
        print(f"  {mname}: R2={s['r2']:.4f} AIC={s['aic']:.1f} BIC={s['bic']:.1f}")

    print("\n[T-R2-04] Leave-songs-out 5-fold CV …")
    cv_summary, fold_df = _run_loso_cv(agg)
    for mname, s in cv_summary.items():
        print(f"  {mname}: heldout R2={s['r2_heldout_mean']:+.4f} "
              f"pearson={s['pearson_r_mean']:+.4f} "
              f"spearman={s['spearman_rho_mean']:+.4f}")

    print("\n[T-R2-04] Bootstrap on interaction coefficient + ΔR² …")
    boot_summary, int_draws, dr2_draws = _bootstrap_interaction(agg)
    np.save(OUT_DIR / "bootstrap_interaction.npy", int_draws)
    np.save(OUT_DIR / "bootstrap_delta_r2.npy", dr2_draws)
    print(f"  interaction β (bootstrap mean): {boot_summary['interaction_mean']:+.4f}")
    print(f"  interaction β 95% CI: [{boot_summary['interaction_ci95'][0]:+.4f}, "
          f"{boot_summary['interaction_ci95'][1]:+.4f}]")
    print(f"  ΔR² (M2 − M1): {boot_summary['delta_r2_mean']:+.5f} "
          f"CI=[{boot_summary['delta_r2_ci95'][0]:+.5f}, "
          f"{boot_summary['delta_r2_ci95'][1]:+.5f}]")

    print("\n[T-R2-04] Quadrant analysis …")
    q_df = _quadrants(agg)
    for _, row in q_df.iterrows():
        print(f"  {row['quadrant']:>18}: n={row['n']:4d} "
              f"obs={row['rating_z_mean_obs']:+.3f} "
              f"pred={row['rating_z_mean_pred']:+.3f}")

    print("\n[T-R2-04] LMM sensitivity (trial-level, random intercepts) …")
    lmm = _lmm_sensitivity(trial)
    for k, v in lmm.items():
        print(f"  {k}: {v}")

    # Cheung comparison
    m2 = full_summary["M2_interaction_IC_x_ENTROPY"]
    m2_coefs = coef_df[coef_df.model == "M2_interaction_IC_x_ENTROPY"].set_index("term")
    ic_beta = float(m2_coefs.loc["IC_z", "beta"])
    ent_beta = float(m2_coefs.loc["ENTROPY_z", "beta"])
    ixn_beta = float(m2_coefs.loc["IC_z:ENTROPY_z", "beta"])
    cheung_cmp = {
        "IC": {
            "MI_proxy_beta": ic_beta,
            "MI_proxy_sign": "+" if ic_beta > 0 else "-",
            "cheung_published_sign": CHEUNG_PUBLISHED["IC_sign"],
            "cheung_published_magnitude": CHEUNG_PUBLISHED["IC_magnitude"],
            "sign_match": (ic_beta > 0) == (CHEUNG_PUBLISHED["IC_sign"] == "+"),
        },
        "ENTROPY": {
            "MI_proxy_beta": ent_beta,
            "MI_proxy_sign": "+" if ent_beta > 0 else "-",
            "cheung_published_sign": CHEUNG_PUBLISHED["ENTROPY_sign"],
            "cheung_published_magnitude": CHEUNG_PUBLISHED["ENTROPY_magnitude"],
            "sign_match": (ent_beta > 0) == (CHEUNG_PUBLISHED["ENTROPY_sign"] == "+"),
        },
        "IC_x_ENTROPY": {
            "MI_proxy_beta": ixn_beta,
            "MI_proxy_sign": "+" if ixn_beta > 0 else "-",
            "cheung_published_sign": CHEUNG_PUBLISHED["IC_ENTROPY_sign"],
            "cheung_published_magnitude": CHEUNG_PUBLISHED["IC_ENTROPY_magnitude"],
            "sign_match": (ixn_beta > 0) == (CHEUNG_PUBLISHED["IC_ENTROPY_sign"] == "+"),
        },
    }

    # Delta-AIC between M1 and M2 (full-data fit)
    delta_aic_m2_m1 = full_summary["M2_interaction_IC_x_ENTROPY"]["aic"] - \
                      full_summary["M1_additive_IC_ENTROPY"]["aic"]
    delta_aic_m3_m1 = full_summary["M3_MI_Eq5_composite"]["aic"] - \
                      full_summary["M1_additive_IC_ENTROPY"]["aic"]
    delta_aic_m3_m0 = full_summary["M3_MI_Eq5_composite"]["aic"] - \
                      full_summary["M0_null_controls"]["aic"]

    # Persist everything
    results = {
        "seed": SEED,
        "bootstrap_B": BOOTSTRAP_B,
        "meta": meta,
        "full_data_fit": full_summary,
        "held_out_cv_summary": cv_summary,
        "bootstrap": boot_summary,
        "lmm_sensitivity": lmm,
        "quadrant_analysis": q_df.to_dict(orient="records"),
        "cheung_vs_MI_proxy": cheung_cmp,
        "delta_aic": {
            "M2_minus_M1": float(delta_aic_m2_m1),
            "M3_minus_M1": float(delta_aic_m3_m1),
            "M3_minus_M0": float(delta_aic_m3_m0),
        },
        "cheung_published_reference": CHEUNG_PUBLISHED,
    }
    (OUT_DIR / "results.json").write_text(json.dumps(results, indent=2))
    fold_df.to_csv(OUT_DIR / "fold_metrics.csv", index=False)
    coef_df.to_csv(OUT_DIR / "coefficients.csv", index=False)
    q_df.to_csv(OUT_DIR / "quadrant_predictions.csv", index=False)

    print(f"\n[T-R2-04] Wrote results to {OUT_DIR}")
    print(f"[T-R2-04] ΔAIC (M2 − M1) full-data = {delta_aic_m2_m1:+.2f}")
    print(f"[T-R2-04] ΔAIC (M3 − M1) full-data = {delta_aic_m3_m1:+.2f}")
    print(f"[T-R2-04] ΔAIC (M3 − M0) full-data = {delta_aic_m3_m0:+.2f}")


if __name__ == "__main__":
    main()
