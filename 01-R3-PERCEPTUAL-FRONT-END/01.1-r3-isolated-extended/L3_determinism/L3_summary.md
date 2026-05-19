# L3 — Determinism — Summary

**Engine pin:** `318eb2f5…` · **Total tests:** 13 PASS / 13 (100 %)

L3 quantifies the engine's max-abs-diff = 0 promise across every
deterministic axis tractable in single-machine CI. Cross-OS / cross-HW /
cross-torch-version / cross-machine-reboot are documented as **out of
scope** at this layer (paper §Limitations boundary case 4); they require
distributed CI infrastructure not yet in place.

---

## Per-axis scorecard

| Axis | Test file | Tests | Verdict |
|------|-----------|-------|---------|
| **L3.1** Same-process N runs (max-abs-diff = 0 over 100 runs × 4 stimulus families) | [test_l3_1_same_process_runs.py](test_l3_1_same_process_runs.py) | 2 | ✅ 2/2 |
| **L3.2** Cross-process — fresh interpreter, same audio, SHA-256 of features identical | [test_l3_2_cross_process.py](test_l3_2_cross_process.py) | 2 | ✅ 2/2 |
| **L3.3** No PRNG — AST audit + behavioural seed flips | [test_l3_3_no_prng.py](test_l3_3_no_prng.py) | 3 | ✅ 3/3 |
| **L3.4** Cross-thread-count (`torch.set_num_threads ∈ {1, 2, 4, 8}`) | [test_l3_4_thread_count.py](test_l3_4_thread_count.py) | 4 | ✅ 4/4 |
| **L3.5** Float-precision sensitivity (float32 vs float64 drift bound) | [test_l3_5_dtype_sensitivity.py](test_l3_5_dtype_sensitivity.py) | 2 | ✅ 2/2 |
| **Total** | | **13** | **✅ 13/13** |

## L3.1 — same-process determinism

- 100 back-to-back extracts on a fixed `mix` clip: `max_abs_diff = 0`.
- Bit-identicality also confirmed on `white`, `tone_a4`, `silence`.

This is the engine's strongest determinism anchor (paper §Discussion
"Services to V-Reproduction"). The paper's published bound is `|Δρ| ≤
8.8 × 10⁻⁵` at the architecture level; R³ alone is **strictly stronger**
(max-abs-diff = 0).

## L3.2 — cross-process determinism

- A fresh Python interpreter, fresh torch import, fresh `R3Extractor()`
  instance, on the same WAV file → SHA-256 of `(B,T,97)` features is
  byte-identical to the in-process baseline.
- Two independent subprocesses also agree.

Pins R³ as **truly stateless across interpreter boundaries** — no module-level
caches, no static initialisation order dependencies, no global PRNG state
that survives across re-imports.

## L3.3 — no PRNG / no seed dependence

(a) **AST audit.** No `random.*`, `np.random`, `torch.manual_seed`, `torch.rand*`,
`torch.bernoulli`, `torch.multinomial`, `F.dropout`, or `nn.Dropout`
appears in any `.py` under `ear/r3/`. Comments are scanned too —
documented determinism, not just implemented determinism.

(b) **Behavioural probe.** Setting `torch.manual_seed`, `np.random.seed`,
`random.seed` to {0, 1, 42, 1729, 9999} between runs: max-abs-diff = 0.

(c) `PYTHONHASHSEED` flips also leave output bit-identical (audits any
accidental `hash(...)` consumption).

## L3.4 — cross-thread-count

- Sweeping `torch.set_num_threads` ∈ {1, 2, 4, 8} between runs: max-abs-diff = 0.
- Pins R³'s operator set (mel @ matrix, FFT, sums, reductions) against
  any future op-substitution that introduces thread-order non-determinism.

## L3.5 — float-precision sensitivity

| Dim | Name                  | f32 ↔ f64 max \|Δ\| | Source of drift                                       |
|-----|-----------------------|---------------------|-------------------------------------------------------|
| 3   | `stumpf_fusion`       | ~0.17               | `_stumpf` k=1..6 best-snap loop with sigmoid×exp products |
| 4   | `sensory_pleasantness`| ~0.07               | Inherits 0.4× of stumpf drift                          |
| 5   | `inharmonicity`       | ~0.17               | = 1 − stumpf_fusion (algebraic alias)                  |
| (all 94 others) |             | ≤ 10⁻⁴              | Numerical noise through sigmoid/clamp, no logical drift |

**Disclosure**: `stumpf_fusion`'s discrete tier-selection (k=1..6 best-snap
choice) introduces the only material dtype-sensitivity in R³. All other
dims are ε-tight at 10⁻⁴. The engine pin is float32; this layer documents
how robust the pipeline is to dtype choice.

---

## Cross-axis pinning summary (paper-grade)

| Determinism axis | Status | Coverage |
|------------------|--------|----------|
| Same process, repeat runs | ✅ Pinned bit-identical | L3.1 (100 runs × 4 stimuli) |
| Same process, multiple stimulus families | ✅ Pinned bit-identical | L3.1 |
| Cross process | ✅ Pinned bit-identical (SHA-256) | L3.2 |
| No PRNG / no seed dependence | ✅ AST + behavioural | L3.3 |
| Cross-thread-count | ✅ Pinned bit-identical | L3.4 |
| Float dtype (f32 vs f64) | ✅ Bounded; disclosed per-dim | L3.5 |
| Cross-OS                 | ⚪ Out of scope (single-OS CI)         | paper §Limitations |
| Cross-HW (M1/M2/x86)     | ⚪ Out of scope (single-HW CI)         | paper §Limitations |
| Cross-torch-version      | ⚪ Out of scope (single-version CI)    | paper §Limitations |
| Cross-machine-reboot     | ⚪ Out of scope (CI ephemeral)         | paper §Limitations |

The "out of scope" axes are not unaddressed — they are unaddressed
**at this CI tier**. The V-Reproduction archive (`Musical_Intelligence_Results/`)
exercises some of them in the paper's Phase-0 reproducibility runs.
