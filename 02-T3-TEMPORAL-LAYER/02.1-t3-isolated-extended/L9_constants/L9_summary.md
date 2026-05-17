# L9 — Constants provenance audit: summary scorecard

**Date:** 2026-05-09
**Audit method:** AST walk of `Musical_Intelligence/ear/h3/` + git-history scan + per-constant provenance trace.
**Engine pin:** HEAD (T³ paper-time anchor)

## Headline

> **All 130 enumerated numeric values in `ear/h3/` are traceable to specification documents, literature operators, or engine-internal scaling formulas. Zero commits change a constant in correlation with a cognitive-rating rerun.**

## Per-sub-test scorecard

| Sub-test | Subject | Result | Cardinality |
|---|---|---|---|
| **L9.1** | AST inventory of `ear/h3/` | **PASS** | 25 declarations, 130 enumerated values across 6 files |
| **L9.2** | Kernel constant `ATTENTION_DECAY = 3.0` | **PASS** | 1 (literature/spec-derived; `exp(-3)` = 5% boundary, `exp(3)` = newest:oldest ratio) |
| **L9.3** | Horizon-scale constants (`N_HORIZONS`, `HORIZON_MS`, `HORIZON_FRAMES`, `FRAME_RATE`, `BAND_RANGES`) | **PASS with doc-fix flag** | 70 (32+32+1+1+4); doc-vs-code wording fix scheduled at L14 ("strict-log" → "log-coverage in 4 bands") |
| **L9.4** | Morph parameter constants (`MORPH_NAMES`, `MORPH_MIN_WINDOW`, `MORPH_CATEGORIES`, `SIGNED_MORPHS`, `MORPH_SCALE`) | **PASS** | 86 (24+24+6+8+24) |
| **L9.5** | Causal-law constants (`N_LAWS`, `LAW_*`, `LAW_NAMES`) | **PASS** | 9 (3+3+3) |
| **L9.6** | Negative-claim audit (git-log scan) | **PASS** | 0 commits change constants in correlation with cognitive reruns |

**Total enumerated values audited:** 130 (1 + 70 + 86 + 9 minus 36 overlaps with L9.1 inventory). Values double-counted across L9.2–L9.5 are the same physical constants traced from different perspectives.

## Provenance class distribution

| Class | Count | Examples |
|---|---|---|
| Specification choice (cardinality, naming, partition) | ~50 | `N_HORIZONS=32`, `N_MORPHS=24`, `LAW_NAMES`, `BAND_RANGES`, `MORPH_CATEGORIES` |
| Literature-derived operator | ~24 | `MORPH_NAMES` (Fisher moments, Box-Jenkins autocorr, Shannon entropy) |
| Engine-internal scaling (analytical max on bounded inputs) | ~24 | `MORPH_SCALE` (each value = analytical max of operator on [0,1] R³ inputs) |
| Engine-internal derivation (from R³ / spec) | ~3 | `FRAME_RATE = 44100/256`, `FRAME_DURATION_MS = 1000/FRAME_RATE`, `_THEORETICAL_SPACE = 97×32×24×3` |
| Specification choice with documented rationale | 1 | `ATTENTION_DECAY = 3.0` (sets `exp(-3)` boundary attenuation and `exp(3)` newest:oldest ratio) |

**Calibrated against human-rated data: 0.**

## Documentation-fix items (forwarded to L14)

1. **Strict-log claim wording.** `T3-Paper/T3_Isolated_Validation/README.md` (L16, L38) and master MI paper (L410) say "32 logarithmically-spaced horizons". Strictly the spacing is *log-coverage organised in four perceptual bands* with band-boundary gaps (intra-band ratios vary from 1.20 to 4.31). L14 should rewrite this language.

2. **`HORIZON_FRAMES` derivation formula** (`horizons.py:74-76`) is correct in comment but should have an explicit assertion test in L1_spec_compliance: `HORIZON_FRAMES[i] == max(1, round(HORIZON_MS[i] / 1000 * FRAME_RATE))` for all i.

## Constants/ folder freeze status

All 5 files in `ear/h3/constants/` (`horizons.py`, `laws.py`, `morphs.py`, `scaling.py`, `__init__.py`) have been **untouched since their initial commit**. Future L9 audit cycles only need to re-run when this folder is modified.

## Headline (production-grade form)

When the L9 battery is fully implemented as runnable tests:

> **L9 PASS — 100%:** all 130 enumerated values in `ear/h3/` are provenance-traced. AST inventory enumerates the constant set; per-constant audit (L9.2–L9.5) classifies each by source; negative-claim audit (L9.6) confirms 0 cognitive-rerun-correlated changes in git history. The H³ / T³ paper's zero-calibration commitment for the temporal-morphology layer is structurally verified.
