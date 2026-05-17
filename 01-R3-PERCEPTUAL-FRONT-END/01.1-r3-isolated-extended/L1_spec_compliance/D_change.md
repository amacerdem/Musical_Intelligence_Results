# L1 — Group D Change (dims 21–24) — Spec Compliance Report

**Engine pin:** `318eb2f5…` · **Test file:** [test_d_change.py](test_d_change.py)

## Spec sources

| Dim | Name                          | Range | Formula                                                  |
|-----|-------------------------------|-------|----------------------------------------------------------|
| 21  | `spectral_flux`               | [0,1] | `sigmoid(10·(L2(Δmel)/√128 − 0.15))`                    |
| 22  | `distribution_entropy`        | [0,1] | `H(p) / log(128)` — Shannon, normalised                  |
| 23  | `distribution_flatness`       | [0,1] | `exp(mean log p) / mean(p)` — Wiener entropy            |
| 24  | `distribution_concentration`  | [0,1] | `(HHI − 1/N) / (1 − 1/N)` — normalised Herfindahl       |

## Test inventory (18 tests, all PASS)

- 4 dims × range/finiteness on 8 stimulus families (8 tests)
- 4 dims × canonical-name agreement
- **Boundary identity**: `spectral_flux[t=0] ≡ sigmoid(−1.5) ≈ 0.182` (zero-init Δmel at frame 0)
- **Behavioural fingerprints**:
  - White noise has higher flatness than pure tone (uniform vs peaked spectrum)
  - Pure tone has higher concentration than white noise (HHI peaked at single bin)
  - Pure tone has lower distribution_entropy than white noise
  - Steady tone → spectral_flux remains at boundary baseline (no change frame-to-frame)
- Determinism: bit-identical run-to-run

## Verdict

**18/18 PASS.** Group D quantifies frame-to-frame change and per-frame
distribution shape exactly as documented; Wiener-entropy / HHI ordering
matches the published references.
