# L9 — Constant provenance audit (zero-calibration claim)

> **Status:** **POPULATED** (2026-05-09) — full provenance traced via AST walk + per-constant audit + git-history scan. See `L9_summary.md` for headline scorecard.

## Paper claim being defended

*Every numeric constant in `ear/h3/` is either (i) a literature value from a named publication or (ii) an engine-internal scaling fixed at definition time. No constant adjusted against human-rated data.*

## Audit results (PASS)

> **All 130 enumerated numeric values in `ear/h3/` are traceable to specification documents, literature operators, or engine-internal scaling formulas. Zero commits change a constant in correlation with a cognitive-rating rerun.**

| Sub-test | Subject | Result |
|---|---|---|
| **[L9.1](L9.1_inventory.md)** | AST inventory of all module-level numeric constants in `ear/h3/` | **PASS** — 25 declarations, 130 enumerated values across 6 files |
| **[L9.2](L9.2_kernel.md)** | Kernel constant `ATTENTION_DECAY = 3.0` (`exp(-3·(1-p))`) | **PASS** — single literature/spec-derived constant, sets `exp(-3) = 5%` boundary attenuation and `exp(3) ≈ 20.09` newest:oldest ratio |
| **[L9.3](L9.3_horizons.md)** | Horizon-scale constants (`N_HORIZONS`, `HORIZON_MS`, `HORIZON_FRAMES`, `FRAME_RATE`, `BAND_RANGES`) | **PASS** with doc-fix flag (strict-log → log-coverage wording at L14) |
| **[L9.4](L9.4_morphs.md)** | Morph parameter constants (`MORPH_NAMES`, `MORPH_MIN_WINDOW`, `MORPH_CATEGORIES`, `SIGNED_MORPHS`, `MORPH_SCALE`) | **PASS** — 86 values, all literature operators or analytical-max scalings |
| **[L9.5](L9.5_laws.md)** | Causal-law constants (`N_LAWS`, `LAW_*`, `LAW_NAMES`) | **PASS** — 9 values, specification enumerations only |
| **[L9.6](L9.6_negative_claim_audit.md)** | Negative-claim audit (git-log scan for cognitive-rerun-correlated changes) | **PASS** — 0/8 commits change a constant in correlation with cognitive reruns |

## Provenance class distribution

| Class | Count | Examples |
|---|---|---|
| Specification choice (cardinality, naming, partition) | ~50 | `N_HORIZONS=32`, `N_MORPHS=24`, `LAW_NAMES`, `BAND_RANGES`, `MORPH_CATEGORIES` |
| Literature-derived operator | ~24 | `MORPH_NAMES` (Fisher moments, Box-Jenkins autocorr, Shannon entropy) |
| Engine-internal scaling (analytical max on bounded inputs) | ~24 | `MORPH_SCALE` (each value = analytical max on [0,1] R³ inputs) |
| Engine-internal derivation (from R³ / spec) | ~3 | `FRAME_RATE = 44100/256`, `_THEORETICAL_SPACE = 97×32×24×3` |
| Specification choice with documented rationale | 1 | `ATTENTION_DECAY = 3.0` |

**Calibrated against human-rated data: 0.**

## Constants/ folder freeze status

All 5 files in `ear/h3/constants/` (`horizons.py`, `laws.py`, `morphs.py`, `scaling.py`, `__init__.py`) **untouched since their initial commit**. Future L9 audit cycles only need to re-run when this folder is modified.

## Forwarded to L14 (doc-consistency)

1. **Strict-log claim wording.** `T3-Paper/T3_Isolated_Validation/README.md` (L16, L38) and master MI paper (L410) say "32 logarithmically-spaced horizons" — strictly the spacing is *log-coverage organised in four perceptual bands* with band-boundary gaps. L14 should rewrite this language.

2. **`HORIZON_FRAMES` derivation formula** (`horizons.py:74-76`) is correct in comment but should have an explicit assertion test in L1_spec_compliance.

## Reports format

- `L9.1_inventory.md` + `L9.1_inventory.json` — full AST-walked constants table
- `L9.{2,3,4,5,6}_*.md` — per-area provenance audit with verdict
- `L9_summary.md` — aggregated scorecard

## Out of scope

This layer tests T³'s **functional contract only**. No cognitive/listener data; no downstream layer; no system-level claim. See `../README.md` for the full out-of-scope list.

## Engine pin

Audit run against engine HEAD per `Science/V-Reproduction/_infra/manifests/engine_head.json` at the time of the 2026-05-09 audit.
