# Phase 05.4 — Cross-Subject Voxelwise ds003720 (Routing-Ablation Test)

**Status:** CLOSED 2026-05-07
**Verdict:** **11/11 PASS** (paper-exact)
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

## Framing

ds003720 (N=4 QC-pass) = ROUTING-ABLATION TEST under stimulus-locking constraints,
NOT a population-level neural effect estimate. 4-encoder × 4-subject within-subject
contrast (16 cells).

## Headline

| Encoder | D | Held-out r | Shuffle-null pass |
|---|---|---|---|
| MI full | 26 | **+0.1653** | **4/4** |
| MI-naive | 26 | +0.0844 | 1/4 |
| Random-26 | 26 | +0.0901 | 0/4 |
| Random-768 | 768 | +0.1211 | 0/4 |
| CLAP-music-512 | 512 | +0.1382 | 2/4 |
| MERT-768 | 768 | +0.2214 (30× MI dim) | 4/4 |

MI vs MI-naive lift: **+96%** (paper claim +93%, Δ=+3pp). MI-unique R² > 0 in
**4/4** subjects (banded-ridge V6 A3, all 95% CIs exclude zero).

## Files

- `00-METHODOLOGY.md`, `01-PROVENANCE.md`, `02-RESULTS.md`, `04-INTEGRATION-LOG.md`
- `code/run.sh` + `run_phase05_4.py`
- `results/05.4_voxelwise_correlations.csv` + manifest
