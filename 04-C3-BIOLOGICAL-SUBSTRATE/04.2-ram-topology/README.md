# Phase 04.2 — RAM Topology

**Status:** CLOSED 2026-05-07
**Verdict:** 5 PASS / 0 CAVEAT / 0 FAIL across 5 paper anchors (V3 audit-anchored).
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

## 1-paragraph summary

All 5 RAM-topology paper anchors reproduce exactly from the V2 T-R1-08 preserved permutation-null artefacts: the headline 28/31 ≤10mm coord-match, both Null-1 centroid-relocation and Null-2 label-shuffle at p<0.0001, the 26/29 no-proxy robustness, and the radius-stability claim of 28 matches at 8/10/12 mm. The literature coordinate set (31-row coord-eligible subset) is vendored alongside the permutation-null CSVs under `datasets/paper-anchors/ram-topology/`. This phase is CSV-anchored — no live engine run is required; engine bit-state stability is independently verified at Phase 04.1 (4-channel neurochem max |Δ|=0.0) and Phase 02.1 (T³ isolated-extended 207 sub-tests).

## Files

- `00-METHODOLOGY.md`, `01-PROVENANCE.md`, `02-RESULTS.md`
- `code/run.sh` + `run_phase04_2.py` — single entry point
- `data/README.md` — pointers
- `results/04.2_ram_topology_correlations.csv` + manifest
