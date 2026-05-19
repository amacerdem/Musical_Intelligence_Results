# L11 — Negative / anti-feature tests (no hidden state)

> **Status:** **STATIC PORTION POPULATED + PASS (2026-05-09)**. L11.3, L11.4, L11.7, L11.8, L11.9 fully covered by static AST audit (zero hits). L11.1, L11.2, L11.5, L11.6 runtime test plans (skeleton). See [`L11_summary.md`](L11_summary.md) for headline scorecard.

## Paper claim being defended

*T³ has no hidden state, cache, global, time-, filename-, or environment-dependence beyond declared inputs.*

## Audit results

> **✅ STATIC PASS — All 5 statically-checkable sub-tests return zero hits across `ear/h3/`. T³ has no PRNG, no filesystem writes, no network calls, no dynamic code execution, no globals.**

| Sub-test | Subject | Method | Result |
|---|---|---|---|
| **L11.1** | No filename dependence | runtime | **Skeleton** — structurally guaranteed by L2.1 |
| **L11.2** | No time-of-day dependence | runtime | **Skeleton** — supported by L11.3 (no PRNG to drift) |
| **L11.3** | No PRNG drift | static AST | **PASS** — 0 imports, 0 calls |
| **L11.4** | No global-state mutation | static AST | **PASS** — covered by L2.1 strict scan |
| **L11.5** | No cross-instance hidden cache | runtime | **Skeleton** — structurally guaranteed by L2.1 |
| **L11.6** | No environment-variable dependence | runtime | **Skeleton** — engine has no `os.environ.get` reads in `ear/h3/` |
| **L11.7** | No filesystem side effects | static AST | **PASS** — 0 `open(..., 'w')`, 0 `Path.write_*` |
| **L11.8** | No network calls | static AST | **PASS** — 0 imports of `socket`/`urllib`/`requests`/etc. |
| **L11.9** | No dynamic code load | static AST | **PASS** — 0 `exec`/`eval`/`compile`/`__import__` |

## Static scan summary

| Pattern | Count |
|---|---|
| Files scanned | 42 |
| PRNG imports (`random`, `secrets`) | 0 |
| PRNG calls (`torch.rand*`, `np.random.*`, `manual_seed`, `seed`, `Generator`) | 0 |
| Filesystem write calls (`open(..., 'w/a/x')`, `Path.write_text/_bytes`) | 0 |
| Network imports (`socket`, `urllib`, `requests`, `httpx`, `aiohttp`, etc.) | 0 |
| Dynamic code calls (`exec`, `eval`, `compile`, `__import__`) | 0 |

## Strongest implication

The combination of **L2.1** (zero non-init self-assigns) + **L9** (zero cognitive-data calibration) + **L11 static** (zero PRNG/IO/network/exec) means:

> **T³'s output at any frame is a pure mathematical function of (R³ input window, demand 4-tuple, FROZEN engine constants).** No source of randomness, no external IO, no environment dependence, no per-instance state. Bit-determinism is a structural consequence, not an empirical hope.

## Reports

- [`L11_summary.md`](L11_summary.md) — full audit + per-sub-test results + structural implications
- [`L11_audit.json`](L11_audit.json) — programmatic scan output

## Reproducibility

Audit script: `../_infra/audit_scripts/h3_anti_features_audit.py`.
Re-run from the source suite at `The Paper/T3-Paper/T3_Isolated_Validation/_infra/audit_scripts/h3_anti_features_audit.py`

Audit is byte-deterministic against engine source; STATIC PASS holds as long as no future commit introduces a PRNG, network, filesystem-write, or dynamic-code pattern in `ear/h3/`.

## Out of scope

This layer tests T³'s **functional contract only**. No cognitive/listener data; no downstream layer; no system-level claim. See `../README.md` for the full out-of-scope list.
