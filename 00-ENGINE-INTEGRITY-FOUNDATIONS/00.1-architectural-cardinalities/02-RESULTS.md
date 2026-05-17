# Phase 00.1 — Architectural Cardinalities — Results (V3 audit-anchored)

**Closed:** 2026-05-17
**Engine SHA pin:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
**Engine aggregate SHA-256:** `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`
**Audit anchor:** `_audits/audit_combined.csv` (9-agent parallel constant-level audit, 2026-05-17)
**Supersedes:** V2 5-PASS classifier (calibration category retired per zero-calibration doctrine)

## Summary

| Verdict | Count |
|---|---|
| PASS | 10 |
| FAIL | 0 |
| PARTIAL | 0 |
| CAVEAT | 0 |
| **Total** | **10** |

10/10 PASS against the constant-level provenance audit aggregate. Engine FROZEN throughout.

## Per-claim verdict table

| ID | Claim | Paper value | Reproduced | Δ | Tolerance | Verdict |
|---|---|---:|---:|---:|---|---|
| C-CARD-01-TOTAL | Total numeric constants | 16,191 | 16,248 | +57 | abs ≤ 100 | **PASS** |
| C-CARD-02-ZERO-CALIB | Calibrated against cognitive data | 0 | 0 | 0 | exact | **PASS** |
| C-CARD-03-LIT-VERBATIM | Literature-bit-exact constants | 67 | 67 | 0 | abs ≤ 5 | **PASS** |
| C-CARD-04-LIT-DERIVED | Literature-form deterministic | 19 | 19 | 0 | abs ≤ 5 | **PASS** |
| C-CARD-05-STRUCTURAL | Topology/dim/index/anatomy | 9,817 | 9,817 | 0 | abs ≤ 200 | **PASS** |
| C-CARD-06-IDENTITY | Trivial 0/1/-1/ε identity | 1,182 | 1,182 | 0 | abs ≤ 100 | **PASS** |
| C-CARD-07-ENGINEERING | Mixer/clamp/sigmoid choices | 5,157 | 5,157 | 0 | abs ≤ 200 | **PASS** |
| C-CARD-08-HAND-DISCLOSED | Reward weights (paper §Reward, **R15**: 6 code + 1 kernel identity) | 6 | 6 | 0 | exact | **PASS** |
| C-CARD-09-DEAD-CODE | Unreachable code constants | 0 | 0 | 0 | exact | **PASS** |
| C-CARD-10-DISCRETE-SELECT | Discrete structural model-selection (HTP-E3, SPH-E3) | 2 | 2 | 0 | exact | **PASS** |

## Doctrine attestation

Across the FROZEN engine tree (`Musical_Intelligence/`, 852 .py files, SHA `318eb2f5...`):

