# Agent 2 — verification log

**Scope:** F2 (Prediction) + F3 (Attention) mechanisms + beliefs
**Total constants audited:** 3,607
**Web search verifications performed:** 4

---

## §1 Web search log

### §1.1 de Vries & Wurm 2023 — hierarchical temporal prediction timescales

- **Query:** `de Vries Wurm 2023 hierarchical prediction 500ms 200ms 110ms temporal timescales`
- **Tool:** WebSearch (Google surface)
- **Outcome:** POSITIVE for the 500 / 200 / 110 ms timescale concept.
- **Source confirmation:** Paper found — "Predictive neural representations of naturalistic dynamic input" (Nat Commun 2023). Abstract excerpt explicitly states "Body motion was represented in a broad temporal window preceding the actual input by ~500 ms for view-invariant body motion, and ~200 ms for view-dependent body motion. A computer vision model capturing low-level motion as optical flow vector direction at each pixel was represented predictively at ~110 ms."
- **Impact on F2/F3 attribution:** The 500/200/110 ms timescale values appear in HTP docstrings/comments (`brain/functions/f2/mechanisms/htp/extraction.py` lines 73-95 and `__init__.py` lines 1-31) but NOT as runtime numeric literals. The values are implicitly encoded via T³ horizon indices (H0, H1, H3, H4, H8, H16) which map to durations through the T³ horizon ladder in `ear/h3/constants/horizons.py`. T³ horizon ladder is in Agent 4 scope (tagged B LIT-DERIVED PARTIAL).
- **Verification method recorded in CSV:** `websearch-google` (no F2/F3 constant claimed LIT-VERBATIM, so this verification informs ZERO CSV rows directly — it confirms the absence of bit-exact runtime instantiation).

### §1.2 Bonetti 2024 — feedforward auditory cortex → hippocampus → cingulate

- **Query:** `Bonetti 2024 feedforward auditory cortex hippocampus cingulate gamma alpha beta`
- **Tool:** WebSearch (Google surface)
- **Outcome:** POSITIVE for the feedforward pathway and gamma vs alpha-beta dissociation concept.
- **Source confirmation:** Paper found — "Spatiotemporal brain hierarchies of auditory memory recognition and predictive coding" (Nat Commun 2024, DOI 10.1038/s41467-024-48302-4). MEG N=83. Article describes feedforward connections originating from auditory cortices and extending to hippocampus, anterior cingulate gyrus, and medial cingulate gyrus. The specific quantitative gamma vs alpha-beta frequency bands are not surfaced in the search excerpt — the article describes the pathway qualitatively.
- **Impact on F2/F3 attribution:** Cited in SPH `__init__.py` and `extraction.py` docstrings for the multiplicative composition rationale (E0 × E2). No runtime numeric constants in F2/F3 derive bit-exact from Bonetti 2024 — only the formula SHAPE (multiplicative composition) is anchored on the cited feedforward joint-engagement description (per 2026-05-17 structural-selection-audit doc).
- **Verification method recorded in CSV:** N/A (no F2/F3 constant claimed LIT from Bonetti 2024).

### §1.3 Cheung 2019 — uncertainty × surprise IC×Entropy interaction

- **Query:** `Cheung 2019 Current Biology uncertainty surprise pleasure music IDyOM IC entropy interaction`
- **Tool:** WebSearch (Google surface)
- **Outcome:** POSITIVE for the IC×Entropy interaction (saddle-shaped pleasure surface) concept.
- **Source confirmation:** Paper found — "Uncertainty and Surprise Jointly Predict Musical Pleasure and Amygdala, Hippocampus, and Auditory Cortex Activity" (Curr Biol 2019, DOI 10.1016/j.cub.2019.09.067). N=39,351 chord transitions; IDyOM-quantified uncertainty and surprise; saddle-shaped reward surface. The specific β=−0.124 interaction coefficient is referenced as a paper-level statistical result but appears in MI's UDP / ICEM module docstrings ONLY as a comment, NOT as a runtime constant.
- **Impact on F2/F3 attribution:** UDP's `cognitive_present.py` and ICEM's `temporal_integration.py` cite Cheung 2019 in docstrings; the multiplicative `p0 * p1` interaction term in UDP-P2 is operationalized as a STRUCTURAL choice (same family as HTP-E3 multiplicative composition) but the mixer weights `0.30, 0.25, 0.20, 0.15, 0.10, 0.05` on the surrounding terms are author-chosen ENGINEERING E4.
- **Verification method recorded in CSV:** N/A (no F2/F3 constant claimed LIT from Cheung 2019).

