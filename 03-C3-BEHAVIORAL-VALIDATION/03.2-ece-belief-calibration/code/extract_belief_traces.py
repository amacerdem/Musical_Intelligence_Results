#!/usr/bin/env python3
"""V6 A2 — Extract (π_pred, PE) traces for 8 selected Core beliefs across 5 DEAM held-out songs.

Pre-registered in `Science/V6/01-pre-registration.md` §A2.

Inputs:
  - 5 DEAM held-out songs: IDs 1034, 1508, 1777, 1896, 1923
  - 8 Core beliefs (1 per cognitive function F1-F8):
      F1 BCH HarmonicStability
      F2 HTP PredictionAccuracy
      F3 IACM AttentionCapture
      F4 HCMC EpisodicEncoding
      F5 AAC EmotionalArousal
      F6 SRP Pleasure
      F7 HGSIC GrooveQuality
      F8 SLEE StatisticalModel

Outputs:
  - `Science/V6/results/A2_traces/{song_id}.npz`: per-song dict with 8 belief traces
    Each trace: (T_post_warmup,) arrays of pi_pred, PE, accurate, posterior, obs
  - Warm-up: first 16 frames per (song, belief) dropped per pre-reg §A2

Determinism: engine HEAD verified at scaffold (5b9aba41+ acceptable);
all numpy/torch ops deterministic-by-construction (no random state used in extraction).
"""
from __future__ import annotations

import importlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import numpy as np
import torch

# V-Reproduction layout: file lives at V-Reproduction/05-ece-belief-calibration/code/
# parents[1] = V-Reproduction/05-ece-belief-calibration/ (this phase's root)
# parents[2] = V-Reproduction/  (vendored engine lives here under engine/)
# parents[3] = Science/ (parent-checkout engine fallback)
_REPRO_ROOT = Path(__file__).resolve().parents[1]
_VREPRO_ROOT = Path(__file__).resolve().parents[2]
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Prefer vendored engine snapshot at V-Reproduction/engine/, fallback to parent.
sys.path.insert(0, str(_VREPRO_ROOT / "_infra"))
import _engine_path  # noqa: E402,F401  (side effect: prepends ENGINE_PARENT to sys.path)

# ── Paper conventions ────────────────────────────────────────────────
SAMPLE_RATE = 44_100
HOP_LENGTH = 256
N_MELS = 128
N_FFT = 2048
FRAME_RATE = SAMPLE_RATE / HOP_LENGTH  # 172.27 Hz
WARMUP_FRAMES = 16  # paper §S5 precision-window warm-up
MAX_DURATION_S = 30.0  # paper convention (V2/T-R3-08: 30 s × 172.27 fps = 5168 frames)

# DEAM dataset path: prefer vendored datasets/ under V-Repro, fallback to Science/
_VENDORED_DEAM = _VREPRO_ROOT / "datasets/emotion/DEAM/audio/MEMD_audio"
_PARENT_DEAM = _PROJECT_ROOT / "datasets/emotion/DEAM/audio/MEMD_audio"
DEAM_AUDIO_DIR = _VENDORED_DEAM if _VENDORED_DEAM.is_dir() else _PARENT_DEAM
HELD_OUT_SONG_IDS = [1034, 1508, 1777, 1896, 1923]

OUT_DIR = _REPRO_ROOT / "results/traces"


