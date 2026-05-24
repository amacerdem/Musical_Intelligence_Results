# R³ Isolated Validation — Paper-Grade Test Battery

> **Scope lock — read before adding any test:**
> This folder validates R³ as a **sealed module**. No downstream layer (H³, C³, RAM, neurochemistry) is involved. No cognitive label (pleasantness, consonance rating, listener data) is involved. The only question we answer here is:
>
> **"Does R³ extract the features it claims to extract, correctly, deterministically, and within its declared boundary — across every stimulus type and every operating axis a sealed front-end can be tested on?"**
>
> The paper's strength comes from R³'s function inside MI. That role demands an isolated validation that is **as strong as the role itself is load-bearing**. Six test categories cannot defend that. The thirteen layers below can.

> **V-Reproduction note:** this copy under `01-R3-PERCEPTUAL-FRONT-END/01.1-r3-isolated-extended/` is **decoupled from the paper tree** — it carries no `.tex` dependency. The doc-consistency audit (L14) exists only in the canonical source suite at `The Paper/R3-Paper/R3_Isolated_Validation/`. Engine, spec, code consistency are all still verified here; only "paper text ↔ code" cross-checks were intentionally omitted.

---

## Quick start (fresh-clone reproduction)

After cloning the `SRC Musical Intelligence` repository:

```bash
cd 01-R3-PERCEPTUAL-FRONT-END/01.1-r3-isolated-extended
python3 run_all.py
```

This runs all 13 layers (`Pin → L1 … L13`) and writes a fresh `REPORT.md` with the per-layer scorecard. Exit code is the worst pytest exit code observed (`0` = all PASS).

**Prerequisites** (no in-tree install, no vendored wheels):

```bash
pip install torch torchaudio numpy scipy soundfile pytest
```

**Two reproduction modes:**

- **Reviewer cache mode (default — no engine source, no raw WAVs needed):** conftest auto-detects the oracle cache at `engine_outputs/_unit_test_oracles/r3_isolated.pkl` (audio/mel → R3Output) plus the facts manifest at `r3_engine_facts.pkl` (constants, class metadata, source-scan results) and installs `Musical_Intelligence.*` stub modules in `sys.modules` so the test-level `from Musical_Intelligence... import …` statements resolve. Wallclock ≈ **7 s** for the full 531-test battery; headline ✅ **531/531 PASS**.

- **Live engine BUILD mode (rebuilds the cache):** clone the engine source alongside (`Musical_Intelligence/` sibling) and run `MI_BUILD_ORACLE=1 python3 -m pytest .` — the conftest wraps the live `R3Extractor` so every test call records its `(audio_hash → R3Output)` pair into the oracle, plus captures static facts (constants, source-scan results, warmup-confidence, _dag structure). Wallclock ≈ **85 s** for 531 tests on M2 8 GB. All stimuli are generated deterministically in memory; no external WAV files needed in either mode.

For a sanity check before the full run:

```bash
python3 run_all.py --quick     # pin-integrity + L1 only (~6 s)
```

---

## What R³ promises (functional contract)

| # | Contract clause | Layer that tests it |
|---|---|---|
| 1 | Raw audio in → 97-D vector out per frame at 172.27 Hz | L1, L4 |
| 2 | Engine output = documented formula, no hidden math | L1, L10 |
| 3 | Frame locality (rule 1): no t±2 escape | L2 |
| 4 | No listener model (rule 2) | L2, L11 |
| 5 | No cross-domain binding (rule 3) | L2 |
| 6 | No prediction (rule 4) | L2 |
| 7 | Deterministic (rule 5) | L3 |
| 8 | 71/97 strictly frame-local, 26/97 with declared warm-up tiers | L8 |
| 9 | 2-stage acyclic DAG | L7 |
| 10 | Each group extracts the physical quantity its name claims | L6 |
| 11 | Output range [0,1], no NaN/Inf | L4 |
| 12 | Well-defined on all valid 44.1 kHz mono inputs | L5 |
| 13 | Zero calibration, every constant literature-grounded or engine-internal-derived | L9 |
| 14 | Frozen API & dataclass | L12 |
| 15 | 3.31× real-time on M2 8GB | L13 |
| 16 | No filename / time / global-state / cache dependence | L11 |

---

## Thirteen-layer test battery

### L1 — Specification compliance (per-dimension formula re-implementation)

**Paper claim being defended:** *"Every one of the 97 dimensions equals its documented formula bit-identically."*

