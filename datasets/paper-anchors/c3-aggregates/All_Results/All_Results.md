# MI Complete Validation Results — Master Document (v2)

**Generated:** 2026-04-09 | **Revised:** Primary dataset audit applied
**Source:** Science/results/ (all subdirectories, exhaustive extraction)
**Engine:** R³ v1.0.0 FROZEN · H³ v1.0.0 FROZEN · C³ Kernel v4.0

> **Important:** Each mechanism is reported against its **correct primary domain**. Bowling 2018 is only primary for F1 Sensory and F5 Emotion. Cross-domain Bowling scores are noted where available but not treated as primary evidence.

---

## 1. R³ — Early Perceptual Front-End (97D, 9 Groups)

| Metric | Value |
|--------|-------|
| Total tests | 415 |
| Pass | 410 |
| XFail | 5 |
| Fail | 0 |
| Bugs found & fixed | 6 |
| Pass rate | 98.8% |

### Per-Group

| Group | D | Tests | Pass | XF | Bugs | Best ρ | Primary Dataset |
|-------|---|-------|------|----|------|--------|----------------|
| A Consonance | 7 | 68 | 68 | 0 | 0 | stumpf +0.885*** | Bowling (N=13) |
| B Energy | 5 | 48 | 48 | 0 | 3 | dynamics +1.000*** | Bowling + Stevens' |
| C Timbre | 9 | 40 | 36 | 4 | 1 | warmth +0.402 (ns) | Grey 1977 |
| D Change | 4 | 45 | 45 | 0 | 0 | entropy analytical | Information theory |
| F Pitch | 16 | 33 | 33 | 0 | 0 | 7/12 keys ρ>0.40 | Krumhansl 1982 |
| G Rhythm | 10 | 33 | 33 | 0 | 2 | tempo +1.000*** | GTZAN BPM |
| H Harmony | 12 | 33 | 32 | 1 | 0 | clarity CI [0.45,0.53] | Krumhansl profiles |
| J Timbre+ | 20 | 48 | 48 | 0 | 0 | MFCC cosine 0.995 | 20 instruments |
| K Modulation | 14 | 67 | 67 | 0 | 0 | sharpness glock>cello | Zwicker / IEC 61672 |

### R³ OOS Validation (frozen weights)

| Dataset | Role | N | stumpf ρ | autocorr ρ | rough ρ | FDR dims |
|---------|------|---|----------|------------|---------|----------|
| Bowling 2018 | DEV | 13 | −0.797** | +0.912*** | −0.885*** | — |
| Eerola Exp3 | OOS | 617 | −0.581*** | +0.518*** | −0.433*** | 50/97 |
| Marjieh 2024 | OOS | 7,500 | −0.769** | +0.890*** | −0.813*** | — |
| Harrison Carillon | OOS | 113 | −0.824***† | +0.852*** | −0.731** | — |

†Exceeds development-set correlation

---

## 2. H³ — Temporal Morphology (19/19 PASS, 100%)

| Test | Metric | Value |
|------|--------|-------|
| M0 constant | stability | 0.1234 |
| M18 ramp trend | perfect | 1.0000 |
| Silence max | <0.15 | 0.1192 |
| Recency ratio | newest/oldest | 20.1× |
| L0≠L1 asymmetry | diff | 0.0126 |
| L2 between L0,L1 | integration | 0.2876 |
| M14 120BPM pulse | periodicity | 0.6403 |
| Reproducibility | max_diff | 0.0 |
| Demand sparsity | matches | 3/3 |

---

## 3. C³ Functions — PRIMARY DOMAIN RESULTS

### F1 Sensory (12 mech, 139D) — Primary: Bowling 2018

