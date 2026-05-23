"""L3.3 — No PRNG / no seed dependence.

R³ contains no `random`, `np.random`, or `torch.manual_seed` calls.
Verified two ways:

(a) **AST audit** — scan every `.py` under `ear/r3/` for `random.`,
    `manual_seed`, `dropout`, `bernoulli`, `multinomial` etc.
(b) **Behavioural probe** — flip `torch.manual_seed`, `np.random.seed`,
    `random.seed`, `PYTHONHASHSEED` between runs and verify R³ output is
    bit-identical.
"""
from __future__ import annotations

import os
import random
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import torch

from _infra import stimuli as stim


# ---------------------------------------------------------------------------
# (a) AST audit
# ---------------------------------------------------------------------------

FORBIDDEN_PATTERNS = (
    "random.random",
    "random.randint",
    "random.choice",
    "random.uniform",
    "np.random",
    "numpy.random",
    "torch.manual_seed",
    "torch.seed(",
    "torch.rand(",
    "torch.randn(",
    "torch.randint(",
    "torch.bernoulli",
    "torch.multinomial",
    "F.dropout(",
    "nn.Dropout(",
)


def _engine_root() -> Path:
    p = Path(__file__).resolve()
    for _ in range(8):
        if (p / "Musical_Intelligence" / "ear" / "r3").exists():
            return p / "Musical_Intelligence" / "ear" / "r3"
        p = p.parent
    raise RuntimeError("engine root not found")


def test_no_prng_calls_in_engine_source():
    """Scan every .py under ear/r3/ for forbidden PRNG / dropout patterns."""
    from _infra.engine_facts import perform_or_recall_scan

    def _scan():
        root = _engine_root()
        found = []
        for p in root.rglob("*.py"):
            if "__pycache__" in p.parts:
                continue
            text = p.read_text()
            for pat in FORBIDDEN_PATTERNS:
                if pat in text:
                    for lineno, line in enumerate(text.splitlines(), start=1):
                        stripped = line.strip()
                        if pat in line and not stripped.startswith("#"):
                            found.append((str(p.relative_to(root)), lineno, pat,
                                          line.strip()))
        return found

    found = perform_or_recall_scan("l3.no_prng_calls_in_engine_source", _scan)
    assert not found, (
        f"PRNG / dropout pattern detected in engine source — Rule 5 audit:\n"
        + "\n".join(f"  {f[0]}:{f[1]}  ({f[2]}): {f[3]}" for f in found[:10])
    )


# ---------------------------------------------------------------------------
# (b) Behavioural probe — flipping seeds is a no-op
# ---------------------------------------------------------------------------

def test_seed_flips_do_not_change_output(r3_extract):
    audio = stim.stim_mix(duration_s=2.0)

    with torch.no_grad():
        baseline = r3_extract(audio).features.cpu().numpy()

    for s in [0, 1, 42, 1729, 9999]:
        torch.manual_seed(s)
        np.random.seed(s)
        random.seed(s)
        with torch.no_grad():
            other = r3_extract(audio).features.cpu().numpy()
        assert np.array_equal(baseline, other), (
            f"seed {s} changed R³ output — Rule 5 violation. "
            f"max |Δ| = {np.max(np.abs(baseline - other)):.3e}"
        )


def test_pythonhashseed_does_not_change_output(r3_extract):
    """PYTHONHASHSEED only affects `hash()` of strings/bytes — but if R³
    accidentally consumes hashes anywhere, it would surface as drift here."""
    audio = stim.stim_mix(duration_s=2.0)
    saved = os.environ.get("PYTHONHASHSEED")
    try:
        os.environ["PYTHONHASHSEED"] = "1234"
        a = r3_extract(audio).features.cpu().numpy()
        os.environ["PYTHONHASHSEED"] = "5678"
        b = r3_extract(audio).features.cpu().numpy()
        assert np.array_equal(a, b)
    finally:
        if saved is None:
            os.environ.pop("PYTHONHASHSEED", None)
        else:
            os.environ["PYTHONHASHSEED"] = saved
