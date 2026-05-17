# Phase 01.3 Cross-Cultural — Chill-Standard Upgrade (STRUCTURAL EXCEPTION)

**Frozen:** 2026-05-12 | **Engine SHA:** `482ade45c50f5d3...`
**Companion:** `02-RESULTS.md` (existing Phase 14 closure)

---

## §0 Why this is a structural exception

The chill-standard methodology (LOSO inter-rater ceiling + bootstrap CI + ceiling-relative MI) requires **per-rater Spearman-target measurements**. Phase 14's six claims do NOT have this structure — none of them are per-rater human Spearman correlations.

## §1 Per-claim structural breakdown

| Claim | Target type | Per-rater? | LOSO ceiling applicable? |
|---|---|---|---|
| C-CROSS-CULT-01 Hindustani raga (+0.565) | Pitch-class identity match (engine vs canonical raga template) | NO (acoustic feature → reference template) | NO |
| C-CROSS-CULT-02 inconMore breadth (+0.408) | Signed ρ aggregated across 7 published consonance studies | NO (meta-analysis of published correlations) | NO |
| C-CROSS-CULT-03 Bonang boundary (+0.221) | Ratio |ρ_bonang|/|ρ_harmonic| as calibration test | NO (ratio threshold, not Spearman target) | NO |
| C-CROSS-CULT-04 Pakistan composite (V4/V5) | Audit-methodology disagreement comparison | NO (methodological reconciliation) | NO |
| C-CROSS-CULT-05 NHS classification (+0.398) | LDA classification accuracy across 86 societies (228D LOSO over societies) | NO at SUBJECT level; YES at SOCIETY level (already done) | DIFFERENT KIND |
| C-CROSS-CULT-06 Mridangam stroke (+0.979) | F7 motor 3-way logistic regression | NO (classification accuracy, not rating Spearman) | NO |

## §2 Why no ceiling is computed

The chill, consonance, and Cheung tests all share a structure:
- **Target:** per-rater Spearman or rank-correlation values
- **Ceiling:** how reliably do individual raters agree with N-1 consensus on the same Spearman scale?
- **MI comparison:** MI's measured ρ vs ceiling

Phase 14 tests do NOT share this structure. Each test has its own appropriate evaluation paradigm:
- Acoustic feature matching → templates, not subject ratings
- Meta-analysis → already aggregates across publications
- Classification accuracy → chance baseline (e.g., 1/N for N classes), not LOSO

Forcing a chill-standard ceiling on these tests would either be (a) meaningless (no per-rater data) or (b) deceptive (computing a ceiling from a different paradigm).

## §3 Honest alternative — paradigm-appropriate baselines

Each Phase 14 test has its own paper-grade baseline already disclosed:

- **Hindustani raga**: 7/7 ragas positive direction (paper-grade unanimity)
- **inconMore**: cross-publication signed-ρ at +0.408 with 6/7 datasets positive
- **Bonang**: V5 honest-scope NEGATIVE preserved (paper §Discussion calibration boundary)
- **NHS**: LDA classification at +0.398 vs k/n≈2 chance baseline — disclosed as overfit-suspect
- **Mridangam**: 3-way classification at +0.979 vs 1/3 chance baseline

These are appropriate baselines for their paradigms. **Adding a chill-standard LOSO ceiling would not improve interpretability** because the tests are not Spearman-on-ratings.

## §4 What this means for the paper

Phase 14 results in the main paper (cross-cultural reach disclosure in §Limitations and §Cross-cultural) already use paradigm-appropriate framings:
- "7/7 ragas positive" (Hindustani)
- "+0.408 with 6/7 datasets positive" (inconMore)
- "boundary at ρ_bonang/ρ_harmonic = 0.55" (Bonang)
- "$k/n \approx 2$ overfit-suspect" (NHS)

**No paper text change is required** for Phase 14. The chill-standard framework does not apply.

## §5 Where the chill-standard DOES apply nearby

Phase 06 R³ consonance (Marjieh, Harrison) — chill-standard LOSO ceiling applied at `Science/V-Reproduction/06-r3-oos-consonance/CHILL_STANDARD_UPGRADE.md`.

## §6 Provenance

This document is the disclosure of structural non-applicability. No new code or computation was added. The Phase 14 closure status (CLOSED 2026-05-07, 6/6 PASS) is unchanged.
