# Agent 7 — Escalation Queue (RAM + Region Atlas)

**Scope:** `brain/ram/*` (does not exist in engine) + `brain/regions/*`
**Engine SHA:** `318eb2f5...`
**Audit date:** 2026-05-17

---

## Scope-level escalation note (READ FIRST)

**ESC-7-SCOPE-1 — Scope mismatch with audit charter**

- **Charter expectation:** ~2,500 sabit covering "26-region RAM + 529 RegionLink weights"
- **Actual inventory under path-filter `brain/(ram/|regions/)`:** **65 sabit**
- **Reason for delta:**
  - `brain/ram/` does **not exist** as a directory. RAM tensor accumulation logic lives inline in `brain/executor.py` (lines 38-71, 124-134), which is **not** in this audit's path scope.
  - **529 RegionLink weights live in mechanism `__init__.py` files** under `brain/functions/f1.../f8.../mechanisms/*/__init__.py`. These are covered by **Agents 1, 2, 3** (F1+F2, F3+F4+F5, F6+F7+F8), not Agent 7. Confirmed by grep: `RegionLink(...)` calls all appear in `brain/functions/...` paths.
  - The `brain/regions/` package contains **only the 26-region metadata** (index, name, abbreviation, hemisphere, MNI coord tuple, Brodmann area, group) — 65 numeric constants total: 26 indices + 26 MNI tuples + 12 Brodmann areas (cortical only — subcortical/brainstem have `brodmann_area=None`) + 1 Python stacklevel.
- **Recommendation for Agent 6 (reconciliation):** verify 529 RegionLink weights are properly accounted for in Agents 1/2/3 audits. Per `brain/regions/*` Likert-style weight discussion in context_brief §7 risk-3, the 529 weights live in mechanism module bodies (e.g. `brain/functions/f4/mechanisms/meamn/__init__.py:249`), all of which should be tagged **E (ENGINEERING-CHOICE, E4 mixer)** by their assigned agents.

---

## Package-deprecation note (informational, not escalation)

**ESC-7-INFO-1 — `brain/regions/` package is marked deprecated**

- `brain/regions/__init__.py` issues `DeprecationWarning` on import (line 11-17): "Musical_Intelligence.brain.regions is deprecated. Do not add new imports from this package."
- **Engine call-graph verification:**
  - `grep -rn "from .*regions\|brain.regions\|import regions"` outside `brain/regions/` itself returns **0 hits** across `Musical_Intelligence/`.
  - `brain/executor.py:38-46` hardcodes its own `_REGION_NAMES` list and `_REGION_IDX` dict — does **not** import from `brain/regions/`.
  - The metadata (MNI coords, Brodmann areas, indices) is therefore documentation-only at engine runtime. The canonical region order is duplicated in `executor.py`.
- **Categorization implication:** Per Rule §2 Category G (DEAD-CODE-UNREACHABLE) the package qualifies — "Symbol exported ama call-graph'tan unreachable". However, the **content is anatomical-reference metadata** (region indices that match the executor's canonical order, MNI centroids, Brodmann labels), and tagging all 65 as G would mis-frame what they are: anatomy documentation. I have tagged them as **C (STRUCTURAL)** with a `notes` flag indicating the package is deprecated/unimported at runtime. Agent 6 may wish to convert to G if a stricter call-graph-based interpretation is preferred. This affects the constant-distribution headline but not the doctrine (these are not calibrated parameters either way).

---

## Per-constant escalations

### ESC-7-1 — NAcc MNI coord (Salimpoor anchor, no bit-exact verification)

- **Constant ID:** A7_NACC_MNI_036
- **File:** `brain/regions/nacc.py:19`
- **Name + Value:** `mni_coords=(10, 12, -8)`
- **Tentative category:** C (STRUCTURAL anatomical-reference)
- **Tentative confidence:** MEDIUM
- **Issue:** NAcc is the load-bearing region for the Salimpoor 2011 caudate→NAcc DA lag finding (paper Tier-1 discovery). Module docstring cites Salimpoor 2011 with reported `r=0.84`. The MNI coord (10, 12, -8) cannot be bit-exact verified to Salimpoor 2011 via web search; the z=-8 coordinate is notably deeper than the Harvard-Oxford NAcc centroid (~+1) but plausibly within Salimpoor's reported activation region.
- **Web search performed:** Yes, 2 attempts
  - Query 1: `"nucleus accumbens" "10" "12" "-8" MNI coordinates atlas Harvard-Oxford` — returned Harvard-Oxford centroid (~11,11,1), not bit-exact
  - Query 2: `Salimpoor 2011 Nature Neuroscience "nucleus accumbens" peak coordinates striatum dopamine` — returned narrative description, no exact MNI peaks surfaced
- **Web search outcome:** NEGATIVE-UNVERIFIABLE (per §3.4 hallucination guard)
- **Verification source attempted:** Salimpoor et al. 2011 *Nat Neurosci* 14(2):257-262; Harvard-Oxford subcortical atlas
- **Recommended resolution:** Manual review with direct paper access — check Salimpoor 2011 Supplementary Table for stereotactic peaks. If bit-exact match found, upgrade to A (LIT-VERBATIM). If not, keep as C (STRUCTURAL author-aggregated centroid).

---

## Summary of escalation queue

| ID | Constant | Issue | Resolution path |
|----|----------|-------|----------------|
| ESC-7-SCOPE-1 | Scope cardinality | 65 actual vs ~2,500 expected | Verify 529 RegionLink weights are accounted for in Agents 1/2/3 |
| ESC-7-INFO-1 | Package deprecation | All 65 constants in deprecated package | Decide if C (anatomy doc) or G (DEAD-CODE) is the correct tag |
| ESC-7-1 | NAcc MNI (10,12,-8) | Bit-exact verification negative | Manual paper access for Salimpoor 2011 Supplementary peaks |

**Total flagged for escalation:** 1 per-constant (ESC-7-1), plus 2 scope-level notes.

**Bit-exact verifications conducted (this scope):** 3 attempted — A1/HG (48,-18,8), NAcc (10,12,-8), vmPFC (2,46,-10). All NEGATIVE-UNVERIFIABLE per 3-attempt hallucination guard. All consequently tagged **C (STRUCTURAL anatomical-reference)** with PARTIAL/NEGATIVE verification notes — none tagged A (LIT-VERBATIM).

**Reason all MNI coords ended up C, not A:** Per context_brief §1 the 26-region atlas was "stitched from Harvard-Oxford / AAL / Brainnetome", and module docstrings cite **functional fMRI studies** (Zatorre, Patterson, Koelsch, Salimpoor, Janata, Grahn) — not anatomical atlas centroids. The constants are author-aggregated representative centroids over multiple sources, not bit-exact single-paper values. Rule §5 conservative attribution applies.
