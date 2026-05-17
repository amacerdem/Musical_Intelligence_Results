# L7 — TC006 noisereduce Cross-Validation

**Purpose:** Verify that the chill marker finding is **denoise-method-robust**, not an artifact of one specific audio-preprocessing pipeline.

## The denoise-robust claim

> The MMP P2:familiarity Bonferroni-pass holds independently across three audio conditions:
>
> | Audio | MMP P2 rb | p_bonf | clips_pos |
> |---|---|---|---|
> | original (no denoise) | +0.201 | 0.020 | 6/7 |
> | afftdn (ffmpeg Wiener) | +0.231 | 0.009 | 7/7 |
> | **noisereduce (non-stationary spectral)** | **+0.222** | **0.0053** | **7/7** |
>
> The chill marker is robust to denoise-algorithm choice. noisereduce gives the strongest single-channel raw p; afftdn gives the broadest channel set (4 vs 2 Bonferroni-pass).

## Protocol

Identical to L4 but on `chillsdb1_noisereduce` engine cache (built from noisereduce-denoised audio).

## What this test asserts

1. `test_mmp_p2_bonferroni_pass_noisereduce` — MMP P2 Bonferroni-pass on noisereduce variant (independent algorithm from afftdn)
2. `test_mmp_p2_within_tolerance_noisereduce` — numbers reproduce paper-time noisereduce baseline
3. `test_denoise_method_robust_directionality` — afftdn + noisereduce agree on MMP P2 direction (both positive)

## Why this matters

A skeptical reviewer might object: "your denoise pipeline could be selectively boosting whatever signal you're looking for." This layer answers: a **second, independently-implemented** denoise algorithm (different signal model: non-stationary spectral subtraction vs Wiener filtering) reproduces the finding at **higher confidence** on the dominant channel.

## Wallclock

~8-10 min (same as L4).

## Output

- `results/tc006_noisereduce_aggregate.csv` — 22 channels × noisereduce variant clip-aggregate.
