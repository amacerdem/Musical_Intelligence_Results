# 23-h4-h5-pmemo-dynamic-emotion — Standalone PMEmo Dynamic Emotion Verdict

> **Purpose:** Reproduce the paper's Tier-1 PMEmo findings — AAC emotional-arousal channel saturates LOSO ceiling at 94.7% (H4) and SRP wanting + VMM Bonferroni-pass concordance for valence (H5) on PMEmo 2018 — **from a fresh clone of the system**, in a single command.
>
> **The two empirical claims under test:**
>
> > On the PMEmo 2018 dataset (767 clips × 10 raters × dynamic 2 Hz arousal slider), the frozen MI engine's `MECH_AAC__E0:emotional_arousal` channel achieves Fisher-Z mean ρ = +0.162 with consensus arousal trajectory at lag-aware Spearman with ±5 s sweep, **94.7% of the LOSO inter-rater ceiling** (+0.171 [95% CI 0.158, 0.184], n=7,069 LOSO trials × 740 clips). Cross-paradigm replication of TenseMusic AAC autonomic-cluster (T1-D, V-Reproduction 22-h8).
>
> > On the same PMEmo 2018 dataset (dynamic 2 Hz valence slider), `MECH_SRP__P0:wanting` achieves ρ = +0.120, **p_bonferroni = 0.0038**, 75.7% of LOSO ceiling (+0.158 [0.144, 0.172]). Two additional channels pass Bonferroni: VMM R0:happy_pathway (p_bonf=0.018) and VMM V1:mode_signal (p_bonf=0.024) — **3/15 Bonferroni-pass**, mechanistically convergent reward-circuit + valence-mode-modeling signal.

## Quick reference

| | |
|---|---|
| **Engine SHA** | `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88` |
| **Engine commit** | `318eb2f5` |
| **Paper section** | C³-Paper §Results, FINDINGS_INDEX T1-E + T1-F |
| **Status** | CLOSED (2026-05-24) — 28/28 pytest PASS (L1–L9, dominated by ≈ 50 min L5 LOSO bootstrap on M2 8 GB); paper-frozen pilot200 baseline reproduces. Full 767-clip clinch tracked in §Limitations. |
| **Headline (arousal)** | `MECH_AAC__E0:emotional_arousal` ρ=+0.162, ceiling-rel = 94.7 % |
| **Headline (valence)** | `MECH_SRP__P0:wanting` ρ=+0.120, p_bonf=0.0038, 3/15 Bonferroni-pass |
| **Sample size** | 767 clips × 10 raters × 2 Hz dynamic slider |

## Quick start

```bash
cd <REPO_ROOT>/03-C3-BEHAVIORAL-VALIDATION/03.6-emotion-pmemo-dynamic
python3 -m pytest L1_engine_pin L2_data_integrity L3_engine_cache L4_ceiling_check L9_verdict_reconciliation
# Fast subset (23 of 28 tests) ≈ 8 s
# Full L1–L9 (incl. L5 primary LOSO bootstrap) ≈ 50 min on M2 8 GB
python3 -m pytest .
```

## Layer scaffold

| Layer | Description | Wall (M2 base) |
|---|---|---|
| L1 | Engine SHA aggregate integrity + paper-baseline structural checks | < 1 s |
| L2 | PMEmo per-rater CSV + engine .npz file presence (≥700 each) | < 1 s |
| L3 | Engine cache integrity (r3 + mech_AAC + mech_SRP + mech_VMM clusters) | < 1 s |
| L4 | LOSO inter-rater ceiling reproduction (arousal +0.171, valence +0.158) | ~5-6 min |
| L5 | PRIMARY inline re-run — pilot200 × 100 perms (H4 + H5) | ~20-25 min |
| L9 | Local vs paper-time baseline tolerance check | < 1 s |

## Why this V-Reproduction package matters

1. **Cross-paradigm replication of AAC autonomic-cluster.** The TenseMusic Tier-1 finding (22-h8, AAC F1:hr_pred_2s at 109% ceiling) is replicated on a second independent continuous-trajectory dataset (PMEmo, AAC E0:emotional_arousal at 94.7% ceiling). Same MECH cluster, different stimulus pool, different rater pool, different annotation modality — engine prediction is **stimulus-driven**, not lucky.

2. **High-entropy ceiling demonstration.** PMEmo dynamic LOSO ceiling is +0.171 (vs DEAM +0.335, TenseMusic +0.386) — among the lowest in the validation portfolio, reflecting genuine inter-rater disagreement at moment-by-moment timescale. The engine still hits this ceiling at sampling precision (94.7% with statistical CI containing 100%). This is the "low-bar that's actually hard" case in the **Ceiling-Saturation Portfolio**.

3. **Multi-channel valence Bonferroni-pass.** Independent VMM (Valence-Mode-Modeling) and SRP (Salimpoor-Reward-Prediction) clusters both contribute Bonferroni-pass channels for valence — mechanistically convergent, not single-channel luck. Berridge-2003 wanting-vs-liking distinction maps cleanly onto engine architecture.

## Paper integration

This package backs FINDINGS_INDEX T1-E (PMEmo arousal) and T1-F (PMEmo valence). C³-Paper §Results + §Discussion (Ceiling-Saturation Portfolio).
