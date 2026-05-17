# L1 — Specification compliance (per-tuple formula re-implementation)

> **Status:** **SAMPLE POPULATED + PASS (2026-05-09)** — 20/20 sample tests pass in 0.33s (M0 across 4 horizons × 3 stimuli × 3 laws + kernel re-impl across 7 window sizes). Full battery (24 morphs × 32 horizons × 3 laws = 2,304 sub-tests, plus stimulus-family × frame-position expansion) is mechanical extension. See [`L1_summary.md`](L1_summary.md).

## Paper claim being defended

*Every active 4-tuple `(r, h, m, ℓ)` in the demand registry equals its documented formula bit-identically.*

## Sub-tests planned

- L1.1 — For each of 24 morphs, re-implement in pure numpy from spec; compare across 8 R³ stimulus families (silence, A4 tone, sweep, real audio, white noise, AM-modulated, Dirac, composite).
- L1.2 — For each of 3 laws (L0 memory, L1 forward, L2 integration), verify temporal direction by perturbation: zeroing samples at t+k for k>0 must (L0) leave output at t unchanged, (L1) change it, (L2) change it.
- L1.3 — Shared exponential attention kernel `exp(−3·(1−p))`: re-impl from constants module, compare bit-identically across 32 horizons.
- L1.4 — Newest-to-oldest weight ratio = e³ ≈ 20.09 verified analytically for each horizon.

## Target

~644 active mech-only tuples × 8 stimuli = ~5,152 sub-tests + 3 law direction tests + 32 kernel checks.



## Reports format

Per sub-test: `l1_spec_compliance/tNN_<name>.py` (pytest) + `tNN_<name>.md` (formula, expected, actual, verdict).
Aggregated: `l1_spec_compliance_summary.md` with PASS/FAIL/CAVEAT scorecard.

## Out of scope

This layer tests T³'s **functional contract only**. No cognitive/listener data; no downstream layer (C³, RAM, neurochem); no system-level claim. See `../README.md` for the full out-of-scope list.
