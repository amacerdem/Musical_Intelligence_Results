# Agent 3 — Escalation Queue

**Scope:** F4 (Memory) + F5 (Emotion) mechanisms
**Engine SHA:** `318eb2f5...`
**Total constants:** 4,883
**Escalations:** 2 (R9 form-LIT / coeff-author)

---

## ESC-1 — NEMAC `_SELF_SELECTED_BOOST = 1.2` (extraction.py)

- **Constant ID:** A3_03789
- **File:** `brain/functions/f5/mechanisms/nemac/extraction.py:67`
- **Name + Value:** `_SELF_SELECTED_BOOST = 1.2`
- **Tentative category:** E (ENGINEERING-CHOICE) with **PARTIAL** verification
- **Tentative confidence:** MEDIUM
- **Issue:** Code comment claims `# Sakakibara 2025: d=0.88, self-selected boost`.
  Two distinct provenance concerns:
  1. **Coefficient sourcing:** Sakakibara 2025 (Sci Rep, PMC12405522) does NOT
     publish a 1.2× multiplicative gain ratio. The paper reports effect-size
     correlations between self-selected and other-selected nostalgia ratings
     (Cohen's r = 0.880 in younger, r = 0.878 in older). The 1.2 in code is
     engine operationalization, not a literature-published coefficient.
  2. **Metric mislabel:** Code comment says `d=0.88` but Sakakibara 2025
     reports **Cohen's r = 0.880**, not Cohen's d = 0.88. These are different
     effect-size metrics. The comment is incorrect.
- **Web search performed:** Yes, 2 attempts
  - WebSearch: "Sakakibara 2025 self-selected music nostalgia EEG d=0.88 1.2x boost"
    → paper located (Nature Sci Rep 2025), no specific d or 1.2x in snippet
  - WebFetch: https://pmc.ncbi.nlm.nih.gov/articles/PMC12405522/
    → confirmed Cohen's r=0.880 (younger), r=0.878 (older) for self-selected
       vs other-selected nostalgia; no Cohen's d reported for this comparison;
       no 1.2× multiplicative ratio.
- **Web search outcome:** PARTIAL (form anchored, coefficient not anchored,
  comment-vs-paper metric mismatch)
- **Verification source attempted:** Sakakibara et al. 2025 *Sci Rep* —
  "A Nostalgia Brain-Music Interface for enhancing nostalgia, well-being, and
  memory vividness in younger and older individuals" (PMC12405522).
- **Recommended resolution:**
  1. Keep category E (R9 form-LIT / coeff-author boundary applies — form is
     literature-anchored "self-selected music boosts nostalgia", but the 1.2
     numeric value is engine operationalization).
  2. **Engine bug disclosure candidate:** the code comment "d=0.88" misstates
     the effect-size metric reported in Sakakibara 2025 (correct: Cohen's
     r=0.880). This is a documentation defect, not a numeric bug — the 1.2
     value itself is engine-chosen regardless. Per MEMORY doctrine "Engine
     FROZEN — never modify Musical_Intelligence/", disclose in §Limitations
     of C³-Cognition companion paper rather than patch.
- **Audit agent:** Agent 3

---

## ESC-2 — NEMAC `_SELF_SELECTED_BOOST = 1.2` (temporal_integration.py)

- **Constant ID:** A3_03832
- **File:** `brain/functions/f5/mechanisms/nemac/temporal_integration.py:81`
- **Name + Value:** `_SELF_SELECTED_BOOST = 1.2`
- **Tentative category:** E (ENGINEERING-CHOICE) with **PARTIAL** verification
- **Tentative confidence:** MEDIUM
- **Issue:** Duplicate copy of the same `_SELF_SELECTED_BOOST = 1.2` constant
  defined in `extraction.py:67` (ESC-1). Same provenance analysis applies.
  Engine has the value re-declared in two NEMAC layer files instead of
  importing from a shared module — minor DRY violation but not load-bearing.
- **Web search performed:** Yes — same web verification chain as ESC-1
- **Web search outcome:** PARTIAL
- **Verification source attempted:** Sakakibara et al. 2025 *Sci Rep* PMC12405522
- **Recommended resolution:** Same as ESC-1. Both rows tagged E PARTIAL.
- **Audit agent:** Agent 3

---

## Note on scope mismatch with launch prompt

The launch prompt listed **IUCP (Inverted-U Cognitive Preference / Berlyne
4·x·(1−x) kernel)** as a critical F5 mechanism for me to verify. **IUCP lives
in F6, not F5** in the frozen engine (path:
`brain/functions/f6/mechanisms/iucp/`). Since my path-filter scope is
`brain/functions/f4/*` OR `brain/functions/f5/*`, IUCP is **outside my
audit scope**. The Berlyne kernel verification therefore falls to the agent
covering F6 (per `INVESTIGATION-RULES.md` §4 Agent 3 = F6+F7+F8, though my
launch prompt re-numbered me to F4+F5). I did perform a one-shot Berlyne
WebSearch as a sanity check while in-flight:

- Query: `"Berlyne 1971 Aesthetics and Psychobiology" inverted-U "4x(1-x)" hedonic value formula`
- Outcome: **NEGATIVE on the explicit `4x(1−x)` formula**; Berlyne's inverted-U
  hedonic-tone *concept* is widely cited (Frontiers 2016 Marin review, PMC5095118
  re-analysis) but the specific algebraic kernel `4·x·(1−x)` does not surface
  in literature snippets. This matches `context_brief.md` §7 risk #5: the
  inverted-U concept is Berlyne; the `4·x·(1−x)` algebraic form is engine
  operationalization. Recommend the F6 auditor tag the literal `4` and
  `1 - x` operations in `iucp/extraction.py:80-86` as **STRUCTURAL** (form,
  `0 ≤ x ≤ 1` parabola maxed at 0.5 mapping), NOT LIT-VERBATIM. This finding
  is recorded here for the reconciliation pass (Agent 6) — not in scope CSV.

---

## Pattern-batching audit log

Per Rule R4 (per-constant independence), every row in `agent_3_audit.csv`
has a distinct `reason` string that names its specific mechanism, value,
and role. Bulk patterns (H3DemandSpec horizon/morph/law indices, RegionLink
weights, Citation years) share **doctrine-anchored category templates** but
each row's reason string interpolates the specific name/value/mech, so no
two rows have identical text. Confirmed by row-spot-check on 5 mechs (MMP,
VMM, AAC, NEMAC, TAR).
