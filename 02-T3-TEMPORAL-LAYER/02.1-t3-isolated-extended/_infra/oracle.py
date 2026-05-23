"""T³ Oracle cache — engine-free reproduction substrate.

Two modes selected by ``MI_BUILD_ORACLE`` env var:

* **BUILD mode** (``MI_BUILD_ORACLE=1``): live H3Extractor wrapped to
  record every ``(r3_features, demand) → H3Output`` triple encountered
  by the test suite. On session end, the recorded entries are pickled to
  ``engine_outputs/_unit_test_oracles/t3_isolated.pkl``.
  Requires the engine source.

* **CACHE mode** (default — reviewer mode): loads the same cache file
  from ``engine_outputs/`` and serves lookups keyed by a stable hash of
  the (r3_features bytes, sorted-demand-tuple). No engine source needed.

The cache lives under ``engine_outputs/`` per the bundle's pre-compute
convention. The MI_Results root is located by walking up from this file
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
from typing import Any, Dict, Iterable, Optional

import torch


class _SerializedDataclass(dict):
    """Marker subclass of dict — rehydrated as SimpleNamespace on lookup."""
    pass


def _to_portable(obj: Any) -> Any:
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
    return obj


def _from_portable(obj: Any) -> Any:
    if isinstance(obj, _SerializedDataclass):
        return SimpleNamespace(**{k: _from_portable(v) for k, v in obj.items()})
    if isinstance(obj, dict):
        return {k: _from_portable(v) for k, v in obj.items()}
    if isinstance(obj, tuple):
        return tuple(_from_portable(x) for x in obj)
    if isinstance(obj, list):
        return [_from_portable(x) for x in obj]
    return obj


_HERE = Path(__file__).resolve().parent


def _find_mi_results_root() -> Path:
    p = _HERE
    for _ in range(8):
        if (p / "engine_outputs").is_dir() and (p / "_infra").is_dir():
            return p
        p = p.parent
    raise RuntimeError(f"Could not locate MI_Results root from {_HERE}")


_MI_RESULTS_ROOT = _find_mi_results_root()
ORACLE_PATH = _MI_RESULTS_ROOT / "engine_outputs" / "_unit_test_oracles" / "t3_isolated.pkl"
BUILD_MODE = os.environ.get("MI_BUILD_ORACLE") == "1"


def _hash_demand(demand: Iterable) -> str:
    """Stable hash of a demand set/iterable (order-independent)."""
    items = sorted(repr(d) for d in demand)
    return hashlib.sha256("\n".join(items).encode("utf-8")).hexdigest()


def call_hash(r3_features: torch.Tensor, demand: Iterable) -> str:
    """Stable SHA-256 of (r3_features bytes, demand)."""
    arr = r3_features.detach().cpu().contiguous().numpy()
    h_feat = hashlib.sha256(arr.tobytes()).hexdigest()
    h_dem = _hash_demand(demand)
    return hashlib.sha256(f"{h_feat}|{h_dem}".encode("utf-8")).hexdigest()


class Oracle:
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

    def lookup(self, r3_features: torch.Tensor, demand: Iterable) -> Any:
        h = call_hash(r3_features, demand)
        if h not in self.cache:
            raise KeyError(
                f"T³ oracle miss for call_hash={h[:16]}… — "
                f"rebuild with `MI_BUILD_ORACLE=1 pytest …` "
                f"(cache contains {len(self.cache)} entries)"
            )
        return _from_portable(self.cache[h])

    def record(self, r3_features: torch.Tensor, demand: Iterable, output: Any) -> None:
        h = call_hash(r3_features, demand)
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
