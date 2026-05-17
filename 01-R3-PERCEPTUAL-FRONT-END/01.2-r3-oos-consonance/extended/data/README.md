# Phase 29 — Input data pointers

Phase 29 reads input CSVs directly from the project-root
`Science/datasets/consonance/` tree. No copies are made under
this `data/` directory in order to avoid duplication.

| Claim ID | Path (relative to project root) |
|---|---|
| C-R3EXT-01 | `Science/datasets/consonance/marjieh2024/data-csv/rating_dyh3dd.csv` |
| C-R3EXT-02 | `Science/datasets/consonance/marjieh2024/data-csv/rating_flute_harmonic_harflt.csv` |
| C-R3EXT-03 | `Science/datasets/consonance/marjieh2024/data-csv/rating_guitar_harmonic_hargtr.csv` |
| C-R3EXT-04 | `Science/datasets/consonance/marjieh2024/data-csv/rating_piano_harmonic_harpno.csv` |
| C-R3EXT-05 | `Science/datasets/consonance/marjieh2024/data-csv/pure_dyad_purdyrt.csv` |
| C-R3EXT-06 | `Science/datasets/consonance/bidelman2009_ffr.csv` |
| C-R3EXT-07 | `Science/datasets/consonance/schwartz2003_speech_harmonics.csv` |
| C-R3EXT-08 | `Science/datasets/consonance/sethares1993_dissonance.csv` |
| C-R3EXT-09 | `Science/datasets/consonance/interval_tension/data/indian_tension_ratings.csv` |

SHA-256 hashes of every input file are computed at run-time and
written to `results/29_input_hashes.json`.
