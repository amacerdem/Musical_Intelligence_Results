# 24-h18-h25-eerola-film-gems — Standalone Eerola Film-Soundtrack GEMS Verdict

> **Purpose:** Reproduce the paper's Tier-1 Eerola 2011 film-soundtrack finding — 8 GEMS emotion labels each Bonferroni-pass on Set 2 (n=110), 7/8 surviving R³-residual ablation, with **mechanistically specific top channels** that reflect literature-anchored MI mech assignments — **from a fresh clone of the system**, in a single command.
>
> **The empirical claim under test:**
>
> > On the Eerola & Vuoskoski 2011 Set 2 film-soundtrack dataset (110 clips × 8 emotion labels: valence, energy, tension, anger, fear, happy, sad, tender — continuous mean ratings), the frozen MI engine demonstrates Bonferroni-corrected cross-clip Spearman alignment for **all 8 labels** (range |ρ|=0.40 – 0.74, all p_bonf<0.001) with **7/8 labels** retaining significant residual signal after 5-fold CV Ridge α=10.0 R³-residual ablation. Per-label top channels are mechanistically specific: sad↔NEMAC mPFC activation, tender↔DAP familiarity-warmth, tension↔CDMR mismatch-amplitude (negative direction), energy↔AAC heart-rate (cross-paradigm replication of TenseMusic AAC cluster), valence↔SRP liking. Set 1 (n=360, pilot per Eerola 2011) provides supportive cross-clip replication with 4/8 identical top channels (sad/tender/fear/tension cluster).

## Quick reference

| | |
|---|---|
| **Engine SHA** | `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88` |
| **Engine commit** | `318eb2f5` |
| **Paper section** | C³-Paper §Results, FINDINGS_INDEX T1-G |
| **Status** | OPEN (2026-05-13) |
| **Primary headline** | 8/8 GEMS labels Bonferroni-pass; 7/8 R³-residual survive (Set 2, n=110) |
| **Supportive** | 4/8 identical-channel replication on Set 1 (n=360, pilot) |
| **No LOSO ceiling** | Eerola public deposit has no per-rater data |

## Top channels (Set 2, paper baseline)

| Label | Pool | Top channel | ρ | p_bonf | ρ_residual | Bonf orig/res | R³ R² | Verdict |
|---|---|---|---|---|---|---|---|---|
| sad | SADNESS-15 | NEMAC M0:mpfc_activation | **+0.741** | 3×10⁻¹⁹ | +0.430 | 12/15 + 6/15 | 0.36 | STRONG |
| tender | TENDERNESS-15 | DAP P1:familiarity_warmth | **+0.722** | 8×10⁻¹⁸ | +0.447 | 13/15 + 9/15 | 0.22 | STRONG |
| tension | TENSION-15 | CDMR f01:mismatch_amplitude | **−0.683** | 3×10⁻¹⁵ | −0.504 | 7/15 + 4/15 | 0.26 | STRONG |
| energy | AROUSAL-19 | AAC A1:hr | **+0.672** | 2×10⁻¹⁴ | +0.317 | 10/19 + 8/19 | 0.56 | STRONG (acoustic-mediated) |
| anger | ANGER-16 | PNH M0:ratio_complexity_norm | +0.636 | 1×10⁻¹² | +0.146 | 8/16 + 3/16 | 0.27 | moderate residual |
| fear | FEAR-17 | TAR E0:therapeutic | −0.525 | 7×10⁻⁸ | −0.361 | 9/17 + 7/17 | 0.18 | STRONG |
| valence | VALENCE-15 | SRP P1:liking | +0.424 | 6×10⁻⁵ | +0.344 | 8/15 + 4/15 | 0.09 | STRONG (C³-dominant) |
| happy | HAPPY-16 | SRP P0:wanting | +0.397 | 3×10⁻⁴ | +0.091 | 2/16 + 1/16 | 0.14 | weak residual |

## Quick start

```bash
cd <REPO_ROOT>/03-C3-BEHAVIORAL-VALIDATION/03.7-gems-eerola-film
python3 run_all.py --quick   # L1 + L4 + L5 only (~5 min)
# Or fully:
python3 run_all.py           # L1-L9 (~5-10 min — eerola is fast, mean-ratings)
```

## Layer scaffold

| Layer | Description | Wall (M2 base) |
|---|---|---|
| L1 | Engine SHA aggregate integrity + paper-baseline structural checks (8/8 Bonf + 4/8 replication locked) | < 1 s |
| L2 | Eerola Set 1 + Set 2 ratings CSVs (n=360 + n=110) + engine cache files present | < 1 s |
| L3 | Engine cache integrity for 8 critical mech clusters (NEMAC, DAP, CDMR, AAC, SRP, TAR, PNH, VMM) | < 1 s |
| L4 | Label rating distribution sanity + paper-time channel route validation (all 8 top channels resolve) | < 1 s |
| L5 | PRIMARY inline re-run — Set 2 (n=110) 8 labels cross-clip Spearman, top-channel + Bonferroni breadth check | ~1-2 min |
| L9 | Local vs paper-time baseline tolerance check + Set 1↔Set 2 replication validation | < 1 s |

## Why this V-Reproduction package matters

1. **Mechanistic specificity at literature-anchor level.** Each GEMS label maps to an engine mech consistent with published cognitive-neuroscience anchors:
   - sad → mPFC (Janata 2009 default-mode/sad-mood)
   - tender → familiarity-warmth (affiliative-intimacy literature)
   - tension → expectancy-mismatch (Meyer 1956, Lehne 2014)
   - energy → autonomic-arousal (Salimpoor 2011, cross-paradigm TenseMusic AAC)
   - valence → wanting-vs-liking (Berridge 2003)
   
   This is **not lucky correlation** — it is mech-design alignment with published cognitive neuroscience.

2. **emotify-ablation inversion.** On emotify (T1 endorsement paradigm, 400 clips × GEMS), 0/458 BELIEF cells survived R³-residual ablation initially. On eerola Set 2 (T1 mean-rating paradigm), 7/8 labels survive. **Mean-rating fidelity preserves C³ cognitive signal that endorsement-count aggregation collapses** — a methodological insight relevant to paradigm-design decisions in future cognitive-signal validation.

3. **Cross-set replication (Set 2 ↔ Set 1).** 4/8 labels show **identical top channel** across Set 2 (n=110, curated) and Set 1 (n=360, pilot): fear (TAR), sad (NEMAC), tender (DAP), tension (CDMR cluster). Engine prediction is stimulus-driven, not dataset-noise-fit.

## Paper integration

This package backs FINDINGS_INDEX T1-G. C³-Paper §Results + §Discussion. The 7/8 R³-residual survival is the strongest cross-clip GEMS-channel concordance result in the validation portfolio.
