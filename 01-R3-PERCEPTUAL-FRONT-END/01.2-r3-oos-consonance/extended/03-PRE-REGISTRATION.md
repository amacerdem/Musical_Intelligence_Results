# Phase 01.2 extended — Pre-Registration (FROZEN 2026-05-16 before any first run)

## Scope

Phase 6 extended establishes the R³ Group A consonance validation portfolio
against nine consonance datasets spanning four axes of variation:

- **Within-corpus stimulus variation** — Marjieh 2024 Study 1A harmonic,
  Study 1B flute / guitar / piano, Study 4A pure
- **Cross-methodology** — Bidelman & Krishnan 2009 (FFR neural anchor)
- **Cross-theoretical-framework** — Schwartz et al. 2003 (speech-derived),
  Sethares 1993 (analytical reference)
- **Cross-complexity** — Eerola & Lahdelma 2021 Experiment 2 (chord
  ratings, N = 11,260, 12 aggregated source corpora)

## Hypothesis

At the pinned engine HEAD `318eb2f529d7103e8b7d80b01228357fdc4e0217`,
the R³ Group A consonance channels (`stumpf_fusion`,
`sensory_pleasantness`, `roughness`) produce correlations against
behavioural / neural / analytical consonance scores that are
sign-consistent with the Group A theoretical specification (see
`00-METHODOLOGY.md` §Channel-sign reference) and magnitude
|ρ| ≥ 0.60 on at least two of the three channels per dataset.

## Decision rules

```
PRE-REGISTERED DECISION RULES (frozen 2026-05-16 before any first run)

Per-dataset claim (C-R3EXT-{01..09}):

  Primary metric: Spearman ρ between an R³ Group A channel and the
                  dataset-provided behavioural / neural / analytical
                  consonance score. Three channels tested per dataset:
                  stumpf_fusion, sensory_pleasantness, roughness.

  Theoretical sign convention (from Group A specification,
  `00-METHODOLOGY.md` §Channel-sign reference):
                  stumpf_fusion        sign(ρ) = +
                  sensory_pleasantness sign(ρ) = +
                  roughness            sign(ρ) = −
  (Reversed for datasets whose target column encodes dissonance / tension
  rather than consonance; per-dataset polarity logged in
  `results/29_sign_convention.json` before correlation computation.)

  PASS    if  ≥ 2 / 3 channels satisfy |ρ| ≥ 0.60  AND  sign matches
              the theoretical convention above

  PARTIAL if  exactly 1 / 3 channels satisfies |ρ| ≥ 0.60 with
              sign-consistency, OR ≥ 2 / 3 channels satisfy
              0.40 ≤ |ρ| < 0.60 with sign-consistency

  FAIL    otherwise

Cross-dataset consistency invariant (C-R3EXT-CDC):

  PASS    if  for each of the three R³ channels, sign(ρ) is consistent
              with the theoretical convention on ≥ 7 / 9 datasets

  This invariant tests whether the channel-level sign behaviour holds
  across the full portfolio, independent of magnitude.

Hierarchy reproduction invariant (C-R3EXT-HRI):

  For each dataset, compute Spearman ρ between (a) the channel-derived
  consonance ranking and (b) the dataset-derived consonance ranking on
  the classical Western interval subset {P1, P4, M3, P5, m6, TT}. For
  C-R3EXT-09 Indian Tension (no P1 / unison stimulus), the subset is
  {P4, M3, P5, m6, TT}.

  PASS    if  ≥ 7 / 9 datasets show ranking_ρ ≥ 0.85 on the headline
              channel (sensory_pleasantness or stumpf_fusion, whichever
              has the larger |ρ| on the per-dataset full set)

Axis-level verdict:

  CLOSED-STRONG  if  ≥ 7 / 9 individual claims PASS  AND  CDC PASS  AND  HRI PASS
  CLOSED-PASS    if  ≥ 5 / 9 individual claims PASS  AND  CDC PASS
  CLOSED-PART    if  3–4 / 9 individual claims PASS  AND  CDC PASS
  CLOSED-FAIL    if  CDC FAIL  OR  ≤ 2 individual claims PASS
```

## Claim manifest (frozen)

| Claim ID | Dataset | N | File | Stimulus class |
|---|---|---|---|---|
| C-R3EXT-01 | Marjieh Study 1A harmonic | 7,500 → 13 bins | `marjieh2024/data-csv/rating_dyh3dd.csv` | 6-partial 1/n |
| C-R3EXT-02 | Marjieh Study 1B flute | 15,000 → 13 bins | `marjieh2024/data-csv/rating_flute_harmonic_harflt.csv` | Western harmonic timbre proxy |
| C-R3EXT-03 | Marjieh Study 1B guitar | 7,500 → 13 bins | `marjieh2024/data-csv/rating_guitar_harmonic_hargtr.csv` | Western harmonic timbre proxy |
| C-R3EXT-04 | Marjieh Study 1B piano | 7,500 → 13 bins | `marjieh2024/data-csv/rating_piano_harmonic_harpno.csv` | Western harmonic timbre proxy |
| C-R3EXT-05 | Marjieh Study 4A pure | 7,500 → 13 bins | `marjieh2024/data-csv/pure_dyad_purdyrt.csv` | Pure-tone (n_harm=1) |
| C-R3EXT-06 | Bidelman & Krishnan 2009 FFR | 7 intervals | `bidelman2009_ffr.csv` | Neural FFR / behavioural |
| C-R3EXT-07 | Schwartz et al. 2003 speech-derived | 13 intervals | `schwartz2003_speech_harmonics.csv` | Theoretical (speech) |
| C-R3EXT-08 | Sethares 1993 dissonance reference | 13 intervals | `sethares1993_dissonance.csv` | Analytical reference |
| C-R3EXT-09 | Lahdelma et al. — Indian interval tension | 852 ratings (Carnatic 312 / Hindustani 228 / Indian non-musicians 312) | `interval_tension/data/indian_tension_ratings.csv` | 12 named intervals (m2..P8) |

