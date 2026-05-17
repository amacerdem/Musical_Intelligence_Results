# T³ Isolated Validation — Paper-Grade Test Battery

> **Scope lock — read before adding any test:**
> This folder validates T³ as a **sealed module**. No downstream layer (C³, RAM, neurochemistry) is involved. No cognitive label (pleasantness, surprisal, listener data, EEG/fMRI traces) is involved. The only question we answer here is:
>
> **"Does T³ extract the multi-scale temporal morphological statistics it claims to extract — correctly, deterministically, statelessly, and within its declared boundary — across every R³-substrate input and every operating axis a sealed temporal-morphology engine can be tested on?"**
>
> The paper's strength comes from T³'s function inside MI. That role demands an isolated validation that is **as strong as the role itself is load-bearing**. Mixing this with cognitive validation re-introduces the layer-leak we just removed.

> **V-Reproduction note:** this copy under `Science/V-Reproduction/20-t3-isolated-validation/` is **decoupled from the paper tree** — no `.tex` dependency. The doc-consistency audit (L14), the heavy experiment-artefact folders (`phase_lag_32rate/`, `wilson_cowan/`, `determinism_canary/`, `_selectivity/`), and the standalone audit scripts under `_infra/audit_scripts/` (hardcoded absolute paths) all live only in the canonical source suite at `The Paper/T3-Paper/T3_Isolated_Validation/`. Engine, spec compliance, statelessness, determinism, output guarantees, robustness, operator correctness, and performance budget are still verified here.

> **Status at copy time:** runtime-tested layers are **Pin + L1 + L3 + L4 + L5 + L6 + L13** (7 layers, 207 tests, ✅ ALL PASS). Layers **L2, L7, L8, L9, L10, L11, L12** ship pre-computed audit artefacts (JSON + summary MD) but no pytest-side runtime tests yet — they appear in the scorecard as ⚪ EMPTY rather than silently disappearing.

---

## Quick start (fresh-clone reproduction)

After cloning the `SRC Musical Intelligence` repository:

```bash
cd Science/V-Reproduction/20-t3-isolated-validation
python3 run_all.py
```

This runs Pin + L1 + L3 + L4 + L5 + L6 + L13 (every layer that ships pytest tests) and writes a fresh `REPORT.md` with the per-layer scorecard. Exit code is the worst pytest exit code observed (`0` = all PASS).

**Prerequisites** (no in-tree install, no vendored wheels):

```bash
pip install torch numpy scipy soundfile pytest
```

The engine (`Musical_Intelligence/`) is auto-discovered via an upward walk from `conftest.py` — no manual `PYTHONPATH` setup needed. Stimuli are generated deterministically in memory by `_infra/stimuli.py`. Expected wallclock on M2 8 GB ≈ 30 s; headline ✅ ALL PASS.

For a sanity check before the full run:

```bash
python3 run_all.py --quick     # pin-integrity + L1 only (~1 s)
```

---

## What T³ promises (functional contract)

| # | Contract clause | Layer that tests it |
|---|---|---|
| 1 | R³ 97-D vector stream in → 4-tuple sparse address space `(r, h, m, ℓ)` out | L1, L4 |
| 2 | 32 horizons with log-coverage organised in four perceptual bands (5.8 ms – 981 s), 24 statistical morphs, 3 causal laws | L1, L8 |
| 3 | Theoretical address space `97 × 32 × 24 × 3 = 223,488`; demand-driven sparsity ~644 mech-only / ~8,600 full registry | L4, L7 |
| 4 | Shared exponential attention kernel `exp(−3·(1−p))`, newest-to-oldest weight ratio e³ ≈ 20.09 | L1, L6, L10 |
| 5 | **Statelessness principle (Rule 1):** no `self._ema`, `self._previous_output`, `self._count`. Every output is a pure function of window content. | L2, L11 |
| 6 | Embarrassingly parallel: outputs at different frames are independent | L2, L7 |
| 7 | Frame-input determinism (Rule 2) | L3 |
| 8 | Each of 24 morphs computes the documented statistic (M0=mean, M2=std, M8=velocity, M14=periodicity, M18=trend, …) | L6, L10 |
| 9 | Each of 3 laws applies the documented temporal direction (L0=memory/causal, L1=forward, L2=integration/bidirectional) | L6 |
| 10 | Output range and dataclass guarantees on `H3Output` | L4, L12 |
| 11 | Well-defined on all valid R³ inputs (silence-frame, single-frame windows, post-warm-up) | L5 |
| 12 | Zero calibration: every numeric constant literature-grounded or engine-internal-derived | L9 |
| 13 | Frozen API; `H3Output` is frozen dataclass; `H3DemandSpec` is slot-restricted (engine-side hardening to frozen-dataclass deferred per L12.3) | L12 |
| 14 | Real-time consumer-hardware budget for the T³ stage alone | L13 |

