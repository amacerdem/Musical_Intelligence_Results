# Musical Intelligence — Results & Audit Archive

**Cite this archive:** [10.5281/zenodo.20457643](https://doi.org/10.5281/zenodo.20457643) (v2.0.0) · concept-DOI [10.5281/zenodo.19744623](https://doi.org/10.5281/zenodo.19744623) (always resolves to latest version)
**Engine SHA pin:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
**Engine aggregate SHA-256:** `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`
**Audit status:** 9-agent parallel constant-level provenance audit complete (2026-05-17)

This repository contains the **results layer** of the Musical Intelligence reproduction archive: per-phase verification reports, constant-level provenance audit, and paper revision evidence. Heavy artefacts (138 GB pre-computed MI engine output, ~3 GB dataset metadata, ds002725 BOLD intermediates) are deposited as separate Zenodo records (DOIs pending).

## Contents

```
Musical_Intelligence_Results/
├── 00-ENGINE-INTEGRITY-FOUNDATIONS/    ← per-phase reproduction packages (bottom-up)
│   ├── 00.1-architectural-cardinalities/  (10/10 PASS — 16,248 constants partitioned across 7 categories)
│   ├── 00.2-fmri-eligibility-audit/        (6/6 PASS)
│   └── 00.3-compute-profile/                (1 PASS + 5 CAVEAT, hardware-tier divergence)
├── 01-R3-PERCEPTUAL-FRONT-END/         ← R³ 97D front-end (extended 531/531 pytest PASS)
├── 02-T3-TEMPORAL-LAYER/                ← T³ multi-scale temporal grammar (extended 207/207 pytest PASS)
├── 03-C3-BEHAVIORAL-VALIDATION/         ← C³ behavioural validation (functional anchors + ECE + Cheung + ChillsDB + TenseMusic + PMEmo + Eerola)
├── 04-C3-BIOLOGICAL-SUBSTRATE/          ← pharmacology + RAM topology
├── 05-FMRI-BRAIN-GROUNDING/             ← Mendelssohn pilot + mech×region + ceiling + voxelwise + cross-dataset + independent fMRI
├── 06-PORTFOLIO-FALSIFIABILITY/         ← pre-committed Table 5 + AI-baseline ablation
├── _audits/                             ← constant-level provenance audit (16,248 constants, 9 parallel agents)
├── _infra/                              ← shared engine path resolver, helpers, verifier scripts
├── engine_outputs/_unit_test_oracles/   ← cache substrate for reviewer-mode pytest (R³ + T³ extended; ~185 MB; Zenodo-shipped)
├── datasets/paper-anchors/              ← paper-time reference intermediates (mech-region excluded — Zenodo)
├── datasets/consonance/                 ← Eerola/Marjieh/Harrison Carillon rating CSVs
└── datasets/emotion/DEAM/audio/         ← 5 DEAM held-out songs (Phase 03.2 ECE input)
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
| MI engine pre-compute (`engine_outputs/`) | 138 GB | Zenodo (DOI pending) — includes the `_unit_test_oracles/` cache substrate (~185 MB) needed for reviewer-mode pytest |
| ds002725 mech×region BOLD intermediates | 702 MB | Zenodo |
| Gen 2 dataset metadata (ChillsDB / TenseMusic / PMEmo / Eerola / emotify) | ~3 GB | Zenodo |
| Raw audio (any dataset) | varies | Original publishers (license-restricted) |
| MI engine source (`Musical_Intelligence/` Python package) | 5.4 MB | github.com/amacerdem/musical-intelligence — **NOT required** for reviewer-mode reproduction; only needed to rebuild the oracle (`MI_BUILD_ORACLE=1 pytest …`) |

## Reviewer mode — reproduce without engine source or raw audio

A reviewer who has cloned this repository and downloaded `engine_outputs/` from Zenodo can verify every paper claim without cloning the engine source or fetching dataset audio:

```bash
python3 _infra/verify_all_phases.py                 # 14 CSV-verdict phases (132 verdicts) — < 5 s
python3 -m pytest 01-R3-PERCEPTUAL-FRONT-END/01.1-r3-isolated-extended  # 531/531 — ~7 s cache mode
python3 -m pytest 02-T3-TEMPORAL-LAYER/02.1-t3-isolated-extended         # 207/207 — ~0.5 s cache mode
python3 -m pytest 03-C3-BEHAVIORAL-VALIDATION 05-FMRI-BRAIN-GROUNDING    # 179 behavioural + fMRI tests
python3 -m pytest _infra/tests/                                          # 80 infra tests
```

Total: **1,097 verdict atoms** (180 CSV + 917 pytest) reproducing the paper headline in ~55 min on M2 8 GB (dominated by the ~27 min ChillsDB permutation cell and ~26 min PMEmo L5 LOSO bootstrap; measured 2026-05-27, cache mode). To rebuild the cache substrate from the live engine, clone the engine source alongside and run `MI_BUILD_ORACLE=1 pytest 01-R3-… 02-T3-…`.

## Engine SHA verification

```bash
find <engine_root>/Musical_Intelligence -type f -name "*.py" -not -path "*__pycache__*" \
  | sort | xargs -I {} shasum -a 256 {} | awk '{print $1}' | shasum -a 256 | awk '{print $1}'
```

Match against `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88` → engine bit-identical to paper-time freeze.

## License

PolyForm Noncommercial 1.0.0 (research/audit/education unrestricted; commercial use requires separate license).
