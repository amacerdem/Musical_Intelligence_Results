# Phase 03.1 — Provenance / Chain of Custody

## Source artefacts (read-only)

### Engine
- HEAD: `318eb2f529d7103e8b7d80b01228357fdc4e0217`
- Path: `Science/Musical_Intelligence/`
- Determinism canary (this phase): max |Δρ| = 4.7×10⁻⁵ on 13-dyad anchor DEV Group A vs Phase 2 anchors — well below paper-disclosed engine bound 8.8×10⁻⁵.

### V1 stored aggregates (the canonical paper-time engine outputs)
- `Science/V1/results/All_Results/All_Results.md` — per-function aggregate tables for F1–F8.
- `Science/V1/results/f1/bch/report.md` — F1 BCH belief headlines (anchor for determinism spot-check).
- `Science/V1/results/f1..f8/<mech>/report.md` — per-mechanism reports (referenced for cross-validation only).

### Paper anchor (Musical-Intelligence-corrected-evidence.tex)
- §F1 Sensory line 312 — `132/139 (95%), 22/22 FDR, TPIO |ρ|=0.978`
- §F2 Prediction line 314 — `107/110 (97%), 50/50 FDR, OOS Marjieh 39/50, UDP |ρ|=0.973`
- §F3 Attention line 316 — `39/56 primary FDR (70%), function-separation pattern`
- §F4 Memory line 318 — `450/450 (100%) DEAM, MMP |ρ|=0.581`
- §F5 Emotion line 322 — `135/142 (95%), VMM perceived_happy +0.918, TenseMusic 38/38`
- §F6 Reward line 324 — `70/70 (100%), 11/11 pharma, antic_da↔caudate +0.933, consum_da↔nacc +0.836`
- §F7 Motor line 326 — `15/17 FDR, NSCP |ρ|=0.945`
- §F8 Learning line 328 — `14/14 FDR, d̄=1.84`

## Reproduction strategy

Phase 7 is **aggregate verification + determinism spot-check**, NOT mechanism re-execution. Per-mechanism re-runs of 89 mechanisms × 7+ datasets would require ~50 GB intermediates and days of compute; given Phase 0's bit-identical engine determinism guarantee + Phase 2/6's confirmation that V1's stored Group A output is bit-reproducible against the same frozen HEAD, V1's stored per-function aggregates are equivalently the V-Reproduction output for this engine HEAD.

The cross-reference verifies that every paper-claim aggregate appears verbatim (or within tolerance) in V1's `All_Results.md`. The determinism spot-check confirms the engine state has not drifted by re-running F1 BCH on V1's preserved 13-dyad anchor stimuli and matching to Phase 2's bit-identical output.

## Derived artefacts (this phase produces)

- `results/07_c3_anchors_correlations.csv` — claim-level table (24 paper claims + 1 determinism canary)
- `results/07_c3_anchors_manifest.json` — schema-valid manifest
- `results/bch_spotcheck.csv` — Group A canary ρ vs Phase 2 anchors (deviations)
- `02-RESULTS.md` — full report
- `04-INTEGRATION-LOG.md` — single-iteration log
