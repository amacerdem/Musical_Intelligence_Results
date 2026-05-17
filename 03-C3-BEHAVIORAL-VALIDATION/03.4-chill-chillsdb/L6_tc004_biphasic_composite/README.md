# L6 — TC004 Biphasic Composite (Salimpoor Pattern)

**Purpose:** Reproduce the biphasic anticipatory-vs-consummatory chill signature at the **composite** level.

## The biphasic claim

> Salimpoor 2011 / Sapolsky 2017 propose a biphasic chill response: **anticipatory** autonomic activation (NAcc-related, arousal-driven) RISES in the lead-up to and during chill, while **consummatory** dopamine signaling (caudate-related, hedonic-driven) FALLS. The engine should reproduce this pattern at the channel-cluster level.
>
> Definition:
>
> - Positive cluster (5 channels): MMP P2, AAC E0, AAC F0, AAC F1, AAC P2
> - Negative cluster (4 channels): DAED f02, DAED f04, SRP P2, UDP M1
>
> Composite = Σ(positive) − Σ(negative), within-clip z-scored.

## Protocol

Per-clip:
1. Load each of the 9 channels, z-score within-clip
2. Compute composite signal `Σ(pos_z) − Σ(neg_z)`
3. Mann-Whitney rank-biserial: event-window vs out-of-window
4. Null = 500 random event-time placements

Across clips: Fisher's combined p; clip-level Bonferroni (0.05/7) for composite significance.

## What this test asserts

1. `test_composite_positive_direction` — composite mean rb > 0 (Salimpoor biphasic sign-correct)
2. `test_composite_combined_p_significant` — composite combined_p < 0.05

## Paper-time observation

The composite IS significant (combined_p ≈ 0.0025 on afftdn 7-clean) but **does NOT exceed** `MMP P2` alone (rb = +0.170 composite vs +0.231 MMP P2 single-channel). This is documented in `CHILL_CALIBRATION_DEEP_DIVE.md`: the chill response is **memory-dominated**, not biphasic-distributed across the cluster. This layer asserts the composite is in the expected direction without requiring it to be the strongest signal.
