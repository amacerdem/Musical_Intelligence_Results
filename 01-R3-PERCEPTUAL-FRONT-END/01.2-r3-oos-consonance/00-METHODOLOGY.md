# Phase 01.2 — R³ OOS Consonance — Methodology (LOCKED 2026-05-07)

**Axis ID:** AXIS-1-OOS
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
**Source datasets** (read-only, no copies):
- `Science/datasets/consonance/dyad_anchor_2018.csv` (DEV; reference, already PASS in Phase 2)
- `Science/datasets/consonance/eerola2021_exp3.csv` (OOS, N=617 chords)
- `Science/datasets/consonance/marjieh2024/data-csv/rating_dyh3dd.csv` (OOS, harmonic 3dB rolloff, N=7,500 ratings → 13 semitone bins)
- `Science/datasets/consonance/harrison2024_carillon/carillon-behavioural-profile.csv` (OOS inharmonic, behavioural profile)
- `Science/datasets/consonance/harrison2024_carillon/lower_bell_spectrum.csv` (carillon timbre)
- `Science/datasets/consonance/harrison2024_carillon/upper_bell_spectrum.csv` (carillon timbre)

## 1. Operationalisation

All four datasets use the same R³ pipeline as Phase 2. The R³ Group A consonance feature names are taken from the canonical engine API (`Musical_Intelligence.ear.r3.groups.a_consonance.group.ConsonanceGroup.feature_names`):

```
[0] roughness
[1] sethares_dissonance
[2] helmholtz_kang
[3] stumpf_fusion
[4] sensory_pleasantness     # paper main-text refers to this channel as "autocorrelation_peak"
[5] inharmonicity
[6] harmonic_deviation
```