## Synthesis recipe (frozen, all dyad sub-studies)

```python
SR        = 44_100                  # Hz
DURATION  = 0.5                     # s
N_HARM    = 6                       # default for harmonic timbres
F0_BASE   = 261.625565              # Hz, 12-TET C4 from A4=440
# Each tone: sum_{n=1..N_HARM} (1/n) · sin(2π · f0 · n · t)
# Dyad: tone(f0) + tone(f0 · 2^(s/12))
```

Sub-study deviations (frozen at pre-reg time, no post-hoc adjustment):

| Sub-study | Deviation |
|---|---|
| C-R3EXT-05 pure | `N_HARM = 1` (single sinusoid per tone) |
| C-R3EXT-02..04 flute/guitar/piano | **Same 6-partial 1/n proxy** as harmonic baseline. The Marjieh paper's instrument timbres use synthesized instrument spectra; using the harmonic proxy is a DELIBERATE approximation, recorded here as a methodological declaration. If a channel correlation drops below the per-dataset PASS threshold under this proxy, the claim is recorded as PARTIAL with a synthesis-mismatch CAVEAT, **not** re-run with adjusted synthesis. |
| C-R3EXT-09 Indian Tension | `Interval` string ↦ semitone via {m2:1, M2:2, m3:3, M3:4, P4:5, A4:6, P5:7, m6:8, M6:9, m7:10, M7:11, P8:12}, then `synth_interval(s, n_harm=6)`. Sign reversed: tension ↑ ⇔ consonance ↓. Mean tension per interval computed across all 852 ratings (cross-group pooled); per-group sub-correlations reported as auxiliary, not load-bearing. |

## Aggregation (frozen)

For dense-rating CSVs (`v1` column = continuous semitone interval, `rating` = subject response):

```
bin = round(v1).clip(0, 12)               # 13 integer-semitone bins {0..12}
mean_rating_per_bin = df.groupby(bin).rating.mean()
engine_feature_per_bin = extract_r3(synth_interval(bin))
ρ = spearmanr(mean_rating_per_bin, engine_feature_per_bin)
```

For pre-aggregated CSVs (Bidelman, Schwartz, Sethares — one row per interval):

```
ρ = spearmanr(behavioural_or_analytical_column, engine_feature_per_interval)
```

For Eerola Exp 2 chord-level:

```
midi = parse_midi_string(row["midi"])
engine_feature = extract_r3(synth_chord(midi))
ρ = spearmanr(df.Rating, engine_features)
```

## Engine HEAD pin

```
ENGINE_HEAD = 318eb2f529d7103e8b7d80b01228357fdc4e0217
```

Verified at `_infra/manifests/engine_head.json`. Phase 6 extended must abort if
the vendored engine HEAD does not match this value.

## Seeds

```
seed_primary  = 2026051601    # YYYY MM DD 01 (date-encoded)
seed_bootstrap = None         # no bootstrap in Phase 6 extended
seed_perm      = None         # no permutation in Phase 6 extended
```

R³ extraction is deterministic — seeds recorded for forward
compatibility only.

## Forbidden moves

The following are explicitly forbidden during Phase 6 extended execution:

1. **No engine modification.** The script aborts if the aggregate SHA
   of the vendored `engine/Musical_Intelligence/` does not match the
   value recorded at `engine/HEAD.md`.
2. **No post-hoc synthesis adjustment.** Synthesis recipe is locked in
   §"Synthesis recipe" above. If a sub-study returns a low correlation
   under the locked recipe, the result is recorded as PARTIAL or FAIL
   per the decision rule — not "fixed" by adjusting synthesis.
3. **No dataset selection.** All nine claims must report a result.
   Adding or removing a claim after pre-reg lock is a protocol
   violation.
4. **No threshold adjustment.** PASS/PARTIAL/FAIL thresholds are locked.
   They do not move based on observed results.
5. **No channel cherry-picking.** All three R³ channels
   (`stumpf_fusion`, `sensory_pleasantness`, `roughness`) are reported
   for every claim. The PASS rule uses ≥ 2 / 3 — it does not require
   choosing which two.

## Independence audit (deferred to phase close)

At close, `01b-INDEPENDENCE-AUDIT.md` records a `git log -S` and `git
grep` sweep of the engine subtree at the pinned HEAD for each of the
nine input CSV filenames and dataset identifiers. The audit reports the
sweep results verbatim. The phase does not make an a-priori claim about
historical engine state; the audit is the test.
