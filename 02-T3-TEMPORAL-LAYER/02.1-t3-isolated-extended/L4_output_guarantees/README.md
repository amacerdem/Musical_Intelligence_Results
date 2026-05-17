# L4 — Output guarantees (4-tuple addressing, range, dataclass)

> **Status:** **POPULATED + PASS (2026-05-09)** — 125/125 tests pass in 0.86s. See [`L4_summary.md`](L4_summary.md) for full scorecard.

## Paper claim being defended

*`H3Output` is a frozen dataclass; demand-driven sparsity is well-defined; outputs respect documented per-morph bounds; no NaN / no Inf on any valid R³ input.*

## Audit results

> **✅ PASS — 125/125 tests pass.** Demand-request → output-key contract holds; per-morph range bounds (signed `[-1,1]` for M6/M8/M9/M11/M12/M16/M18/M23, unsigned `[0,1]` for the other 16) hold across 5 stimulus families; **2,400 random-input morph evaluations + 5 pathological-input cases produced zero NaN, zero Inf**.

| Sub-test | Subject | Tests | Result |
|---|---|---|---|
| **L4.1** | Demand contract: request set ↔ return set | 9 | **PASS** |
| **L4.2** | Per-morph range: `[0,1]` unsigned vs `[-1,1]` signed across 5 stimuli | 11 | **PASS** |
| **L4.3** | No NaN / no Inf on 100 random seeds + 5 pathological edge cases | 105 | **PASS** |
| **L4.4** | Demand sparsity (~644 mech-only / ~8,600 full registry) | runtime | **Skeleton** — needs C³ mechanism registry import |
| **L4.5** | `H3Output` frozen dataclass | static | **PASS by L12.2** |
| **L4.6** | `feature_map` immutable | static | **PASS by L12.2 + L4.1** |

## Strongest result

**Engine is finite-output-correct on pathological + randomised input.** Combined 105 NaN/Inf tests cover:
- 100 random seeds × 24 morphs = **2,400 morph evaluations**
- 4 pathological edge cases × ~24-288 morphs each
- **Zero failures.**

Combined with L4.2 per-morph range bounds, this establishes T³ outputs are well-defined and bounded for any well-formed R³ input. This is the operator-level realisation of `H3Output`'s docstring contract:

> "Unsigned morphs are in [0, 1]; signed morphs (M6, M8, M9, M11, M12, M16, M18, M23) are in [-1, 1]."

## Reports

- [`L4_summary.md`](L4_summary.md) — full audit + per-test scorecard
- [`test_demand_contract.py`](test_demand_contract.py) — 9 demand contract tests
- [`test_output_range.py`](test_output_range.py) — 11 range tests
- [`test_no_nan_inf.py`](test_no_nan_inf.py) — 105 finite-output tests

## Reproducibility

Run tests:
```bash
cd T3-Paper/T3_Isolated_Validation
pytest L4_output_guarantees/ -v
```

Engine pin verified at session start. Random seeds are deterministic (`torch.Generator().manual_seed(seed)`); same seeds = same R³ streams = same engine outputs (L3 determinism). Tests are reproducible byte-for-byte.

## Coverage gap (deferred)

- **L4.4** demand sparsity: needs C³ mechanism registry to count actual demand cardinalities; cross-paper coupling, deferred.
- 10K random-input sweep version (current: 100 seeds for fast iteration).

## Out of scope

This layer tests T³'s **functional contract only**. No cognitive/listener data; no downstream layer; no system-level claim. See `../README.md` for the full out-of-scope list.
