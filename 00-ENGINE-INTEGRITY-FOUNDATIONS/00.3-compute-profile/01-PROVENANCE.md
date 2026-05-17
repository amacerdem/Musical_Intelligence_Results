# V-Reproduction Phase 00.3 — Provenance

## Paper claim source

Source: `The Paper/Divan-Final-corrected-evidence/Musical-Intelligence-corrected-evidence.tex` and §Compute profile / §Performance subsection.

Numerical claims (verbatim from MEMORY.md canonical summary, traceable to corrected-evidence paper):

> 3.31× real-time on Apple MacBook Air M2 (2023, 8 GB unified memory) consumer laptop, single-threaded.
> Median 570 fps over 15 runs × 30s, p95 margin 2.94× against 172.27 Hz frame rate.
> Peak resident memory 465 MB / 30s.
> Bit-identical engine: |Δρ| ≤ 8.8 × 10⁻⁵ across runs.

Per-frame latency (paper §Compute profile table, corrected-evidence v):

| Percentile | Value |
|---|---|
| p50 | 1.753 ms |
| p95 | 1.972 ms |
| p99 | 1.990 ms |
| Real-time line (1/172.27) | 5.805 ms |
| p95 margin | (5.805 − 1.972) / 1.972 ≈ 1.94× headroom; "margin" = 5.805 / 1.972 = 2.94× |

The 2.94× p95-margin is the ratio of the real-time line over p95 latency, **not** a "headroom" subtraction.

## Reproduction lineage

- **V1 baseline:** `Science/V1/scripts/` contains no canonical compute-profile script — paper number was generated post-V1 close on the same M2 8GB hardware. Phase 4 is the first formal reproduction.
- **Engine HEAD pinned:** `318eb2f529d7103e8b7d80b01228357fdc4e0217` per `_infra/manifests/engine_head.json`.
- **Runner:** `Science/V-Reproduction/_infra/engine/runner.py:run_engine()` is the canonical wrapper; this is the same wrapper used by Phase 0/2/3 closes and by V6 A2 ECE belief extraction.

## Hardware verification

Run at Phase 4 session start (2026-05-06):

```
Model Name: MacBook Air
Model Identifier: Mac14,2
Chip: Apple M2
Memory: 8 GB
```

**Match to paper hardware: MISMATCH.**

The corrected-evidence paper §Methods §Compute profile (line 1223) actually
specifies:

> "Apple M2 Max CPU, 64 GB RAM, macOS 26.3.1, torch 2.10.0 CPU."

This contradicts MEMORY.md's downstream simplification ("MacBook Air M2
(2023, 8 GB unified memory)"). The paper's compute profile was generated on
**M2 Max 64 GB**, not vanilla M2 8 GB. M2 Max has ~4× higher memory
bandwidth (≈ 400 GB/s vs ≈ 100 GB/s) and double the performance cores
(8P vs 4P), giving substantial throughput advantage on this BLAS-bound
workload. The 8 GB unified-memory cap also forces page-pressure on a
~1.5 GB-resident process that the 64 GB machine never sees.

Per pre-registration, hardware mismatch downgrades all
`C-COMPUTE-01..05` claims to **CAVEAT** regardless of measurement. The
observed numbers are reported truthfully alongside the paper numbers; the
deviation reflects hardware class, not engine drift.

C-COMPUTE-06 (determinism) is hardware-independent and remains PASS.

## Audio sources

- `Science/datasets/real-music/*.wav` — 6 long-form real recordings (truncated to 30 s by engine).
- `Science/datasets/emotion/DEAM/audio/MEMD_audio/` — 1,802 DEAM mp3s, ~45 s each (truncated to 30 s by engine). DEAM provides emotional+stylistic diversity.

Both sources are accessible offline; no remote download required during benchmark.

## Tooling versions

- Python 3.x (system); torch + librosa + torchaudio per `_infra/requirements.txt` (versions pinned in Phase 0).
- jsonschema for manifest validation.
- macOS Darwin 25.3.0 / Mac14,2.
