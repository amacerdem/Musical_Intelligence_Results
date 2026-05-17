# L1 — Group C Timbre (dims 12–20) — Spec Compliance Report

**Engine pin:** `318eb2f5…` · **Test file:** [test_c_timbre.py](test_c_timbre.py)

## Spec sources

| Dim | Name                       | Range | Engine formula                                                       |
|-----|----------------------------|-------|----------------------------------------------------------------------|
| 12  | `warmth`                   | [0,1] | `sigmoid(6·(low_lt_1kHz_energy_ratio − 0.7))`                        |
| 13  | `sharpness`                | [0,1] | `sigmoid(6·(zwicker_high_emphasis − 0.3))`                           |
| 14  | `tonalness`                | [0,1] | `mel_peak / mel_sum`                                                 |
| 15  | `clarity`                  | [0,1] | normalised mel centroid                                              |
| 16  | `spectral_smoothness`      | [0,1] | `1 − |Δmel|.mean() / frame_energy` (clamped)                         |
| 17  | `spectral_autocorrelation` | [0,1] | lag-1 autocorrelation of mel spectrum                                |
| 18  | `tristimulus1`             | [0,1] | `mel[:N/3].sum / mel.sum`                                            |
| 19  | `tristimulus2`             | [0,1] | `mel[N/3:2N/3].sum / mel.sum`                                        |
| 20  | `tristimulus3`             | [0,1] | `mel[2N/3:].sum / mel.sum`                                           |

## Test inventory (32 tests, all PASS)

- 9 dims × range/finiteness on 8 stimulus families (18 tests)
- 9 dims × canonical-name agreement
- **Algebraic identity**: `tristimulus1 + tristimulus2 + tristimulus3 ≈ 1` on non-degenerate stimuli (silence, impulse excluded — `mel.sum → eps` makes the partition degenerate by design)
- **Behavioural fingerprints**:
  - 4 kHz tone is sharper / less warm than 200 Hz tone (strict ordering on both dims)
  - Pure tone more tonal than white noise
  - Silence → smoothness near 1 (no per-frame jaggedness)
- Determinism: bit-identical run-to-run

## Verdict

**32/32 PASS.** Group C extracts the spectral-distribution descriptors its
spec promises, with the documented partition identity holding on all
audio-bearing stimuli.