For each of the 97 dimensions, re-implement the documented formula in pure numpy/scipy from the engine spec and compare bit-identically to the engine output across **eight stimulus families**:

1. White Gaussian noise (seeded)
2. Pure tone at A4 (440 Hz)
3. Pure tone sweep across {100, 220, 440, 880, 1760, 3520} Hz
4. Real audio (3 clips: solo piano, polyphonic ensemble, percussion)
5. Silence (zeros, full duration)
6. DC offset (constant 0.5)
7. Dirac impulse
8. Composite (white noise + tone)

Target: **97 dims × 8 stimuli = 776 sub-tests, max-abs-diff = 0** (or documented float-tolerance for transcendentals like log/sinh).

Reports: `L1_spec_compliance/d{idx:02d}_{name}.md` per dim, plus `L1_summary.md` (97 × 8 grid).

### L2 — Boundary doctrine probes (the 5 inclusion rules quantified)

**Paper claim being defended:** *"R³ provably obeys all five ontological inclusion rules."*

- **L2.1 Frame locality (Rule 1).** For each of 71 frame-local dims, perturb samples at frame `t+k` for `k ∈ {3, 5, 10, 50, 100}` and verify output at frame `t` bit-identical. **71 dims × 5 perturbations = 355 sub-tests.**
- **L2.2 No-listener-model (Rule 2).** Sweep every engine config knob and listener-identity proxy (sample rate downstream, "user" object, env vars); verify no output change. Engine has no listener-identity hook by design — test confirms.
- **L2.3 Group isolation / no cross-domain binding (Rule 3).** For each ordered pair of groups (G_a, G_b), perturb only frequency bands relevant to G_b and verify G_a output changes only via documented physics, not via cross-domain product. **9 × 8 = 72 group-pair sub-tests.**
- **L2.4 No prediction (Rule 4).** Truncate clip at frames `T ∈ {344, 600, 1000, 2000, 5000}`; verify output at every frame `t < T` bit-identical to the same frame in the full untruncated clip. **5 truncations × N frames = thousands of sub-tests.**
- **L2.5 Deterministic (Rule 5).** Tested in L3 with full instrumentation.

Reports: `L2_boundary_doctrine/L2_{1..5}_*.md` plus `L2_summary.md`.

### L3 — Determinism & reproducibility (cross-axis bit-identicality)

**Paper claim being defended:** *"max-abs-diff = 0 on the full (B, T, 97) output across run, seed, thread permutation, hardware, OS, and torch-version axes."*

- L3.1 — 1,000 independent runs, same input, same process: max-abs-diff = 0
- L3.2 — Cross-process determinism (fresh interpreter): max-abs-diff = 0
- L3.3 — Cross-seed determinism (R³ has no PRNG; verify): max-abs-diff = 0
- L3.4 — Cross-thread-permutation (1, 2, 4, 8 worker threads): max-abs-diff = 0
- L3.5 — Cross-machine-reboot: max-abs-diff = 0
- L3.6 — Cross-OS (macOS vs Linux): max-abs-diff = 0 (or documented float-tolerance)
- L3.7 — Cross-torch-version (within compatible range): max-abs-diff = 0
- L3.8 — Cross-hardware (M1, M2, x86) where accessible
- L3.9 — Float32 vs float64 sensitivity probe (engine pin = float32; document drift)

Reports: `L3_determinism/L3_{1..9}_*.md` plus `L3_summary.md` with provenance hashes per run.

### L4 — Output guarantees (range, shape, no-NaN, dataclass)

**Paper claim being defended:** *"R³Output is a frozen dataclass; features are (B, T, 97) ∈ [0,1] with no NaN / Inf on any valid input."*

- L4.1 — Shape: `(B, T, 97)` for B ∈ {1, 2, 8}, T spanning 1 frame to 30s
- L4.2 — Range: every of 97 dims in [0, 1] across **10,000 random valid clips**
- L4.3 — No-NaN / no-Inf across the same 10,000 clips
- L4.4 — Frozen dataclass: assignment to `R3Output.features` raises
- L4.5 — feature_map immutable: registry snapshot cannot be mutated
- L4.6 — feature_names tuple has exactly 97 entries, group boundaries match docs

Reports: `L4_output_guarantees/L4_{1..6}_*.md` plus `L4_summary.md`.

### L5 — Pathological input robustness

**Paper claim being defended:** *"R³ is well-defined on every valid 44.1 kHz mono input, including edge cases."*

