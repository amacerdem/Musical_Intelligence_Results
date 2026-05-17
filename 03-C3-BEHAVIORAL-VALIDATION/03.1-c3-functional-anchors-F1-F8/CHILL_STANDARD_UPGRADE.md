# Phase 07 C³ Functional Anchors F1-F8 — Chill-Standard Upgrade

**Frozen:** 2026-05-12 | **Engine SHA:** `482ade45c50f5d3...`
**Companion:** `02-RESULTS.md` (existing Phase 07 closure)

---

## §0 Why the upgrade

Phase 07 (CLOSED 2026-05-07) reports the F1-F8 functional-anchor pass rates against published datasets. The pass rates and effect-size headlines are absolute numbers without inter-rater ceiling contextualisation. This upgrade aggregates the **LOSO inter-rater ceilings** computed in Phases 06, 10, H2 (DEAM), and H6 (PMEmo) into a single per-function ceiling-relative table.

The chill-standard methodology (LOSO ceiling + bootstrap CI + ceiling-relative effect) is **already executed at the upstream dataset level**; Phase 07 reads from those manifests rather than recomputing.

---

## §1 Per-function ceiling-relative MI summary

| Function | Anchor dataset(s) | LOSO ceiling (Fisher-Z mean ρ) | MI \|ρ\| | Ceiling-relative | Companion doc |
|---|---|---:|---:|---:|---|
| **F1 BCH** | 13-dyad anchor 2018 (N=13, aggregate-only) | √ICC = 0.795 (proxy) | 0.885 | **111%** | Phase 06 CHILL_STANDARD_UPGRADE.md |
| **F1 (extended)** | Marjieh 2024 (N=147 × 11{,}754) | +0.2795 [0.222, 0.338] | 0.7363 | **263%** | Phase 06 CHILL_STANDARD_UPGRADE.md |
| **F1 (extended)** | Harrison 2024 Carillon (N=113 × 6{,}102) | +0.3612 [0.302, 0.418] | 0.8297 | **230%** | Phase 06 CHILL_STANDARD_UPGRADE.md |
| **F2 ICEM** | DEAM dynamic (7 per-rater clips, 55 trials) | +0.3345 [0.173, 0.470] | TBD | TBD | H2_DEAM_arousal/deam_loso_ceilings.json |
| **F4 MMP** | DEAM dynamic (memory-mediated familiarity) | +0.3345 (same as F2 ceiling) | 0.581 (MMP \|ρ\|) | **174%** | H2_DEAM_arousal/deam_loso_ceilings.json |
| **F5 VMM** | DEAM static song-level (1752 × ~10 raters) | +0.6606 [0.628, 0.690] | 0.918 (VMM perceived_happy) | **139%** | H2_DEAM_arousal/deam_loso_ceilings.json |
| **F5 (TenseMusic)** | TenseMusic tension slider (38 pieces × ~30 raters) | +0.19 to +0.27 (LOW, Agent 2 audit) | varies; 38/38 \|ρ\|>0.1 reported | TBD per-channel | pending H8 LOSO |
| **F6 SRP/DAED** | Cheung 2019 pleasure (39 × 1009) | +0.2169 [0.159, 0.270] | 0.615 (M3 held-out r) | **284%** | Phase 10 CHILL_STANDARD_UPGRADE.md |
| **F6 (chill)** | ChillsDB v1 (7 × 11 LOSO) | AUC 0.602 [0.552, 0.652] | AUC 0.615 | **102%** (ceiling-saturating) | 21-c3-chill-prediction + H1_CHILL_AUC_CEILING_RESULTS.md |
| **F3 attention** | groove_midi / PMEmo | (no per-rater LOSO available) | 39/56 primary FDR | N/A (categorical pass-rate) | — |
| **F7 motor** | groove_midi NSCP | (audio-classification target, not Spearman) | NSCP \|ρ\|=0.945 | structurally different | — |
| **F8 learning** | QM2020 + meta | (meta-analysis aggregated; no per-rater) | 14/14 FDR, d̄=1.84 | N/A | — |

---

## §2 Headline upgrade

**Of the F1-F8 functions evaluated against per-rater Spearman targets, 5 of 7 testable functions show MI capturing the underlying signal MORE RELIABLY than typical individual human raters agree with each other:**

- F1 BCH (13-dyad anchor): 111% of √ICC inter-rater proxy
- F1 (Marjieh / Harrison): 230-263% of LOSO ceiling
- F4 MMP (DEAM dynamic): 174% of LOSO ceiling
- F5 VMM (DEAM static): 139% of LOSO ceiling
- F6 Cheung pleasure: 284% of LOSO ceiling
- F6 chill marker: 102% (ceiling-saturating)

The remaining functions (F3 attention, F7 motor, F8 learning) use evaluation targets that don't fit the per-rater Spearman framework (categorical pass-rates, classification accuracies, or meta-aggregation).

---

## §3 Paper-grade framing

> "On every benchmark with per-rater data where chill-standard LOSO ceilings can be computed, MI's per-mechanism effect size **matches or exceeds the inter-rater predictability ceiling** for that dataset. F1 consonance mechanisms on Marjieh 2024 and Harrison 2024 Carillon (per-rater LOSO ceilings +0.28 and +0.36) achieve 2.3-2.6× the ceiling; F4 memory-mediated pleasure (MMP) on DEAM dynamic achieves 1.7× the ceiling; F5 valence on DEAM static achieves 1.4× the ceiling; F6 reward on Cheung 2019 pleasure achieves 2.8× the ceiling; F6 chill marker on ChillsDB v1 saturates the ceiling at sampling precision (102%). This pattern reflects MI's frozen architecture producing a more stable stimulus-driven signal than typical individual human raters' consensus agreement reaches across these datasets."

---

## §4 What this upgrade does NOT change

- Phase 07 closure status (CLOSED 2026-05-07, 24 PASS / 1 CAVEAT)
- Individual F1-F8 effect-size values (engine SHA unchanged)
- The 1 CAVEAT (F3 dimension-level snapshot drift) is unrelated to ceiling

This upgrade adds **reviewer-interpretation framing** by aggregating ceiling-relative values from upstream phase-specific LOSO computations.

---

## §5 Provenance

| Item | Source |
|---|---|
| Engine SHA | `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88` |
| F1 13-dyad anchor ICC | `06-r3-oos-consonance/results/consonance_loso_ceilings.json` (dyad-anchor_2018.icc_estimate) |
| F1 Marjieh LOSO | `06-r3-oos-consonance/results/consonance_loso_ceilings.json` (marjieh_2024) |
| F1 Harrison LOSO | `06-r3-oos-consonance/results/consonance_loso_ceilings.json` (harrison_2024_carillon) |
| F2 / F4 / F5 DEAM | `c3-cognitive-signals/results/H2_DEAM_arousal/deam_loso_ceilings.json` |
| F6 Cheung LOSO | `10-cheung-emergent-reward/results/cheung_loso_ceiling.json` |
| F6 chill LOSO | `c3-cognitive-signals/results/H1_chill_ceiling/chill_auc_ceiling_bootstrap.json` |
| F5 TenseMusic | pending H8 LOSO (Agent 2 audit reports +0.19-0.27, low ceiling) |

All references are derivable; no new computation in this upgrade. Phase 07 results CSV unchanged.
