# Agent 6 — Escalation Queue

**Engine SHA:** `318eb2f5...`
**Scope:** `brain/functions/f7/*` + `brain/functions/f8/*` (2,998 constants)
**Date:** 2026-05-17
**Total escalations:** 2 (both Category E with PARTIAL outcome per Rule R9)

Escalation flag is reserved for `LOW` confidence + ambiguous-category cases. F7+F8
constant population is dominated by structural topology indices and engineering
mixer weights with HIGH confidence. The two escalations below cover the only two
constants in scope whose comment text references load-bearing literature with a
specific numeric value, where web-search verification was NEGATIVE/PARTIAL for
bit-exact publication of the coefficient.

---

## ESC-1

- **Constant ID:** A6_01290
- **File:** `brain/functions/f7/mechanisms/peom/temporal_integration.py:42`
- **Name + Value:** `_TAU = 4.0`
- **Tentative category:** E (E5 operational scaling)
- **Tentative confidence:** MEDIUM
- **Issue:** Comment reads `# seconds -- period convergence time constant (Thaut 2015)`.
  PEOM extraction docstring explicitly states: "Implements Thaut et al. (2015,
  1998b) period entrainment model: f01: period entrainment from beat/onset
  periodicity at 1s ... f02: velocity optimization from coupling periodicity".
  The dP/dt = α·(T − P(t)) period-entrainment differential model is form-LIT
  (Thaut neurologic music therapy literature). However, the specific τ = 4.0 s
  time-constant is not bit-exact published in Thaut 2015 Front Psychol — that
  paper is a qualitative review of neurobiological foundations and does not
  publish a τ = 4.0 s coefficient.
- **Web search performed:** Yes, 1 attempt
  - Query: `Thaut 2015 period entrainment tau 4 seconds dP/dt rhythmic auditory motor coupling`
  - Outcome: Paper located (Thaut, McIntosh & Hoemberg 2015 Front Psychol 5:1185)
    but PARTIAL verification — the period-entrainment differential framework is
    in the cited corpus, but no explicit τ = 4.0 s appears in abstract / search
    snippets / standard citations.
- **Web search outcome:** PARTIAL
- **Verification source attempted:** Thaut et al. 2015 Front Psychol 5:1185
- **Recommended resolution:** **Keep as E with PARTIAL per Rule R9** (form-LIT,
  coefficient author re-parameterization). If a stricter reviewer wants this
  upgraded to B (LIT-DERIVED), the audit team must locate an Egerton/Thaut 1998
  primary paper publishing the time-constant explicitly; absent that, E is the
  correct conservative attribution.
- **Audit agent:** Agent 6

---

## ESC-2

- **Constant ID:** A6_02538
- **File:** `brain/functions/f8/mechanisms/esme/extraction.py:78`
- **Name + Value:** `_ALPHA = 1.5`
- **Tentative category:** E (E5 operational scaling)
- **Tentative confidence:** MEDIUM
- **Issue:** Module comment reads `# -- Trainable alpha for expertise enhancement
  ---`. The word "trainable" explicitly flags this as an author-chosen / fitted
  hyperparameter (not a published value). In ESME f04 the value multiplies
  max(f01, f02, f03). Documentation cites Criscuolo 2022 ALE meta (k=84, N=3005)
  for the gradient principle, but the meta-analysis does not publish an α = 1.5
  scaling factor.
- **Web search performed:** Yes, 1 attempt
  - Query: included along with verification of Pantev 2001 / Koelsch 1999 /
    Criscuolo 2022 literature anchors for F8 ESME
  - Outcome: NEGATIVE — the cited literature does not publish α = 1.5 as a
    coefficient. Author choice operationalising the "gradient principle".
- **Web search outcome:** NEGATIVE (for bit-exact value); POSITIVE for the
  conceptual anchor (expertise gradient principle, Pantev/Koelsch/Vuust/Criscuolo
  corpus).
- **Verification source attempted:** Criscuolo 2022 *Cereb Cortex* ALE; Pantev 2001
  *Neuroreport*; Koelsch 1999 *Neuroreport*
- **Recommended resolution:** **Keep as E with PARTIAL.** In-code comment
  "trainable alpha" semantically marks this as engineering choice. Note: under
  the **2026-05-16 zero-calibration doctrine**, "trainable" should not be
  interpreted as "fit against held-out data" (audit canonical: zero of 16,191
  numeric constants calibrated against cognitive data). It is an author-chosen
  amplification factor; the term "trainable" in the comment is a developmental
  artifact and may warrant cleanup or rename to clarify intent. Recommend manual
  review.
- **Audit agent:** Agent 6

---

## Pattern-level notes (no individual escalations)

The following classes of constants in F7+F8 are confidently attributed but worth
noting for cross-agent reconciliation:

1. **TAU class-attr in beliefs (8 instances in scope, values 0.55, 0.60, 0.65,
   0.70, 0.95).** Author-chosen belief-inertia coefficients (base = (1−TAU)·prev
   + TAU·BASELINE). No literature anchor in code comments; correctly tagged
   E5 HIGH. Per Doc 04 §F adaptation table, the Friston 2005 precision-weighted
   update *template* is cited; individual TAU values are author choice. The
   variation across beliefs (some 0.55, some 0.95) reflects belief-specific
   intended forgetting-rate, not different literature anchors.

2. **W_TREND/W_PERIOD/W_CTX predict-equation weights (24 instances across 8
   belief files, all 0.05/0.03/0.02).** Per context_brief §3, §8: explicit
   exclusion from F-list — these are E4 mixer weights, NOT F. Constant
   identical values across all 8 belief files indicate a shared template, not
   per-belief calibration.

3. **RegionLink author-normalised weights (95 instances, values in [0.55,
   0.95] Likert range).** Per context_brief §7.3: author-normalised over a
   literature-cited edge set. Edge identity (e.g. STG ↔ BCH) is LIT-cited but
   weight magnitude (0.85) is author choice. All tagged E4 HIGH.

4. **NeuroLink author-normalised weights (14 instances).** Same pattern as
   RegionLink; all E4 HIGH.

5. **`brain/functions/f7/mechanisms/ctbb/temporal_integration.py:45
   TAU_DECAY = 1800.0`.** 30-minute iTBS LTP-like facilitation window. The
   iTBS literature describes a facilitation window (typical effects in the
   tens-of-minutes range), but no specific paper publishes τ=1800.0 s.
   Author-chosen, tagged E5 HIGH (no escalation flag — comment is qualitative
   reference, not load-bearing literature claim).

6. **`brain/functions/f8/mechanisms/slee/temporal_integration.py:51 _TAU_PATTERN
   = 3.0`.** Author-chosen pattern-memory integration time-constant; no
   in-comment citation; E5 HIGH.

7. **F category strictly 0 in F7+F8 scope.** This is the protocol-required
   outcome — F (HAND-SPECIFIED-DISCLOSED) is closed at the 7 reward weights
   in `brain/reward.py`. The audit confirms zero leakage into F7+F8 mechanism
   files.
