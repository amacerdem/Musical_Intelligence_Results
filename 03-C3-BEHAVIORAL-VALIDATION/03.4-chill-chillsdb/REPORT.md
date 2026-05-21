# 21-c3-chill-prediction — Run Report

- **Started:**  2026-05-20T15:27:30
- **Finished:** 2026-05-20T15:27:30
- **Headline:** ⛔ ABORTED at L1 engine-pin gate

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **L1** | ❌ FAIL | 1 error in 0.07s | Engine SHA + dim-registry integrity |

## Headline TC005 verdict (afftdn 7-clean)

| Channel | mean_rb | bonf_p | n_clips_pos | status |
|---|---|---|---|---|
| MECH_MMP__P2:familiarity | +0.2307 | 0.0072 | 7/7 | ★ Bonferroni |
| MECH_AAC__E0:emotional_arousal | +0.1697 | 0.0141 | 5/7 | ★ Bonferroni |
| MECH_AAC__F1:hr_pred_2s | +0.1327 | 0.0319 | 5/7 | ★ Bonferroni |
| MECH_AAC__P2:perceptual_arousal | +0.1144 | 0.0557 | 5/7 | • BH-FDR |
| MECH_AAC__F0:scr_pred_1s | +0.1009 | 0.0204 | 5/7 | ★ Bonferroni |

## Engine pin

Pin manifest: [`_infra/manifests/engine_pin.json`](_infra/manifests/engine_pin.json)

Paper-time baseline: [`_infra/manifests/paper_time_baseline.json`](_infra/manifests/paper_time_baseline.json)

