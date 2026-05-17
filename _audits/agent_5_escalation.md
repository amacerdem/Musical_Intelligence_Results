# Agent 5 — Escalation Queue

**Scope:** `brain/functions/f6/*` + `brain/reward.py`
**Constants audited:** 1,415
**Total escalations:** 3 (formal) + 1 critical structural finding

---

## ESC-1 (CRITICAL — F-category enforcement)

- **Constant ID:** N/A — structural absence
- **File:** `brain/reward.py`
- **Name + Value:** `phi_fam_star = 0.5` (per protocol F-list item #5)
- **Tentative category:** F (per protocol) — but NO code-named constant matches
- **Tentative confidence:** N/A
- **Issue:** The protocol enumerates 7 F-category constants; the 5th is `phi_fam_star = 0.5` (familiarity peak). In `brain/reward.py`, the familiarity inverted-U appears at line 83 as `fam_mod = 0.5 + 0.5 * 4.0 * f * (1.0 - f)`. **The peak f = 0.5 is a MATHEMATICAL IDENTITY** — the parabola `4f(1-f)` peaks at f = 0.5 by definition of unit-interval-normalised quadratic; there is no `phi_fam_star = 0.5` named constant in the code. The two `0.5` values on line 83 are (a) the additive offset `0.5 + ...` (so fam_mod ∈ [0.5, 1.0]) and (b) the scale on the inverted-U term — NEITHER is the "familiarity peak position".
- **Web search performed:** N/A (structural identity)
- **Web search outcome:** N/A
- **Verification source attempted:** Berlyne 1971 inverted-U (form, not coefficient) — `4x(1-x)` peaks at x=0.5 by trivial calculus.
- **Recommended resolution:**
  1. Either update paper §Reward to disclose only 6 hand-tuned weights (4 mixer + 2 DA-split), describing `phi_fam_star = 0.5` as a mathematical-identity peak of the disclosed `4f(1-f)` kernel (no separately tunable parameter), OR
  2. Make `phi_fam_star` an explicit named constant if the paper still wishes to enumerate it as one of 7 disclosed weights.
- **Agent:** Agent 5
- **Resolution this audit:** Tagged 6 F constants (W_SURPRISE, W_RESOLUTION, W_EXPLORATION, W_MONOTONY, g_DA_wanting = 0.6, g_DA_liking = 0.4). Did NOT inflate the count to 7 by mis-categorising one of the two 0.5 values on line 83 — would have violated the F-closed-list rule.

---

## ESC-2

- **Constant ID:** AGT5_xxxx (line 83 of `brain/reward.py`, value `4.0`)
- **File:** `brain/reward.py:83`
- **Name + Value:** `<expr-R> = 4.0` in `fam_mod = 0.5 + 0.5 * 4.0 * f * (1.0 - f)`
- **Tentative category:** B (LIT-DERIVED) with PARTIAL
- **Tentative confidence:** MEDIUM
- **Issue:** The `4.0` is the canonical normalisation for the Berlyne inverted-U `4x(1-x)` so the peak height is 1.0 on the unit interval. Berlyne 1971 publishes the inverted-U qualitatively; the specific `4x(1-x)` parameterisation is the textbook unit-interval-normalised quadratic, not a numerical value bit-published in Berlyne 1971. Per Rule R9 this is form-LIT (Berlyne) with mathematical-identity coefficient — sits between A (LIT-VERBATIM, value-match) and pure E.
- **Web search performed:** Yes (1 attempt for Berlyne 1971 inverted-U + formula).
- **Web search outcome:** PARTIAL — inverted-U doctrine confirmed; specific `4x(1-x)` formula not surfaced in abstracts.
- **Verification source attempted:** Berlyne 1971 *Aesthetics and Psychobiology*; secondary citations (Althuizen 2021, Berlyne Revisited 2016).
- **Recommended resolution:** Treat as B-PARTIAL (LIT-DERIVED, form-LIT, coefficient = unit-interval normalisation identity). Manual reviewer could either (a) upgrade to A if Berlyne 1971 §X explicitly publishes `4x(1-x)`, or (b) downgrade to E if reviewer treats normalisation as engine choice.
- **Agent:** Agent 5

---

## ESC-3

- **Constant ID:** AGT5_xxxx (line 44 of `brain/functions/f6/mechanisms/ssri/temporal_integration.py`)
- **File:** `brain/functions/f6/mechanisms/ssri/temporal_integration.py:44`
- **Name + Value:** `_KAPPA_SOCIAL = 0.60`
- **Tentative category:** E (ENGINEERING-CHOICE) with PARTIAL
- **Tentative confidence:** MEDIUM
- **Issue:** Comment on line 44 cites "Dunbar 2012" as anchor for social amplification. SSRI module docstring describes 1.3-1.8x amplification range from Dunbar. The 0.60 coefficient is author re-parameterisation: Dunbar 2012 publishes synchronized-music bonding effects qualitatively + pain-threshold effects (Cohen et al. 2010, Tarr et al. 2014) but no specific `kappa = 0.60` coefficient. Per Rule R9 (form-LIT, coefficient author re-parameterisation) → E with PARTIAL.
- **Web search performed:** Yes (1 attempt for Dunbar 2012 social bonding music synchronized amplification).
- **Web search outcome:** PARTIAL — bonding/amplification framework confirmed; specific 1.3-1.8x and 0.60 not surfaced.
- **Verification source attempted:** Dunbar 2012 + Savage 2021 (BBS review); Cohen-Tarr synchronized-exertion endorphin literature.
- **Recommended resolution:** E with PARTIAL stands; document in paper §Limitations alongside other Rule-R9 cases.
- **Agent:** Agent 5

---

## ESC-4

- **Constant ID:** AGT5_xxxx (line 107 of `brain/functions/f6/mechanisms/ssri/temporal_integration.py`)
- **File:** `brain/functions/f6/mechanisms/ssri/temporal_integration.py:107`
- **Name + Value:** `clamp(1.0, 3.0)` — upper bound `3.0`
- **Tentative category:** E (ENGINEERING-CHOICE)
- **Tentative confidence:** MEDIUM
- **Issue:** Clamp upper bound `3.0` corresponds to maximum social amplification (Dunbar 2012 publishes 1.3-1.8x range; `3.0` is a defensive upper bound). Author-chosen clamp, not literature-published.
- **Web search performed:** Same as ESC-3 (Dunbar 2012).
- **Web search outcome:** NEGATIVE for `3.0` specifically.
- **Verification source attempted:** Dunbar 2012.
- **Recommended resolution:** E (E2 clamp endpoint) stands. Defensive saturation guard for the multiplicative SA computation.
- **Agent:** Agent 5

---

## Summary

| # | Type | Severity | Affects F count? |
|---|------|----------|------------------|
| ESC-1 | F-list structural mismatch | CRITICAL | YES — F=6 in code, protocol says 7 |
| ESC-2 | Berlyne `4.0` coefficient | MEDIUM | NO |
| ESC-3 | `_KAPPA_SOCIAL` Dunbar | MEDIUM | NO |
| ESC-4 | SSRI clamp `3.0` | LOW | NO |

**Critical finding (ESC-1):** Only **6 F-category constants** appear as named/expression code values in `brain/reward.py`. The protocol's 7th item `phi_fam_star = 0.5` is the mathematical-identity peak of the `4f(1-f)` kernel, not a separately tunable code parameter. Paper disclosure may need adjustment to either disclose 6 weights or to explicitly name `phi_fam_star` in code.
