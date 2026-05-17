"""L3.8 — Float32 vs Float64 sensitivity probe.

Engine pin: float32. We document the magnitude of drift between float32
and float64 inputs to characterise the engine's numerical sensitivity.

Expected: drift small but non-zero (float32 has ~7-decimal precision; the
cumulative attention-weighted sum across a 32-frame window can accumulate
~1e-6 error). This is a CHARACTERISATION test, not a pass/fail; we assert
the drift is below a documented bound (1e-4) which is well above engine's
own |Δρ| ≤ 8.8e-5 reproducibility envelope.
"""
from __future__ import annotations

import pytest
import torch


def test_float32_vs_float64_drift_below_1e_minus_4(h3_extract, stim):
    """Engine pin is float32. Float64 input drifts within documented bound."""
    # Note: H3Extractor casts internally; we generate the input in both dtypes.
    # The sinusoid generator uses float32 by default; we make a float64 version.
    features_f32 = stim.stim_sinusoid(freq_hz=4.0, T=512, r3_dim=10)
    features_f64 = features_f32.to(torch.float64)

    demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0)

    # Run engine on both; cast f64 output back to f32 for comparison
    out_f32 = h3_extract(features_f32, demand)
    out_f64 = h3_extract(features_f64, demand)

    drifts = []
    for key in out_f32.features:
        a = out_f32.features[key].to(torch.float64)
        b = out_f64.features[key].to(torch.float64)
        diff = (a - b).abs().max().item()
        drifts.append((key, diff))

    max_drift = max(d for _, d in drifts)
    # Document the actual drift; assert it's well within engine's reproducibility envelope
    assert max_drift < 1e-4, (
        f"L3.8: float32-vs-float64 drift {max_drift} exceeds 1e-4 bound. "
        f"Engine's documented reproducibility envelope is |Δρ| ≤ 8.8e-5; "
        f"a drift this large suggests the engine is more dtype-sensitive "
        f"than documented."
    )

    # Print observed drift for documentation purposes (visible with -s flag)
    print(f"\n  L3.8 max float32-vs-float64 drift: {max_drift:.2e}")
    print(f"  (engine's documented |Δρ| envelope: ≤ 8.8e-5)")
