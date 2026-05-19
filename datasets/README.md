# Datasets

The repository ships with the paper-time intermediates and small public
fixtures needed to verify the recorded verdicts. The default reproduction
verifier (`python3 _infra/verify_all_phases.py`) reads these vendored
artefacts directly; no external download is required for the headline
verdicts.

## Layout

```
datasets/
├── paper-anchors/              Paper-time anchors organised by SCIENTIFIC PURPOSE (~796 MB)
│   ├── r3-ground-truth/        R³ DEV stimulus and per-group reports (33 MB)
│   ├── c3-aggregates/          F1–F8 mechanism pass-rates and F3 dim-level (~180 KB)
│   ├── bb-fdr/                 Paper-wide 1,496-test BB-FDR registry (~210 KB)
│   ├── mech-region/            ds002725 mechanism × region encoding pipeline + 692 MB pre-extracted MI features
│   ├── voxelwise-encoding/     ds003720 routing-ablation pipeline (Cycle 17) + RunPod ckpt_bold (6.8 MB)
│   ├── cross-cultural/         Cross-cultural anchor reproduction (60 KB)
│   ├── ece-calibration/        ECE belief calibration with Brier decomposition (5.7 MB)
│   ├── voxelwise-A3/           Banded-ridge variance partitioning (5 MB)
│   ├── cheung-reward/          Cheung 2019 emergent reward analysis (350 KB)
│   ├── cardinality/            Numeric constants AST inventory (16 MB)
│   ├── ram-topology/           RAM 28/31 paper-anchor (~120 KB)
│   ├── mendelssohn-pilot/      Single-subject illustrative + cross-subject N=17 (~160 KB)
│   ├── r3-oos/                 R³ out-of-sample consonance (~30 KB)
│   └── neurochemicals/         Pharmacology 11/11 + accumulation 132/132 (~40 KB)
├── consonance/                 Public consonance fixtures (24 MB)
│                                  Eerola 2021 Exp 3,
│                                  Marjieh 2024, Harrison 2024 Carillon
├── emotion/
│   └── DEAM/audio/MEMD_audio/  Five DEAM held-out songs used by Phase 5 ECE
│                                  (song IDs 1034, 1508, 1777, 1896, 1923; 3.5 MB)
└── README.md                   This file
```

**Total vendored: ~823 MB.**

## What is not vendored (optional, larger)

The default reproduction does not require these. They are useful for
extending the analysis or re-deriving from raw sources at a stricter
level than the vendored intermediates allow:

| Dataset | Size | Purpose | Phase |
|---|---|---|---|
| DEAM full corpus (1,802 songs) | ~27 GB | ECE extension to non-held-out songs | 03.2 |
| ds002725 raw BIDS (N=21) | ~2 GB | Phase 05.2 from-BIDS raw rerun | 05.2 |
| ds003720 raw BIDS (N=4) | ~20 GB | Phase 05.4 from-BIDS raw rerun | 05.4 |
| studyforrest 7T music stimulus (40 WAVs) | ~10 MB | Phase 05.7.1 execution | 05.7.1 |
| ds000171 raw BIDS + supplementary audio | ~4 GB | Phase 05.7.5 execution | 05.7.5 |

To fetch any subset:

```bash
bash _infra/download_datasets.sh                     # all
bash _infra/download_datasets.sh --datasets deam     # specific
```

## Licences

| Resource | Licence | Source |
|---|---|---|
| Paper-time anchors | PolyForm Noncommercial 1.0.0 | See repository-root `LICENSE` |
| Vendored engine snapshot | PolyForm Noncommercial 1.0.0 | See repository-root `LICENSE`; engine SHA pin in `_infra/manifests/engine_head.json` |
| DEAM | CC BY-NC-SA 4.0 | Aljanaki, Yang, Soleymani 2017, *PLoS ONE* |
| Eerola 2021 Exp 3 | CC BY 4.0 | Eerola, Lahdelma 2021, *Music Perception* |
| Marjieh 2024 data-csv | CC BY 4.0 | Marjieh et al. 2024, *Nature Communications* |
| Harrison 2024 Carillon | CC BY 4.0 | Harrison et al. 2024, *iScience* |
| ds002725 | CC0 | OpenNeuro public domain |
| ds003720 | CC0 | OpenNeuro public domain |
| studyforrest | PDDL | Hanke et al. 2014–2016, *Sci. Data* |
| ds000171 | CC0 | OpenNeuro public domain (supplementary audio licensed separately by Lepping et al. 2016) |

## Maintainer-only: re-vendor from a parent checkout

To regenerate the vendored anchors from an upstream Science/ tree:

```bash
bash _infra/vendor_paper_capture.sh
```

This is the maintainer's bootstrap script. External collaborators do
not need to run it; the vendored artefacts are committed to the
repository.
