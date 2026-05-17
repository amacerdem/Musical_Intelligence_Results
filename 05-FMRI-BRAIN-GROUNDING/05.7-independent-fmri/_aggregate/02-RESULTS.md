# Phase 05.7 — Aggregate Results

**Status:** PRE-REG-FROZEN (2026-05-07). Aggregate execution awaits
external stimulus audio fetches for the two ELIGIBLE sub-axes; the
other three sub-axes are NON-ELIGIBLE per the Phase 0.5 entry-gate.

## Headline

|  | Pre-registered | NON-ELIGIBLE | EXEC-PENDING | EXECUTED |
|---|---|---|---|---|
| Sub-axes (5) | 2 | 3 | 2 | 0 |
| Subjects (target 148) | 48 | 84 | 48 | 0 |

## Per sub-axis

| Sub-axis | Status | Reason |
|---|---|---|
| 18.1 — studyforrest 7T music genres (N = 20) | PRE-REG-FROZEN, EXEC-PENDING | Audio fetch via `datalad get artifact/7T_musicperception/stimulus/` (40 genre WAVs, ~10 MB) |
| 18.2 — ds005880 Diminished 7th (N = 20) | NON-ELIGIBLE | events.tsv onsets are integer-second only; the engine requires sub-TR (172.27 Hz) alignment |
| 18.3 — ds006583 Affective Transitions (N = 23) | NON-ELIGIBLE | events.tsv files are absent on disk after partial public-data download |
| 18.4 — ds006564 Naturalistic film with music (N = 41) | NON-ELIGIBLE | events.tsv files absent; naturalistic-film paradigm typically uses continuous audio without per-trial events |
| 18.5 — ds000171 Music + depression (N = 39: 19 MDD + 20 ND) | PRE-REG-FROZEN, EXEC-PENDING | Lepping et al. 2016 supplementary stimulus audio (Sci. Rep. doi:10.1038/srep24818) is not part of the OpenNeuro release |

## Why NON-ELIGIBLE is not FAIL

A NON-ELIGIBLE verdict reflects the dataset's BIDS curation or recording
paradigm being incompatible with the engine's frame-level (172.27 Hz)
input requirement. It is an infrastructure exclusion, not an
analytical failure. Phase 0.5 ran the eligibility audit before any
analysis was attempted; the 3 NON-ELIGIBLE sub-axes here are part of
the broader set of datasets that Phase 0.5 classified as
non-mi-compatible.

## Why EXEC-PENDING is not PARTIAL

EXEC-PENDING is a status marker, not an analytical verdict. The
pre-registrations for 18.1 and 18.5 are frozen with locked decision
rules. When the audio arrives, the pipeline executes deterministically
and produces a verdict (POSITIVE, PARTIAL, or NEGATIVE). The
pre-registration discipline is what makes a future POSITIVE verdict
load-bearing: there is no parameter freedom to tune the analysis to
the data after seeing it.

## What Phase 05.7 contributes today

Even without execution, Phase 05.7 delivers:

1. **Entry-gate transparency.** 32 datasets audited at Phase 0.5;
   4 classified as mi-compatible (ds002725, ds003720, studyforrest,
   ds000171); 28 excluded with explicit reasons recorded in
   `00.5-fmri-eligibility/results/`.
2. **Frozen pre-registrations** for two sub-axes that an independent
   auditor can execute with no parameter-tuning freedom.
3. **Paper revision item R5** (READY) — a §Future directions hint
   that a prospective fMRI experiment is the natural next step.
4. **Paper revision item R11** (READY) — a §Limitations footnote
   disclosing the Phase 05.7 freeze state so reviewers can verify it
   themselves.

## What Phase 05.7 will contribute when audio arrives

When the external audio fetches for 18.1 and 18.5 complete:

- **18.1 studyforrest:** F1 routing test on N = 20 at 7T resolution.
  Wall ≤ 15 minutes.
- **18.5 ds000171:** F5 + F6 clinical contrast on the alignment-
  qualified N = 28 subset. Wall ≤ 20 minutes.

Combined: +48 fMRI subjects across two independent datasets, ≤ 35
minutes of execution time on consumer hardware.

## Aggregate verdict

The Phase 05.7 aggregate manifest carries three claims:

| Claim | Verdict |
|---|---|
| `C-PH18-AGG-ENTRYGATE` | PASS (Phase 0.5 entry-gate verbatim) |
| `C-PH18-AGG-PREREG` | PASS (2 frozen pre-registrations) |
| `C-PH18-AGG-EXEC` | EXEC-PENDING |

Across the 5 sub-axis manifests plus 1 aggregate manifest, Phase 05.7
records: 5 PASS, 0 FAIL, 3 EXEC-PENDING, 3 NON-ELIGIBLE. The Phase 17
ledger merges these into the unified claims table.