---

## Thirteen-layer test battery

Each layer below has its own subfolder with a `README.md` defining the test plan, expected results, and reports format. Tests inside each layer are paired `tNN_<name>.py` (pytest) + `tNN_<name>.md` (formula, expected, actual, verdict).

| Layer | Subject | Status in this copy |
|---|---|---|
| **L1** — Spec compliance | Per-tuple `(r, h, m, ℓ)` formula re-implementation, bit-identical to engine | ✅ pytest (20 tests) |
| **L2** — Statelessness & boundary doctrine | AST + runtime audits for the 5 inclusion rules | ⚪ audit artefacts (no pytest) |
| **L3** — Determinism & reproducibility | Bit-identicality across run, seed, thread, OS, hardware axes | ✅ pytest (7 tests) |
| **L4** — Output guarantees | 4-tuple addressing, range, no NaN/Inf, dataclass freezing | ✅ pytest (125 tests) |
| **L5** — Pathological input robustness | Silence frames, single-frame windows, edge-case R³ inputs | ✅ pytest (21 tests) |
| **L6** — Operator correctness | Each morph + law on stimuli where the answer is analytically known | ✅ pytest (22 tests) |
| **L7** — Pipeline & DAG correctness | Demand-driven executor, dependency narrowness, no Stage-2→Stage-1 leakage | ⚪ audit artefacts (no pytest) |
| **L8** — Horizon scale validation | 32 horizons with log-coverage in 4 bands match documented ranges | ⚪ audit artefacts (no pytest) |
| **L9** — Constant provenance audit | Every numeric constant traced (exp(-3·(1-p)), 24 morph definitions, 3 law definitions) | ⚪ audit artefacts (no pytest) |
| **L10** — Cross-implementation cross-validation | Pure-numpy/scipy re-impl of each morph + law | ⚪ audit artefacts (no pytest) |
| **L11** — Anti-feature tests | No hidden state, no time-of-day, no PRNG drift, no env dep | ⚪ audit artefacts (no pytest) |
| **L12** — API contract & immutability | `H3Extractor.extract()` purity, `H3Output` frozen, `H3DemandSpec` slot-restricted, public surface stable | ⚪ audit artefacts (no pytest) |
| **L13** — Performance probe | T³ stage real-time factor on M2 8GB, peak memory budget | ✅ pytest (5 tests) |

---

## What is OUT of scope here

If a test needs any of the following, it belongs in `T3_Success_in_System/` (system-level annotation of master-paper claims) or in the C³ companion paper:

- ❌ DEAM emotion ratings, Eerola Set 1/2 ratings, listener-rated valence/arousal (cognitive)
- ❌ Cheung 2019 reward, surprisal, expectation-error (cognitive — F2/F6 territory)
- ❌ EEG envelope tracking, MEG cortical entrainment (cognitive cross-modal — V-Reproduction)
- ❌ fMRI BOLD encoding, voxelwise prediction (system — master / C³-Bio)
- ❌ Beat tracking, downbeat detection, GTZAN benchmarks (cognitive substrate — C³ F7 motor or master)
- ❌ Cross-cultural beat hierarchy (NHS, Hindustani, gamelan) when the claim is about *listener perception* (master V5)
- ❌ Speech-vs-music dissociation against listener / lesion data (cognitive — master)
- ❌ Pooled ECE on held-out songs (master claim — annotated in `T3_Success_in_System/S2`)
- ❌ Any C³ mechanism (BCH, PCCR, MIAA, MMP, SRP, …)
- ❌ Any F-mechanism's predictive performance against human ratings

