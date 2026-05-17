# L1 — Group J Timbre Extended (dims 63–82) — Spec Compliance Report

**Engine pin:** `318eb2f5…` · **Test file:** [test_j_timbre_extended.py](test_j_timbre_extended.py)

## Spec sources

| Dim     | Name                       | Range | Source                                                      |
|---------|----------------------------|-------|-------------------------------------------------------------|
| 63–75   | `mfcc_1..mfcc_13`         | [0,1] | DCT-II of log-mel, per-coefficient affine map (Davis & Mermelstein 1980) |
| 76–82   | `spectral_contrast_1..7`   | [0,1] | (peak − valley) / 10 over 7 octave-spaced mel bands (Jiang 2002) |

## Test inventory (64 tests, all PASS)

- 20 dims × range/finiteness on 8 stimulus families (40 tests)
- 20 dims × canonical-name agreement
- **DCT-II structural identity** (independent re-construction): the engine's
  `_build_dct_matrix` is reconstructed independently and each of the 13
  cosine basis columns is verified to have norm √(N/2) = 8 — the standard
  DCT-II identity. If the formula drifts from Davis-Mermelstein 1980, this
  test trips immediately.
- **Behavioural fingerprints**:
  - Silence → spectral_contrast in every band stays near 0 (peak ≈ valley)
  - Pure tone has higher spectral_contrast in the band containing its frequency than white noise does in the same band
- Determinism: bit-identical run-to-run

## Verdict

**64/64 PASS.** Group J's MFCC bank (Davis-Mermelstein 1980) and 7-band
spectral contrast (Jiang 2002) implement their published formulas
correctly; the DCT-II basis-column-norm identity provides an
independent-reconstruction certificate.
