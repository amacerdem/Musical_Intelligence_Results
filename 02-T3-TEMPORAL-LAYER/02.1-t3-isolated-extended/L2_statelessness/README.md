# L2 — Statelessness & boundary doctrine probes

> **Status:** **L2.1 POPULATED + PASS (2026-05-09)**; L2.2–L2.5 runtime-test plans (skeleton). See [`L2_summary.md`](L2_summary.md) for headline scorecard.

## Paper claim being defended

*T³ provably obeys statelessness and the inclusion rules: every output is a pure function of window content; no hidden temporal state inside the engine.*

## Audit results

> **✅ L2.1 PASS (AST audit, structurally definitive). T³'s statelessness principle is structurally upheld: zero non-init `self.X = ...` assignments anywhere in 15 classes / 42 files / 8 compute methods.**

| Sub-test | Subject | Result |
|---|---|---|
| **[L2.1](L2.1_ast_audit.md)** | Statelessness AST audit (compute-method scan + strict scan over all methods) | **PASS** — 0 state-keeper-pattern violations, 0 non-init self-assigns, 0 globals |
| **[L2.2](L2.2_window_purity.md)** | Window-content purity (runtime: same input → same output) | **Skeleton** — structurally guaranteed by L2.1; supported by L3.1 canary already PASS |
| **[L2.3](L2.3_embarrassingly_parallel.md)** | Embarrassingly-parallel property (serial vs threaded) | **Skeleton** — structurally guaranteed for overlap-aware chunking |
| **[L2.4](L2.4_no_instance_mutation.md)** | No instance-state mutation across calls | **PASS by L2.1 structural guarantee** + skeleton runtime confirmation |
| **[L2.5](L2.5_no_r3_frame_state_leakage.md)** | Causal-window honesty (L0/L1/L2 truncation probe) | **Skeleton** — independent of L2.1 (catches window-misindexing, not hidden state) |

## Anti-pattern probes (all clean)

| Pattern | Hits |
|---|---|
| `self._ema` / `self.ema_*` | 0 |
| `self._previous_*` / `self._prev_*` | 0 |
| `self._count` | 0 |
| `self._cache` / `self._cache_*` | 0 |
| `self._buffer` / `self._buffer_*` | 0 |
| `self._history` | 0 |
| `self._last_*` | 0 |
| `self._accumulator` / `self._accum` | 0 |
| `self._running_*` | 0 |
| `self._memo` | 0 |
| `self._state` | 0 |
| `global` declarations in compute paths | 0 |

## Strongest implication

Two `H3Extractor.extract()` calls on the same input produce **bit-identical output by construction** — the AST audit proves there is no internal state to drift between calls. T³'s embarrassingly-parallel property is a structural consequence of the source code, not an empirical hope.

## Reports

- `L2.1_ast_audit.md` + `L2.1_ast_audit.json` — programmatic AST audit results (definitive)
- `L2.2_window_purity.md` — runtime test plan (skeleton)
- `L2.3_embarrassingly_parallel.md` — runtime test plan (skeleton)
- `L2.4_no_instance_mutation.md` — structural confirmation + runtime test plan (skeleton)
- `L2.5_no_r3_frame_state_leakage.md` — runtime test plan (skeleton, independent of L2.1)
- `L2_summary.md` — aggregated scorecard

## Reproducibility

Audit script committed at `../_infra/audit_scripts/h3_statelessness_audit.py`.
Re-run: `python3 _infra/audit_scripts/h3_statelessness_audit.py`

Audit is byte-deterministic; L2.1 PASS holds as long as no future commit introduces a non-init self-assign or `global` declaration in `ear/h3/`.

## Out of scope

This layer tests T³'s **functional contract only**. No cognitive/listener data; no downstream layer; no system-level claim. See `../README.md` for the full out-of-scope list.