The paper main text and Table c3_r3_oos use three labels: `stumpf` (= [3] stumpf_fusion), `autocorr` (= [4] sensory_pleasantness, the paper's main-text alias for this channel — same engine output, see paper §13-dyad anchor Honest-effect-size framing footnote on the calibrated `sensory_pleasantness = 0.6·(1−sethares) + 0.4·stumpf` definition), `rough` (= [0] roughness).

### 1.1 Audio synthesis

- Sample rate: 44 100 Hz, dtype float32, **identical to Phase 2** to keep engine output bit-comparable.
- Mel transform: `n_fft=2048, hop_length=256, n_mels=128, power=2.0`, log1p, identical to V1 / Phase 2.
- Duration: 0.5 s per stimulus.
- Harmonic timbres (13-dyad anchor, Eerola, Marjieh): 6 harmonics, `1/n` amplitude decay.

### 1.2 Per-dataset stimulus construction

| Dataset | Stimulus | Source field | Synthesis |
|---|---|---|---|
| 13-dyad anchor 2018 | 13 dyads | `semitones` | `synthesize_interval(s, f0=261.63, n_harm=6)` |
| Eerola Exp3 | 617 chords (size 2–4) | `midi` (e.g. `60-64-67`) | `synthesize_chord(midi_notes, n_harm=6)` |
| Marjieh 2024 | 7,500 ratings → 13 integer-semitone bins | `v1` (continuous semitones), `rating` | aggregate by `round(v1)`, keep bins with ≥3 samples, `synthesize_interval(s_int, f0=261.63, n_harm=6)` |
| Harrison Carillon | 1,501 interval rows from `carillon-behavioural-profile.csv`, sub-sampled to one row per 0.1 semitone (151 rows) | `pitch_interval`, `pleasantness` | inharmonic dyad: lower bell at 261.63 Hz with 12 partials per `lower_bell_spectrum.csv`, upper bell at $261.63 \cdot 2^{i/12}$ Hz with partials per `upper_bell_spectrum.csv` |

### 1.3 Spearman ρ

```python
ρ, p = scipy.stats.spearmanr(human_rating, channel_value)
```

For each dataset × channel ∈ {stumpf_fusion, sensory_pleasantness, roughness}, compute ρ once. No bootstrap, no permutation, no FDR at this phase (FDR aggregation lives in Phase 16).

## 2. Engine-runner contract

All R³ extraction goes through the canonical Phase-2-validated path:

```python
from Musical_Intelligence.ear.r3.extractor import R3Extractor
import torchaudio.transforms as T_audio

_r3 = R3Extractor()
_mel = T_audio.MelSpectrogram(sample_rate=44_100, n_fft=2048, hop_length=256, n_mels=128, power=2.0)

def extract_r3(audio):
    mel = torch.log1p(_mel(audio))
    out = _r3.extract(mel, audio=audio, sr=44_100)
    return out.features[0, :, :7].mean(dim=0).numpy()  # (7,) consonance vector
```

This is byte-identical to the V1 / Phase 2 entry. **No engine code is modified.**

## 3. Per-claim paper values + tolerances (PRE-REGISTERED)

| Claim ID | Channel | Dataset | Paper ρ | Tolerance | Pre-registered decision rule |
|---|---|---|---|---|---|
| C-R3OOS-01 | stumpf_fusion | Eerola Exp3 (N=617) | −0.581 | abs ≤ 0.05 AND sign−consistent (paper sign) | PASS / FAIL |
| C-R3OOS-02 | sensory_pleasantness ("autocorr") | Eerola Exp3 (N=617) | +0.518 | abs ≤ 0.05 AND sign+consistent | PASS / FAIL |
| C-R3OOS-03 | roughness | Eerola Exp3 (N=617) | −0.433 | abs ≤ 0.05 AND sign−consistent | PASS / FAIL |
| C-R3OOS-04 | stumpf_fusion | Marjieh 2024 (13 bins) | −0.769 | abs ≤ 0.05 AND sign−consistent | PASS / FAIL |
| C-R3OOS-05 | sensory_pleasantness | Marjieh 2024 (13 bins) | +0.890 | abs ≤ 0.05 AND sign+consistent | PASS / FAIL |
| C-R3OOS-06 | roughness | Marjieh 2024 (13 bins) | −0.813 | abs ≤ 0.05 AND sign−consistent | PASS / FAIL |
| C-R3OOS-07 | stumpf_fusion | Carillon (inharmonic) | −0.824 | abs ≤ 0.05 AND sign−consistent | **Falsifiable Table 5 #1** PASS / FAIL |
| C-R3OOS-08 | sensory_pleasantness | Carillon (inharmonic) | +0.852 | abs ≤ 0.05 AND sign+consistent | PASS / FAIL |
| C-R3OOS-09 | roughness | Carillon (inharmonic) | −0.731 | abs ≤ 0.05 AND sign−consistent | PASS / FAIL |
| C-R3OOS-10 | Anti-overfit invariant | Carillon vs 13-dyad anchor | $|ρ_{stumpf,carillon}| > |ρ_{stumpf,dyad-anchor}|$ (paper: 0.824 > 0.797) | sign + magnitude inequality | PASS / FAIL |

Sign convention: throughout this axis, ρ is computed against the **human consonance / pleasantness rating** as the y-variable. Higher rating = more consonant / more pleasant. So channels that index dissonance carry a negative sign (stumpf_fusion is the engine's signed dissonance score in this convention; see paper §13-dyad anchor Honest-effect-size framing footnote on the sign-flip vs Table c3_r3_groups).

## 4. Iteration policy

Per `02-ITERATION-POLICY.md`:

- First-run paper-deviation > tolerance → debug protocol (engine HEAD diff → dataset diff → methodology diff → determinism → numerical → seed audit), one cause per iteration, ≤ 5 iterations before escalation.
- This phase **may not edit the methodology mid-run to chase a number** (forbidden p-hacking move).
- This phase **may not** edit engine constants to fit an OOS number — engine is frozen since pre-V1, validated bit-identical in Phase 2 + ECE phase.

## 5. What this phase does NOT do

- No FDR (paper-wide BB-FDR aggregation lives in Phase 16; Eerola 50/97 is Phase 7's responsibility, since it counts across **all 97 R³ dimensions**, not just Group A).
- No bootstrap CI (Carillon 95% CI lives in Falsifiable Table 5; this phase reports point ρ).
- No tonal scope split (Phase 14 cross-cultural will reproduce Marjieh stretched / compressed / Korean / gamelan separately).
- No determinism re-test (Phase 0 + Phase 2 already verified bit-identical engine across processes).

## 6. What constitutes PASS for the axis

- 9/10 individual claims PASS at ±0.05 tolerance, AND
- C-R3OOS-10 (anti-overfit invariant: |ρ_carillon_stumpf| > |ρ_dyad-anchor_stumpf|) PASS.

If 1–2 claims FAIL at ±0.05 but reproduce within ±0.10 with sign-consistency, downgrade to PARTIAL with disclosure. If C-R3OOS-10 fails (i.e., reproduced Carillon |ρ| does NOT exceed reproduced 13-dyad anchor |ρ|), report as FAIL — this is the load-bearing anti-overfitting claim and may not be hedged.
