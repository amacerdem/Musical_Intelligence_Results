"""SHA-256 helpers used by the pin-integrity gate.

Kept in a standalone module (not in conftest) so both conftest and
``test_pin_integrity.py`` can import ``aggregate_engine_sha`` without
depending on pytest collection order.
"""
from __future__ import annotations

import hashlib
from pathlib import Path


def aggregate_engine_sha(engine_root: Path | None = None) -> str:
    """Return the canonical engine aggregate SHA-256.

    Cache-only mode: reads the recorded SHA from engine_outputs/_aggregate_sha.txt
    (preferred) or _infra/manifests/engine_head.json. Engine source tree is
    NOT scanned — the cache + manifest are the load-bearing artefacts.

    The ``engine_root`` argument is accepted for backward compatibility but
    ignored; we read from the recorded value.
    """
    # Walk up to MI_Results root (contains engine_outputs/ and _infra/)
    here = Path(__file__).resolve()
    repo_root = None
    for parent in [here.parent, *here.parents]:
        if (parent / "engine_outputs").is_dir() and (parent / "_infra").is_dir():
            repo_root = parent
            break
    if repo_root is None:
        raise RuntimeError(f"Could not locate MI_Results from {here}")

    rec = repo_root / "engine_outputs" / "_aggregate_sha.txt"
    if rec.exists():
        return rec.read_text().strip()

    import json
    manifest = repo_root / "_infra" / "manifests" / "engine_head.json"
    return json.loads(manifest.read_text())["content_aggregate_sha256"]

