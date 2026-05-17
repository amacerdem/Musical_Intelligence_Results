# Phase 01.3 — Cross-Cultural Honest Reproduction

**Status:** CLOSED 2026-05-07
**Verdict:** 6/6 PASS — paper-exact + honest-scope disclosures preserved
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

## Headline

| Anchor | Paper | Reproduced |
|---|---|---|
| Hindustani raga (Saraga 1.5) | +0.565 | **+0.5697** |
| inconMore breadth (V5 audit-fixed) | +0.408 | **+0.4076** |
| Bonang inharmonic (V5 NEGATIVE) | +0.221 | **+0.2208** |
| Pakistan composite | V4 +0.40 / V5 +0.07 (disclosed) | exact |
| NHS classification (out-of-scope) | OOS | V4 P5 +0.398 |
| Mridangam stroke (out-of-scope F7) | OOS | V4 P6 +0.979 |

V5 NEGATIVE on bonang + NHS/Mridangam out-of-scope disclosures preserved
verbatim per paper §Discussion §Cross-cultural calibration boundary.

## Files

- `00-METHODOLOGY.md`, `01-PROVENANCE.md`, `02-RESULTS.md`, `04-INTEGRATION-LOG.md`
- `code/run.sh` + `run_phase14.py`
- `results/14_cross_cultural_correlations.csv` + manifest
