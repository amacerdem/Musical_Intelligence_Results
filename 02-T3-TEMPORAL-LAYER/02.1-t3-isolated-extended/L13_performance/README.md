# L13 — Performance probe (T³ stage budget on consumer hardware)

> **Status:** **POPULATED + PASS (2026-05-09)** — 5/5 tests pass in 0.56s. Median 478K fps (2,777× real-time floor); peak RSS 345 MB < 465 MB ceiling. See [`L13_summary.md`](L13_summary.md).

## Paper claim being defended

*T³ stage executes within its share of the documented MI total budget (3.31× real-time on M2 8GB, single-threaded) for the full demand registry.*

## Sub-tests planned

- L13.1 — T³ stage real-time factor: median over 30 runs × 30 s clips, single-threaded.
- L13.2 — Frame rate (fps) for T³ stage alone: median ≥ documented threshold.
- L13.3 — Peak resident memory for T³ stage: ≤ documented budget.
- L13.4 — Memory scaling: linear in clip duration (no quadratic blow-up from horizon windows).
- L13.5 — Mech-only vs full-registry compute: ~644 vs ~8,600 tuples, scaling as documented.
- L13.6 — Cold-start vs warm-start gap quantified.
- L13.7 — V-Reproduction reproducibility: real-time factor reproduces across re-runs within ±10%.

## Target

7 performance probes with hardware fingerprint.



## Reports format

Per sub-test: `l13_performance/tNN_<name>.py` (pytest) + `tNN_<name>.md` (formula, expected, actual, verdict).
Aggregated: `l13_performance_summary.md` with PASS/FAIL/CAVEAT scorecard.

## Out of scope

This layer tests T³'s **functional contract only**. No cognitive/listener data; no downstream layer (C³, RAM, neurochem); no system-level claim. See `../README.md` for the full out-of-scope list.
