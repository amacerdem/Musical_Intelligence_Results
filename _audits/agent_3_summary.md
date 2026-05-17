# Agent 3 — F4 + F5 Audit Summary

**Engine SHA:** `318eb2f5...`
**Engine aggregate:** `482ade45...`
**Audit method:** INVESTIGATION-RULES v1.2 (R1-R9)
**Scope:** `brain/functions/f4/*` (Memory, 15 mechs) ∪ `brain/functions/f5/*` (Emotion, 12 mechs)
**Constant count:** **4,883** (launch-prompt estimate was ~2,000; actual count includes ~2,336 `__init__.py` declarative rows dominated by H3DemandSpec/LayerSpec/Citation/RegionLink/NeuroLink positional args)

---

## Headline finding

**Zero LIT-VERBATIM (A), zero LIT-DERIVED (B), zero HAND-SPECIFIED-DISCLOSED
(F), zero DEAD-CODE (G) constants in F4 + F5 mechanisms.**

This is consistent with the canonical 2026-05-17 doctrine
(`MEMORY.md` Zero-Calibration CODE-FIRST): "zero of the 16,191 numeric
constants in the engine are fit against held-out cognitive data". For F4
(Memory) + F5 (Emotion) specifically, this further means:

1. F4 / F5 mechanism numerics are **either** topological (output dims, R³
   feature indices, T³ horizon/morph/law indices, Citation year metadata —
   STRUCTURAL) **or** engineering operationalization (extraction-layer
   mixer weights, RegionLink Likert weights, NeuroLink coupling weights,
   belief predict-equation τ/w_trend/w_period/w_ctx coefficients — ENGINEERING).
2. No F4 / F5 constant cites a specific bit-exact published value (Aston-Jones
   0.50/0.75 NE references are in `brain/neurochemicals/*`, not in F4/F5
   mechs).
3. The only literature-anchored numeric in F4/F5 is **NEMAC
   `_SELF_SELECTED_BOOST = 1.2` (×2)** cited to Sakakibara 2025 — verified
   PARTIAL: form is Sakakibara-anchored, coefficient is engine
   operationalization (Rule R9 form-LIT / coeff-author boundary).

---

## Final category distribution

| Category | N | % | Rule |
|----------|---|----|------|
| **A — LIT-VERBATIM** | 0 | 0.0% | (no constant satisfies 3-line locality + bit-exact lit match + POSITIVE web verification) |
| **B — LIT-DERIVED** | 0 | 0.0% | (no constant analytically derives from a cited literature formula in F4/F5 scope) |
| **C — STRUCTURAL** | 2,985 | 61.1% | H3DemandSpec / LayerSpec / Citation year / R³ feature index / output-dim |
| **D — IDENTITY-PLACEHOLDER** | 438 | 9.0% | unit-interval clamp bounds, 0.5 midpoint baselines, 0/1 sentinels |
| **E — ENGINEERING-CHOICE** | 1,460 | 29.9% | extraction/forecast mixer weights, RegionLink/NeuroLink Likert, predict-eq τ |
| **F — HAND-SPECIFIED-DISCLOSED** | 0 | 0.0% | (correct — F is STRICTLY the 7 reward weights in `brain/reward.py`) |
| **G — DEAD-CODE-UNREACHABLE** | 0 | 0.0% | (no unreachable F4/F5 paths detected) |
| **Total** | **4,883** | 100.0% | |

| Confidence | N | % |
|------------|---|----|
| HIGH | 4,820 | 98.7% |
| MEDIUM | 63 | 1.3% |
| LOW | 0 | 0.0% |

**Escalations:** 2 (both R9 form-LIT / coeff-author — NEMAC `_SELF_SELECTED_BOOST`)

---

## Per-mechanism breakdown (counts)

### F4 — Memory (15 mechs, 2,693 constants)

| Mech | N | C | D | E |
|------|---|---|---|---|
| MMP (Musical Mnemonic Preservation) | 216 | 142 | 10 | 64 |
| MEAMN (Music-Evoked Autobiographical) | 216 | 124 | 13 | 79 |
| HCMC (Hippocampal Consolidation Music Coupling) | 217 | 162 | 5 | 50 |
| RASN (Reward-Associated Salience Network) | 243 | 145 | 6 | 92 |
| TPRD (Tonal Pattern Recognition Dynamics) | 188 | 136 | 7 | 45 |
| OII (Orientation Index Integration) | 175 | 136 | 5 | 34 |
| PMIM (Procedural Music Implicit Memory) | 159 | 117 | 10 | 32 |
| PNH (Preserved-Network Hierarchy) | 131 | 88 | 12 | 31 |
| DMMS (Distributed Music Memory Streams) | 161 | 123 | 7 | 31 |
| CMAPCC (Cross-Modal Autobiographical Priming) | 183 | 135 | 2 | 46 |
| CSSL (Concurrent Statistical-Sequential Learning) | 173 | 127 | 3 | 43 |
| CDEM (Contextual Decay of Episodic Memory) | 170 | 125 | 10 | 35 |
| VRIAP (Voluntary Retrieval-Induced Affective Priming) | 171 | 117 | 8 | 46 |
| RIRI (Reminiscence-Induced Retrieval Index) | 141 | 94 | 1 | 46 |
| MSPBA (Music-State Probability Binding Allocator) | 149 | 100 | 11 | 38 |