Each of the following is fed through the engine; the test verifies no crash, no NaN, no Inf, output in [0, 1], and (where the answer is analytically known) output matches the analytical answer:

- L5.1 Silence (full duration zeros): every dim deterministic; specific dims (RMS, energy) = 0; chroma uniform; consonance well-defined
- L5.2 DC offset (constant non-zero)
- L5.3 Dirac impulse
- L5.4 Pure tones across the audible band: 50, 100, 220, 440, 880, 1k, 2k, 4k, 8k, 16k, Nyquist
- L5.5 White / pink / brown noise
- L5.6 Saturated / clipped audio (peak amplitude beyond [-1, 1])
- L5.7 Very low amplitude (-60 dB)
- L5.8 Phase-inverted audio (output should be invariant for spectral features)
- L5.9 Very short clips: 1 frame, 5 frames, 100 frames, < warm-up window
- L5.10 Clip exactly at warm-up boundary (frame 343, 344, 345; frame 687, 688, 689)
- L5.11 Clip exceeding 30 s cap: truncation behavior matches documented `MAX_DURATION_S`
- L5.12 Stereo input → mono coerce; multi-channel rejection or coerce
- L5.13 Sample rate mismatch (48 kHz, 22.05 kHz): documented resample behavior
- L5.14 NaN / Inf in input samples: documented error or coerce behavior

Reports: `L5_robustness/L5_{1..14}_*.md` plus `L5_summary.md`.

### L6 — Group-internal physical correctness

**Paper claim being defended:** *"Each named group extracts the physical quantity its name claims, on stimuli where the answer is analytically or by-construction known."*

These are **not cognitive tests** — they verify that the formula extracts the physical quantity it advertises, on stimuli engineered so that the answer is independently known.

- **Group A (Consonance, 7-D)** — pairwise dyads at known intervals: roughness peak at Δf/CB ≈ 0.25 (Plomp-Levelt prediction), Sethares output for harmonic dyad matches Sethares 1993 paper Table 2 entries
- **Group B (Energy, 5-D)** — RMS on known clip = analytical RMS; loudness on calibrated -20 dBFS = expected
- **Group C (Timbre, 9-D)** — spectral centroid on flat noise = mid-band; centroid on bright tone > centroid on dark tone; flatness on white noise → 1; flatness on pure tone → 0
- **Group D (Change, 4-D)** — spectral flux on identical-frame stream = 0; onset strength on click track peaks at click times
- **Group F (Pitch & Chroma, 16-D)** — pure tone at A4 → chroma[9] (A) peaks; pure tone at C4 → chroma[0] peaks; equal-tempered triad → 3-bin chroma; PCCR rotation invariance verified analytically
- **Group G (Rhythm & Groove, 10-D)** — metronome at 120 BPM → tempo dim peaks near 120/60 normalised; isochronous click → low syncopation; offbeat emphasis → high syncopation
- **Group H (Harmony & Tonality, 12-D)** — C-major scale → C-major key template scores higher than C-minor; modulation from C to G → key shift detected
- **Group J (Timbre Extended, 20-D)** — spectral contrast bands match Jiang 2002 partition; MFCC reconstruction matches DCT-II of log-mel
- **Group K (Modulation, 14-D)** — AM-modulated tone at f_m = 8 Hz → modulation-rate dim peaks at 8 Hz; sharpness of bright tone > sharpness of dark tone (DIN 45692); A-weighted level matches IEC 61672-1 reference

Each subtest reports the analytical expected value, the engine output, and the deviation. Target: **all groups pass on at least one analytical anchor per dim**.

Reports: `L6_group_internal/L6_{A,B,C,D,F,G,H,J,K}_*.md` plus `L6_summary.md`.

### L7 — DAG & staging correctness

**Paper claim being defended:** *"R³ is a 2-stage acyclic DAG; Stage 1 is parallel-ready; Stage 2 declares its dependencies via `compute_with_deps`."*

- L7.1 — Topological-order audit: build graph from `compute_with_deps` declarations; verify DAG (no cycles).
- L7.2 — Stage barrier: instrument execution; verify no Stage-2 group starts before all Stage-1 groups complete.
- L7.3 — Dependency narrowness: G reads only `energy[11]` (`onset_strength`); H reads only `pitch_chroma[25:36]`; verify by zeroing other Stage-1 outputs and confirming G/H output unchanged.
- L7.4 — Stage 1 parallelism: 7 Stage-1 groups produce identical output under serial vs parallel execution (max-abs-diff = 0).
- L7.5 — No Stage-2 → Stage-1 leakage: Stage-2 outputs never feed back to Stage-1.

