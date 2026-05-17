# L3 — Determinism & reproducibility (cross-axis bit-identicality)

> **Status:** **POPULATED + PASS (2026-05-09)** — 7/7 tests pass in 2.72s. 5/8 axes empirically verified; 3 multi-environment axes (L3.5/L3.6/L3.7) deferred to V-Reproduction Phase 4. See [`L3_summary.md`](L3_summary.md).

## Paper claim being defended

*max-abs-diff = 0 on the full T³ output across run, seed, thread permutation, hardware, OS axes.*

## Sub-tests planned

- L3.1 — 1,000 independent runs, same input, same process: max-abs-diff = 0
- L3.2 — Cross-process determinism (fresh interpreter): max-abs-diff = 0
- L3.3 — Cross-seed determinism (T³ has no PRNG; verify): max-abs-diff = 0
- L3.4 — Cross-thread-permutation (1, 2, 4, 8 worker threads): max-abs-diff = 0
- L3.5 — Cross-machine-reboot: max-abs-diff = 0
- L3.6 — Cross-OS (macOS vs Linux): max-abs-diff = 0 (or documented float-tolerance)
- L3.7 — Cross-hardware (M1, M2, x86) where accessible
- L3.8 — Float32 vs float64 sensitivity probe (engine pin = float32; document drift)

## Target

≥ 1,008 bit-identicality checks across 8 axes.


## Migrated content

Currently populated by `determinism_canary/` (28-pair canary). Expand to full 8-axis battery.


## Reports format

Per sub-test: `l3_determinism/tNN_<name>.py` (pytest) + `tNN_<name>.md` (formula, expected, actual, verdict).
Aggregated: `l3_determinism_summary.md` with PASS/FAIL/CAVEAT scorecard.

## Out of scope

This layer tests T³'s **functional contract only**. No cognitive/listener data; no downstream layer (C³, RAM, neurochem); no system-level claim. See `../README.md` for the full out-of-scope list.
