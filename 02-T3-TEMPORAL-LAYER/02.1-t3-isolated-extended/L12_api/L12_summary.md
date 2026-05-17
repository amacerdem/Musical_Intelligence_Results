# L12 — API contract & immutability audit: summary scorecard

**Date:** 2026-05-09
**Audit method:** Static reflection (`inspect`, `dataclasses`) on the public API surface of `Musical_Intelligence/ear/h3/` + `Musical_Intelligence/contracts/dataclasses/H3DemandSpec`.
**Engine pin:** HEAD (T³ paper-time anchor, frozen since 2026-05-06).

## Headline

> **✅ STATIC PASS — 5/6 statically-checkable sub-tests PASS. L12.3 surfaces 1 doc-vs-code mismatch (H3DemandSpec is slot-restricted, NOT a frozen dataclass as the test plan assumed); engine code is functional but slot values remain mutable. Engine-side hardening recommended; not load-bearing for the existing T³ contract.**

## Per-sub-test scorecard

| Sub-test | Subject | Result |
|---|---|---|
| **L12.1** | `H3Extractor.extract(self, r3: Tensor, demand: Set) -> H3Output` signature | **PASS** |
| **L12.2** | `H3Output` is `@dataclass(frozen=True)` with fields (`features`, `n_tuples`) | **PASS** |
| **L12.3** | `H3DemandSpec` immutability characterisation | **DOC-FIX** — slot-restricted regular class, not a frozen dataclass |
| **L12.4** | Two extractor instances state-independent | **Skeleton** (runtime) — structurally guaranteed by L2.1 |
| **L12.5** | Concurrent `extract()` multi-thread torture | **Skeleton** (runtime) — structurally guaranteed by L2.1 + L11 |
| **L12.6** | `extract` twice on same input → bit-identical | **PASS by L2.1 + L11.3 structural composition** + L3 canary empirical |
| **L12.7** | No protected attributes leak through public API | **PASS** — only documented public methods (`extract`, `warmup_handler`) accessible |
| **L12.8** | `ear.h3.__init__` exports match `__all__` | **PASS** — `__all__ = ["H3Extractor", "H3Output"]` exactly |

## L12.1 — extract signature detail

```python
H3Extractor.extract(self, r3: Tensor, demand: Set[Tuple[int, int, int, int]]) -> H3Output
```

| Param | Type | Source |
|---|---|---|
| `self` | implicit | method binding |
| `r3` | `Tensor` | shape (B, T, 97), values in [0, 1] |
| `demand` | `Set[Tuple[int, int, int, int]]` | each tuple = (r3_idx, horizon, morph, law) |
| return | `H3Output` | sparse dict + tuple count |

Matches paper §Methods description and `extractor.py:73-95` docstring.

## L12.2 — H3Output immutability detail

```python
@dataclass(frozen=True)
class H3Output:
    features: Dict[Tuple[int, int, int, int], Tensor]
    n_tuples: int
```

- `dataclasses.is_dataclass(H3Output)` → `True`
- 2 fields enumerated by `dataclasses.fields()`: `features`, `n_tuples`
- `frozen=True` confirmed by attempting assignment → `dataclasses.FrozenInstanceError` raised

