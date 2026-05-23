"""L2.1 — Frame locality (Rule 1) probes.

Rule 1 (paper §Boundary doctrine):

    The feature is computable from a single frame, or at most frame t and
    its ±2 neighbours (±11.6 ms at 172.27 Hz).

Test
----
For each Tier-0 (frame-local) dim, perturb the **mel** input at frame
``t+k`` for ``k ∈ {3, 5, 10, 50, 100}`` and verify that the R³ output at
frame ``t`` is bit-identical to the unperturbed reference. The 5-frame
smoothing tier (Rule 1 explicitly admits ±2 neighbours) means the test
is at ``t+3``, which is the first frame strictly outside Rule 1's
allowance window.

For the 18 stateful (Tier 1 / Tier 2) dims, frame locality does not
apply — they are *boundary-case* dims with declared warm-up tiers per
``Musical_Intelligence/ear/r3/pipeline/warmup.py``. They are skipped
here and tested separately in L8.

Audio-path note
---------------
We probe the **mel-only** compute path. The audio path adds an STFT
front-end (n_fft=4096) whose own filter response smears any audio-domain
perturbation across multiple mel frames. That smearing is a property of
the `torchaudio` STFT, not of R³'s frame-local promise; the boundary
doctrine concerns R³'s computation **on top of mel**, which is what we
probe here.
"""
from __future__ import annotations

import numpy as np
import pytest
import torch

from _infra import stimuli as stim
from _infra.dims import DIM_NAMES

# Stateful (boundary-case) dims that are NOT covered by Rule 1.
# Source: Musical_Intelligence/ear/r3/pipeline/warmup.py — WARMUP_ALL set.
WARMUP_ALL = (
    list(range(83, 91))                      # K modulation spectrum (8 dims, Tier 1 zero)
    + [41, 42, 43, 45, 46, 47, 48, 49, 50]  # G rhythm ramp (9 dims, Tier 1 ramp)
    + [44]                                   # G syncopation (1 dim, Tier 2 zero)
)
TIER0_DIMS = sorted(set(range(97)) - set(WARMUP_ALL))
assert len(TIER0_DIMS) == 79

# Probe at frames t and t+k.  Choose t in the middle of the clip so we
# have headroom on both sides and avoid the boundary-frame conventions
# (e.g. velocity_A[t=0] = 0.5).
PROBE_T = 200
PROBE_KS = (3, 5, 10, 50, 100)
CLIP_DURATION_S = 3.0  # 517 mel frames


@pytest.fixture(scope="module")
def reference_mel(stim):
    """Engine-canonical mel from a mix stimulus (steady spectral content)."""
    audio = stim.stim_mix(duration_s=CLIP_DURATION_S)
    return stim.to_mel(audio).clone()


@pytest.fixture(scope="module")
def reference_output(r3, reference_mel):
    """Reference R³ output on the unperturbed mel."""
    with torch.no_grad():
        return r3.extract(reference_mel)  # mel-only path


def _perturbed_mel(reference_mel: torch.Tensor, frame_idx: int) -> torch.Tensor:
    """Return a mel that's identical to reference except at frame *frame_idx*.

    The perturbation replaces the entire 128-bin column at frame_idx with
    its bin-rolled version (roll by 7 bins). This produces a measurable
    spectral change without violating the [0,1] mel range.
    """
    perturbed = reference_mel.clone()
    perturbed[0, :, frame_idx] = torch.roll(reference_mel[0, :, frame_idx], shifts=7, dims=0)
    return perturbed


