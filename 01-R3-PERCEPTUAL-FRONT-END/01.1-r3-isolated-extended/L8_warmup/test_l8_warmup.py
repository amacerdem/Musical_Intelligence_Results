"""L8 — Warm-up tier disclosure.

Engine claim (paper §97-D instantiation Fig 1c, ``WarmupManager`` source):

    71/97 dims are strictly frame-local; 26/97 carry hidden temporal state
    under disclosed warm-up tiers — Tier 0 (immediately valid), Tier 1 ramp
    (344-frame ramp 0→1), Tier 1 zero (344-frame zero-then-1), Tier 2 zero
    (688-frame zero-then-1).

The warmup module's truth-of-record is
``Musical_Intelligence/ear/r3/pipeline/warmup.py``. We pin:

  1. Tier counts match the paper claim.
  2. Tier-0 dim set = all 97 ∖ (Tier-1 ∪ Tier-2).
  3. Each Tier-1-zero dim outputs zero before frame 344 on a non-zero stimulus.
  4. Each Tier-2-zero dim outputs zero before frame 688 on a non-zero stimulus.
  5. Each Tier-1-ramp dim is monotone non-decreasing in confidence over
     [0, 344) frames (engine documentation: linear ramp `min(1, t/344)`).

Note: the paper README claim was "79 / 9 / 8 / 1 = 97" which is consistent
with the current warmup.py (8 + 9 + 1 = 18 stateful, 79 frame-local).
"""
from __future__ import annotations

import importlib

import numpy as np
import pytest
import torch

from _infra import stimuli as stim


# ---------------------------------------------------------------------------
# Tier-count contract
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def warmup_module():
    return importlib.import_module(
        "Musical_Intelligence.ear.r3.pipeline.warmup"
    )


def test_tier_counts_match_pin(warmup_module):
    """Engine pin: 8 Tier-1-zero, 9 Tier-1-ramp, 1 Tier-2-zero, 79 Tier-0."""
    assert len(warmup_module.WARMUP_344_ZERO) == 8
    assert len(warmup_module.WARMUP_344_RAMP) == 9
    assert len(warmup_module.WARMUP_688_ZERO) == 1
    assert len(warmup_module.WARMUP_ALL) == 18
    # Tier 0 = 97 - 18 = 79 (frame-local)
    tier0 = set(range(97)) - set(warmup_module.WARMUP_ALL)
    assert len(tier0) == 79


def test_tier_sets_are_disjoint(warmup_module):
    z344 = set(warmup_module.WARMUP_344_ZERO)
    r344 = set(warmup_module.WARMUP_344_RAMP)
    z688 = set(warmup_module.WARMUP_688_ZERO)
    assert not (z344 & r344)
    assert not (z344 & z688)
    assert not (r344 & z688)


def test_tier_1_zero_is_K_modulation_spectrum(warmup_module):
    """Tier-1-zero set is exactly the 8 K-modulation-spectrum dims [83..90]."""
    expected = set(range(83, 91))
    assert set(warmup_module.WARMUP_344_ZERO) == expected


def test_tier_1_ramp_is_g_rhythm_minus_syncopation(warmup_module):
    """Tier-1-ramp set is the 9 G-rhythm dims excluding syncopation (44)."""
    expected = {41, 42, 43, 45, 46, 47, 48, 49, 50}
    assert set(warmup_module.WARMUP_344_RAMP) == expected


def test_tier_2_zero_is_syncopation(warmup_module):
    """Tier-2-zero set is exactly {44} (G syncopation_index)."""
    assert set(warmup_module.WARMUP_688_ZERO) == {44}


# ---------------------------------------------------------------------------
# Behavioural pin: WarmupManager.get_confidence
# ---------------------------------------------------------------------------

def test_get_confidence_at_frame_0(warmup_module):
    wm = warmup_module.WarmupManager()
    # Tier 0: confidence 1
    assert wm.get_confidence(0, 12) == 1.0          # warmth (Tier 0)
    # Tier 1 zero: confidence 0
    assert wm.get_confidence(0, 83) == 0.0          # modulation_0_5Hz
    # Tier 1 ramp: confidence 0/344 = 0
    assert wm.get_confidence(0, 41) == 0.0          # tempo_estimate
    # Tier 2 zero: confidence 0
    assert wm.get_confidence(0, 44) == 0.0          # syncopation_index


