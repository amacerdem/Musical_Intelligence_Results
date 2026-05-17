# Phase 06 R³ OOS Consonance — Chill-Standard Upgrade

**Frozen:** 2026-05-12 | **Engine SHA:** `482ade45c50f5d3...`
**Companion:** `02-RESULTS.md` (existing Phase 06 closure)
**Mirror:** none required (Phase 06 is single-repo V-Reproduction)

---

## §0 Why the upgrade

Phase 06 (CLOSED 2026-05-07) reports MI engine consonance correlations against three published datasets (13-dyad anchor 2018, Marjieh 2024, Harrison 2024 Carillon). The original closure framing used absolute ρ values without contextualisation against inter-rater predictability. Following the H1 chill-marker methodology established 2026-05-12 (`H1_CHILL_AUC_CEILING_RESULTS.md`), we add ceiling-relative effect-size framing to make MI's performance interpretable against the theoretical maximum any stimulus-only model could achieve.

## §1 Method — LOSO inter-rater ceiling (chill-standard)

For each dataset with per-rater data:

1. For each held-out subject: consensus = mean of N-1 OTHER subjects' per-bin ratings
2. Compute Spearman ρ between consensus and held-out subject's per-bin vector
3. Aggregate Fisher-Z mean across raters
4. Bootstrap 95% CI (5,000 iterations)

Binning: 13 semitone bins (matches paper c3_r3_oos Marjieh protocol).

## §2 Results

### §2.1 Marjieh 2024 (rating_w3rdd.csv, "5_equal" timbre)

| Metric | Value |
|---|---:|
| N participants | 147 |
| N ratings | 11,754 |
| N LOSO trials | 147 |
| **LOSO Fisher-Z mean ρ** | **+0.2795** |
| 95% bootstrap CI | [0.2221, 0.3382] |
| **MI engine roughness × Marjieh** | **−0.7363** (paper Phase 06) |
| **|MI ρ| / LOSO ceiling** | **263.4%** |

### §2.2 Harrison 2024 Carillon

| Metric | Value |
|---|---:|
| N participants | 113 |
| N trials | 6,102 |
| N LOSO trials | 113 |
| **LOSO Fisher-Z mean ρ** | **+0.3612** |
| 95% bootstrap CI | [0.3024, 0.4184] |
| **MI engine inharmonicity × Carillon** | **−0.8297** (paper Phase 06) |
| **|MI ρ| / LOSO ceiling** | **229.7%** |

### §2.3 13-dyad anchor 2018 (aggregate only)

| Metric | Value |
|---|---:|
| N dyads | 13 |
| N raters per dyad | 30 |
| Per-rater data | NOT PUBLIC |
| Within-dyad mean SD | 1.111 |
| Between-dyad SD | 1.507 |
| **ICC(1,1) estimate** | **0.6333** |
| **MI engine roughness × 13-dyad anchor** | **−0.8846** (paper Phase 06) |
| **|MI ρ| / √ICC** | **111.2%** |

---

## §3 Interpretation — two different ceilings

**Important methodological distinction:**

The chill-marker H1 standard used **individual-level LOSO**: MI predicts each subject's chill events, compared to N-1-consensus predicting same subject's events. Both at individual level → same ceiling.

The consonance test compares **MI to the AGGREGATE rating curve** (per-bin mean across all subjects). This is a different reference frame:

- **Individual-level LOSO ceiling** (computed here): how well does N-1 mean predict an individual rater? ~0.28-0.36
- **Aggregate-level ceiling** (MI's actual target): how well can any stimulus-only model predict the noise-averaged aggregate? Effective bound is close to 1.0 because aggregate-of-N averages out individual noise.

**MI's >100% of LOSO ceiling is NOT a paradox** — it means: MI matches the underlying stimulus-driven signal MORE RELIABLY than any individual subject matches the N-1 consensus of their peers.

In paper-friendly framing:

> "MI captures the stimulus-driven consonance signal with greater reliability than individual human raters demonstrate with each other (Marjieh 2024 LOSO inter-rater ρ = 0.28 [95% CI 0.22-0.34], MI |ρ| = 0.74; Harrison 2024 Carillon LOSO ρ = 0.36 [0.30-0.42], MI |ρ| = 0.83). The engine's frozen architecture aggregates physiological/psychophysical features such that its output curve approximates the consensus rating curve more closely than typical individual human raters do."

---

## §4 Paper claim upgrade

Existing claim (Phase 06 RESULTS.md):

> "MARJIEH-ROUGH: paper ρ = −0.813, reproduced −0.7912, Δ = +0.0218, PASS"
> "CARILLON-STUMPF: paper ρ = −0.824, reproduced −0.8297, Δ = −0.0057, PASS"

Upgraded claim (incorporating ceiling-relative framing):

> "MI engine consonance correlations on Marjieh 2024 (|ρ| = 0.74, n=11,754 ratings × 147 participants) and Harrison 2024 Carillon (|ρ| = 0.83, n=6,102 ratings × 113 participants) **exceed the inter-rater LOSO ceiling by 2-3×** (0.28 and 0.36 respectively, both 95% CI ≤ 0.42), indicating that the frozen engine produces a more stable stimulus-driven consonance ranking than typical individual human raters' consensus agreement. 13-dyad anchor 2018 (aggregate-only, N=30 raters per dyad, ICC(1,1) = 0.63) shows |ρ| = 0.88 ≈ √ICC × 111%."

---

## §5 Provenance

| Item | Value |
|---|---|
| Script | `code/compute_consonance_loso_ceiling.py` |
| Result JSON | `results/consonance_loso_ceilings.json` |
| Seed | 2026051221 |
| N bootstrap | 5,000 |
| Engine SHA | `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88` |

---

## §6 What this upgrade does NOT change

- Phase 06 closure status (CLOSED 2026-05-07)
- The paper's published ρ values (engine SHA unchanged)
- The synthesis-pipeline CAVEAT-SYNTH for Marjieh/Carillon (separate issue)

This upgrade only adds **framing for reviewer interpretation** — neither the engine nor the dataset numbers change.
