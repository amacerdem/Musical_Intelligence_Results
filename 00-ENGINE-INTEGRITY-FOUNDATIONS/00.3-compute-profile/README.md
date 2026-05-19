# Phase 00.3 — Compute Profile (CLOSED 2026-05-06)

**Verdict:** 1 PASS / 5 CAVEAT (hardware-class mismatch).

## What was reproduced

| Claim | Paper (M2 Max 64GB) | Reproduced (M2 8GB) | Verdict |
|---|---|---|---|
| C-COMPUTE-01 — 3.31× real-time | 3.31× | 0.467× | CAVEAT |
| C-COMPUTE-02 — 570 fps median | 570 fps | 80.47 fps | CAVEAT |
| C-COMPUTE-03 — 465 MB peak RSS | 465 MB | 1 553.81 MB | CAVEAT |
| C-COMPUTE-04 — latency p50/p95/p99 | 1.753 / 1.972 / 1.990 ms | 12.43 / 14.11 / 16.24 ms | CAVEAT |
| C-COMPUTE-05 — p95 margin 2.94× | 2.94× | 0.411× | CAVEAT |
| C-COMPUTE-06 — bit-identical engine | \|Δρ\| ≤ 8.8e-5 | MD5 match (zero drift) | **PASS** |

## Why CAVEAT, not FAIL

Hardware-class mismatch: paper specifies **Apple M2 Max + 64 GB RAM**, this
session ran on **MacBook Air M2 + 8 GB RAM**. Pre-registration locks
hardware-mismatch → CAVEAT. Determinism (C-COMPUTE-06) is hardware-
independent and reproduces exactly.

## Files

- `02-RESULTS.md` — full close report with 15-run table and per-claim verdicts.
- `01-PROVENANCE.md` — paper citations + the M2-Max-vs-M2-base finding.
- `03-PRE-REGISTRATION.md` — frozen pre-run tolerances and CAVEAT downgrade rule.
- `results/04_compute_profile_manifest.json` — schema-validated manifest.
- `figures/{fps_distribution,latency_histogram,memory_trace}.png` — visual.

## Quick re-run

```sh
cd 00-ENGINE-INTEGRITY-FOUNDATIONS/00.3-compute-profile
bash code/run.sh
python3 code/make_figures.py
```

Sequential 15 × 30 s ≈ 16 min on M2 8 GB.
