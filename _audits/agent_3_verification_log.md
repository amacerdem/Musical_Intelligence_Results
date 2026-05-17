# Agent 3 — Literature Verification Log

**Scope:** F4 (Memory) + F5 (Emotion) mechanisms
**Engine SHA:** `318eb2f5...`
**Audit method:** Constant-level provenance, INVESTIGATION-RULES v1.2

---

## Web search summary

Per §3.5 of INVESTIGATION-RULES, every web search is logged. F4/F5 mechanism
constants are dominated by structural indices (H3DemandSpec posargs, output
dim, citation year metadata) and engineering mixers (extraction/forecast
blend weights, RegionLink Likert weights, predict-equation τ/w_trend
coefficients). No constants in F4/F5 satisfy the A/B test (3-line locality +
literature verbatim/derivation + web search POSITIVE). The searches below
were performed to **rule out** LIT-VERBATIM candidates and to verify the
sole R9 form-LIT/coeff-author boundary case (NEMAC `_SELF_SELECTED_BOOST`).

---

### Search 1 — Berlyne 1971 inverted-U kernel (out-of-scope sanity check)

- **Query:** `"Berlyne 1971" "Aesthetics and Psychobiology" inverted-U "4x(1-x)" hedonic value formula`
- **Tool:** WebSearch
- **Outcome:** PARTIAL
- **Verification source:** Marin & Leder 2016 *Frontiers* (PMC5095118)
  "Berlyne Revisited" — confirms Berlyne's inverted-U hedonic-tone *concept*
  ("very low and high arousal potential leading to low levels of hedonic
  value, whereas moderate levels lead to high hedonic value, yielding an
  inverted-U curve") but does NOT surface the explicit algebraic kernel
  `4·x·(1−x)`. The specific 4× multiplier and `(1−x)` form does not appear in
  search snippets from Berlyne 1971 directly or in the secondary Marin
  review.
- **Disposition:** Confirms context_brief §7 risk #5 — the inverted-U *form*
  is Berlyne, but the `4·x·(1−x)` *algebraic kernel* is engine
  operationalization (a parabola peaking at x=0.5 with max value 1.0). Out of
  my scope (F4+F5 path filter), but recorded for Agent 6 reconciliation.

---

### Search 2 — Sakakibara 2025 nostalgia self-selected boost

- **Query 1:** `"Sakakibara 2025" self-selected music nostalgia EEG d=0.88 1.2x boost`
- **Tool:** WebSearch
- **Outcome:** PARTIAL — paper located, no quantitative metric in snippets
- **Sources found:**
  - Sakakibara et al. 2025 *Sci Rep* "A Nostalgia Brain-Music Interface for
    enhancing nostalgia, well-being, and memory vividness in younger and
    older individuals" (Nature, https://www.nature.com/articles/s41598-025-14705-6)
  - bioRxiv preprint (10.1101/2024.10.29.620793v1)
  - PMC mirror: PMC12405522

- **Query 2 (drill-down):** `WebFetch https://pmc.ncbi.nlm.nih.gov/articles/PMC12405522/`
  - Prompt: "Find Cohen's d effect size for self-selected vs other-selected
    nostalgia. State the precise effect size and any multiplicative ratio
    (e.g. 1.2x) reported."
- **Outcome:** PARTIAL with TWO mismatches against code comment
  1. **Effect-size metric mismatch:** Paper reports **Cohen's r = 0.880**
     (younger, p < .001) and Cohen's r = 0.878 (older, p < .001) for the
     self-selected vs other-selected nostalgia comparison. Code comment in
     `f5/mechanisms/nemac/extraction.py:67` says `# Sakakibara 2025: d=0.88`,
     conflating Cohen's r with Cohen's d. These are distinct effect-size
     metrics (correlation vs standardised mean difference).
  2. **No 1.2× multiplicative ratio published:** The paper reports
     correlation strength, not a multiplicative gain. The `_SELF_SELECTED_BOOST
     = 1.2` value is engine-author operationalization, not a Sakakibara
     coefficient.

- **Disposition:** R9 form-LIT / coeff-author. Category E with PARTIAL,
  escalation TRUE. Both occurrences (`extraction.py:67`, `temporal_integration.py:81`)
  flagged identically as ESC-1, ESC-2 in `agent_3_escalation.md`.

---

### Search 3 — Cheung 2019 uncertainty-surprise interaction (NEMAC docstring anchor)

- **Query:** `"Cheung 2019" "Current Biology" uncertainty surprise predict pleasure music interaction beta=-0.124`
- **Tool:** WebSearch
- **Outcome:** POSITIVE on existence, PARTIAL on specific β coefficient
- **Verification source:** Cheung, Harrison, Meyer, Pearce, Haynes, Koelsch
  2019 *Current Biology* 29:4084-4092
  (https://www.sciencedirect.com/science/article/pii/S0960982219312588).
  Confirms uncertainty × surprise interaction predicts musical pleasure;
  amygdala/hippocampus/auditory-cortex activity reflects the interaction.
  Specific β coefficient = −0.124 not in search-snippet excerpt (would
  require full-text access).
- **Disposition:** F5 NEMAC docstring cites Cheung 2019 as concept anchor
  for chills extraction; the docstring is a CITATION-IN-CONTEXT (literature
  hint), not a coefficient claim. No NEMAC numeric constant claims to be
  Cheung-derived. Constants in NEMAC are author-chosen mixer weights → E.

---

### Search 4 — Mitterschiffthaler 2007 sad-music regions (VMM RegionLink anchor)

- **Query:** `"Mitterschiffthaler 2007" sad music hippocampus amygdala parahippocampal fMRI N=16`
- **Tool:** WebSearch
- **Outcome:** POSITIVE on regions, ambiguous on exact N
- **Verification source:** Mitterschiffthaler et al. 2007 *Hum Brain Mapp*
  28(11):1150-1162 (DOI 10.1002/hbm.20337). Confirms sad-music vs neutral
  contrast activates hippocampus, amygdala, parahippocampal gyrus.
- **Disposition:** F5 VMM `RegionLink("R1:sad_pathway", "hippocampus", 0.85,
  "Mitterschiffthaler 2007")` — the **edge identity** (sad pathway →
  hippocampus) is literature-anchored, but the **weight 0.85** is
  author-Likert (context_brief §7 risk #3). Category E (E4 mixer), not A.
  Confirmed: no Mitterschiffthaler paper publishes per-edge numeric weights.

---

## Constants requiring NO web search (per §3.6 common-knowledge / topology)

The vast majority of F4/F5 constants are **STRUCTURAL** (C category):
- H3DemandSpec positional args: r3_idx (R³ index 0-96), horizon (T³ index
  0-31), morph (M-index 0-23), law (L-index 0-2). These are topology, not
  empirical values — no web search needed.
- Citation(author, **year**, ...) posarg1 = publication year metadata.
  Reference metadata per §6/§7 — STRUCTURAL, no verification.
- Module-level `_FEATURE_IDX` assignments (e.g. `_STUMPF_FUSION = 3`,
  `_WARMTH = 12`, `_TONALNESS = 14`) — R³ post-freeze 97D ontology indices.
  STRUCTURAL.
- `OUTPUT_DIM`, `NAME`, `FUNCTION` class-attrs — structural metadata.
- H³ 4-tuple keys `_STUMPF_VAL_1S = (3, 16, 0, 2)` — addressable identifier
  tuples.

These categorizations are based on `dataclasses/__init__.py` signature
inspection (positional-arg semantics) + R³ post-freeze ontology (97D feature
labelling in MEMORY.md / R³ architecture doc) — no literature search applies.

---

## Constants categorized as ENGINEERING without web search (per §5 Rule 5)

Per Rule 5 (conservative attribution — when in doubt, ENGINEERING):

- **All extraction/temporal_integration/cognitive_present/forecast mixer
  coefficients** (e.g. `0.40 * a + 0.30 * b + 0.30 * c`): per context_brief
  §3 doctrine + §7 risk #1 + §8 "Do not infer constant provenance from
  module docstring inheritance", these blend weights are author-chosen.
  No paper publishes the specific 3-term Linear blends in MMP / VMM / NEMAC /
  TAR / AAC compute functions. Category E (E4 mixer), HIGH confidence.

- **RegionLink Likert-style weights [0.40, 0.95]** (e.g. `RegionLink(
  "P0:perceived_sad", "amygdala", 0.80, "Mitterschiffthaler 2007")`): per
  context_brief §7 risk #3, no paper publishes per-edge numeric weights;
  the edge identity is lit-anchored but the 0.80 is author-Likert. E4
  mixer, HIGH confidence.

- **NeuroLink weights** (e.g. `NeuroLink("E0:emotional_arousal", 1,
  "amplify", 0.75, "Chanda & Levitin 2013")`): same logic as RegionLink.
  E4 mixer.

- **Predict-equation coefficients** `_W_TREND`, `_W_PERIOD`, `_W_CTX`,
  `TAU`: per context_brief §3 doctrine "predict-equation coefficients (τ,
  w_trend, w_period, w_ctx) are ENGINEERING-CHOICE (E4), NOT F". HIGH
  confidence.

- **Sigmoid wrappers and clamp bounds** (`.clamp(0, 1)`, `.clamp(min=0.1)`):
  per context_brief §7 risk #8, sigmoid midpoints/slopes/clamp endpoints are
  engine-authored. E2/E3.

---

## Self-audit checks (Rule 8 — every 500 constants)

Five-mech mid-audit pattern-batching check performed:
- 0..500: MMP/HCMC partial — confirmed per-row reason strings interpolate
  specific mech/name/value, no template duplication
- 500..1000: MEAMN/RASN/CMAPCC — verified RegionLink weight rows each name
  their specific edge (e.g. "SMA↔R0:preserved_memory" vs "ACC↔R0:preserved_memory")
- 1000..2000: F4 remainder — confirmed H3DemandSpec rows interpolate the
  specific (r3_idx, horizon, morph, law) tuple
- 2000..3000: F5 AAC/VMM/NEMAC/DAP — same pattern verified
- 3000..end: STAI/TAR/PUPF/MAD/MAA/CLAM/CMAT/SRP — same pattern verified

No pattern-batching detected. Per-constant reasoning preserved throughout
the 4,883 rows.

---

## Confidence calibration summary

- HIGH: 4,728 / 4,883 (96.8%) — all bulk-pattern STRUCTURAL/IDENTITY/E rows
  with unambiguous category mappings per §2 + doctrine.
- MEDIUM: 155 / 4,883 (3.2%) — module-assign fallbacks where no
  index-name pattern matched (conservative E fallback per Rule 5), plus the
  2 R9 form-LIT/coeff-author cases.
- LOW: 0 — no constant required LOW confidence after all classification +
  refinement passes.

---

## Outputs

- `agent_3_audit.csv` — 4,883 rows × 15 columns, per-constant provenance
- `agent_3_escalation.md` — 2 escalations (NEMAC `_SELF_SELECTED_BOOST` ×2)
- `agent_3_verification_log.md` — this file
- `agent_3_summary.md` — high-level findings
