# L3 — Engine Cache Build / Verify

**Purpose:** Verify (or trigger build of) the engine per-frame output cache for 3 audio preprocessings × 7 ChillsDB v1 clips × 84 mechanism classes.

## Cache layout

```
Musical_Intelligence_Outputs/emotion/
├── chillsdb1/                        ← original audio variant
│   ├── manifest.json                 ← records engine_sha, build timestamp
│   ├── pooled.csv                    ← per-clip mean of all 1,147 dims (used for routing)
│   ├── pooled_pct.csv                ← per-clip percentile features
│   ├── targets.csv                   ← dataset labels (placeholder for chill paradigm)
│   └── per_frame/<clip_id>.npz       ← per-frame trajectory: r3, ram, neuro, beliefs, mech_<CLS>
├── chillsdb1_denoised/                 ← afftdn variant (TC003/TC005)
└── chillsdb1_noisereduce/              ← noisereduce variant (TC006)
```

Each `.npz` contains arrays:
- `r3` (T, 97)
- `ram` (T, 26)
- `neuro` (T, 4) — DA, NE, OPI, 5HT
- `beliefs` (T, 131)
- `mech_<CLASS>` (T, dim) for each of 84 mech classes

## What this layer asserts

1. For each of `chillsdb1`, `chillsdb1_denoised`, `chillsdb1_noisereduce`:
   - Cache root directory exists
   - `per_frame/` subdirectory present
   - All 7-clean clips (`CLIPS_7_CLEAN` constant) have `.npz` files
2. `manifest.json` records the canonical engine SHA aggregate (matches pin)

## Build trigger

If a variant cache is missing, this layer **skips with a clear instruction** rather than auto-building (engine cache build takes ~5-10 min per variant on M2 8 GB and would silently exceed pytest's typical timeout).

To build the missing cache manually:

```bash
# For original audio (assumes audio_chillsdb1/ exists)
python3 Musical_Intelligence_Results/<engine_runner>.py --dataset chillsdb1 \
  --audio_root Science/datasets/emotion/chillsdb/audio_chillsdb1

# For afftdn variant (build denoised audio first)
ffmpeg -i input.wav -af afftdn=nr=12 output.wav  # for each clip
python3 Musical_Intelligence_Results/<engine_runner>.py --dataset chillsdb1_denoised \
  --audio_root Science/datasets/emotion/chillsdb/audio_chillsdb1_denoised

# For noisereduce variant
python3 Science/c3-cognitive-signals/code/_true_calibration/denoise_noisereduce.py
python3 Musical_Intelligence_Results/<engine_runner>.py --dataset chillsdb1_noisereduce \
  --audio_root Science/datasets/emotion/chillsdb/audio_chillsdb1_noisereduce
```

## Downstream impact

If a variant cache is missing → all downstream tests for that variant SKIP. Specifically:
- L4 + L5 + L6 + L8 depend on `chillsdb1_denoised` (afftdn variant) — the primary path
- L7 depends on `chillsdb1_noisereduce`

A `quick` run (`run_all.py --quick`) only exercises L4, so only `chillsdb1_denoised` is needed.
