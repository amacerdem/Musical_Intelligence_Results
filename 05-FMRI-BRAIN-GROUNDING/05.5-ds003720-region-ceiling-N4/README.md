# 05.5-ds003720-region-ceiling-N4 — Companion Ceiling Test for V-Repro 12

> **Purpose:** Add per-region cross-subject LOSO BOLD ceiling-saturation analysis to ds003720 (Nakai 2021 GTZAN-fMRI) at the cycle-17 ckpt_bold scale. **V-Repro 12** (voxelwise routing-ablation, CLOSED, 11/11 PASS) remains paper-canonical primary; this package adds a complementary ceiling perspective without touching V-Repro 12.

## Quick reference

| | |
|---|---|
| **Engine SHA** | `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88` |
| **Engine commit** | `318eb2f5` |
| **Paper section** | C³-Paper §Cross-subject fMRI complementary ceiling evidence |
| **Status** | OPEN 2026-05-13 |
| **Cohort** | ds003720 N=4 paper-canonical QC-pass (sub-001, sub-003, sub-004, sub-005) |
| **BOLD source** | Cycle-17 ckpt_bold (15 runs × (410, 26) per subject = 6150 TRs total) |
| **MI encoder r** | Cycle-17 per_subject_per_region_r.csv (mi_ram_26d Ridge LOSO) |
| **Relationship to V-Repro 12** | Companion (does not modify or overlap with V-Repro 12 voxelwise framework) |

## The empirical claim under test

> On the ds003720 dataset (N=4 paper-canonical QC-pass cohort, cycle-17 26-region BOLD aggregate at 6150 TRs per subject), the per-region cross-subject LOSO inter-rater predictability ceiling is statistically significant in **16 of 21 non-brainstem regions** (BH-FDR q<0.05, effect floor r>0.05). Top regions are **hippocampus +0.354** [+0.301, +0.405], dlPFC +0.319 [+0.269, +0.371], AG +0.243 [+0.207, +0.279], IFG +0.233 [+0.138, +0.313], PMC +0.193, putamen +0.166, SMA +0.173, VTA +0.173, MGB +0.141 [+0.080, +0.191]. Brainstem auditory pathway also stimulus-driven (IC +0.206, PAG +0.206). These confirm ds003720 BOLD is reliably stimulus-driven cross-subject at the per-region level, **independent of MI's role**, and complement V-Repro 12's voxelwise routing-ablation finding (MI 26-D r=0.165 top-5% held-out).

## Quick start

```bash
cd <REPO_ROOT>/05.5-ds003720-region-ceiling-N4
python3 run_all.py --quick   # L1-L5 + L9 (< 3 sec, paper-baseline checks)
# Full re-run (regenerates ceiling CSV from cycle-17 ckpt_bold):
python3 code/run_phase05_5.py  # ~4-5 min on M2 base
```

## What this V-Reproduction package contributes

1. **Per-region BOLD reliability** on ds003720 at the cycle-17 26-region scale. Previously unmeasured.
2. **hippocampus +0.354** highlighted as the cleanest ds003720 ceiling region — consistent with sparse-clip stimulus-paradigm engaging clip-recognition / memory systems.
3. **Cross-paradigm anchor for V-Repro 25 (ds002725 N=17)**:
   - V-Repro 25 top: putamen +0.4422, amygdala +0.3825 (continuous-listening)
   - V-Repro 26 top: hippocampus +0.354, dlPFC +0.319 (sparse-clip)
   - Both paradigms produce similar-magnitude per-region ceilings (~0.3-0.45) despite very different cohort sizes (17 vs 4).
4. **MI encoder saturation verdict** (cycle-17 per-clip r vs per-TR ceiling): 5 of 21 non-brainstem regions ceiling-saturating. Lower than ds002725 N=17 (16/21) due to (a) N=4 statistical power limit, (b) per-clip vs per-TR scale mismatch between cycle-17 encoder and TR-level ceiling. Disclosed as honest paradigm-scale comparison.

## What this package does NOT claim

- It does NOT claim ds003720 per-region encoder fidelity at ds002725-N=17-scale (paper-canonical ds003720 framing is V-Repro 12 voxelwise routing-ablation, NOT per-region encoder).
- It does NOT modify V-Repro 12.
- It does NOT replace cycle-17 ckpt_bold or per-subject per-region encoder r files.

## Layer scaffold (L1-L9)

| Layer | Purpose | Wall (M2 base) |
|---|---|---|
| L1 | Engine SHA + paper-baseline structural checks | < 1 s |
| L2 | Cycle-17 ckpt_bold + per_subject_per_region_r.csv present | < 1 s |
| L3 | Phase 05.5 output CSVs + manifest exist | < 1 s |
| L4 | Per-region ceiling matches paper baseline (top-5 + n_pass_floor_q05) | < 1 s |
| L5 | Saturation verdict distribution within tolerance | < 1 s |
| L9 | Verdict reconciliation + V-Repro 12 untouched check | < 1 s |

**Full Stage** (regenerates ceiling CSV from scratch):  `code/run_phase05_5.py`, ~4.6 min on M2 base.

## Provenance

- **Phase 05.5 script:** `code/run_phase05_5.py` (uses cycle-17 ckpt_bold + cycle-17 per-region encoder r)
- **Engine SHA pin verified:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
- **N=4 cohort:** sub-001, sub-003, sub-004, sub-005 (sub-002 excluded per Phase 05.4 paper QC)
- **Stat protocol:** Per-region BOLD z-score within subject; Fisher-Z mean across LOSO subjects; cluster-bootstrap B=5000 → 95% CI; circular-shift null B=5000 → p_null
- **Wallclock:** 276 s (4.6 min) on M2 base
