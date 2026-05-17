"""Validate Section B manifests."""
import json
import subprocess
from pathlib import Path

import pytest

INFRA = Path(__file__).resolve().parent.parent


def _valid_example():
    """Return a fresh valid example for negative-test mutation."""
    return {
        "axis_id": "AXIS-4",
        "axis_name": "Held-out belief calibration",
        "engine_head": "318eb2f529d7103e8b7d80b01228357fdc4e0217",
        "seed_registry": {"primary": 2026050502, "bootstrap": 1729, "permutation": 42},
        "phase_close_date": "2026-05-05",
        "git_commit_hash": "abc123def456",
        "claims": [{
            "claim_id": "C-CALIB-01",
            "paper_value": 0.079,
            "tolerance": "absolute_deviation <= 0.025",
            "reproduced_value": 0.0841,
            "deviation": 0.0051,
            "verdict": "PASS",
            "iteration_count": 1,
            "notes": "Pooled ECE on 5 DEAM held-out songs."
        }]
    }


def test_engine_head_pinned():
    # NOTE: value mirrors manifests/engine_head.json — update both on engine HEAD bump
    manifest = json.loads((INFRA / "manifests/engine_head.json").read_text())
    assert manifest["pinned_commit"] == "318eb2f529d7103e8b7d80b01228357fdc4e0217"
    assert manifest["pinned_date"] == "2026-05-06"
    assert manifest["engine_path"] == "Science/Musical_Intelligence"


def test_engine_head_verification_block_complete():
    manifest = json.loads((INFRA / "manifests/engine_head.json").read_text())
    v = manifest["verification"]
    assert v["frame_rate_hz"] == 172.27
    assert v["r3_dim"] == 97
    assert v["c3_mechanisms"] == 89
    assert v["c3_beliefs_f1_f8"] == 121
    assert v["c3_beliefs_full_registry"] == 131
    assert v["ram_regions"] == 26
    assert v["region_links"] == 529
    assert v["neuro_links"] == 48


def test_seed_registry_complete():
    seeds = json.loads((INFRA / "manifests/seed_registry.json").read_text())
    # Phases 00-18 (19 top-level entries; Phase 18 added 2026-05-06 per user-approved master-plan revision)
    expected_phases = [f"phase_{n:02d}" for n in range(0, 19)]
    for phase in expected_phases:
        assert phase in seeds["phases"], f"Missing seed for {phase}"


def test_seed_registry_phase18_sub_axes():
    """Phase 18 has 5 sub-axes (5 Tier-1 fMRI datasets)."""
    seeds = json.loads((INFRA / "manifests/seed_registry.json").read_text())
    for n in range(1, 6):
        key = f"phase_18_{n}"
        assert key in seeds["phases"], f"Missing Phase 18 sub-axis {key}"


def test_seed_registry_phase00_5_present():
    """Phase 0.5 V-fMRI Eligibility Audit is the gate for Phases 11/12/18."""
    seeds = json.loads((INFRA / "manifests/seed_registry.json").read_text())
    assert "phase_00_5" in seeds["phases"], "Missing Phase 0.5 V-fMRI Eligibility Audit seed"
    p = seeds["phases"]["phase_00_5"]
    assert p["primary"] == 20260506005
    assert "eligibility" in p["scope"].lower()


def test_seed_registry_inherited_phase11_v3():
    seeds = json.loads((INFRA / "manifests/seed_registry.json").read_text())
    assert seeds["phases"]["phase_11"]["primary"] == 20260503


def test_seed_registry_inherited_phase05_v6_a2():
    seeds = json.loads((INFRA / "manifests/seed_registry.json").read_text())
    assert seeds["phases"]["phase_05"]["primary"] == 2026050502


def test_seed_registry_inherited_phase14_v5():
    seeds = json.loads((INFRA / "manifests/seed_registry.json").read_text())
    assert seeds["phases"]["phase_14"]["primary"] == 2026050505


def test_seed_registry_lock_policy():
    seeds = json.loads((INFRA / "manifests/seed_registry.json").read_text())
    assert "LOCKED" in seeds["policy"]


def test_claim_schema_validates_example():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((INFRA / "manifests/claim_schema.json").read_text())
    jsonschema.validate(_valid_example(), schema)


def test_claim_schema_rejects_invalid_verdict():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((INFRA / "manifests/claim_schema.json").read_text())
    bad = _valid_example()
    bad["claims"][0]["verdict"] = "MAYBE"  # invalid
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_claim_schema_rejects_short_engine_head():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((INFRA / "manifests/claim_schema.json").read_text())
    bad = _valid_example()
    bad["engine_head"] = "318eb2f5"  # only 8 chars
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_claim_schema_rejects_iteration_count_zero():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((INFRA / "manifests/claim_schema.json").read_text())
    bad = _valid_example()
    bad["claims"][0]["iteration_count"] = 0
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_claim_schema_rejects_iteration_count_six():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((INFRA / "manifests/claim_schema.json").read_text())
    bad = _valid_example()
    bad["claims"][0]["iteration_count"] = 6
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_claim_schema_rejects_lowercase_axis_id():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((INFRA / "manifests/claim_schema.json").read_text())
    bad = _valid_example()
    bad["axis_id"] = "axis-4"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_claim_schema_rejects_unknown_property():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads((INFRA / "manifests/claim_schema.json").read_text())
    bad = _valid_example()
    bad["axsi_id"] = "AXIS-4"  # typo
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_eligibility_schema_validates():
    """Phase 0.5 eligibility-row schema accepts a canonical valid row."""
    jsonschema = pytest.importorskip("jsonschema")
    schema_path = (
        INFRA.parent / "00.5-fmri-eligibility" / "code" / "schema_eligibility.json"
    )
    if not schema_path.exists():
        pytest.skip("eligibility schema not yet created")
    schema = json.loads(schema_path.read_text())
    valid_row = {
        "dataset_id": "ds002725",
        "modality": "fMRI",
        "n_dataset_level": 17,
        "audio_available": "yes_in_dataset",
        "exact_timing": "events_tsv_sub_TR",
        "mni_derivative": "runnable_via_fmriprep",
        "n_qc_pass": 17,
        "n_alignment_qualified": 12,
        "mi_compatible": True,
        "exclusion_reason": "",
        "phase_consumer": "Phase 11",
        "notes": "Mendelssohn Op.54, 7 classical pieces.",
    }
    jsonschema.validate(valid_row, schema)
