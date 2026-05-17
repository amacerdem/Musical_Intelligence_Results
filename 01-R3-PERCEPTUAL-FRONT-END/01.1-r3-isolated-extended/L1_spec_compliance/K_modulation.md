# L1 — Group K Modulation (dims 83–96) — Spec Compliance Report

**Engine pin:** `318eb2f5…` · **Test file:** [test_k_modulation.py](test_k_modulation.py)

## Spec sources

| Dim | Name                  | Range | Source                                              |
|-----|-----------------------|-------|-----------------------------------------------------|
| 83  | `modulation_0_5Hz`    | [0,1] | modulation FFT energy at 0.5 Hz, max-normalised     |
| 84  | `modulation_1Hz`      | [0,1] | same at 1 Hz                                         |
| 85  | `modulation_2Hz`      | [0,1] | same at 2 Hz                                         |
| 86  | `modulation_4Hz`      | [0,1] | same at 4 Hz (= source for `fluctuation_strength`)  |
| 87  | `modulation_8Hz`      | [0,1] | same at 8 Hz                                         |
| 88  | `modulation_16Hz`     | [0,1] | same at 16 Hz                                        |
| 89  | `modulation_centroid` | [0,1] | `(weighted log2(rate) − (−1)) / (4 − (−1))`         |
| 90  | `modulation_bandwidth`| [0,1] | weighted std(log2 rates) / 2.5                      |
| 91  | `sharpness_zwicker`   | [0,1] | DIN 45692 — Bark-band weighted z-axis ratio         |
| 92  | `fluctuation_strength`| [0,1] | = `modulation_4Hz`                                   |
| 93  | `loudness_a_weighted` | [0,1] | IEC 61672-1 A-weighted mel sum, max-normalised      |
| 94  | `alpha_ratio`         | [0,1] | `Σ mel<1kHz / Σ mel` (Hammarberg 1980)              |
| 95  | `hammarberg_index`    | [0,1] | `sigmoid(peak<2kHz / peak[2-5kHz] / 5)`             |
| 96  | `spectral_slope_0_500`| [0,1] | sigmoid(LSE slope of mel bins 0..17 × 10)           |

## Test inventory (49 tests, all PASS)

- 14 dims × range/finiteness on 8 stimulus families (28 tests)
- 14 dims × canonical-name agreement
- **Algebraic identity**: `fluctuation_strength ≡ modulation_4Hz` exactly (engine line 154) — verified bit-identical on all 8 stimulus families
- **Modulation-window engagement**: a strongly-AM-modulated tone fires the modulation FFT at the documented sliding-window centres (frames 172, 258, 344, 430, …, hopping by 86 frames per `_MOD_HOP`) — at least 4 of the expected centres get nonzero energy
- **Spectral-band fingerprints**:
  - 200 Hz tone has higher `alpha_ratio` than 5 kHz tone (sub-1kHz energy dominance)
  - 5 kHz tone has higher `sharpness_zwicker` than 200 Hz tone (DIN 45692 z-axis weight)
- **AM tone has more total modulation energy than constant-amplitude tone**
- **Disclosed engine behaviour — per-rate max-norm**: pinned. Engine `k_modulation/group.py:125-127` divides each rate column by its time-axis max. After this normalisation, every rate that ever fires reaches ≈ 1 at its strongest window, so per-frame argmax across the 6 rate dims does **not** localise the AM rate of the stimulus. A pure 8 Hz AM tone produces ~0.99 on all six rate dims at the same centre frame. Test pins this property: if a future engine change removes per-rate norm (and modulation_8Hz becomes a real 8 Hz detector), this test trips and forces an L1-MD update.
- Determinism: bit-identical run-to-run

## Verdict

**49/49 PASS.** Group K's modulation FFT, DIN 45692 sharpness, A-weighted
loudness, alpha-ratio, Hammarberg, and spectral-slope dims behave as
documented. Two known engine quirks are pinned: (a) per-rate max-norm
prevents cross-rate argmax, (b) `fluctuation_strength` is by-construction
identical to `modulation_4Hz` (no semantic difference at v1.0.0).
