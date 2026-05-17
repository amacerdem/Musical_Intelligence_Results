# Phase 05.7.1 — studyforrest 7T Music Genres Extension — Pre-Registration

**Status:** FROZEN 2026-05-07. Execution pending external audio fetch.
**Dataset:** studyforrest 7T music perception (5 genres × 8 stimuli; ds000113-ext)
**N planned:** 20 subjects (alignment-qualified per Phase 0.5)
**Seed:** `phase_18_1` (in `_infra/manifests/seed_registry.json`)
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

## Hypotheses (locked before execution)

1. **F1 sensory routing.** F1 mechanisms (BCH, PNH, MIAA, PCCR, IIS) predict
   BOLD in A1/HG and STG above shuffled-null at q<0.05 BH-FDR in **≥3/5
   mechanism × region pairs**.
2. **F2 prediction routing.** F2 mechanisms (HTP, ICEM, UDP) predict BOLD in
   dlPFC and IFG above shuffled-null at q<0.05 BH-FDR in **≥2/3 mechanism ×
   region pairs**.
3. **Subject-level reproducibility.** MI's per-subject ridge LOSO held-out
   r > shuffled-null mean+1σ in **≥15/20 subjects** for at least one F1/F2
   target pair.

## Data acquisition (one-time external fetch)

```bash
cd Science/datasets/neuroimaging/studyforrest/studyforrest-data
datalad get artifact/7T_musicperception/stimulus/   # ~40 WAVs, ~10 MB
```

The 7T music perception extension stimuli are 5 genres (rocknroll,
symphonic, country, metal, ambient) × 8 clips × 6 s each = 40 WAVs at
44.1 kHz. Filenames already referenced in
`sub-XX/ses-auditoryperception/func/*_events.tsv` (column `stim`).

## Analytical pipeline (locked before execution)

For each of 20 alignment-qualified subjects:

1. Load BOLD (`sub-XX_ses-auditoryperception_task-auditoryperception_run-NN_bold.nii.gz`)
2. Load events.tsv (sub-second `onset`, `duration`, `stim`, `genre` columns)
3. For each unique stimulus WAV:
   - Run frozen MI engine on stimulus audio at 44.1 kHz
   - Extract F1 mechs (BCH, PNH, MIAA, PCCR, IIS) at 172.27 Hz
   - Extract F2 mechs (HTP, ICEM, UDP) at 172.27 Hz
4. Convolve mech timeseries with canonical HRF (SPM12 double-gamma,
   peak 6 s, undershoot 16 s)
5. Resample to BOLD TR (=1.4 s for 7T studyforrest music task)
6. Per-mech × region: ridge regression LOSO with α∈{1, 10, 100, 1000};
   held-out Pearson r computed on left-out runs
7. Shuffled-null: 500 permutations of stimulus-onset alignment within
   subject; report empirical p-value per pair
8. BH-FDR correction at q<0.05 over the 5+3=8 target pairs

## Decision rule (locked before execution)

- **POSITIVE:** ≥3/5 F1 pairs AND ≥2/3 F2 pairs survive BH-FDR at q<0.05.
- **PARTIAL:** one of (F1, F2) survives but not both.
- **NEGATIVE:** neither F1 nor F2 hits its threshold.
- **NON-ELIGIBLE:** Phase 0.5 entry-gate rejected (not the case here).

The decision rule is binary: re-running the pipeline cannot change the
verdict because all parameter choices (α grid, HRF model, perm count, q,
target pairs) are locked.

## Forbidden moves (locked before execution)

- Adjusting α grid after seeing held-out r.
- Changing HRF model.
- Adding/removing target pairs.
- Re-running with different seeds and reporting the better one.
- Cherry-picking subjects post-hoc.

## Auditability

The seed registry entry `phase_18_1` will record run timestamps, hashes
of stimulus WAVs (SHA-256), engine HEAD, and per-subject held-out r values
for every (mech, region) pair. Re-runs on a fresh clone produce
byte-identical CSVs.

## Why FROZEN now (before execution)

Pre-registering the pipeline before audio arrives prevents post-hoc
parameter tuning. When `datalad get` completes, the pipeline executes
deterministically and the verdict is whatever it is — POSITIVE, PARTIAL,
NEGATIVE, or technically-PARTIAL (e.g., 2/5 F1 pairs and 3/3 F2 pairs).

## Estimated wall (post-fetch)

- Audio engine pass on 40 WAVs at 6 s each, ~3.3× real-time on M2 8 GB:
  ~75 s
- Per-subject ridge LOSO + 500 perms, 8 pairs × 20 subs: ~5–10 min total
  on M2 8 GB
- Total Phase 05.7.1: ≤ 15 min wall on consumer M2.
