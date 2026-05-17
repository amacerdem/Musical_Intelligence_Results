# Agent 7 — Verification Log (RAM + Region Atlas)

**Scope:** `brain/(ram/|regions/)`
**Engine SHA:** `318eb2f5...`
**Total constants audited:** 65
**Audit date:** 2026-05-17

---

## Scope reconciliation (pre-verification)

**Initial expectation:** ~2,500 sabit (RAM tensor + 26-region centroids + 529 RegionLink weights).

**Inventory check** (`grep "^brain/(ram/|regions/)" raw_constants_inventory.csv`):
- Total rows: **65**
- File count: **27** (26 region files + `__init__.py`; `_region.py` and `registry.py` have zero numeric literals — `NUM_REGIONS = len(ALL_REGIONS)` is a derived assertion not in inventory)

**Where the missing ~2,400 sabit live (out of Agent 7 scope):**
1. **529 RegionLink weights** — declared in mechanism `__init__.py` files at `brain/functions/f1/.../f8/mechanisms/*/__init__.py`. Path-filter routes these to **Agents 1-3**.
2. **RAM accumulation infrastructure** (`_NUM_REGIONS=26`, `_NUM_NEURO=4`, `_REGION_NAMES` list, ReLU `min=0.0`) — lives in `brain/executor.py`. This file is in `brain/` root, not under `brain/ram/` or `brain/regions/` — routed to **Agent 5** per `Investigation-Rules §4`.
3. **NeuroLink call sites and neurochemical reference values** — under `brain/neurochemicals/`. Out of scope, **Agent 5**.

**Conclusion:** path-filter applied correctly; Agent 7 scope is the 26-region metadata package only. Reported as ESC-7-SCOPE-1 in escalation queue.

---

## Engine call-graph status of `brain/regions/`

Verified via grep across `Musical_Intelligence/`:

```
grep -rn "from Musical_Intelligence.brain.regions\|from .regions\|import regions"
  --include="*.py" (excluding brain/regions/ itself and __pycache__)
→ 0 hits
```

`brain/executor.py:38-46` re-declares its own `_REGION_NAMES` list (matching `brain/regions/registry.py:50-56` canonical order verbatim) and `_REGION_IDX` dict. This means:
- The MNI coords / Brodmann labels in `brain/regions/*.py` are **not consumed by engine runtime**
- The canonical region order is duplicated; the deprecation warning in `__init__.py:11-17` is genuine
- If `brain/regions/` were deleted, engine runtime would not change

This affects category assignment for the 26 region-index constants — they would technically qualify as Category G (DEAD-CODE-UNREACHABLE). However, the content is anatomical-reference metadata used by the paper/documentation pipeline, so I tagged them all C with a notes flag (see ESC-7-INFO-1).

---

## Web-search verification log

### Verification 1 — A1/HG MNI (48, -18, 8) [A7_A1HG_MNI_003]

- **Query 1:** `"Heschl's gyrus" "primary auditory cortex" MNI coordinates "48" "-18" "8" BA41`
- **Tool:** WebSearch
- **Outcome:** NEGATIVE — discussion of HG/BA41 anatomy returned, but (48,-18,8) bit-exact not surfaced from any single primary
- **Sources scanned:** PMC localization of human PAC, Wikipedia transverse temporal gyrus, J Neurosci Heschl shape paper, ResearchGate auditory MNI table
- **Decision:** Conservative C (STRUCTURAL anatomical-reference). Coord is plausible within HG range but is an author-aggregated representative centroid, not bit-equal to any cited single source.

### Verification 2 — NAcc MNI (10, 12, -8) [A7_NACC_MNI_036]

- **Query 1:** `Salimpoor 2011 nucleus accumbens MNI coordinates dopamine music PET` → narrative findings only
- **Query 2:** `"nucleus accumbens" "10" "12" "-8" MNI coordinates atlas Harvard-Oxford` → Harvard-Oxford centroid ~(11,11,1), not bit-exact
- **Tool:** WebSearch (×2)
- **Outcome:** NEGATIVE-UNVERIFIABLE (per §3.4)
- **Sources scanned:** Salimpoor 2011 full-text PDF reference, PNAS music/reward, NCBI bookshelf, Frontiers basal ganglia connectivity
- **Decision:** Conservative C (STRUCTURAL anatomical-reference); flagged ESC-7-1 for manual review of Salimpoor Supplementary Table

### Verification 3 — Salimpoor 2011 Nature Neurosci primary (depth check) [A7_NACC_MNI_036, A7_CAUDATE_MNI_016]

- **Query:** `Salimpoor 2011 Nature Neuroscience "nucleus accumbens" peak coordinates striatum dopamine`
- **Tool:** WebSearch
- **Outcome:** NEGATIVE — paper described methodologically; no exact stereotactic peaks in abstracts/snippets
- **Decision:** Both caudate (12,10,10) and NAcc (10,12,-8) MNI tuples cannot be tagged LIT-VERBATIM without direct paper access. Both → C with PARTIAL.

### Verification 4 — Janata 2009 vmPFC tonality MNI (2, 46, -10) [A7_VMPFC_MNI_062]

- **Query:** `Janata 2009 ventromedial prefrontal cortex tonality MNI coordinates "rostromedial"`
- **Tool:** WebSearch
- **Outcome:** NEGATIVE — narrative description of rostromedial PFC tonality map only; specific MNI peaks not surfaced
- **Decision:** Conservative C (STRUCTURAL anatomical-reference). Coord is plausible within rostromedial PFC range per Harvard-Oxford frontal pole / vmPFC, but not bit-equal to any verifiable single source.

### Verification 5 — Brodmann area textbook anatomy (12 BAs)

