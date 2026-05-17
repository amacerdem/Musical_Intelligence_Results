#!/usr/bin/env python3
"""V-Reproduction Phase 4 — Memory peak measurement.

Single fresh Python process (this script) running a single `run_engine()`
call on a 30 s clip, then reads `resource.getrusage(RUSAGE_SELF).ru_maxrss`
and converts to MB using platform-correct convention (macOS: bytes;
Linux: kilobytes).

Output: `results/memory_peak.csv`.
"""
from __future__ import annotations

import csv
import json
import os
import resource
import sys
from pathlib import Path

# Pin BLAS threads BEFORE numpy/torch imports
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = Path(__file__).resolve().parent
PHASE_DIR = HERE.parent
VREPRO_ROOT = PHASE_DIR.parent
INFRA = VREPRO_ROOT / "_infra"
SCIENCE_ROOT = VREPRO_ROOT.parent
REPO_ROOT = SCIENCE_ROOT.parent

if str(INFRA) not in sys.path:
    sys.path.insert(0, str(INFRA))
import _engine_path  # noqa: E402,F401

from engine.runner import run_engine  # noqa: E402


SEED = 2026050604
LEGACY_AUDIO = SCIENCE_ROOT / "datasets" / "real-music"

# Use first WAV from Science/datasets/real-music (sorted) — same as benchmark.py run 1
def pick_clip() -> Path:
    legacy_wavs = sorted(p for p in LEGACY_AUDIO.glob("*.wav"))
    if not legacy_wavs:
        raise RuntimeError("no WAV in Science/datasets/real-music")
    return legacy_wavs[0]


def main() -> int:
    clip = pick_clip()
    print(f"  memory_peak: clip = {clip.name}")

    # Single fresh run
    out = run_engine(clip, return_layers=("r3","h3","c3","ram","neuro","beliefs"), seed=SEED)
    n_frames = out["r3"].shape[0]

    ru = resource.getrusage(resource.RUSAGE_SELF)
    raw = int(ru.ru_maxrss)
    if sys.platform == "darwin":
        # macOS: ru_maxrss is in bytes
        peak_mb = raw / (1024.0 * 1024.0)
        unit = "bytes"
    else:
        # Linux: ru_maxrss is in kilobytes
        peak_mb = raw / 1024.0
        unit = "kilobytes"

    print(f"  ru_maxrss = {raw} {unit} -> {peak_mb:.2f} MB")
    print(f"  T_frames  = {n_frames}")

    out_csv = PHASE_DIR / "results" / "memory_peak.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["platform", "ru_maxrss_raw", "raw_unit", "peak_mb", "n_frames", "clip"])
        w.writerow([sys.platform, raw, unit, round(peak_mb, 3), n_frames, clip.name])
    print(f"  wrote {out_csv}")

    # Summary for aggregator
    summary = {
        "peak_mb": round(peak_mb, 3),
        "platform": sys.platform,
        "raw": raw,
        "raw_unit": unit,
        "clip": clip.name,
        "n_frames": int(n_frames),
    }
    with open(PHASE_DIR / "results" / "_memory_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    return 0


if __name__ == "__main__":
    sys.exit(main())
