# L8 — TC007 Pre/Post Event-Window Asymmetry

**Purpose:** Test whether engine chill response is **temporally symmetric** (sustained) or **sharply biphasic** (peaks before/after event).

## The temporal-structure claim

> Splitting the ±5 s event window into pre-event (−5..0 s) and post-event (0..+5 s) halves reveals that:
>
> - **MMP P2:familiarity** is symmetric: rb_pre ≈ rb_post ≈ +0.20 (sustained chill response)
> - **AAC autonomic-prediction channels** (F0, F1) are mildly **POST-dominant** (1-3 s reaction-lag of button-press behind actual arousal peak)
> - **DAED consummatory cluster** (f02, f04) is negative in **both halves** (sustained suppression, not sharply biphasic)
>
> The Salimpoor-Sapolsky sharply-biphasic temporal structure is **NOT cleanly demonstrated** at this fine-grained split — the engine's chill response is more sustained than sharply temporally-locked.

## What this test asserts

1. `test_mmp_p2_positive_both_halves` — MMP P2 positive in BOTH pre and post halves (no temporal flip)
2. `test_aac_post_dominance_modest` — AAC autonomic asymmetry within ±0.20 absolute (modest, not catastrophic)
3. `test_daed_negative_both_halves` — DAED consummatory cluster sustained-negative

## Output

- `results/tc007_pre_post_aggregate.csv` — 6 test channels × pre/post rb breakdown.

## Refinement note

Paper-time TC007 finding refines TC004's "biphasic composite" interpretation: the composite IS sign-correct (positive autonomic + negative consummatory), but the temporal locking is **slow-time-scale sustained**, not millisecond-precise biphasic. This is consistent with the engine's continuous-trajectory architectural claim — it emits flowing state, not click-locked impulses.
