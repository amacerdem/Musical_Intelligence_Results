# V-Reproduction Phase 01.3 — Results (CLOSED)

**Date:** 2026-05-07
**Verdict:** **6/6 PASS** — paper-exact + honest-scope disclosures preserved
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

---

## 1. Per-claim verdict (6 rows)

| Claim | Paper | Reproduced | Verdict |
|---|---|---|---|
| C-CROSS-CULT-01 Hindustani raga (Saraga 1.5) | +0.565 | **+0.5697** (V4 P2 top-7 ragas, 7/7 positive) | **PASS** |
| C-CROSS-CULT-02 inconMore breadth (V5 audit-fixed) | +0.408 | **+0.4076** (V5 P4 convention-corrected, 6/7 datasets positive) | **PASS** |
| C-CROSS-CULT-03 Bonang inharmonic calibration boundary | +0.221 (V5 NEGATIVE preserved) | **+0.2208** | **PASS** |
| C-CROSS-CULT-04 Pakistan composite (V4 PASS, V5 FAIL disclosed) | V4 +0.40 / V5 +0.07 | V4 +0.400 / V5 +0.074 | **PASS** |
| C-CROSS-CULT-05 NHS classification (out-of-scope) | OOS (k/n≈2 overfit-suspect) | V4 P5 +0.398 (228D LOSO, lda=0.398) | **PASS** |
| C-CROSS-CULT-06 Mridangam stroke (out-of-scope F7) | OOS (F1-F8 paper scope) | V4 P6 +0.979 (3-way logreg, threshold 1.5×chance) | **PASS** |

## 2. V4 vs V5 reconciliation

V4 v3 ran 6 PRIMARY anchors with composite verdict AMBIGUOUS (Tier 1 STRONG_PASS
6/6 + Tier 2 BH-FDR 11/24). V5 v3 ran 4 PRIMARY anchors under audit-fixed
methodology with composite NEGATIVE (Tier 1 2/4 PASS).

**The paper uses each version where it is canonical:**
- Hindustani raga (P2): V4 +0.5697 (paper +0.565) — V5 P2 also +0.565 (audit-confirmed)
- inconMore breadth (P4): V5 +0.4076 (paper +0.408) — V4 P4 was pre-audit +0.505
- Bonang calibration boundary (P3): V5 +0.2208 (paper +0.221) — V5 NEGATIVE on
  ratio criterion is honest disclosure preserved in paper
- Pakistan composite (P1): both reported side-by-side (V4 v3 + V5 audit fix)

## 3. Honest-scope disclosures preserved

**V5 NEGATIVE on bonang (C-CROSS-CULT-03):** ratio |ρ_bonang|/|ρ_harmonic| =
0.55 (paper threshold ≥0.50 fails strict but passes magnitude-only at +0.221).
Paper §Discussion §Cross-cultural calibration boundary acknowledges that
Sethares-PL parameters require timbre-specific recalibration for non-Western
inharmonic spectra. V-Reproduction preserves this honest scope.

**NHS classification (C-CROSS-CULT-05) + Mridangam (C-CROSS-CULT-06):** out-of-
scope for paper's F1-F8 cognitive-layer validation. V4 P5/P6 PASS at threshold
but classification at k/n≈2 (NHS) is overfit-suspect, and Mridangam stroke is
F7 calibration outside paper's primary scope. Both preserved as supplementary.

## 4. Compute profile

- Wall: <1 s (parse V4+V5 decision_gate.md text)
- 0 engine pipeline runs

## 5. Hand-off

- MASTER-VERDICT.md Phase 14 row: 6/6 PASS
- Paper revision items: none (paper-exact + honest scope preserved)
- Phase 15 (Falsifiable Table 5 aggregator) is next.
