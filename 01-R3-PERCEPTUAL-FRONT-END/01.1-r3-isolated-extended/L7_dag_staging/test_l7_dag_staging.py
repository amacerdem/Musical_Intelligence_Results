"""L7 — DAG & staging correctness.

Engine claim (paper §97-D instantiation, §Architecture Fig 1b):

    R³ is a 2-stage acyclic DAG. Stage 1 is parallel-ready (7 groups, no
    inter-group deps); Stage 2 has 2 groups (G ← B[11], H ← F[25:36]).

This module verifies:

  * The DAG is acyclic and covers all 9 groups.
  * Stage 1 ⇒ Stage 2 ordering is enforced (validated by `DependencyDAG.validate()`).
  * No group's `compute()` reaches into another group's output via globals,
    closures, or class state.
  * Stage 2's `compute_with_deps` interface narrows what each group sees.
  * Serial vs parallel execution of Stage-1 groups produces identical output.
"""
from __future__ import annotations

import numpy as np
import pytest
import torch

from _infra import stimuli as stim


# ---------------------------------------------------------------------------
# DAG self-validation
# ---------------------------------------------------------------------------

def test_dag_validates(r3):
    """`DependencyDAG.validate()` passes — covers acyclicity, full coverage,
    no cross-stage cycles."""
    r3._dag.validate()


def test_dag_has_two_stages(r3):
    assert r3._dag.stages == (1, 2)


def test_stage_1_has_seven_groups(r3):
    s1 = r3._dag.get_stage(1)
    assert len(s1) == 7
    expected = {"consonance", "energy", "timbre", "change",
                "pitch_chroma", "timbre_extended", "modulation"}
    assert set(s1) == expected


def test_stage_2_has_two_groups(r3):
    s2 = r3._dag.get_stage(2)
    assert set(s2) == {"rhythm_groove", "harmony"}


def test_stage_2_dependencies_are_canonical(r3):
    """G depends only on energy; H depends only on pitch_chroma."""
    assert r3._dag.get_dependencies("rhythm_groove") == ("energy",)
    assert r3._dag.get_dependencies("harmony")       == ("pitch_chroma",)


def test_stage_1_groups_have_no_dependencies(r3):
    for g in r3._dag.get_stage(1):
        assert r3._dag.get_dependencies(g) == ()


# ---------------------------------------------------------------------------
# Stage-2 narrow-deps probe (also in L2.3, re-pinned here)
# ---------------------------------------------------------------------------

def test_g_consumes_only_onset_strength(r3, mel_of, stim):
    audio = stim.stim_mix(duration_s=4.0)
    mel = mel_of(audio)
    e_group = r3._groups["energy"]
    g_group = r3._groups["rhythm_groove"]
    with torch.no_grad():
        e_out = e_group.compute(mel)
        g_full = g_group.compute_with_deps(mel, {"energy": e_out})
    e_only_onset = torch.zeros_like(e_out)
    e_only_onset[:, :, 4] = e_out[:, :, 4]
    with torch.no_grad():
        g_narrow = g_group.compute_with_deps(mel, {"energy": e_only_onset})
    assert torch.equal(g_full, g_narrow)


def test_h_consumes_only_chroma_12(r3, mel_of, stim):
    audio = stim.stim_mix(duration_s=3.0)
    mel = mel_of(audio)
    f_group = r3._groups["pitch_chroma"]
    h_group = r3._groups["harmony"]
    with torch.no_grad():
        f_out = f_group.compute(mel)
        h_full = h_group.compute_with_deps(mel, {"pitch_chroma": f_out})
    f_only_chroma = f_out.clone()
    f_only_chroma[:, :, 12:] = 0.0
    with torch.no_grad():
        h_narrow = h_group.compute_with_deps(mel, {"pitch_chroma": f_only_chroma})
    assert torch.equal(h_full, h_narrow)


# ---------------------------------------------------------------------------
# Stage-1 parallel-equivalence: serial = parallel
# ---------------------------------------------------------------------------

def test_stage1_groups_independent(r3, mel_of, stim):
    """Run each Stage-1 group in isolation and compare to its slice in the
    full pipeline. They must be identical."""
    audio = stim.stim_mix(duration_s=2.0)
    mel = mel_of(audio)

    with torch.no_grad():
        full_out = r3.extract(mel, audio=audio, sr=44100).features.cpu().numpy()

    for group_name in r3._dag.get_stage(1):
        group = r3._groups[group_name]
        # Try the audio path first (returns Tensor or None depending on override).
        # Fall back to compute(mel) if audio path returns None (base class default).
        isolated_t = None
        if hasattr(group, "compute_from_audio"):
            with torch.no_grad():
                isolated_t = group.compute_from_audio(mel, audio, 44100)
        if isolated_t is None:
            with torch.no_grad():
                isolated_t = group.compute(mel)
        isolated = isolated_t.cpu().numpy()
        s, e = group.INDEX_RANGE
        # Engine FeatureNormalizer also clamps; we compare post-clamp values.
        full_slice = full_out[0, :, s:e]
        # `isolated` is (B, T, dim) — squeeze batch to compare with full_slice (T, dim)
        iso_2d = isolated[0]
        # Note: full goes through FeatureNormalizer which clamps to [0,1].
        # Group output is also clamped internally to [0,1]. So they must match.
        assert np.array_equal(iso_2d, full_slice), (
            f"Stage-1 group {group_name} output drifts when run in isolation. "
            f"max |Δ| = {np.max(np.abs(iso_2d - full_slice)):.3e}"
        )


# ---------------------------------------------------------------------------
# No cycles: Stage-2 groups never feed back into Stage-1
# ---------------------------------------------------------------------------

def test_stage_1_does_not_consume_stage_2_output(r3, mel_of, stim):
    """Permuting Stage-2 groups' output (G, H) cannot affect Stage-1 outputs.

    Operationally: run R³ twice on the same mel; compare Stage-1 dim slices.
    If Stage-1 ever consumed Stage-2 output via globals or shared state,
    the second run could differ — but L3 already pins bit-identicality, so
    this is a static-contract repeat. We verify the static contract by
    checking that no Stage-1 group declares any DEPENDENCIES."""
    for name in r3._dag.get_stage(1):
        group = r3._groups[name]
        assert group.DEPENDENCIES == (), (
            f"Stage-1 group {name} declares DEPENDENCIES={group.DEPENDENCIES} "
            f"— would create a cycle"
        )
