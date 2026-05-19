# Phase 05.7 — Independent fMRI Replication

**Status:** PRE-REG-FROZEN (2026-05-07). Execution of two ELIGIBLE
sub-axes is contingent on external stimulus audio fetches. The other
three sub-axes are NON-ELIGIBLE per the Phase 0.5 entry-gate.

**Sub-axes:** 5 (05.7.1 studyforrest, 05.7.2 ds005880, 05.7.3 ds006583,
05.7.4 ds006564, 05.7.5 ds000171)

**Pre-registered target:** +148 fMRI subjects across 5 datasets

**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

## Per-sub-axis status

| Sub-axis | Dataset | N planned | Phase 0.5 entry-gate | Phase 05.7 status |
|---|---|---|---|---|
| 05.7.1 | studyforrest 7T music genres ext (ds000113-ext) | 20 | ELIGIBLE (audio fetch required) | PRE-REG-FROZEN, EXEC-PENDING |
| 05.7.2 | ds005880 Diminished 7th chord | 20 | NON-ELIGIBLE (events.tsv TR-only) | NON-ELIGIBLE |
| 05.7.3 | ds006583 Affective Transitions | 23 | NON-ELIGIBLE (events.tsv missing) | NON-ELIGIBLE |
| 05.7.4 | ds006564 Naturalistic film with music | 41 | NON-ELIGIBLE (events.tsv missing) | NON-ELIGIBLE |
| 05.7.5 | ds000171 Music + depression | 39 (19 MDD + 20 ND) | ELIGIBLE (audio fetch required) | PRE-REG-FROZEN, EXEC-PENDING |

**Aggregate:** 0 sub-axes executed, 2 PRE-REG-FROZEN with EXEC-PENDING,
3 NON-ELIGIBLE.

## Audit philosophy at this phase

The audit principle for Phase 05.7 is the same as for the rest of the
audit: paper claims must come from real engine outputs. Phase 05.7 does
not manufacture sub-axis verdicts in the absence of actual stimulus
audio. Three of five sub-axes fail the dataset eligibility entry-gate;
the remaining two require a single external audio fetch each.

Pre-registrations for the two ELIGIBLE sub-axes are frozen now, so the
analytical pipeline cannot later be tuned to the data. When audio
arrives, the pre-registered decision rules execute deterministically
without parameter freedom.

This is consistent with the entry-gate rule documented in
`00-MASTER-PLAN.md`: a NON-ELIGIBLE verdict is an infrastructure
exclusion, not an analytical failure. The reasoning for each
NON-ELIGIBLE outcome is recorded in the sub-axis manifest and traces
back to the Phase 0.5 audit.

## Directory layout

```
05.7-independent-fmri/
├── README.md                          (this file)
├── 05.7.1-studyforrest/                 PRE-REG-FROZEN, EXEC-PENDING
│   ├── 03-PRE-REGISTRATION.md
│   ├── code/run.sh + run_phase05_7_1.py
│   └── results/05.7.1_manifest.json
├── 05.7.2-ds005880/                     NON-ELIGIBLE
│   └── results/05.7.2_manifest.json
├── 05.7.3-ds006583/                     NON-ELIGIBLE
│   └── results/05.7.3_manifest.json
├── 05.7.4-ds006564/                     NON-ELIGIBLE
│   └── results/05.7.4_manifest.json
├── 05.7.5-ds000171/                     PRE-REG-FROZEN, EXEC-PENDING
│   ├── 03-PRE-REGISTRATION.md
│   ├── code/run.sh + run_phase05_7_5.py
│   └── results/05.7.5_manifest.json
└── _aggregate/
    ├── 02-RESULTS.md
    ├── 04-INTEGRATION-LOG.md
    └── results/05.7_independent_fmri_manifest.json
```

## Resumption instructions for executors

To complete sub-axis 05.7.1 (studyforrest 7T music genres):

```bash
# 1. Fetch the 7T music stimulus archive (~40 WAVs, ~10 MB total)
cd datasets/neuroimaging/studyforrest/studyforrest-data
datalad get artifact/7T_musicperception/stimulus/

# 2. Run the pre-registered analysis (no parameter changes permitted)
cd ../../../..
bash 05.7-independent-fmri/05.7.1-studyforrest/code/run.sh
```

To complete sub-axis 05.7.5 (ds000171 Music + depression):

```bash
# 1. Acquire the Lepping et al. 2016 supplementary stimulus audio
#    (Sci. Rep. doi:10.1038/srep24818). Tracks are referenced in the
#    paper §Materials Table S1.

# 2. Place the audio under datasets/neuroimaging/ds000171/stimuli/
#    with filenames matching the paper's §Materials Table S1
#    (positive_music_NN.wav, negative_music_NN.wav, etc.).

# 3. Run the pre-registered analysis
bash 05.7-independent-fmri/05.7.5-ds000171/code/run.sh
```

Both pre-registrations are frozen with seed registry entries
`phase_05_7_1` and `phase_05_7_5`. Re-running is deterministic.

## Paper revision items triggered by Phase 05.7

- Add a §Future directions hint about a prospective fMRI experiment.
- Add a §Limitations footnote disclosing the Phase 05.7 freeze state.
