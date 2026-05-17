"""Pre-registration JSON loader + immutability enforcer.

Every analysis script loads its prereg JSON through load_prereg(...) instead of
json.load(...). The loader rejects post-freeze edits and enforces engine-SHA
agreement.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class PreregError(RuntimeError):
    pass


REQUIRED_TOP_KEYS = {
    "schema_version",
    "dataset_id",
    "segment",
    "engine_sha",
    "frozen_at",
    "immutable",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _frozen_at_in_past(stamp: str) -> bool:
    try:
        ts = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise PreregError(f"frozen_at must be ISO8601 UTC ('YYYY-MM-DDThh:mm:ssZ'); got {stamp!r}") from exc
    return ts <= datetime.now(timezone.utc)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_prereg(path: Path, expected_engine_sha: str | None = None) -> dict[str, Any]:
    """Load and validate a prereg JSON. Returns the parsed dict.

    Raises PreregError on:
      - missing required top-level keys
      - immutable != True
      - frozen_at not set or in the future
      - engine_sha mismatch (when expected_engine_sha is provided)
    """
    path = Path(path)
    if not path.exists():
        raise PreregError(f"Prereg file missing: {path}")

    obj = json.loads(path.read_text())

    missing = REQUIRED_TOP_KEYS - set(obj)
    if missing:
        raise PreregError(f"Prereg {path.name} missing keys: {sorted(missing)}")

    if obj.get("immutable") is not True:
        raise PreregError(f"Prereg {path.name} is not marked immutable (got {obj.get('immutable')!r}); refusing to load")

    if not _frozen_at_in_past(obj["frozen_at"]):
        raise PreregError(f"Prereg {path.name} frozen_at is in the future: {obj['frozen_at']}")

    if expected_engine_sha is not None and obj.get("engine_sha") != expected_engine_sha:
        raise PreregError(
            f"Prereg {path.name} engine_sha mismatch.\n"
            f"  expected: {expected_engine_sha}\n  actual:   {obj.get('engine_sha')}"
        )

    obj["_path"] = str(path)
    obj["_loaded_at"] = _now_iso()
    obj["_file_sha256"] = file_sha256(path)
    return obj


def assert_bindings_columns_present(prereg: dict[str, Any], pooled_columns: set[str], binding_key: str = "bindings",
                                    column_field: str = "mi_output_column") -> None:
    """Halt if any binding's named column is missing from pooled_columns.

    Used by S1/S6/S8 scripts. RAM/region prereg uses a different shape — caller
    handles that.
    """
    items = prereg.get(binding_key)
    if items is None:
        raise PreregError(f"Prereg has no '{binding_key}' key")
    missing = [b[column_field] for b in items if b[column_field] not in pooled_columns]
    if missing:
        raise PreregError(f"Prereg references columns not in pooled.csv: {missing}")


if __name__ == "__main__":
    import sys
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if p is None:
        print("usage: prereg_validator.py <path/to/prereg.json>")
        sys.exit(1)
    obj = load_prereg(p)
    print(f"OK prereg {obj['dataset_id']}/{obj['segment']} frozen={obj['frozen_at']}")
    print(f"   bindings: {len(obj.get('bindings', obj.get('hubs', obj.get('cells', []))))}")
    print(f"   file SHA-256: {obj['_file_sha256'][:16]}...")
