#!/usr/bin/env python3
"""
build_features.py — prepare per-clip feature matrices for ds003720 encoding.

Inputs (via 01_mi_features/ and cycle-17 mert_features.npy):
  - MI RAM 26D full:  full_none/ram_mean.npy          (720, 26)
  - MI RAM naive 26D: full_naive/ram_mean.npy          (720, 26)
  - MERT 768D:         cycle-17-ds003720/mert_features.npy  (720, 768)
  - Clip order:        full_none/meta.json → clips[].id

Outputs (to ds003720/05_features/):
  - mi_ram_26d.npy       (720, 26)
  - mi_naive_26d.npy     (720, 26)
  - mert_768d.npy        (720, 768)
  - random_26d.npy       (seed 20260424)
  - random_768d.npy      (seed 20260424)
  - clip_order.json      (canonical 720 clip ids)
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np

SEED = 20260424
BASE = Path("<PAPER_TIME_SCIENCE_ROOT>/Science/Bold-fMRI")
DS = BASE / "ds003720"
FEAT_OUT = DS / "05_features"
FEAT_OUT.mkdir(parents=True, exist_ok=True)

CYC = BASE / "cycle-17-ds003720"
MI_FULL = CYC / "mi_ram" / "full_none"
MI_NAIVE = CYC / "mi_ram" / "full_naive"
MERT_PATH = CYC / "mert_features.npy"


def main():
    print("[features] loading MI RAM full_none", flush=True)
    mi_full = np.load(MI_FULL / "ram_mean.npy").astype(np.float32)
    print(f"  mi_ram_26d shape={mi_full.shape}")
    np.save(FEAT_OUT / "mi_ram_26d.npy", mi_full)

    print("[features] loading MI RAM naive", flush=True)
    mi_naive = np.load(MI_NAIVE / "ram_mean.npy").astype(np.float32)
    print(f"  mi_naive_26d shape={mi_naive.shape}")
    np.save(FEAT_OUT / "mi_naive_26d.npy", mi_naive)

    print("[features] loading MERT 768D", flush=True)
    mert = np.load(MERT_PATH).astype(np.float32)
    print(f"  mert_768d shape={mert.shape}")
    np.save(FEAT_OUT / "mert_768d.npy", mert)

    print("[features] generating random_26d / random_768d (seed 20260424)", flush=True)
    rng = np.random.default_rng(SEED)
    rand26 = rng.standard_normal((720, 26)).astype(np.float32)
    rand768 = rng.standard_normal((720, 768)).astype(np.float32)
    np.save(FEAT_OUT / "random_26d.npy", rand26)
    np.save(FEAT_OUT / "random_768d.npy", rand768)
    print(f"  random_26d shape={rand26.shape}")
    print(f"  random_768d shape={rand768.shape}")

    print("[features] saving clip_order.json", flush=True)
    meta = json.loads((MI_FULL / "meta.json").read_text())
    order = [c["id"] for c in meta["clips"]]
    assert len(order) == 720
    (FEAT_OUT / "clip_order.json").write_text(json.dumps(order, indent=2))
    print(f"  {len(order)} clips, first={order[0]!r} last={order[-1]!r}")

    print("[features] DONE", flush=True)


if __name__ == "__main__":
    main()
