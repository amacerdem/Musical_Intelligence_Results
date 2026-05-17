# Phase 03.3 — Cheung 2019 Emergent Reward Interaction

**Status:** CLOSED 2026-05-07
**Verdict:** 7 PASS / 0 CAVEAT / 0 FAIL across 6 paper claims + 1 sample-size sanity.
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

## 1-paragraph summary

All 6 paper Cheung-2019 reward-interaction claims (β(IC×ENT)=−0.158, bootstrap CI [−0.228,−0.084] containing Cheung's −0.124, ΔAIC=−33.5, held-out r=+0.615 for M3 Eq. 5, Eq. 5 architectural additivity) reproduce paper-exact from the preserved V2 T-R2-04 reanalysis artefact (2026-04-22, frozen-engine, statsmodels 0.14.6, seed=42, B=5000). Engine architectural control verified by source-tree inspection: 16 F6 reward-mechanism files contain no `IC*ENTROPY` product term, confirming the paper's claim that the Cheung interaction *emerges* from HTP×ICEM dynamic coupling rather than being hard-coded into Eq. 5. No engine pipeline call required (Cheung 2019 audio was never released; analysis is post-hoc statistical on the OSF CSV).

## Files

- `00-METHODOLOGY.md`, `01-PROVENANCE.md`, `02-RESULTS.md`, `04-INTEGRATION-LOG.md`
- `code/run.sh` + `run_phase10.py` — single entry point
- `data/README.md` — pointers
- `results/10_cheung_correlations.csv` + manifest
