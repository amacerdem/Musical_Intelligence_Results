"""L2.3 — Group isolation / no cross-domain binding (Rule 3).

Rule 3 (paper §Boundary doctrine):

    The feature operates within a single perceptual domain. It does not
    multiply, correlate, or combine features from different groups.

The strong form of Rule 3:

    Each group's `compute()` (or `compute_from_audio()`) consumes only its
    declared inputs (mel, audio, and — for Stage-2 groups — its declared
    `dependencies`). Replacing OTHER groups' input proxies must not change
    THIS group's output.

There are two kinds of test we can run:

(a) **Static contract** — each group's `DEPENDENCIES` tuple plus the
    extractor's auto-discovery wire-up enforce the binding statically.
    We audit these.

(b) **Dynamic probe** — for each Stage-2 group, replace the *non-declared*
    Stage-1 outputs in its dependencies dict with zeros (where the
    pipeline allows interception) and verify Stage-2 output is unchanged.
    The engine's `compute_with_deps` interface narrows what each
    Stage-2 group sees, so this probe is bounded to "did the engine wire
    only the declared deps".

We do (a) here for all 9 groups, plus (b) targeted at Stage-2 groups
(G ← B[11], H ← F[25:36]).
"""
from __future__ import annotations

import inspect
import numpy as np
import pytest
import torch

from _infra import stimuli as stim
from _infra.dims import GROUPS, group_for_index


# ---------------------------------------------------------------------------
# (a) Static contract audit
# ---------------------------------------------------------------------------

def test_each_group_declares_dependencies_attribute(r3):
    """Every discovered group has a DEPENDENCIES tuple (possibly empty)."""
    for group in r3._groups.values():
        assert hasattr(group, "DEPENDENCIES"), (
            f"{type(group).__name__} missing DEPENDENCIES — Rule 3 audit fails"
        )
        assert isinstance(group.DEPENDENCIES, tuple), (
            f"{type(group).__name__}.DEPENDENCIES is not a tuple"
        )


def test_stage_1_groups_have_empty_dependencies(r3):
    """Stage-1 groups must declare DEPENDENCIES=() — they consume only mel/audio."""
    for group in r3._groups.values():
        if group.STAGE == 1:
            assert group.DEPENDENCIES == (), (
                f"{type(group).__name__} is Stage-1 but declares "
                f"DEPENDENCIES={group.DEPENDENCIES} — Rule 3 violation"
            )


def test_stage_2_groups_declare_their_deps(r3):
    """Stage-2 groups must declare exactly their documented dependencies.

    Documented (paper Table tab:arch + engine `dims.py`):
      * G rhythm_groove → ('energy',)
      * H harmony       → ('pitch_chroma',)
    """
    EXPECTED = {
        "rhythm_groove":    ("energy",),
        "harmony":          ("pitch_chroma",),
    }
    for group in r3._groups.values():
        if group.STAGE == 2:
            name = group.GROUP_NAME
            assert name in EXPECTED, (
                f"Stage-2 group '{name}' is unknown to L2.3 — update audit"
            )
            assert group.DEPENDENCIES == EXPECTED[name], (
                f"Stage-2 group '{name}' declares "
                f"DEPENDENCIES={group.DEPENDENCIES}, expected {EXPECTED[name]}"
            )


def test_no_group_imports_another_group(r3):
    """No group module imports another group module — would create a runtime
    binding outside the declared DAG."""
    import importlib
    for group in r3._groups.values():
        mod = importlib.import_module(type(group).__module__)
        src = inspect.getsource(mod)
        for other_letter in ("a_consonance", "b_energy", "c_timbre", "d_change",
                              "f_pitch_chroma", "g_rhythm_groove", "h_harmony",
                              "j_timbre_extended", "k_modulation"):
            if other_letter in mod.__name__:
                continue  # don't flag imports of one's own siblings
            forbidden = f"from .....ear.r3.groups.{other_letter}"
            assert forbidden not in src, (
                f"{mod.__name__} imports {other_letter} — Rule 3 violation"
            )
            forbidden2 = f"from ear.r3.groups.{other_letter}"
            assert forbidden2 not in src, (
                f"{mod.__name__} imports {other_letter} — Rule 3 violation"
            )


# ---------------------------------------------------------------------------
# (b) Dynamic probe — Stage-2 dep narrowness
# ---------------------------------------------------------------------------

def test_stage2_g_uses_only_onset_strength(r3, stim, mel_of):
    """Group G's `compute_with_deps` reads only `deps['energy'][:, :, 4]`
    (onset_strength). Zeroing all other channels of energy leaves G's
    output bit-identical."""
    audio = stim.stim_mix(duration_s=4.0)
    mel = mel_of(audio)

    # Get the group instances
    g_group = r3._groups["rhythm_groove"]
    e_group = r3._groups["energy"]

    # Run B (energy) once
    with torch.no_grad():
        energy_out = e_group.compute(mel)  # (B, T, 5)

    # Reference G output with full energy deps
    deps_full = {"energy": energy_out}
    with torch.no_grad():
        g_full = g_group.compute_with_deps(mel, deps_full)

    # Zero out every channel of energy except idx 4 (onset_strength)
    energy_only_onset = torch.zeros_like(energy_out)
    energy_only_onset[:, :, 4] = energy_out[:, :, 4]
    deps_narrow = {"energy": energy_only_onset}
    with torch.no_grad():
        g_narrow = g_group.compute_with_deps(mel, deps_narrow)

    a = g_full.cpu().numpy()
    b = g_narrow.cpu().numpy()
    assert np.array_equal(a, b), (
        f"Group G uses energy channels other than idx 4 (onset_strength). "
        f"Max |Δ| = {float(np.max(np.abs(a - b))):.6e}"
    )


def test_stage2_h_uses_only_chroma_12(r3, stim, mel_of):
    """Group H's `compute_with_deps` reads only `deps['pitch_chroma'][:, :, :12]`
    (the 12 chroma bins). Zeroing dims 12-15 (pitch_height, pc_entropy,
    salience, inharmonicity_index) leaves H's output bit-identical."""
    audio = stim.stim_mix(duration_s=3.0)
    mel = mel_of(audio)

    f_group = r3._groups["pitch_chroma"]
    h_group = r3._groups["harmony"]

    with torch.no_grad():
        f_out = f_group.compute(mel)  # (B, T, 16)

    deps_full = {"pitch_chroma": f_out}
    with torch.no_grad():
        h_full = h_group.compute_with_deps(mel, deps_full)

    # Zero everything past index 12 (the chroma 12-bin)
    f_only_chroma = f_out.clone()
    f_only_chroma[:, :, 12:] = 0.0
    deps_narrow = {"pitch_chroma": f_only_chroma}
    with torch.no_grad():
        h_narrow = h_group.compute_with_deps(mel, deps_narrow)

    a = h_full.cpu().numpy()
    b = h_narrow.cpu().numpy()
    assert np.array_equal(a, b), (
        f"Group H uses pitch_chroma channels past idx 12 (chroma_12). "
        f"Max |Δ| = {float(np.max(np.abs(a - b))):.6e}"
    )
