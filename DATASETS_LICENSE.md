# Bundled Upstream Datasets — Attribution and Licenses

This deposit (the *MI Reproduction Archive*) ships copies of several upstream
research datasets under `Musical_Intelligence_Results/datasets/` and one file
under `engine_outputs/consonance/`. These were bundled for reviewer
reproducibility convenience — so a replicator does not need to chase down a
dozen different download portals.

**Each bundled dataset remains the intellectual property of its original
authors and is included under its own original license.** The
**PolyForm Noncommercial 1.0.0** license of the MI Reproduction Archive
applies only to MI-authored content (engine outputs, analysis scripts,
verdict tables, documentation). It does **not** override, relicense, or
extend to any bundled upstream dataset.

If you reuse any of these datasets independently of this archive:
1. **Cite the original publication**, not this deposit.
2. **Obtain a fresh copy from the authoritative source** (column 4 below),
   so you receive any subsequent author corrections.
3. **Comply with the upstream license**, not the PolyForm-NC license of the
   surrounding archive.

---

## Bundled datasets

| Dataset | Subdirectory in archive | License | Authoritative source | Primary citation |
|---|---|---|---|---|
| **PMEmo** | `datasets/emotion/PMEmo/` | Academic research use | https://github.com/HuiZhangDB/PMEmo *(verify URL)* | Zhang, K. et al. (2018). "PMEmo: A Dataset for Music Emotion Computing." *ICMR'18*. |
| **ChillsDB** | `datasets/emotion/chillsdb/` | CC-BY 4.0 *(verify)* | *(verify upstream URL — likely OSF or GitHub)* | *Bertonatti et al. / authors of the ChillsDB paper — verify exact citation* |
| **TenseMusic** | `datasets/emotion/TenseMusic/` | *(see upstream LICENSE; no LICENSE file in repo as bundled)* | https://github.com/* — *(verify TenseMusic upstream repo URL)* | Wang et al. (2024). "TenseMusic: An automatic prediction model for musical tension." *(verify venue + DOI)* |
| **DEAM** | `datasets/emotion/DEAM/` | CC BY-NC-SA 4.0 | https://cvml.unige.ch/databases/DEAM/ | Aljanaki, A., Yang, Y.-H. & Soleymani, M. (2017). "Developing a benchmark for emotional analysis of music." *PLOS ONE* 12(3): e0173392. |
| **Emotify** | `datasets/emotion/emotify/` | CC-BY-NC-SA 4.0 *(verify)* | http://www.cs.uu.nl/research/projects/emotify/ *(verify)* | Aljanaki, A., Wiering, F., Veltkamp, R.C. (2016). "Studying emotion induced by music through a crowdsourcing game." *Information Processing & Management* 52(1): 115–128. |
| **Eerola Film Soundtracks** | `datasets/emotion/eerola_film/`, `eerola_film_set2/` | Academic redistribution permitted *(see paper)* | https://www.jyu.fi/hytk/fi/laitokset/mutku/en/research/materials *(verify)* | Eerola, T. & Vuoskoski, J.K. (2011). "A comparison of the discrete and dimensional models of emotion in music." *Psychology of Music* 39(1): 18–49. |
| **Eerola 2021 (Experiment 3)** | `datasets/consonance/eerola2021_exp3.csv` | Paper supplementary | *(verify DOI / supplementary URL)* | Eerola et al. (2021). *(verify exact title + venue)* |
| **Marjieh 2024** | `datasets/consonance/marjieh2024/` | Paper supplementary | *(verify DOI / OSF URL)* | Marjieh, R. et al. (2024). *(verify exact title + venue — likely cross-cultural consonance perception)* |
| **Harrison 2024 (Carillon)** | `datasets/consonance/harrison2024_carillon/` | Paper supplementary | *(verify DOI / OSF URL)* | Harrison, P. et al. (2024). *(verify exact title + venue)* |
| **Bowling 2018 (Consonance targets)** | `engine_outputs/consonance/bowling2018/targets.csv` | Paper supplementary | https://doi.org/10.1073/pnas.1713206115 *(verify)* | Bowling, D.L., Purves, D., Gill, K.Z. (2018). "Vocal similarity predicts the relative attraction of musical chords." *PNAS* 115(1): 216–221 *(verify)*. |

---

## Not bundled — MI-derived analysis outputs

The following subdirectories may share names with upstream datasets but
contain only MI-authored derivative analysis outputs (bootstrap statistics,
regression coefficients, encoding-pipeline pre-extracted MI features,
figure scripts). These are not redistributions of upstream datasets and
fall under the PolyForm-NC license of this archive:

- `datasets/paper-anchors/cheung-reward/` (MI's Cheung-data analysis: `bootstrap_delta_r2.npy`, `coefficients.csv`, `figure.png/svg`)
- `datasets/paper-anchors/{c3-aggregates,cross-cultural,ece-calibration,mech-region,mendelssohn-pilot,neurochemicals,r3-ground-truth,r3-oos,ram-topology,voxelwise-A3,voxelwise-encoding}/` (MI's paper-time intermediate analysis outputs)
- `datasets/reward/cheung2024/` (MI's Cheung 2024 reward analysis outputs)
- `engine_outputs/**/per_frame/*.npz`, `pooled.csv`, `pooled_pct.csv`, `_analysis/per_target__*.csv`, `_meta/*.csv` (all MI engine output and analysis derivatives)

---

## Removal request — for upstream authors

If you are an upstream author and prefer your dataset to be **removed** from
future versions of this deposit, please contact:

- **Amaç Erdem** — amace@bu.edu
- Or open an issue at the MI_Results repository.

Removal in the next version will be prompt and acknowledged in the version
notes. The published v2.0.0 cannot be altered (Zenodo deposits are
immutable once published) but a superseding clean v2.1 can be issued upon
request.

---

## Why bundle at all?

Reproducing the MI Validation Portfolio touches ~13 datasets across ~5
modalities (audio, fMRI, behavioral ratings, neurochemistry, EEG). Asking a
peer reviewer to register for, request access to, and download each one
separately is a 1–2 week obstacle that prevents replication attempts from
happening in practice. Bundling under each upstream's own license keeps the
"6-week post-acceptance replication attempt" feasible in an afternoon.

Future versions may transition to a **fetch-from-source** pointer model
(`scripts/fetch_datasets.sh`) once the MI Reproduction Archive has matured
past the peer-review window.

---

*Last updated: 2026-05-31. Verify and tighten dataset citations / URLs marked
"(verify)" before formal release.*
