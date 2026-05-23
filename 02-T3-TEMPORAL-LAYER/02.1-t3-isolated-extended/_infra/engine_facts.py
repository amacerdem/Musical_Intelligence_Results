"""T³ engine-facts manifest + sys.modules stub installer.

Mirror of R³'s engine_facts.py adapted for T³'s smaller surface:
``Musical_Intelligence.ear.h3.{H3Extractor, attention.kernel.AttentionKernel,
constants.horizons.HORIZON_FRAMES}``.

BUILD mode (``MI_BUILD_ORACLE=1``) imports live engine + records facts; saves
to ``engine_outputs/_unit_test_oracles/t3_engine_facts.pkl``.
CACHE mode loads the pickle and injects sys.modules stubs.
"""
from __future__ import annotations

import functools
import importlib
import inspect
import os
import pickle
from dataclasses import fields, is_dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Tuple

import torch

_HERE = Path(__file__).resolve().parent


def _find_mi_results_root() -> Path:
    p = _HERE
    for _ in range(8):
        if (p / "engine_outputs").is_dir() and (p / "_infra").is_dir():
            return p
        p = p.parent
    raise RuntimeError(f"Could not locate MI_Results root from {_HERE}")


_MI_RESULTS_ROOT = _find_mi_results_root()
FACTS_PATH = _MI_RESULTS_ROOT / "engine_outputs" / "_unit_test_oracles" / "t3_engine_facts.pkl"
BUILD_MODE = os.environ.get("MI_BUILD_ORACLE") == "1"


SURFACE: list = [
    # constants.horizons
    ('Musical_Intelligence.ear.h3.constants.horizons', 'N_HORIZONS', 'value'),
    ('Musical_Intelligence.ear.h3.constants.horizons', 'HORIZON_MS', 'value'),
    ('Musical_Intelligence.ear.h3.constants.horizons', 'HORIZON_FRAMES', 'value'),
    ('Musical_Intelligence.ear.h3.constants.horizons', 'FRAME_RATE', 'value'),
    # constants.morphs
    ('Musical_Intelligence.ear.h3.constants.morphs', 'N_MORPHS', 'value'),
    ('Musical_Intelligence.ear.h3.constants.morphs', 'MORPH_NAMES', 'value'),
    ('Musical_Intelligence.ear.h3.constants.morphs', 'SIGNED_MORPHS', 'value'),
    # constants.laws
    ('Musical_Intelligence.ear.h3.constants.laws', 'N_LAWS', 'value'),
    ('Musical_Intelligence.ear.h3.constants.laws', 'LAW_NAMES', 'value'),
    ('Musical_Intelligence.ear.h3.constants.laws', 'ATTENTION_DECAY', 'value'),
    # attention.kernel
    ('Musical_Intelligence.ear.h3.attention.kernel', 'AttentionKernel', 'class'),
    # extractor + output
    ('Musical_Intelligence.ear.h3', 'H3Extractor', 'class'),
    ('Musical_Intelligence.ear.h3', 'H3Output', 'class'),
]


_VALUES: Dict[Tuple[str, str], Any] = {}
_CALLS: Dict[Tuple[str, str, str], Any] = {}
_CLASS_META: Dict[Tuple[str, str], Dict[str, Any]] = {}
_SCAN_RESULTS: Dict[str, Any] = {}
_CACHED_SCANS: Dict[str, Any] = {}


def _capture_class_meta(cls: type) -> Dict[str, Any]:
    meta: Dict[str, Any] = {
        "name": cls.__name__,
        "qualname": cls.__qualname__,
        "module": cls.__module__,
        "is_dataclass": is_dataclass(cls),
    }
    if is_dataclass(cls):
        meta["dataclass_fields"] = tuple(f.name for f in fields(cls))
        meta["dataclass_frozen"] = getattr(cls.__dataclass_params__, "frozen", False)
    # Capture .extract signature if present (H3Extractor)
    if hasattr(cls, "extract") and callable(getattr(cls, "extract")):
        try:
            sig = inspect.signature(cls.extract)
            meta["extract_signature"] = {
                name: {
                    "kind": p.kind.name,
                    "default": p.default if p.default is not inspect.Parameter.empty else "<empty>",
                }
                for name, p in sig.parameters.items()
                if name != "self"
            }
        except (TypeError, ValueError):
            pass
    return meta


