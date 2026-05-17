"""V-Reproduction engine path resolver.

Audit-grade self-contained-first resolution: prefers the vendored engine
snapshot at `V-Reproduction/engine/Musical_Intelligence/` (HEAD `318eb2f5`)
and falls back to the parent-checkout `Science/Musical_Intelligence/` if
the vendored copy is absent (dev-mode use).

Usage from any phase script:

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_infra"))
    import _engine_path  # noqa: F401  (side-effect: extends sys.path)

After import, `from Musical_Intelligence.ear.r3 import ...` works.
"""
from __future__ import annotations

import sys
from pathlib import Path

# This file: V-Reproduction/_infra/_engine_path.py
_VREPRO_ROOT = Path(__file__).resolve().parents[1]
_VENDORED_PARENT = _VREPRO_ROOT / "engine"          # vendored flat snapshot
_PARENT_SCIENCE = _VREPRO_ROOT.parent               # Science/ checkout

if (_VENDORED_PARENT / "Musical_Intelligence").is_dir():
    ENGINE_PARENT = _VENDORED_PARENT
    ENGINE_SOURCE = "vendored (HEAD 318eb2f5)"
elif (_PARENT_SCIENCE / "Musical_Intelligence").is_dir():
    ENGINE_PARENT = _PARENT_SCIENCE
    ENGINE_SOURCE = "parent-checkout"
else:
    raise RuntimeError(
        f"V-Reproduction engine not found. Expected one of:\n"
        f"  {_VENDORED_PARENT}/Musical_Intelligence (vendored)\n"
        f"  {_PARENT_SCIENCE}/Musical_Intelligence (parent fallback)"
    )

if str(ENGINE_PARENT) not in sys.path:
    sys.path.insert(0, str(ENGINE_PARENT))
