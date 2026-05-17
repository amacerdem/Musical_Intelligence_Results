# `_infra/c3_panel_shared/` — Cross-segment utilities

Shared Python utilities used by all three C³ evidence segments:

- `C3-Cognitive-Signals/`
- `C3-Region/`
- `C3-Neurochemicals/`

Each segment imports from this package; nothing in this package depends on a specific segment.

## Planned files

| File | Responsibility |
|---|---|
| `engine_pin_check.py` | Assert engine SHA matches `Musical_Intelligence_Outputs/_build/_engine_pin.json` before any analysis runs. First call of every script. |
| `load_outputs.py` | Read `pooled.csv`, `pooled_pct.csv`, `targets.csv`, and (where built) per-rater long tables from `Musical_Intelligence_Outputs/<category>/<dataset>/`. Returns typed DataFrames. |
| `stats_core.py` | BH–FDR; Fisher-Z combination; label-permutation null; hierarchical Benjamini–Bogomolov FDR for cross-segment aggregation. |
| `prereg_validator.py` | JSON-schema validator for the immutable `data/<dataset>/prereg_*.json` files. Halts on any post-hoc edit attempt. |

## Status

**SCAFFOLD ONLY** — files are not yet implemented. Analysis scripts in the three segments will be written once the dataset cache is fully validated.

## Engine pin

All scripts in all three segments MUST call `engine_pin_check.assert_pinned_sha()` as their first action.

Current pin: SHA `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88` (engine commit `318eb2f5`).

A mismatch halts execution. The pin is **frozen** — never edit it from a script.

---

## Per-dataset join contracts

`pooled.csv` and `targets.csv` may use different `clip_id` schemes per dataset. `load_outputs.py` owns the canonical join rule for every dataset; no analysis script reimplements join construction. As of 2026-05-11:

### emotify

- `pooled.csv` clip_id: `<genre>_<stem>` with `<stem>` 1..100 within each of 4 genres (`classical`, `rock`, `electronic`, `pop`)
- `targets.csv` clip_id: global `int64` 1..400, partitioned with offsets:

```python
EMOTIFY_GENRE_OFFSET = {"classical": 0, "rock": 100, "electronic": 200, "pop": 300}
```

`load_outputs.load_emotify_joined(...)` constructs `clip_id_join = f"{genre}_{clip_id - offset}"` on the targets side and returns a fully joined DataFrame with exact 400 / 400 overlap. Naïve `pd.merge(on='clip_id')` raises `ValueError` (object vs int64) — loud fail-fast.

Full rule + verification documented in `C3-Cognitive-Signals/data/emotify/README.md §Join-key contract`.

### Future datasets

Each new dataset adds a `load_<dataset>_joined(...)` helper here. The function name signals the dataset-specific join rule lives in one place. Per-dataset README files reference this helper.
