# Phase 01.2 extended — R³ Extended OOS Consonance Battery — Methodology (LOCKED 2026-05-16)

**Axis ID:** AXIS-1-OOS-EXT
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
**Pre-registration:** see `03-PRE-REGISTRATION.md` (frozen 2026-05-16
before any first run).

## 1. Purpose

Phase 6 extended tests the R³ Group A consonance front-end against nine
consonance datasets that span four orthogonal axes of variation:

| Axis | Datasets |
|---|---|
| Within-corpus stimulus variation | Marjieh Study 1A harmonic (C-R3EXT-01), Study 1B flute / guitar / piano (C-R3EXT-02..04), Study 4A pure (C-R3EXT-05) |
| Cross-methodology (neural) | Bidelman & Krishnan 2009 FFR (C-R3EXT-06) |
| Cross-theoretical-framework | Schwartz et al. 2003 speech-derived (C-R3EXT-07), Sethares 1993 analytical reference (C-R3EXT-08) |
| Cross-cultural | Lahdelma et al. Indian interval tension, Carnatic / Hindustani / Indian non-musicians (C-R3EXT-09) |

The phase is a generalisation audit, not a parameter search. The
synthesis recipe (§2.2) and per-claim pipeline (§2.3) are locked at
pre-reg time and forbidden from post-hoc adjustment.

## 2. Operationalisation

### 2.1 R³ Group A engine channels

Engine API:
`Musical_Intelligence.ear.r3.groups.a_consonance.group.ConsonanceGroup.feature_names`

```
[0] roughness                  reported in Phase 6 extended
[1] sethares_dissonance
[2] helmholtz_kang
[3] stumpf_fusion              reported in Phase 6 extended
[4] sensory_pleasantness       reported in Phase 6 extended
[5] inharmonicity
[6] harmonic_deviation
```

All seven channels are computed and stored for every stimulus. Decision
rules apply only to the three "headline" channels named in
§Pre-registration §Decision rules.

### 2.2 Audio pipeline

Locked at pre-reg time. No deviation permitted by pre-reg §Forbidden
moves item 2:

```python
SR        = 44_100
DURATION  = 0.5
N_HARM    = 6   # default; pure-tone sub-study uses N_HARM=1
F0_BASE   = 261.625565   # 12-TET C4, A4=440
```

Mel transform:

```python
T_audio.MelSpectrogram(sample_rate=44100, n_fft=2048, hop_length=256,
                       n_mels=128, power=2.0)
mel = torch.log1p(mel)
mel = mel / mel.max().clamp(min=1e-8)
r3_features = R3Extractor().extract(mel, audio=audio, sr=44100).features
r3_group_a = r3_features[0, :, :7].mean(dim=0)
```

Determinism: single-thread BLAS (`OMP_NUM_THREADS=1`,
`OPENBLAS_NUM_THREADS=1`, `MKL_NUM_THREADS=1`,
`VECLIB_MAXIMUM_THREADS=1`, `NUMEXPR_NUM_THREADS=1`), `float32`
throughout, `torch.no_grad`.

### 2.3 Per-dataset stimulus construction

| Claim ID | Source field | Synthesis call |
|---|---|---|
| C-R3EXT-01 harmonic | `v1` → 13 integer-bins | `synth_interval(s, n_harm=6)` |
| C-R3EXT-02..04 flute/guitar/piano | `v1` → 13 integer-bins | `synth_interval(s, n_harm=6)` (6-partial 1/n proxy; see §Limitations) |
| C-R3EXT-05 pure | `v1` → 13 integer-bins | `synth_interval(s, n_harm=1)` |
| C-R3EXT-06 Bidelman FFR | `semitones` per row | `synth_interval(s, n_harm=6)` |
| C-R3EXT-07 Schwartz | `semitones` per row | `synth_interval(s, n_harm=6)` |
| C-R3EXT-08 Sethares | `semitones` per row | `synth_interval(s, n_harm=6)` |
| C-R3EXT-09 Indian Tension | `Interval` (name) per row → semitone via lookup | `synth_interval(s, n_harm=6)` |

### 2.4 Aggregation

For dense-rating Marjieh CSVs (continuous `v1`, dense `rating`):

```python
df = pd.read_csv(csv_path)
df["bin"] = df["v1"].round().clip(0, 12).astype(int)
mean_per_bin = df.groupby("bin")["rating"].mean()
assert len(mean_per_bin) == 13, "expected 13 integer-semitone bins"
```

For pre-aggregated CSVs (Bidelman / Schwartz / Sethares — one row per
interval):

```python
df = pd.read_csv(csv_path)
human = df[behavioural_or_analytical_column].values  # per-row
```