# ── PRIMARY: paper's 8 Core beliefs (V2/T-R3-08 methodology, F1×4 + F2×4) ──
# This subset reproduces paper's pooled ECE = 0.079 by construction.
PAPER_BELIEFS: List[Tuple[str, str, str, str]] = [
    ("F1", "BCH",   "Musical_Intelligence.brain.functions.f1.beliefs.bch.harmonic_stability",     "HarmonicStability"),
    ("F1", "PSCL",  "Musical_Intelligence.brain.functions.f1.beliefs.pscl.pitch_prominence",      "PitchProminence"),
    ("F1", "PCCR",  "Musical_Intelligence.brain.functions.f1.beliefs.pccr.pitch_identity",        "PitchIdentity"),
    ("F1", "MIAA",  "Musical_Intelligence.brain.functions.f1.beliefs.miaa.timbral_character",     "TimbralCharacter"),
    ("F2", "HTP",   "Musical_Intelligence.brain.functions.f2.beliefs.htp.prediction_hierarchy",   "PredictionHierarchy"),
    ("F2", "HTP",   "Musical_Intelligence.brain.functions.f2.beliefs.htp.prediction_accuracy",    "PredictionAccuracy"),
    ("F2", "SPH",   "Musical_Intelligence.brain.functions.f2.beliefs.sph.sequence_match",         "SequenceMatch"),
    ("F2", "ICEM",  "Musical_Intelligence.brain.functions.f2.beliefs.icem.information_content",   "InformationContent"),
]

# ── EXTENSION: V6's 6 additional beliefs (F3-F8) — V6's novel test ──
# These are NOT in paper's 8. V6 measures whether calibration generalizes
# to attention/memory/emotion/reward/motor/learning beliefs.
EXTENSION_BELIEFS: List[Tuple[str, str, str, str]] = [
    ("F3", "IACM",  "Musical_Intelligence.brain.functions.f3.beliefs.iacm.attention_capture",  "AttentionCapture"),
    ("F4", "HCMC",  "Musical_Intelligence.brain.functions.f4.beliefs.hcmc.episodic_encoding",  "EpisodicEncoding"),
    ("F5", "AAC",   "Musical_Intelligence.brain.functions.f5.beliefs.aac.emotional_arousal",   "EmotionalArousal"),
    ("F6", "SRP",   "Musical_Intelligence.brain.functions.f6.beliefs.srp.pleasure",            "Pleasure"),
    ("F7", "HGSIC", "Musical_Intelligence.brain.functions.f7.beliefs.hgsic.groove_quality",    "GrooveQuality"),
    ("F8", "SLEE",  "Musical_Intelligence.brain.functions.f8.beliefs.slee.statistical_model",  "StatisticalModel"),
]

SELECTED_BELIEFS = PAPER_BELIEFS + EXTENSION_BELIEFS  # 14 total: 8 paper + 6 extension


def collect_mechanisms() -> Tuple[List[Any], Set[Tuple[int, int, int, int]]]:
    """Auto-discover all mechanism instances across F1-F8."""
    from Musical_Intelligence.contracts.bases.nucleus import _NucleusBase

    role_to_depth = {"relay": 0, "encoder": 1, "associator": 2, "integrator": 3, "hub": 4}
    seen: set = set()
    nuclei: List[Any] = []

    for fn in ("f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9"):
        try:
            mod = importlib.import_module(f"Musical_Intelligence.brain.functions.{fn}.mechanisms")
        except Exception:
            continue
        for attr_name in getattr(mod, "__all__", []):
            cls = getattr(mod, attr_name, None)
            if cls is None:
                continue
            try:
                inst = cls()
            except Exception:
                continue
            if not isinstance(inst, _NucleusBase):
                continue
            if inst.NAME in seen:
                continue
            seen.add(inst.NAME)
            role = getattr(inst, "ROLE", "relay")
            min_depth = role_to_depth.get(role, 0)
            if inst.PROCESSING_DEPTH < min_depth:
                inst.PROCESSING_DEPTH = min_depth
            nuclei.append(inst)

    h3_demands: Set[Tuple[int, int, int, int]] = set()
    for m in nuclei:
        for spec in m.h3_demand:
            h3_demands.add(spec.as_tuple())

    return nuclei, h3_demands


