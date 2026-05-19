# Phase 01.2 extended — Provenance (LOCKED 2026-05-16)

Chain-of-custody for the nine input artefacts consumed by Phase 01.2 extended.
All paths are relative to the `Musical_Intelligence_Results/` repository root
unless otherwise noted.

## Engine

| Item | Value |
|---|---|
| Pinned HEAD | `318eb2f529d7103e8b7d80b01228357fdc4e0217` |
| Vendored at | `Musical-Intelligence-Reproduction/engine/Musical_Intelligence/` |
| Aggregate SHA | recorded at `engine/HEAD.md` |

The script aborts if the aggregate SHA at runtime does not match the
value recorded at `engine/HEAD.md`.

## Datasets

### C-R3EXT-01 .. C-R3EXT-05 — Marjieh 2024 sub-studies

| Item | Value |
|---|---|
| Source repository | https://github.com/AbsoluteHarmony/consonance-repository |
| Local clone | `Science/datasets/consonance/marjieh2024/` |
| README | `Science/datasets/consonance/marjieh2024/README.md` |
| Local commit | recorded at clone-time (see `data/README.md` for sha) |
| License | per source repository LICENSE |
| Original publication | Marjieh, R., Harrison, P. M. C., Lee, H., Deligiannaki, F., & Jacoby, N. (2024). Reshaping musical consonance with timbral manipulations and massive online experiments. *Nature Communications*, 15. |

CSV files consumed:

| Claim ID | File | N raw | N binned |
|---|---|---|---|
| C-R3EXT-01 | `marjieh2024/data-csv/rating_dyh3dd.csv` | 7,500 | 13 (integer semitone bins) |
| C-R3EXT-02 | `marjieh2024/data-csv/rating_flute_harmonic_harflt.csv` | 15,000 | 13 |
| C-R3EXT-03 | `marjieh2024/data-csv/rating_guitar_harmonic_hargtr.csv` | 7,500 | 13 |
| C-R3EXT-04 | `marjieh2024/data-csv/rating_piano_harmonic_harpno.csv` | 7,500 | 13 |
| C-R3EXT-05 | `marjieh2024/data-csv/pure_dyad_purdyrt.csv` | 7,500 | 13 |

All CSVs share the schema `participant_id, musical_exp, v1, rating`
(`v1` is the dyad interval in continuous semitones).

### C-R3EXT-06 — Bidelman & Krishnan 2009 FFR

| Item | Value |
|---|---|
| File | `Science/datasets/consonance/bidelman2009_ffr.csv` |
| N | 7 intervals |
| Columns | `interval, ratio, semitones, pitch_salience, behavioral_consonance, source` |
| Original publication | Bidelman, G. M., & Krishnan, A. (2009). Neural correlates of consonance, dissonance, and the hierarchy of musical pitch in the human brainstem. *Journal of Neuroscience*, 29(42), 13165–13171. |
| Phase 6 extended target column | `behavioral_consonance` (primary), `pitch_salience` (secondary, neural FFR amplitude proxy) |

### C-R3EXT-07 — Schwartz et al. 2003 speech-derived

| Item | Value |
|---|---|
| File | `Science/datasets/consonance/schwartz2003_speech_harmonics.csv` |
| N | 13 intervals |
| Columns | `interval, ratio, semitones, percent_similar, consonance_rank, source` |
| Original publication | Schwartz, D. A., Howe, C. Q., & Purves, D. (2003). The statistical structure of human speech sounds predicts musical universals. *Journal of Neuroscience*, 23(18), 7160–7168. |
| Phase 6 extended target column | `percent_similar` (consonance ↑ = % similar to speech harmonics ↑) |

### C-R3EXT-08 — Sethares 1993 analytical reference

| Item | Value |
|---|---|
| File | `Science/datasets/consonance/sethares1993_dissonance.csv` |
| N | 13 intervals |
| Columns | `interval, ratio, semitones, relative_dissonance, consonance_rank, source` |
| Original publication | Sethares, W. A. (1993). Local consonance and the relationship between timbre and scale. *Journal of the Acoustical Society of America*, 94(3), 1218–1228. |
| Phase 6 extended target column | `relative_dissonance` (consonance ↑ = relative_dissonance ↓; sign reversal logged in `results/29_sign_convention.json`) |

### C-R3EXT-09 — Lahdelma et al. Indian Interval Tension

| Item | Value |
|---|---|
| File | `Science/datasets/consonance/interval_tension/data/indian_tension_ratings.csv` |
| N | 852 per-participant per-interval ratings (Carnatic 312 / Hindustani 228 / Indian non-musicians 312) |
| Columns | `omsi1indian, omsi1western, gender, age, participant, Expertise, Interval, tensionrating, Group, musicianship, musicianshipW, musicianshipI, ExpertiseN` |
| Original publication | Lahdelma, I., Eerola, T., Ahmad, N., Clayton, M., Armitage, J., Bhattacharyya, B., & Munsamy, N. Musical expertise better predictor of tension in harmonic intervals than psychoacoustics across North and South Indian listeners. *In preparation*. |
| Phase 6 extended target column | `tensionrating` (sign reversed: tension ↑ ⇔ consonance ↓; reversal logged in `results/29_sign_convention.json`) |
| Interval coverage | 12 named intervals: m2, M2, m3, M3, P4, A4, P5, m6, M6, m7, M7, P8 — no P1 unison |
| Interval → semitone map | `{m2:1, M2:2, m3:3, M3:4, P4:5, A4:6, P5:7, m6:8, M6:9, m7:10, M7:11, P8:12}` |
| Aggregation | Mean `tensionrating` per interval, pooled across all 852 ratings. Per-group sub-correlations (Carnatic / Hindustani / Indian non-musicians) reported as auxiliary, not load-bearing. |
| Cross-cultural axis | Tests whether the engine's consonance signal aligns with tension ratings from listeners trained in Carnatic and Hindustani musical traditions, which use non-Western interval systems but were tested here on 12-TET Western intervals. |

## Provenance verification

At Phase 6 extended first run, the script computes SHA-256 of each input CSV
and writes the hashes to `results/29_input_hashes.json`. A reviewer
re-running the phase against a fresh clone of the source datasets can
diff the hash file against the values stored at close-time to confirm
no upstream dataset drift.

## Independence verification

A separate `01b-INDEPENDENCE-AUDIT.md` (deferred to Phase 6 extended close)
will append a `git log` extraction confirming that none of the nine
filenames above appears in any commit message, file path, or comment
inside the engine subtree at the pinned HEAD.

## Vendoring policy

Phase 6 extended does not copy the source CSVs into `data/` or
`paper-evidence/`. The script reads directly from
`Science/datasets/consonance/` to avoid duplication. A future
self-contained-bundle phase (Phase 17) may vendor these files for
external reproduction.
