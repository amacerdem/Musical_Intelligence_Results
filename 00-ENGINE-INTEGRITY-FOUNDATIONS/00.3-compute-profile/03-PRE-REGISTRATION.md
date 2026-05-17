# V-Reproduction Phase 00.3 — Pre-Registration (frozen pre-run)

**Frozen:** 2026-05-06, before any benchmark execution.
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`.
**Hardware:** MacBook Air M2 (2023, Mac14,2, 8 GB) — verified.

| Claim | Paper value | Tolerance | Operationalization | Verdict rule |
|---|---|---|---|---|
| C-COMPUTE-01 | 3.31× real-time | relative ≤ 0.15 | median(real_time_ratio) over 15×30s runs | abs(repro − 3.31) / 3.31 ≤ 0.15 |
| C-COMPUTE-02 | 570 fps | relative ≤ 0.15 | median(fps) over 15×30s runs | abs(repro − 570) / 570 ≤ 0.15 |
| C-COMPUTE-03 | 465 MB peak RSS | relative ≤ 0.20 | `resource.getrusage(RUSAGE_SELF).ru_maxrss` after fresh single run | abs(repro − 465) / 465 ≤ 0.20 |
| C-COMPUTE-04 | p50 1.753, p95 1.972, p99 1.990 ms | relative ≤ 0.15 | wall_per_run / n_frames_per_run percentiles over 15 runs | each percentile within ±15% relative |
| C-COMPUTE-05 | p95 margin 2.94× | relative ≤ 0.15 | 5.805 ms / p95_ms | abs(repro − 2.94) / 2.94 ≤ 0.15 |
| C-COMPUTE-06 | bit-identical engine | exact | 2-run MD5 hash on r3 layer | MD5 equal across two `run_engine` calls on same audio |

## Audio clip list (frozen pre-run)

15 clips, deterministic by seed `2026050604`:

1-6. `Science/datasets/real-music/*.wav` — all 6 real recordings, in directory-listing order.
7-15. DEAM `MEMD_audio/*.mp3` — 9 clips selected via `random.Random(2026050604).sample(sorted(listdir), 9)`.

Exact clip list materialized in `data/README.md` after benchmark runs.

## What constitutes PASS / FAIL / PARTIAL / CAVEAT

- **PASS:** within tolerance, hardware match.
- **PARTIAL:** within 1.5× tolerance, hardware match.
- **FAIL:** outside 1.5× tolerance.
- **CAVEAT:** hardware mismatch OR known measurement caveat (e.g. wall÷T approximation for C-COMPUTE-04 — this is documented and accepted but flagged).

Per Phase 4 plan, hardware was verified MATCH at session start, so CAVEAT downgrade does not apply.

## Iteration policy

Up to 5 iterations per claim. If a claim fails:
1. First check engine HEAD vs pin.
2. Then check thread pinning (env vars set).
3. Then check audio loading (correct file format, no fallback path).
4. Then check background CPU contention (no parallel heavy compute).
5. If all pass and claim still fails, declare honest FAIL/PARTIAL.

No engine modification permitted under any circumstances.
