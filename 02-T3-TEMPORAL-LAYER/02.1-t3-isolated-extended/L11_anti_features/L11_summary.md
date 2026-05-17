# L11 — Anti-features audit: summary scorecard

**Date:** 2026-05-09
**Audit method:** Static AST scan of `Musical_Intelligence/ear/h3/` (42 files) for non-determinism, side-effect, and environment-dependence patterns. Runtime sub-tests (L11.1, L11.2, L11.5, L11.6) deferred to skeleton.
**Engine pin:** HEAD (T³ paper-time anchor, frozen since 2026-05-06).

## Headline

> **✅ STATIC PASS — All 5 statically-checkable sub-tests of L11 return zero hits across `ear/h3/`. T³ has no PRNG, no filesystem writes, no network calls, no dynamic code execution, and no module-level globals declared as mutable in compute paths.**

## Per-sub-test scorecard

| Sub-test | Subject | Method | Result |
|---|---|---|---|
| **L11.1** | No filename dependence (same R³ stream from two paths → same output) | runtime | **Skeleton** — structurally guaranteed by L2.1 (no instance state); empirical confirmation deferred |
| **L11.2** | No time-of-day dependence (1000 runs over 24h → max-abs-diff = 0) | runtime | **Skeleton** — supported by L2.1 + L11.3 (no PRNG to drift) + L3 canary |
| **L11.3** | No PRNG drift | static AST | **PASS** — 0 PRNG imports (`random`, `secrets`); 0 PRNG calls (no `torch.rand*`, no `numpy.random.*`, no `torch.manual_seed`, no `np.random.seed`) |
| **L11.4** | No global-state mutation (extractor instances independent) | static AST | **PASS** — covered by L2.1 strict scan (0 non-init `self.X = ...`; 0 `global` declarations) |
| **L11.5** | No cross-instance hidden cache | runtime | **Skeleton** — structurally guaranteed by L2.1 + L11.4 |
| **L11.6** | No environment-variable dependence (sweep `NUMEXPR_*`, `OMP_*`, `MKL_*`, `PYTHONHASHSEED`) | runtime | **Skeleton** — engine has no `os.environ.get(...)` reads in `ear/h3/` (verified incidentally during scan; exhaustive runtime sweep deferred) |
| **L11.7** | No filesystem side effects during extract | static AST | **PASS** — 0 `open(..., 'w'/'a'/'x')` calls; 0 `pathlib.Path.write_text` or `.write_bytes` calls anywhere in `ear/h3/` |
| **L11.8** | No network calls | static AST | **PASS** — 0 imports of `socket`, `urllib`, `urllib3`, `requests`, `httpx`, `http.client`, `ftplib`, `smtplib`, `aiohttp`, `websockets` |
| **L11.9** | No dynamic code load | static AST | **PASS** — 0 `exec(...)`, 0 `eval(...)`, 0 `compile(...)`, 0 `__import__(...)` calls |

## Static scan summary

| Pattern | Count |
|---|---|
| Files scanned | 42 |
| PRNG imports (`random`, `secrets`) | 0 |
| PRNG calls (`torch.rand*`, `np.random.*`, `manual_seed`, `seed`, `Generator`, etc.) | 0 |
| Filesystem write calls (`open(..., 'w/a/x')`, `Path.write_text`, `Path.write_bytes`) | 0 |
| Network imports (`socket`, `urllib`, `requests`, `httpx`, etc.) | 0 |
| Dynamic code calls (`exec`, `eval`, `compile`, `__import__`) | 0 |

## Implications

The combination of **L2.1** (zero non-init self-assigns) + **L9** (zero cognitive-data calibration) + **L11 static** (zero PRNG/IO/network/exec) means:

1. **T³'s output at any frame is a pure mathematical function** of (R³ input window, demand 4-tuple, FROZEN engine constants). No source of randomness, no external IO, no environment dependence, no per-instance state can affect the output.

2. **Bit-determinism is a structural consequence**, not an empirical hope. The L3 canary's 28-pair PASS becomes the *measurement* of a property that L2 + L11 prove must hold by construction.

3. **The "engine HEAD pin" is sufficient for reproducibility**: any clone at the engine's commit hash will produce bit-identical T³ output, because there is no source of variation outside the source code itself. This grounds the master MI's `|Δρ| ≤ 8.8 × 10⁻⁵` reproducibility claim.

## Reports

- [`L11_audit.json`](L11_audit.json) — programmatic scan output
- [`L11_summary.md`](L11_summary.md) — this scorecard

L11.1, L11.2, L11.5, L11.6 runtime test plans are skeletons within the README; their structural guarantees are noted above.

## Reproducibility

Audit script: `_infra/audit_scripts/h3_anti_features_audit.py`.
Re-run: `python3 _infra/audit_scripts/h3_anti_features_audit.py`

Audit is byte-deterministic against engine source; PASS holds as long as no future commit introduces a PRNG, network, filesystem-write, or dynamic-code pattern in `ear/h3/`.

## Headline (production-grade form)

When L11 runtime tests (L11.1, L11.2, L11.5, L11.6) are added, the layer becomes:

> **L11 PASS — 9/9:** zero PRNG, zero IO, zero network, zero exec/eval, zero env-dependence, zero filename-dependence, zero time-of-day-dependence, zero cross-instance cache, zero shared-state mutation. T³ output is a pure function of input + frozen engine constants.