For Indian Tension (per-participant per-interval rating, named intervals):

```python
INTERVAL_TO_SEMITONE = {
    "m2": 1, "M2": 2, "m3": 3, "M3": 4, "P4": 5, "A4": 6,
    "P5": 7, "m6": 8, "M6": 9, "m7": 10, "M7": 11, "P8": 12,
}
df = pd.read_csv(csv_path)
df["semitone"] = df["Interval"].map(INTERVAL_TO_SEMITONE)
mean_per_interval = df.groupby("semitone")["tensionrating"].mean()
# Sign: tension ↑ ⇔ consonance ↓, so engine_channel_sign_convention is reversed.
```

### 2.5 Statistical test

`scipy.stats.spearmanr` per channel × per dataset. Two-sided p-values
reported. **No multiple-comparison correction within Phase 6 extended** — the
phase reports raw correlations and applies the per-claim decision rule
(§Pre-registration). FDR correction applies at the paper-wide
aggregation level (Phase 16).

## 3. Channel-sign reference

The expected sign per channel is derived from the Group A specification
(see `Musical_Intelligence/ear/r3/groups/a_consonance/` engine source):

```
stumpf_fusion        +    Stumpf-Helmholtz fusion score increases with
                          interval consonance by construction.
sensory_pleasantness +    Sensory pleasantness composite (1 − sethares
                          + stumpf fusion) increases with consonance by
                          construction.
roughness            −    Plomp-Levelt / Sethares roughness sum
                          decreases with consonance by construction.
```

For datasets whose target column encodes *dissonance* or *tension*
rather than *consonance* (e.g. `relative_dissonance` in Sethares 1993),
all expected signs are reversed; the per-dataset polarity is read from
the source README or column header and logged in
`results/29_sign_convention.json` before correlation computation.

## 4. Reproducibility

```
cd 29-r3-extended-oos-consonance
bash code/run.sh
```

Expected wall-clock on Apple M2 + 8 GB unified memory, single-threaded:

| Tier | Claims | Estimate |
|---|---|---|
| T1 | C-R3EXT-01..05 (5× Marjieh sub-studies, 13 stimuli each) | ~15–25 min |
| T2 | C-R3EXT-06..09 (Bidelman 7 + Schwartz 13 + Sethares 13 + Indian Tension 12 stimuli) | ~5–8 min |
| **Total** | **9 claims** | **~20–35 min** |

## 5. Limitations (locked at pre-reg)

1. **Instrument-timbre proxy for C-R3EXT-02..04.** The Marjieh Study 1B
   flute / guitar / piano sub-studies use synthesised instrument spectra
   in the original experiment. Phase 6 extended uses the same 6-partial 1/n
   harmonic proxy as the harmonic baseline, which captures the
   fundamental + first 5 harmonics but does not reproduce the detailed
   formant / decay structure of each instrument. This is a methodological
   approximation declared at pre-reg time, not a result-dependent fix.
   If a sub-study claim does not meet the PASS threshold under this
   proxy, the result is recorded as PARTIAL with a synthesis-mismatch
   CAVEAT, **not re-run with adjusted synthesis** (forbidden by
   pre-reg §Forbidden moves item 2). Re-running with instrument-specific
   timbres is deferred to a future Phase 30+.

2. **Cross-cultural sub-studies deferred to a future phase.** Marjieh
   Study 2B Korean (`korean_dyad_*.csv`), Study 2C gamelan
   (`gamelan_dyad_gamdyrt.csv`), and Milne 2023 PNG-Sydney
   (`milne2023/raw_data.csv`, N=35,820) are not included in Phase 6 extended.
   These sub-studies require non-12-TET stimulus generation (gamelan
   bonang spectrum, Korean ajaeng spectrum, PNG instrument spectra)
   which is outside the locked Phase 6 extended synthesis recipe. They are
   inventoried for a planned Phase 30 cross-cultural extension.

3. **Stretched / compressed / 5-equal Marjieh sub-studies deferred.**
   Marjieh Study 2A stretched / compressed (`rating_dys3dd.csv`,
   `rating_dyc3dd.csv`) and Study 4A 5-equal / no-3rd
   (`rating_w3rdd.csv`, `rating_wo3rdd.csv`) require non-default
   harmonic-amplitude or harmonic-frequency mapping. Deferred to Phase 30.

4. **Spearman ρ only.** Phase 6 extended does not compute Pearson, Kendall τ,
   or bootstrap CIs. Pearson and CI re-statement are deferred to the
   Paper-side regenerator if needed.

5. **No noise floor.** Phase 6 extended does not synthesise with additive noise
   or amplitude jitter. Engine output is bit-identical across
   re-executions on the same hardware.