- **Zero of 16,248 numeric constants are calibrated against cognitive data.** No optimizer, no gradient descent, no MLE fit, no curve-fit-to-behaviour anywhere in the engine call-graph.
- **86 constants (0.53%) are literature-anchored** — 67 bit-exact to published primary sources (Sethares 1993, Krumhansl-Kessler 1982, IEC 61672-1, Traunmüller 1990 Bark, Stevens 1957, O'Shaughnessy 1987 mel, Tonnetz 6D); 19 derive analytically from cited form (Hasson temporal-window ladder, Plomp-Levelt 25% CB peak, Sethares parametric kernel, Berlyne 4·x·(1−x) kernel).
- **6 constants (0.04%) are paper-disclosed reward weights** in `brain/reward.py` (`w_S=1.5`, `w_R=0.8`, `w_E=0.5`, `w_M=-0.6`, `g_DA_wanting=0.6`, `g_DA_liking=0.4`). The 7th protocol-listed item (`phi_fam_star = 0.5`) is a kernel-peak mathematical identity, not a separately tunable code parameter — disclosed in **paper revision R15**.
- **9,817 constants (60.42%) are structural** — topology, dimension addresses, region/channel indices, citation metadata. No empirical content.
- **1,182 constants (7.27%) are identity placeholders** — 0, 1, -1, ε guards.
- **5,157 constants (31.74%) are author engineering choices** — mixer weights, RegionLink/NeuroLink Likert weights, sigmoid wrappers, predict-equation τ/W_TREND/W_PERIOD/W_CTX, Bayesian gain clamp [0.20, 0.80] — all documented as author choice by their module context.
- **2 mechanisms (HTP-E3, SPH-E3) include a discrete structural model-selection step** — formula-form choice between two candidates, literature-anchored (de Vries & Wurm 2023 for HTP, Bonetti 2024 for SPH). No numeric weight was fit. Documented in `_audits/2026-05-17_htp-sph-e3-structural-selection-audit.md`.

## Audit methodology

The verdict is anchored on the 2026-05-17 constant-level provenance audit (`_audits/`):

- **9 parallel audit agents** (1, 2, 3, 4, 5, 6, 7, 8, 9) attributed all 16,248 constants per `INVESTIGATION-RULES.md v1.2`
- **Agent 10 reconciliation** merged 9 CSVs into `audit_combined.csv`, performed cross-agent consistency check (pattern, citation, confidence)
- **98.10% HIGH confidence** overall (15,939/16,248)
- **46 escalations** (0.28%) — all MEDIUM/PARTIAL, none destabilize the doctrinal headline
- **R8 walker false-positives** rejected at scale (~750 by Agent 6 alone)
- **R9 form-LIT/coefficient-author** boundary applied conservatively (25 PARTIAL outcomes → E, not B)

Full reviewer-facing summary: `_audits/audit_summary.md`

## Paper revision items surfaced

| ID | Item | Paper section |
|---|---|---|
| **R15** | `phi_fam_star = 0.5` is kernel-peak identity, not 7th tunable weight (F = 6 code, 7 if counting math identity) | C³-Reward §Disclosed weights |
| **R16** | NEMAC `_SELF_SELECTED_BOOST = 1.2` code comment cites Sakakibara 2025 `d = 0.88` — paper reports Cohen's `r = 0.880`, not `d` | C³-Cognition §Limitations |
| **R17** | ESME `_ALPHA = 1.5` 'trainable' comment is developmental artifact predating zero-calibration doctrine | C³-Cognition §Limitations |
| **R18** | `brain/regions/` package is deprecated-unimported (65 metadata-only constants); MNI tuples live in `brain/ram/` | C³-Biology §Implementation note |

R15 is load-bearing for this phase (F = 6 verdict requires paper text alignment).

## V2 → V3 supersession

The V2 audit (2026-05-07) used a coarser 5-bucket classifier that included a calibration category. Per the 2026-05-16 CODE-FIRST zero-calibration doctrine (and confirmed by the V3 audit: zero `calibrat` references in engine source, zero constants empirically attributed to a calibration category under the V3 classifier), the calibration category has been **retired**. V2's 5 PASS verdict is superseded by V3's 10 PASS verdict on a more granular and more honest 7-category taxonomy.

## Reading order

1. `00-METHODOLOGY.md` — V3 methodology and 7-category taxonomy
2. `01-PROVENANCE.md` — paper-line anchors + audit traceability
3. `02-RESULTS.md` (this file) — 10/10 PASS verdict
4. `code/run_phase1.py` — reproduces the verdict against `_audits/audit_combined.csv`
5. `_audits/audit_summary.md` — full audit synthesis with per-agent breakdowns

## How to reproduce

```bash
bash code/run.sh
```

Reads the audit aggregate, verifies the 7-category distribution against paper headlines, writes `results/01_cardinalities_correlations.csv`. ~1 second wall-clock.

## Output integrity

- `results/01_cardinalities_correlations.csv` — 10 rows, per-claim verdict
- Engine state preserved at SHA `318eb2f5...`; no modifications introduced.
