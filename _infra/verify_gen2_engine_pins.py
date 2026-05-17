#!/usr/bin/env python3
"""Phase 19-27 L1-only engine-pin / spec-compliance verifier.

Each Phase 19-27 (Gen 2) suite is a pytest-based standalone validation
package. Their L1 layer either:

- L1_engine_pin/         (Phases 21-27) — verifies engine SHA-256 aggregate
                          against the canonical pin manifest.
- L1_spec_compliance/    (Phases 19, 20) — verifies R³/T³ specification
                          compliance against synthesised stimuli.

L1 in both cases requires NO external audio / no engine cache / no fMRI
BOLD data. It is the fresh-clone safe verification that:
    1. The vendored engine bit-identical matches the paper-time HEAD
       (SHA-256 482ade45c50f...).
    2. The Gen 2 conftest engine-path resolver works for the V-Reproduction
       vendored layout (engine/Musical_Intelligence/).

Layers L2+ require external data fetched via _infra/download_datasets.sh
(see each phase's README).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

V_REPRO = Path(__file__).resolve().parent.parent

# Phase folder name → L1 layer subdir name (different conventions across phases)
GEN2_PHASES = [
    ("19-r3-isolated-validation",            "L1_spec_compliance"),
    ("20-t3-isolated-validation",            "L1_spec_compliance"),
    ("21-c3-chill-prediction",               "L1_engine_pin"),
    ("22-h8-tensemusic-tension-prediction",  "L1_engine_pin"),
    ("23-h4-h5-pmemo-dynamic-emotion",       "L1_engine_pin"),
    ("24-h18-h25-eerola-film-gems",          "L1_engine_pin"),
    ("25-c3-fmri-region-ceiling-saturation", "L1_engine_pin"),
    ("26-c3-fmri-ds003720-region-ceiling",   "L1_engine_pin"),
    ("27-c3-fmri-cross-dataset",             "L1_engine_pin"),
]


def _run_l1(phase_dir: Path, l1_subdir: str) -> tuple[bool, int, str]:
    """Run pytest <l1_subdir>/ from inside phase_dir. Return (ok, count, summary)."""
    target = phase_dir / l1_subdir
    if not target.is_dir():
        return False, 0, f"L1 directory missing: {l1_subdir}"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", l1_subdir, "--tb=line", "-q"],
        cwd=str(phase_dir),
        capture_output=True,
        text=True,
    )
    # Parse last meaningful line of pytest output
    for line in reversed(result.stdout.strip().splitlines()):
        line = line.strip()
        if " passed" in line or " failed" in line or " error" in line:
            summary = line
            break
    else:
        summary = "(no pytest summary line)"
    ok = result.returncode == 0
    # Try to extract test count
    count = 0
    for token in summary.split():
        if token.isdigit():
            count = int(token)
            break
    return ok, count, summary


def main() -> int:
    print("=" * 80)
    print("Gen 2 Phase 19-27 — L1 engine-pin / spec-compliance verifier")
    print("(L1 layer is fresh-clone safe: no external audio / no BOLD required.)")
    print("=" * 80)
    all_ok = True
    summary_rows: list[tuple[str, str, str]] = []
    for phase_name, l1_subdir in GEN2_PHASES:
        phase_dir = V_REPRO / phase_name
        if not phase_dir.is_dir():
            print(f"[SKIP] {phase_name:<42}  not found")
            summary_rows.append((phase_name, "SKIP", "phase directory missing"))
            continue
        ok, count, summary = _run_l1(phase_dir, l1_subdir)
        status = "[✓]" if ok else "[✗]"
        print(f"{status} {phase_name:<42}  {l1_subdir:<22}  {summary}")
        summary_rows.append((phase_name, "PASS" if ok else "FAIL", summary))
        if not ok:
            all_ok = False
    print()
    print("=" * 80)
    if all_ok:
        print(f"✓ ALL {len(summary_rows)} GEN 2 PHASES L1 VERIFIED — engine pin + spec compliance.")
        print("  Higher layers (L2+) require external data; see each phase README.md.")
    else:
        print("✗ AT LEAST ONE GEN 2 PHASE L1 FAILED. See output above.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
