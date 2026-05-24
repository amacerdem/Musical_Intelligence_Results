# Phase 03.7 gems-eerola-film — Run Report

- **Started:**  2026-05-24T14:32:00
- **Finished:** 2026-05-24T14:32:13
- **Headline:** ✅ ALL PASS — **24/24** in ≈ 13 s on M2 8 GB

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **L1** | ✅ PASS | Engine SHA aggregate integrity + paper-baseline structural checks |
| **L2** | ✅ PASS | Eerola film GEMS data integrity (Set 1 n=360 + Set 2 n=110 across 9 emotion categories) |
| **L3** | ✅ PASS | Engine cache (per-frame MI features) + canonical SHA pin |
| **L4** | ✅ PASS | Set 2 PRIMARY: 8/8 GEMS labels Bonferroni-pass, 7/8 R³-residual survive |
| **L5** | ✅ PASS | Set 1 replication: 4/8 identical-channel replication (fear/sad/tender + tension cluster) |
| **L9** | ✅ PASS | Verdict reconciliation against paper-time baseline (mechanistic specificity preserved across all 9 GEMS labels) |

**Total: 24 passed in ≈ 13 s on M2 8 GB.**

## Headline mechanistic-specificity verdict

| GEMS label | Top MI channel | ρ | Mechanistic interpretation |
|---|---|---|---|
| sad | NEMAC mPFC activation | +0.741 | Janata 2009 default-mode anchor |
| tender | DAP familiarity_warmth | +0.722 | Affiliative-intimacy |
| tension | CDMR mismatch_amplitude | −0.683 | Expectancy-violation |
| energy | AAC heart-rate | +0.672 | Cross-paradigm TenseMusic AAC cluster replication |
| valence | SRP liking | +0.424 | Berridge wanting-vs-liking |

## Critical caveat

No per-rater data publicly deposited; LOSO ceiling is **NOT computable**. Bonferroni + R³-residual ablation are the load-bearing metrics; ceiling-relative saturation is not reported for this phase.

## Reproduction

```bash
cd 03-C3-BEHAVIORAL-VALIDATION/03.7-gems-eerola-film
python3 -m pytest .                          # ≈ 13 s on M2 8 GB
```

## Engine pin

- Commit: `318eb2f529d7103e8b7d80b01228357fdc4e0217`
- Tree aggregate SHA-256: `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`
- Pin manifest: [`_infra/manifests/engine_pin.json`](_infra/manifests/engine_pin.json)
- Paper-time baseline: [`_infra/manifests/paper_time_baseline.json`](_infra/manifests/paper_time_baseline.json)
