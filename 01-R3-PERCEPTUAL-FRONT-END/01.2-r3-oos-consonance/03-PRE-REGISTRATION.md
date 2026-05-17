# Phase 01.2 — Pre-Registration (FROZEN 2026-05-07 before any first run)

## Hypothesis

Under the frozen engine HEAD `318eb2f529d7103e8b7d80b01228357fdc4e0217`, the R³ Group A consonance features (`stumpf_fusion`, `sensory_pleasantness`, `roughness`) reproduce the paper's published Spearman ρ values on three out-of-sample datasets within ±0.05, with sign preserved. The Harrison Carillon stumpf_fusion correlation exceeds the 13-dyad DEV magnitude in absolute value (anti-overfitting invariant).

## Decision rules

```
PRE-REGISTERED DECISION RULES (frozen 2026-05-07)

Per-claim (C-R3OOS-01..09):
  PASS    if |ρ_reproduced - ρ_paper| ≤ 0.05  AND  sign(ρ_reproduced) = sign(ρ_paper)
  PARTIAL if |ρ_reproduced - ρ_paper| ≤ 0.10  AND  sign-consistent
  FAIL    otherwise

Anti-overfit invariant (C-R3OOS-10):
  PASS if |ρ_carillon_stumpf,reproduced| > |ρ_dyad-anchor_stumpf,reproduced|
       AND sign(ρ_carillon_stumpf,reproduced) = sign(ρ_dyad-anchor_stumpf,reproduced) = -

Axis-level:
  CLOSED-PASS  if 9/10 individual claims PASS  AND  C-R3OOS-10 PASS
  CLOSED-PART  if 6-8/10 individual claims PASS  AND  C-R3OOS-10 PASS
  CLOSED-FAIL  if C-R3OOS-10 FAIL  OR  ≤5 individual claims PASS
```

## Seed

```
seed = int("2026" + "05" + "07" + "01") = 2026050701   # primary
```

(R³ extraction is deterministic — no RNG draws — so seed is recorded for forward compatibility only. No bootstrap or permutation in Phase 6.)

## Audio synthesis parameters (frozen)

```python
SR        = 44_100
DURATION  = 0.5
N_HARM    = 6   # harmonic timbres only
DECAY     = "1/n"
F0_BASE   = 261.625565  # MIDI 60 = C4 (12-TET A4=440)

mel:
  n_fft       = 2048
  hop_length  = 256
  n_mels      = 128
  power       = 2.0
  log         = log1p
```

## Carillon synthesis (locked)

For each interval `i` (in semitones), generate a dyad of two inharmonic bells:

```
lower_partials = lower_bell_spectrum.csv  # 12 partials with FrequencyRatio + Amplitude
upper_partials = upper_bell_spectrum.csv  # 12 partials, separate inharmonic structure
f0_lower = 261.625565
f0_upper = 261.625565 * 2 ** (i / 12.0)

audio = sum over partials in lower_partials [amp * sin(2π · f0_lower · ratio · t)]
      + sum over partials in upper_partials [amp * sin(2π · f0_upper · ratio · t)]
```

Both partial tables are normalised so that the Prime (ratio=1.0) partial has amplitude 1.0; remaining partials carry the per-bell amplitude column from the dataset (already published, no per-Phase-6 re-normalisation).

## Marjieh aggregation (locked)

```python
df = read_csv("rating_dyh3dd.csv")
df["s_int"] = df["v1"].round().astype(int).clip(0, 12)   # 13 bins, 0..12 semitones
agg = df.groupby("s_int")["rating"].agg(["mean", "count"]).reset_index()
agg = agg[agg["count"] >= 3]                               # drop sparse bins
ρ_paper, ρ_reproduced = spearmanr(agg["mean"], r3_channel(agg["s_int"]))
```

If the rounding produces ≠13 bins (e.g., 0..15 spans wider than 12), the count of bins reproduced is reported alongside ρ; tolerance still applies on the ρ value.

## Carillon sub-sampling (locked)

The carillon-behavioural-profile.csv is a smoothed Gaussian-process posterior at 0.01 semitone resolution → 1,501 rows on $i \in [0, 15]$. Sub-sample at every 0.1 semitone → 151 rows. Drop NA pleasantness rows. Run R³ on each row's synthesised inharmonic dyad.

## Forbidden moves (per `02-ITERATION-POLICY.md`)

- Editing audio synthesis parameters mid-axis to chase a number — that is methodology p-hacking.
- Editing engine constants — engine is frozen.
- Cherry-picking which sub-sample of carillon rows to report.
- Aggregating Marjieh at non-integer semitone resolution to chase ρ — paper specifies "13 semitone bins" verbatim.
