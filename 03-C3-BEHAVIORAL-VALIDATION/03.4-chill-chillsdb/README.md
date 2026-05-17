# 21-c3-chill-prediction — Standalone Chill-Marker Verdict

> **Purpose:** Reproduce the paper's Tier-1 chill-marker finding (`MMP P2:familiarity` Bonferroni-pass on ChillsDB v1 7-clean continuous-music subset) **from a fresh clone of the system**, in a single command.
>
> **The single empirical claim under test:**
>
> > On the ChillsDB v1 7-clean continuous-music subset, the frozen MI engine's `MECH_MMP__P2:familiarity` channel shows Bonferroni-corrected elevation within ±5 s windows of participant chill events: **rank-biserial = +0.231**, **p_bonf = 0.009** across 22 chill-related channels (7/7 clips positive, n=146 chill events, 500 random event-time null shuffles per clip).
>
> If `run_all.py` completes with ✅ verdict at L4, the paper's headline chill finding is independently reproduced on the runner's machine.

---

## Quick start

After cloning the `SRC Musical Intelligence` repository **and** placing the ChillsDB v1 audio files at the expected location (see `L2_audio_integrity/README.md`):

```bash
cd Science/V-Reproduction/21-c3-chill-prediction
python3 run_all.py
```

This runs all 9 layers in order (Pin → L1 → L2 → ... → L9) and writes a fresh `REPORT.md` with:
- Per-layer PASS / FAIL / CAVEAT scorecard
- Per-channel rank-biserial table for the primary chill test
- Cross-validation results across audio-preprocessing variants
- Final reconciliation against paper-time numbers (frozen at engine SHA `482ade45c...`)

Exit code is the worst pytest exit code observed (`0` = all PASS).

**Prerequisites:**

```bash
pip install torch numpy scipy soundfile pandas pytest noisereduce
```

System dependencies (system-level installs, NOT pip):
- `ffmpeg` (for `afftdn` Wiener denoise variant used in TC003/005)

The engine (`Musical_Intelligence/`) is auto-discovered via an upward walk from `conftest.py` — no manual `PYTHONPATH` setup needed.

**Expected wallclock on M2 8 GB:** ~25-35 min full run (engine cache build ~10 min for 7 clips × 3 audio variants + stat tests ~5 min).

For a sanity check before the full run:

```bash
python3 run_all.py --quick     # pin-integrity + L1 + L4 only (~3-5 min)
```

This produces only the headline L4 verdict, skipping the additional sensitivity/cross-validation layers.

---

## Inputs required (what user must provide)

When the reviewer or independent runner clones the repo, they must additionally place:

1. **ChillsDB v1 audio WAVs** at:
   ```
   Science/datasets/emotion/chillsdb/audio/<clip_id>.wav
   ```
   The 9 clips (full set; 7 are used for the primary verdict):
   ```
   C1ZL5AxmK_A.wav    # Lakmé Flower Duet
   FOjdXSrtUxA.wav    # Hans Zimmer Inception "Time"
   H3v9unphfi0.wav    # Allegri Miserere
   Y1UiD2sxoWo.wav    # Ed Sheeran
   fRL447oDId4.wav    # Lana Del Rey
   va1oiojnGrA.wav    # Hans Zimmer Gladiator "Now We Are Free"
   zx_dTSPzXlk.wav    # Barber Agnus Dei
   CwzjlmBLfrQ.wav    # (excluded from 7-clean) Mr. Bean Olympics
   YbNYinfj1h0.wav    # (excluded from 7-clean) 15 Vocal Intros
   ```

2. **ChillsDB v1 event timestamps CSV** at:
   ```
   Science/datasets/emotion/chillsdb/chillsdb_top_50/top_50_metadata.csv
   ```

If audio files are missing, `L2_audio_integrity` will fail with a clear file-presence error. No silent fallback.

---

## Layer overview

