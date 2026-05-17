# Phase 00.2 — V-fMRI Eligibility Audit

**Status:** CLOSED 2026-05-06
**Verdict:** POSITIVE (6/6 C-ELIG claims PASS)
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217` (frozen)
**Seed:** 20260506005

## Quick reference

| Item | Value |
|---|---|
| Datasets audited | 32 |
| MI-compatible | 4 |
| Excluded | 28 |
| ds002725 alignment-qualified N | **17** (vs dataset-level N=21) |
| ds003720 framing | **routing-ablation** (not population estimate) |
| Phase 18 sub-axis verdicts | 18.1 ELIG, 18.2 NON-ELIG, 18.3 NON-ELIG, 18.4 NON-ELIG, 18.5 ELIG |

## Phase consumers (entry-gate tables)

### Phase 11 (Pre-reg mech×region encoding, ds002725)

| Field | Value |
|---|---|
| Dataset | ds002725 |
| mi_compatible | True |
| n_alignment_qualified | 17 |
| Phase 11 minimum N | ≥12 |
| Verdict | **ENTRY-GATE PASS** (17 ≥ 12) |
| Note | No T1w on disk; preproc uses EPI-based normalization (existing pipeline at `Bold-fMRI/ds002725/02_bold_preproc/`) |

### Phase 12 (Cross-subject voxelwise, ds003720)

| Field | Value |
|---|---|
| Dataset | ds003720 |
| mi_compatible | True |
| n_alignment_qualified | 5 |
| Framing requirement | "routing-ablation" present in notes |
| Verdict | **ENTRY-GATE PASS** with routing-ablation framing locked |

### Phase 18 (5 sub-axes)

| Sub-axis | Dataset | Verdict | Reason |
|---|---|---|---|
| 18.1 | studyforrest_7t_music | **ELIGIBLE** (cond.) | Audio external DOI; 20 subs at 7T |
| 18.2 | ds005880 | **NON-ELIGIBLE** | Partial DL + integer-second TR-only events |
| 18.3 | ds006583 | **NON-ELIGIBLE** | Partial DL; 0 events.tsv on disk |
| 18.4 | ds006564 | **NON-ELIGIBLE** | Partial DL; 0 events.tsv on disk |
| 18.5 | ds000171 | **ELIGIBLE** (cond.) | Audio external (Lepping 2016 supp.); 39 subs |

ELIGIBLE sub-axes (18.1, 18.5) require external audio fetch to convert
"conditional" into actually runnable. NON-ELIGIBLE sub-axes are accepted
by the Phase 18 plan; re-audit is encouraged when downloads complete.

## Files

```
00.5-fmri-eligibility/
├── README.md                        ← you are here
├── 00-PLAN.md                       (sub-plan; pre-existing)
├── 00-METHODOLOGY.md                (operationalization, LOCKED)
├── 01-PROVENANCE.md                 (chain to MI_fMRI_validasyon_notlari.md + 5-agent scan)
├── 02-RESULTS.md                    (verdicts + headline numbers)
├── 03-PRE-REGISTRATION.md           (LOCKED 2026-05-06)
├── 04-INTEGRATION-LOG.md            (per-dataset iteration log)
├── code/
│   ├── audit_helpers.py
│   ├── audit_dataset.py
│   ├── run_full_audit.py            (orchestrator with DATASET_REGISTRY)
│   ├── render_supplementary_table.py
│   ├── visualize_eligibility.py
│   ├── aggregate.py
│   └── schema_eligibility.json      (JSON Schema draft-07)
├── data/README.md                   (per-dataset local-disk presence)
├── results/
│   ├── eligibility_audit.csv        (32 rows, schema-valid)
│   ├── eligibility_audit.json       (full audit + metadata)
│   ├── per_dataset_audit_log.jsonl  (one JSON line per dataset)
│   └── 00.5_eligibility_manifest.json   (claim-level manifest)
├── figures/
│   ├── eligibility_matrix.png
│   ├── alignment_qualified_n_bar.png
│   └── exclusion_reasons_pareto.png
└── paper-evidence/
    ├── README.md
    └── Supplementary_Table_S-Eligibility.tex
```

## Reproducibility

```bash
cd "Science/V-Reproduction/00.5-fmri-eligibility"
python code/run_full_audit.py
python code/render_supplementary_table.py
python code/visualize_eligibility.py
python code/aggregate.py
```

The full audit is deterministic (no RNG); seed 20260506005 is recorded
for compliance.

## Paper revision implications (R1–R5)

These 5 revisions will land in a single paper-revision pass at Phase 17
(Zenodo deposit time):

- **R1** §Methods §Dataset eligibility (NEW subsection) cites
  `Supplementary_Table_S-Eligibility.tex`.
- **R2** ds002725 alignment-qualified N=17 disclosed in figure caption +
  body + §Limitations.
- **R3** ds003720 explicitly framed as routing-ablation.
- **R4** sub-08 illustrative-only tightening (Phase 13).
- **R5** §Future directions: prospective fMRI experiment hint.

## Pytest

`_infra/tests/test_manifests.py` — **17 PASS** (was 16 + 1 new
`test_eligibility_schema_validates`).

```bash
cd Science/V-Reproduction
pytest _infra/tests/test_manifests.py -v
```
