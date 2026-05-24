# Phase 03.4 chill-chillsdb — Run Report

- **Started:**  2026-05-24T14:00:00
- **Finished:** 2026-05-24T14:23:31
- **Headline:** ✅ PASS — **38 PASS + 2 xfail = 40/40** across L1–L9

## Layer scorecard

| Layer | Status | pytest summary | Coverage |
|-------|--------|----------------|----------|
| **L1** | ✅ PASS | 4 passed | Engine pin + paper-baseline manifest integrity |
| **L2** | ✅ PASS | 11 passed | Audio integrity (7 clips × 3 variants — original/afftdn/noisereduce — per-stimulus WAV SHA-256, engine npz loadable, manifests pin canonical SHA) |
| **L3** | ✅ PASS | 6 passed | Engine cache present + manifest SHA matches pin per audio variant |
| **L4** | ✅ PASS | 5 passed | TC005 PRIMARY (MMP P2 Bonferroni-pass rb=+0.231, p_bonf=0.009, 7/7 clips positive; AAC autonomic cluster + DAED negative direction) |
| **L5** | ✅ PASS (with 2 xfail) | 3 passed + 2 xfail | TC003 sensitivity (Tier-2 channels expected below sensitivity envelope per paper §Limitations — `xfail` markers preserve the disclosed null) |
| **L6** | ✅ PASS | 2 passed | TC004 biphasic composite |
| **L7** | ✅ PASS | 2 passed | TC006 noisereduce cross-validation |
| **L8** | ✅ PASS | 2 passed | TC007 pre/post asymmetry (sustained chill response) |
| **L9** | ✅ PASS | 3 passed | Verdict reconciliation within tolerance against paper-time baseline |

**Total: 38 passed + 2 xfail in ≈ 23.5 min on M2 8 GB.** The two `xfail` cells are paper-disclosed expected-fails (Tier-2 sensitivity envelope); they count as PASS for the headline-effect verdict.

## Headline TC005 verdict (afftdn 7-clean)

| Channel | mean_rb | bonf_p | n_clips_pos | status |
|---|---|---|---|---|
| MECH_MMP__P2:familiarity | +0.2307 | 0.0072 | 7/7 | ★ Bonferroni (PRIMARY) |
| MECH_AAC__E0:emotional_arousal | +0.1697 | 0.0141 | 5/7 | ★ Bonferroni |
| MECH_AAC__F1:hr_pred_2s | +0.1327 | 0.0319 | 5/7 | ★ Bonferroni |
| MECH_AAC__P2:perceptual_arousal | +0.1144 | 0.0557 | 5/7 | • BH-FDR |
| MECH_AAC__F0:scr_pred_1s | +0.1009 | 0.0204 | 5/7 | ★ Bonferroni |

## Reproduction

```bash
cd 03-C3-BEHAVIORAL-VALIDATION/03.4-chill-chillsdb
python3 -m pytest .                          # ≈ 23.5 min on M2 8 GB
```

Wallclock is dominated by L5 TC003 sensitivity permutation tests (500 random event-time shuffles per channel × 22 channels × 7 clips × 3 audio variants).

## Engine pin

- Commit: `318eb2f529d7103e8b7d80b01228357fdc4e0217`
- Tree aggregate SHA-256: `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`
- Pin manifest: [`_infra/manifests/engine_pin.json`](_infra/manifests/engine_pin.json)
- Paper-time baseline: [`_infra/manifests/paper_time_baseline.json`](_infra/manifests/paper_time_baseline.json)
