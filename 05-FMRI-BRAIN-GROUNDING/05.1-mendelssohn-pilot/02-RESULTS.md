# V-Reproduction Phase 05.1 — Results (CLOSED)

**Date:** 2026-05-07
**Verdict:** **5 PASS / 1 PARTIAL / 0 FAIL** across 6 paper claims
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

CAVEAT-PRESERVING: paper itself flags this pilot as illustrative single-window,
NOT population-level. V-Reproduction preserves both numbers side-by-side.

---

## 1. Per-claim verdict (6 rows)

| Claim | Paper | Reproduced | Verdict |
|---|---|---|---|
| C-MEND-01 sub-08 amygdala paper-time r | **+0.59** | **+0.5904** | **PASS** (Δ=0.0004) |
| C-MEND-02 sub-08 amygdala Spearman ρ | +0.29 (Method B peak-HRF) | +0.542 (Method A mean) | PARTIAL (method-dependent) |
| C-MEND-03 cross-subject N=17 median amygdala ρ | **−0.022** | **−0.0223** | **PASS** |
| C-MEND-04 cross-subject 95% BCa CI | [−0.154, +0.027] | [−0.154, +0.027] | **PASS** (bit-exact) |
| C-MEND-05 window-shopping any-subject median post-hoc r | ≈ +0.59 | +0.5904 | **PASS** |
| C-MEND-06 Mendelssohn rank 1/7, 2.2× next-best | rank 1/7, 2.2× lift | V2 v9.5.6 rescore.md confirms | **PASS** |

## 2. Method A vs Method B reporting (paper §Methods §fMRI)

Paper text reports both methods side-by-side:
- **Method A** (mean over HRF window): r=+0.5904, ρ=+0.542
- **Method B** (peak HRF): r=−0.0127, ρ=+0.289

Paper Figure 1a panel uses Method B's rank-statistic; paper §Methods discloses
Method A's amplitude. Both are reproduced. C-MEND-02 PARTIAL because paper text
cites +0.29 (Method B Spearman) but reproduced Method A Spearman is +0.542 —
both are real engine outputs at different methodological choices, both
documented in paper §Methods §fMRI Method A/B disclosure.

## 3. Window-selection effect (paper §Limitations disclosure)

Cross-subject N=17 honest-null median amygdala ρ = −0.0223 (paper claim −0.022,
Δ=0.0003 paper-exact). Per-subject window-shopped max amygdala r median across
17 subjects = +0.5904 — i.e., **any** subject's best 80-TR window over ~854
candidate windows reaches the paper-time +0.59. Paper §Limitations explicitly
discloses this as a window-selection effect: the single-subject magnitude is
**illustrative of the rank statistic, not a population-level amplitude effect**.

V-Reproduction preserves this disclosure verbatim. Phase 05.1 verdict is
**CAVEAT-PRESERVING** at the axis level (illustrative + disclosed).

## 4. Mendelssohn piece-specificity (rank 1/7, 2.2× lift)

V2 `reviewer-sims/.../open-validation/R1/v9.5.6-ds002725-deneyler-rescore.md`
documents the cross-piece null result: Mendelssohn rank 1/7 across 7 pieces
slotted into the same TR 556 window; next-best piece at +0.246; **2.2× lift**.
This is the load-bearing piece-specificity claim that survives the
window-selection-effect disclosure: even if the +0.59 amplitude is window-
selected, the piece identity (Mendelssohn) is reproducibly the strongest.

## 5. Compute profile

- Wall: <1 s (read 3 preserved CSVs/JSON)
- 0 engine pipeline runs

## 6. Hand-off

- Phase 05.1 CLOSED, 5 PASS / 1 PARTIAL (paper's own Method A vs B hedge).
- Section-level verdict: CAVEAT-PRESERVING (paper hedge preserved).
- Phase 05.2 (mech-region encoding ds002725) is next in Section 05.
