#!/usr/bin/env python3
"""T-R3-08 Phase B — Frozen-engine capture of per-frame belief cycle traces.

Authorized by Amaç 2026-04-22 (~30 min M2 Max compute). No engine edit;
this script imports frozen MI modules and captures the return dict of
``CoreBelief.run_cycle()`` at the caller site. The engine code
(``Musical_Intelligence/*``) is NOT modified.

Pipeline per song:
    mp3 → mono 44.1k → log-mel(128,256,2048) → R³Extractor → H³Extractor
    → mechanism chain (depth-ordered: BCH, MIAA, HTP, SPH, ICEM, PSCL,
      PCCR) → for each of 8 CoreBeliefs, call run_cycle(mechanism_output,
      context, h3_features) → save {obs, pred, pe, pi_obs, pi_pred, gain,
      posterior} per (song, belief) to belief_traces_T-R3-08.npz.

Held-out DEAM selection: seed=42 random.choice from DEAM song_ids with
id > 1000 (safely past F5 N=200 calibration range).

Beliefs captured (8, same as V1 BAYESIAN_CYCLE_VALIDATION.md):
    F1: harmonic_stability (BCH), pitch_prominence (PSCL),
        pitch_identity (PCCR), timbral_character (MIAA)
    F2: prediction_hierarchy (HTP), prediction_accuracy (HTP),
        sequence_match (SPH), information_content (ICEM)

Outputs:
    computing-phase/T-R3-08/belief_traces_T-R3-08.npz
    computing-phase/T-R3-08/phase_b_capture.log
"""
from __future__ import annotations

import random
import sys
import time
import warnings
from collections import OrderedDict
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import torch

warnings.filterwarnings("ignore")

# Repo root = .../Science
HERE = Path(__file__).resolve().parent
SCIENCE_ROOT = HERE.parents[4]  # computing-phase/T-R3-08 -> .../Science
assert SCIENCE_ROOT.name == "Science", f"unexpected root {SCIENCE_ROOT}"
if str(SCIENCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SCIENCE_ROOT))

# ── Constants (match V1 pipeline) ───────────────────────────────────────
SAMPLE_RATE = 44_100
HOP_LENGTH = 256
N_MELS = 128
N_FFT = 2048
FRAME_RATE = SAMPLE_RATE / HOP_LENGTH  # ~172.27 Hz
# Cap to 30 s per DEAM clip (DEAM clips are typically 45 s);
# 30 s × 172.27 fps = 5168 frames per song-belief, 5 songs × 8 = 40 traces.
MAX_DURATION_S = 30.0

DEAM_AUDIO_DIR = SCIENCE_ROOT / "datasets" / "emotion" / "DEAM" / "audio" / "MEMD_audio"
DEAM_SONG_CSV = (
    SCIENCE_ROOT
    / "datasets"
    / "emotion"
    / "DEAM"
    / "annotations"
    / "annotations averaged per song"
    / "song_level"
    / "static_annotations_averaged_songs_1_2000.csv"
)

OUT_NPZ = HERE / "belief_traces_T-R3-08.npz"
LOG_FILE = HERE / "phase_b_capture.log"


def log(msg: str, fh=None) -> None:
    stamp = time.strftime("%H:%M:%S")
    line = f"[{stamp}] {msg}"
    print(line, flush=True)
    if fh is not None:
        fh.write(line + "\n")
        fh.flush()


def select_heldout_songs(seed: int = 42, n: int = 5) -> list:
    """Seed=42 deterministic choice of 5 DEAM song IDs > 1000.

    F5 calibration used N=200 DEAM songs (per V2/results/GT-0003/
    f5_deam_extracted.md). Restricting to song_id > 1000 provides a
    conservative safety margin — these IDs are not in any V1 F5
    calibration or validation manifest.
    """
    import csv
    all_ids = []
    with open(DEAM_SONG_CSV, newline="") as fh:
        reader = csv.reader(fh)
        next(reader)  # header
        for row in reader:
            if not row:
                continue
            sid = int(row[0].strip())
            if sid > 1000:
                audio_path = DEAM_AUDIO_DIR / f"{sid}.mp3"
                if audio_path.exists():
                    all_ids.append(sid)
    rng = random.Random(seed)
    rng.shuffle(all_ids)
    return sorted(all_ids[:n])


