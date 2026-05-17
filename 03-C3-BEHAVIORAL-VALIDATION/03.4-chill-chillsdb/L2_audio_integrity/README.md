# L2 — ChillsDB v1 Audio Integrity

**Purpose:** Verify that ChillsDB v1 audio WAV files are present at the expected location and have plausible durations.

## Expected file layout

```
Science/datasets/emotion/chillsdb/
├── audio_chillsdb1/<clip>.wav                  ← original (input to L3 engine cache)
├── audio_chillsdb1_denoised/<clip>.wav         ← ffmpeg afftdn nr=12 (for TC003/005)
├── audio_chillsdb1_noisereduce/<clip>.wav      ← noisereduce non-stationary (for TC006)
└── music_stimuli.csv                           ← event timestamps
```

The 9 ChillsDB v1 clips (filenames keyed by YouTube video ID):

| clip_id | title | genre | excluded from 7-clean? |
|---|---|---|---|
| C1ZL5AxmK_A | Lakmé Flower Duet (Delibes) | classical/opera | — |
| FOjdXSrtUxA | Inception "Time" (Hans Zimmer) | film_score | — |
| H3v9unphfi0 | Miserere (Allegri) | sacred | — |
| Y1UiD2sxoWo | Ed Sheeran | popular | — |
| fRL447oDId4 | Lana Del Rey | popular | — |
| va1oiojnGrA | Gladiator "Now We Are Free" (Hans Zimmer) | film_score | — |
| zx_dTSPzXlk | Agnus Dei (Barber) | sacred | — |
| CwzjlmBLfrQ | Mr. Bean Olympics 2012 | comedy_sketch | **EXCLUDED** |
| YbNYinfj1h0 | 15 Greatest Vocal Intros | compilation_montage | **EXCLUDED** |

## What this layer asserts

1. ChillsDB root exists at the expected path
2. All 9 `audio_chillsdb1/<clip>.wav` files are present
3. `ffprobe` (ffmpeg) is installed and callable
4. Each audio file's duration is within ±5 s of the canonical measured duration

## What this layer does NOT check

- Audio file checksums (ChillsDB clips are sourced from YouTube; minor codec differences are tolerated within the ±5 s duration tolerance).
- Sample rate (engine resamples on ingest; sample-rate-agnostic).
- Denoised variant presence (L7 checks these separately).

## Failure mode

If audio files are missing, L3 cache build will also fail. Place the audio files at the expected paths before re-running. The error message lists exactly which files are missing.

## ChillsDB audio sourcing

For reviewer/reproducer convenience, the audio can be regenerated from YouTube video IDs using `yt-dlp` (audio extracted as WAV, no resampling). The exact source files used at paper-time are not redistributable due to YouTube ToS, but the source URLs are publicly accessible via the YouTube IDs above.
