#!/usr/bin/env python3
"""Phase 21 — Stage 2: MI features for the Mendelssohn window.

Per pre-reg `01-METHODOLOGY-SPEC.md` Pillar 2 + v1.4 continuous-encoder
paradigm (here restricted to the Mendelssohn-window paper-canonical subset
for paradigm-fit replication with the BOLD cache and Phase 05.1).

Pipeline:
  1. Load MI engine output for Mendelssohn (27608 frames × 26 regions @ 172.27 Hz)
  2. HRF convolve at native 172.27 Hz with SPM canonical HRF
  3. Anti-alias Butterworth LPF (order 4, zero-phase, cutoff = 0.4 / TR)
  4. Resample to TR=2.0 s grid (80 frames target = same length as paper N_TRS)
  5. N1 z-score per region (within-region temporal z-score)

Output:
  data/stage2_mi_mendelssohn.npz  — keys: 'mi_feat' (80, 26), 'region_names' (26,),
                                      'mi_fr_hz' (scalar), 'tr_s' (scalar),
                                      'source_npz' (str), 'meta' (dict)

Engine SHA pin: 318eb2f529d7103e8b7d80b01228357fdc4e0217
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
from scipy.signal import butter, filtfilt, fftconvolve

SCIENCE_ROOT = Path("/Volumes/SRC-9/SRC Musical Intelligence/Science")
PHASE21_ROOT = SCIENCE_ROOT / "V8-Additional-fMRI/21-mi-fmri-rigorous-mapping"

MI_ENGINE_DS002725 = SCIENCE_ROOT / "V-Reproduction/Musical_Intelligence_Outputs/neuroimaging/ds002725/per_frame"
MENDELSSOHN_NPZ = MI_ENGINE_DS002725 / "classical_p5_mendelssohn-variations-serieuses-op54-larrard.npz"

MI_FR = 44100.0 / 256.0  # 172.265625 Hz exact
TR = 2.0
N_TRS_TARGET = 80
REGION_NAMES = [
    "A1_HG", "STG", "STS", "IFG", "dlPFC", "vmPFC", "OFC", "ACC", "SMA", "PMC",
    "AG", "TP", "VTA", "NAcc", "caudate", "amygdala", "hippocampus", "putamen",
    "MGB", "hypothalamus", "insula",
    "IC", "AN", "CN", "SOC", "PAG",
]


def spm_canonical_hrf(tr_native_s: float, time_length_s: float = 32.0) -> np.ndarray:
    """SPM canonical HRF (Glover 1999, Friston 1998 dual-gamma).

    a1=6, a2=16, b1=1, b2=1, c=1/6.
    """
    t = np.arange(0, time_length_s + tr_native_s, tr_native_s, dtype=np.float64)
    a1, a2, b1, b2, c = 6.0, 16.0, 1.0, 1.0, 1.0 / 6.0
    # Gamma PDFs
    from math import gamma as math_gamma

    def gpdf(t, a, b):
        out = np.zeros_like(t)
        mask = t > 0
        out[mask] = (b ** a) / math_gamma(a) * np.power(t[mask], a - 1) * np.exp(-b * t[mask])
        return out

    hrf = gpdf(t, a1, b1) - c * gpdf(t, a2, b2)
    hrf = hrf / np.abs(hrf).sum()  # normalise
    return hrf.astype(np.float32)


def main():
    t_start = time.time()
    data_dir = PHASE21_ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    log_path = PHASE21_ROOT / "results" / "_logs" / "stage2.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_fp = open(log_path, "a")
    def log(msg=""):
        print(msg)
        log_fp.write(msg + "\n")
        log_fp.flush()

    log(f"\n=== Stage 2 MI features (Mendelssohn window) @ {datetime.utcnow().isoformat()}Z ===")
    log(f"  source: {MENDELSSOHN_NPZ.name}")
    log(f"  MI_FR  = {MI_FR} Hz (exact 44100/256)")
    log(f"  TR     = {TR} s")
    log(f"  target = {N_TRS_TARGET} TRs")

    # Load Mendelssohn MI engine output
    d = np.load(MENDELSSOHN_NPZ)
    if "ram" not in d.files:
        log(f"  ERROR: no 'ram' key in {MENDELSSOHN_NPZ.name}")
        sys.exit(1)
    ram = d["ram"].astype(np.float64)  # (T_native, 26)
    log(f"  RAM shape: {ram.shape}, native duration: {ram.shape[0] / MI_FR:.2f}s")

    # Step 1: HRF convolve at native rate (per region, independently)
    log(f"\n  Step 1: HRF convolution @ {MI_FR:.3f} Hz...")
    hrf_dt = 1.0 / MI_FR
    hrf = spm_canonical_hrf(hrf_dt, time_length_s=32.0)
    log(f"    HRF kernel length: {len(hrf)} samples ({len(hrf) / MI_FR:.2f}s)")
    ram_conv = np.zeros_like(ram)
    for r in range(ram.shape[1]):
        x = ram[:, r]
        c = fftconvolve(x, hrf, mode="full")[:len(x)]
        ram_conv[:, r] = c
    log(f"    convolved shape: {ram_conv.shape}")

    # Step 2: Anti-alias Butterworth LPF (zero-phase)
    log(f"\n  Step 2: Butterworth LPF (order 4, cutoff = 0.4/TR = {0.4 / TR:.4f} Hz)...")
    cutoff = 0.4 / TR  # Hz
    nyq = 0.5 * MI_FR
    b, a = butter(4, cutoff / nyq, btype="low")
    ram_lpf = np.zeros_like(ram_conv)
    for r in range(ram_conv.shape[1]):
        ram_lpf[:, r] = filtfilt(b, a, ram_conv[:, r])
    log(f"    LPF shape: {ram_lpf.shape}")

    # Step 3: Resample to TR grid via interpolation
    log(f"\n  Step 3: Resample to TR={TR}s grid ({N_TRS_TARGET} target frames)...")
    t_native = np.arange(ram.shape[0]) / MI_FR
    # Place TR samples at TR/2 + k*TR (centre of TR window)
    t_tr = TR / 2 + np.arange(N_TRS_TARGET) * TR
    if t_tr[-1] > t_native[-1]:
        log(f"    WARN: last TR sample at {t_tr[-1]:.2f}s exceeds native span {t_native[-1]:.2f}s")
    mi_tr = np.zeros((N_TRS_TARGET, ram.shape[1]), dtype=np.float64)
    for r in range(ram.shape[1]):
        mi_tr[:, r] = np.interp(t_tr, t_native, ram_lpf[:, r])
    log(f"    resampled shape: {mi_tr.shape}")

    # Step 4: N1 z-score per region
    log(f"\n  Step 4: N1 within-region temporal z-score...")
    mi_n1 = np.zeros_like(mi_tr)
    for r in range(mi_tr.shape[1]):
        x = mi_tr[:, r]
        m = x.mean()
        s = x.std()
        if s < 1e-9:
            log(f"    WARN: region {REGION_NAMES[r]} (idx {r}) has zero variance after pipeline; setting zero")
            mi_n1[:, r] = 0.0
        else:
            mi_n1[:, r] = (x - m) / s

    # Per-region sanity summary
    log(f"\n  Per-region pipeline summary (after N1):")
    log(f"  {'idx':>4} {'name':<14} {'min':>8} {'max':>8} {'range':>8} {'std':>8}")
    for r in range(ram.shape[1]):
        x = mi_n1[:, r]
        log(f"  {r:>4} {REGION_NAMES[r]:<14} {x.min():+8.3f} {x.max():+8.3f} {(x.max() - x.min()):>8.3f} {x.std():>8.3f}")

    # Save
    out_path = data_dir / "stage2_mi_mendelssohn.npz"
    np.savez(out_path,
             mi_feat=mi_n1.astype(np.float32),
             region_names=np.array(REGION_NAMES),
             mi_fr_hz=np.array([MI_FR]),
             tr_s=np.array([TR]),
             source_npz=np.array([str(MENDELSSOHN_NPZ.name)]),
             meta=np.array([json.dumps({
                 "engine_sha_pin": "318eb2f529d7103e8b7d80b01228357fdc4e0217",
                 "pre_reg_version": "v1.4",
                 "n_trs": N_TRS_TARGET,
                 "tr_s": TR,
                 "mi_fr_hz": MI_FR,
                 "hrf": "SPM canonical (dual-gamma a1=6, a2=16, b1=b2=1, c=1/6)",
                 "lpf": "Butterworth order 4 zero-phase, cutoff = 0.4/TR Hz",
                 "normalization": "N1 within-region temporal z-score",
                 "source_npz": MENDELSSOHN_NPZ.name,
                 "native_frames": int(ram.shape[0]),
                 "native_duration_s": float(ram.shape[0] / MI_FR),
                 "wallclock_s": time.time() - t_start,
             })]),
    )
    log(f"\n  wrote: {out_path}")
    log(f"  wallclock: {time.time() - t_start:.1f}s")
    log_fp.close()


if __name__ == "__main__":
    main()
