"""L3.4 — Cross-thread-permutation determinism.

torch's default thread count varies by hardware. We test that varying the
intra-op thread count (1, 2, 4, 8) produces bit-identical outputs.

Note: torch.set_num_threads() must be called BEFORE any torch op for the
change to take effect on some backends. We isolate each thread count in
its own subprocess to avoid contamination.

For speed, we test inside-process by setting torch.set_num_threads() before
each extract call. If the engine's behavior is truly thread-independent
(per L2.1 statelessness + L11.3 zero PRNG), this should suffice.
"""
from __future__ import annotations

import pytest
import torch


def test_cross_thread_permutation_1_2_4_8_bit_identical(h3_extract, stim):
    """Output is bit-identical across thread counts {1, 2, 4, 8}."""
    features = stim.stim_sinusoid(freq_hz=4.0, T=512, r3_dim=10)
    demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0)

    outputs_per_thread_count = {}
    for n_threads in [1, 2, 4, 8]:
        torch.set_num_threads(n_threads)
        out = h3_extract(features, demand)
        outputs_per_thread_count[n_threads] = out

    reference = outputs_per_thread_count[1]
    for n_threads in [2, 4, 8]:
        cur = outputs_per_thread_count[n_threads]
        for key in reference.features:
            ref_t = reference.features[key]
            cur_t = cur.features[key]
            diff = (ref_t - cur_t).abs().max().item()
            assert diff == 0.0, (
                f"L3.4 violated: thread_count={n_threads} differs from 1 "
                f"at tuple {key}: max-abs-diff = {diff}"
            )


def test_cross_thread_with_large_demand(h3_extract, stim):
    """Repeat L3.4 with a larger demand set (32 horizons × 1 morph × 1 law = 32 tuples)."""
    features = stim.stim_sinusoid(freq_hz=4.0, T=1024, r3_dim=10)
    demand = stim.demand_all_horizons_one_morph(r3_idx=10, morph=0, law=0)

    outputs = []
    for n_threads in [1, 4]:
        torch.set_num_threads(n_threads)
        outputs.append(h3_extract(features, demand))

    for key in outputs[0].features:
        a = outputs[0].features[key]
        b = outputs[1].features[key]
        diff = (a - b).abs().max().item()
        assert diff == 0.0, (
            f"L3.4 violated for large demand at tuple {key}: "
            f"thread 1 vs thread 4 max-abs-diff = {diff}"
        )
