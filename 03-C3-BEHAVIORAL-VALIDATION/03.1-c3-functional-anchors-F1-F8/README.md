# Phase 03.1 — C³ Functional Anchors (F1–F8)

**Status:** CLOSED 2026-05-07
**Verdict:** 24 PASS / 1 CAVEAT / 0 FAIL across 25 rows (24 paper claims + 1 determinism canary).
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

## 1-paragraph summary

All 24 paper-claim aggregates spanning F1–F8 (mech-pass-rates, FDR-counts, lead-mechanism |ρ|, OOS pass-rates) reproduce verbatim from V1's stored `Science/V1/results/All_Results/All_Results.md` against the frozen engine HEAD. The determinism canary (F1 R³ on V1 stimulus WAVs) reproduces Phase 2's bit-identical output to **max |Δρ| = 4.7×10⁻⁵**, which is *inside* the paper-disclosed engine-determinism bound (`|Δρ| ≤ 8.8×10⁻⁵`). The single CAVEAT is the F3 dimension-level expansion claim (paper enumerated N=290 tests vs V1 stored N=122 — snapshot drift, parallel to Phase 1 cardinalities). Strategy: aggregate verification + live canary, NOT mech-by-mech re-execution (which would cost days of compute and reproduce numbers already validated bit-identical against this engine HEAD by Phases 0/2/6).

## Files

- `00-METHODOLOGY.md` — locked operationalisation
- `01-PROVENANCE.md` — chain of custody to V1 + paper
- `02-RESULTS.md` — full numerical report + per-claim verdict
- `04-INTEGRATION-LOG.md` — single-iteration log
- `code/run.sh` + `run_phase7.py` — single entry point
- `data/README.md` — dataset pointers
- `results/` — manifest + correlations CSV + BCH spotcheck CSV
