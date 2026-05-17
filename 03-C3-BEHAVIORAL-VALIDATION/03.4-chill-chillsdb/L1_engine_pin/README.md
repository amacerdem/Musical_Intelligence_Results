# L1 — Engine Pin Integrity

**Purpose:** Refuse to run downstream layers if the engine has drifted from the canonical paper-time SHA aggregate.

## What this layer asserts

1. `_infra/manifests/engine_pin.json` exists and declares `content_aggregate_sha256` (64 hex chars).
2. `Musical_Intelligence/` tree resolves and contains the canonical entry point `ear/r3/extractor.py`.
3. The SHA-256 aggregate of all `.py` files under `Musical_Intelligence/` matches the pinned value `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`.
4. `_infra/manifests/paper_time_baseline.json` declares the headline Tier-1 numbers for MMP P2:familiarity (rb ≥ +0.20, p_bonf < 0.05).

## What this layer does NOT test

- Engine correctness (covered by `19-r3-isolated-validation` + `20-t3-isolated-validation`).
- Engine determinism across runs (covered by 19-r3 L3).

This layer only verifies that the engine bits on disk match what the paper was run against.

## Failure mode

If `aggregate_engine_sha(Musical_Intelligence) != pinned`, the conftest `_pin_integrity` session fixture halts pytest at session start with `pytest.exit(returncode=2)`. Run cannot continue — no result is more important than knowing you have the correct engine.

## Files

- `test_engine_pin.py` — explicit assertions
- `../_infra/sha_utils.py` — `aggregate_engine_sha()` implementation (copied from 19-r3)
- `../_infra/manifests/engine_pin.json` — pinned SHA + commit metadata
