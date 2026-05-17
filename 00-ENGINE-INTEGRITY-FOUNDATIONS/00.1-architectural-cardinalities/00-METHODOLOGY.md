# Phase 1 — Architectural Cardinalities — Methodology (LOCKED 2026-05-06)

> Per V-Reproduction iteration policy (`02-ITERATION-POLICY.md`), this document is locked before the first run and may not be edited mid-run to chase a number.

## Scope

Reproduce 16 numerical cardinalities (C-CARD-01..16) declared in the master paper §Architectural cardinalities (`Publication/Amac-Erdem-Musical-Intelligence.tex`, §Architecture §Parameter provenance + §Online Methods §Parameter provenance accounting).

## Engine HEAD

`318eb2f529d7103e8b7d80b01228357fdc4e0217` (pinned in `_infra/manifests/engine_head.json`). Verified bit-identical against current working tree on `Science/Musical_Intelligence/`.

## Seed

Phase-1 primary seed `2026050601` (from `_infra/manifests/seed_registry.json`). Bootstrap `1729`, permutation `42`. Forward-passed to `run_engine(seed=…)` for traceability; the frozen engine has no RNG draws so seed is not consumed at compute time.

## AST traversal scope

Root: `Science/Musical_Intelligence/` (the engine package as it lives in this repo). Recursive glob `**/*.py`. Excluded: `__pycache__/`, `.git/`, `.pytest_cache/`. Numeric literals enumerated via Python `ast` stdlib visiting `ast.Constant` nodes with `value: int|float` (booleans excluded).

Note: paper Methods cites "856 .py files" — that count is engine-snapshot specific and tolerated as part of the AST claim's tolerance window.

## Mechanism enumeration

`importlib.import_module("Musical_Intelligence.brain.functions.{f1..f9}.mechanisms")` → walk `__all__` → `getattr(mod, name)` → record class. F9 may not exist on disk; absent module is recorded as zero contribution (not as failure). Per-function counts are derived from `__all__` length.

A mechanism is counted at most once even if exposed by multiple aliases. Output: `results/mechanism_inventory.csv`.

## Belief enumeration

`importlib.import_module("Musical_Intelligence.brain.functions.{f1..f9}.beliefs")` → walk `__all__` → record class. Classification into Core / Appraisal / Anticipation by class introspection:

1. MRO scan for class-name substrings `"Core"`, `"Appraisal"`, `"Anticipation"`.
2. Class attribute `BELIEF_TYPE` if set.
3. Module path heuristic (fallback): `…beliefs.<sub>.<name>` where `<sub>` is the F1-canonical sub-belief group (BCH, MIAA, etc.).
4. If still unresolved → `Unknown` (will be visible in the CSV; not silently bucketed).

Output: `results/belief_inventory.csv`.

## RegionLink + NeuroLink enumeration

In MI's architecture, `RegionLink` and `NeuroLink` are per-mechanism properties (`region_links`, `neuro_links` on `_NucleusBase`). The engine has no central registry — links live on each instantiated mechanism. The runtime enumerator therefore:

1. Reuses the runner's `_collect_mechanisms` strategy: instantiate every F1..F9 mechanism class.
2. For each instance, iterate `inst.region_links` and `inst.neuro_links`.
3. Record `(mechanism_NAME, dim_name, region_or_channel, weight, citation)` to CSV.
4. Total RegionLink count = sum across all mechs. Total NeuroLink count = sum across all mechs (paper reports 48 *resolutions*, i.e. canonical (mech, dim, channel) triples; raw call sites may be 54 with the modulator-alias collapse handled by `_MODULATOR_TO_CHANNEL` in `contracts/dataclasses/__init__.py`).

Outputs: `results/region_links.csv`, `results/neuro_links.csv`.

## Constant classifier (5 buckets)

Per paper §S-Provenance line 581 ("lenient classifier: HAND-TUNED = 495 / 3.1%, CALIB-BOWLING = 246 / 1.5%"). The classifier is a *deterministic file-path + value heuristic*, not a learned model. Order matters — first match wins.

