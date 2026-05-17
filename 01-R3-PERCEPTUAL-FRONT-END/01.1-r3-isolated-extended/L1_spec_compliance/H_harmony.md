# L1 — Group H Harmony & Tonality (dims 51–62) — Spec Compliance Report

**Engine pin:** `318eb2f5…` · **Test file:** [test_h_harmony.py](test_h_harmony.py)

## Stage placement

Group H is **Stage 2** — depends on Group F's chroma (97-D indices 25–36).
Reads chroma via `compute_with_deps`; the bare `compute(mel)` path returns
zeros (intentional fallback).

## Spec sources

| Dim | Name                     | Range | Source                                                    |
|-----|--------------------------|-------|-----------------------------------------------------------|
| 51  | `key_clarity`            | [0,1] | `(max − mean)` of 24 KK-profile correlations × 5 (clamped) |
| 52  | `tonnetz_fifth_x`        | [0,1] | `(sin(fifth-axis) + 1)/2` — Harte 2010                    |
| 53  | `tonnetz_fifth_y`        | [0,1] | `(cos(fifth-axis) + 1)/2`                                 |
| 54  | `tonnetz_minor_x`        | [0,1] | `(sin(minor-third axis) + 1)/2`                           |
| 55  | `tonnetz_minor_y`        | [0,1] | `(cos(minor-third axis) + 1)/2`                           |
| 56  | `tonnetz_major_x`        | [0,1] | `(sin(major-third axis) + 1)/2`                           |
| 57  | `tonnetz_major_y`        | [0,1] | `(cos(major-third axis) + 1)/2`                           |
| 58  | `voice_leading_distance` | [0,1] | `L1(Δchroma)/2`                                           |
| 59  | `harmonic_change`        | [0,1] | `1 − cos_sim(chroma_t, chroma_{t-1})`                    |
| 60  | `tonal_stability`        | [0,1] | `key_clarity · (1 − smooth(harmonic_change))`            |
| 61  | `diatonicity`            | [0,1] | `1 − (active_PCs − 7)/5`, clamped                         |
| 62  | `syntactic_irregularity` | [0,1] | `1 − exp(−KL(chroma || best key template))`              |

## Test inventory (43 tests, all PASS)

- 12 dims × range/finiteness on 8 stimulus families (24 tests)
- 12 dims × canonical-name agreement
- **Boundary identities** (engine-enforced via zero-init at frame 0):
  - `voice_leading_distance[t=0] ≡ 0`
  - `harmonic_change[t=0] ≡ 1` (engine convention: no prior frame ⇒ report maximum change)
- **Tonnetz unit-circle invariant**: each (sin, cos) pair satisfies `(2x − 1)² + (2y − 1)² ≤ 1.10` on every frame & non-degenerate stimulus, verifying the (sin, cos) encoding is preserved through the affine [0,1] shift
- **Behavioural fingerprints**:
  - Pure tone (1 active PC) → higher diatonicity than white noise
  - White noise → low key_clarity (no key stands out)
  - Constant tone → harmonic_change near 0 (chroma is stationary)
- Determinism: bit-identical run-to-run

## Verdict

**43/43 PASS.** Group H's KK-profile key-clarity scoring, Harte Tonnetz
projection, voice-leading / harmonic-change deltas, and diatonicity
indicator behave exactly as documented. Both boundary conventions
(vl=0, change=1 at t=0) are pinned.
