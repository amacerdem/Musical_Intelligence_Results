# Phase 05.4 — Cross-Subject Voxelwise ds003720 — Methodology

**Axis ID:** AXIS-9
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

## EXPLICIT FRAMING (mandatory, repeated in every output)

> ds003720 (N=4 QC-pass) is a **routing-ablation test under stimulus-locking
> constraints**, NOT a population-level neural effect estimate. The architectural
> question: "Does MI's full routed representation outperform routing-ablated
> MI-naive AND random controls on an independent stimulus-locked fMRI dataset?"
> — a 4-encoder × 4-subject within-subject contrast (16 cells). The
> population-oriented neural evidence is Phase 05.2 (ds002725 mech×region,
> alignment-qualified N=17) and Phase 05.7 (independent fMRI replication).

## 1. Scope (11 paper claims)

- 4 subjects QC-pass (1 of 5 spatial-warp excluded)
- Shuffle-null contrast: MI 4/4 vs MI-naive 1/4 vs Random-26 0/4 vs Random-768 0/4
- Ridge held-out r per encoder (Fisher-z mean across 4 subjects):
  - MI = 0.165, MI-naive = 0.084, Random-26 = 0.090
  - MERT-768 = 0.221, CLAP-512 = 0.138, Random-768 = 0.121
- MI vs MI-naive lift = +93% (matched-dim architectural effect)
- Banded-ridge variance partitioning: MI-unique R² > 0 in 4/4 subjects (V6 A3)
- Feature-level CKA(MI-full, MI-naive) = 0.994 (geometric routing similarity)

## 2. Paper anchor

- `Science/Bold-fMRI/ds003720/06_encoding/C17_deney_1_shuffle_null_results.csv`
- `Science/Bold-fMRI/ds003720/06_encoding/C17_deney_2_ridge_loso.csv`
- `Science/V6/results/A3_per_subject.csv` + `A3_summary.json` (banded-ridge)
- V2 tex: `reviewer-sims/.../main-v9.5.7-cycle-17-ds003720.tex` (paper claim source)

## 3. Verification approach

Read preserved Cycle 17 + V6 A3 outputs, compute Fisher-z mean across 4 subjects
per encoder, count shuffle-null pass per encoder × 4, count MI-unique CI-excludes-0
across 4 subjects. No engine re-execution required.

## 4. Honest reporting

MERT-768 wins absolute r at 30× MI's dim. **Reported clearly, not buried.** The
paper's claim is NOT "MI beats MERT" — it is "matched-dim glass-box matches
learned features at the routing level." V-Reproduction repeats this distinction
explicitly.