Reports: `L7_dag_staging/L7_{1..5}_*.md` plus `L7_summary.md`.

### L8 — Warm-up tier disclosure

**Paper claim being defended:** *"71/97 dims are frame-local; 26/97 carry hidden temporal state under disclosed warm-up tiers (Tier 0, Tier 1 ramp, Tier 1 zero, Tier 2 zero)."*

- L8.1 — Tier 0 (79 dims): output well-defined and confidence = 1 from frame 0.
- L8.2 — Tier 1 ramp (9 dims): confidence ramps 0 → 1 over exactly 344 frames, linear shape verified.
- L8.3 — Tier 1 zero (8 dims): output = 0 until frame 344, then engages.
- L8.4 — Tier 2 zero (1 dim): output = 0 until frame 688, then engages.
- L8.5 — `WarmupManager` registry equals the 26-dim set declared in spec (set equality test).
- L8.6 — Each stateful dim's tier matches its inline documentation (per-file audit).

Reports: `L8_warmup/L8_{1..6}_*.md` plus `L8_summary.md`.

### L9 — Constant provenance audit (zero-calibration claim)

**Paper claim being defended:** *"Every numeric constant in `ear/r3/` is either (i) a literature value from a named publication or (ii) an engine-internal scaling fixed at definition time. No constant is adjusted against human-rated data."*

- L9.1 — AST walk of `ear/r3/{groups,pipeline,registry,constants}/*.py`: enumerate every module-level numeric constant. Target: ≥ 58 constants.
- L9.2 — Literature constants (≥ 9): each verified to its named publication at source resolution. Includes all 7 Sethares 1993 dyad-consonance fit coefficients, 12-element Krumhansl & Kessler 1982 major and minor profiles, Plomp-Levelt critical-band formula coefficients, Stumpf 1890 fusion k-tier weights, Harte 2010 Tonnetz angles, Davis & Mermelstein 1980 MFCC DCT-II, Jiang 2002 spectral contrast band partition, Zwicker & Fastl 2007 critical-band formula, DIN 45692 sharpness curve, IEC 61672-1 A-weighting, Hammarberg 1980 voice bands, Stevens 1957 power-law exponent, Wiener 1930 entropy.
- L9.3 — Engine-internal derivations: each constant matches its inline derivation comment (e.g. `_FRAME_RATE = 172.27 = 44100/256`, `_RATIO_SIGMA = 0.0383 = 2^(65/1200) − 1`).
- L9.4 — Algebraic constants: 4 derived constants computed from base values match their declared expressions.
- L9.5 — Structural constants: 21 slice tuples, group boundaries, domain maps verified against the 97-D layout.
- L9.6 — **Negative-claim audit:** no commit in `ear/r3/` history contains a constant change correlated with a downstream cognitive-rating dataset rerun. Auditable git-log scan against a forbidden-corpus regex pattern (full pattern preserved in `L9_constants/test_l9_constants.py` as the protective enforcement; not narrated here).

Reports: `L9_constants/L9_{1..6}_*.md` plus `L9_summary.md` with full provenance table.

### L10 — Cross-implementation cross-validation

**Paper claim being defended:** *"The engine's formula is correct against independent re-implementations, not just against itself."*

For each load-bearing formula, build an **independent** re-implementation and verify the engine output matches:

- L10.1 — Sethares 1993 dissonance kernel: pure-Python re-impl from 1993 paper Equations 1–3, verify match across 50 dyads.
- L10.2 — Plomp-Levelt critical bandwidth: pure-Python re-impl from 1965 paper Equation 4.
- L10.3 — Stumpf 1890 fusion criterion: pure-Python re-impl from text source.
- L10.4 — Krumhansl-Kessler 1982 key profiles: vector match against published Table 2.4 / 2.5.
- L10.5 — Harte 2010 Tonnetz: 6 angles match published reference.
- L10.6 — MFCC DCT-II: numpy re-impl matches engine output bit-identically.
- L10.7 — Jiang 2002 spectral contrast: band partition matches paper Table 1.
- L10.8 — Plomp-Levelt CB formula in scipy: independent route.
- L10.9 — A-weighting filter: scipy.signal.freqz-based independent computation.

Each line contributes a "two independent computations agree" certificate.

Reports: `L10_cross_impl/L10_{1..9}_*.md` plus `L10_summary.md`.

### L11 — Negative / anti-feature tests (no hidden state, no leakage)

