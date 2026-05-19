"""V-Reproduction paper-time capture path resolver.

Phase scripts read paper-time outputs (V1/V2/V3/V4/V5/V6/Bold-fMRI captures
and small redistributable consonance CSVs). For audit-grade self-contained
operation, V-Reproduction vendors these under
`datasets/paper-anchors/` and `datasets/consonance/`.

This module provides one helper, `science(*parts)`, that resolves a path
under the parent Science/ tree but prefers the vendored copy if present.

Usage from any phase script:

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_infra"))
    from _capture_path import science  # noqa: E402

    GT_0006 = science("V2", "results", "GT-0006", "test_registry.csv")
    EEROLA  = science("datasets", "consonance", "eerola2021_exp3.csv")

`science()` returns the vendored path if it exists, else the parent
Science/ checkout path. Phase scripts work in both modes (vendored
self-contained mode AND parent-checkout dev mode).
"""
from __future__ import annotations

from pathlib import Path

# This file: _infra/_capture_path.py
_VREPRO_ROOT = Path(__file__).resolve().parents[1]
_PARENT_SCIENCE = _VREPRO_ROOT.parent
_VENDORED_CAPTURE = _VREPRO_ROOT / "datasets" / "paper-anchors"
_VENDORED_DATASETS = _VREPRO_ROOT / "datasets"


def science(*parts: str) -> Path:
    """Resolve a paper-time path: vendored first, parent Science fallback.

    Vendored layout:
      - V1/V2/V3/V4/V5/V6/Bold-fMRI -> datasets/paper-anchors/<X>/
      - datasets/consonance/*       -> datasets/consonance/* (already at root)
      - datasets/emotion/*          -> datasets/emotion/*
    """
    if not parts:
        return _PARENT_SCIENCE

    head = parts[0]
    rel = Path(*parts)

    # V1-V6, Bold-fMRI live under paper-anchors/
    if head in ("V1", "V2", "V3", "V4", "V5", "V6", "V7", "Bold-fMRI"):
        vendored = _VENDORED_CAPTURE / rel
    elif head == "datasets":
        # datasets/* live at V-Repro/datasets/* (no paper-anchors prefix)
        vendored = _VREPRO_ROOT / rel
    else:
        # Anything else (e.g. Musical_Intelligence): defer to parent
        return _PARENT_SCIENCE / rel

    if vendored.exists():
        return vendored
    return _PARENT_SCIENCE / rel
