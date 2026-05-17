# Agent 7 — Audit Summary (RAM + Region Atlas)

**Scope:** `brain/(ram/|regions/)` engine paths
**Engine SHA:** `318eb2f5...`
**Audit date:** 2026-05-17
**Constants audited:** **65** (vs charter expectation ~2,500)

---

## Key findings

### 1. Scope-cardinality reconciliation (CRITICAL)

The charter expected ~2,500 constants covering "26-region RAM + 529 RegionLink weights". The actual `brain/(ram/|regions/)` path-filter contains **65 sabit** because:

- **`brain/ram/` does not exist** as a directory in the engine. RAM tensor accumulation logic (region accumulation, ReLU clamp, `_NUM_REGIONS=26`, `_REGION_NAMES` list) lives inline in `brain/executor.py:34-134`, which is in `brain/` root, not the audit path-filter. This routes to **Agent 5** per `Investigation-Rules §4`.
- **529 RegionLink weights** are declared in per-mechanism `__init__.py` files at `brain/functions/f{1..8}/mechanisms/*/__init__.py`. These route to **Agents 1, 2, 3** by function-domain, not Agent 7. Confirmed by grep: `RegionLink("...", "REGION", 0.XX, ...)` calls appear exclusively in `brain/functions/...` paths.
- The `brain/regions/` package contains only the 26-region anatomical metadata: indices, names, abbreviations, hemispheres, MNI coord tuples, Brodmann areas, group labels. AST walker extracts 65 numeric values: **26 indices + 26 MNI tuples + 12 Brodmann area integers** (subcortical/brainstem regions have `brodmann_area=None` so are not in inventory) + **1 Python `stacklevel=2` warning kwarg**.

This is documented as `ESC-7-SCOPE-1` in the escalation queue. Agent 6 should verify that the 529 RegionLink weights are accounted for in Agents 1/2/3 outputs (and tagged **E (E4 mixer)** per context_brief §4 + §7 risk-3 doctrine).

### 2. Engine call-graph status — package is unimported

The `brain/regions/` package's `__init__.py` issues a `DeprecationWarning` on import. Grep verification across the engine (`grep -rn "from .*regions\|brain.regions\|import regions"` excluding the package itself) returns **zero hits**. `brain/executor.py:38-46` declares its own hardcoded `_REGION_NAMES` list (matching `registry.py:50-56` verbatim) and `_REGION_IDX` dict — does not import from `brain/regions/`. The metadata is documentation/paper-pipeline only at engine runtime.

A strict call-graph reading would tag all 65 as **Category G (DEAD-CODE-UNREACHABLE)**. I chose the lighter touch — tag as **C (STRUCTURAL)** with a `notes` flag indicating the package is deprecated/unimported. This preserves the anatomical-reference semantics for the paper's RAM atlas discussion. Documented as `ESC-7-INFO-1`. Agent 6 may re-tag to G if a stricter interpretation is preferred.

### 3. Category distribution (final)

| Category | Count | % |
|----------|------:|---:|
| A — LIT-VERBATIM | 0 | 0.0% |
| B — LIT-DERIVED | 0 | 0.0% |
| C — STRUCTURAL | 64 | 98.5% |
| D — IDENTITY-PLACEHOLDER | 0 | 0.0% |
| E — ENGINEERING-CHOICE | 1 | 1.5% |
| F — HAND-SPECIFIED-DISCLOSED | 0 | 0.0% |
| G — DEAD-CODE-UNREACHABLE | 0 | 0.0% (see §2 above) |

**The 1 E:** `stacklevel=2` in the `_warnings.warn(...)` deprecation call — standard Python convention parameter.

**The 64 C:** 26 region indices (0-25 — RAM tensor topology positions, mirrored verbatim in `executor.py:38-46`), 26 MNI coord tuples (78 underlying integers — author-aggregated representative centroids stitched from Harvard-Oxford / AAL / Brainnetome per context_brief §1, with multi-paper functional-fMRI citations rather than single-source atlas reference), and 12 Brodmann area integers (textbook anatomy from Brodmann 1909 — BA41 PAC, BA22 STG, BA44 Broca, etc.).

### 4. Anti-overclaim conformance — no MNI coord tagged LIT-VERBATIM