**Paper claim being defended:** *"R³ has no hidden state, cache, global, time-, filename-, or environment-dependence beyond declared inputs."*

- L11.1 — No filename dependence: extract on `clip_a.wav` then on a byte-identical copy `clip_b.wav`; outputs bit-identical.
- L11.2 — No time-of-day dependence: 1000 runs over 24 hours; max-abs-diff = 0.
- L11.3 — No PRNG drift: R³ contains no `random` or `torch.manual_seed` hook; AST audit confirms; runtime instrumentation confirms no PRNG calls.
- L11.4 — No global-state mutation: extractor instances are independent; output of A then B = output of B then A bit-identically.
- L11.5 — No hidden cache: re-extracting same input gives bit-identical output (cache would; absence of cache also gives bit-identical — this test pairs with L11.6).
- L11.6 — No cache-survives-across-instances: discard extractor A, create B; output identical (rules out per-instance cache that affects B).
- L11.7 — No environment-variable dependence: sweep `NUMEXPR_*`, `OMP_*`, `MKL_*`, `PYTHONHASHSEED`; max-abs-diff = 0.
- L11.8 — No file-system side effects: instrument `os.write` / `open(..., 'w')` during extract; assert empty.
- L11.9 — No network calls: instrument socket; assert no traffic.
- L11.10 — No dynamic code load: assert no `exec` / `eval` / `__import__` after init.

Reports: `L11_anti_features/L11_{1..10}_*.md` plus `L11_summary.md`.

### L12 — API contract & immutability

**Paper claim being defended:** *"`R3Extractor.extract()` is a pure function from input to `R3Output`; the dataclass is frozen; the registry is immutable; the public API is stable."*

- L12.1 — `R3Extractor.extract(mel, audio, sr)` signature matches paper §Methods.
- L12.2 — `R3Output` is a frozen dataclass; `dataclasses.fields()` enumerates documented fields only.
- L12.3 — `R3Output.feature_map` is an immutable registry snapshot (try-mutate test).
- L12.4 — `R3Output.feature_names` is a frozen tuple of length 97.
- L12.5 — Two extractor instances are state-independent (parallel test).
- L12.6 — Concurrent extract() calls do not interfere (multi-thread torture test).
- L12.7 — Extract twice on same input → bit-identical output (purity test).
- L12.8 — No protected attributes leak through public API (introspection audit).
- L12.9 — Public symbols at `ear.r3.__init__` match documented exports.

Reports: `L12_api/L12_{1..9}_*.md` plus `L12_summary.md`.

### L13 — Performance probe (consumer-hardware budget)

**Paper claim being defended:** *"R³ executes at 3.31× real-time on a 2023 MacBook Air M2 (8 GB), single-threaded, with peak resident memory ≤ 465 MB / 30 s."*

- L13.1 — Real-time factor: median over 30 runs × 30 s clips, single-threaded.
- L13.2 — Frame rate (fps): median ≥ 570 fps; p95 ≥ 172.27 fps (real-time floor).
- L13.3 — Peak RSS ≤ 465 MB on 30 s clip.
- L13.4 — Peak RSS scaling: linear in clip duration (no quadratic blow-up).
- L13.5 — CPU utilisation (single-threaded): one core saturated, no thread spillover.
- L13.6 — Cold-start vs warm-start gap quantified.
- L13.7 — V-Reproduction Phase 0 reproducibility: real-time factor reproduces across re-runs within ±10%.

Reports: `L13_performance/L13_{1..7}_*.md` plus `L13_summary.md` with hardware fingerprint.

> *L14 (Documentation ↔ code consistency) is intentionally not included in this V-Reproduction copy — see the note at the top of this README. The canonical source suite at `The Paper/R3-Paper/R3_Isolated_Validation/` carries that layer against the live `.tex`.*

---

## What is OUT of scope here

If a test needs any of the following, it belongs in `R3_Success_in_System/` (system-level, master paper) or in the C³ companion paper:

- ❌ Western consonance dyad rating corpora (Eerola Exp3, Marjieh, Harrison Carillon)
- ❌ Cross-cultural rating corpora (inconMore, Hindustani raga, bonang)
- ❌ Any C³ mechanism (BCH, PCCR, MIAA, TPIO, …)
- ❌ Any H³ aggregator, RAM region, neurochemical
- ❌ Any human-rated dataset, listener panel, ground-truth annotation
- ❌ Predictive performance, surprisal, expectation-error
- ❌ "R³ predicts X" or "R³ recovers X" where X is a cognitive variable