def load_audio(path: Path) -> torch.Tensor:
    """Load audio → (1, N) mono waveform at 44.1 kHz, trimmed to MAX_DURATION_S."""
    import torchaudio
    try:
        wav, sr = torchaudio.load(str(path))
        if wav.shape[0] > 1:
            wav = wav.mean(dim=0, keepdim=True)
        if sr != SAMPLE_RATE:
            wav = torchaudio.transforms.Resample(sr, SAMPLE_RATE)(wav)
    except Exception:
        import librosa
        y, _ = librosa.load(str(path), sr=SAMPLE_RATE, mono=True, duration=MAX_DURATION_S)
        wav = torch.from_numpy(y).unsqueeze(0).float()
    max_s = int(MAX_DURATION_S * SAMPLE_RATE)
    if wav.shape[-1] > max_s:
        wav = wav[:, :max_s]
    return wav


# ── Mechanism + belief factory (frozen imports) ─────────────────────────
def build_mechs_and_beliefs():
    from Musical_Intelligence.brain.functions.f1.mechanisms.bch import BCH
    from Musical_Intelligence.brain.functions.f1.mechanisms.miaa import MIAA
    from Musical_Intelligence.brain.functions.f1.mechanisms.pscl import PSCL
    from Musical_Intelligence.brain.functions.f1.mechanisms.pccr import PCCR
    from Musical_Intelligence.brain.functions.f2.mechanisms.htp import HTP
    from Musical_Intelligence.brain.functions.f2.mechanisms.sph import SPH
    from Musical_Intelligence.brain.functions.f2.mechanisms.icem import ICEM

    mechs = OrderedDict([
        ("bch", BCH()),
        ("miaa", MIAA()),
        ("htp", HTP()),
        ("sph", SPH()),
        ("icem", ICEM()),
        ("pscl", PSCL()),   # depth 1
        ("pccr", PCCR()),   # depth 2
    ])

    from Musical_Intelligence.brain.functions.f1.beliefs.bch.harmonic_stability import HarmonicStability
    from Musical_Intelligence.brain.functions.f1.beliefs.pscl.pitch_prominence import PitchProminence
    from Musical_Intelligence.brain.functions.f1.beliefs.pccr.pitch_identity import PitchIdentity
    from Musical_Intelligence.brain.functions.f1.beliefs.miaa.timbral_character import TimbralCharacter
    from Musical_Intelligence.brain.functions.f2.beliefs.htp.prediction_hierarchy import PredictionHierarchy
    from Musical_Intelligence.brain.functions.f2.beliefs.htp.prediction_accuracy import PredictionAccuracy
    from Musical_Intelligence.brain.functions.f2.beliefs.sph.sequence_match import SequenceMatch
    from Musical_Intelligence.brain.functions.f2.beliefs.icem.information_content import InformationContent

    # Each entry: (belief_name, mech_key_for_mechanism_output, BeliefInstance)
    beliefs = [
        ("harmonic_stability", "bch", HarmonicStability()),
        ("pitch_prominence", "pscl", PitchProminence()),
        ("pitch_identity", "pccr", PitchIdentity()),
        ("timbral_character", "miaa", TimbralCharacter()),
        ("prediction_hierarchy", "htp", PredictionHierarchy()),
        ("prediction_accuracy", "htp", PredictionAccuracy()),
        ("sequence_match", "sph", SequenceMatch()),
        ("information_content", "icem", InformationContent()),
    ]
    return mechs, beliefs