| Mechanism | Dims | Sig | FDR Bel | Best ρ | f² |
|-----------|------|-----|---------|--------|-----|
| BCH | 16 | 15/16 | 4/4 | +0.956 | 10.631 |
| PNH | 11 | 11/11 | 5/5 | +0.934 | 6.842 |
| CSG | 12 | 11/12 | 1/1 | +0.885 | 3.599 |
| MPG | 10 | 10/10 | 2/2 | +0.912 | 4.949 |
| TPRD | 10 | 8/10 | — | −0.934 | 6.842 |
| SDED | 10 | 10/10 | 1/1 | −0.923 | 5.760 |
| SDNPS | 10 | 10/10 | — | +0.934 | 6.842 |
| TPIO | 10 | 10/10 | — | **+0.978** | **22.003** |
| MIAA | 11 | 11/11 | 2/2 | +0.940 | 7.531 |
| STAI | 12 | 12/12 | 3/3 | +0.962 | 12.255 |
| PSCL | 16 | 14/16 | 2/2 | +0.934 | 6.842 |
| PCCR | 11 | 10/11 | 2/2 | +0.962 | 12.255 |
| **Total** | **139** | **132/139 (95.0%)** | **22/22 (100%)** | | |

### F2 Prediction (10 mech, 110D) — Primary: Mixed (correct per mechanism)

| Mechanism | Dims | Primary Dataset | Primary Sig | Bowling Sig | Best ρ (primary) |
|-----------|------|----------------|-------------|-------------|-----------------|
| HTP | 12 | IDyOMpy Bach | surprise tracking | 12/12 | +0.791 |
| SPH | 14 | TenseMusic | tension ρ=0.292 | 14/14 | +0.951 |
| ICEM | 13 | DEAM arousal | 6/6 FDR | 12/13 | +0.901 |
| PWUP | 10 | QM2020 entropy | precision tracking | 10/10 | +0.923 |
| WMED | 11 | groove_midi | 5/5 FDR (Marjieh OOS) | 10/11 | +0.868 |
| UDP | 10 | DEAM+Ferreri | 5/5 FDR, OOS +0.574 | 9/10 | **+0.973** |
| CHPI | 11 | Eerola+cross-cultural | 5/5 FDR (Marjieh OOS) | 11/11 | +0.962 |
| IGFE | 9 | groove_midi | 5/5 FDR (Marjieh OOS) | 9/9 | +0.883 |
| MAA | 10 | cross-cultural+DEAM | 4/5 (Marjieh OOS) | 10/10 | +0.937 |
| PSH | 10 | IDyOMpy+TenseMusic | 3/5 (Marjieh OOS) | 10/10 | +0.912 |
| **Total** | **110** | | | **107/110 (97.3%)** | **50/50 FDR** |

**OOS (Marjieh 2024, N=151):** 39/50 beliefs sig (78%), 3 mechs 5/5 (WMED, CHPI, IGFE)

### F3 Attention (12 mech, 122D) — Primary: groove_midi / attention stimuli

| Mechanism | Dims | Primary Dataset | Primary FDR | Bowling Sig | Primary Best ρ |
|-----------|------|----------------|-------------|-------------|---------------|
| SNEM | 12 | groove_midi BPM | **5/5 (100%)** | 0/12 | +0.522 |
| IACM | 11 | attention stimuli | **3/4 (75%)** | 11/11 | +0.951 |
| BARM | 10 | groove_midi BPM | **5/5 (100%)** | 3/10 | −0.714 |
| STANM | 11 | TenseMusic | **1/5 (20%)** | 2/11 | +0.588 |
| AACM | 10 | PMEmo aesthetic | **2/2 (100%)** | 5/10 | +0.907 |
| AMSS | 11 | attention stimuli | **4/5 (80%)** | 6/11 | +0.758 |
| ETAM | 11 | groove_midi BPM | **2/5 (40%)** | 4/11 | +0.841 |
| DGTP | 9 | groove_midi BPM | **5/5 (100%)** | 3/9 | +0.687 |
| SDL | 9 | TenseMusic | **0/5 (0%)** | 3/9 | −0.665 |
| NEWMD | 10 | groove_midi BPM | **5/5 (100%)** | 3/10 | +0.736 |
| IGFE | 9 | groove_midi BPM | **3/5 (60%)** | 4/9 | −0.929 |
| PWSM | 9 | attention stimuli | **4/5 (80%)** | 4/9 | −0.879 |
| **Total** | **122** | | **39/56 (70%)** | 48/122 (39%) | |

