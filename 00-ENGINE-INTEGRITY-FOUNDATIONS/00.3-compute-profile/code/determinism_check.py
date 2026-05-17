#!/usr/bin/env python3
"""V-Reproduction Phase 4 — Determinism re-check (C-COMPUTE-06).

Two consecutive `run_engine` calls on the same audio clip; MD5 hashes the
`r3` numpy array bytes. PASS iff hashes are identical (bit-identical, paper
bound |Δρ| ≤ 8.8×10⁻⁵ trivially satisfied).

This re-asserts the Phase 0 finding (R³+C³+RAM+neuro+beliefs all
bit-identical across 3 runs) at Phase 4 close time.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from pathlib import Path

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
LEGACY_AUDIO = REPO_ROOT / "Legacy" / "Test-Audio"


def main() -> int:
    clip = sorted(p for p in LEGACY_AUDIO.glob("*.wav"))[0]

    print(f"  determinism check: clip = {clip.name}")

    out1 = run_engine(clip, return_layers=("r3",), seed=SEED)
    out2 = run_engine(clip, return_layers=("r3",), seed=SEED)

    r3_1 = out1["r3"]
    r3_2 = out2["r3"]

    h1 = hashlib.md5(r3_1.tobytes()).hexdigest()
    h2 = hashlib.md5(r3_2.tobytes()).hexdigest()

    import numpy as np
    max_abs_diff = float(np.max(np.abs(r3_1 - r3_2)))

    bit_identical = h1 == h2

    print(f"  run1 MD5 = {h1}")
    print(f"  run2 MD5 = {h2}")
    print(f"  max-abs-diff = {max_abs_diff}")
    print(f"  verdict: {'PASS (bit-identical)' if bit_identical else 'FAIL'}")

    out_csv = PHASE_DIR / "results" / "determinism_check.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["clip", "run1_md5", "run2_md5", "max_abs_diff", "bit_identical"])
        w.writerow([clip.name, h1, h2, max_abs_diff, bit_identical])

    summary = {
        "clip": clip.name,
        "md5_run1": h1,
        "md5_run2": h2,
        "max_abs_diff": max_abs_diff,
        "bit_identical": bit_identical,
    }
    with open(PHASE_DIR / "results" / "_determinism_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    return 0 if bit_identical else 1


if __name__ == "__main__":
    sys.exit(main())
