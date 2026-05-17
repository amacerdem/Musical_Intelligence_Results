"""L3.2 — Cross-process determinism.

Spawn a fresh Python interpreter, run extract() with a known seeded input,
serialise the output to disk, then load it back in the parent process and
compare bit-identically against an in-process extract() call.

This guards against any process-startup-order or memory-layout effect that
could perturb output. Per L2.1 (zero non-init self-assigns) + L11.3 (zero
PRNG) + L11.6 (zero env-var reads), we expect bit-identical outputs.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import torch


CHILD_SCRIPT = '''
import sys
sys.path.insert(0, "{project_root}")
sys.path.insert(0, "{suite_root}")
import torch
from Musical_Intelligence.ear.h3 import H3Extractor
from _infra import stimuli as stim

h3 = H3Extractor()
features = stim.stim_sinusoid(freq_hz=4.0, T=512, r3_dim=10)
demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0)
out = h3.extract(features, demand)

# Serialise: dict of tuple-key (as JSON-safe string) → tensor (saved separately)
import torch
out_path = "{out_path}"
serialised = {{
    repr(k): out.features[k] for k in sorted(out.features.keys())
}}
torch.save(serialised, out_path)
'''


def test_cross_process_bit_identical(h3_extract, stim, project_root, tmp_path):
    """A fresh Python interpreter produces bit-identical T³ output."""
    suite_root = Path(__file__).resolve().parent.parent  # T3_Isolated_Validation/

    # 1) In-process reference
    features = stim.stim_sinusoid(freq_hz=4.0, T=512, r3_dim=10)
    demand = stim.demand_all_morphs_one_horizon(r3_idx=10, horizon=5, law=0)
    reference = h3_extract(features, demand)

    # 2) Subprocess result
    out_path = tmp_path / "subprocess_out.pt"
    script_text = CHILD_SCRIPT.format(
        project_root=str(project_root),
        suite_root=str(suite_root),
        out_path=str(out_path),
    )
    result = subprocess.run(
        [sys.executable, "-c", script_text],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        pytest.fail(
            f"Subprocess failed (return {result.returncode}):\n"
            f"STDOUT:\n{result.stdout}\n\n"
            f"STDERR:\n{result.stderr}"
        )

    # 3) Load subprocess output and compare
    subprocess_features = torch.load(out_path, weights_only=False)
    for key, ref_tensor in reference.features.items():
        sub_tensor = subprocess_features[repr(key)]
        diff = (ref_tensor - sub_tensor).abs().max().item()
        assert diff == 0.0, (
            f"L3.2 violated: cross-process output for tuple {key} "
            f"max-abs-diff = {diff} (expected 0.0)"
        )
