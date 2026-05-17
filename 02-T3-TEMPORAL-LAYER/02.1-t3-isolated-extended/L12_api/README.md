# L12 — API contract & immutability

> **Status:** **STATIC POPULATED + PASS (2026-05-09)** with 1 doc-fix surfaced (L12.3). 6/8 sub-tests fully covered statically; L12.4 + L12.5 are runtime skeletons. See [`L12_summary.md`](L12_summary.md) for headline scorecard.

## Paper claim being defended

*`H3Extractor.extract()` is a pure function from input to `H3Output`; `H3Output` is a frozen dataclass; `H3DemandSpec` is slot-restricted; the public API is stable.*

> **Claim corrected from earlier "registry is immutable; H3DemandSpec is a frozen dataclass" wording per L12.3 finding.** `H3DemandSpec` uses `__slots__` (blocks new attributes) but is not a `@dataclass(frozen=True)` (existing slot values remain mutable). Engine-side hardening recommended; flagged as deferred.

## Audit results

| Sub-test | Subject | Result |
|---|---|---|
| **L12.1** | `H3Extractor.extract(self, r3, demand) -> H3Output` signature | **PASS** |
| **L12.2** | `H3Output` is `@dataclass(frozen=True)` with fields (`features`, `n_tuples`) | **PASS** |
| **L12.3** | `H3DemandSpec` immutability characterisation | **DOC-FIX** — slot-restricted regular class (NOT frozen dataclass); engine-hardening recommendation deferred |
| **L12.4** | Two extractor instances state-independent | **Skeleton** (runtime) — structurally guaranteed by L2.1 |
| **L12.5** | Concurrent `extract()` multi-thread torture | **Skeleton** (runtime) — structurally guaranteed by L2.1 + L11 |
| **L12.6** | `extract` twice on same input → bit-identical | **PASS by L2.1 + L11.3 structural composition** + L3 canary empirical |
| **L12.7** | No protected attributes leak through public API | **PASS** — only `extract` + `warmup_handler` accessible without underscore |
| **L12.8** | `ear.h3.__init__` exports match `__all__` | **PASS** — `__all__ = ["H3Extractor", "H3Output"]` exactly |

## L12.3 finding — H3DemandSpec characterisation

**Code reality** (`Musical_Intelligence/contracts/dataclasses/__init__.py:7-48`): `H3DemandSpec` is a **regular class with `__slots__`** (10 slots), NOT a `@dataclass(frozen=True)`.

| Property | Status |
|---|---|
| `dataclasses.is_dataclass(H3DemandSpec)` | False |
| New attribute blocked at runtime (via `__slots__`) | ✓ |
| Existing slot values mutable | ✗ (mutation succeeds at runtime) |

**Doc-fix applied in this commit:**
- L12 README + `T3_Isolated_Validation/README.md` (contract row 13) corrected to "slot-restricted, not frozen"

**Engine-side hardening recommendation (DEFERRED):**
- Migrate to `@dataclass(frozen=True, slots=True)` for true immutability at no memory cost (Python 3.10+).
- **NOT IN SCOPE for this commit** per repo boundary: The Paper does not modify engine code.
- Flagged as item for next cross-paper engine PR.

## Reports

- [`L12_summary.md`](L12_summary.md) — full audit + per-sub-test results + L12.3 detail
- [`L12_audit.json`](L12_audit.json) — programmatic audit output

## Reproducibility

Audit script: `../_infra/audit_scripts/h3_api_audit.py`.
Re-run: `python3 _infra/audit_scripts/h3_api_audit.py`

Audit is byte-deterministic against engine source; STATIC PASS holds as long as `extractor.py`, `__init__.py`, and `contracts/dataclasses/__init__.py` are unchanged.

## Out of scope

This layer tests T³'s **functional contract only**. No cognitive/listener data; no downstream layer; no system-level claim. See `../README.md` for the full out-of-scope list.
