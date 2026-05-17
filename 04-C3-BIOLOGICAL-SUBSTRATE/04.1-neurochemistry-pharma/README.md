# Phase 04.1 — Neurochemistry + Pharmacological Cross-Validation

**Status:** CLOSED 2026-05-07
**Verdict:** 11 PASS / 0 CAVEAT / 0 FAIL across 10 paper claims + 1 determinism canary.
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

## 1-paragraph summary

All 10 paper neurochemistry/pharma aggregates (132/132 accumulation, 11/11 pharmacological cross-validation, antic_da↔caudate ρ=+0.933, consum_da↔NAcc ρ=+0.836, caudate-leads-NAcc 52/56 with +0.9s lag, NAcc-leads-caudate 0/56 architectural null, Ferreri levodopa>placebo>risperidone, Putkinen 7/7 μ-opioid PET regions, Mallik chills>neutral p=0.044) reproduce verbatim against V1 stored `neurochemical_validation.md`. The live engine spot-check is the strongest determinism evidence in this section: max |Δ| = 0.0 across all 4 neurochemical channels × 345 frames (1,380 values) on the P5-fifth interval WAV — exact bit-equality vs paper-disclosed engine bound 8.8×10⁻⁵.

## Files

- `00-METHODOLOGY.md` — locked operationalisation
- `01-PROVENANCE.md` — chain of custody to V1 + paper
- `02-RESULTS.md` — full numerical report
- `code/run.sh` + `run_phase04_1.py` — single entry point
- `data/README.md` — pointers
- `results/` — manifest + correlations CSV + neurochem spotcheck CSV
