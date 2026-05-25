# Phase 00.1 — paper-evidence/ (POINTERS ONLY)

This directory holds no copies of the paper. The authoritative provenance
record for every constant is the **constant-level audit** in this repository:

- `../../../_audits/audit_summary.md` — final 7-category distribution over all
  16,248 numeric constants (2026-05-17, 9 parallel agents + reconciliation)
- `../../../_audits/audit_combined.csv` — per-constant reconciled ledger
- `../01-PROVENANCE.md` — phase-local provenance narrative + classifier supersession note

## Canonical constant accounting (CODE-FIRST audit, 2026-05-17)

| Category | Count | % |
|---|---:|---:|
| A LIT-VERBATIM (literature bit-exact) | 67 | 0.41% |
| B LIT-DERIVED (literature-form analytic) | 19 | 0.12% |
| C STRUCTURAL (topology/index/anatomy) | 9,817 | 60.42% |
| D IDENTITY-PLACEHOLDER (0/1/−1/ε) | 1,182 | 7.27% |
| E ENGINEERING-CHOICE (mixer/clamp/sigmoid) | 5,157 | 31.74% |
| F HAND-SPECIFIED-DISCLOSED (6 reward weights) | 6 | 0.04% |
| G DEAD-CODE | 0 | 0% |
| **TOTAL** | **16,248** | 100% |

**Zero of 16,248 constants are calibrated against held-out cognitive, behavioural,
fMRI, or pharmacological data.** Engine source contains zero `calibrat`/`fit_to`/
`loss=`/optimizer-call patterns in the runtime call-graph.

> **Superseded classifier note.** Pre-2026-05-16 paper drafts referenced a coarser
> 5-bucket "lenient classifier" that included a calibration bucket (~246 constants)
> and a ~495 hand-tuned bucket. That classifier is **retired** doctrinally and
> operationally — see `../01-PROVENANCE.md` §"V2 → V3 supersession". The CODE-FIRST
> audit above redistributes those constants to LIT-VERBATIM (file-citation inheritance)
> or STRUCTURAL (dim/index codes); none survives as calibrated. Do not propagate the
> retired 16,191 / 7,517 / 495 / 246 figures.

## Paper cross-reference (architectural cardinalities)

The paper's §Architectural cardinalities and §Parameter provenance paragraphs state the
16,248 total and the zero-calibration headline. The numeric values reproduce exactly
against the audit ledger above; per-cardinality verdicts are in `../results/01_cardinalities_correlations.csv`.

## Engine HEAD ↔ paper version

Engine HEAD `318eb2f529d7103e8b7d80b01228357fdc4e0217` (tree aggregate SHA-256
`482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`) is the frozen
snapshot the paper was written against. Phase 00.1 reproduces every cardinality at this
HEAD with no engine modification.

## How to verify a number

For any cardinality C-CARD-NN:
1. Find it in `../results/01_cardinalities_correlations.csv` (paper value, reproduced value, deviation, tolerance, verdict).
2. Cross-check the category total against `../../../_audits/audit_summary.md`.
3. Re-run the corresponding script in `../code/`.
4. Compare against `../results/01_cardinalities_manifest.json` claim entry.

If divergence > tolerance, trigger the debug protocol in `../../../_audits/_internal/INVESTIGATION-RULES.md`.