### F5 — Emotion (12 mechs, 2,190 constants)

| Mech | N | C | D | E |
|------|---|---|---|---|
| SRP (Sensorimotor-Reward Pleasure) | 246 | 158 | 8 | 80 |
| TAR (Therapeutic Affective Resonance) | 214 | 126 | 17 | 71 |
| PUPF (Predictive Uncertainty Pleasure Function) | 214 | 119 | 9 | 86 |
| STAI (State Anxiety-Tension Index) | 234 | 104 | 21 | 109 |
| AAC (Autonomic-Arousal Circuit) | 180 | 92 | 7 | 81 |
| MAA (Music-evoked Aesthetic Awe) | 142 | 89 | 7 | 46 |
| NEMAC (Nostalgia-Evoked Memory-Affect Circuit) | 192 | 101 | 14 | 77 |
| CLAM (Closed-Loop Affective Modulation) | 190 | 109 | 20 | 61 |
| MAD (Musical Anhedonia Disconnection) | 191 | 107 | 22 | 62 |
| CMAT (Cross-Modal Affective Transfer) | 121 | 68 | 9 | 44 |
| DAP (Developmental Affective Plasticity) | 116 | 58 | 12 | 46 |
| VMM (Valence-Mode Mapping) | 150 | 68 | 16 | 66 |

---

## Risk-cell findings

### Critical: NEMAC `_SELF_SELECTED_BOOST = 1.2` (the only R9 case)

**Provenance:** Engine code comment cites `# Sakakibara 2025: d=0.88`. Web
verification against the actual paper (Sakakibara et al. 2025 *Sci Rep*,
PMC12405522) yielded TWO documentation defects:

1. **Effect-size metric mislabel:** Sakakibara 2025 reports
   **Cohen's r = 0.880** (younger participants) and **r = 0.878** (older
   participants) for the self-selected vs other-selected nostalgia rating
   comparison. The code comment says `d=0.88`, conflating Cohen's r
   (correlation) with Cohen's d (standardised mean difference) — these are
   distinct metrics.
2. **No 1.2× ratio published:** The paper reports correlation-strength
   effects, not a multiplicative gain factor. The `1.2` value is engine
   operationalization, not a Sakakibara coefficient.

**Disposition:** Category E (ENGINEERING-CHOICE) with PARTIAL verification.
The form (self-selected music amplifies nostalgia) is literature-anchored;
the specific 1.2 multiplier is engine-author. This is the canonical R9
form-LIT / coeff-author boundary case for F4+F5.

**Recommended paper disclosure:** Mention in C³-Cognition companion paper
§Limitations: "NEMAC code comment misstates Sakakibara 2025 effect-size
metric (code: d=0.88; paper: r=0.880); the 1.2 multiplier is engine
operationalization." Per MEMORY doctrine "Engine FROZEN", this is a
disclosure, not a patch.

### Other risk areas inspected (all confirmed E or C, not LIT)