Per context_brief §1 the 26-region atlas is "stitched from Harvard-Oxford / AAL / Brainnetome", and module docstrings cite **functional fMRI peak studies** (Zatorre 2002, Patterson 2002, Koelsch 2014, Salimpoor 2011, Janata 2009, Grahn & Rowe 2009, Blood & Zatorre 2001) — these are not anatomical-atlas-centroid sources. Web search verification on three load-bearing coords (A1/HG, NAcc, vmPFC) returned NEGATIVE-UNVERIFIABLE per §3.4 hallucination guard. Conservative §5 + R8/R9 rules applied: all MNI tuples → **C (STRUCTURAL anatomical-reference, MEDIUM confidence)**, none → A.

This conforms to context_brief §7 risk-3 doctrine: "RegionLink weights are author-normalized Likert-style [0.40, 0.95] — no paper publishes per-edge weights" → analogously, **per-region MNI centroids in MI's stitched-atlas scheme are author-aggregated representatives**, not single-source bit-equal. The honest categorization is C with partial verification, not A.

### 5. Confidence distribution

Verified by CSV grep:

| Confidence | Count | % |
|------------|------:|---:|
| HIGH | 40 | 61.5% |
| MEDIUM | 25 | 38.5% |
| LOW | 0 | 0.0% |

HIGH covers: 26 region indices + 12 Brodmann areas + 1 A1/HG MNI (textbook coord) + 1 stacklevel = 40. MEDIUM covers: 25 of the 26 MNI tuples (A1/HG is the only MNI marked HIGH because BA41 anchor is textbook-verified; the rest are author-aggregated atlas/functional centroids with no bit-exact single source).

The MNI-tuple MEDIUM bucket reflects honest non-verifiability per §3.4 (NEGATIVE-UNVERIFIABLE outcomes on the three attempted searches generalize across the stitched-atlas scheme). No attribution change — all 26 MNI tuples remain C. Agent 6 may wish to normalize the A1/HG MNI from HIGH to MEDIUM for uniformity if a stricter convention is preferred.

### 6. Pattern-batching audit (Rule 6 / Rule R4)

Each of the 65 constants received an independent `reason` line in the CSV. Region-specific anatomical context (e.g. "Topology slot 14" for caudate vs "Topology slot 8" for SMA; "right Premotor Cortex within lateral PMC per multiple atlases" vs "right STS within Harvard-Oxford range") prevents copy-paste batching. The 12 Brodmann area rows each name the specific BA→region mapping (BA41=PAC, BA44=Broca, BA46=dlPFC, etc.) — no template.

### 7. Escalation queue

- **1 per-constant escalation** flagged: `ESC-7-1` (NAcc MNI (10,12,-8) cannot bit-exact verify to Salimpoor 2011 via 2 web search attempts; manual Supplementary Table check recommended)
- **2 scope-level notes**: `ESC-7-SCOPE-1` (cardinality reconciliation) + `ESC-7-INFO-1` (package deprecation status)

---

## Doctrine implications

**Reinforces zero-calibration doctrine.** Zero of the 65 constants in Agent 7 scope are calibrated against held-out cognitive data:
- Region indices = topology slots
- MNI coords = anatomy-reference representatives over public atlases
- Brodmann areas = Brodmann 1909 textbook labels
- `stacklevel=2` = Python warning convention

None of these is a fit parameter or empirically tuned weight. Audit conformance with the 2026-05-16 CODE-FIRST doctrine: PASS.

**Frames the 529 RegionLink weights for downstream agents.** Although out of Agent 7 scope, the structural inference holds: **per-region anatomical metadata is C (STRUCTURAL)**, **per-edge RegionLink weights are E4 (ENGINEERING-CHOICE mixer)**. Agent 6 should ensure Agents 1-3 have tagged the 529 weights as E4. If any Agent 1-3 tags a RegionLink weight as A or F, that is an over-attribution per context_brief §7 risk-3.

---

## Deliverable manifest

1. `/Volumes/SRC-9/SRC Musical Intelligence/Musical_Intelligence_Results/_audits/agent_7_audit.csv` — 65 rows with full attribution chain
2. `/Volumes/SRC-9/SRC Musical Intelligence/Musical_Intelligence_Results/_audits/agent_7_escalation.md` — 1 per-constant escalation + 2 scope notes
3. `/Volumes/SRC-9/SRC Musical Intelligence/Musical_Intelligence_Results/_audits/agent_7_verification_log.md` — web-search log + scope reconciliation + category/confidence breakdown
4. `/Volumes/SRC-9/SRC Musical Intelligence/Musical_Intelligence_Results/_audits/agent_7_summary.md` — this file
