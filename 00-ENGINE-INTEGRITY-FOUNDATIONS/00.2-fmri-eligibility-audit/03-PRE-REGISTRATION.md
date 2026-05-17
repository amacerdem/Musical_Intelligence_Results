# Phase 00.2 V-fMRI Eligibility Audit — Pre-registration (LOCKED 2026-05-06)

> **Status:** LOCKED before audit code runs. No criterion change after this commit
> without master-plan revision 3+.

## Datasets to audit (≥30, frozen at this commit)

### A. Paper-cited (must audit)

1. `ds002725` — Daly 2019, Mendelssohn (paper §Phase 11)
2. `ds003720` — Nakai 2021, voxelwise (paper §Phase 12)
3. `putkinen2025` — μ-opioid PET (paper §F6 pharma)
4. `mallik2017` — naltrexone (paper §F6 pharma)
5. `salimpoor2011` — caudate-NAcc lag (paper §F6)
6. `ferreri2019` — levodopa>placebo>risperidone (paper §F6 pharma)
7. `blood2001` — chills (paper §RAM topology)
8. `salimpoor2013` — high>low reward (paper §RAM)
9. `grahn2007` — beat>non-beat (paper §RAM)
10. `koelsch2005` — irregular>regular (paper §RAM)
11. `brattico2011` — happy vs sad (paper §RAM)
12. `zatorre2005` — imagery>rest (paper §RAM)

### B. Phase 18 planned (must audit)

13. `studyforrest_7T_music` — 7T music genre extension (ds000113 derivative)
14. `ds005880` — Diminished 7th chord
15. `ds006583` — Affective Transitions
16. `ds006564` — Naturalistic film with controlled musical information
17. `ds000171` — Music + depression

### C. 5-agent scan Tier 1+2+3 candidates (audit; expected mostly excluded)

18. `nmedh_hindi_eeg` — NMED-H Hindi EEG
19. `daly_ds002721` — EEG twin of ds002725
20. `di_liberto_bach` — Di Liberto Bach EEG
21. `marion_meg` — Marion / Di Liberto MEG (eLife 2023)
22. `musin_g` — MUSIN-G ds003774
23. `bellier_ecog` — Bellier Pink Floyd ECoG (Zenodo 7876019)
24. `music_expertise_ieeg` — Music expertise iEEG+EEG (Nat Commun 2025)

### D. Comparator / negative-control datasets (audit; expected mostly excluded)

25. `mehr2019_nhs` — NHS Discography (cross-cultural, behavioral)
26. `aam` — Audio-Music Affective
27. `pmemo` — PMEmo (audio-only, behavioral)
28. `deam` — DEAM (audio-only; used in Phase 5 ECE only)
29. `groove_midi` — Groove MIDI (motor)
30. `emotify` — Emotify (audio-only behavioral)
31. `gold2019_absolute_pitch` — Gold 2019 absolute pitch fMRI (audit-only)
32. `ds001417` — generic music-fMRI (audit-only)

**Total registry size: 32 datasets** (≥30 satisfied).

## Eligibility criteria (LOCKED)

A dataset is `mi_compatible=True` iff ALL of:

- **(a)** `audio_available ∈ {yes_in_dataset, yes_external_DOI}`
- **(b)** `exact_timing ∈ {events_tsv_sub_TR, recoverable_from_logs}`
- **(c)** `mni_derivative ∈ {present, runnable_via_fmriprep}`
- **(d)** `n_alignment_qualified ≥ 1`

Any failure on (a–d) yields `mi_compatible=False` with the failing criterion(a)
recorded in `exclusion_reason`.

## Alignment-qualified definition (LOCKED)

A subject is `alignment_qualified=True` iff ALL of:

- BIDS `events.tsv` present for the subject's task runs (or shared task-level
  events.tsv applies).
- Mean `abs(stimulus_onset − events_onset) ≤ 100 ms` across all relevant runs.
  At Phase 00.2 this is verified by event resolution check (sub-TR
  `min_diff < 1.0 s`); per-subject onset matching is deferred to Phase 11.
- TR consistency: no missing volumes detected.
- Motion FD mean < 0.5 mm. (At Phase 00.2, motion is estimated by lower bound
  = number of subs with bold + events; full FD computation is in Phase 11.)
- MNI152NLin2009cAsym warp QC passes default fmriprep criteria, OR the dataset
  is `runnable_via_fmriprep` (T1w + bold present).

## Decision rule

- **POSITIVE:** ≥30 datasets audited; ≥6 paper-cited datasets have explicit
  `mi_compatible` verdict; ≥3 datasets explicitly excluded with documented
  reason; `ds002725`, `ds003720`, and the 5 Phase 18 sub-axes all have
  entry-gate verdicts.
- **NEGATIVE:** <20 datasets audited OR <2 explicit exclusions OR ANY of
  {ds002725, ds003720, Phase 18 sub-axis} missing entry-gate verdict.
- **AMBIGUOUS:** 20–29 datasets audited (escalate; may need to expand
  candidate list).

## Seeds

- **Primary:** `20260506005` (per `_infra/manifests/seed_registry.json`
  `phase_00_5`)
- All audits are deterministic (no RNG); seed listed for compliance.

## Iteration policy

- Per-dataset audit decisions can iterate at most 5 times (e.g., revise
  criteria after discovering BIDS sidecar issues).
- Audit-criteria changes after Phase 00.2 close require a master-plan revision
  (revision 3+).

## Provenance chain

- User-validated framing: `MI_fMRI_validasyon_notlari.md`
- 5-agent scan candidate list: documented in `01-PROVENANCE.md`
- Engine HEAD: `318eb2f529d7103e8b7d80b01228357fdc4e0217`
- Phase 0 deliverables: `_infra/manifests/{engine_head,seed_registry,claim_schema}.json`
