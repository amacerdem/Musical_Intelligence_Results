"""L3.1 + L3.3 — Run-to-run + cross-seed determinism.

L3.1: 1,000 independent extract() calls on the same input within one process.
      max-abs-diff = 0 across all calls.
L3.3: T³ contains no PRNG (per L11.3 static AST scan); changing torch RNG
      seed between calls must NOT affect output.

These two tests live together because they exercise the same harness in the
same process; the cross-seed test simply varies torch.manual_seed between
otherwise identical extract() calls.
"""
from __future__ import annotations

import pytest
import torch


def test_run_to_run_1000_iterations_bit_identical(h3_extract, stim):
    """1,000 extract() calls on the same input produce bit-identical output."""
    features = stim.stim_sinusoid(freq_hz=4.0, T=512, r3_dim=10)
    demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0)
    reference = h3_extract(features, demand)

    n_iters = 1_000
    for i in range(n_iters):
        out = h3_extract(features, demand)
        for key in reference.features:
            ref_t = reference.features[key]
            cur_t = out.features[key]
            diff = (ref_t - cur_t).abs().max().item()
            assert diff == 0.0, (
                f"L3.1 violated at iteration {i}, tuple {key}: "
                f"max-abs-diff = {diff} (expected 0.0)"
            )


def test_cross_seed_torch_manual_seed_no_effect(h3_extract, stim):
    """Setting torch.manual_seed to different values between extract() calls
    must NOT affect the output (T³ has no PRNG; per L11.3 AST scan)."""
    features = stim.stim_sinusoid(freq_hz=4.0, T=512, r3_dim=10)
    demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0)

    torch.manual_seed(42)
    out_seed_42 = h3_extract(features, demand)

    torch.manual_seed(137)
    out_seed_137 = h3_extract(features, demand)

    torch.manual_seed(20260509)
    out_seed_date = h3_extract(features, demand)

    for key in out_seed_42.features:
        a = out_seed_42.features[key]
        b = out_seed_137.features[key]
        c = out_seed_date.features[key]
        diff_ab = (a - b).abs().max().item()
        diff_ac = (a - c).abs().max().item()
        assert diff_ab == 0.0, (
            f"L3.3 violated: seed 42 vs 137 differ at tuple {key}: "
            f"max-abs-diff = {diff_ab} (T³ has no PRNG; should be 0)"
        )
        assert diff_ac == 0.0, (
            f"L3.3 violated: seed 42 vs 20260509 differ at tuple {key}: "
            f"max-abs-diff = {diff_ac}"
        )


def test_cross_seed_extreme_seeds(h3_extract, stim):
    """Edge seeds (0, 1, 2**31 - 1) — same input, different seeds, still bit-identical."""
    features = stim.stim_constant(value=0.5, T=256, r3_dim=10)
    demand = stim.demand_single(r3_idx=10, horizon=5, morph=0, law=0)

    seeds = [0, 1, 2**31 - 1]
    outputs = []
    for seed in seeds:
        torch.manual_seed(seed)
        outputs.append(h3_extract(features, demand))
    ref = outputs[0].features[(10, 5, 0, 0)]
    for i, out in enumerate(outputs[1:], start=1):
        cur = out.features[(10, 5, 0, 0)]
        diff = (ref - cur).abs().max().item()
        assert diff == 0.0, (
            f"Cross-seed differ: seed {seeds[0]} vs seed {seeds[i]}: "
            f"max-abs-diff = {diff}"
        )
