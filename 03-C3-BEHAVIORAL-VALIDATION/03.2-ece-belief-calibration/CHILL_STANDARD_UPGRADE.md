# Phase 05 ECE Belief Calibration — Chill-Standard Upgrade (Calibration vs Agreement)

**Frozen:** 2026-05-13 | **Engine SHA:** `482ade45c50f5d3...`
**Companion:** `02-RESULTS.md` (existing Phase 05 closure)

---

## §0 Why this is partially applicable

Phase 05 reports two claims:
1. **Pooled ECE = 0.079** on 8 Core beliefs × 5 DEAM held-out songs × N=206,080 frames
2. **Cheung 2019 M3 held-out r = +0.615** (also covered by Phase 10)

These are different metrics with different ceiling implications:

| Metric | Type | LOSO ceiling applicable? |
|---|---|---|
| ECE (Expected Calibration Error) | Probability calibration | NOT directly (calibration ≠ agreement) |
| Held-out Spearman r | Per-rater Spearman target | YES (and already in Phase 10) |

---

## §1 ECE is calibration error, not inter-rater agreement

Expected Calibration Error measures how well predicted probabilities (π_pred) match observed frequencies of prediction errors:

```
ECE = Σ_k (|B_k|/N) · |accuracy(B_k) − confidence(B_k)|
```

This is **independent** of inter-rater Spearman agreement on the underlying ratings. ECE=0.079 means "MI's stated 80% confidence corresponds to 80% accuracy, on average" — a calibration property.

The 0.10 conventional threshold (Guo et al. 2017, Naeini et al. 2015) is the paper-grade reference, NOT inter-rater agreement.

## §2 What inter-rater ceiling DOES say about the underlying DEAM data

The DEAM datasets that Phase 05 uses for ECE have separate inter-rater ceilings computed in `H2_DEAM_arousal/deam_loso_ceilings.json`:

- **DEAM dynamic per-rater** (7 clips): Fisher-Z LOSO ρ = +0.3345 [0.173, 0.470]
- **DEAM static song-level** (73 raters × 1744 songs): Fisher-Z LOSO ρ = +0.6606 [0.628, 0.690]

These contextualise the **DEAM TARGET** that MI's beliefs predict but do not directly modify the ECE result.

**Implication for paper claim:** MI is well-calibrated (ECE=0.079) **against a target whose inter-rater agreement is +0.66 (static) / +0.33 (dynamic)**. The calibration claim holds at a level of probabilistic accuracy that is independent of underlying signal noise; both can coexist as separate strengths.

## §3 Cheung M3 held-out r is already ceiling-framed (Phase 10)

Phase 05's secondary claim of held-out Pearson r = +0.615 on Cheung 2019 pleasure is identical to Phase 10's ceiling analysis:

- Cheung pleasure LOSO inter-rater ceiling: +0.2169 [95% CI 0.159, 0.270]
- MI M3 held-out r / ceiling = **2.84× (≈ 284%)**

See `Science/V-Reproduction/10-cheung-emergent-reward/CHILL_STANDARD_UPGRADE.md` for the full Phase 10 framing.

## §4 No paper text change required

The paper currently reports:
- ECE = 0.079 on N=206,080 frames (paper-grade, conventional threshold)
- Cheung M3 r = +0.615 with ceiling-relative framing (added in Phase 10 upgrade)

Both framings are already in the paper. Phase 05's ECE claim does not need chill-standard ceiling reframing because ECE is a calibration metric, not an agreement metric.

## §5 Why not force a ceiling on ECE?

Two reasons:
1. **ECE measures calibration, not agreement.** Calibration is the alignment between confidence and accuracy. Agreement is the correlation between subjects on a target. These measure different things.
2. **ECE has its own well-established baseline** (0.10 conventional threshold, uniform-precision baseline at 10.8× worse Brier). Adding LOSO ρ as a denominator would be category-mixing.

## §6 What this upgrade does NOT change

- Phase 05 closure status (CLOSED 2026-05-06, 10/11 PASS + 1 CAVEAT)
- ECE = 0.079 paper claim (unchanged)
- Per-belief ECE values (unchanged)

This upgrade adds: documentation that Phase 05's TARGET DATA (DEAM, Cheung) has chill-standard LOSO ceilings computed upstream (H2, Phase 10), and these ceilings contextualise the WHAT IS BEING CALIBRATED, even though they do not modify the calibration metric itself.

---

## §7 Provenance

| Item | Source |
|---|---|
| Engine SHA | `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88` |
| DEAM LOSO ceilings | `c3-cognitive-signals/results/H2_DEAM_arousal/deam_loso_ceilings.json` |
| Cheung LOSO ceiling | `10-cheung-emergent-reward/results/cheung_loso_ceiling.json` |

No new computation; documentation only.
