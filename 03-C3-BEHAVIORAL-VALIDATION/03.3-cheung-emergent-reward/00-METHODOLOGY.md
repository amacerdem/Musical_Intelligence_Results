# Phase 03.3 — Cheung Emergent Reward Interaction — Methodology (LOCKED 2026-05-07)

**Axis ID:** AXIS-10
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

## 1. Scope

Phase 10 reproduces 6 paper claims for the Cheung 2019 uncertainty × surprise reward-interaction reanalysis (paper §Discussion + Significance). Specifically:

- β(IC × ENTROPY) = **−0.158** (OLS, M2 model)
- 95% CI = **[−0.228, −0.084]** (5000 song-block bootstrap)
- Cheung's published **β = −0.124 inside our bootstrap CI**
- ΔAIC = **−33.5** (M2 − M1, leave-songs-out)
- Held-out **r = +0.615** (M3 Eq. 5 closed-form, paper text §Significance)
- N = **39,351** trials × 39 subjects × 30 songs × 3 rhythms; 1,009 chord-level aggregated rows

## 2. Reproduction strategy

Phase 10 is a **deterministic post-hoc statistical reanalysis on a frozen dataset** — no engine calls. The relevant artefact is `Science/V2/reviewer-sims/divan-major-revision-2026-04-22/computing-phase/T-R2-04/results.json` (authored 2026-04-22, frozen `Musical_Intelligence/`, statsmodels 0.14.6, seed=42, B=5000).

We:
1. Load `results.json` directly,
2. Verify each of the 6 paper claims against the numerical entries,
3. Confirm the underlying CSV is byte-identical to the V2-recorded version,
4. Verify the static reward formula in the engine source is purely additive (the architectural-control claim).

This is a **non-engine reproduction**: the underlying engine state has not changed (Phases 0/2/6/7/8/9 all confirmed bit-stable engine HEAD), and the T-R2-04 analysis runs over Cheung's published CSV without invoking the MI pipeline at all (audio for Cheung stimuli was never released).

## 3. Per-claim paper values + tolerances

| Claim ID | Paper value | Source | Tolerance |
|---|---|---|---|
| C-CHEUNG-01 | β(IC × ENTROPY) OLS = −0.158 | results.json full_data_fit.M2 / coefficients.csv | abs ≤ 0.01 |
| C-CHEUNG-02 | 95% CI [−0.228, −0.084] (bootstrap) | results.json bootstrap.interaction_ci95 | abs(end-points) ≤ 0.01 |
| C-CHEUNG-03 | Cheung published β=−0.124 inside CI | results.json bootstrap | exact_match (boolean) |
| C-CHEUNG-04 | ΔAIC = −33.5 (M2 − M1) | results.json delta_aic.M2_minus_M1 | abs ≤ 1.0 |
| C-CHEUNG-05 | Held-out r = +0.615 (M3 Eq. 5) | results.json held_out_cv_summary.M3 | abs ≤ 0.01 |
| C-CHEUNG-06 | Eq. 5 reward formula additive (architectural control) | engine source `f6/mechanisms` | exact_match (no `IC*ENTROPY` product term in static reward) |

## 4. Engine architectural control (C-CHEUNG-06)

Read the engine's reward-formula computation (paper Eq. 5):
> Reward = Σ salience × (1.5·surprise + 0.8·resolution + 0.5·exploration − 0.6·monotony) × fam_mod × da_gain

This is **additive** — no IC×ENTROPY product term. The Cheung interaction reproduces *only* under M2 (explicit interaction term) and is *absent* from M3 (Eq. 5 closed-form). This is the load-bearing architectural disclosure: paper §Discussion concedes Eq. 5 is additive and doesn't on its own encode the Cheung interaction. Phase 10 confirms by inspecting the engine source.

## 5. Forbidden moves

- Re-running T-R2-04 with different bootstrap seed and reporting a different CI.
- Re-fitting M2 with different control variables to nudge β closer to Cheung's −0.124.
- Editing Eq. 5 to add an interaction term retroactively (this would invalidate the paper's architectural claim that the interaction *emerges* from HTP×ICEM dynamic coupling, not from the static formula).
