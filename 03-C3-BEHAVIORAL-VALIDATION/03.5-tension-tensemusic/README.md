# 22-h8-tensemusic-tension-prediction — Standalone Tension Tier-1 Verdict

> **Purpose:** Reproduce the paper's Tier-1 tension-prediction finding (`MECH_AAC__F1:hr_pred_2s` ceiling-saturating on TenseMusic 38 pieces × 30 raters) **from a fresh clone**, in a single command.
>
> **The single empirical claim under test:**
>
> > On the TenseMusic corpus (38 continuous-music pieces × 30 raters × 50 Hz tension-slider trajectories), the frozen MI engine's autonomic-forecast channel `MECH_AAC__F1:hr_pred_2s` achieves Fisher-Z Spearman ρ = **+0.421** against consensus tension slider (positive direction in **89.5 %** of pieces), with **15/15 channels** in the TENSION-15 pre-registered pool passing Bonferroni at α/15. The result reaches **109 %** of the leave-one-subject-out inter-rater ceiling (+0.386, 95 % CI [0.36, 0.41]) — ceiling-saturating like the chill marker.
>
> If `run_all.py` completes with ✅ verdict at L5, the paper's tension finding is independently reproduced.

---

## Quick start

After cloning the repository:

```bash
cd Science/V-Reproduction/22-h8-tensemusic-tension-prediction
python3 run_all.py
```

This runs all 6 layers in order (Pin → L1 → L2 → ... → L9) and writes a fresh `REPORT.md` with:
- Per-layer PASS / FAIL / CAVEAT scorecard
- Per-channel Fisher-Z mean rank-correlation table
- Ceiling-relative verdict
- Reconciliation against paper-time baseline

Exit code is the worst pytest exit code observed (`0` = all PASS).

**Prerequisites:**

```bash
pip install numpy scipy pandas pytest
```

Engine (`Musical_Intelligence/`) is auto-discovered via an upward walk from `conftest.py`.

**Expected wallclock on M2 8 GB:** ~3–5 min full run (LOSO ceiling computation is the longest part at ~30 s; primary test ~90 s + 5,000-iter bootstrap ~60 s).

For a sanity check before the full run:

```bash
python3 run_all.py --quick     # pin-integrity + L1 + L4 + L5 only (~2 min)
```

---

## Inputs required

When the reviewer clones the repo, they must additionally place:

1. **TenseMusic per-rater CSV files** at:
   ```
   Science/datasets/emotion/TenseMusic/data_raw/
       Ades.csv
       Bach.csv
       Bartok.csv
       Beethoven.csv
       ...
       (38 piece CSVs)
   ```

2. **TenseMusic engine cache** at:
   ```
   Science/V-Reproduction/Musical_Intelligence_Outputs/emotion/TenseMusic/per_frame/
       Ades.npz
       Bach.npz
       ...
       (38 piece engine outputs)
   ```

L2/L3 verify both exist before L5 runs.

---

## Layer overview

| Layer | Purpose | Wallclock |
|---|---|---|
| `L1_engine_pin` | Engine SHA aggregate must match `482ade45c...` | <1 s |
| `L2_data_integrity` | 38 TenseMusic CSVs + engine .npz files present | ~5 s |
| `L3_engine_cache` | Per-frame npz integrity for all 38 pieces | ~10 s |
| `L4_ceiling_check` | Reproduce LOSO inter-rater ceiling +0.386 [95 % CI 0.36, 0.41] | ~30 s |
| **`L5_primary_test`** | **PRIMARY** — TENSION-15 lag-aware Spearman + lag-sweep null + Bonferroni | ~90 s |
| `L9_verdict_reconciliation` | Compare L5 result to paper-time baseline | <1 s |

**L5 carries the primary headline verdict.** L4 ensures the ceiling estimate is reproducible.

---

## Numeric tolerance

This reproduction is engine-bit-identical up to floating-point noise (`|Δρ| ≤ 1×10⁻⁴`). For the headline:

```
|fz_mean_rho_local − fz_mean_rho_paper| ≤ 0.01  (1e-2 absolute)
direction agreement ≥ 80 % per the chill standard
n_bonferroni_pass ≥ 13 of 15 (paper-time: 15/15)
```

---

## Paper-time baseline (locked)

```
top channel:        MECH_AAC__F1:hr_pred_2s
fz_mean_rho:        +0.4207
direction_pct:      89.5 %
n_bonferroni_pass:  15/15  (TENSION-15 pool)
n_bh_fdr_pass:      15/15
ceiling_point:      +0.3857
ceiling_ci_95:      [+0.3601, +0.4120]  (trial-level bootstrap, 5000 iters)
ceiling_relative:   109.1 %  ← ceiling-saturating
```

These numbers are hard-coded in `_infra/manifests/paper_time_baseline.json` for L9 reconciliation.

---

## What this reproduction does NOT test

- **Engine correctness** — covered by `19-r3-isolated-validation` and `20-t3-isolated-validation`
- **Other cognitive-signal datasets** — those have their own segments under `c3-cognitive-signals/`
- **Cross-cultural tension** — Phase 14 (structural exception, no per-rater data)

This phase is laser-focused on **one Tier-1 finding** so a reviewer can independently confirm it.

---

## If a layer fails

- **L1 FAIL**: engine SHA mismatch → check `Musical_Intelligence/` SHA, ensure clean clone
- **L2 FAIL**: missing TenseMusic CSV or engine cache → place files at expected paths
- **L3 FAIL**: engine cache corrupt → rebuild from audio
- **L4 FAIL**: ceiling drift outside 95 % CI → numeric drift; document and investigate
- **L5 FAIL**: most concerning; investigate via L9 reconciliation dump
- **L9 FAIL**: tolerance breach → flag as CAVEAT, not FAIL

---

## Reviewer attestation pattern

When this passes for a reviewer:
```
✅ 22-h8-tensemusic-tension-prediction
  L1 PASS — engine SHA matches 482ade45c...
  L2 PASS — 38/38 TenseMusic CSVs + 38/38 engine .npz present
  L3 PASS — engine cache integrity verified
  L4 PASS — LOSO ceiling +0.386 [95 % CI 0.36, 0.41] reproduced
  L5 PASS — top channel AAC F1:hr_pred_2s ρ=+0.421, 15/15 Bonferroni
  L9 PASS — reconciliation within tolerance, 109 % of ceiling

Total wallclock: 4m12s
```

This is the contract: one command, one boolean output, full diagnostic trail.

---

## Companion documents

- Pre-registration (locked): `Science/c3-cognitive-signals/PREREGISTRATION_C3_COGNITIVE_SIGNALS.md` (H8 hypothesis, TENSION-15 pool)
- Original research code: `Science/c3-cognitive-signals/code/H8_TenseMusic_tension/`
- Paper-time results: `Science/c3-cognitive-signals/results/H8_TenseMusic_tension/`
