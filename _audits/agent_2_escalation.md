# Agent 2 — escalation queue

**Scope:** F2 (Prediction) + F3 (Attention) mechanisms + beliefs
**Total constants audited:** 3,607
**Escalation count:** **0**

---

## §1 Status

Zero escalations in F2/F3 scope.

All 3,607 constants resolved at HIGH confidence under the conservative attribution doctrine:
- 2,282 STRUCTURAL (C) — tensor coordinates, declared metadata, citation years
- 160 IDENTITY-PLACEHOLDER (D) — clamp endpoints, unit-interval midpoints
- 1,165 ENGINEERING-CHOICE (E) — mixer weights, predict-equation coefficients, RegionLink weights
- 0 LIT-VERBATIM (A) / LIT-DERIVED (B) / HAND-SPECIFIED-DISCLOSED (F) / DEAD-CODE (G)

---

## §2 Why no escalations

The escalation queue protocol (§8) triggers on:
1. LOW confidence
2. Ambiguous functional role / multiple competing categories
3. Web search NEGATIVE on a claimed LIT attribution

In F2/F3 scope:
1. **No LIT candidates.** No constant in F2/F3 was a candidate for LIT-VERBATIM / LIT-DERIVED at the constant level. The 500/200/110 ms timescale values from de Vries-Wurm 2023 appear ONLY in docstrings/comments, not as runtime numeric literals. The actual ms-value ladder lives in `ear/h3/constants/horizons.py` (Agent 4 scope, where it was tagged B LIT-DERIVED with PARTIAL verification + escalation).
2. **No category ambiguity.** Every constant fits cleanly into one bucket per the well-defined kind / value-pattern rules:
   - `spec-numeric-posarg{2,3,4}` (H3DemandSpec horizon/morph/law args) → STRUCTURAL
   - `link-weight-posarg*` (RegionLink edge weights) → ENGINEERING E4 (per context_brief §7-3)
   - `citation-call-posarg1` (Citation year) → STRUCTURAL
   - `module-assign` int 0..96 (R³ feature index alias) → STRUCTURAL
   - `module-assign` tuple (H³ tuple key) → STRUCTURAL
   - `_W_*` predict-equation coefficient → ENGINEERING E4
   - `TAU` belief persistence → ENGINEERING E5
   - `BASELINE = 0.5` → IDENTITY (unit-interval midpoint)
   - `BASELINE != 0.5` → ENGINEERING E5
   - `expr-literal` 0/1/-1 → IDENTITY
   - `expr-literal` 0.0/1.0/-1.0 → IDENTITY (clamp endpoint / inversion)
   - `expr-literal` 0.5 in baseline ctx → IDENTITY; 0.5 in mixer ctx → ENGINEERING E4
   - `expr-literal` other float → ENGINEERING E4 (mixer weight)
   - `expr-literal` int >= 2 → STRUCTURAL (shape/dim/index bound)
   - `call-kw` with `confidence_range` / `evidence_tier` → STRUCTURAL
   - `call-kw` ε floor (< 1e-3) → ENGINEERING E1
3. **No web search NEGATIVE on a claimed attribution.** No A/B attributions claimed, so no search to fail.

---

## §3 Special-handling notes (NOT escalations)

These deserve mention for reconciliation but did not trigger LOW confidence:

### §3.1 HTP-E3 / SPH-E3 multiplicative composition (`e3 = (e0 * e2).clamp(0, 1)`)

- File / line: `brain/functions/f2/mechanisms/htp/extraction.py:104` and `brain/functions/f2/mechanisms/sph/extraction.py:104`.
- AST walker captured NO constants on these specific lines (the clamp 0/1 literals on `.clamp(0, 1)` were not enumerated as named-position constants).
- Per protocol's HTP-E3 / SPH-E3 special-handling clause and the 2026-05-17 structural-selection-audit doc, the formula SHAPE `(e0 * e2)` is a STRUCTURAL two-candidate discrete model selection (literature-anchored on de Vries-Wurm 2023 / Bonetti 2024), not a numeric calibration. The AST walker correctly captured zero load-bearing constants on these lines.
- Defensive: if any future AST walker captures the clamp 0/1 here, the classifier's `is_htp_e3` / `is_sph_e3` branch will tag them D IDENTITY with explicit annotation about the structural-selection context.

### §3.2 RegionLink edge weights (universally tagged E4)

