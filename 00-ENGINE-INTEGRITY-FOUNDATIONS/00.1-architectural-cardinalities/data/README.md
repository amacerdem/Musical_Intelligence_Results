# Phase 1 — data/ (POINTERS ONLY)

This directory holds NO data files. All inputs live in their canonical locations.

## Sensitivity panel audio

The paper's sensitivity panel originally used a 30s Cheung 2019 chord audio clip. As of 2026-05-06, `Science/datasets/prediction/cheung2019/` is empty on this machine — the dataset is pending sync. Phase 1 falls back to a deterministic substrate from the legacy test corpus:

```
Science/V1/stimuli/micro_beliefs/  (655 WAV files, ~125 MB)
```

Selection rule (deterministic): smallest WAV by file size in `Science/V1/stimuli/micro_beliefs/` recursively, then alphabetical by name. The selected file is recorded in `results/sensitivity_summary.json`.

This substrate is fit-for-purpose for the determinism floor demonstration (C-CARD-16 CAVEAT). True ±30% perturbation (paper claim) requires engine modification (forbidden by frozen-engine policy) and is referenced from V1 evidence base.

## Future re-run with Cheung audio

Once `Science/datasets/prediction/cheung2019/` populates, the sensitivity script can be re-pointed by editing the `CHEUNG_AUDIO_CANDIDATES` list in `code/sensitivity_perturb.py`. Engine output is bit-identical regardless of input audio for the determinism-floor purpose.

## No git-tracked data

This README is the only file in `data/`. Audio inputs are referenced by absolute path; CSV/JSON outputs land under `results/`.
