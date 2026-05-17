# L5 — TC003 9-Full Sensitivity Check

**Purpose:** Verify that the 7-clean exclusion (Mr. Bean + Vocal Intros) is justified, not p-hacking.

## The exclusion-rationale claim

> Including the two structurally problematic stimuli (`CwzjlmBLfrQ` Mr. Bean comedy sketch + `YbNYinfj1h0` 15-song Vocal Intros compilation) materially **weakens** the engine's chill detection because they violate H³ Macro horizon continuity. The 7-clean subset is the appropriate test set; the 9-full result is **predictably weaker** but still directionally consistent.

## Protocol

Same as L4 but on **all 9 clips** instead of 7-clean.

## What this test asserts

1. `test_mmp_p2_present_in_9full` — MMP P2 channel present in 9-full result
2. `test_9full_directionally_positive_mmp` — MMP P2 still positive direction (excluded clips weaken but don't sign-flip)
3. `test_9full_weaker_than_7clean` — 9-full MMP P2 rb < 7-clean MMP P2 rb (exclusion rationale empirically supported)

## Why this matters

A reviewer might object: "you excluded 2 of 9 clips — that could be p-hacking." This layer directly answers: the exclusion was **theory-driven** (continuity-violating stimuli are out-of-scope for the engine's H³ Macro horizon claim), and the empirical result on the full set is consistent with the exclusion rationale (weaker but same direction).

## Output

- `results/tc003_9full_aggregate.csv` — 22 channels × 9-full clip aggregate, mirroring L4 schema.
