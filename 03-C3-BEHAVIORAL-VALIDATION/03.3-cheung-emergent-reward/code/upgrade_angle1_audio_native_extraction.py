"""Phase 10 Audio-Native Upgrade — Angle 1 — MI engine on Cheung WAVs.

Pre-registration: ../AUDIO_NATIVE_UPGRADE.md §2 Angle 1 (frozen 2026-05-16).
Engine SHA pin: 318eb2f529d7103e8b7d80b01228357fdc4e0217.

Pipeline:
  1. Run MI engine on 30 rhythm1 WAVs → cache HTP[T,4], ICEM[T,4] + RAM/neuro per stim.
  2. For each chord onset (from pitches/*.txt): windowed mean (±200 ms) of
     MI HTP.E0 and ICEM.E0 at that onset → per-chord MI value.
  3. Pair with Cheung's IDyOM IC and ENTROPY columns (constant per
     (song, chordnumber)) → per-stimulus Pearson r across chords.
  4. Aggregate: median + IQR + 95% bootstrap CI of per-stimulus r distribution.
  5. Apply pre-registered decision rule.

Output: cached engine features + per-stimulus correlation table + decision JSON.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as scistats

REPO_ROOT = Path(__file__).resolve().parents[3]
# The MI engine Python package (``Musical_Intelligence/``) and the build
# pipeline live outside MI_Results. Set MI_ENGINE_ROOT to point at the
# directory containing ``Musical_Intelligence/`` (default: MI_Results parent).
ENGINE_ROOT = Path(os.environ.get("MI_ENGINE_ROOT", REPO_ROOT.parent))
PIPELINE_DIR = ENGINE_ROOT / "engine_outputs" / "_build"
sys.path.insert(0, str(ENGINE_ROOT))
sys.path.insert(0, str(PIPELINE_DIR))
import _pipeline  # noqa: E402

PHASE_DIR = Path(__file__).resolve().parent.parent
WAV_DIR = PHASE_DIR / "data" / "cheung_audio" / "stimuli_rhythm1"
PITCH_DIR = PHASE_DIR / "data" / "cheung_audio" / "pitches"
PLEASURE_CSV = Path(os.environ.get(
    "CHEUNG_2024_CSV",
    REPO_ROOT / "datasets" / "reward" / "cheung2024" / "data_pleasure_2023.csv",
))

CACHE_DIR = PHASE_DIR / "data" / "cheung_audio_outputs" / "mi_features_rhythm1"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR = PHASE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

ENGINE_AGGREGATE_SHA_EXPECTED = "482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88"
ENGINE_PIN_COMMIT = "318eb2f529d7103e8b7d80b01228357fdc4e0217"
FRAME_RATE_HZ = 172.265625
WINDOW_MS = 200.0
SEED = 42
N_BOOTSTRAP = 5000


def file_sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def aggregate_engine_sha() -> str:
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


def windowed_mean(arr: np.ndarray, frame_idx: int, half_window_frames: int) -> float:
    lo = max(0, frame_idx - half_window_frames)
    hi = min(arr.shape[0], frame_idx + half_window_frames + 1)
    if lo >= hi:
        return float("nan")
    return float(np.mean(arr[lo:hi]))


def extract_one_stim(wav_path: Path, nuclei) -> tuple[dict, dict]:
    """Run engine, return cache dict (npz-friendly) + timing metadata."""
    t0 = time.time()
    audio = _pipeline.load_audio(wav_path)
    # Engine expects mono — librosa.load already does this with mono=True (in _pipeline)
    bundle = _pipeline.run_full_pipeline(audio, nuclei)
    t_run = time.time() - t0
    cache = {
        "htp": bundle["mech_HTP"].astype(np.float32),     # (T, 4)
        "icem": bundle["mech_ICEM"].astype(np.float32),   # (T, 4)
        "ram": bundle["ram"].astype(np.float32),          # (T, 26)
        "neuro": bundle["neuro"].astype(np.float32),      # (T, 4)
        "n_frames": np.int32(bundle["mech_HTP"].shape[0]),
        "n_samples": np.int32(audio.shape[-1]),
    }
    meta = {
        "stim_id": wav_path.stem,
        "wav_sha256": file_sha256(wav_path),
        "n_frames": int(cache["n_frames"]),
        "n_samples": int(cache["n_samples"]),
        "wall_seconds": float(t_run),
    }
    return cache, meta


def per_chord_alignment(cache: dict, pitch_df: pd.DataFrame,
                         half_window_frames: int) -> pd.DataFrame:
    """For each chord onset, compute windowed-mean HTP.E0 and ICEM.E0."""
    htp = cache["htp"]
    icem = cache["icem"]
    rows = []
    for _, prow in pitch_df.iterrows():
        onset_sec = float(prow["onset"])
        frame = int(round(onset_sec * FRAME_RATE_HZ))
        rows.append({
            "song": int(prow["song"]),
            "onset_sec": onset_sec,
            "frame": frame,
            "htp_e0_mean": windowed_mean(htp[:, 0], frame, half_window_frames),
            "icem_e0_mean": windowed_mean(icem[:, 0], frame, half_window_frames),
        })
    df = pd.DataFrame(rows)
    df["chordnumber"] = np.arange(2, 2 + len(df))   # Cheung numbering: chordnumber starts at 2 in CSV (1=cue chord); first onset in pitches file is chord 1 cue → chord 2 onwards
    return df


def main() -> int:
    print("=" * 70)
    print("Phase 10 Audio-Native Upgrade — Angle 1 — MI on rhythm1")
    print(f"Pre-reg: AUDIO_NATIVE_UPGRADE.md §2 Angle 1 (frozen 2026-05-16)")
    print("=" * 70)

    print("\nVerifying engine pin ...")
    actual_sha = aggregate_engine_sha()
    print(f"  expected: {ENGINE_AGGREGATE_SHA_EXPECTED}")
    print(f"  actual:   {actual_sha}")
    if actual_sha != ENGINE_AGGREGATE_SHA_EXPECTED:
        print("ERROR: engine SHA mismatch — abort", file=sys.stderr); return 2

    print("\nBuilding nuclei ...")
    nuclei = _pipeline.build_nuclei()
    print(f"  built {len(nuclei)} nuclei")

    wavs = sorted(WAV_DIR.glob("*.wav"))
    print(f"\nFound {len(wavs)} rhythm1 WAVs")
    if len(wavs) != 30:
        print(f"  WARN: expected 30, got {len(wavs)}", file=sys.stderr)

    half_window_frames = int(round((WINDOW_MS / 1000.0) * FRAME_RATE_HZ))
    print(f"  alignment window: ±{WINDOW_MS:.0f} ms = ±{half_window_frames} frames @ {FRAME_RATE_HZ:.2f} Hz")

    # Load Cheung's IDyOM IC/ENT (chord-level constants — pick first VPID per (song, chordnumber, rhythm=1))
    print("\nLoading Cheung IDyOM columns (rhythm=1 subset, first VPID per chord) ...")
    df_full = pd.read_csv(PLEASURE_CSV)
    df_full.columns = [c.lstrip("﻿") for c in df_full.columns]
    df_r1 = df_full[df_full["rhythm"] == 1].copy()
    # IDyOM IC/ENT are constant per (song, chordnumber) — confirm by drop_duplicates
    idyom_per_chord = (df_r1.drop_duplicates(subset=["song", "chordnumber"])
                            [["song", "chordnumber", "IC", "ENTROPY"]]
                            .reset_index(drop=True))
    print(f"  IDyOM rhythm-1 chord-level rows: {len(idyom_per_chord)} "
          f"(across {idyom_per_chord['song'].nunique()} songs)")

    # Process each stim
    audio_records = []
    per_chord_all = []
    per_stim_corr = []
    for wav_path in wavs:
        stim_id = wav_path.stem
        # Parse song number from stim_id like "merged_wav_stim01_rhythm01" → song=1
        # Cheung 30 stim → song 1..30
        try:
            song_num = int(stim_id.split("_stim")[1].split("_")[0])
        except Exception:
            print(f"  {stim_id}: cannot parse song number, skipping", file=sys.stderr)
            continue

        pitch_path = PITCH_DIR / f"pitches_merged_wav_stim{song_num:02d}.txt"
        if not pitch_path.exists():
            print(f"  {stim_id}: missing pitch file {pitch_path.name}, skipping")
            continue

        print(f"  {stim_id} (song={song_num}): extracting ...", end=" ", flush=True)
        cache, meta = extract_one_stim(wav_path, nuclei)
        # Save compact npz cache
        out_npz = CACHE_DIR / f"{stim_id}.npz"
        np.savez_compressed(out_npz, **cache)
        meta["cache_npz"] = str(out_npz.relative_to(PHASE_DIR))
        meta["song"] = song_num
        audio_records.append(meta)

        # Per-chord alignment
        pitch_df = pd.read_csv(pitch_path, sep="\t")
        per_chord_df = per_chord_alignment(cache, pitch_df, half_window_frames)
        per_chord_df["song"] = song_num   # ensure consistency with stim
        per_chord_df["stim_id"] = stim_id

        # Merge with IDyOM at same (song, chordnumber)
        idyom_song = idyom_per_chord[idyom_per_chord["song"] == song_num].copy()
        merged = per_chord_df.merge(idyom_song, on=["song", "chordnumber"], how="inner",
                                     suffixes=("_mi", "_idyom"))
        per_chord_all.append(merged)

        # Per-stimulus correlation
        if len(merged) >= 5 and merged["htp_e0_mean"].std() > 0 and merged["ENTROPY"].std() > 0:
            r_he, p_he = scistats.pearsonr(merged["htp_e0_mean"], merged["ENTROPY"])
            r_ii, p_ii = scistats.pearsonr(merged["icem_e0_mean"], merged["IC"])
        else:
            r_he, p_he, r_ii, p_ii = np.nan, np.nan, np.nan, np.nan
        per_stim_corr.append({
            "stim_id": stim_id,
            "song": song_num,
            "n_chord_rows_aligned": int(len(merged)),
            "r_HTP_ENT": float(r_he) if not np.isnan(r_he) else None,
            "p_HTP_ENT": float(p_he) if not np.isnan(p_he) else None,
            "r_ICEM_IC": float(r_ii) if not np.isnan(r_ii) else None,
            "p_ICEM_IC": float(p_ii) if not np.isnan(p_ii) else None,
        })
        print(f"ok ({meta['n_frames']} frames, {meta['wall_seconds']:.1f}s, "
              f"{len(merged)} aligned chords, r(HTP,ENT)={r_he:+.3f}, r(ICEM,IC)={r_ii:+.3f})")

    # Save per-chord merged
    if per_chord_all:
        pd.concat(per_chord_all, ignore_index=True).to_csv(
            RESULTS_DIR / "angle1_per_chord_aligned.csv", index=False)

    # Save per-stim corr
    psc_df = pd.DataFrame(per_stim_corr)
    psc_df.to_csv(RESULTS_DIR / "angle1_per_stim_correlations.csv", index=False)

    # Aggregate
    rs_he = [r["r_HTP_ENT"] for r in per_stim_corr if r["r_HTP_ENT"] is not None]
    rs_ii = [r["r_ICEM_IC"] for r in per_stim_corr if r["r_ICEM_IC"] is not None]
    rng = np.random.default_rng(SEED)

    def boot_median_ci(vs):
        if len(vs) < 3: return (float("nan"), float("nan"))
        arr = np.array(vs)
        meds = []
        for _ in range(N_BOOTSTRAP):
            idx = rng.integers(0, len(arr), size=len(arr))
            meds.append(np.median(arr[idx]))
        return float(np.quantile(meds, 0.025)), float(np.quantile(meds, 0.975))

    median_he, median_ii = float(np.median(rs_he)), float(np.median(rs_ii))
    ci_he, ci_ii = boot_median_ci(rs_he), boot_median_ci(rs_ii)

    # Decision rule per pre-reg §2 Angle 1
    pos = median_he >= 0.5 and median_ii >= 0.5
    neg = median_he <= 0.2 or median_ii <= 0.2
    if pos and not neg:
        verdict = "POSITIVE_SUBSTITUTION_VALID"
    elif neg and not pos:
        verdict = "NEGATIVE_SUBSTITUTION_INVALID"
    else:
        verdict = "INCONCLUSIVE"

    aggregate = {
        "n_stimuli": len(rs_he),
        "alignment_window_ms": WINDOW_MS,
        "channels": {"MI_HTP_channel": "E0_high_level_lead", "MI_ICEM_channel": "E0_information_content"},
        "r_HTP_ENT": {
            "median": median_he, "ci95": list(ci_he),
            "min": float(np.min(rs_he)), "max": float(np.max(rs_he)),
            "iqr": [float(np.quantile(rs_he, 0.25)), float(np.quantile(rs_he, 0.75))],
            "n": len(rs_he),
        },
        "r_ICEM_IC": {
            "median": median_ii, "ci95": list(ci_ii),
            "min": float(np.min(rs_ii)), "max": float(np.max(rs_ii)),
            "iqr": [float(np.quantile(rs_ii, 0.25)), float(np.quantile(rs_ii, 0.75))],
            "n": len(rs_ii),
        },
        "decision": {"verdict": verdict,
                     "rule_pos": "median r(HTP,ENT) >= 0.5 AND median r(ICEM,IC) >= 0.5",
                     "rule_neg": "either median <= 0.2"},
    }

    output = {
        "stage": "Phase 10 Audio-Native Upgrade — Angle 1",
        "engine_pin_commit": ENGINE_PIN_COMMIT,
        "engine_aggregate_sha256": actual_sha,
        "rhythm_condition": 1,
        "audio_records": audio_records,
        "aggregate": aggregate,
        "library_versions": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": __import__("scipy").__version__,
        },
    }
    with open(RESULTS_DIR / "angle1_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print()
    print("=" * 70)
    print(f"VERDICT: {verdict}")
    print(f"  median r(MI_HTP, IDyOM_ENTROPY)  = {median_he:+.4f}  CI95 [{ci_he[0]:+.4f}, {ci_he[1]:+.4f}]")
    print(f"  median r(MI_ICEM, IDyOM_IC)      = {median_ii:+.4f}  CI95 [{ci_ii[0]:+.4f}, {ci_ii[1]:+.4f}]")
    print(f"  range r(HTP,ENT) [{np.min(rs_he):+.3f}, {np.max(rs_he):+.3f}]")
    print(f"  range r(ICEM,IC) [{np.min(rs_ii):+.3f}, {np.max(rs_ii):+.3f}]")
    print("=" * 70)
    print(f"Cached engine outputs: {CACHE_DIR}/ ({len(audio_records)} npz files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
