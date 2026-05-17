# Phase 4 — Audio Source Pointers

15 clips, sequential, deterministic-by-seed selection.

## Source 1: `Science/datasets/real-music/*.wav` (6 clips)

Six real recordings, all longer than the engine's `MAX_DURATION_S = 30 s` cap, so all process exactly 30 s of audio:

1. `Beethoven - Pathetique Sonata Op13 I. Grave - Allegro.wav` (497 s)
2. `Cello Suite No. 1 in G Major, BWV 1007 I. Prélude.wav` (151 s)
3. `Cello_Suite_No._1_in_G_Major__BWV_1007_I._Prélude_9fb7a346.wav` (151 s)
4. `Duel of the Fates - Epic Version.wav` (177 s)
5. `Enigma in The Veil-Eclipse-Segment I - the maintainer.wav` (521 s)
6. `Herald of the Change - Hans Zimmer.wav` (301 s)

(Listed in directory-sorted order; first 6 wavs.)

## Source 2: `Science/datasets/emotion/DEAM/audio/MEMD_audio/` (9 clips)

Nine DEAM mp3s sampled deterministically:

```python
import random
rng = random.Random(2026050604)
deam_pick = rng.sample(sorted(deam_dir.glob("*.mp3")), 9)
```

DEAM clips are uniformly ~45 s; engine truncates to 30 s.

The exact 9 names are recorded in `results/_benchmark_summary.json["clip_list"]`.

## Why this mix

Compute profile is data-independent at frame level (engine path doesn't branch on audio content), but using diverse audio confirms the throughput is real (not silence-shortcut). The 6 Legacy wavs span symphonic / cello / synth / film-score; the 9 DEAM mp3s span pop/rock/folk/electronic emotional content.

## Reproducibility

To re-select clips later, run `code/benchmark.py` — `select_clips()` is deterministic by `SEED = 2026050604`.
