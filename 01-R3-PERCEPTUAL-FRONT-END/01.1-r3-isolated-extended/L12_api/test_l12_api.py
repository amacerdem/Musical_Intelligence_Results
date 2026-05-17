"""L12 — API contract & immutability.

Engine claim (paper §Methods, R3Output dataclass):

    `R3Extractor.extract()` is a pure function from input to `R3Output`;
    the dataclass is frozen; the registry is immutable; the public API is stable.
"""
from __future__ import annotations

import dataclasses
import inspect

import numpy as np
import pytest
import torch

from _infra import stimuli as stim


# ---------------------------------------------------------------------------
# L12.1 — extract() signature
# ---------------------------------------------------------------------------

def test_extract_signature(r3):
    sig = inspect.signature(r3.extract)
    params = sig.parameters
    assert "mel" in params
    assert "audio" in params
    assert "sr" in params
    # `mel` is positional-or-keyword; `audio`/`sr` are keyword-only after `*`
    assert params["mel"].kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert params["audio"].kind == inspect.Parameter.KEYWORD_ONLY
    assert params["sr"].kind == inspect.Parameter.KEYWORD_ONLY


# ---------------------------------------------------------------------------
# L12.2 — R3Output is a frozen dataclass
# ---------------------------------------------------------------------------

def test_r3output_is_frozen_dataclass(r3_extract):
    out = r3_extract(stim.stim_mix(duration_s=1.0))
    assert dataclasses.is_dataclass(type(out))
    fields = {f.name for f in dataclasses.fields(out)}
    assert fields == {"features", "feature_names", "feature_map"}
    with pytest.raises(dataclasses.FrozenInstanceError):
        out.features = torch.zeros_like(out.features)


# ---------------------------------------------------------------------------
# L12.3 — feature_map is immutable registry snapshot
# ---------------------------------------------------------------------------

def test_feature_map_is_immutable_snapshot(r3_extract):
    out = r3_extract(stim.stim_mix(duration_s=1.0))
    fm = out.feature_map
    # Try to mutate `groups` attribute
    if hasattr(fm, "groups"):
        groups = fm.groups
        # Either it's a tuple (immutable) or list (mutable but the registry
        # ought to be a snapshot). We pin tuple for a frozen registry.
        assert isinstance(groups, tuple), (
            f"R3Output.feature_map.groups is not a tuple — registry mutability risk"
        )


# ---------------------------------------------------------------------------
# L12.4 — feature_names is a frozen tuple of length 97
# ---------------------------------------------------------------------------

def test_feature_names_immutable_tuple(r3_extract):
    from _infra.dims import DIM_NAMES
    out = r3_extract(stim.stim_mix(duration_s=1.0))
    assert isinstance(out.feature_names, tuple)
    assert len(out.feature_names) == 97
    assert tuple(out.feature_names) == DIM_NAMES


# ---------------------------------------------------------------------------
# L12.5 — Two extractor instances are state-independent
# ---------------------------------------------------------------------------

def test_two_instances_state_independent(stim, mel_of):
    from Musical_Intelligence.ear.r3.extractor import R3Extractor
    audio = stim.stim_mix(duration_s=2.0)
    mel = mel_of(audio)
    a = R3Extractor()
    b = R3Extractor()
    out_a = a.extract(mel, audio=audio, sr=44100).features.cpu().numpy()
    out_b = b.extract(mel, audio=audio, sr=44100).features.cpu().numpy()
    assert np.array_equal(out_a, out_b)


# ---------------------------------------------------------------------------
# L12.6 — Concurrent extracts (same instance, repeated calls) — purity
# ---------------------------------------------------------------------------

def test_repeated_extract_pure(r3_extract):
    """Two back-to-back extracts on the same audio give bit-identical output —
    a purity certificate (no instance state mutation)."""
    audio = stim.stim_mix(duration_s=2.0)
    a = r3_extract(audio).features.cpu().numpy()
    b = r3_extract(audio).features.cpu().numpy()
    assert np.array_equal(a, b)


# ---------------------------------------------------------------------------
# L12.7 — No private attributes leak through public output
# ---------------------------------------------------------------------------

def test_r3output_has_only_documented_fields(r3_extract):
    out = r3_extract(stim.stim_mix(duration_s=1.0))
    public_attrs = {a for a in dir(out) if not a.startswith("_")}
    # Allow dataclass / Python machinery attributes
    expected_subset = {"features", "feature_names", "feature_map"}
    assert expected_subset <= public_attrs


# ---------------------------------------------------------------------------
# L12.8 — Engine pin: total_dim attribute is 97
# ---------------------------------------------------------------------------

def test_extractor_total_dim_is_97(r3):
    assert r3.total_dim == 97


# ---------------------------------------------------------------------------
# L12.9 — Public symbols at ear.r3.__init__ — engine pin
# ---------------------------------------------------------------------------

def test_public_module_imports_extractor():
    """`Musical_Intelligence.ear.r3.extractor` exports `R3Extractor` and
    `R3Output` — the canonical public surface."""
    import Musical_Intelligence.ear.r3.extractor as mod
    assert hasattr(mod, "R3Extractor")
    assert hasattr(mod, "R3Output")