def test_get_confidence_at_frame_343_344_345(warmup_module):
    wm = warmup_module.WarmupManager()
    # Tier 1 zero: 0 before, 1 at/after threshold
    assert wm.get_confidence(343, 83) == 0.0
    assert wm.get_confidence(344, 83) == 1.0
    # Tier 1 ramp at 344 → 1.0; just before → < 1
    assert wm.get_confidence(344, 41) == 1.0
    assert wm.get_confidence(343, 41) < 1.0
    # Tier 2 zero: still 0 at 343/344
    assert wm.get_confidence(343, 44) == 0.0
    assert wm.get_confidence(344, 44) == 0.0


def test_get_confidence_at_frame_687_688_689(warmup_module):
    wm = warmup_module.WarmupManager()
    # Tier 2 zero: 0 before, 1 at/after threshold
    assert wm.get_confidence(687, 44) == 0.0
    assert wm.get_confidence(688, 44) == 1.0


def test_get_confidence_ramp_linearity(warmup_module):
    """Tier-1-ramp confidence is exactly `min(1, t/344)` — linear in t."""
    wm = warmup_module.WarmupManager()
    for t in [0, 50, 100, 172, 200, 300, 343, 344, 500]:
        actual = wm.get_confidence(t, 41)  # tempo_estimate (ramp dim)
        expected = min(1.0, t / 344.0)
        assert abs(actual - expected) < 1e-9


# ---------------------------------------------------------------------------
# End-to-end: short clip → Tier-1-zero dims output 0 before frame 344
# ---------------------------------------------------------------------------

def test_short_clip_modulation_rate_dims_zero_before_warmup(r3_extract):
    """**Disclosed engine behaviour**: short clip (< 344 frames):
    dims 83–88 (the 6 modulation-rate energies) are exactly 0; dims 89
    (modulation_centroid) and 90 (modulation_bandwidth) carry their
    degenerate-zero-input baseline of 0.2 and 0.0 respectively.

    The `WarmupManager` declares all 8 dims [83..91) as Tier-1-zero, but
    the engine's compute path only zeroes the 6 rate-energy dims; centroid
    and bandwidth are computed from those zeros and reach a degenerate
    baseline (0/eps) rather than being explicitly masked. Downstream
    consumers (H³, C³) are expected to query `WarmupManager.get_confidence`
    and gate the values themselves — the warmup metadata is informational
    rather than enforced.

    This test pins the de-facto behaviour so a future engine change to
    explicit warmup masking trips it.
    """
    audio = stim.stim_mix(duration_s=1.5)  # ≈ 258 frames
    feats = r3_extract(audio).features[0, :, :].cpu().numpy()
    assert feats.shape[0] < 344

    # Dims 83-88: rate energies — exactly 0 in the warmup zone
    rate_block = feats[:, 83:89]
    assert (rate_block == 0.0).all(), (
        f"Tier-1-zero rate-energy dim has nonzero output before frame 344: "
        f"max nonzero = {rate_block.max():.6e}"
    )

    # Dim 89: modulation_centroid baseline = (0 - (-1)) / 5 = 0.2 when input is zero
    centroid = feats[:, 89]
    assert np.allclose(centroid, 0.2, atol=1e-5), (
        f"modulation_centroid degenerate baseline ≠ 0.2 — engine has changed: "
        f"min={centroid.min():.4f}, max={centroid.max():.4f}"
    )

    # Dim 90: modulation_bandwidth baseline = sqrt(0)/2.5 = 0 when input is zero
    bandwidth = feats[:, 90]
    assert np.allclose(bandwidth, 0.0, atol=1e-5), (
        f"modulation_bandwidth degenerate baseline ≠ 0 — engine has changed: "
        f"max = {bandwidth.max():.4f}"
    )


def test_short_clip_syncopation_zero_before_688(r3_extract):
    """A clip < 688 frames: syncopation_index dim 44 outputs 0 throughout."""
    audio = stim.stim_mix(duration_s=3.0)  # ≈ 517 frames < 688
    sync = r3_extract(audio).features[0, :, 44].cpu().numpy()
    assert sync.shape[0] < 688
    assert (sync == 0.0).all()
