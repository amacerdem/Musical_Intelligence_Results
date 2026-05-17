# L10 — Cross-implementation cross-validation

> **Status:** skeleton — test plan defined, implementations to be written.

## Paper claim being defended

*Each morph + law operator is correct against an independent re-implementation, not just against itself.*

## Sub-tests planned

- L10.1 — Pure-numpy re-impl of M0–M23: 24 morph operators on 8 stimulus families.
- L10.2 — Pure-numpy re-impl of L0/L1/L2 attention masking.
- L10.3 — Shared exponential kernel: `np.exp(-3*(1-p))` independent route, bit-identical match.
- L10.4 — Permutation-null structural sparsity: shuffling demand registry preserves cardinality bounds. *Currently populated by* `permutation_null/`.

## Target

≥ 30 cross-impl certificates.


## Migrated content

Currently populated by `permutation_null/`. Expand to per-morph cross-impl.


## Reports format

Per sub-test: `l10_cross_impl/tNN_<name>.py` (pytest) + `tNN_<name>.md` (formula, expected, actual, verdict).
Aggregated: `l10_cross_impl_summary.md` with PASS/FAIL/CAVEAT scorecard.

## Out of scope

This layer tests T³'s **functional contract only**. No cognitive/listener data; no downstream layer (C³, RAM, neurochem); no system-level claim. See `../README.md` for the full out-of-scope list.
