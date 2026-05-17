# Data — ECE Reproduction inputs

This directory contains **no audio files**. DEAM is large (~1 GB) and lives in the shared dataset cache. This README tells you where to find it and what to expect.

## Required input

5 DEAM held-out songs:

| Song ID | Path |
|---|---|
| 1034 | `Science/datasets/emotion/DEAM/audio/MEMD_audio/1034.mp3` |
| 1508 | `Science/datasets/emotion/DEAM/audio/MEMD_audio/1508.mp3` |
| 1777 | `Science/datasets/emotion/DEAM/audio/MEMD_audio/1777.mp3` |
| 1896 | `Science/datasets/emotion/DEAM/audio/MEMD_audio/1896.mp3` |
| 1923 | `Science/datasets/emotion/DEAM/audio/MEMD_audio/1923.mp3` |

Total size: ~3.6 MB (5 × ~720 KB each). Format: 44.1 kHz mono mp3, ~45 s each.

## DEAM dataset provenance

- **Source:** Soleymani, Caro, Schmidt, Sha, Yang (2013). "1000 Songs for Emotional Analysis of Music." Trans. ACM Multimedia.
- **Distribution:** Free for academic use. License: see `Science/datasets/emotion/DEAM/LICENSE` (if present).
- **Cache state:** Pre-extracted at `Science/datasets/emotion/DEAM/audio/MEMD_audio/` (1,802 MP3s, 1.3 GB total).
- **Original ZIP:** `Science/datasets/emotion/DEAM/DEAM_audio.zip` (kept for re-extraction if needed).

## Why these 5 songs?

Selection rule (paper-time, V2/T-R3-08):

```python
import random, csv
all_ids = [int(row[0]) for row in csv.reader(open(deam_song_csv)) if int(row[0]) > 1000]
rng = random.Random(seed=42)
rng.shuffle(all_ids)
selected = sorted(all_ids[:5])  # → [1034, 1508, 1777, 1896, 1923]
```

The `> 1000` filter excludes songs used in F5 calibration (paper used songs 1-1000 for emotion calibration; >1000 is held-out by construction).

Seed 42 is the paper-time seed. Re-running with seed 42 will deterministically select these same 5.

## Verifying inputs

```bash
ls -la "/Volumes/SRC-9/SRC Musical Intelligence/Science/datasets/emotion/DEAM/audio/MEMD_audio/"{1034,1508,1777,1896,1923}.mp3
```

Should show 5 files, each ~720 KB.

## Annotations (NOT used in this reproduction)

DEAM also provides per-second valence/arousal annotations at `Science/datasets/emotion/DEAM/annotations/`. **These are NOT used in the calibration ECE computation.** The "y = 1 - |PE|" target in this reproduction is the engine's internal Bayesian consistency, not external emotion ground truth (see `00-METHODOLOGY.md` §7).

If a future reproduction needs DEAM annotations (e.g., for F5 EmotionalArousal alignment), they live at:
```
Science/datasets/emotion/DEAM/annotations/annotations averaged per song/
Science/datasets/emotion/DEAM/annotations/annotations per each rater/
```
