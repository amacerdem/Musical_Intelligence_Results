# Phase 0 — Infrastructure — CLOSED 2026-05-06

## Deliverables shipped

- [x] `01-CONVENTIONS.md` — locked folder template + manifest schema + verdict types
- [x] `02-ITERATION-POLICY.md` — debug protocol + "no first low number" rule + tolerance categories
- [x] `_infra/manifests/engine_head.json` — pinned at 318eb2f5 (frozen since pre-V1)
- [x] `_infra/manifests/seed_registry.json` — frozen for all 18 phases (00-17), 3 inherited from V3/V5/V6
- [x] `_infra/manifests/claim_schema.json` — JSON Schema draft-07 with additionalProperties:false, tolerance regex, verdict enum
- [x] `_infra/engine/runner.py` — bit-identical determinism on R³ + C³ + RAM + neuro + beliefs (stronger than paper's |Δρ| ≤ 8.8×10⁻⁵; true bit-equality)
- [x] `_infra/stats/fdr.py` — BH, BB hierarchical, Bonferroni (11 tests)
- [x] `_infra/stats/permutation.py` — 4 null types, plus-one convention everywhere (11 tests)
- [x] `_infra/stats/bootstrap.py` — BCa CI with jackknife acceleration, song-block bootstrap (9 tests)
- [x] `_infra/stats/ridge.py` — LOSO + banded ridge wrapper (himalaya 0.4.10 pinned, 5 PASS + 1 SKIP)
- [x] `_infra/stats/cka.py` — linear CKA (Kornblith 2019, 6 tests)
- [x] `_infra/figures/reliability_panel.py` — N-panel calibration (5 tests)
- [x] `_infra/figures/forest_plot.py` — per-pair forest plot (6 tests)
- [x] `_infra/figures/topology_match.py` — distance histogram + threshold (5 tests)
- [x] 6 missing dataset acquisitions: Saraga 1.5 (partial — downloading), NHS Discography, Mridangam Stroke, QM2020 (alias), Putkinen 2025 (summary), Mallik 2017 (summary)
- [x] `_infra/tests/` — pytest suite, 82 PASS + 1 SKIP, all sections approved
- [x] `MASTER-VERDICT.md` — skeleton populated with Phase 0 status + 17 pending phases

## Acceptance criteria

- [x] Pytest 100% PASS on `_infra/tests/` (82 PASS + 1 expected SKIP)
- [x] Engine runner produces bit-identical output across multiple calls (proven on R³ + C³ + RAM + neuro + beliefs — STRONGER than paper claim)
- [x] All 6 missing datasets either downloaded OR documented honestly with truthful acquisition state per iteration policy
- [x] Conventions and iteration policy reviewed, locked, and committed

## Iteration discipline applied

The locked iteration policy was exercised during Phase 0 itself:

- Section A: 5 fixes after quality review (iteration-cap reconciliation, FDR-row tolerance unit clarity, p-value floor for paper p<10⁻⁴, debug-protocol stopping rule, seed format disambiguation)
- Section B: 4 Important + 3 Minor fixes (tolerance regex, additionalProperties:false, deviation-array alignment, git_commit_hash pattern, 5 negative tests, dropped REPO dead code, engine HEAD duplication note)
- Section C: 5 fixes (silent except → stderr WARN + strict kwarg, full-layer determinism test, beliefs-subset docstring, stable WAV tie-break, truthful seed docstring)
- Section D: CRITICAL fix (shuffled_link_null was mathematically degenerate; reimplemented with uniform per-edge null, variance verified) + 5 Important + 2 Minor
- Section E: APPROVED first round
- Section F: CRITICAL fix (Saraga DATASET.md misrepresented acquisition state; corrected to truthful PARTIAL with resume command)

This iteration discipline IS the policy — every phase will exercise it.

## Open items deferred

- Saraga 1.5 Hindustani download still in progress (~459 MB / 4109 MB at close; background curl PID 45264). Phase 14 entry condition includes verifying download completed.
- Per-dataset loaders are built **per-phase** (not in Phase 0) since each loader has phase-specific shape/normalization. Will be created or copied from V1/V2/V3/V6 as each phase begins.
- OSF deposit deferred to Phase 17 per master plan.
- Nested-repo workaround at `Science/datasets/cross_cultural/` (pakistan-chords vendor): canonical DATASET.md files mirrored at `Science/datasets/_v_reproduction_pointers/cross_cultural/` for git tracking. Long-term cleanup deferred.

## Phase 1 entry condition

`MASTER-VERDICT.md` Phase 0 row reads `CLOSED`. Phase 1 sub-plan can be requested.