| Layer | Purpose | Typical wallclock |
|---|---|---|
| `L1_engine_pin` | Assert engine SHA matches `482ade45c...` | <1 s |
| `L2_audio_integrity` | Verify ChillsDB v1 WAV files present + correct format | ~5 s |
| `L3_engine_cache` | Build or verify engine cache for original + afftdn + noisereduce audio variants | ~15-25 min |
| `L4_tc005_primary_verdict` | **PRIMARY** — TC005 7-clean Bonferroni Mann-Whitney rank-biserial | ~30 s |
| `L5_tc003_sensitivity` | 9-full sensitivity (Mr. Bean + Vocal Intros included) | ~30 s |
| `L6_tc004_biphasic_composite` | Biphasic composite (positive autonomic + negative DA cluster) | ~30 s |
| `L7_tc006_noisereduce_crossval` | Independent denoise algorithm cross-validation | ~30 s |
| `L8_tc007_pre_post` | Pre/post event-window asymmetry | ~30 s |
| `L9_verdict_reconciliation` | Compare local results to frozen paper-time numbers | <1 s |

**L4 carries the primary headline verdict.** Layers L5-L8 provide supporting sensitivity and cross-validation analyses.

---

## Numeric tolerance

This reproduction tree is **engine-bit-identical** up to floating-point noise (|Δρ| ≤ 1×10⁻⁴ tolerated). For the headline statistic (MMP P2 rb-biserial on 7-clean denoised audio), L9 asserts:

```
|rb_local - rb_paper_time| ≤ 0.005  (5e-3 absolute)
|p_bonf_local - p_bonf_paper_time| ≤ 5e-4
```

Any deviation beyond these tolerances triggers a CAVEAT (not FAIL), with full diagnostic dump for investigation.

---

## What this reproduction does NOT test

- **The engine itself** — engine correctness is validated under `19-r3-isolated-validation` (R³) and `20-t3-isolated-validation` (T³/H³). Here we assume engine is the canonical frozen artifact.
- **Other C³-Cognitive-Signals dataset evidence** (DEAM, PMEmo, TenseMusic, etc.) — those have their own segment under `c3-cognitive-signals/`.
- **The paper's full 1,496-test BB-FDR aggregation** — that lives elsewhere.

This phase is laser-focused on **one Tier-1 finding** so a reviewer can independently confirm it in one command.

---

## Provenance + reproducibility

- **Engine SHA:** `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`
- **Engine commit:** `318eb2f5`
- **Strategy doc:** [`ISOLATED_STRATEGY_chillsdb1.md`](../c3-cognitive-signals/ISOLATED_STRATEGY_chillsdb1.md)
- **Source TC scripts:** ported from [`C3-Cognitive-Signals/code/_true_calibration/True_Calibration_005_clean7.py`](../c3-cognitive-signals/code/_true_calibration/) etc.
- **Paper-time CSVs (frozen baseline for L9 reconciliation):** [`C3-Cognitive-Signals/results/_true_calibration/Calibration_005_clean7/`](../c3-cognitive-signals/results/_true_calibration/Calibration_005_clean7/) and TC006

---

## If a layer fails

- **L1 FAIL** (engine SHA mismatch) → user has a different engine version; cannot reproduce paper claims. Stop, check `Musical_Intelligence/` SHA, ensure clean clone.
- **L2 FAIL** (audio missing) → place ChillsDB WAVs at the expected path (see L2 README).
- **L3 FAIL** (cache build fails) → check engine runtime errors; usually transient (OOM, missing deps).
- **L4 FAIL** (TC005 verdict differs from paper) → most concerning; investigate via L9 reconciliation dump. Could indicate: engine non-determinism, audio decoder difference, or genuine reproducibility issue.
- **L5-L8 FAIL** → sensitivity-test failures; affect paper's secondary claims but not the headline.
- **L9 FAIL** (reconciliation outside tolerance) → numeric drift; document and investigate.

---

## Reviewer attestation pattern

When this passes for a reviewer:
```
✅ 21-c3-chill-prediction (3rd-party reproduction on M2 16 GB / Ubuntu 22.04)
  L1 PASS — engine SHA matches 482ade45c...
  L2 PASS — 9/9 ChillsDB audio files present, correct duration
  L3 PASS — engine cache built (7 clips × 3 audio variants × 84 mechs)
  L4 PASS — MMP P2 rb=+0.2306 p_bonf=0.0092 (matches paper, |Δrb|<0.001)
  L5 PASS — 9-full sensitivity (paper-grade)
  L6 PASS — biphasic composite (Salimpoor pattern reproduced)
  L7 PASS — noisereduce cross-validation (denoise-method-robust)
  L8 PASS — pre/post asymmetry (sustained chill response)
  L9 PASS — reconciliation within tolerance

Total wallclock: 32m18s
```

This is the contract: one command, one boolean output, full diagnostic trail.
