# Phase 00.2 — Results

**Date:** 2026-05-06
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
**Seed:** 20260506005
**Closing verdict:** **POSITIVE**

## Headline numbers

- **32 datasets audited** (vs ≥30 pre-registered).
- **4 datasets `mi_compatible=True`** (ds002725, ds003720, studyforrest_7t_music,
  ds000171; the latter two conditional on external-audio fetch).
- **28 datasets explicitly excluded** with documented reason.
- **ds002725 alignment-qualified N = 17** (vs dataset-level N=21 in BIDS;
  4 subs lack the classicalMusic bold). **Exceeds Phase 11 minimum of N≥12.**
- **ds003720 framed as routing-ablation, not population estimate**
  (notes field contains the keyword `routing-ablation`).
- **Phase 18 sub-axis verdicts (5/5):**
  - 18.1 studyforrest_7t_music — **ELIGIBLE** (conditional on external Forrest
    Gump audio fetch; 20 subs at 7T)
  - 18.2 ds005880 — **NON-ELIGIBLE** (PARTIAL DOWNLOAD ~710 MB / 6 GB;
    events.tsv is integer-second TR-only)
  - 18.3 ds006583 — **NON-ELIGIBLE** (PARTIAL DOWNLOAD; 0 events.tsv on disk)
  - 18.4 ds006564 — **NON-ELIGIBLE** (PARTIAL DOWNLOAD; 0 events.tsv on disk)
  - 18.5 ds000171 — **ELIGIBLE** (conditional on external Lepping 2016
    audio fetch; 39 subs MDD + ND)

## Per-claim summary

| Claim | Verdict | Reproduced | Notes |
|---|---|---|---|
| C-ELIG-01 | **PASS** | 32 | ≥30 datasets audited (paper-cited + Phase 18 + scan + comparator). |
| C-ELIG-02 | **PASS** | 6/6 | All paper-cited datasets have explicit `mi_compatible` verdict. |
| C-ELIG-03 | **PASS** | 28 | ≫3 explicit exclusions with documented reason. |
| C-ELIG-04 | **PASS** | 17 | ds002725 alignment-qualified N reported. |
| C-ELIG-05 | **PASS** | "routing-ablation" | ds003720 explicitly framed. |
| C-ELIG-06 | **PASS** | 5/5 | All Phase 18 sub-axes have entry-gate verdicts. |

## Detail: paper-cited datasets

| Dataset | mi_compatible | n_align | Reason / consumer |
|---|---|---|---|
| ds002725 | True | 17 | Phase 11 (mech×region encoding), 7 classical pieces, shared events.tsv applies to all subs with classicalMusic bold |
| ds003720 | True | 5 | Phase 12 (cross-subject voxelwise), framed as routing-ablation (93% lift over MI-naive) |
| putkinen2025 | False | -1 | Closed-access PET; summary-only (µ-opioid 7/7 regions) |
| mallik2017 | False | -1 | Subject-level data not deposited; summary-only naltrexone |
| salimpoor2011 | False | -1 | Closed-access; +0.9s caudate-NAcc lag claim only |
| ferreri2019 | False | -1 | Closed-access pharmacology; dose-ordering claim only |

## Modality boundary verdicts (deferred to companion papers)

| Dataset | Modality | Companion paper |
|---|---|---|
| nmedh_hindi_eeg, musin_g, daly_ds002721, di_liberto_bach | EEG | Companion paper #2 (EEG/MEG) — requires source-localization adapter |
| marion_meg | MEG | Companion paper #2 |
| bellier_ecog, music_expertise_ieeg | iEEG | Companion paper #1 (iEEG) — requires sub-cm electrode validation |

## Behavioral / negative-control deferrals

mehr2019_nhs (Phase 14 cross-cultural V5), aam (path missing), pmemo
(audio-only no fMRI), deam (Phase 5 ECE only), groove_midi (Phase 7
F3+F7), emotify (audio-only behavioral) — all correctly excluded from
the fMRI core analysis path.

## Engine HEAD + seed lock

- Engine HEAD `318eb2f529d7103e8b7d80b01228357fdc4e0217` is referenced but
  **not exercised** in Phase 00.2 (no engine pipeline runs).
- Seed `20260506005` is referenced for compliance; all audits are
  deterministic (no RNG).

## Memory profile

Audit run measured at <300 MB total resident memory (pandas DataFrame
parsing of events.tsv per dataset, < 50 MB peak per dataset). M2 8GB
budget satisfied with margin.

## Paper revision triggers (R1–R5)

- **R1** — Insert §Methods §Dataset eligibility subsection citing
  `Supplementary_Table_S-Eligibility.tex`.
- **R2** — Disclose ds002725 alignment-qualified N=17 (figure caption +
  body + §Limitations) — replace any `N=17` shorthand with the explicit
  "dataset-level N=21, alignment-qualified N=17" framing.
- **R3** — Add explicit ds003720 routing-ablation framing in §Results
  Phase 12 paragraph.
- **R4** — Tighten sub-08 illustrative-only language (Phase 13 deliverable).
- **R5** — §Future directions: 1-2 sentence prospective fMRI experiment
  hint to address the ecosystem-level limitation.

## Decision

**POSITIVE** per pre-registration:

- 32 ≥ 30 datasets audited ✓
- 6 ≥ 6 paper-cited verdicts produced ✓
- 28 ≥ 3 explicit exclusions documented ✓
- ds002725 + ds003720 + 5 Phase 18 sub-axes all have entry-gate verdicts ✓

Phase 00.2 is **CLOSED 2026-05-06**. Phases 11, 12, and 18 entry-gates
are now legitimately unblocked.
