#!/usr/bin/env python3
"""V6 A2 — Quick test: extract (π_pred, PE) for HarmonicStability on 1 DEAM song.

Verifies that we can:
  1. Run MIPipeline on a DEAM mp3
  2. Capture mechanism outputs + h3_features (not just final beliefs)
  3. Manually invoke CoreBelief.run() to get the full Bayesian trace
  4. Verify shape and value ranges of (π_pred, PE)

If this works, scale to all 8 beliefs × 5 songs in extract_belief_traces.py.
"""
from __future__ import annotations

import importlib
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import numpy as np
import torch

# Project root: V6 → Science → root
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def main() -> int:
    import torchaudio
    import librosa
    from Musical_Intelligence.ear.r3 import R3Extractor
    from Musical_Intelligence.ear.h3 import H3Extractor
    from Musical_Intelligence.brain.executor import execute
    from Musical_Intelligence.brain.functions.f1.beliefs.bch.harmonic_stability import (
        HarmonicStability,
    )

    import os

    SAMPLE_RATE = 44_100
    HOP_LENGTH = 256
    N_MELS = 128
    N_FFT = 2048
    _REPO_ROOT = Path(__file__).resolve().parents[3]
    DEAM_AUDIO = Path(os.environ.get(
        "DEAM_AUDIO_DIR",
        _REPO_ROOT / "datasets/emotion/DEAM/audio/MEMD_audio",
    ))
    SONG_ID = 1034
    DURATION = 30.0  # 30s test, scale to full later

    # ── 1. Audio load ─────────────────────────────────────────────
    audio_path = DEAM_AUDIO / f"{SONG_ID}.mp3"
    print(f"[test] loading {audio_path.name} ({DURATION}s)...")
    t0 = time.time()
    y, sr = librosa.load(str(audio_path), sr=SAMPLE_RATE, mono=True, duration=DURATION)
    print(f"[test]   loaded {len(y)/sr:.1f}s in {time.time()-t0:.1f}s")

    audio_t = torch.from_numpy(y).unsqueeze(0).float()  # (1, N)
    mel_transform = torchaudio.transforms.MelSpectrogram(
        sample_rate=SAMPLE_RATE,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        n_mels=N_MELS,
        power=2.0,
    )

    # ── 2. R³ ─────────────────────────────────────────────────────
    r3_extractor = R3Extractor()
    print("[test] extracting R³...")
    t0 = time.time()
    with torch.no_grad():
        mel = torch.log1p(mel_transform(audio_t))
        mel_max = mel.amax(dim=(-2, -1), keepdim=True).clamp(min=1e-8)
        mel = mel / mel_max
        r3_out = r3_extractor.extract(mel, audio=audio_t, sr=SAMPLE_RATE)
    r3_features = r3_out.features  # (1, T, 97)
    print(f"[test]   R³ shape {tuple(r3_features.shape)} in {time.time()-t0:.1f}s")

    # ── 3. Collect mechanisms (need BCH for HarmonicStability) ────
    print("[test] collecting mechanisms...")
    from Musical_Intelligence.contracts.bases.nucleus import _NucleusBase
    seen_names: set = set()
    nuclei: List[Any] = []
    _ROLE_TO_DEPTH = {"relay": 0, "encoder": 1, "associator": 2, "integrator": 3, "hub": 4}
    for fn in ("f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9"):
        mod_path = f"Musical_Intelligence.brain.functions.{fn}.mechanisms"
        try:
            mod = importlib.import_module(mod_path)
        except Exception as e:
            print(f"[test]   skip {fn}: {e}")
            continue
        for attr_name in getattr(mod, "__all__", []):
            cls = getattr(mod, attr_name, None)
            if cls is None:
                continue
            try:
                inst = cls()
            except Exception as e:
                print(f"[test]   skip {attr_name}: {e}")
                continue
            if not isinstance(inst, _NucleusBase):
                continue
            if inst.NAME in seen_names:
                continue
            seen_names.add(inst.NAME)
            role = getattr(inst, "ROLE", "relay")
            min_depth = _ROLE_TO_DEPTH.get(role, 0)
            if inst.PROCESSING_DEPTH < min_depth:
                inst.PROCESSING_DEPTH = min_depth
            nuclei.append(inst)
    print(f"[test]   collected {len(nuclei)} mechanisms")

    # ── 4. H³ ─────────────────────────────────────────────────────
    h3_demands: Set[Tuple[int, int, int, int]] = set()
    for m in nuclei:
        for spec in m.h3_demand:
            h3_demands.add(spec.as_tuple())
    h3_extractor = H3Extractor()
    print(f"[test] extracting H³ ({len(h3_demands)} demands)...")
    t0 = time.time()
    with torch.no_grad():
        h3_out = h3_extractor.extract(r3_features, h3_demands)
    print(f"[test]   H³ extracted in {time.time()-t0:.1f}s")

    # ── 5. Execute mechanisms ────────────────────────────────────
    print("[test] executing mechanisms...")
    t0 = time.time()
    with torch.no_grad():
        outputs, ram, neuro = execute(nuclei, h3_out.features, r3_features)
    print(f"[test]   executed in {time.time()-t0:.1f}s; outputs keys (first 5): {list(outputs.keys())[:5]}")

    # ── 6. Find BCH mechanism output ──────────────────────────────
    bch_key = None
    for key in outputs.keys():
        if "bch" in key.lower() or "BCH" in str(outputs[key]):
            bch_key = key
            break
    # Fallback: just look for "BCH" or "bch"
    for key in outputs.keys():
        if "bch" in key.lower():
            bch_key = key
            break
    if bch_key is None:
        # Print all keys to debug
        print(f"[test] !! BCH not found. All keys ({len(outputs)}):")
        for k in outputs.keys():
            print(f"        {k}")
        return 1
    bch_output = outputs[bch_key]  # (1, T, 16) presumably
    print(f"[test]   BCH key='{bch_key}' shape={tuple(bch_output.shape)}")

    # ── 7. Manually invoke HarmonicStability.run() ────────────────
    belief = HarmonicStability()
    print(f"[test] calling HarmonicStability.run()...")
    print(f"[test]   PRECISION_H3_TUPLES needed: {belief.PRECISION_H3_TUPLES}")
    # Get only the H³ features needed by this belief
    h3_for_belief = {
        tup: h3_out.features.get(tup, torch.zeros_like(r3_features[..., 0]))
        for tup in belief.PRECISION_H3_TUPLES + (
            (0, 6, 18, 0),  # roughness trend
            (0, 12, 1, 0),  # roughness period
        )
    }
    print(f"[test]   h3_for_belief keys: {list(h3_for_belief.keys())}")
    # Empty context (no related beliefs available without recursion)
    context = {}
    t0 = time.time()
    with torch.no_grad():
        result = belief.run_cycle(
            mechanism_output=bch_output,
            context=context,
            h3_features=h3_for_belief,
        )
    print(f"[test]   belief.run_cycle() done in {time.time()-t0:.1f}s")
    print(f"[test]   result keys: {list(result.keys())}")

    # ── 8. Verify shapes and ranges ───────────────────────────────
    pi_pred = result["pi_pred"][0].cpu().numpy()  # (T,)
    pe = result["pe"][0].cpu().numpy()  # (T,)
    posterior = result["posterior"][0].cpu().numpy()  # (T,)
    obs = result["obs"][0].cpu().numpy()
    print(f"[test]   pi_pred shape {pi_pred.shape}, range [{pi_pred.min():.3f}, {pi_pred.max():.3f}], mean {pi_pred.mean():.3f}")
    print(f"[test]   PE       shape {pe.shape}, range [{pe.min():.3f}, {pe.max():.3f}], mean abs {abs(pe).mean():.3f}")
    print(f"[test]   posterior range [{posterior.min():.3f}, {posterior.max():.3f}]")
    print(f"[test]   obs range [{obs.min():.3f}, {obs.max():.3f}]")

    # Quick ECE sanity check
    accurate = (np.abs(pe) <= 0.10).astype(np.float32)
    print(f"[test]   accurate rate (|PE|<=0.10): {accurate.mean():.3f}")
    # 10 equal-mass bins
    sorted_idx = np.argsort(pi_pred)
    bin_edges = np.linspace(0, len(pi_pred), 11).astype(int)
    eces = []
    for i in range(10):
        bin_idx = sorted_idx[bin_edges[i]:bin_edges[i+1]]
        if len(bin_idx) == 0:
            continue
        bin_mean_pp = pi_pred[bin_idx].mean()
        bin_mean_acc = accurate[bin_idx].mean()
        eces.append((len(bin_idx)/len(pi_pred)) * abs(bin_mean_pp - bin_mean_acc))
    ece = sum(eces)
    print(f"[test]   quick ECE on 30s of HarmonicStability: {ece:.4f}")

    print("[test] PASS — pipeline works; ready to scale to 8 beliefs × 5 songs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
