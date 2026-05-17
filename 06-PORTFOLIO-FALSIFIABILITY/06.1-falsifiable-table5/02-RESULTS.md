# V-Reproduction Phase 06.1 — Results (CLOSED)

**Date:** 2026-05-07
**Verdict:** **5/5 PASS** — all 5 paper Falsifiable Table 5 tests survive
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

---

## Falsifiable Table 5 — paper §Methods §Falsifiable predictions

These 5 tests were pre-committed by the paper as falsification points. If any
fails, the corresponding architectural claim is falsified. **All 5 survive.**

| # | Test | Paper claim | Reproduced | Verdict |
|---|---|---|---|---|
| FT5-#1 | Carillon ρ_stumpf | −0.824 | −0.8297 (Phase 01.2) | **PASS** |
| FT5-#2 | ds003720 voxelwise contrast | MI 4/4 vs MI-naive 1/4 vs Random 0/4 | 4/4 / 1/4 / 0/4 (Phase 05.4) | **PASS** |
| FT5-#3 | Cheung interaction | β=−0.158 + Cheung's −0.124 in CI | β=−0.158 + IN CI (Phase 03.3) | **PASS** |
| FT5-#4 | Mendelssohn piece-specificity | rank 1/7 + 2.2× lift | rank 1/7 + 2.2× (Phase 05.1) | **PASS** |
| FT5-#5 | Pre-reg mech×region | 16/22 BH-FDR + Δ=+0.105 | 16/22 verbatim (Phase 05.2) | **PASS** |

## Compute profile

- Wall: <1 s (read 5 phase CSVs, aggregate)

## Hand-off

- Phase 06.1 CLOSED, 5/5 PASS.
- **Aggregate verdict:** Falsifiable Table 5 = ALL FIVE pre-committed falsification
  tests SURVIVE. The paper's pre-registered falsification points each have a
  PASS verdict from V-Reproduction.
- Phase 16 (Paper-wide BB-FDR aggregation) is next.
