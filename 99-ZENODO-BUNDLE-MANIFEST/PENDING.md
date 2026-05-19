# Zenodo bundle manifest — PENDING

This directory is reserved for the Zenodo deposit manifest. It is empty by
design until the paper-submission gate is reached and a Zenodo DOI is minted.

## What will live here

When the bundle is published, this directory will contain:

- `MANIFEST.md` — list of tarballs in the Zenodo deposit, their SHA-256
  checksums, expected extracted sizes, and target unpack paths
- `CITATION.cff` — citation metadata for the dataset DOI
- `reproduce_all.sh` — single-command end-to-end verifier that downloads any
  missing public datasets, walks every phase, and emits the unified verdict
  table
- A `verdicts/` subdirectory mirroring the per-phase canonical verdict CSVs
  for at-a-glance machine-readable cross-check

## What is NOT in the Zenodo bundle

- Raw audio for any dataset (license-restricted; fetch from original
  publishers)
- The MI engine Python package source (lives separately at
  <https://github.com/amacerdem/musical-intelligence>; SHA `318eb2f5…`
  pinned in `_infra/manifests/engine_head.json`)

## How to verify before the bundle exists

Until the DOI is minted, third-party reviewers can:

1. Clone this repository
2. Clone the MI engine source at SHA `318eb2f5…` next to it
3. Set the `MI_ENGINE_ROOT` environment variable to the engine's parent
   directory if non-default
4. Run `python3 _infra/verify_all_phases.py` to walk every phase against
   its documented verdict envelope

Reviewers can also inspect any phase directly under `00-` through `06-`;
each phase ships a `README.md`, `00-METHODOLOGY.md`, `01-PROVENANCE.md`,
`02-RESULTS.md`, and machine-readable verdict CSVs / JSON manifests.
