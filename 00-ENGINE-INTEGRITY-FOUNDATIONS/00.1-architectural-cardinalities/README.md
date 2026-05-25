# Phase 00.1 — Architectural Cardinalities (V3 audit-anchored)

**Status:** Closed 2026-05-17 (V3 audit-anchored)
**Verdict:** **10 / 10 PASS**
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
**Aggregate SHA:** `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`
**Supersedes:** V2 5-PASS classifier (retired per zero-calibration doctrine)

This phase verifies the architectural inventory of the FROZEN engine against the constant-level provenance audit (`_audits/audit_combined.csv`, 9 parallel agents + Agent 10 reconciliation, 2026-05-17). 7-category attribution distribution and zero-calibration attestation.

## Quick reference

| Claim | Paper | Reproduced | Tolerance | Verdict |
|---|---|---|---|---|
| C-CARD-01-TOTAL | 16,248 numeric constants | 16,248 | abs ≤ 100 | PASS (exact) |
| C-CARD-02-ZERO-CALIB | 0 calibrated against cognitive data | 0 | exact | PASS |
| C-CARD-03-LIT-VERBATIM | 67 literature-bit-exact | 67 | abs ≤ 5 | PASS |
| C-CARD-04-LIT-DERIVED | 19 literature-form deterministic | 19 | abs ≤ 5 | PASS |
| C-CARD-05-STRUCTURAL | 9,817 topology/anatomy | 9,817 | abs ≤ 200 | PASS |
| C-CARD-06-IDENTITY | 1,182 trivial 0/1/-1/ε | 1,182 | abs ≤ 100 | PASS |
| C-CARD-07-ENGINEERING | 5,157 mixer/clamp/sigmoid | 5,157 | abs ≤ 200 | PASS |
| C-CARD-08-HAND-DISCLOSED | 6 reward weights (R15) | 6 | exact | PASS |
| C-CARD-09-DEAD-CODE | 0 unreachable | 0 | exact | PASS |
| C-CARD-10-DISCRETE-SELECT | 2 mechs structural pick (HTP-E3, SPH-E3) | 2 | exact | PASS |

**Aggregate: 10 / 10 PASS.**

## Doctrine attestation (headline)

> Across 16,248 numeric constants in the FROZEN Musical Intelligence engine, **zero are calibrated against cognitive data**. 86 (0.53%) are literature-anchored, 6 (0.04%) are paper-disclosed reward weights, and the remaining 16,156 are structural topology, identity placeholders, or transparent engineering choices.

## How to run

```bash
bash code/run.sh
```

Reads the audit aggregate at `_audits/audit_combined.csv`, verifies the 7-category distribution against paper headlines (post R15-R18 revision), and writes the verdict CSV. ~1 second wall-clock.

## Outputs

- `results/01_cardinalities_correlations.csv` — 10-row per-claim verdict
- Documented in `02-RESULTS.md`

## Reading order

1. `00-METHODOLOGY.md` — V3 7-category taxonomy + audit methodology
2. `01-PROVENANCE.md` — paper-line anchors + audit traceability + R15-R18 paper revision items
3. `02-RESULTS.md` — full 10/10 PASS verdict table + doctrine attestation
4. `code/run_phase1.py` — reproduces verdict from `_audits/audit_combined.csv`
5. `_audits/audit_summary.md` — full audit reviewer-facing synthesis

## What this phase supersedes

V2 (2026-05-07, paper-anchor V2 classifier) reported 5 / 5 PASS on a coarser 5-bucket classifier that included a calibration category. Per the 2026-05-16 CODE-FIRST zero-calibration doctrine and the 2026-05-17 constant-level audit (zero `calibrat` references in engine source; zero constants empirically attributed to a calibration bucket), the calibration category is **retired**. V3 supersedes V2 entirely with a more granular and more honest 7-category taxonomy.
