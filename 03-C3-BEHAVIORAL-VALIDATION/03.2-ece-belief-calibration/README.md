# ECE Reproduction — Pooled Bayesian Belief Calibration

**Paper claim:** "Pooled expected-calibration error was ECE = 0.079, below the conventional 0.10 threshold" (paper §Bayesian beliefs are well-calibrated, S5).

**Status:** **REPLICATED** by V6 independent measurement (0.0841, deviation +0.005, ~6.5% relative).
**V-Reproduction Phase 03.2:** **CLOSED 2026-05-06**, 10/11 PASS + 1 CAVEAT (`pitch_identity` paper-flagged outlier). See `02-RESULTS-PHASE5.md` and `results/05_ece_calibration_manifest.json`.

**Last verified:** 2026-05-05 (V6 phase A2 close); refined into per-claim verdicts 2026-05-06 (Phase 5).

---

## Quick verdict

| Number | Paper (T-R3-08, 2026-04-23) | V6 (this archive, 2026-05-05) |
|---|---:|---:|
| Pooled ECE (8 beliefs × 5 songs) | 0.079 | **0.0841** |
| Pooled Brier | 0.014 | 0.014 |
| N frames pooled | 206,080 | 128,800 (30s × 5 × 8 — see Methodology §clip duration note) |
| timbral_character per-belief ECE | 0.111 | 0.111 (EXACT) |
| prediction_hierarchy per-belief ECE | 0.101 | 0.101 (EXACT) |
| information_content per-belief ECE | 0.049 | 0.048 (EXACT) |
| Brier reliability/uncertainty | n/a | 0.085 (≪ 1) |

**Bottom line:** Independent reproduction confirms the paper's calibration claim. Per-belief ECE values match to within 0.015 across all 8 paper beliefs.

V6 also tested **6 extension beliefs** (F3–F8) NOT in paper's selection: 4 of 6 (F3, F4, F5, F8) generalize calibration; F7 GrooveQuality is the only catastrophic outlier (ECE = 0.218).

---

## Files

```
ece/
├── README.md                     ← this file (verdict + quick reference)
├── 00-METHODOLOGY.md             ← exact operationalization (locked)
├── 01-PROVENANCE.md              ← who computed what, when, where
├── 02-RESULTS.md                 ← full numerical results + interpretation
├── code/
│   ├── extract_belief_traces.py  ← engine → (π_pred, PE) traces
│   ├── compute_metrics.py        ← traces → ECE, Brier, null, reliability
│   ├── plot_reliability.py       ← reliability diagram figures
│   ├── run.sh                    ← single-command reproduction
│   ├── requirements.txt          ← Python deps
│   └── README.md                 ← how to run
├── data/
│   └── README.md                 ← DEAM held-out song IDs + cache pointer
├── results/
│   ├── A2_per_cell_ece.csv       ← 70 rows: per-(song, belief) ECE+Brier
│   ├── A2_circular_null.csv      ← 70 rows: 10K-perm null per cell
│   ├── A2_summary.json           ← headline numbers + pass/fail
│   ├── A2_reliability_data.npz   ← bin-level data for figures
│   └── traces/
│       └── song_{1034,1508,1777,1896,1923}.npz  ← 14 belief traces per song
├── figures/
│   ├── reliability_per_belief.png ← 14-panel reliability diagrams
│   ├── ece_per_cell_heatmap.png   ← 5 × 14 ECE heatmap
│   └── extension_vs_paper.png     ← bar chart comparing paper-8 vs extension-6
└── paper-evidence/
    ├── original_compute_ece_brier.py     ← V2/T-R3-08 paper-time computation
    ├── original_ece_brier_analysis.py    ← V2/T-R3-08 paper-time analysis
    ├── original_ece_result.json          ← paper-time output (8 beliefs only)
    └── original_ece_brier_summary.md     ← paper-time summary report
```

---

## To reproduce

```bash
cd "/Volumes/SRC-9/SRC Musical Intelligence/Science/V-Reproduction/05-ece-belief-calibration/code"
./run.sh
```

Expected wall-clock: ~5 minutes on M2 (engine 6 × 5 songs × 30 s = 750 s of analysed audio at ~10 s/song wall + metrics ~30 s).

Expected output: `results/` populated; `figures/` populated; pooled ECE printed to stdout = 0.0841.

---

## Engine pin

Reproduction valid against MI engine HEAD `5b9aba41` (V3 anchor) or successor with documented `|Δρ| ≤ 1e-4`. Engine itself is **not** copied here; assumed at standard path `Science/Musical_Intelligence/`.

---

## Pre-registration

V6 A2 was pre-registered at `Science/V6/01-pre-registration.md` §A2 (frozen at scaffold close 2026-05-05 before any data was touched in this V branch).

Paper-time T-R3-08 pre-registration: `V2/reviewer-sims/divan-major-revision-2026-04-22/T-R3-08/` (authorised at 2026-04-22).
