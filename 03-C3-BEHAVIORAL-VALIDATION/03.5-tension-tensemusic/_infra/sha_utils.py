"""SHA-256 helpers used by the pin-integrity gate.

Kept in a standalone module (not in conftest) so both conftest and
``test_pin_integrity.py`` can import ``aggregate_engine_sha`` without
depending on pytest collection order.
"""
from __future__ import annotations

import hashlib
from pathlib import Path


def aggregate_engine_sha(engine_root: Path) -> str:
    """SHA-256 of (sorted .py file SHAs) under *engine_root*, excluding __pycache__.

    Matches the manifest's documented ``content_aggregate_method`` exactly.
    """
    py_files = sorted(
        p for p in engine_root.rglob("*.py")
        if "__pycache__" not in p.parts
    )
    inner = hashlib.sha256()
    for p in py_files:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        inner.update(h.hexdigest().encode("ascii"))
        inner.update(b"\n")
    return inner.hexdigest()