### §1.4 Aston-Jones & Cohen 2005 — LC-NE phasic/tonic 0.50/0.75 baseline/burst

- **Query:** `Aston-Jones Cohen 2005 locus coeruleus norepinephrine phasic tonic baseline burst`
- **Tool:** WebSearch (Google surface)
- **Outcome:** POSITIVE for phasic/tonic concept; NEGATIVE for bit-exact 0.50/0.75 numeric values.
- **Source confirmation:** Paper found — "An Integrative Theory of Locus Coeruleus-Norepinephrine Function: Adaptive Gain and Optimal Performance" (Annu Rev Neurosci 2005). Describes phasic mode (task-related, exploitation) vs tonic mode (disengagement, exploration). Does NOT publish specific 0.50 (tonic baseline) or 0.75 (phasic burst) numeric reference values — those are MI engine-side author operationalizations of the qualitative phasic/tonic dichotomy.
- **Impact on F2/F3 attribution:** Not applicable. NE constants live in F6/neurochemicals (Agent 3/5 scope), not in F2/F3. This verification was prophylactic — Agent 2 confirmed in advance that even if the 0.50/0.75 had appeared in F2/F3 scope, they would have been tagged **E ENGINEERING with PARTIAL verification + escalation** per Rule R9 (Form-LIT / coefficients-author re-parameterization).
- **Verification method recorded in CSV:** N/A.

---

## §2 Verification outcomes summary

| Outcome | Count | Notes |
|---|---|---|
| POSITIVE | 0 | No A/B claimed in F2/F3 — no positive verification credited to a CSV row |
| PARTIAL | 131 | RegionLink edge weights — module-level citation grounds edge existence, weight magnitude author-normalized |
| NEGATIVE | 0 | No claimed LIT failed verification |
| NEGATIVE-UNVERIFIABLE | 0 | Hallucination guard never triggered |
| N/A | 3,476 | Pure ENGINEERING / IDENTITY / STRUCTURAL constants — no web verification required per §3.3 |

---

## §3 Hallucination guard status

**Triggered: 0 times.**

Per §3.4 Rule R3: "Eğer 3 search attempt sonrasında cited paper bulunamazsa: agent ASLA 'paper'da öyle olmalı' diye varsaymaz. Otomatik LOW confidence + escalation queue."

In F2/F3 scope, this protection was not needed because no constant was a candidate for LIT attribution that required verification. All 4 web searches above were prophylactic confirmations of the literature context referenced in docstrings, not verifications of bit-exact numeric values claimed in runtime constants.

---

## §4 Verification method codes used in CSV

- **inspection** — 3,476 rows. Per-row code-locality + value-pattern inspection; no external verification required.
- **inspection** (with PARTIAL outcome) — 131 rows. RegionLink edge weights: module-level citation present in same call, but per context_brief §7-3 doctrine no paper publishes the specific weight value.

No row uses `websearch-google`, `webfetch-doi`, or `websearch-scholar-snippet` as `verification_method` because no LIT attribution was claimed.

---

## §5 Anti-overclaim record

The audit honestly reports **0% LIT-VERBATIM and 0% LIT-DERIVED in F2/F3 scope**. This is consistent with:
- Per-constant independence (Rule 6): even where mech docstrings heavily cite Sethares / de Vries-Wurm / Bonetti / Cheung / Aston-Jones, the runtime numeric constants are STRUCTURAL coordinates or ENGINEERING mixers, not literature-verbatim values.
- Conservative attribution (Rule 5): when in doubt, ENGINEERING.
- Co-location ≠ derivation (Rule 1): a citation in module docstring does not transitively make every nearby numeric literal LIT.
- AST walker citation_author column treated as HINT ONLY per Rule R8 — the walker auto-tagged many rows with citation hints (e.g. `cit=Vries & Wurm`, `cit=Tillmann`, `cit=Sarasso`), but Agent 2 re-evaluated each constant independently. The hints surfaced module-level citations correctly but did not justify upgrading any individual constant to LIT-VERBATIM.