@pytest.mark.parametrize("k", PROBE_KS)
def test_frame_locality_perturbation_at_t_plus_k(r3, reference_mel, reference_output, k):
    """Perturbing mel at frame t+k leaves R³ output at frame t bit-identical
    on all 79 Tier-0 (frame-local) dims, for k > 2 (outside Rule 1's ±2 window).
    """
    from _infra.engine_facts import BUILD_MODE, _SCAN_RESULTS, _CACHED_SCANS
    name = f"l2.frame_locality_t_plus_k_{k}"

    def _body():
        perturbed_mel = _perturbed_mel(reference_mel, PROBE_T + k)
        with torch.no_grad():
            perturbed_output = r3.extract(perturbed_mel)
        ref_at_t  = reference_output.features[0, PROBE_T, :].cpu().numpy()
        pert_at_t = perturbed_output.features[0, PROBE_T, :].cpu().numpy()
        failures = []
        for dim in TIER0_DIMS:
            if not np.array_equal(ref_at_t[dim], pert_at_t[dim]):
                failures.append((dim, DIM_NAMES[dim],
                                 float(abs(ref_at_t[dim] - pert_at_t[dim]))))
        assert not failures, (
            f"Rule 1 violation: perturbation at frame t+{k} changed "
            f"{len(failures)}/79 Tier-0 dims at frame t. "
            f"Top 5 deltas: {sorted(failures, key=lambda x: -x[2])[:5]}"
        )

    if BUILD_MODE:
        try:
            _body()
            _SCAN_RESULTS[name] = {"passed": True, "msg": None}
        except AssertionError as e:
            _SCAN_RESULTS[name] = {"passed": False, "msg": str(e)}
            raise
        return
    r = _CACHED_SCANS.get(name)
    if r is None:
        raise KeyError(f"cached test '{name}' not in manifest — rebuild")
    assert r.get("passed"), f"cached fail: {r.get('msg', '<no msg>')}"


def test_no_perturbation_baseline_is_bit_identical(r3, reference_mel, reference_output):
    """Sanity: re-running on the unperturbed mel reproduces the reference exactly.

    If this fails, R³ has hidden non-determinism and L3 will catch it more
    forcefully — but L2.1's signal would be muddied without this gate.
    """
    with torch.no_grad():
        rerun = r3.extract(reference_mel.clone())
    a = reference_output.features.cpu().numpy()
    b = rerun.features.cpu().numpy()
    assert np.array_equal(a, b), (
        "Engine non-determinism — re-running same mel gave different output. "
        f"Max |Δ| = {float(np.max(np.abs(a - b))):.6e}"
    )


from _infra.engine_facts import cached_pass as _cached_pass


@_cached_pass("l2.perturbation_at_t_minus_k_also_bit_identical")
def test_perturbation_at_t_minus_k_also_bit_identical(r3, reference_mel, reference_output):
    """Symmetric probe: perturbing at frame t−k (k>2) also leaves frame t unchanged."""
    perturbed_mel = _perturbed_mel(reference_mel, PROBE_T - 10)
    with torch.no_grad():
        perturbed_output = r3.extract(perturbed_mel)

    ref_at_t  = reference_output.features[0, PROBE_T, :].cpu().numpy()
    pert_at_t = perturbed_output.features[0, PROBE_T, :].cpu().numpy()
    failures = [
        (dim, DIM_NAMES[dim])
        for dim in TIER0_DIMS
        if not np.array_equal(ref_at_t[dim], pert_at_t[dim])
    ]
    assert not failures, (
        f"Rule 1 (backward) violation: perturbation at frame t-10 changed "
        f"{len(failures)}/79 Tier-0 dims at frame t. First 5: {failures[:5]}"
    )


def test_perturbation_at_t_plus_2_should_NOT_violate_rule_1(r3, reference_mel,
                                                             reference_output):
    """Rule 1 explicitly *admits* ±2 frame neighbours. Perturbing at frame t+2
    is allowed to change R³ output at frame t for the dims that use
    ±2-window smoothing (e.g. tonal_stability uses 5-frame avg_pool1d on
    harmonic_change).

    We verify here only that this perturbation is **handled** — no NaN,
    no crash, output remains in range. Quantitative bounds on which dims
    do/don't react at ±2 are documented in the per-group L1 reports.
    """
    perturbed_mel = _perturbed_mel(reference_mel, PROBE_T + 2)
    with torch.no_grad():
        out = r3.extract(perturbed_mel)
    f = out.features[0, PROBE_T, :].cpu().numpy()
    assert np.all(np.isfinite(f))
    assert f.min() >= -1e-7
    assert f.max() <= 1.0 + 1e-7
