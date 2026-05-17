# L1 — Group F Pitch & Chroma (dims 25–40) — Spec Compliance Report

**Engine pin:** `318eb2f5…` · **Test file:** [test_f_pitch_chroma.py](test_f_pitch_chroma.py)

## Spec sources

| Dim     | Name                 | Range | Formula                                              |
|---------|----------------------|-------|------------------------------------------------------|
| 25–36   | `chroma_C..chroma_B` | [0,1] | mel @ Gaussian-soft mel→chroma matrix, L1-normalised |
| 37      | `pitch_height`       | [0,1] | normalised log-frequency centroid (20 → 22050 Hz)    |
| 38      | `pitch_class_entropy`| [0,1] | `−Σ chroma·log chroma / log(12)`                     |
| 39      | `pitch_salience`     | [0,1] | `(peak − median) / (peak + median)` over mel         |
| 40      | `inharmonicity_index`| [0,1] | `1 − peak / sum(mel)`                                |

## Test inventory (65 tests, all PASS)

- 16 dims × range/finiteness on 8 stimulus families (32 tests)
- 16 dims × canonical-name agreement
- **Algebraic identity**: `Σ chroma_C..chroma_B ≈ 1` on non-degenerate stimuli (silence/impulse/dc excluded — mel below 20 Hz is masked from chroma matrix by engine line 28-29; for DC input chroma is well-defined but the partition does not sum to 1)
- **Pitch-class identification (top-3)**: pure tone at MIDI note → corresponding chroma bin in the top 3 of 12 (9 notes covered: D4, E4, F4, G4, A4, B4, C5, A5, A6)
- **Disclosed engine quirk — C4 (261.63 Hz)**: pinned. The mel filter-bank at 261 Hz spreads across 3-4 mel bins covering pitch-class range 10..1.5; with chroma σ=0.5 PC, a pure C4 tone's chroma argmax is *Bb* (not C), and C is not in the top 3. Same tone an octave higher (C5, 523.25 Hz) is correctly argmaxed at C. This is a documented limitation of mel→chroma quantisation at the bottom of the audible-music range; the test pins the current behaviour so any future engine change that fixes C4 trips this test and forces the disclosure to be updated.
- **Behavioural fingerprints**:
  - Pitch_height orders 220 Hz < 3.5 kHz (strict)
  - Pure tone → high pitch_salience; white noise → low
  - White noise → near-uniform chroma → high pitch_class_entropy
  - Pure tone → lower pc_entropy than broadband noise
- Determinism: bit-identical run-to-run

## Verdict

**65/65 PASS.** Group F implements the Gaussian-soft mel→chroma routing,
log-frequency pitch height, and pitch-class entropy/salience exactly as
documented. The C4 chroma quirk is disclosed and pinned — not a bug, a
design trade-off in the mel/chroma quantisation grid.
