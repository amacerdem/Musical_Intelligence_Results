"""Phase 10 Audio-Native Upgrade — Angle 4 — Cross-rhythm consistency.

Pre-registration: ../AUDIO_NATIVE_UPGRADE.md §2 Angle 4 (frozen 2026-05-16).
Engine SHA pin: 318eb2f529d7103e8b7d80b01228357fdc4e0217.

Tests architectural prediction: MI's HTP and ICEM are CHORD-LEVEL features.
For the same chord progression in 3 different rhythm conditions, MI HTP/ICEM
should be near-invariant.

Pipeline:
  1. Run engine on rhythm2 + rhythm3 (60 WAVs) — rhythm1 already cached from Angle 1.
  2. Per stim: chord-onset windowed mean of HTP.E0 and ICEM.E0 in each rhythm.
  3. Per stim, per channel: Pearson r across rhythm pairs (1-2, 1-3, 2-3).
  4. Aggregate: median + IQR across 30 stim × 3 pairs = 90 r values per channel.
  5. Apply pre-registered decision rule.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as scistats

ENGINE_ROOT = Path("/Volumes/SRC-9/SRC Musical Intelligence")
PIPELINE_DIR = ENGINE_ROOT / "Science" / "V-Reproduction" / "Musical_Intelligence_Outputs" / "_build"
sys.path.insert(0, str(ENGINE_ROOT))
sys.path.insert(0, str(PIPELINE_DIR))
import _pipeline  # noqa: E402

PHASE_DIR = Path(__file__).resolve().parent.parent
CHEUNG_AUDIO = PHASE_DIR / "data" / "cheung_audio"
PITCH_DIR = CHEUNG_AUDIO / "pitches"
CACHE_BASE = PHASE_DIR / "data" / "cheung_audio_outputs"
RESULTS_DIR = PHASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

ENGINE_AGGREGATE_SHA_EXPECTED = "482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88"
FRAME_RATE_HZ = 172.265625
WINDOW_MS = 200.0
SEED = 42
N_BOOTSTRAP = 5000


def aggregate_engine_sha():
    engine_dir = ENGINE_ROOT / "Musical_Intelligence"
    files = sorted(p for p in engine_dir.rglob("*.py") if "__pycache__" not in p.parts)
    h = hashlib.sha256()
    for fp in files:
        sub = hashlib.sha256()
        with open(fp, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                sub.update(chunk)
        h.update((sub.hexdigest() + "\n").encode("ascii"))
    return h.hexdigest()


def windowed_mean(arr, frame_idx, half_window):
    lo = max(0, frame_idx - half_window)
    hi = min(arr.shape[0], frame_idx + half_window + 1)
    return float("nan") if lo >= hi else float(np.mean(arr[lo:hi]))


def extract_or_load(wav_path: Path, cache_dir: Path, nuclei) -> np.lib.npyio.NpzFile:
    cache_dir.mkdir(parents=True, exist_ok=True)
    out_npz = cache_dir / f"{wav_path.stem}.npz"
    if out_npz.exists():
        return np.load(out_npz)
    audio = _pipeline.load_audio(wav_path)
    bundle = _pipeline.run_full_pipeline(audio, nuclei)
    np.savez_compressed(out_npz,
                         htp=bundle["mech_HTP"].astype(np.float32),
                         icem=bundle["mech_ICEM"].astype(np.float32),
                         ram=bundle["ram"].astype(np.float32),
                         neuro=bundle["neuro"].astype(np.float32),
                         n_frames=np.int32(bundle["mech_HTP"].shape[0]),
                         n_samples=np.int32(audio.shape[-1]))
    return np.load(out_npz)


def chord_aligned_means(cache, pitch_df, half_window):
    htp = cache["htp"][:, 0]   # E0
    icem = cache["icem"][:, 0] # E0
    rows = []
    for i, prow in pitch_df.iterrows():
        onset = float(prow["onset"])
        frame = int(round(onset * FRAME_RATE_HZ))
        rows.append({
            "chord_idx": i,
            "onset_sec": onset,
            "htp_e0": windowed_mean(htp, frame, half_window),
            "icem_e0": windowed_mean(icem, frame, half_window),
        })
    return pd.DataFrame(rows)


def main():
    print("Phase 10 Audio-Native Upgrade — Angle 4 — Cross-rhythm consistency")
    print("=" * 70)

    actual_sha = aggregate_engine_sha()
    if actual_sha != ENGINE_AGGREGATE_SHA_EXPECTED:
        print(f"ERROR: engine SHA mismatch", file=sys.stderr); return 2
    print(f"Engine SHA verified: {actual_sha[:16]}...")

    print("Building nuclei ...")
    nuclei = _pipeline.build_nuclei()
    print(f"  built {len(nuclei)} nuclei")

    half_window = int(round((WINDOW_MS / 1000.0) * FRAME_RATE_HZ))
    print(f"alignment window ±{half_window} frames ({WINDOW_MS:.0f} ms)")

    # For each stimulus (1..30), load/extract MI features per rhythm (1, 2, 3)
    per_stim_rhythm = {}  # {stim_num: {rhythm: chord_df}}
    print("\nExtracting/loading MI features for 30 stim × 3 rhythms = 90 runs ...")
    t_start = time.time()
    for stim_num in range(1, 31):
        per_stim_rhythm[stim_num] = {}
        pitch_path = PITCH_DIR / f"pitches_merged_wav_stim{stim_num:02d}.txt"
        if not pitch_path.exists():
            print(f"  stim{stim_num:02d}: missing pitch file", file=sys.stderr)
            continue
        pitch_df = pd.read_csv(pitch_path, sep="\t")
        for rhythm in [1, 2, 3]:
            wav_path = CHEUNG_AUDIO / f"stimuli_rhythm{rhythm}" / f"merged_wav_stim{stim_num:02d}_rhythm{rhythm:02d}.wav"
            if not wav_path.exists():
                print(f"  stim{stim_num:02d}_r{rhythm}: missing WAV", file=sys.stderr)
                continue
            cache_dir = CACHE_BASE / f"mi_features_rhythm{rhythm}"
            cache = extract_or_load(wav_path, cache_dir, nuclei)
            per_stim_rhythm[stim_num][rhythm] = chord_aligned_means(cache, pitch_df, half_window)
        elapsed = time.time() - t_start
        eta = elapsed / stim_num * (30 - stim_num)
        print(f"  stim{stim_num:02d}: 3 rhythms done  elapsed={elapsed:.0f}s  ETA={eta:.0f}s")

    # Per-stimulus per-pair correlation
    rhythm_pairs = [(1, 2), (1, 3), (2, 3)]
    rows = []
    for stim_num, rd in per_stim_rhythm.items():
        if len(rd) < 3: continue
        for r1, r2 in rhythm_pairs:
            d1, d2 = rd.get(r1), rd.get(r2)
            if d1 is None or d2 is None: continue
            n_chords = min(len(d1), len(d2))
            d1 = d1.iloc[:n_chords]
            d2 = d2.iloc[:n_chords]
            mask_h = ~(d1["htp_e0"].isna() | d2["htp_e0"].isna())
            mask_i = ~(d1["icem_e0"].isna() | d2["icem_e0"].isna())
            if mask_h.sum() >= 5 and d1["htp_e0"][mask_h].std() > 0 and d2["htp_e0"][mask_h].std() > 0:
                r_h, _ = scistats.pearsonr(d1["htp_e0"][mask_h], d2["htp_e0"][mask_h])
            else:
                r_h = np.nan
            if mask_i.sum() >= 5 and d1["icem_e0"][mask_i].std() > 0 and d2["icem_e0"][mask_i].std() > 0:
                r_i, _ = scistats.pearsonr(d1["icem_e0"][mask_i], d2["icem_e0"][mask_i])
            else:
                r_i = np.nan
            rows.append({"stim": stim_num, "pair": f"r{r1}-r{r2}",
                         "n_chords": n_chords, "n_valid_htp": int(mask_h.sum()),
                         "n_valid_icem": int(mask_i.sum()),
                         "r_HTP": float(r_h) if not np.isnan(r_h) else None,
                         "r_ICEM": float(r_i) if not np.isnan(r_i) else None})
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS_DIR / "angle4_cross_rhythm_per_stim_pair.csv", index=False)

    # Aggregate
    rs_h = [r["r_HTP"] for r in rows if r["r_HTP"] is not None]
    rs_i = [r["r_ICEM"] for r in rows if r["r_ICEM"] is not None]
    rng = np.random.default_rng(SEED)

    def boot_med_ci(vs):
        if len(vs) < 3: return (float("nan"), float("nan"))
        arr = np.array(vs)
        meds = []
        for _ in range(N_BOOTSTRAP):
            idx = rng.integers(0, len(arr), size=len(arr))
            meds.append(np.median(arr[idx]))
        return float(np.quantile(meds, 0.025)), float(np.quantile(meds, 0.975))

    median_h, median_i = float(np.median(rs_h)), float(np.median(rs_i))
    ci_h, ci_i = boot_med_ci(rs_h), boot_med_ci(rs_i)

    # Decision rule per spec §2 Angle 4
    pos = median_h >= 0.7 and median_i >= 0.7
    neg = median_h <= 0.3 or median_i <= 0.3
    if pos and not neg:
        verdict = "POSITIVE_RHYTHM_INVARIANT"
    elif neg and not pos:
        verdict = "NEGATIVE_RHYTHM_COUPLED"
    else:
        verdict = "INCONCLUSIVE"

    output = {
        "stage": "Phase 10 Audio-Native Upgrade — Angle 4",
        "engine_pin_commit": "318eb2f529d7103e8b7d80b01228357fdc4e0217",
        "engine_aggregate_sha256": actual_sha,
        "n_stim": len(per_stim_rhythm),
        "n_rhythm_pairs": 3,
        "channels": {"HTP": "E0_high_level_lead", "ICEM": "E0_information_content"},
        "alignment_window_ms": WINDOW_MS,
        "r_HTP_cross_rhythm": {
            "median": median_h, "ci95": list(ci_h),
            "min": float(np.min(rs_h)), "max": float(np.max(rs_h)),
            "iqr": [float(np.quantile(rs_h, 0.25)), float(np.quantile(rs_h, 0.75))],
            "n": len(rs_h),
        },
        "r_ICEM_cross_rhythm": {
            "median": median_i, "ci95": list(ci_i),
            "min": float(np.min(rs_i)), "max": float(np.max(rs_i)),
            "iqr": [float(np.quantile(rs_i, 0.25)), float(np.quantile(rs_i, 0.75))],
            "n": len(rs_i),
        },
        "decision": {"verdict": verdict,
                     "rule_pos": "median r_HTP >= 0.7 AND median r_ICEM >= 0.7",
                     "rule_neg": "either median <= 0.3"},
    }
    with open(RESULTS_DIR / "angle4_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print()
    print("=" * 70)
    print(f"VERDICT: {verdict}")
    print(f"  HTP cross-rhythm:  median r = {median_h:+.4f}  CI95 [{ci_h[0]:+.4f}, {ci_h[1]:+.4f}]  range [{min(rs_h):+.3f}, {max(rs_h):+.3f}]")
    print(f"  ICEM cross-rhythm: median r = {median_i:+.4f}  CI95 [{ci_i[0]:+.4f}, {ci_i[1]:+.4f}]  range [{min(rs_i):+.3f}, {max(rs_i):+.3f}]")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