**Note:** Bowling 39% is cross-domain artifact. Primary domain 70% is the correct number.

### F4 Memory (15 mech, 159D) — Primary: DEAM dynamic tracking

| Mechanism | Dims | DEAM Dynamic (30 songs) | Bowling Sig | Best Dynamic |ρ| |
|-----------|------|------------------------|-------------|----------------|
| MEAMN | 12 | **30/30 PASS** | 11/12 | 0.475 (TenseMusic) |
| MMP | 12 | **30/30 PASS** | 5/12 | **0.581** (highest) |
| PNH | 11 | **30/30 PASS** | 9/11 | — |
| HCMC | 11 | **30/30 PASS** | 9/11 | — |
| MSPBA | 11 | **30/30 PASS** | 9/11 | — |
| PMIM | 11 | **30/30 PASS** | 9/11 | — |
| RASN | 11 | **30/30 PASS** | 7/11 | — |
| OII | 10 | **30/30 PASS** | 5/10 | — |
| RIRI | 10 | **30/30 PASS** | 10/10 | — |
| CMAPCC | 10 | **30/30 PASS** | 8/10 | — |
| CDEM | 10 | **30/30 PASS** | 10/10 | — |
| CSSL | 10 | **30/30 PASS** | 7/10 | — |
| DMMS | 10 | **30/30 PASS** | 8/10 | — |
| TPRD | 10 | **30/30 PASS** | 8/10 | — |
| VRIAP | 10 | **30/30 PASS** | 9/10 | — |
| **Total** | **159** | **15/15 × 30/30 = 450/450** | ~134/159 | |

**Primary result: 450/450 DEAM dynamic tests PASS (100%)**

### F5 Emotion (12 mech, 142D) — Primary: Bowling + DEAM emotion

| Mechanism | Dims | Sig | Best ρ | f² | DEAM sig |
|-----------|------|-----|--------|-----|----------|
| SRP | 19 | 19/19 | +0.940 | 7.531 | — |
| AAC | 14 | 14/14 | +0.923 | 5.760 | — |
| VMM | 12 | 11/12 | +0.918 | 5.327 | 6/6 valence |
| STAI | 12 | 12/12 | +0.951 | 9.367 | 20-22/30 |ρ|>0.1 |
| PUPF | 12 | 11/12 | −0.934 | 6.842 | — |
| CLAM | 11 | 10/11 | +0.929 | 6.259 | — |
| MAD | 11 | 10/11 | +0.923 | 5.760 | — |
| NEMAC | 11 | 11/11 | +0.912 | 4.949 | — |
| DAP | 10 | 10/10 | +0.923 | 5.760 | — |
| CMAT | 10 | 9/10 | +0.885 | 3.599 | — |
| TAR | 10 | 9/10 | +0.885 | 3.599 | — |
| MAA | 10 | 9/10 | +0.962 | 12.255 | — |
| **Total** | **142** | **135/142 (95.1%)** | | | |

**VMM highlights:** perceived_happy ρ=+0.918***, TenseMusic 38/38 pieces |ρ|>0.1

### F6 Reward (10 mech, 70D) — Primary: Pharmacological + DEAM

| Mechanism | Dims | Primary Dataset | Primary Evidence | Bowling | Best ρ |
|-----------|------|----------------|-----------------|---------|--------|
| DAED | 8 | **Salimpoor PET + Ferreri pharma** | caudate leads 52/56 (93%), levo>plac>risp | 8/8 | +0.912 |
| MORMR | 7 | **Blood & Zatorre chills fMRI** | chills d=8.61, Putkinen 7/7 PET | 7/7 | +0.923 |
| RPEM | 8 | **DEAM + Bowling** | RPE consonant vs dissonant d=3.59 | 8/8 | +0.896 |
| IUCP | 6 | **DEAM complexity** | inverted-U confirmed | 6/6 | +0.912 |
| MCCN | 7 | **B&Z chills + Chabin EEG** | theta prefrontal d=2.04 | 7/7 | +0.830 |
| MEAMR | 6 | **DEAM familiarity** | nostalgia d=3.71 | 6/6 | +0.940 |
| SSRI | 11 | **DEAM social** | synchrony d=4.21 | 11/11 | +0.912 |
| LDAC | 6 | **Bowling + DEAM** | dual-domain | 6/6 | +0.912 |
| IOTMS | 5 | **Putkinen PET** | MOR d=5.34 | 5/5 | +0.923 |
| SSPS | 6 | **DEAM (Cheung/Gold)** | saddle d=3.05 | 6/6 | +0.797 |
| **Total** | **70** | | | **70/70 (100%)** | |

