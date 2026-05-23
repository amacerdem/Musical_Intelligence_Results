"""R³ Oracle cache — engine-free reproduction substrate.

Two modes selected by ``MI_BUILD_ORACLE`` env var:

* **BUILD mode** (``MI_BUILD_ORACLE=1``): live R3Extractor wrapped to
  record every ``(audio_tensor → R3Output)`` pair encountered by the
  test suite. On session end, the recorded pairs are pickled to
  ``engine_outputs/_unit_test_oracles/r3_isolated.pkl``. Requires
  the engine source.

* **CACHE mode** (default — reviewer mode): loads the same cache file
  from ``engine_outputs/`` and serves lookups keyed by SHA-256 of
  audio tensor bytes. No engine source needed.

The oracle is keyed by a SHA-256 of the audio tensor's raw bytes
(``audio.detach().cpu().contiguous().numpy().tobytes()``) — stable for
the deterministic stimulus library (all stimuli are seed-fixed or
analytic, see ``stimuli.py``).

The cache lives under ``engine_outputs/`` per the bundle's pre-compute
convention (same root as ``engine_outputs/emotion/TenseMusic/per_frame``
etc.). The MI_Results root is located by walking up from this file
until ``engine_outputs/`` + ``_infra/`` are both present.
"""
from __future__ import annotations

import atexit
import hashlib
import os
import pickle
from dataclasses import fields, is_dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Optional

import torch


class _SerializedDataclass(dict):
    """Marker subclass of dict. _from_portable() rehydrates these as
    SimpleNamespace; plain dicts stay dicts (preserves any genuine dict
    fields in R3Output / R3FeatureMap, e.g. ``feature_map.groups``).
    """
    pass


def _to_portable(obj: Any) -> Any:
    """Convert an arbitrary engine-output tree into a form that pickles
    without requiring the engine's classes to be importable on load."""
    if is_dataclass(obj) and not isinstance(obj, type):
        return _SerializedDataclass(
            (f.name, _to_portable(getattr(obj, f.name))) for f in fields(obj)
        )
    if isinstance(obj, dict):
        return {k: _to_portable(v) for k, v in obj.items()}
    if isinstance(obj, tuple):
        return tuple(_to_portable(x) for x in obj)
    if isinstance(obj, list):
        return [_to_portable(x) for x in obj]
    return obj  # torch.Tensor / numpy / str / int / float — pickle-portable


# Optional registry: engine_facts.install_stubs() can register the R3Output
# stub class here so cached lookups rehydrate as real dataclass instances
# (tests that check is_dataclass(type(out)) need this).
_R3OUTPUT_STUB: Optional[type] = None


def register_r3output_stub(cls: type) -> None:
    """engine_facts.install_stubs() calls this after creating R3Output stub."""
    global _R3OUTPUT_STUB
    _R3OUTPUT_STUB = cls


def _from_portable(obj: Any) -> Any:
    """Rehydrate a portable tree: dataclass-marker dicts → SimpleNamespace
    (or R3Output stub if registered), plain dicts/tuples/lists stay native."""
    if isinstance(obj, _SerializedDataclass):
        rehydrated = {k: _from_portable(v) for k, v in obj.items()}
        if (_R3OUTPUT_STUB is not None
                and set(rehydrated) == {"features", "feature_names", "feature_map"}):
            return _R3OUTPUT_STUB(**rehydrated)
        return SimpleNamespace(**rehydrated)
    if isinstance(obj, dict):
        return {k: _from_portable(v) for k, v in obj.items()}
    if isinstance(obj, tuple):
        return tuple(_from_portable(x) for x in obj)
    if isinstance(obj, list):
        return [_from_portable(x) for x in obj]
    return obj

_HERE = Path(__file__).resolve().parent


def _find_mi_results_root() -> Path:
    """Walk up until we find the MI_Results root (engine_outputs/ + _infra/)."""
    p = _HERE
    for _ in range(8):
        if (p / "engine_outputs").is_dir() and (p / "_infra").is_dir():
            return p
        p = p.parent
    raise RuntimeError(f"Could not locate MI_Results root from {_HERE}")


_MI_RESULTS_ROOT = _find_mi_results_root()
ORACLE_PATH = _MI_RESULTS_ROOT / "engine_outputs" / "_unit_test_oracles" / "r3_isolated.pkl"
BUILD_MODE = os.environ.get("MI_BUILD_ORACLE") == "1"


def tensor_hash(t: torch.Tensor) -> str:
    """Stable SHA-256 of any tensor's bytes."""
    arr = t.detach().cpu().contiguous().numpy()
    return hashlib.sha256(arr.tobytes()).hexdigest()


# Back-compat alias (audio is just one tensor kind)
audio_hash = tensor_hash


class Oracle:
    """Singleton oracle cache. Single backing file."""

    _instance: Optional["Oracle"] = None

    def __init__(self):
        self.cache: Dict[str, Any] = {}
        self.dirty = False
        if ORACLE_PATH.exists():
            with open(ORACLE_PATH, "rb") as f:
                self.cache = pickle.load(f)
        if BUILD_MODE:
            atexit.register(self.save)

    @classmethod
    def instance(cls) -> "Oracle":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def lookup(self, audio: torch.Tensor) -> Any:
        """Lookup by audio tensor hash (alias for lookup_tensor)."""
        return self.lookup_tensor(audio)

    def lookup_tensor(self, t: torch.Tensor) -> Any:
        """Lookup by any tensor's hash — supports audio or mel keys."""
        h = tensor_hash(t)
        if h not in self.cache:
            raise KeyError(
                f"Oracle miss for tensor_hash={h[:16]}… — "
                f"rebuild oracle with `MI_BUILD_ORACLE=1 pytest …` "
                f"(cache contains {len(self.cache)} entries)"
            )
        return _from_portable(self.cache[h])

    def record(self, audio: torch.Tensor, output: Any) -> None:
        """Record under audio key (alias for record_tensor)."""
        self.record_tensor(audio, output)

    def record_tensor(self, t: torch.Tensor, output: Any) -> None:
        h = tensor_hash(t)
        if h not in self.cache:
            self.cache[h] = _to_portable(output)
            self.dirty = True

    def save(self) -> int:
        if not self.dirty:
            return len(self.cache)
        ORACLE_PATH.parent.mkdir(exist_ok=True)
        with open(ORACLE_PATH, "wb") as f:
            pickle.dump(self.cache, f)
        self.dirty = False
        return len(self.cache)
