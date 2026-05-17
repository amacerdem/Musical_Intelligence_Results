# Phase 01.2 — Provenance / Chain of Custody

## Source artefacts

### Engine
- HEAD: `318eb2f529d7103e8b7d80b01228357fdc4e0217` (`_infra/manifests/engine_head.json`)
- Module: `Science/Musical_Intelligence/ear/r3/extractor.py` + `groups/a_consonance/group.py`
- API: `R3Extractor.extract(mel, audio, sr).features[0, :, :7]` mean over time

### Reference reproduction (V1)
- `datasets/Validation-V2/F1-Validation/analysis/run_all_r3.py` — V1 was run 2026-03-24, results stored in
  - `datasets/Validation-V2/F1-Validation/results/r3/dyad-anchor_r3.json`
  - `datasets/Validation-V2/F1-Validation/results/r3/eerola_r3.json`
  - `datasets/Validation-V2/F1-Validation/results/r3/marjieh_r3.json`
- V1 covered 13-dyad anchor, Eerola, Marjieh-harmonic. Phase 6 extends to Harrison Carillon (inharmonic) which was NOT in V1.
- Phase 6 re-runs all four datasets through the same canonical R³ path to verify (a) V1 numbers reproduce; (b) Carillon ρ matches paper-reported $-0.824$.

### Datasets (read-only)
| Dataset | Path | SHA-256 (header line) | N |
|---|---|---|---|
| 13-dyad anchor 2018 | `Science/datasets/consonance/dyad_anchor_2018.csv` | (header: `interval,ratio,semitones,mean_rating,sd,n_subjects,source`) | 13 dyads |
| Eerola Exp3 | `Science/datasets/consonance/eerola2021_exp3.csv` | (header: 43 columns starting `"","id","rating",...`) | 617 chords |
| Marjieh 2024 harm | `Science/datasets/consonance/marjieh2024/data-csv/rating_dyh3dd.csv` | (header: `"participant_id","musical_exp","v1","rating"`) | 7,500 ratings → 13 bins |
| Harrison Carillon | `Science/datasets/consonance/harrison2024_carillon/carillon-behavioural-profile.csv` | (header: `type,pitch_interval,pleasantness,pleasantness_se`) | 1,501 rows behavioural profile (sub-sampled) |
| Carillon timbre lower | `Science/datasets/consonance/harrison2024_carillon/lower_bell_spectrum.csv` | 12 partials | – |
| Carillon timbre upper | `Science/datasets/consonance/harrison2024_carillon/upper_bell_spectrum.csv` | 12 partials | – |

Datasets are not copied into Phase 6 folder; `data/README.md` contains pointers only (per V-Reproduction conventions).

## Paper anchor (Musical-Intelligence-corrected-evidence.tex)

| Claim | TeX line | Verbatim quote |
|---|---|---|
| Eerola | 266 | `$\rho_{\text{stumpf}} = -0.581$, $\rho_{\text{autocorr}} = +0.518$, $\rho_{\text{roughness}} = -0.433$; all $p < 10^{-5}$` |
| Marjieh | 267 | `autocorrelation peak reaches $\rho = +0.890$ ($p < 10^{-4}$), with Stumpf fusion at $\rho = -0.769$ and roughness at $\rho = -0.813$` |
| Carillon | 268 | `Stumpf fusion correlates with carillon pleasantness ratings at $\rho = -0.824$, exceeding the development-set magnitude ($-0.797$)` |
| Anti-overfit | 271 + 312 + 438 | `the strongest single piece of anti-overfitting evidence in the validation suite` |
| Table | 280-285 | `Carillon$^{\dagger}$ & OOS & 113 & $-.824$*** & $+.852$*** & $-.731$**` |

## Derived artefacts (this phase produces)

- `results/06_r3_oos_manifest.json` (claim-level)
- `results/eerola_r3.csv` (per-chord 7-feature output)
- `results/marjieh_r3.csv` (13-bin aggregate)
- `results/carillon_r3.csv` (per-interval inharmonic stimulus output)
- `results/dyad_anchor_r3.csv` (sanity-only, recomputed against Phase 2 baseline)
- `figures/forest_oos.png` (4-dataset, 3-channel forest plot — paper Figure 2a OOS panel)
- `04-INTEGRATION-LOG.md` (iterations, if any)
- `02-RESULTS.md` (per-claim verdict)
