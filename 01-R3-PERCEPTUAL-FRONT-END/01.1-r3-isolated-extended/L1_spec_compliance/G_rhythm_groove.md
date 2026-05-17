# L1 — Group G Rhythm & Groove (dims 41–50) — Spec Compliance Report

**Engine pin:** `318eb2f5…` · **Test file:** [test_g_rhythm_groove.py](test_g_rhythm_groove.py)

## Stage placement

Group G is **Stage 2** — depends on Group B's `onset_strength` (97-D
index 11). Computed via `compute_with_deps`. Operates over a 688-frame
analysis window (~4 s); short clips return zero output. L1 stimulus
families therefore use 5-s clips.

## Spec sources

| Dim | Name                  | Range | Source                                                         |
|-----|-----------------------|-------|----------------------------------------------------------------|
| 41  | `tempo_estimate`      | [0,1] | `(BPM − 30) / 270`, BPM = 172.27·60/best_lag                  |
| 42  | `beat_strength`       | [0,1] | onset autocorrelation peak at best_lag                         |
| 43  | `pulse_clarity`       | [0,1] | per-window-aggregated periodicity strength                    |
| 44  | `syncopation_index`   | [0,1] | fraction of onset peaks falling 25-75 % off the beat          |
| 45  | `metricality_index`   | [0,1] | cross-window beat-grid alignment                              |
| 46  | `isochrony_nPVI`      | [0,1] | `1 − nPVI/200` over inter-onset intervals                      |
| 47  | `groove_index`        | [0,1] | composite (subcortical/cortical timing surrogates)             |
| 48  | `event_density`       | [0,1] | onset peaks / sec, normalised                                  |
| 49  | `tempo_stability`     | [0,1] | `1 − std(BPM_window) / mean`                                   |
| 50  | `rhythmic_regularity` | [0,1] | inverse `std(IOI) / mean(IOI)`                                 |

## Test inventory (35 tests, all PASS)

- 10 dims × range/finiteness on 8 stimulus families (20 tests)
- 10 dims × canonical-name agreement
- **Behavioural fingerprints**:
  - Metronome → high `pulse_clarity` AND high `beat_strength` AND high `tempo_stability` (octave-invariant periodicity check)
  - 60 BPM metronome → smaller `tempo_estimate` than 180 BPM metronome
  - Metronome `isochrony_nPVI` is finite & in range (well-formedness; tighter claims are downstream-detection issues)
- **Disclosed engine behaviour — octave-doubling**: pinned. Engine implements Dixon 2001 / Klapuri 2003 octave preference (lines 79-86): when 2× lag autocorrelation > 70 % of best-peak strength, prefer the longer (slower) lag. On a perfectly-isochronous 120 BPM metronome, the 60 BPM (doubled) autocorrelation is identical, so the engine consistently reports the slower octave. Test pins detected BPM at 50–70 BPM (≈ doubled-from-120) so a future octave-rule change trips it.
- Determinism: bit-identical run-to-run

## Verdict

**35/35 PASS.** Group G's Stage-2 onset-autocorrelation periodicity
detector behaves as documented; the engine's octave-preference rule is
explicitly pinned so cross-octave assumptions in downstream H³/C³
consumers can be audited.