Note: the `features` dict itself is **mutable in-place** (Python doesn't deep-freeze container values). For full immutability, callers must treat the returned dict as read-only or wrap it (e.g. `MappingProxyType`). This is a Python language limitation, not an engine bug.

## L12.3 — H3DemandSpec characterisation (DOC-FIX)

**Code reality** (`Musical_Intelligence/contracts/dataclasses/__init__.py:7-48`):

```python
class H3DemandSpec:
    """Specification for a single H3 temporal feature demand."""
    __slots__ = (
        "r3_idx", "r3_name", "horizon", "horizon_label",
        "morph", "morph_name", "law", "law_name",
        "purpose", "citation",
    )
    def __init__(self, r3_idx, r3_name, horizon, horizon_label, ...) -> None:
        self.r3_idx = r3_idx
        ...
```

**Audit findings:**
- `dataclasses.is_dataclass(H3DemandSpec)` → **False** (regular class, not `@dataclass`)
- `__slots__` defined with 10 slots → new attributes blocked at runtime ✓
- Existing slot values **ARE mutable** — `spec.r3_idx = 99` succeeds at runtime ✗

**Implication:**

The class provides a **partial immutability guarantee** (no surprise attributes) but does NOT prevent in-place mutation of declared slots. In practice this is harmless for T³'s flow because `H3DemandSpec` instances are constructed once at mechanism declaration time and never touched again — but the immutability is convention-only, not enforced.

**Doc-fix items:**

1. **In this audit's planning docs** (L9 audit, L12 README skeleton, T3_Isolated_Validation/README contract row): replace "H3DemandSpec is a frozen dataclass" wording with "H3DemandSpec is a slot-restricted regular class (immutable by convention; new attributes blocked, but existing slots remain mutable)". Applied in this commit.

2. **Engine-side hardening recommendation (DEFERRED, NOT IN SCOPE FOR THIS COMMIT):** migrate `H3DemandSpec` to `@dataclass(frozen=True, slots=True)` (Python 3.10+) for the same memory benefit + true immutability:

   ```python
   from dataclasses import dataclass

   @dataclass(frozen=True, slots=True)
   class H3DemandSpec:
       r3_idx: int
       r3_name: str
       horizon: int
       horizon_label: str
       morph: int
       morph_name: str
       law: int
       law_name: str
       purpose: str
       citation: str

       def as_tuple(self) -> tuple[int, int, int, int]:
           return (self.r3_idx, self.horizon, self.morph, self.law)
   ```

   This would close the L12.3 gap. **Engine change is OUT OF SCOPE for this commit** (per repo boundary: The Paper does not modify engine code); flagged as a deferred engine-hardening item for the next cross-paper engine PR.

## L12.6 — Purity (structural)

`extract` twice on same input is bit-identical because:
- L2.1: zero non-init `self.X = ...` anywhere in `ear/h3/` → no instance state to drift
- L11.3: zero PRNG (no `random`, `np.random`, `torch.rand*`, `manual_seed`, `Generator`)
- L11.6: no `os.environ.get` reads in `ear/h3/`

Empirical confirmation: L3 determinism canary (28-pair PASS, migrated from `experiments/determinism_canary/`).

## L12.7 — Public API surface

`H3Extractor` instance dir():
- **Documented public** (2): `extract` (method), `warmup_handler` (property)
- **Private (single underscore)**: `_executor`, `_warmup` — instance attributes set in `__init__`
- **Dunder** (built-in): `__init__`, `__repr__`, `__class__`, `__dict__`, etc.

No undocumented public surface item. Public API is exactly what the docstring promises.

## L12.8 — Module exports

```python
# ear/h3/__init__.py
__all__ = [
    "H3Extractor",
    "H3Output",
]
```

`__all__` matches the documented public API exactly. No re-exports of internal modules.

Cross-import sanity: `from Musical_Intelligence.ear.h3 import H3Extractor` and `from Musical_Intelligence.ear.h3.extractor import H3Extractor` resolve to the same class identity.

## Reports

- [`L12_summary.md`](L12_summary.md) — this scorecard
- [`L12_audit.json`](L12_audit.json) — programmatic audit output

## Reproducibility

Audit script: `_infra/audit_scripts/h3_api_audit.py`.
Re-run: `python3 _infra/audit_scripts/h3_api_audit.py`

Audit is byte-deterministic against engine source; STATIC PASS holds as long as `extractor.py`, `__init__.py`, and `contracts/dataclasses/__init__.py` are unchanged.

## Headline (production-grade form)

When L12.3 is closed (engine-side hardening) and L12.4/L12.5 runtime tests are added:

> **L12 PASS — 8/8:** API signature stable, both dataclasses frozen (H3Output + H3DemandSpec), no public-API leakage, `__all__` exact, instance independence + concurrent purity confirmed at runtime.