def setup_recording() -> int:
    n = 0
    for modpath, attr, kind in SURFACE:
        try:
            mod = importlib.import_module(modpath)
        except ImportError as exc:
            print(f"[t3_engine_facts] WARN: cannot import {modpath}: {exc}")
            continue
        if not hasattr(mod, attr):
            print(f"[t3_engine_facts] WARN: {modpath} has no attr {attr}")
            continue
        target = getattr(mod, attr)
        if kind == "value":
            _VALUES[(modpath, attr)] = target
            n += 1
        elif kind == "class":
            _CLASS_META[(modpath, attr)] = _capture_class_meta(target)
            n += 1
    return n


def save_facts() -> int:
    facts = {
        "values": _VALUES,
        "calls": _CALLS,
        "class_meta": _CLASS_META,
        "scans": _SCAN_RESULTS,
    }
    FACTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(FACTS_PATH, "wb") as f:
        pickle.dump(facts, f)
    n = len(_VALUES) + len(_CALLS) + len(_CLASS_META) + len(_SCAN_RESULTS)
    print(f"[t3_engine_facts] BUILD saved {len(_VALUES)} values / "
          f"{len(_CALLS)} calls / {len(_CLASS_META)} class_metas / "
          f"{len(_SCAN_RESULTS)} scans → {FACTS_PATH}")
    return n


def install_stubs() -> int:
    if not FACTS_PATH.exists():
        return 0
    with open(FACTS_PATH, "rb") as f:
        facts = pickle.load(f)
    global _CACHED_SCANS
    _CACHED_SCANS = facts.get("scans", {})

    modpaths_needed = set()
    for (mp, _) in facts.get("values", {}):
        modpaths_needed.add(mp)
    for (mp, _) in facts.get("class_meta", {}):
        modpaths_needed.add(mp)

    all_paths = set()
    for mp in modpaths_needed:
        parts = mp.split(".")
        for i in range(1, len(parts) + 1):
            all_paths.add(".".join(parts[:i]))

    import sys
    for path in sorted(all_paths, key=lambda p: p.count(".")):
        if path in sys.modules:
            continue
        mod = ModuleType(path)
        sys.modules[path] = mod
        if "." in path:
            parent, child = path.rsplit(".", 1)
            if parent in sys.modules:
                setattr(sys.modules[parent], child, mod)

    for (mp, attr), value in facts.get("values", {}).items():
        setattr(sys.modules[mp], attr, value)

    for (mp, attr), meta in facts.get("class_meta", {}).items():
        class_stub = _make_class_stub(meta)
        setattr(sys.modules[mp], attr, class_stub)
        if attr == "H3Output":
            try:
                from _infra import oracle as _oracle
                if hasattr(_oracle, "register_r3output_stub"):
                    _oracle.register_r3output_stub(class_stub)
            except ImportError:
                pass

    return len(all_paths)


def _make_class_stub(meta: Dict[str, Any]) -> type:
    name = meta["name"]
    attrs: Dict[str, Any] = {"__qualname__": meta.get("qualname", name)}

    if meta.get("is_dataclass"):
        from dataclasses import make_dataclass
        field_names = list(meta["dataclass_fields"])
        return make_dataclass(
            name,
            [(fn, Any, None) for fn in field_names],
            frozen=meta.get("dataclass_frozen", False),
        )

    # H3Extractor: oracle-backed extract(r3_features, demand)
    if name == "H3Extractor":
        def _extract_oracle(self, r3_features, demand):
            from _infra.oracle import Oracle
            return Oracle.instance().lookup(r3_features, demand)
        attrs["extract"] = _extract_oracle

    return type(name, (), attrs)


def perform_or_recall_scan(scan_name: str, scan_fn):
    if BUILD_MODE:
        result = scan_fn()
        _SCAN_RESULTS[scan_name] = result
        return result
    if scan_name in _CACHED_SCANS:
        return _CACHED_SCANS[scan_name]
    raise KeyError(
        f"t3_engine_facts: scan '{scan_name}' not in manifest — "
        f"rebuild with `MI_BUILD_ORACLE=1 pytest`"
    )


def cached_pass(scan_name: str):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if BUILD_MODE:
                try:
                    fn(*args, **kwargs)
                    _SCAN_RESULTS[scan_name] = {"passed": True, "msg": None}
                except AssertionError as e:
                    _SCAN_RESULTS[scan_name] = {"passed": False, "msg": str(e)}
                    raise
                return
            r = _CACHED_SCANS.get(scan_name)
            if r is None:
                raise KeyError(
                    f"cached_pass: '{scan_name}' not in manifest — rebuild"
                )
            assert r.get("passed"), (
                f"cached_pass '{scan_name}' failed at build: {r.get('msg')}"
            )
        return wrapper
    return decorator
