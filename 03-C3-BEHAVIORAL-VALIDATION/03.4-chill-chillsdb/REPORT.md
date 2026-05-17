# 21-c3-chill-prediction — Run Report

- **Started:**  2026-05-12T19:33:16
- **Finished:** 2026-05-12T19:42:16
- **Headline:** ❌ FAIL

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **L1** | ✅ PASS | 4 passed in 0.40s | Engine SHA + dim-registry integrity |
| **L2** | ✅ PASS | 12 passed in 2.69s | ChillsDB v1 audio file presence + format |
| **L4** | ❌ FAIL | 2 failed, 3 passed in 535.44s (0:08:55) | PRIMARY — TC005 7-clean Bonferroni-pass (MMP P2) |

## Headline TC005 verdict (afftdn 7-clean)

| Channel | mean_rb | bonf_p | n_clips_pos | status |
|---|---|---|---|---|
| MECH_AAC__E0:emotional_arousal | +0.1702 | 0.0220 | 6/7 | ★ Bonferroni |
| MECH_AAC__F1:hr_pred_2s | +0.1337 | 0.0487 | 6/7 | ★ Bonferroni |
| MECH_AAC__P2:perceptual_arousal | +0.1202 | 0.9015 | 6/7 | • BH-FDR |
| MECH_SSRI__P1:endorphin_proxy | +0.1166 | 0.1045 | 5/7 | • BH-FDR |
| MECH_AAC__F0:scr_pred_1s | +0.1043 | 0.5844 | 5/7 | • BH-FDR |

## Engine pin

Pin manifest: [`_infra/manifests/engine_pin.json`](_infra/manifests/engine_pin.json)

Paper-time baseline: [`_infra/manifests/paper_time_baseline.json`](_infra/manifests/paper_time_baseline.json)

