# 05.3-ds002725-region-ceiling-N17 — Standalone ds002725 N=17 Ceiling-Saturation Verdict

> **Purpose:** Reproduce the paper's Tier-1 ds002725 per-region cross-subject ceiling-saturation finding — MI saturates or exceeds the inter-rater LOSO predictability ceiling in 16 of 21 paper-canonical regions on the Mendelssohn 80-TR window, with literature-anchored top regions (A1_HG, STG, MGB, SMA, caudate) — **from a fresh clone of the system**, in a single command.

## Quick reference

| | |
|---|---|
| **Engine SHA** | `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88` |
| **Engine commit** | `318eb2f5` |
| **Paper section** | C³-Paper §Results, §Cross-subject fMRI |
| **Status** | OPEN (2026-05-13) — promoted from V8 Phase 21 v1.4 positive stages |
| **Cohort** | ds002725 N=17 paper-canonical (Daly 2019) |
| **Sample size** | 17 subjects × 26 regions × 80 TRs Mendelssohn window (and 930 TRs full scan) |

## The four empirical claims under test

> **C1** (Stage 3 full-scan ceiling): On ds002725 N=17 paper-canonical cohort, 15 of 21 non-brainstem regions show statistically significant cross-subject BOLD predictability ceiling (BH-FDR q<0.05). Top regions: putamen +0.4422 [+0.327, +0.556], amygdala +0.3825 [+0.228, +0.507], MGB +0.3464 [+0.247, +0.438], ACC +0.3036 [+0.149, +0.440]. These match literature-anchored music-cognition substrates.

> **C2 (HEADLINE)** (Stage 4 encoder + saturation verdict): On the Mendelssohn 80-TR window (N=17), MI's frozen stimulus-only output saturates or exceeds the LOSO inter-rater ceiling in **16 of 21 non-brainstem regions** (11 AT_CEILING + 5 EXCEEDS). Top: A1_HG +0.5088 AT_CEILING, STG +0.3747 AT_CEILING, MGB +0.3639 EXCEEDS, SOC +0.3469 AT_CEILING (brainstem), SMA +0.3267 AT_CEILING (N=14 per-region cohort). The 5 EXCEEDS regions (IFG, ACC, PMC, caudate, MGB) span MI's prediction, attention, motor, reward, and auditory clusters — consistent with the engine's architectural cluster anchoring.

> **C3** (Mendelssohn pilot paradox resolution): Phase 05.1 N=17 cross-subject median ρ = −0.022 for amygdala was about MI's amygdala-channel encoder fidelity on the Mendelssohn 80-TR subwindow (where the BOLD ceiling itself is only +0.012, because Mendelssohn Op.54 is technical, not emotion-loaded), NOT about general BOLD amygdala reliability (full-scan ceiling +0.3825).

> **C4** (Cross-paradigm bridge): ds002725 ↔ ds003720 per-region comparison shows 1 STRONG (STG: ds002725 saturating AND ds003720 above floor) + 5 MIXED (IFG, OFC, MGB, hypothalamus, insula: ds002725 saturating AND ds003720 marginally positive). Cross-paradigm consistency in the auditory + reward + interoception cluster.

## Quick start

```bash
cd /Volumes/SRC-9/SRC\ Musical\ Intelligence/Musical_Intelligence_Results/05.3-ds002725-region-ceiling-N17
python3 run_all.py --quick   # L1 + L4 + L5 + L6 + L9 (~12-15 min)
# Or fully:
python3 run_all.py           # L1-L9 (~15-20 min)
```

## Layer scaffold

| Layer | Description | Wall (M2 base) |
|---|---|---|
| L1 | Engine SHA aggregate + paper-baseline structural checks | < 1 s |
| L2 | BOLD cache (N=17) + MI engine cache (Mendelssohn) present | < 1 s |
| L3 | Mendelssohn MI RAM 26-region cache integrity | < 1 s |
| L4 | Full-scan LOSO ceiling reproduction (Stage 3 numbers) | < 1 s (paper-baseline check); ~12 min (full re-run via code/stage3_loso_ceiling.py) |
| L5 | Mendelssohn encoder + saturation verdict (Stage 4 numbers) | < 1 s (paper-baseline check); ~8 min (full re-run via code/stage4_encoder.py) |
| L6 | Cross-paradigm bridge ds002725 ↔ ds003720 | < 1 s |
| L9 | All four headline numbers locked | < 1 s |

L4/L5 paper-baseline checks read from pre-computed CSVs (`data/stage3_ceiling_ds002725.csv`, `data/stage4_encoder_ds002725.csv`). Full re-runs are available via `code/` scripts but not required for paper-time baseline verification.

## Files

- `_infra/manifests/engine_pin.json`, `paper_time_baseline.json` — engine + paper-time numbers
- `_infra/sha_utils.py` — engine SHA aggregator
- `conftest.py` — pytest fixtures + auto pin-integrity gate
- `run_all.py` — orchestrator (writes REPORT.md)
- `code/stage2_mi_features.py` — HRF convolve + LPF + downsample + N1 z-score
- `code/stage3_loso_ceiling.py` — per-region LOSO ceiling
- `code/stage4_encoder.py` — encoder + saturation verdict
- `code/stage9_cross_paradigm_bridge.py` — ds002725 ↔ ds003720 aggregation
- `data/stage{2,3,4,9}_*.{csv,npz,json}` — frozen paper-time outputs
- `results/_logs/stage{3,4,9}_summary.json` — machine-readable summaries
- `L1`-`L9` layered pytest scaffold

## Why this V-Reproduction package matters (paper-canonical contribution)

1. **First per-region cross-subject ceiling-saturation evidence on ds002725 N=17.** Prior paper evidence (Phase 05.2/V-Repro 05.2 mech×region) tests 89 mechs × 26 regions; Phase 05.4/V-Repro 12 tests voxelwise N=4 on ds003720. This package fills the gap: 26 regions × N=17 ds002725 ceiling-saturating per-region encoder.

2. **Phase 05.1 Mendelssohn-pilot paradox cleanly resolved.** The paper's Phase 05.1 N=17 cross-subject median ρ=−0.022 was attributed in §Limitations to "window-selection effect"; this package shows it is more precisely a separation between BOLD reliability (high on full scan) and MI encoder fidelity (low on specific Mendelssohn subwindow because the piece is technical not emotion-loaded).

3. **Cross-paradigm consistency** between ds002725 N=17 and ds003720 N=4 anchored at STG (auditory primary): both paradigms show MI prediction in this region. Five mixed regions (IFG, OFC, MGB, hypothalamus, insula) span the engine's prediction, reward, auditory, and interoception clusters.

4. **Engine architectural cluster signatures preserved.** The 5 EXCEEDS regions (IFG, ACC, PMC, caudate, MGB) span exactly the engine's prediction (IFG), attention (ACC), motor (PMC), reward (caudate), and auditory (MGB) clusters — consistent with engine architecture, not random model fit.

## Paper integration

This package backs C³-Paper §Cross-subject fMRI per-region ceiling-saturation main paragraph + §Discussion (Three-claim separability framing).
