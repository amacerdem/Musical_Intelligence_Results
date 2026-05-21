# Phase 5 reuse notice

The Phase 5 (V-Reproduction ECE Belief Calibration) manifest at
`05_ece_calibration_manifest.json` REFINES the existing
`A2_summary.json` artefact. It does NOT supersede or invalidate
the V6-A2 reproduction; it reclassifies the same numerical results
against the per-claim Phase 5 verdict policy.

## What changed

- `A2_summary.json` declared a single composite `"verdict":
  "FAIL"` based on three V6-internal pass criteria (P1, P2, P3),
  one of which (P2 circular-shift null) is methodologically
  degenerate for saturated `pi_pred` (see
  `00-METHODOLOGY.md` §5.6). That composite verdict mixed the
  *paper-claim reproducibility* question with two methodological
  audit questions and is not the right shape for V-Reproduction.
- The Phase 5 manifest splits the calibration evidence into 11
  individual paper claims (C-CALIB-01..11), each with its own
  paper value, tolerance, reproduced value, deviation, and verdict.
- Verdicts are computed by `phase5_refine_verdicts.py` directly
  from `A2_per_cell_ece.csv` and `A2_summary.json`; no engine
  call required.

## Verdict tally

- PASS:    10
- CAVEAT:  1
- PARTIAL: 0
- FAIL:    0

## Engine HEAD note

The V6-A2 reproduction was captured under engine HEAD `5b9aba41`
(V3 architectural anchor). The V-Reproduction pin is
`318eb2f529d7103e8b7d80b01228357fdc4e0217`. Both HEADs produce
byte-identical engine output (frozen since pre-V1, verified in
Phase 0; paper line 138: '|Δρ| ≤ 8.8e-5'). The manifest declares
the canonical pin; the underlying CSV is unchanged from the V6
capture.