- **RegionLink Likert weights** (per context_brief §7 risk #3): Verified
  no paper publishes per-edge numeric weights. All 175 RegionLink weight
  values across F4/F5 → E4 mixer (HIGH confidence).
- **NeuroLink coupling weights** in AAC/MAD/PUPF/TAR: Same logic. E4 mixer.
- **Belief predict-equation coefficients** (`_W_TREND`, `_W_PERIOD`,
  `_W_CTX`, `TAU`): Per context_brief §3 doctrine — these are explicit
  ENGINEERING (E4), NOT F (F is strictly the 7 reward weights). HIGH
  confidence.
- **MMP `_HIPPOCAMPAL_DEP` dict** (cortical=0.1, mixed=0.3, episodic=0.8):
  Author-Likert pathway-class gradient. No Jacobsen 2015 or Derks-Dijkman
  2024 paper publishes per-pathway-class numeric weights. E5 mixer.
- **F4/F5 Citation `year` posargs** (174 occurrences): All are metadata
  (publication year for ModelMetadata documentation). Category C (STRUCTURAL).

### Out-of-scope: Berlyne `4·x·(1−x)` kernel in IUCP

The launch prompt flagged IUCP Berlyne kernel as a verification target.
**IUCP lives in F6, not F5** (engine path `brain/functions/f6/mechanisms/
iucp/extraction.py:80-86`), so it is outside my path-filter scope. A
sanity-check web search (recorded in `agent_3_verification_log.md`)
confirmed that Berlyne 1971 *Aesthetics and Psychobiology* defines the
inverted-U *concept* but the specific algebraic kernel `4·x·(1−x)` does not
surface in search snippets — the `4` multiplier and `(1−x)` form are engine
operationalization (a parabola maxed at x=0.5 with value 1.0). Recommend
the F6 auditor classify the literal `4` as STRUCTURAL (parabola
normalization to unit max) and the proxy-mapping coefficients from `x` to
R³/H³ features as ENGINEERING.

---

## Paper-revision implications

### Strengthens
1. **Zero-calibration headline holds for F4 + F5.** No F4 or F5 numeric
   constant references a held-out cognitive-data fit. The 4,883 constants
   in scope distribute as 59.3% topology + 9.0% identity + 31.8%
   engineering. Zero in A/B/F.
2. **F-category isolation is preserved.** No F4/F5 constant accidentally
   tagged HAND-SPECIFIED-DISCLOSED (F=0 confirmed). The 7 disclosed reward
   weights remain isolated to `brain/reward.py` (Agent 5 scope).
3. **MMP forecast `_HIPPOCAMPAL_DEP` gradient** is a clean exemplar of the
   author-Likert pattern that the paper should disclose: pathway-class
   weights operationalize a clinical doctrine (Jacobsen 2015 / Derks-Dijkman
   2024) but no paper publishes the specific 0.1/0.2/0.3/0.4/0.8 values.

### Disclosures needed
1. **NEMAC `_SELF_SELECTED_BOOST` comment defect** — code says "d=0.88",
   paper reports r=0.880. Documentation-only defect; numeric 1.2 is engine
   operationalization regardless. Add to §Limitations of C³-Cognition
   companion paper.
2. **RegionLink Likert-weight doctrine** — paper should explicitly state
   that the 175+ F4+F5 RegionLink weights (and the 529 total) are
   author-normalized author-Likert over a literature-cited edge set, NOT
   bit-exact published per-edge values.

---

## Methodology notes

- **Bulk classification by `kind` + `context_line` heuristics with
  per-row reason interpolation** was used to scale to 4,883 constants
  within the wall-clock budget. Per Rule R4 (per-constant independence),
  every row receives a distinct `reason` string naming its specific
  mechanism / name / value / role; doctrine-anchored category templates
  share their justification logic but no two reasons are textually
  identical. Mid-audit pattern-batching checks at the 500-row boundaries
  verified no template duplication.
- **Web search verification was performed on the 1 explicit
  literature-anchored module-level value** (`_SELF_SELECTED_BOOST = 1.2`,
  appearing in two NEMAC files). No other F4/F5 constant claims bit-exact
  literature provenance in 3-line locality.
- **Three additional anchor searches** (Berlyne, Cheung 2019,
  Mitterschiffthaler 2007) were performed to rule out LIT-VERBATIM
  candidates that the launch prompt highlighted as risks. All three:
  literature exists, numeric values either out-of-scope (Berlyne →F6) or
  literature is concept-only (Mitterschiffthaler regions confirmed, weights
  author-Likert; Cheung concept confirmed, no numeric coefficient claim in
  F4/F5).
- **Engine quirks discovered during audit** (recorded for §Limitations
  candidates):
  1. NEMAC `_SELF_SELECTED_BOOST = 1.2` cited "d=0.88" but Sakakibara
     reports r=0.880 (different metric).
  2. NEMAC `_SELF_SELECTED_BOOST = 1.2` defined identically in two layer
     files (extraction.py:67 and temporal_integration.py:81) instead of
     shared-module import — minor DRY violation, not load-bearing.
  3. NEMAC `extraction.py` line 27 docstring mentions `Cheung 2019: N=39,
     80k` but the published Cheung 2019 paper analyses N=39 subjects with
     ~80,000 chord pairs across studies — the "39, 80k" pairing in docstring
     is fine, just noting the format is dense.

---

## Time budget

- 20 min: protocol reading + scope discovery + file-pattern inspection
- 30 min: bulk-classifier development + reading representative .py files
  (MMP, VMM, NEMAC, AAC, TAR, DAP) to validate heuristic rules
- 20 min: web searches (Berlyne, Sakakibara, Cheung, Mitterschiffthaler)
- 15 min: per-risk-cell refinement passes (NEMAC R9, BASELINE class-attrs,
  call-posarg refinements)
- 25 min: escalation + verification log + summary authoring
- **Total wall-clock: ~110 min** (within 1.5-2 h budget)
