# Phase 00.2 Methodology — Operationalized Eligibility Criteria

> **Locked alongside `03-PRE-REGISTRATION.md`. Each criterion below has a
> deterministic implementation in `code/audit_helpers.py`.**

## Why eligibility, not N

MI is a frame-level (172.27 Hz), raw-audio-locked architecture. Standard
music-fMRI datasets sample BOLD at TR ≈ 2 s = 0.5 Hz, so testing MI on a
public dataset requires:

- **(a) recoverable raw stimulus audio** (the engine consumes raw audio);
- **(b) sample-accurate event onset/duration timing** (so 5.8 ms-frame BOLD
  predictions can be aggregated to TR-bin BOLD);
- **(c) MNI-normalized derivatives or raw-data-permitting preprocessing**
  (so cross-subject voxelwise encoding lands on a shared atlas).

A "high-N music-fMRI" dataset that fails (a), (b), or (c) cannot be used by
MI even though the scan is technically usable for ROI-mean GLM analyses.
The binding eligibility criterion for MI validation is **stimulus-lockability**,
NOT N.

## Per-criterion computation

### `audio_available`

Walk the BIDS root for any of the audio extensions
`{*.wav, *.mp3, *.aiff, *.flac, *.aif, *.ogg}` under `stimuli/`,
`sourcedata/stimuli/`, or anywhere in the tree. If absent, check
`dataset_description.json` for an external `DatasetDOI` or `RelatedDOI`.

Verdict ∈
- `yes_in_dataset` — audio files materialised in the dataset tree.
- `yes_external_DOI` — paper / dataset references a Zenodo / OSF link.
- `summary_only` — published summary (effect sizes, region peaks) exists
  but raw audio is not deposited.
- `no_recoverable` — no audio in dataset and no external link discovered.

### `exact_timing`

Parse all `*_events.tsv` files. Compute
`min(positive onset_diff)` across rows in the first available events file.

- If `min_diff < 1.0 s` → `events_tsv_sub_TR` (sub-TR resolution).
- Else if events.tsv exists but resolution ≥ 1 s → `events_tsv_TR_only`.
- Else if no events.tsv but timing recoverable from non-BIDS logs (paper
  Methods, supplementary) → `recoverable_from_logs`.
- Else → `none_recoverable`.

### `mni_derivative`

Check `derivatives/fmriprep/sub-*/func/` for files matching the pattern
`*MNI152NLin2009cAsym*.nii.gz`. If found → `present`.

If raw (T1w + bold) is present but no derivative → check fmriprep
feasibility (T1w present + bold present) → `runnable_via_fmriprep`.

If neither → `not_feasible`.

If the modality is non-fMRI (PET / EEG / MEG / behavioral) → `not_applicable`.

### `n_qc_pass`

For Phase 00.2 we report the lower bound that is programmatically
estimable without running fmriprep:

- Number of `sub-*` directories with at least one `*_bold.nii.gz` (or
  `*_bold.nii`) **AND** at least one task-matching `*_events.tsv` (or a
  shared task-level events.tsv that applies).

Real motion-FD QC requires running fmriprep or extracting confound files;
that is deferred to Phase 11 for `ds002725` and to each phase consumer for
the others.

### `n_alignment_qualified`

Of `n_qc_pass` subjects, the intersection with subjects whose `events.tsv`
matches stimulus audio onset within ±100 ms.

Phase-0.5 conservative heuristic:

- If `audio + sub-TR events.tsv` both present → assume `n_qc_pass`
  subjects qualify (their events.tsv applies; audio is single canonical
  stimulus or per-trial audio with deterministic onset).
- If `events.tsv` resolution > 1 s → 0 (cannot do frame-level alignment
  even in principle).
- If audio only `summary_only` or `external_DOI` → manual confirmation
  required (logged in `04-INTEGRATION-LOG.md`).
- If path not on local disk → `-1` (unknown; documented exclusion).

The full per-subject onset-matching pass for `ds002725` is in Phase 11.

## Manual overrides for closed-access datasets

Closed-access datasets (Putkinen, Mallik, Salimpoor, Ferreri, Blood,
Salimpoor 2013, Grahn, Koelsch, Brattico, Zatorre) cannot have their
audio / events / MNI derivatives inspected programmatically. The audit
applies `manual_overrides` from the `DATASET_REGISTRY` in
`code/run_full_audit.py`, recording:

- `audio_available = "summary_only"` or `"no_recoverable"`,
- `exact_timing = "none_recoverable"`,
- `mni_derivative = "not_applicable"`,
- `n_qc_pass = -1`, `n_alignment_qualified = -1`,
- `exclusion_reason` with explicit `Closed-access` flag,
- `mi_compatible = False`.

This is the honest verdict required by the user-validated `MI_fMRI_validasyon_notlari.md`.

## Iteration policy

- Per-dataset audit decisions can iterate at most 5 times before
  escalation. Each iteration is logged in `04-INTEGRATION-LOG.md`
  (one bullet per change).
- Loosening a criterion (e.g., `±100 ms → ±200 ms` onset tolerance)
  requires a master-plan revision (revision 3+).

## Output schema

`code/schema_eligibility.json` (JSON Schema draft-07, additionalProperties:false)
with required fields:

```
dataset_id, modality, n_dataset_level, audio_available, exact_timing,
mni_derivative, n_qc_pass, n_alignment_qualified, mi_compatible,
exclusion_reason, phase_consumer, notes
```

Test: `_infra/tests/test_manifests.py::test_eligibility_schema_validates`.