T³ is upstream of all of these. Validating T³ against them mixes layers. T³'s job is to deliver the morphological substrate; any claim about how that substrate predicts cognition belongs to the consumer layer that uses it.

---

## Test format & layout

```
20-t3-isolated-validation/
├── README.md                       ← this file
├── conftest.py                     ← pytest session fixtures (engine pin walk-up + h3 fixture)
├── _infra/
│   ├── stimuli.py                 ← R³ feature streams (silence, tones, ramps, AM, real audio bytes)
│   ├── sha_utils.py               ← engine-tree SHA aggregation
│   ├── test_pin_integrity.py      ← engine SHA + registry pin gate
│   └── manifests/engine_pin.json  ← engine HEAD pin manifest
├── L1_spec_compliance/             ← pytest: M0/M8/M14/M18 formula re-impl (20 tests)
├── L2_statelessness/               ← audit JSONs + summary (no pytest yet)
├── L3_determinism/                 ← pytest: run/seed/thread (7 tests)
├── L4_output_guarantees/           ← pytest: dtype/shape/range/no-NaN (125 tests)
├── L5_robustness/                  ← pytest: silence / single-frame / pathological (21 tests)
├── L6_operator_correctness/        ← pytest: morph + law analytical anchors (22 tests)
├── L7_pipeline_dag/                ← audit (no pytest yet)
├── L8_horizon_scale/               ← audit (no pytest yet)
├── L9_constants/                   ← audit JSONs + summary (no pytest yet)
├── L10_cross_impl/                 ← audit + permutation_null sub-experiment (no pytest yet)
├── L11_anti_features/              ← audit JSON + summary (no pytest yet)
├── L12_api/                        ← audit JSON + summary (no pytest yet)
├── L13_performance/                ← pytest: real-time factor + memory budget (5 tests)
├── run_all.py                      ← top-level pytest orchestrator → REPORT.md
└── REPORT.md                       ← aggregated PASS/FAIL/EMPTY scorecard (regenerated)
```

Layers and experiment directories present in the source suite but **excluded from this V-Reproduction copy** (not consumed by any test_*.py):

- `L6_operator_correctness/phase_lag_32rate/` (98 MB experiment outputs)
- `L6_operator_correctness/wilson_cowan/` (figure/output scripts)
- `L3_determinism/determinism_canary/` (16 MB experiment outputs)
- `_selectivity/f6_ablation_v2/` (load-bearingness audit scripts)
- `_infra/audit_scripts/` (one-shot tooling with hardcoded `/Volumes/` paths)
- `L14_doc_consistency/` (paper-↔-code drift summary; not a runtime layer)

---

## Verdict aggregation

Headline target (when battery is fully populated):

> **T³ delivers what it claims to deliver: ≥ 99.9% of the isolated checks PASS, every CAVEAT named and disclosed, statelessness principle audited end-to-end, zero layer-leakage incidents, every numeric constant traced to literature or engine-internal derivation.**

This is the only quantitative claim the T³ paper makes about itself in isolation. Cognitive validity is not claimed here and not relevant here. T³'s role inside the MI/MI system is what makes this isolated battery load-bearing — and that is also why the battery has to be this strong.

System-level claims that depend on T³ as substrate live in `../T3_Success_in_System/`, with provenance annotation back to the master paper.

---

## Engine pin

All tests run against the engine HEAD pinned in `_infra/manifests/engine_pin.json`. The pin-integrity gate (first row of every run) computes a SHA-256 aggregate of `Musical_Intelligence/ear/h3/**.py` and refuses to proceed if it disagrees with the manifest.