R³ is upstream of all of these. Validating R³ against them mixes layers.

---

## Test format & layout

```
R3_Isolated_Validation/
├── README.md                           ← this file
├── _infra/
│   ├── conftest.py                    ← pytest fixtures (engine pin, fixed mel)
│   ├── stimuli.py                     ← stimulus library (silence, tones, noise, …)
│   └── manifests/engine_head.json     ← engine HEAD pin
├── L1_spec_compliance/
│   ├── d00_consonance_complexity.py
│   ├── d00_consonance_complexity.md
│   └── … (97 pairs) + L1_summary.md
├── L2_boundary_doctrine/ ……………… L2_summary.md
├── L3_determinism/      ……………… L3_summary.md
├── L4_output_guarantees/ ……………… L4_summary.md
├── L5_robustness/       ……………… L5_summary.md
├── L6_group_internal/   ……………… L6_summary.md
├── L7_dag_staging/      ……………… L7_summary.md
├── L8_warmup/           ……………… L8_summary.md
├── L9_constants/        ……………… L9_summary.md
├── L10_cross_impl/      ……………… L10_summary.md
├── L11_anti_features/   ……………… L11_summary.md
├── L12_api/             ……………… L12_summary.md
├── L13_performance/     ……………… L13_summary.md
├── run_all.py                          ← top-level pytest runner
└── REPORT.md                           ← aggregated PASS/FAIL/CAVEAT scorecard
```

Each test pair: `tNN_<name>.py` (pytest) + `tNN_<name>.md` (formula, expected, actual, verdict).

---

## Verdict aggregation

`REPORT.md` aggregates per-layer verdict and a single headline. Per-layer pytest-collected test counts (each parametrized call counts as one collected test):

| Layer | Tests | Description |
|---|---:|---|
| L1 — Spec compliance | 362 | Per-dim formula re-impl × stimulus families (parametrized over 9 R³ groups × 8 stimuli + sub-tests) |
| L2 — Boundary doctrine | 38 | Five inclusion rules quantified (frame locality, no-listener-model, group isolation, no prediction, determinism) |
| L3 — Determinism | 13 | Bit-identicality across run/seed/thread/process axes |
| L4 — Output guarantees | 6 | Shape (B,T,97), range [0,1], no-NaN, frozen dataclass |
| L5 — Robustness | 14 | Pathological inputs (silence, DC, impulse, clipped, low-amp, phase-inverted, …) |
| L6 — Group-internal physics | 17 | Analytical anchors per group |
| L7 — DAG staging | 10 | 2-stage DAG topology + dependency narrowness |
| L8 — Warm-up | 9 | Tier disclosure (Tier 0 / Tier 1 ramp / Tier 1 zero / Tier 2 zero) |
| L9 — Constants | 14 | Literature provenance + source-scan negative claims |
| L10 — Cross-impl | 9 | Independent re-implementations (Sethares, K-K 1982, Harte Tonnetz, MFCC DCT-II, A-weighting, Stevens) |
| L11 — Anti-features | 10 | No PRNG, no fs side-effects, no sockets, no exec/eval/subprocess, no global-state mutation |
| L12 — API | 9 | extract() signature pin, R3Output frozen dataclass, total_dim=97, immutable feature_map |
| L13 — Performance | 8 | Real-time factor + peak RSS budget |
| _infra | 12 | Engine pin integrity + output bounds + dim layout |
| **Total** | **531** | (reviewer cache mode + live BUILD mode both pass 531/531) |

Headline:

> **R³ delivers what it claims to deliver: 531 / 531 pytest tests PASS in both reviewer cache mode and live-engine BUILD mode against the canonical engine SHA-pin. Zero layer-leakage incidents, zero non-determinism incidents, every numeric constant traced to literature or engine-internal derivation.**

This is the only quantitative claim the R³ paper makes about itself in isolation. Cognitive validity is not claimed here and not relevant here. R³'s role inside the MI system is what makes this isolated battery load-bearing — and that is also why the battery has to be this strong.

---

## Engine pin

All tests run against engine HEAD `318eb2f529d7103e8b7d80b01228357fdc4e0217` (tree aggregate SHA-256 `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`) per `_infra/manifests/engine_pin.json`. Reviewer cache mode verifies against the pre-computed oracle at `engine_outputs/_unit_test_oracles/r3_isolated.pkl` + facts at `r3_engine_facts.pkl`.
