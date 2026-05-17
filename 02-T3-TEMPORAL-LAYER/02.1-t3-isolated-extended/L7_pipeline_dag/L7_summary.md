# L7 — Pipeline & DAG audit: summary scorecard

**Date:** 2026-05-09
**Audit method:** Static AST + import-graph analysis of `Musical_Intelligence/ear/h3/`. Runtime sub-tests (L7.2, L7.3, L7.4) deferred to skeleton.
**Engine pin:** HEAD (T³ paper-time anchor, frozen since 2026-05-06).

## Headline

> **✅ STATIC PASS — 3/3 statically-checkable sub-tests PASS. T³ pipeline is structurally acyclic, all 7 documented phases are present in `executor.py`, and there are zero backward (T³→R³) or downward (T³→C³) imports. The R³ → T³ → C³ unidirectional data flow is enforced at the import-graph level.**

## Per-sub-test scorecard

| Sub-test | Subject | Method | Result |
|---|---|---|---|
| **L7.1** | Topological order: pipeline acyclic | static AST | **PASS** — `execute()` does not recurse to self; no event loop / callback / signal-handler imports |
| **L7.2** | Demand sparsity: mech-only registry → ~644 tuples | runtime | **Skeleton** (instrumentation needed for actual count) |
| **L7.3** | Full registry → ~8,600 tuples | runtime | **Skeleton** (instrumentation; awaits AST-walk reconciliation per master discrepancy paragraph) |
| **L7.4** | Dependency narrowness: requesting (r=5, h=10, m=14, ℓ=0) reads only frames in H10 window of R³ dim 5 | runtime | **Skeleton** (R³ access instrumentation) |
| **L7.5** | Pipeline phase ordering: 7 phases in `execute()` body | static AST | **PASS** — all 7 phase markers identified in source |
| **L7.6** | No backward dependency (T³ → R³) and no downward (T³ → C³) | static import-graph | **PASS** — 0 violations across all h3/ imports |

## L7.1 detail — Topological order

`H3Executor.execute()` is structurally acyclic:

| Check | Result |
|---|---|
| `self.execute()` recursive calls inside `execute` body | **0** |
| `asyncio` / `callback` / `signal` imports anywhere in `executor.py` | **0** |
| Inner loops are bounded (`for h_idx in sorted(...)`, `for (r3_idx, law_idx), morph_indices in grouped.items():`, `for morph_idx in morph_indices:`) | bounded by demand cardinality |

The data flow within `execute()` is a sequential read of `r3_tensor`, computation via `kernel + batch_morph + normalize_morph`, and write to a fresh `results` dict. No back-edges, no event registration, no recursion.

## L7.5 detail — Pipeline phase ordering

All 7 documented phases are present in [`executor.py`](../../../../../Musical_Intelligence/ear/h3/pipeline/executor.py) — verified via marker presence in source:

| Phase | Marker found at |
|---|---|
| 1–2: Demand collection / tree ready (input) | `if not demand_tree: return {}` (executor.py:111) |
| 3: Horizon loop | `for h_idx in sorted(demand_tree.keys()):` (executor.py:121) |
| 4: Window selection (per law) | `if law_idx == LAW_MEMORY:` …`elif … LAW_PREDICTION:` …`else: # LAW_INTEGRATION` (executor.py:177-182) + `r3_series.unfold(1, n_frames, 1)` (executor.py:171) |
| 5: Attention weighting | `weights = self._kernel.compute_weights(n_frames, device=device)` + `w_normed = weights / weights.sum().clamp(min=1e-8)` (executor.py:128-129) |
| 6: Morph dispatch | `batch_morph(windows, w_normed, morph_idx)` (executor.py:186) |
| 7: Result packing | `normalize_morph(raw, morph_idx)` (executor.py:188) + `results[key] = morph_results[morph_idx]` (executor.py:203) |

The module docstring (executor.py:8-15) lists all 7 phases in declared order; the implementation realises them in the same order. **No Stage-2 → Stage-1 leakage**: morph dispatch and normalization happen *after* window selection, which happens *after* horizon iteration. No back-edge.

**Optimisation note:** Phase 5 (kernel computation) is hoisted **out of the per-tuple loop** — kernel weights are computed *once per horizon* and reused across all (r3_idx, law) groups at that horizon. This is a pure-function caching: the kernel is stateless (L2.1 confirmed), so per-horizon computation is identical to per-tuple computation but avoids redundant work. Documented at executor.py:127.

## L7.6 detail — Import-graph directionality

Forbidden patterns scanned in all h3/ imports:

| Pattern | Reason | Hits |
|---|---|---|
| `ear.r3` (relative) | T³→R³ backward import | **0** |
| `Musical_Intelligence.ear.r3` (absolute) | absolute R³ import | **0** |
| `brain` (any C³ module) | T³→C³ downward import | **0** |
| `Musical_Intelligence.brain` (absolute) | absolute C³ import | **0** |
| `Musical_Intelligence.contracts.bases` | C³ contracts/bases (belief base classes) | **0** |

**Allowlisted:** `Musical_Intelligence.contracts.dataclasses` (where `H3DemandSpec` is defined). This is a shared dataclass surface, not an upward dependency — `H3DemandSpec` is the **input contract** that C³ uses to declare what it wants from T³, and T³ consumes it. The class itself does not import C³ logic.

The R³ → T³ → C³ directional flow is therefore enforced **at the import-graph level**, not just by convention. Any future commit that introduced a `from ear.r3 import …` or `from brain import …` in h3/ would fail this audit.

## Cross-reference

- **L9 + L8** confirm the constants surface (HORIZONS, MORPHS, LAWS) is frozen and traceable.
- **L11.4** confirms no module-level globals declare mutable state.
- **L2.1** confirms no method on any h3 class mutates instance state.
- **L7** + above ⇒ T³ is a **pure-function pipeline** with **acyclic structure** and **unidirectional data flow** that consumes R³ output and produces a sparse result dict. C³ reads the result; nothing in h3/ knows about C³.

## Reports

- [`L7_summary.md`](L7_summary.md) — this scorecard
- [`L7_audit.json`](L7_audit.json) — programmatic audit output

## Reproducibility

Audit script: `_infra/audit_scripts/h3_pipeline_audit.py`.
Re-run: `python3 _infra/audit_scripts/h3_pipeline_audit.py`

Audit is byte-deterministic against engine source; STATIC PASS holds as long as `executor.py` and h3/ import structure are unchanged.

## Headline (production-grade form)

When L7.2/L7.3/L7.4 runtime tests are added:

> **L7 PASS — 6/6:** pipeline acyclic, 7 phases in declared order, demand-driven sparsity ~644 mech-only / ~8,600 full registry confirmed by instrumentation, dependency narrowness verified per-tuple, R³ → T³ → C³ unidirectional flow enforced at import-graph level.
