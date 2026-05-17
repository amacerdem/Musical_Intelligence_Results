# Phase 04.1 — Provenance / Chain of Custody

## Source artefacts (read-only)

### Engine
- HEAD: `318eb2f529d7103e8b7d80b01228357fdc4e0217`
- Path: `Musical_Intelligence/`
- Determinism canary: max |Δ| = 0.0 on 345 frames × 4 neurochem channels (live spot-check, P5-fifth interval WAV)

### V1 stored neurochemical validation
- `Science/V1/results/neurochemicals/neurochemical_validation.md` — canonical paper-time engine output for all 10 Phase 04.1 claims.

### Paper anchor
- §F6 Reward line 324 (Musical-Intelligence-corrected-evidence.tex) — `70/70, 11/11 pharma, antic_da↔caudate +0.933, consum_da↔NAcc +0.836, caudate-leads 52/56 +0.9s lag, Putkinen 7/7, Mallik p=0.044`

### Audio for spot-check
- `Science/V1/stimuli/intervals/interval_P5_fifth.wav` — perfect-fifth dyad (R³ ground-truth stimulus, 0.5 s)

## Reproduction strategy

Aggregate verification against the V1 stored neurochem validation file + live engine determinism canary. Phase 04.1 runs the **full engine pipeline** (R³ → T³ → C³ → RAM → 4-channel neurochem) on the V1 P5 WAV via `_infra/engine/runner.py` and confirms bit-identical output across two consecutive runs.

## Derived artefacts (this phase produces)

- `results/04.1_neurochem_correlations.csv` — claim-level table (10 paper claims + 1 determinism canary)
- `results/04.1_neurochem_manifest.json` — schema-valid manifest
- `results/neurochem_spotcheck.csv` — 4-channel mean + max-Δ table