def run_engine_on_song(song_path: Path, nuclei, h3_demands) -> Dict[str, Any]:
    """Run R³ → H³ → mechanisms on a song; return outputs + h3_features + r3_features."""
    import torchaudio
    import librosa
    from Musical_Intelligence.ear.r3 import R3Extractor
    from Musical_Intelligence.ear.h3 import H3Extractor
    from Musical_Intelligence.brain.executor import execute

    r3_extractor = R3Extractor()
    h3_extractor = H3Extractor()
    mel_transform = torchaudio.transforms.MelSpectrogram(
        sample_rate=SAMPLE_RATE,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        n_mels=N_MELS,
        power=2.0,
    )

    # 30s clip cap (paper convention: V2/T-R3-08 MAX_DURATION_S = 30.0)
    y, _ = librosa.load(str(song_path), sr=SAMPLE_RATE, mono=True, duration=MAX_DURATION_S)
    audio_t = torch.from_numpy(y).unsqueeze(0).float()

    with torch.no_grad():
        mel = torch.log1p(mel_transform(audio_t))
        mel_max = mel.amax(dim=(-2, -1), keepdim=True).clamp(min=1e-8)
        mel = mel / mel_max
        r3_out = r3_extractor.extract(mel, audio=audio_t, sr=SAMPLE_RATE)
        r3_features = r3_out.features
        h3_out = h3_extractor.extract(r3_features, h3_demands)
        outputs, ram, neuro = execute(nuclei, h3_out.features, r3_features)

    return {
        "outputs": outputs,
        "h3_features": h3_out.features,
        "r3_features": r3_features,
        "duration_s": len(y) / SAMPLE_RATE,
        "n_frames": r3_features.shape[1],
    }


