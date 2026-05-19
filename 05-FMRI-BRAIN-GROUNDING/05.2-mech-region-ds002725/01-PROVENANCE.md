# Phase 05.2 — Provenance

## Source artefacts (read-only)

### V3 preserved analysis
- `Science/V3/results/pair_evidence_ds002725.csv` — 44 pairs (22 target + 22 random), per-pair median_r, CI, p_perm, BH-FDR pass flag, n_subjects
- `Science/V3/results/decision_gate.md` — verdict POSITIVE, 16/22 target pass, separation +0.105
- `Science/V3/results/per_region_effect_summary.csv` — per-region best target/random
- `Science/V3/V3-comprehensive/results/l2_cross_piece.csv` — L2 LOSO ridge (462 target × 462 random cells)
- `Science/V3/V3-comprehensive/results/l3_cross_subject.csv` — L3 LOSO ridge (154 target × 154 random cells)
- `Science/V3/V3-comprehensive/results/comprehensive_summary.md` — L1/L2/L3 verdicts + key statistics

### Phase 0.5 dependency
- `00-ENGINE-INTEGRITY-FOUNDATIONS/00.2-fmri-eligibility-audit/` — ds002725 mi_compatible=True, n_alignment_qualified=17

### Paper anchor
- §Pre-registered confirmatory test (Musical-Intelligence-corrected-evidence.tex)
- §Methods §Dataset eligibility (alignment-qualified N disclosure)

## Reproduction strategy

V3 ran the pre-registered analysis end-to-end on engine HEAD `318eb2f5` (pre-V1 frozen). Phase 05.2 reads V3's preserved CSVs/MD and verifies 12 paper claims against stored numbers. No engine re-execution required (engine bit-determinism re-verified Phases 0/2/6/7/8/9 canaries).

## Derived artefacts

- `results/05.2_mech_region_correlations.csv` — 12-row claim verdict table
- `results/05.2_mech_region_manifest.json` — schema-valid manifest
