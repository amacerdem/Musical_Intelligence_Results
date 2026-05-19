# Phase 05.2 — Pre-Registered Mechanism × Region Encoding (ds002725) — Methodology

**Axis ID:** AXIS-8
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
**Strategy:** REUSES V3 preserved analysis artefacts + per-subject alignment QC.

## 1. Scope

Verifies paper's pre-registered 22 target × 22 random mechanism×region encoding
analysis on ds002725 (paper Results §Pre-registered confirmatory test). Decision
rule frozen 2026-05-03 18:29; seed 20260503.

Paper claims (12 total):
- C-MXREG-01: 16/22 target BH-FDR pass (q<0.05) on L1 single-subject
- C-MXREG-02: F1 5/5 target pairs pass
- C-MXREG-03: F2 4/4 target pairs pass
- C-MXREG-04: F4 2/2 target pairs pass
- C-MXREG-05: F8 1/1 target pair passes
- C-MXREG-06: PNH→A1_HG r=+0.334
- C-MXREG-07: BCH→A1_HG r=+0.317
- C-MXREG-08: CDEM→MGB r=+0.315
- C-MXREG-09: L2 cross-piece 226/371 BH-FDR pass
- C-MXREG-10: L3 cross-subject 34/147 BH-FDR pass
- C-MXREG-11: F3→ACC null preserved (p_perm > 0.20)
- C-MXREG-12: alignment-qualified N disclosure

## 2. Paper anchor

V3 preserved analysis at:
- `Science/V3/results/pair_evidence_ds002725.csv` — 22+22 pairs, per-pair median_r,
  CI, p_perm, BH-FDR pass flag
- `Science/V3/results/decision_gate.md` — verdict POSITIVE, target_pass=16/22,
  separation +0.105 vs 2×SE 0.048
- `Science/V3/results/per_region_effect_summary.csv` — per-region best target/random r
- `Science/V3/V3-comprehensive/results/l2_cross_piece.csv` — L2 LOSO ridge across pieces
- `Science/V3/V3-comprehensive/results/l3_cross_subject.csv` — L3 LOSO ridge across subjects

## 3. Verification approach

V3 ran the pre-registered analysis end-to-end against engine HEAD `318eb2f5`
(frozen since pre-V1). This phase reads V3's preserved CSVs and verifies each of
the 12 paper claims against the stored numbers. No engine re-execution required
— V3's pipeline already produced the canonical numbers; engine bit-determinism
re-verified by Phases 0/2/6/7/8/9 canaries.

## 4. Alignment-qualified N (C-MXREG-12)

V3 used N=17 (dataset-level). Phase 0.5 V-fMRI eligibility audit
(`00-ENGINE-INTEGRITY-FOUNDATIONS/00.2-fmri-eligibility-audit/`) classified ds002725 as
`mi_compatible=True` with `n_alignment_qualified=17`. All 17 subjects pass
alignment QC; M=N=17.

## 5. Forbidden moves

- Re-running 22 target pairs with different seeds to chase a higher pass count.
- Filtering V3's stored CSV to a different subject subset.
- Modifying paper claims to fit V3's numbers.
