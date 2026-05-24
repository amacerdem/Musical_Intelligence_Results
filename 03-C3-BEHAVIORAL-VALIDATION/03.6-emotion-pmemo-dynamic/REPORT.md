# Phase 03.6 emotion-pmemo-dynamic — Run Report

- **Started:**  2026-05-24T15:30:00
- **Finished:** 2026-05-24T16:19:44
- **Headline:** ✅ ALL PASS — **28/28** across L1–L9 in ≈ 50 min on M2 8 GB

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **L1** | ✅ PASS | 4 passed | Engine pin + paper-baseline manifest integrity |
| **L2** | ✅ PASS | 8 passed | PMEmo per-rater data integrity (767 clips × 10 raters × 2 Hz arousal/valence sliders) |
| **L3** | ✅ PASS | 5 passed | Engine cache (per-frame MI features for 767 clips) + canonical SHA pin |
| **L4** | ✅ PASS | 2 passed | LOSO inter-rater ceiling (arousal +0.171 [0.158, 0.184]; valence +0.158 [0.144, 0.172]) |
| **L5** | ✅ PASS | 5 passed | PRIMARY pilot200: H4 AAC E0 arousal saturates ceiling at 94.7%; H5 SRP P0 wanting Bonferroni-pass (3/15 valence) |
| **L9** | ✅ PASS | 4 passed | Verdict reconciliation against locked paper-time pilot200 baseline |

**Total: 28 passed in ≈ 50 min on M2 8 GB.** Wallclock dominated by L5 LOSO arousal + valence bootstrap on pilot200 (≈ 49 min); L1–L4 + L9 = ≈ 8 s.

## Headline pilot200 verdicts

**H4 — Arousal (`MECH_AAC__E0:emotional_arousal`):**
- Fisher-Z mean ρ = **+0.162** with consensus arousal trajectory at lag-aware Spearman with ±5 s sweep
- **94.7 %** of LOSO inter-rater ceiling (+0.171 [95 % CI 0.158, 0.184], n = 7,069 LOSO trials × 740 clips)
- Cross-paradigm replication of TenseMusic AAC autonomic cluster (109 % → 94.7 % ceiling-saturating signature)

**H5 — Valence (`MECH_SRP__P0:wanting` + 2 additional Bonferroni-pass):**
- ρ = **+0.120**, **p_bonferroni = 0.0038**, 75.7 % of LOSO ceiling
- Additional Bonferroni-pass: VMM R0:happy_pathway (p_bonf = 0.018), VMM V1:mode_signal (p_bonf = 0.024)
- **3/15 Bonferroni-pass**, mechanistically convergent reward-circuit + valence-mode-modeling signal

## Reproduction

```bash
cd 03-C3-BEHAVIORAL-VALIDATION/03.6-emotion-pmemo-dynamic
# Fast subset (23/28 in ≈ 8 s):
python3 -m pytest L1_engine_pin L2_data_integrity L3_engine_cache L4_ceiling_check L9_verdict_reconciliation
# Full suite incl. L5 LOSO bootstrap (≈ 50 min on M2 8 GB):
python3 -m pytest .
```

## Engine pin

- Commit: `318eb2f529d7103e8b7d80b01228357fdc4e0217`
- Tree aggregate SHA-256: `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`
- Pin manifest: [`_infra/manifests/engine_pin.json`](_infra/manifests/engine_pin.json)
- Paper-time baseline: [`_infra/manifests/paper_time_baseline.json`](_infra/manifests/paper_time_baseline.json)
