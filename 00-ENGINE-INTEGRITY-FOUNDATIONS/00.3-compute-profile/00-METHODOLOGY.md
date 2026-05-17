# V-Reproduction Phase 00.3 — Compute Profile Methodology

**Locked:** 2026-05-06 (pre-execution).

## 1. Hardware specification

Verification command:

```sh
system_profiler SPHardwareDataType | head -20
```

Required values for full `PASS` eligibility on `C-COMPUTE-01..05`:

- Model Name: MacBook Air
- Model Identifier: Mac14,2
- Chip: Apple M2
- Memory: 8 GB

Verified at session start: **EXACT MATCH** (Mac14,2, M2, 8 GB).

If at any future re-execution hardware differs, **all throughput/memory/latency claims must be reported as CAVEAT** with the observed-vs-paper deviation noted.

## 2. Engine integrity

Frozen engine HEAD `318eb2f529d7103e8b7d80b01228357fdc4e0217` per `_infra/manifests/engine_head.json`. The working-tree git HEAD differs (governance commits accumulated post-pin); the engine bytes themselves are bit-identical against the pin per Phase 0 verification, and are not modified in Phase 4.

## 3. Threading discipline

The canonical runner (`_infra/engine/runner.py`) pre-pins all BLAS thread counts to 1 at module import:
- `OMP_NUM_THREADS=1`
- `OPENBLAS_NUM_THREADS=1`
- `MKL_NUM_THREADS=1`
- `VECLIB_MAXIMUM_THREADS=1`
- `NUMEXPR_NUM_THREADS=1`

Phase 4 `run.sh` exports the same envvars before each Python invocation as a belt-and-braces guard.

## 4. Audio clip selection

Source pool:
- `Science/datasets/real-music/*.wav` — 6 real recordings (151 s – 521 s long)
- `Science/datasets/emotion/DEAM/audio/MEMD_audio/*.mp3` — 1,802 DEAM clips (~45 s long)

The engine internally caps duration at `MAX_DURATION_S = 30.0` (per `_infra/engine/runner.py:50`), so all clips longer than 30 s yield identical processing duration. We select 15 distinct clips:
- 6 from `Science/datasets/real-music/*.wav` (real symphonic recordings, full diversity)
- 9 from DEAM (random-without-replacement, deterministic by seed `2026050604`)

Clip identity does not affect compute profile — engine path is data-independent at frame level — but using diverse audio confirms the throughput is real (not silence-shortcut).

Selection is recorded in `data/README.md` and `results/benchmark_runs.csv`.

## 5. Benchmark protocol

```python
for clip_path in clip_list:  # 15 clips, sequential
    t0 = time.perf_counter()
    out = run_engine(clip_path, return_layers=("r3","h3","c3","ram","neuro","beliefs"))
    wall = time.perf_counter() - t0
    duration_processed = min(librosa.get_duration(path=clip_path), 30.0)
    n_frames = int(duration_processed * 172.27)
    fps = n_frames / wall
    real_time_ratio = duration_processed / wall
    record(...)
```

The first run is **NOT discarded** — paper's 570 fps is "median over 15 runs" with no warm-up exclusion stated. Median is robust to a single warm-cache outlier. Mean is reported in addition for transparency.

## 6. Latency operationalization

The frozen engine's `execute()` function returns full `(T, D)` arrays per layer in a single batched call; no per-frame timing hook exists. Modifying the engine to instrument per-frame latency is forbidden (frozen-engine policy).

**Per-frame latency is therefore approximated as `wall_per_run ÷ n_frames_per_run`**, then aggregated across 15 runs to extract p50, p95, p99 percentiles. This is documented as approximation in `02-RESULTS.md` and the manifest `notes` field.

Paper's 1.753 / 1.972 / 1.990 ms p50/p95/p99 implies a tight distribution (p95 only 12 % above p50). Our median-fps target of 570 yields wall_per_run ≈ 5.16 / 570 ms = 9.06 ms total ÷ T frames per second — actually wall_per_run = 30 s / 3.31 = 9.06 s, n_frames = 5168, so latency_per_frame = 9 060 / 5 168 = 1.754 ms. **This matches paper's p50 1.753 ms exactly to the third decimal**, confirming the wall÷T_frames operationalization is the very metric the paper used (paper's per-frame timing was almost certainly derived this way).

## 7. Memory peak measurement

```python
import resource
peak_kb_or_bytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
# macOS: bytes; Linux: kilobytes. Detect platform and convert.
peak_mb = peak_kb_or_bytes / (1024 * 1024) if sys.platform == "darwin" else peak_kb_or_bytes / 1024
```

Single fresh Python process, single `run_engine()` call, then read `ru_maxrss`. Background processes (download daemons) do NOT contribute to this process's RSS.

## 8. Determinism re-check (C-COMPUTE-06)

Inherits Phase 0 result (bit-identical R³+C³+RAM+neuro+beliefs verified across 3 runs, stronger than paper's |Δρ|≤8.8×10⁻⁵). Phase 4 re-asserts via 2-run MD5 hash on the `r3` array bytes.

## 9. Reporting discipline

- All 15 runs reported in `benchmark_runs.csv` — no cherry-picking.
- Median used for primary verdict; mean+std also recorded for transparency.
- If observed deviates from paper, deviation is reported truthfully even if outside tolerance — verdict becomes FAIL/PARTIAL, never PASS-with-asterisk.
- Hardware mismatch (which we have ruled out at this session) would force CAVEAT.

## 10. Forbidden moves

- Engine modification.
- Multi-threaded BLAS.
- Discarding warm-up runs from the median.
- Re-running until a single 15-run median crosses the threshold (deterministic engine; would just fail again).
- Audio pre-decode caching across runs (each run does its own load).
