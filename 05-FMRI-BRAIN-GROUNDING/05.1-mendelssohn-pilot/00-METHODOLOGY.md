# Phase 05.1 — Mendelssohn Single-Subject Pilot — Methodology

**Axis ID:** AXIS-7
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
**Strategy:** CAVEAT-PRESERVING — paper itself flags as illustrative.

## 1. Scope (6 paper claims)

- sub-08 ds002725 paper-time TR 556 amygdala r=+0.59 (single window, illustrative)
- Spearman ρ=+0.29 (Method B peak-HRF rank statistic)
- Cross-subject N=17 median amygdala ρ=−0.022 (window-selection effect disclosure)
- 95% BCa CI [−0.154, +0.027]
- Window-shopping any-subject median post-hoc r ≈ +0.59
- Mendelssohn rank 1/7 across 4 alignment methods (2.2× next-best)

## 2. Paper anchor

V2 GT-0016 + fig1_reinforcement preserved analyses:
- `Science/V2/results/GT-0016-cross-subject/cross_subject_summary.json` — N=17 aggregates
- `Science/V2/results/GT-0016-cross-subject/cross_subject_headtohead.csv` — per-subject r/ρ
- `Science/V2/results/GT-0016-cross-subject/supplementary_posthoc_max_r.csv` — window-shopped max
- `Science/V2/results/fig1_reinforcement/sub08_mendelssohn_smoke.csv` — sub-08 paper-time TR 556 Method A vs B
- `Science/V2/reviewer-sims/.../v9.5.6-ds002725-deneyler-rescore.md` — Mendelssohn rank 1/7 + 2.2× lift documentation

## 3. Honest framing (preserved from paper)

Paper §Methods §fMRI explicitly reports BOTH Method A and Method B; Figure 1a
panel uses Method B's rank statistic; paper §Limitations §Single-subject pilot
discloses window-selection effect with cross-subject median ρ=−0.022.

V-Reproduction does NOT promote the illustrative +0.59 to population-level. Both
illustrative and population-level numbers reported side-by-side.

## 4. Forbidden moves

- Promoting CAVEAT to PASS by claiming sub-08's +0.59 is population-level evidence.
- Suppressing the cross-subject median −0.022 disclosure.
- Cherry-picking which alignment method gives the strongest result.