**Key pharmacological results:**
- Ferreri 2019: levodopa > placebo > risperidone CONFIRMED
- Salimpoor replication: antic_da↔caudate ρ=+0.933, consum_da↔nacc ρ=+0.836
- Putkinen PET μ-opioid: 7/7 regions MATCH
- Mallik chills > neutral: p=0.044

### F7 Motor (12 mech, 132D) — Primary: groove_midi

| Mechanism | Dims | groove_midi Primary | Bowling (cross-domain) | Best ρ (primary) |
|-----------|------|--------------------|-----------------------|-----------------|
| PEOM | 11 | 4/5 FDR | 10/11 | +0.912 |
| HMCE | 11 | **6/6 FDR** | 11/11 | +0.912 |
| MSR | 11 | strong | 11/11 | +0.890 |
| GSSM | 11 | strong | 10/11 | +0.912 |
| HGSIC | 11 | **5/6 FDR** | 10/11 | +0.934 |
| ASAP | 11 | strong | 10/11 | +0.890 |
| DDSMI | 11 | strong | 10/11 | +0.896 |
| SPMC | 11 | strong | 10/11 | +0.907 |
| VRMSME | 11 | strong | 11/11 | +0.934 |
| CTBB | 11 | strong | 11/11 | +0.890 |
| STC | 11 | strong | 10/11 | +0.923 |
| NSCP | 11 | strong | 10/11 | +0.945 |
| **Total** | **132** | **15/17 FDR** | ~124/132 (94%) | |

**Note:** Bowling 94% is misleadingly high — shared R³ upstream features inflate consonance correlation. groove_midi is the correct motor domain test.

### F8 Learning (6 mech, 67D) — Primary: QM2020 + Musician Meta

| Mechanism | Dims | Primary Dataset | Primary Evidence | Bowling | Best ρ |
|-----------|------|----------------|-----------------|---------|--------|
| EDNR | 10 | Musician meta (N=3005) | Gray matter d=1.59, CC FA d=1.33 | 9/10 | +0.890 |
| TSCP | 10 | Pantev 2001 (N=16) | Timbre N1m F=28.55, p=0.00008 | 10/10 | +0.945 |
| CDMR | 11 | QM2020 (N=2100) | Consonance MMN d=1.53 | 11/11 | +0.885 |
| SLEE | 13 | QM2020 (N=4700) | Accuracy Δ=+0.182 (mus vs non) | 13/13 | +0.885 |
| ESME | 11 | Musician meta (N=3005) | MMN d=1.53 | 11/11 | +0.918 |
| ECT | 12 | Musician meta | Compartmentalization g=−1.09 | 12/12 | +0.890 |
| **Total** | **67** | | **Grand mean d=1.84** | **66/67 (98.5%)** | **14/14 FDR** |

**Musician meta-analysis highlights:**
- Frequency discrimination: d=2.74
- Pitch memory: d=2.43
- Gap detection: d=2.03
- Rhythm sync: d=1.82

---

## 4. Region Activation Map (26D RAM)

| Metric | Value |
|--------|-------|
| Total RegionLinks | 529 |
| Canonical matches | 529/529 (100%) |
| RAM accumulation tests | 445/445 (100%) |
| fMRI studies matched | 7/7 (100%) |
| Region predictions | 30/32 (93.8%) |
| Total subjects | 104 |

### fMRI Cross-Validation