- 131 RegionLink calls across F2 + F3 mech `__init__.py` files (e.g. `RegionLink("E0:high_level_lead", "AG", 0.80, "de Vries & Wurm 2023")`).
- Per context_brief §7-3 doctrine: the citation grounds the EDGE EXISTENCE (i.e. that an AG↔HTP-E0 link is supported by the cited paper), but the numeric weight (0.80) is author-normalized Likert-style scaling — no paper publishes "AG ↔ HTP-E0 = 0.80".
- Tagged uniformly as **E ENGINEERING E4 mixer** with PARTIAL verification outcome and HIGH confidence. Reconciliation note: Agent 5 (RAM/NeuroLink) will treat the same way for the master 529-RegionLink corpus.

### §3.3 Citation years and confidence_range tuples

- All `Citation(_, YEAR, ...)` positional-year args (99 in scope) tagged **C STRUCTURAL** (bibliographic metadata).
- All `confidence_range=(low, high)` tuples on ModelMetadata (22 in scope, one per mech) tagged **C STRUCTURAL** declared evidence-tier metadata. These are author-declared qualitative confidence bands, not empirical values.

### §3.4 TAU vs F category boundary

- `TAU = 0.40` (or 0.35, 0.40, 0.45, 0.50 depending on belief) appears in ~36 Core beliefs across F2/F3.
- Per context_brief §3 doctrine, `τ` is explicitly NOT in the F-list of 7 reward weights: F is restricted to `w_S=1.5, w_R=0.8, w_E=0.5, w_M=-0.6, phi_fam_star=0.5, g_DA_wanting=0.6, g_DA_liking=0.4` in `brain/reward.py`.
- All TAU constants in F2/F3 tagged **E ENGINEERING E5** (predict-equation persistence operational scaling, NOT F).
- This is the canonical pilot-flagged razor-sharp boundary from Agent 4 summary §3 — Agent 2 respected it strictly.

---

## §4 What Agent 6 reconciliation should verify

1. **F count = 0 in F2/F3 scope.** Correct per protocol §12.6 — F lives only in `brain/reward.py` (Agent 3 scope, F6).
2. **Citation year metadata category consistency.** Agent 2 = C; verify Agent 1, 3, 4, 5 also use C for citation years.
3. **RegionLink weight category consistency.** Agent 2 = E4 with PARTIAL verification + HIGH confidence; verify Agent 5 (RAM owner) uses identical attribution for the same edges where they overlap.
4. **Predict-equation coefficients consistency.** Agent 2 = E4 / E5 (never F); verify Agent 1 (F1 + F2 overlap), Agent 3 (F6/F7/F8 beliefs) use identical attribution.

No expected conflicts.

---

## §5 Honest negative

Agent 2's audit produced **0% LIT-VERBATIM and 0% LIT-DERIVED in F2 + F3 scope**. This is the honest empirical finding under the conservative-attribution doctrine. It is fully consistent with:
- Agent 4 pilot's expectation for Agent 2 (~3-7% LIT projected; the under-shoot is because F2 + F3 is mechanism-heavy and predict-equation-heavy, while the original protocol projection envisioned Agent 2 covering F3 + F4 + F5 where F4 memory might carry more literature anchors).
- Context_brief §5 anticipation (constant-level rate ~5-15% across engine; F2 + F3 at 0% sits at the low end but well within the band — the 14,000 C³ constants overall are "mostly ENGINEERING-CHOICE + HAND-SPECIFIED-DISCLOSED, with named anchor constants like Salimpoor BP_ND = 0.78/0.88/0.35 and Aston-Jones NE = 0.50/0.75 as LIT-VERBATIM islands" — those islands are in F6 (reward) and the neurochem channels, NOT in F2 or F3).
- Context_brief §7 risk areas — risk 1 (BCH/PNH mixer over-attribution), risk 2 (HTP-E3/SPH-E3 structural HYBRID), risk 5 (Berlyne 4x(1-x) kernel), risk 7 (KK profiles), risk 8 (R³ sigmoid wrappers) — NONE of these are in F2/F3 scope. F2/F3 is downstream of those LIT-bearing layers; it consumes R³/T³ via STRUCTURAL indices and blends them via ENGINEERING mixers.

The zero-LIT result is **not** evidence of under-attribution; it is the audit's correct finding under per-constant independence and conservative attribution.
