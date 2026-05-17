# L7 — Pipeline & demand-driven DAG correctness

> **Status:** **STATIC PORTION POPULATED + PASS (2026-05-09)**. L7.1, L7.5, L7.6 fully covered statically. L7.2, L7.3, L7.4 runtime test plans (skeleton). See [`L7_summary.md`](L7_summary.md) for headline scorecard.

## Paper claim being defended

*T³'s executor is a demand-driven graph; only the requested ~644/8,600 tuples are computed; no spurious computation; no Stage-2 → Stage-1 leakage; R³ → T³ → C³ data flow is unidirectional.*

## Audit results

> **✅ STATIC PASS — 3/3 statically-checkable sub-tests PASS.** T³ pipeline is structurally acyclic, all 7 documented phases are present in `executor.py`, and there are zero backward (T³→R³) or downward (T³→C³) imports. The R³ → T³ → C³ unidirectional data flow is enforced at the import-graph level.

| Sub-test | Subject | Method | Result |
|---|---|---|---|
| **L7.1** | Topological order: pipeline acyclic | static AST | **PASS** — `execute()` does not recurse; no event loop / callback imports |
| **L7.2** | Demand sparsity: mech-only registry → ~644 tuples | runtime | **Skeleton** (instrumentation needed) |
| **L7.3** | Full registry → ~8,600 tuples | runtime | **Skeleton** (awaits AST-walk reconciliation per master discrepancy) |
| **L7.4** | Dependency narrowness | runtime | **Skeleton** (R³ access instrumentation) |
| **L7.5** | Pipeline phase ordering: 7 phases in `execute()` body | static AST | **PASS** — all 7 phase markers identified |
| **L7.6** | No backward (T³→R³) / downward (T³→C³) dependency | static import-graph | **PASS** — 0 violations |

## L7.1 — Acyclic structure

| Check | Result |
|---|---|
| `self.execute()` recursive calls inside `execute` body | **0** |
| `asyncio` / `callback` / `signal` imports anywhere in `executor.py` | **0** |

## L7.5 — 7 phase markers in [`executor.py`](../../../../../Musical_Intelligence/ear/h3/pipeline/executor.py)

| Phase | Source line |
|---|---|
| 1–2: Demand collection / tree ready (input) | executor.py:111 |
| 3: Horizon loop | executor.py:121 |
| 4: Window selection (per law) | executor.py:171, 177-182 |
| 5: Attention weighting (computed once per horizon, hoisted) | executor.py:128-129 |
| 6: Morph dispatch | executor.py:186 |
| 7: Result packing (normalize + store) | executor.py:188, 203 |

## L7.6 — Import-graph forbidden patterns (all 0)

| Pattern | Hits |
|---|---|
| `ear.r3` (relative) | 0 |
| `Musical_Intelligence.ear.r3` (absolute) | 0 |
| `brain` (any C³ module) | 0 |
| `Musical_Intelligence.brain` (absolute) | 0 |
| `Musical_Intelligence.contracts.bases` (C³ belief base classes) | 0 |

**Allowlisted:** `Musical_Intelligence.contracts.dataclasses` (where `H3DemandSpec` is defined). Shared dataclass surface, not an upward dependency.

## Strongest implication

L7 + L2.1 + L9 + L11 jointly establish that:

> **T³ is a pure-function pipeline with acyclic structure and unidirectional data flow.** It consumes R³ output and produces a sparse result dict. C³ reads the result; nothing in h3/ knows about C³. R³ → T³ → C³ is enforced at the import-graph level, not just by convention.

## Reports

- [`L7_summary.md`](L7_summary.md) — full audit + per-sub-test results
- [`L7_audit.json`](L7_audit.json) — programmatic audit output

## Reproducibility

Audit script: `../_infra/audit_scripts/h3_pipeline_audit.py`.
Re-run: `python3 _infra/audit_scripts/h3_pipeline_audit.py`

Audit is byte-deterministic against engine source; STATIC PASS holds as long as `executor.py` and h3/ import structure are unchanged.

## Out of scope

This layer tests T³'s **functional contract only**. No cognitive/listener data; no downstream layer; no system-level claim. See `../README.md` for the full out-of-scope list.
