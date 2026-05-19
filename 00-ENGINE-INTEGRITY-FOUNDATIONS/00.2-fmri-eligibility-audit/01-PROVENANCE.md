# Phase 00.2 Provenance

## Inputs

### User-validated framing

- `MI_fMRI_validasyon_notlari.md` — the source document that locked the
  framing "MI's binding eligibility criterion is stimulus-lockability,
  not N." Phase 00.2 is the operational embodiment of that framing.

### 5-agent literature scan (≈30 candidates)

The candidate dataset list (Tier 1+2+3) was produced by a 5-agent
literature scan against the public music-fMRI / PET / EEG / MEG
ecosystem. Tier 1 fMRI = paper-cited (12) + Phase 18 planned (5). Tier 2
multimodal = EEG twin / MEG / iEEG (7). Tier 3 behavioral / negative
control = audio-only and MIDI-only datasets (8). Total =
**32 datasets** matching the pre-registered registry.

### Paper §Methods (current state, to be revised at Phase 17)

The current paper text discusses ds002725 alignment-qualified N
implicitly (via §Limitations N=17 → window-selection effect at sub-08).
Phase 00.2 audit makes that disclosure **explicit**:

- R1 — paper §Methods §Dataset eligibility (NEW subsection).
- R2 — ds002725 alignment-qualified N disclosure in figure caption +
  body + §Limitations.
- R3 — ds003720 explicit routing-ablation framing.
- R4 — sub-08 illustrative-only tightening.
- R5 — §Future directions prospective experiment hint.

These 5 paper revisions land in Phase 17 alongside the Zenodo deposit.

### Phase 0 deliverables consumed

- `_infra/manifests/engine_head.json` — engine HEAD pin
  `318eb2f529d7103e8b7d80b01228357fdc4e0217`. Not exercised in Phase 00.2
  (no engine pipeline runs) but recorded for audit-trail completeness.
- `_infra/manifests/seed_registry.json` — `phase_00_5.primary = 20260506005`.
- `_infra/manifests/claim_schema.json` — used by `code/aggregate.py` to
  produce `00.5_eligibility_manifest.json`.

## Outputs (downstream consumers)

### Phase 11 (Pre-reg mech×region encoding)

Consumes `n_alignment_qualified` for `ds002725`. Phase 11 cannot
legitimately run on subs whose events.tsv onset does not match the
classical stimulus track onsets. `02-RESULTS.md` reports the
Phase-0.5-conservative count; Phase 11 may iterate further (per-subject
onset-residual histogram, motion FD, MNI warp QC).

### Phase 12 (Cross-subject voxelwise encoding)

Consumes `mi_compatible=True` verdict for `ds003720` AND the explicit
routing-ablation framing requirement (Phase 12's headline claim is the
**93 % lift over routing-ablation MI-naive**, not a population
estimate). `02-RESULTS.md` records this with the keyword
`routing-ablation`.

### Phase 18 (Independent fMRI replication, 5 sub-axes)

Each sub-axis (18.1–18.5) gets an entry-gate verdict. NON-ELIGIBLE
outcomes are accepted by the Phase 18 plan; partial downloads (e.g.,
ds005880 with ~710 MB of 6 GB) are audited on partial state with a
PARTIAL DOWNLOAD note. Phase 18 may re-run audit when downloads
complete — that is iteration 2+, logged in `04-INTEGRATION-LOG.md`.

### Phase 17 (Zenodo bundle + paper revision pass)

Consumes `Supplementary_Table_S-Eligibility.tex` (paper-ready LaTeX)
and the 3 figures in `figures/`. The paper-revision pass at Phase 17
applies R1–R5 to `MI-Paper/main.tex`.

## Chain of custody

Phase 00.2 reads existing local datasets but **never writes to them**.
Outputs of Phase 00.2 are limited to its own directory:
`00-ENGINE-INTEGRITY-FOUNDATIONS/00.2-fmri-eligibility-audit/`. No engine source is
modified (frozen-engine policy).
