# Phase 01.3 — Provenance

## Source artefacts (read-only)

### V4 cross-cultural workspace (preserved)
- `Science/V4/results/decision_gate.md` — 6 PRIMARY anchors composite verdict
- `Science/V4/results/per_anchor/anchor_{1..6}.csv` — per-anchor evidence

### V5 cross-cultural re-cycle (audit-fixed, preserved)
- `Science/V5/results/decision_gate.md` — 4 PRIMARY anchors audit-fixed composite
- `Science/V5/results/per_anchor/anchor_{1..4}.csv` — per-anchor evidence
- `Science/V5/code/synth_a3_marjieh.py` + `analyse_a3_marjieh.py` — Marjieh bonang+harmonic synth
- `Science/V5/code/extract_*` — A1 Pakistan, A2 Saraga, A3 Marjieh extraction

### Paper anchor
- §Cross-cultural validation (Musical-Intelligence-corrected-evidence.tex)
- §Discussion §Cross-cultural calibration boundary

## Reproduction strategy

V4 + V5 ran the analyses end-to-end on engine HEAD pin `15df5177` (V3
architectural anchor, ENGINE_HEAD_ACTUAL=`5b9aba41`). Phase 14 reads preserved
decision-gate text + anchor CSVs, verifies paper claims against stored numbers.

## Derived artefacts

- `results/14_cross_cultural_correlations.csv` — 6-row claim verdict
- `results/14_cross_cultural_manifest.json`
