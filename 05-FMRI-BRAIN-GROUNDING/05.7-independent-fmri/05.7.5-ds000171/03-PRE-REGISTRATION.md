# Phase 05.7.5 — ds000171 Affective Music in Depression — Pre-Registration

**Status:** FROZEN 2026-05-07. Execution pending external audio fetch.
**Dataset:** Lepping et al. 2016 ds000171 OpenNeuro (Music+Depression)
**N planned:** 39 (19 MDD + 20 ND), alignment-qualified N=28 per Phase 0.5
**Seed:** `phase_18_5` (in `_infra/manifests/seed_registry.json`)
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

## Hypotheses (locked before execution)

1. **F5 emotion routing (group-blind).** F5 valence mechanisms (VMM, EAM,
   ARC) predict BOLD in amygdala and ACC at q<0.05 BH-FDR in **≥2/3
   mech × region pairs** when pooled across all 28 alignment-qualified
   subjects.
2. **F6 reward attenuation (clinical contrast).** F6 anticipation_da
   coupling with NAcc BOLD is lower in MDD than ND with **effect size
   d > +0.4** (anhedonia hypothesis; Mallik 2017 direction).
3. **F5 group-invariance.** F5 amygdala BOLD prediction does NOT differ
   between MDD and ND with effect size |d| < 0.3 (basic perceptual routing
   is preserved in clinical population).
4. **Convergence with Cheung 2019 / Salimpoor 2011.** F6 antic_da signal
   peaks ahead of F6 consum_opi signal in ≥20/28 alignment-qualified
   subjects (replicates Phase 8 caudate-leads-NAcc lag at population scale).

## Data acquisition (one-time external fetch)

Lepping 2016 paper supplementary stimulus files are not on OpenNeuro. Two
acquisition paths, in order of preference:

1. **Sci. Rep. supplementary materials.** Lepping et al. 2016, Sci Rep
   doi:10.1038/srep24818 — supplementary materials may contain stimulus
   tracks. Visit
   `https://www.nature.com/articles/srep24818#Sec24` and download
   supplementary audio.
2. **Author request.** Email Lepping et al.; cite ds000171 + paper §Materials
   request stimulus audio for replication purposes.

Place files under
`Science/datasets/neuroimaging/ds000171/stimuli/` with filenames
`positive_music_NN.wav`, `negative_music_NN.wav`, `tones_NN.wav` matching
paper §Materials Table S1. Approximately 18 unique stimuli at ~31.5 s
each = ~10 minutes total audio.

## Analytical pipeline (locked before execution)

For each of 28 alignment-qualified subjects (per Phase 0.5):

1. Load BOLD (`sub-XX_task-music_run-N_bold.nii.gz` for music runs +
   `task-nonmusic` for tone-only baseline).
2. Load events.tsv (block-design `trial_type`: positive_music,
   negative_music, tones, response).
3. For each unique stimulus (~18 tracks):
   - Run frozen MI engine on stimulus audio at 44.1 kHz
   - Extract F5 mechs (VMM, EAM, ARC) at 172.27 Hz
   - Extract F6 channels (antic_da, consum_opi) at 172.27 Hz
4. Convolve mech timeseries with canonical HRF (SPM12 double-gamma).
5. Resample to BOLD TR (=2.0 s for ds000171 per dataset_description.json).
6. Per-mech × region: ridge regression LOSO across runs; held-out r.
7. Group contrast: MDD vs ND on per-pair held-out r distributions; report
   Cohen's d with bootstrap 95% CI (10,000 resamples per pair).
8. F6 caudate-NAcc lag check: cross-correlate antic_da with NAcc BOLD,
   peak lag in [+0.5, +2.0 s] window matches ds002725 Phase 8 finding.

## Decision rule (locked before execution)

- **POSITIVE:** Hypothesis 1 PASS AND (Hypothesis 2 OR Hypothesis 3) PASS.
- **PARTIAL:** Hypothesis 1 PASS only.
- **NEGATIVE:** Hypothesis 1 fails.
- **CLINICAL-CONVERGENCE-BONUS:** Hypothesis 4 (lag check) is bonus —
  PASS strengthens narrative but does not affect verdict alone.

## Forbidden moves (locked before execution)

- Adjusting α grid after seeing held-out r.
- Changing HRF model.
- Adding/removing target pairs or regions.
- Re-running with different seeds and reporting the better one.
- Cherry-picking subjects post-hoc.
- Reporting MDD-only or ND-only sub-analysis as primary.

## Auditability

Seed registry entry `phase_18_5` records run timestamps, hashes of
stimulus WAVs (SHA-256), engine HEAD, per-subject held-out r, and per-pair
group-contrast d values.

## Estimated wall (post-fetch)

- Audio engine pass on 18 WAVs at ~31.5 s each, ~3.3× real-time on M2 8 GB:
  ~3 min
- Per-subject ridge LOSO + group bootstrap, 28 subs × 3+2 = 5 pairs:
  ~10–15 min on M2 8 GB
- Total Phase 05.7.5: ≤ 20 min wall.
