# Phase 05.5 ds003720-region-ceiling-N4 — Run Report

- **Started:**  2026-05-24T14:33:30
- **Finished:** 2026-05-24T14:33:31
- **Headline:** ✅ ALL PASS — **18/18** in ≈ 0.1 s on M2 8 GB (cache-anchored)

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **L1** | ✅ PASS | 4 passed | Engine SHA + paper-baseline structural checks |
| **L4** | ✅ PASS | 3 passed | Per-region cross-subject LOSO ceiling on ds003720 N=4 at cycle-17 26-region BOLD scale |
| **L5** | ✅ PASS | 4 passed | MI encoder saturation distribution (5/21 — per-clip vs per-TR scale mismatch documented) |
| **L9** | ✅ PASS | 7 passed | Per-region verdict reconciliation against paper baseline |

**Total: 18 passed in ≈ 0.1 s.** Cache-anchored against `paper_time_baseline.json`; companion to V-Repro 12 (paper-canonical voxelwise on the same ds003720 cohort).

## Headline regions

**Top stimulus-driven regions (LOSO ceiling):** hippocampus +0.354, dlPFC +0.319, AG +0.243, IFG +0.233, PMC +0.193.
**N pass floor + q05 (non-brainstem):** 16/21.
**MI encoder saturation:** 5/21 (scale mismatch: cycle-17 per-clip representation vs per-TR ceiling — paper-disclosed in §Limitations).

## Reproduction

```bash
cd 05-FMRI-BRAIN-GROUNDING/05.5-ds003720-region-ceiling-N4
python3 -m pytest .                          # ≈ 0.1 s on M2 8 GB
```

## Engine pin

- Commit: `318eb2f529d7103e8b7d80b01228357fdc4e0217`
- Tree aggregate SHA-256: `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`
- Pin manifest: [`_infra/manifests/engine_pin.json`](_infra/manifests/engine_pin.json)
- Paper-time baseline: [`_infra/manifests/paper_time_baseline.json`](_infra/manifests/paper_time_baseline.json)
