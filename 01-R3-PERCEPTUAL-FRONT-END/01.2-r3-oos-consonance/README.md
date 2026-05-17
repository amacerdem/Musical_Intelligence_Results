# Phase 01.2 — R³ OOS Consonance Generalisation

**Status:** CLOSED — combined verdict across two pre-registered audit cycles.

| Cycle | Closed | Verdict | Datasets |
|---|---|---|---|
| Original (hierarchy anchor) | 2026-05-15 (iter-3 final) | 8 PASS / 2 PARTIAL / 0 FAIL across 10 paper claims | 4 corpora: 13-dyad DEV N=13 sanity, Eerola Exp3 N=617, Marjieh 5-equal N=11,754, Harrison Carillon N=113 inharmonic |
| Extended (`extended/`) | 2026-05-16 | CLOSED-PASS · 6 PASS / 3 PARTIAL / 0 FAIL · CDC 9/9 sign-consistent on all 3 R³ headline channels · HRI 4/9 | 9 datasets across 4 axes (Marjieh × 5 sub-studies + Bidelman 2009 FFR + Schwartz 2003 speech-derived + Sethares 1993 analytical + Lahdelma Indian Tension cross-cultural) |

**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217` (verified bit-identical aggregate SHA in both cycles).

## 1-paragraph summary

Phase 6 holds the full R³ Group A consonance-front-end validation portfolio. The original audit cycle reproduces the paper's Table c3_r3_oos four-dataset OOS panel (8 PASS / 2 PARTIAL / 0 FAIL across 10 paper claims under the V2-established paper→engine label cross-walk; full detail in `02-RESULTS.md`). The extended audit cycle (`extended/`) tests the same frozen front-end against nine additional consonance datasets spanning four orthogonal axes — within-corpus stimulus variation (Marjieh Study 1A harmonic, Study 1B flute / guitar / piano, Study 4A pure tone), cross-methodology (Bidelman 2009 brainstem FFR), cross-theoretical-framework (Schwartz 2003 speech-derived, Sethares 1993 analytical reference), and cross-cultural (Lahdelma Indian Tension, Carnatic / Hindustani / Indian non-musicians N=852). The cross-dataset consistency (CDC) invariant returns 9 / 9 sign-consistent on every R³ headline channel (`stumpf_fusion`, `sensory_pleasantness`, `roughness`), with six per-claim PASSes, three PARTIALs, and zero FAILs. Phase 6 therefore evaluates the consonance front-end on thirteen independent rating corpora in total; no parameter was tuned between original and extended cycles.

## Files

### Original cycle (top-level)

- `00-METHODOLOGY.md` — locked operationalisation
- `01-PROVENANCE.md` — chain of custody to V1/V2 artefacts
- `02-RESULTS.md` — full numerical report + per-claim verdict (10 paper claims)
- `03-PRE-REGISTRATION.md` — frozen decision rules + seed (frozen 2026-05-07)
- `04-INTEGRATION-LOG.md` — iteration history (3 iterations)
- `code/` — `run.sh` + `run_phase6.py` (single-script)
- `data/` — pointers only (read from `Science/datasets/consonance/`)
- `results/` — original-cycle manifest + per-dataset CSVs + raw correlations JSON + `iterations/`
- `figures/` — forest plot

### Extended cycle (`extended/`)

- `extended/README.md` — extended-cycle quick reference
- `extended/00-METHODOLOGY.md` — extended-cycle operationalisation
- `extended/01-PROVENANCE.md` — chain of custody for the 9 extended inputs
- `extended/02-RESULTS.md` — extended-cycle verdict tables
- `extended/03-PRE-REGISTRATION.md` — frozen decision rules + seed (frozen 2026-05-16)
- `extended/04-INTEGRATION-LOG.md` — extended-cycle iteration history
- `extended/code/run.sh` + `code/run_extended.py` + `code/requirements.txt`
- `extended/data/README.md` — pointers to extended inputs
- `extended/results/` — extended-cycle manifest + per-claim engine outputs + independence audit
- `extended/figures/` — extended-cycle figures