def main() -> int:
    t0 = time.time()
    fh = open(LOG_FILE, "w")
    log(f"T-R3-08 Phase B capture. Authorized by Amaç 2026-04-22.", fh)
    log(f"Output: {OUT_NPZ}", fh)

    # 1. Held-out DEAM selection
    song_ids = select_heldout_songs(seed=42, n=5)
    log(f"Selected DEAM song IDs (seed=42, id>1000): {song_ids}", fh)

    # 2. Frozen engine setup
    import torchaudio
    from Musical_Intelligence.ear.r3 import R3Extractor
    from Musical_Intelligence.ear.h3 import H3Extractor

    log("Loading R3 + H3 extractors (frozen) ...", fh)
    r3 = R3Extractor()
    h3 = H3Extractor()
    mel_op = torchaudio.transforms.MelSpectrogram(
        sample_rate=SAMPLE_RATE, n_fft=N_FFT,
        hop_length=HOP_LENGTH, n_mels=N_MELS, power=2.0,
    )

    mechs, belief_specs = build_mechs_and_beliefs()
    log(f"Loaded {len(mechs)} mechanisms, {len(belief_specs)} beliefs", fh)

    # Collect H³ demands from all mechanisms + all belief precision tuples
    h3_demands = set()
    for m in mechs.values():
        for spec in m.h3_demand:
            h3_demands.add(spec.as_tuple())
    for _, _, bobj in belief_specs:
        for tup in bobj.PRECISION_H3_TUPLES:
            h3_demands.add(tup)
    # Add belief predict() H³ tuples — harvested by hand from source
    # to avoid missing any (they default to zero if missing, but we want
    # the real H³ features for fidelity):
    extra_predict_tuples = [
        # harmonic_stability
        (0, 6, 18, 0), (0, 12, 1, 0),
        # pitch_prominence (defaults fine, observe-only on PSCL output)
        # pitch_identity
        # timbral_character
        # prediction_hierarchy
        (60, 8, 18, 0), (11, 3, 14, 2),
        # prediction_accuracy
        # sequence_match
        # information_content
    ]
    for tup in extra_predict_tuples:
        h3_demands.add(tup)
    log(f"Total unique H³ demand tuples: {len(h3_demands)}", fh)

    # 3. Per-song capture
    all_traces: Dict[str, np.ndarray] = {}
    total_frames = 0
    for sid in song_ids:
        audio_path = DEAM_AUDIO_DIR / f"{sid}.mp3"
        log(f"── Song {sid} → {audio_path.name} ──", fh)
        t_song = time.time()

        wav = load_audio(audio_path)
        log(f"  loaded audio: shape={tuple(wav.shape)} ({wav.shape[-1]/SAMPLE_RATE:.1f}s)", fh)

        with torch.no_grad():
            mel = torch.log1p(mel_op(wav))
            mel = mel / mel.amax(dim=(-2, -1), keepdim=True).clamp(min=1e-8)
            r3_out = r3.extract(mel, audio=wav, sr=SAMPLE_RATE)
            r3_feat = r3_out.features  # (1, T, 97)
            h3_out = h3.extract(r3_feat, h3_demands)
            h3_feat = h3_out.features
        T = r3_feat.shape[1]
        total_frames += T
        log(f"  R³ shape={tuple(r3_feat.shape)}, H³ demands x frames = {len(h3_feat)} tuples", fh)

        # Mechanism chain (depth order)
        with torch.no_grad():
            mech_out: Dict[str, torch.Tensor] = {}
            mech_out["bch"] = mechs["bch"].compute(h3_feat, r3_feat)
            mech_out["miaa"] = mechs["miaa"].compute(h3_feat, r3_feat)
            mech_out["htp"] = mechs["htp"].compute(h3_feat, r3_feat)
            mech_out["sph"] = mechs["sph"].compute(h3_feat, r3_feat)
            mech_out["icem"] = mechs["icem"].compute(h3_feat, r3_feat)
            mech_out["pscl"] = mechs["pscl"].compute(h3_feat, r3_feat, {"BCH": mech_out["bch"]})
            mech_out["pccr"] = mechs["pccr"].compute(h3_feat, r3_feat, {
                "BCH": mech_out["bch"], "PSCL": mech_out["pscl"],
            })
        log(f"  mechanism chain done", fh)

        # Run each belief's full Bayesian cycle
        empty_ctx: Dict[str, torch.Tensor] = {}
        for bname, mkey, bobj in belief_specs:
            mout = mech_out[mkey]
            with torch.no_grad():
                trace = bobj.run_cycle(mout, empty_ctx, h3_feat)
            # Save per-belief tensors (1, T) as numpy arrays, stripped of batch
            for k, v in trace.items():
                arr = v.detach().cpu().numpy()
                if arr.ndim >= 2 and arr.shape[0] == 1:
                    arr = arr[0]
                all_traces[f"{sid}__{bname}__{k}"] = arr.astype(np.float32)
            log(f"  {bname:22s} cycle captured (T={T})", fh)

        log(f"  song {sid} done in {time.time()-t_song:.1f}s", fh)

    # 4. Save all traces
    log(f"Saving {len(all_traces)} trace arrays to {OUT_NPZ.name} ...", fh)
    np.savez_compressed(OUT_NPZ, **all_traces)
    log(f"  saved, on-disk size ≈ {OUT_NPZ.stat().st_size/1e6:.1f} MB", fh)

    elapsed = time.time() - t0
    log(f"DONE. total_frames={total_frames}, wall={elapsed:.1f}s", fh)
    fh.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