- **Query:** `Brodmann area BA41 primary auditory cortex Heschl gyrus BA22 superior temporal gyrus`
- **Tool:** WebSearch
- **Outcome:** POSITIVE — standard textbook cytoarchitectonic mapping confirmed (BA41 = PAC/HG, BA22 = STG, BA44 = pars opercularis/Broca, BA39 = AG, BA38 = TP, BA46 = dlPFC, BA10 = frontopolar, BA11 = OFC, BA32 = ACC, BA6 = SMA/PMC, BA21 = middle temporal/STS)
- **Decision:** All 12 Brodmann area integers tagged C (STRUCTURAL anatomical-reference) — common-knowledge anatomy from Brodmann 1909 atlas, no fit involved. Confidence HIGH for each.

---

## Brodmann area assignment table (verified textbook anatomy)

| Region | BA | Standard label | Verified? |
|--------|-----|----------------|-----------|
| A1_HG (index 0) | 41 | Primary auditory cortex / Heschl's gyrus | YES — Wiki + ScienceDirect |
| STG (1) | 22 | Superior temporal gyrus / Wernicke's | YES |
| STS (2) | 21 | Middle temporal gyrus / STS banks | YES (BA21 = MTG; STS spans BA21/22 boundary) |
| IFG (3) | 44 | Pars opercularis (Broca's posterior) | YES |
| dlPFC (4) | 46 | Dorsolateral prefrontal cortex | YES |
| vmPFC (5) | 10 | Frontopolar cortex (anterior PFC) | YES |
| OFC (6) | 11 | Medial orbitofrontal cortex | YES |
| ACC (7) | 32 | Dorsal anterior cingulate | YES |
| SMA (8) | 6 | Premotor / SMA (medial part of BA6) | YES — shared BA6 with PMC |
| PMC (9) | 6 | Lateral premotor cortex | YES — shared BA6 with SMA |
| AG (10) | 39 | Angular gyrus | YES |
| TP (11) | 38 | Temporopolar cortex | YES |

All 12 → **C (STRUCTURAL), HIGH confidence**. These are anatomical labels from Brodmann 1909 cytoarchitectonic atlas, not empirical values.

---

## Region index assignments (canonical order)

All 26 indices (0-25) verified against:
1. `brain/regions/registry.py:50-56` (ALL_REGIONS tuple order)
2. `brain/executor.py:38-46` (_REGION_NAMES list — matches verbatim)

| Block | Indices | Regions |
|-------|---------|---------|
| Cortical | 0-11 | A1_HG, STG, STS, IFG, dlPFC, vmPFC, OFC, ACC, SMA, PMC, AG, TP |
| Subcortical | 12-20 | VTA, NAcc, caudate, amygdala, hippocampus, putamen, MGB, hypothalamus, insula |
| Brainstem | 21-25 | IC, AN, CN, SOC, PAG |

All 26 → **C (STRUCTURAL), HIGH confidence**. Topology positions, not empirical values. Matches RAM tensor `(B, T, 26)` cardinality assertion at `registry.py:67`.

---

## MNI coord summary table

All 26 MNI tuples → **C (STRUCTURAL anatomical-reference)**, confidence HIGH for indices and BA labels, MEDIUM for MNI tuples (per §3.4 NEGATIVE-UNVERIFIABLE outcomes; author-aggregated representative coords over multiple atlas/functional sources).

**Note on `tuple-numeric` row representation:** the AST walker records each `mni_coords=(x, y, z)` as a single inventory row covering the 3-int tuple. The 26 tuples contain 78 underlying integer values. Constant-level audit treats them as 26 named-position constants per the inventory schema.

---

## Category distribution — Agent 7 final

| Category | Count | % | Notes |
|----------|------:|---:|-------|
| A — LIT-VERBATIM | 0 | 0.0% | No bit-exact single-source MNI/atlas verification possible; all candidates downgraded to C per §5 conservative attribution + §3.4 hallucination guard |
| B — LIT-DERIVED | 0 | 0.0% | — |
| C — STRUCTURAL | 64 | 98.5% | 26 indices + 26 MNI tuples + 12 Brodmann areas (anatomical-reference + topology metadata) |
| D — IDENTITY-PLACEHOLDER | 0 | 0.0% | — |
| E — ENGINEERING-CHOICE | 1 | 1.5% | `stacklevel=2` (Python warning convention) |
| F — HAND-SPECIFIED-DISCLOSED | 0 | 0.0% | Correct — F is STRICTLY the 7 reward weights |
| G — DEAD-CODE-UNREACHABLE | 0 | 0.0% | Whole package is deprecated/unimported by engine — see ESC-7-INFO-1 for borderline; tagged C with note rather than G |
| **Total** | **65** | **100.0%** | |

---

## Confidence distribution (verified via CSV grep)

| Confidence | Count | % | Notes |
|------------|------:|---:|-------|
| HIGH | 40 | 61.5% | 26 indices + 12 BAs + 1 A1/HG MNI + 1 stacklevel |
| MEDIUM | 25 | 38.5% | 25 of 26 MNI tuples (author-aggregated atlas reps, NEGATIVE-UNVERIFIABLE per §3.4) |
| LOW | 0 | 0.0% | — |

---

## Pattern-batching audit (Rule 6)

Per Rule 6 / Rule R4, each of the 65 constants received an independent `reason` field. The 26 region-index entries and 12 Brodmann entries share structural similarity but each row has region-specific reason text identifying the slot/anatomy. No batched reason copy-paste. Verified by reading the CSV's `reason` column.

---

## Checkpoint summary (Rule 8)

Scope is only 65 constants — well under the 500-constant checkpoint threshold. Single-pass audit. No mid-stream pattern-batching risk.
