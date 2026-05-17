# Musical Intelligence — Results & Audit Archive

**Engine SHA pin:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
**Engine aggregate SHA-256:** `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`
**Audit status:** 9-agent parallel constant-level provenance audit complete (2026-05-17)

This repository contains the **results layer** of the Musical Intelligence reproduction archive: per-phase verification reports, constant-level provenance audit, and paper revision evidence. Heavy artefacts (138 GB pre-computed MI engine output, ~3 GB dataset metadata, ds002725 BOLD intermediates) are vendored separately (Zenodo / R2 — DOI pending).

## Contents

```
Musical_Intelligence_Results/
├── 00-ENGINE-INTEGRITY-FOUNDATIONS/    ← per-phase reproduction packages (bottom-up)
│   └── 00.1-architectural-cardinalities/  (Phase 01 V2-current, 5 PASS)
├── 01-R3-PERCEPTUAL-FRONT-END/         ← (in progress)
├── 02-T3-TEMPORAL-LAYER/
├── 03-C3-BEHAVIORAL-VALIDATION/
├── 04-C3-BIOLOGICAL-SUBSTRATE/
├── 05-FMRI-BRAIN-GROUNDING/
├── 06-PORTFOLIO-FALSIFIABILITY/
├── 99-ZENODO-BUNDLE-MANIFEST/
├── _audits/                             ← constant-level provenance audit (16,248 sabit, 9 agent)
├── _infra/                              ← shared engine path resolver, helpers
├── datasets/paper-anchors/              ← paper-time reference intermediates (mech-region excluded — Zenodo)
├── datasets/consonance/                 ← Eerola/Marjieh/Harrison Carillon rating CSVs
└── datasets/emotion/DEAM/audio/         ← 5 DEAM held-out songs (Phase 5 ECE input)
```

## Audit headline (constant-level provenance, 2026-05-17)

| Category | Count | % |
|---|---:|---:|
| A LIT-VERBATIM | 67 | 0.41% |
| B LIT-DERIVED | 19 | 0.12% |
| C STRUCTURAL | 9,817 | 60.42% |
| D IDENTITY-PLACEHOLDER | 1,182 | 7.27% |
| E ENGINEERING-CHOICE | 5,157 | 31.74% |
| F HAND-SPECIFIED-DISCLOSED | 6 | 0.04% |
| G DEAD-CODE | 0 | 0.0% |
| **TOTAL** | **16,248** | 100% |

**Doctrine attestation:** Zero of 16,248 numeric constants are calibrated against cognitive data. 86 (0.53%) are literature-anchored bit-exact or formula-derived (Sethares 1993, Plomp-Levelt 1965, Krumhansl-Kessler 1982, Davis-Mermelstein 1980, Zwicker-Fastl 1990, IEC 61672-1, Stevens 1957). 6 are hand-specified-disclosed reward weights in `brain/reward.py`. The remaining 16,156 are structural topology, identity placeholders, or transparent engineering choices.

Full audit protocol: `_audits/INVESTIGATION-RULES.md` (v1.2)
Reconciled aggregate: `_audits/audit_combined.csv` (16,248 rows, 16 cols)
Reviewer-facing summary: `_audits/audit_summary.md`

## What's NOT in this repo (vendored separately)

| Asset | Size | Location |
|---|---|---|
| MI engine pre-compute (`engine_outputs/`) | 138 GB | Zenodo (DOI pending) |
| ds002725 mech×region BOLD intermediates | 702 MB | Zenodo |
| Gen 2 dataset metadata (ChillsDB / TenseMusic / PMEmo / Eerola / emotify) | ~3 GB | Zenodo |
| Raw audio (any dataset) | varies | Original publishers (license-restricted) |
| MI engine source (`Musical_Intelligence/` Python package) | 5.4 MB | github.com/amacerdem/musical-intelligence |

## Engine SHA verification

```bash
find <engine_root>/Musical_Intelligence -type f -name "*.py" -not -path "*__pycache__*" \
  | sort | xargs -I {} shasum -a 256 {} | awk '{print $1}' | shasum -a 256 | awk '{print $1}'
```

Match against `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88` → engine bit-identical to paper-time freeze.

## License

PolyForm Noncommercial 1.0.0 (research/audit/education unrestricted; commercial use requires separate license).
