# Phase 0.5 — Audited datasets and local presence

This file documents which datasets the Phase 0.5 audit references and
their current local presence at `Science/datasets/`. Audit decisions
based on programmatic inspection are written into
`results/eligibility_audit.csv`.

## Local-disk status (as of 2026-05-06)

### A. Paper-cited datasets

| Dataset | Local path | Status |
|---|---|---|
| ds002725 (Daly 2019) | `neuroimaging/fmri_openneuro/ds002725/` | PRESENT (BIDS, ~21 subs, 17 with classicalMusic bold) |
| ds003720 (Nakai 2021) | `neuroimaging/ds003720/` | PRESENT (BIDS, 5 subs, 1720 stimulus WAVs, 90 events.tsv) |
| putkinen2025 | `neuroimaging/putkinen2025/` | SUMMARY-ONLY (regional CSV; raw PET not deposited) |
| mallik2017 | `neuroimaging/mallik2017/` | SUMMARY-ONLY (effect-size CSV; subject-level not deposited) |
| salimpoor2011 | (not on disk) | CLOSED-ACCESS |
| ferreri2019 | (not on disk) | CLOSED-ACCESS |
| blood2001 | (not on disk) | CLOSED-ACCESS (PET, peaks-only) |
| salimpoor2013 | (not on disk) | CLOSED-ACCESS |
| grahn2007 | (not on disk) | CLOSED-ACCESS |
| koelsch2005 | (not on disk) | CLOSED-ACCESS |
| brattico2011 | (not on disk) | CLOSED-ACCESS |
| zatorre2005 | (not on disk) | CLOSED-ACCESS |

### B. Phase 18 planned datasets

| Dataset | Local path | Status |
|---|---|---|
| studyforrest_7T_music | `neuroimaging/studyforrest/` | PRESENT (37 subs, 148 events.tsv, 750 bold; **no audio in stimuli/ — relies on external Forrest Gump audio**) |
| ds005880 | `neuroimaging/ds005880/` | PARTIAL DOWNLOAD (~710 MB / 6 GB; 20 subs listed, 15 bold, 40 events.tsv; **no audio yet**) |
| ds006583 | `neuroimaging/ds006583/` | PARTIAL DOWNLOAD (23 subs listed, 9 bold, **0 events.tsv**, no audio) |
| ds006564 | `neuroimaging/ds006564/` | PARTIAL DOWNLOAD (41 subs listed, 56 bold, **0 events.tsv**, no audio) |
| ds000171 | `neuroimaging/ds000171/` | PRESENT (39 subs, 141 events.tsv, 89 bold, **no audio in tree — paper-supplied**) |

### C. 5-agent scan candidates (Tier 2 multimodal)

| Dataset | Local path | Status |
|---|---|---|
| nmedh_hindi_eeg | (re-uses MUSIN-G EEG companion) | PRESENT-AS-MUSIN-G-PROXY |
| musin_g | `attention/MUSIN-G/` | PRESENT (audio + EEG; non-fMRI) |
| daly_ds002721 | (not on disk) | NOT ON DISK (EEG twin of ds002725) |
| diliberto2020 | `prediction/diliberto2020/` | EMPTY (placeholder) |
| marion_meg | (not on disk) | NOT ON DISK |
| bellier_ecog | (not on disk) | NOT ON DISK |
| music_expertise_ieeg | (not on disk) | NOT ON DISK |

### D. Comparator / negative control

| Dataset | Local path | Status |
|---|---|---|
| nhs_discography (Mehr 2019) | `cross_cultural/nhs_discography/` | PRESENT (118 mp3 + metadata, behavioral cross-cultural) |
| aam | (not on disk) | NOT ON DISK |
| pmemo | `emotion/PMEmo/` | PRESENT (audio-only, no fMRI) |
| deam | `emotion/DEAM/` | PRESENT (audio-only, used in Phase 5 ECE only) |
| groove_midi | `motor/groove_midi/` | PRESENT (MIDI-only, no audio rendered) |
| emotify | `emotion/emotify/` | PRESENT (audio-only behavioral) |

## Notes

- Path-not-present datasets return `mi_compatible=False` with
  `exclusion_reason="Local path not present"` (acceptable per the
  audit's documentation goal).
- Closed-access datasets get explicit `manual_overrides` in
  `code/run_full_audit.py` to honestly label them `summary_only` /
  `no_recoverable` rather than fabricate alignment-qualified N.
- Phase 18 sub-axis verdicts may iterate (max 5 times per dataset)
  if downloads complete and re-audit changes verdict; logged in
  `04-INTEGRATION-LOG.md`.