def extract_belief_trace(belief_inst, mechanism_output, h3_features) -> Dict[str, np.ndarray]:
    """Run Bayesian belief cycle for a single belief; return (π_pred, PE, accurate, posterior) traces.

    Empty context is used (V6 operationalization, disclosed in pre-reg §A2 SCOPE NOTE).
    Warm-up first 16 frames dropped (paper convention).
    """
    context: Dict[str, torch.Tensor] = {}

    with torch.no_grad():
        result = belief_inst.run_cycle(
            mechanism_output=mechanism_output,
            context=context,
            h3_features=h3_features,
        )

    pi_pred = result["pi_pred"][0].cpu().numpy()  # (T,)
    pe = result["pe"][0].cpu().numpy()
    posterior = result["posterior"][0].cpu().numpy()
    obs = result["obs"][0].cpu().numpy()

    # Drop warm-up
    pi_pred = pi_pred[WARMUP_FRAMES:]
    pe = pe[WARMUP_FRAMES:]
    posterior = posterior[WARMUP_FRAMES:]
    obs = obs[WARMUP_FRAMES:]

    # Paper convention (V2/T-R3-08): y = 1 - |PE|, continuous [0,1]
    y_continuous = 1.0 - np.clip(np.abs(pe), 0.0, 1.0)

    return {
        "pi_pred": pi_pred,
        "pe": pe,
        "posterior": posterior,
        "obs": obs,
        "y_continuous": y_continuous,
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Collect engine
    print(f"[A2] collecting engine mechanisms...")
    t0 = time.time()
    nuclei, h3_demands = collect_mechanisms()
    print(f"[A2]   {len(nuclei)} mechanisms, {len(h3_demands)} h3 demands ({time.time()-t0:.1f}s)")

    # 2. Instantiate the 8 selected beliefs
    belief_instances: List[Tuple[str, str, str, Any]] = []  # (function, mech_key, belief_name, instance)
    for fn, mech_key, mod_path, cls_name in SELECTED_BELIEFS:
        try:
            mod = importlib.import_module(mod_path)
            cls = getattr(mod, cls_name)
            inst = cls()
            belief_instances.append((fn, mech_key, cls_name, inst))
            print(f"[A2]   loaded {fn} {mech_key}.{cls_name}")
        except Exception as e:
            print(f"[A2]   !! FAILED to load {fn} {mech_key}.{cls_name}: {e}")
            return 2

    # 3. Loop over songs
    summary: List[Dict[str, Any]] = []
    for song_id in HELD_OUT_SONG_IDS:
        song_path = DEAM_AUDIO_DIR / f"{song_id}.mp3"
        if not song_path.exists():
            print(f"[A2] !! song missing: {song_path}")
            return 3

        print(f"\n[A2] song {song_id}: running engine...")
        t0 = time.time()
        engine_state = run_engine_on_song(song_path, nuclei, h3_demands)
        print(f"[A2]   engine done: {engine_state['duration_s']:.1f}s audio, "
              f"{engine_state['n_frames']} frames ({time.time()-t0:.1f}s wall)")

        # 4. Extract per-belief traces
        traces: Dict[str, Dict[str, np.ndarray]] = {}
        for fn, mech_key, cls_name, belief_inst in belief_instances:
            outputs = engine_state["outputs"]
            if mech_key not in outputs:
                print(f"[A2]   !! {mech_key} not in outputs (keys: {list(outputs.keys())[:10]}...)")
                continue
            mech_out = outputs[mech_key]  # (1, T, D)
            t0b = time.time()
            try:
                trace = extract_belief_trace(
                    belief_inst,
                    mech_out,
                    engine_state["h3_features"],
                )
            except Exception as e:
                print(f"[A2]   !! {fn} {cls_name} run_cycle failed: {e}")
                continue

            traces[f"{fn}_{cls_name}"] = trace
            ece_quick = quick_ece(trace["pi_pred"], trace["y_continuous"])
            print(f"[A2]   {fn} {cls_name:<22}: T={len(trace['pi_pred'])}, "
                  f"|PE|={np.abs(trace['pe']).mean():.3f}, "
                  f"π_pred={trace['pi_pred'].mean():.3f}, "
                  f"y={trace['y_continuous'].mean():.3f}, "
                  f"ECE={ece_quick:.4f} ({time.time()-t0b:.1f}s)")
            summary.append({
                "song_id": song_id,
                "function": fn,
                "mechanism": mech_key,
                "belief_class": cls_name,
                "n_frames": int(len(trace["pi_pred"])),
                "mean_pi_pred": float(trace["pi_pred"].mean()),
                "mean_abs_pe": float(np.abs(trace["pe"]).mean()),
                "mean_accurate": float(trace["y_continuous"].mean()),
                "ece_simple": float(ece_quick),
            })

        # 5. Save per-song traces
        out_path = OUT_DIR / f"song_{song_id}.npz"
        np.savez_compressed(out_path, **{
            f"{name}__{k}": v
            for name, trace in traces.items()
            for k, v in trace.items()
        })
        print(f"[A2]   saved {out_path.name} ({len(traces)} beliefs)")

    # 6. Save summary CSV
    import csv
    summary_path = OUT_DIR.parent / "A2_per_cell_summary.csv"
    with open(summary_path, "w", newline="") as f:
        if summary:
            w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
            w.writeheader()
            w.writerows(summary)
    print(f"\n[A2] summary CSV: {summary_path}")
    print(f"[A2] N rows: {len(summary)} (expected 5 songs × 8 beliefs = 40)")
    print("[A2] PASS")
    return 0


def quick_ece(pi_pred: np.ndarray, accurate: np.ndarray, n_bins: int = 10) -> float:
    """Equal-mass binned ECE."""
    n = len(pi_pred)
    if n < n_bins:
        return float("nan")
    sorted_idx = np.argsort(pi_pred)
    bin_edges = np.linspace(0, n, n_bins + 1).astype(int)
    ece = 0.0
    for i in range(n_bins):
        idx = sorted_idx[bin_edges[i]:bin_edges[i+1]]
        if len(idx) == 0:
            continue
        bin_mean_pp = pi_pred[idx].mean()
        bin_mean_acc = accurate[idx].mean()
        ece += (len(idx) / n) * abs(bin_mean_pp - bin_mean_acc)
    return ece


if __name__ == "__main__":
    sys.exit(main())