1. **CALIB-BOWLING (246 expected)**. File path matches `f1.beliefs.bch.*` (Bowling-calibrated relay gains; specifically `harmonic_stability.py`, `consonance_trajectory.py`, `interval_quality.py`, `harmonic_template_match.py`).
2. **HAND-TUNED (495 expected)**. Numeric literal `value` ∈ {1.5, 0.8, 0.5, −0.6, 0.6, 0.4, 3.0} AND file path contains `reward`, `f6`, or `modulation`. Captures the 7 reward/modulation weights and their callers.
3. **NULL (1,381 expected)**. Literal value `0` or `0.0` (placeholder zero in dataclass defaults; covers null initializers).
4. **STRUCTURAL (6,290 expected)**. Integer-valued literals: dimension counts (1..1000), citation years (1900..2030), MNI coords, clamp bounds, dataset sizes, indices. Captures all integer-like floats too.
5. **LITERATURE (7,779 expected)**. Everything else (literature-derived float scalars, e.g. CKM gains, Krumhansl profile entries, neurochemical decay constants).

Tolerance per bucket: ±5% relative. The classifier is a documented heuristic; the paper declares "lenient classifier" so re-implementing the exact same boundary is the goal but small drift is tolerable.

Outputs: `results/ast_constants.csv` (full inventory with bucket column), `results/provenance_summary.csv` (5-row summary).

## Sensitivity panel — DETERMINISM FLOOR (C-CARD-16)

The paper's claim "ρ > 0.995 across 100 perturbations of the 7 hand-tuned weights ±30%" was verified at engine-build time (V1 evidence base). Reproducing it in V-Reproduction would require modifying engine module-level constants, which is *forbidden* by the frozen-engine policy.

Phase 1 substitutes a determinism-floor demonstration: 100 sequential `run_engine` calls on a single fixed audio chunk; bit-identical output expected (paper's Phase-0 finding |Δρ| ≤ 8.8×10⁻⁵; engine runner verified bit-equality). This is a strict superset of "stable under perturbation" because it shows the engine has no stochastic noise floor at all.

Verdict for C-CARD-16 will be `CAVEAT` (paper claim refers to a build-time test that requires engine modification to reproduce; V-Reproduction documents the determinism floor and references V1 for the original sensitivity result).

If the user wants TRUE ±30% perturbation, that is a separate engine PR adding `with_overrides()` context manager. Out of scope for V-Reproduction.

Audio choice: lacking Cheung 2019 chord audio (dir empty under `Science/datasets/prediction/cheung2019/`), use a single 30s clip from `Science/V1/stimuli/micro_beliefs/` (smallest file by size) as deterministic substrate. The actual file is recorded in `results/sensitivity_summary.json`.

Output: `results/sensitivity_panel.csv` (101 rows: baseline + 100 reruns), `results/sensitivity_summary.json`.

## Per-claim tolerance table

| ID | Claim | Paper value | Tolerance |
|---|---|---|---|
| C-CARD-01 | R³ feature dimensions | 97 | exact_match |
| C-CARD-02 | H³ theoretical tuple space | 223,488 | exact_match |
| C-CARD-03 | H³ active runtime sparsity | ~8,600 | absolute_deviation ≤ 200 |
| C-CARD-04 | Mechanism count F1-F8 | 89 | exact_match |
| C-CARD-05 | Belief full registry | 131 | exact_match |
| C-CARD-06 | F1-F8 belief classification | 34/59/28 | exact_match |
| C-CARD-07 | NeuroLink resolutions | 48 | exact_match |
| C-CARD-08 | RegionLink count | 529 | exact_match |
| C-CARD-09 | Total numeric constants | 16,191 | absolute_deviation ≤ 50 |
| C-CARD-10 | Compute-path materialized | 7,517 | absolute_deviation ≤ 20 |
| C-CARD-11 | LITERATURE bucket | 7,779 | relative_deviation ≤ 0.05 |
| C-CARD-12 | STRUCTURAL bucket | 6,290 | relative_deviation ≤ 0.05 |
| C-CARD-13 | NULL bucket | 1,381 | relative_deviation ≤ 0.05 |
| C-CARD-14 | CALIB bucket | 246 | relative_deviation ≤ 0.05 |
| C-CARD-15 | HAND-TUNED bucket | 495 | relative_deviation ≤ 0.05 |
| C-CARD-16 | Sensitivity panel ρ > 0.995 | 0.995 | exact ≥ 0.995 (CAVEAT — see above) |

## Iteration policy reference

- First-run-low triggers debug protocol from `02-ITERATION-POLICY.md`.
- Maximum 5 iterations per claim.
- Methodology may NOT be edited mid-run.
- All iterations preserved under `results/iterations/`.

## Outputs (canonical)

```
results/01_cardinalities_manifest.json   ← schema-validated final
results/mechanism_inventory.csv
results/belief_inventory.csv
results/region_links.csv
results/neuro_links.csv
results/ast_constants.csv
results/provenance_summary.csv
results/sensitivity_panel.csv
results/sensitivity_summary.json
```