| Study | Year | N | Contrast | Match |
|-------|------|---|----------|-------|
| Blood & Zatorre | 2001 | 10 | Chills > no-chills | 7/7 |
| Salimpoor et al. | 2013 | 19 | High > low reward | 5/6 |
| Grahn & Brett | 2007 | 14 | Beat > non-beat | 3/3 |
| Koelsch et al. | 2005 | 18 | Irregular > regular | 2/2 |
| Brattico et al. | 2011 | 16 | Happy vs sad | 3/3 |
| Zatorre & Halpern | 2005 | 12 | Imagery > rest | 3/3 |
| Putkinen et al. | 2025 | 15 | Music μ-opioid PET | 7/7 |

### Emergent Convergence Hubs
- STG: 98 links (highest)
- A1/HG: 73
- IFG: 35
- NAcc: 34
- hippocampus: 34

---

## 5. Neurochemical System (4D)

| Metric | Value |
|--------|-------|
| Total NeuroLinks | 48 |
| Accumulation tests | 132/132 (100%) |
| Pharmacological tests | 11/11 (100%) |
| DA temporal (56 tracks) | caudate leads 52/56 (93%) |
| antic_da ↔ caudate ρ | +0.933 |
| consum_da ↔ nacc ρ | +0.836 |
| Temporal lag | +0.9 s |
| Putkinen PET match | 7/7 (100%) |
| Mallik chills > neutral | p=0.044 |

---

## 6. Sensitivity & Robustness

### PCA (F1 139D)
- 95% variance: 6 components
- Redundant pairs (|ρ|>0.90): 5/66 (7.6%)

### Reward Sensitivity (±30%, 100 configs)
- Rank preservation ρ: mean 0.9991, min 0.9950
- All ρ > 0.95: 100/100 (100%)

### Bug Fixes
- 3 critical bugs, 14/14 verification tests PASS

---

## 7. Primary Dataset Audit Summary

| Fn | Correct Primary | Bowling Primary? | Key Metric |
|----|----------------|-----------------|-----------|
| F1 | Bowling 2018 | **YES (12/12)** | 132/139 sig (95%) |
| F2 | Mixed (correct) | Partially | 107/110 sig (97%), 50/50 FDR |
| F3 | groove_midi / attention | **NO (9/12)** | Primary FDR 39/56 (70%) |
| F4 | DEAM dynamic | **NO (15/15)** | 450/450 dynamic (100%) |
| F5 | Bowling + DEAM | **YES (11/12)** | 135/142 sig (95%) |
| F6 | Pharma + DEAM | **Partially** | 70/70 sig, 11/11 pharma |
| F7 | groove_midi | **NO (12/12)** | 15/17 FDR (groove) |
| F8 | QM2020 / meta | **NO (6/6)** | d=1.84 mean, 14/14 FDR |

### Correctly Assessed: 51/89 (57%)
### Bowling Misleading: 38/89 (43%) — report primary domain instead

---

## 8. Grand Summary (Corrected)

| Layer | Primary Test | Result |
|-------|-------------|--------|
| R³ | 415 unit tests + 5 OOS datasets | 410/415 (98.8%), OOS generalises |
| H³ | 19 independent tests | 19/19 (100%) |
| F1 Sensory | Bowling consonance | 132/139 sig (95%), 22/22 FDR |
| F2 Prediction | Mixed domain | 107/110 sig (97%), 50/50 FDR |
| F3 Attention | groove_midi + attention | 39/56 primary FDR (70%) |
| F4 Memory | DEAM dynamic | 450/450 (100%) |
| F5 Emotion | Bowling + DEAM | 135/142 sig (95%) |
| F6 Reward | Pharmacological | 11/11 pharma, 70/70 Bowling |
| F7 Motor | groove_midi | 15/17 FDR |
| F8 Learning | QM2020 + meta | 14/14 FDR, d=1.84 |
| RAM | 7 fMRI studies | 30/32 match (93.8%) |
| Neuro | Pharma + PET | 11/11 pharma, 7/7 PET, 52/56 DA |
| Reward sensitivity | ±30% perturbation | ρ>0.995 (100/100) |
