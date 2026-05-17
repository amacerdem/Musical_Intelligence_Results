# L4 — PRIMARY VERDICT (TC005 7-clean Bonferroni Mann-Whitney)

**This is the headline test.** If L4 passes, the paper's Tier-1 chill marker finding is independently reproduced on the runner's machine.

## The single claim under test

> On the **ChillsDB v1 7-clean continuous-music subset** with **afftdn-denoised** audio, the frozen MI engine's `MECH_MMP__P2:familiarity` channel shows **Bonferroni-corrected elevation** within ±5 s windows of participant chill events:
>
> - **rank-biserial = +0.231** (Fisher-Z aggregate across 7 clips)
> - **p_bonf = 0.009** across 22 chill-related channels
> - **7/7 clips positive direction**
>
> Three additional channels in the AAC autonomic-arousal cluster also Bonferroni-pass: AAC E0:emotional_arousal (rb=+0.170, p_bonf=0.041), AAC F1:hr_pred_2s (rb=+0.133, p_bonf=0.035), AAC F0:scr_pred_1s (rb=+0.101, p_bonf=0.023).

## Protocol (TC005 byte-faithful)

1. Load chill event timestamps from `Science/datasets/emotion/chillsdb/music_stimuli.csv` (filter `chills Binary == 1`).
2. For each of 22 pre-registered chill-cluster channels × 7 clean clips:
   - Z-score signal within-clip
   - Compute Mann-Whitney rank-biserial: event-window (±5 s) vs out-of-window, alternative=`greater`
   - Null distribution: 500 random event-time placements uniform in [0, clip_duration]
   - Empirical p = (1 + #{null ≥ observed}) / (1 + n_null)
3. Across clips: Fisher-Z aggregate of rank-biserial values; Fisher's combined p-value
4. Apply Bonferroni correction over 22 channels (and BH-FDR for reference)
5. Compare result to `paper_time_baseline.json` headline numbers within tolerance

## What this test asserts

1. `test_mmp_p2_bonferroni_pass` — MMP P2 Bonferroni-pass (rb > +0.20, p_bonf < 0.05, 7/7 clips positive)
2. `test_mmp_p2_within_tolerance` — MMP P2 numbers reproduce paper-time within declared tolerance (rb ±0.01, p_bonf ±0.005)
3. `test_aac_cluster_directionally_correct` — AAC autonomic cluster (E0, F0, F1, P2) all positive direction (Salimpoor anticipatory phase)
4. `test_daed_cluster_negative_direction` — DAED consummatory cluster (f02, f04) all negative direction (Salimpoor consummatory suppression)
5. `test_at_least_2_bonferroni_passes` — ≥2 of 22 channels Bonferroni-pass (paper-time = 4)

## Tolerance rationale

The 500-permutation null introduces ~0.002 absolute variance in `bonf_p` across runs at fixed engine SHA + fixed RNG seed (variance is from chi2 tail of Fisher's combined p; not numeric drift in engine). Tolerance is set to **0.005 absolute on bonf_p** and **0.01 absolute on rb**, both well below the Bonferroni-pass threshold (p<0.05) so the qualitative verdict is invariant.

## Wallclock

Approximately **8-10 minutes** for the full 22-channel × 7-clip × 500-permutation null on M2 8 GB. The `tc005_results` fixture is session-scoped, so subsequent tests reuse the computed DataFrame.

## Output

- `results/tc005_single_channel_aggregate.csv` — 22 channels × 1 audio variant × clip-aggregate statistics. Consumed by L5 (sensitivity comparison), L7 (denoise crossval comparison), L9 (reconciliation).

## Failure modes

| Symptom | Likely cause |
|---|---|
| MMP P2 rb ≈ 0, sign random | Wrong dim ordering. Verify `_infra/engine_cache.route()` reads `pooled.csv` correctly. |
| MMP P2 rb negative | Events placed at wrong timestamps OR signal sign-flipped. Inspect `load_events()`. |
| MMP P2 rb correct sign but very weak (~+0.05) | Safezone applied incorrectly. TC005 does NOT apply 8 s safezone. |
| All channels Bonferroni-fail | Null permutation count too low OR signal not z-scored within-clip. |
