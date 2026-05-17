# Phase 01.2 extended — R³ Extended OOS Consonance Battery

**Status:** CLOSED 2026-05-16 — **CLOSED-PASS** (6 PASS / 3 PARTIAL / 0 FAIL; CDC 9/9 all channels; HRI 4/9). See `02-RESULTS.md`.
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

## 1-paragraph summary

Phase 6 extended tests the R³ Group A consonance front-end against nine
consonance datasets spanning four orthogonal axes of variation: (i)
within-corpus stimulus variation (Marjieh 2024 Study 1A harmonic,
Study 1B flute / guitar / piano, Study 4A pure), (ii) cross-methodology
(Bidelman & Krishnan 2009 neural FFR), (iii) cross-theoretical-framework
(Schwartz et al. 2003 speech-derived, Sethares 1993 analytical
reference), and (iv) cross-cultural (Lahdelma et al. Indian interval
tension, Carnatic / Hindustani / Indian non-musicians, N=852). All nine
claims are scored on the same three R³ headline channels
(`stumpf_fusion`, `sensory_pleasantness`, `roughness`) under a single
locked synthesis recipe. Decision rules and the cross-dataset
consistency (CDC) and hierarchy reproduction (HRI) invariants are
frozen in `03-PRE-REGISTRATION.md` before any first run.

## Files

- `00-METHODOLOGY.md` — locked operationalisation
- `01-PROVENANCE.md` — chain-of-custody for the nine inputs
- `02-RESULTS.md` — per-claim verdicts (populated at phase close)
- `03-PRE-REGISTRATION.md` — frozen decision rules + seed
- `04-INTEGRATION-LOG.md` — iteration history (populated as runs occur)
- `code/`
  - `run.sh` — single entry point (`bash code/run.sh`)
  - `run_extended.py` — canonical reproduction script
  - `requirements.txt`
- `data/README.md` — pointers to read-only input CSVs (no vendoring)
- `results/` — manifest JSON + per-claim correlation CSV + per-dataset engine outputs
- `figures/` — forest plot (generated post-close)

## Quick start

```
cd 06-r3-oos-consonance/extended
bash code/run.sh
```

Wall-clock on Apple M2 + 8 GB unified memory, single-threaded: ~2 seconds for the full nine-claim battery (binned dyad recipe is cheap; engine extraction per stimulus < 100 ms).

## Verdict scheme

See `03-PRE-REGISTRATION.md` §"Decision rules" for full per-claim,
invariant, and axis-level rules. In brief:

- **Per claim:** PASS = ≥ 2 / 3 headline channels with |ρ| ≥ 0.60 and
  sign-consistent with the Group A theoretical convention; PARTIAL or
  FAIL otherwise.
- **CDC invariant:** ≥ 7 / 9 sign-consistent per headline channel.
- **HRI invariant:** ≥ 7 / 9 datasets reproduce the classical Western
  interval ranking at Spearman ρ ≥ 0.85 on the headline channel.
- **Axis verdict:** CLOSED-STRONG / CLOSED-PASS / CLOSED-PART /
  CLOSED-FAIL combined from the above.
