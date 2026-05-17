"""L2.2 — No listener model (Rule 2) probe.

Rule 2 (paper §Boundary doctrine):

    The feature does not require modelling the listener's expectations,
    memory, or prior experience. It describes the signal, not the
    listener's response to the signal.

The strong form of Rule 2 is: **R³'s output is a deterministic function
of (mel, audio, sr) — and nothing else**. There is no `user`, `culture`,
`prior_history`, `expectation_model` parameter that the engine could
consume. We verify this:

(a) by AST audit of the public interface — no listener-side parameter
    appears anywhere in `R3Extractor.extract` or any group's
    `compute()` / `compute_from_audio()` / `compute_with_deps()`
    signature;
(b) by behavioural probe — sweeping environment variables that some
    psycho/cognitive libraries do consume (LANG, LOCALE, USERNAME) leaves
    R³ output bit-identical.
"""
from __future__ import annotations

import inspect
import os
import re
import sys

import numpy as np
import pytest
import torch


# ---------------------------------------------------------------------------
# (a) AST / signature audit
# ---------------------------------------------------------------------------

def test_extract_signature_has_no_listener_params(r3):
    """`R3Extractor.extract` has only (mel, audio, sr) parameters — no listener proxies."""
    sig = inspect.signature(r3.extract)
    names = list(sig.parameters.keys())
    allowed = {"self", "mel", "audio", "sr"}
    forbidden_substrings = (
        "listener", "user", "culture", "prior", "expectation",
        "history", "memory", "context", "session", "subject", "personality",
    )
    for n in names:
        if n in allowed:
            continue
        nlow = n.lower()
        for fs in forbidden_substrings:
            assert fs not in nlow, (
                f"R3Extractor.extract has a listener-proxy parameter '{n}' "
                f"matching '{fs}' — Rule 2 violation"
            )


def test_no_group_method_has_listener_params(r3):
    """No discovered group's compute methods have listener-proxy parameters."""
    forbidden_substrings = (
        "listener", "user", "culture", "prior", "expectation",
        "history", "memory", "context", "session", "subject", "personality",
    )
    for group in r3._groups:
        for method_name in ("compute", "compute_from_audio", "compute_with_deps"):
            if not hasattr(group, method_name):
                continue
            method = getattr(group, method_name)
            sig = inspect.signature(method)
            for param_name in sig.parameters:
                if param_name in ("self", "mel", "audio", "sr", "deps"):
                    continue
                low = param_name.lower()
                for fs in forbidden_substrings:
                    assert fs not in low, (
                        f"{type(group).__name__}.{method_name} has parameter "
                        f"'{param_name}' matching '{fs}' — Rule 2 violation"
                    )


def test_no_group_attribute_holds_listener_state(r3):
    """No discovered group has an instance attribute that looks like
    listener state. Allow attributes from BaseSpectralGroup / engine
    infrastructure (cached matrices, group metadata, etc.); the audit
    targets *new* engine attributes that drift toward listener-modelling."""
    forbidden_substrings = (
        "listener", "user_id", "culture", "prior_belief",
        "expectation_history", "session", "personality",
    )
    for group in r3._groups:
        for attr in dir(group):
            if attr.startswith("_"):
                continue
            attr_low = attr.lower()
            for fs in forbidden_substrings:
                assert fs not in attr_low, (
                    f"{type(group).__name__} has attribute '{attr}' matching "
                    f"'{fs}' — Rule 2 violation"
                )


# ---------------------------------------------------------------------------
# (b) Behavioural probe — environment variables that listener-aware libs
#     sometimes consume must NOT change R³ output
# ---------------------------------------------------------------------------

LISTENER_ENV_VARS = {
    "LANG":     "tr_TR.UTF-8",   # locale change
    "LC_ALL":   "tr_TR.UTF-8",
    "USER":     "audit_listener",
    "USERNAME": "audit_listener",
    "TZ":       "Asia/Istanbul",
}


def test_listener_env_vars_do_not_change_output(r3, stim, mel_of):
    """Sweeping LANG/LC_ALL/USER/USERNAME/TZ env vars must leave R³ output
    bit-identical. R³ contains no env-aware code path; this probe pins the
    invariant against any future drift toward listener-aware behavior."""
    audio = stim.stim_mix(duration_s=2.0)
    mel = mel_of(audio)

    with torch.no_grad():
        baseline = r3.extract(mel, audio=audio, sr=44100).features.cpu().numpy()

    saved = {k: os.environ.get(k) for k in LISTENER_ENV_VARS}
    try:
        for k, v in LISTENER_ENV_VARS.items():
            os.environ[k] = v
        with torch.no_grad():
            permuted = r3.extract(mel, audio=audio, sr=44100).features.cpu().numpy()
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    assert np.array_equal(baseline, permuted), (
        f"Engine output changed under listener-env-var sweep — Rule 2 violation. "
        f"Max |Δ| = {float(np.max(np.abs(baseline - permuted))):.6e}"
    )
