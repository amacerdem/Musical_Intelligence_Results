# Audit Summary — Constant-Level Provenance (Final)

**Engine SHA:** `318eb2f5...` (FROZEN 2026-05-15)  
**Aggregate SHA:** `482ade45...`  
**Audit date:** 2026-05-17  
**Protocol:** INVESTIGATION-RULES.md v1.2 (R1-R9 integrated)  
**Agents:** 9 parallel audit agents + Agent 10 reconciliation

---

## Headline

- **16248 numeric constants audited** across the full FROZEN engine tree (`Musical_Intelligence/`).
- **86 literature-anchored** (67 LIT-VERBATIM + 19 LIT-DERIVED = 0.53%) — all in R³/T³ early perceptual front-end + 1 Berlyne kernel coefficient in `brain/reward.py`.
- **6 HAND-SPECIFIED-DISCLOSED** reward weights — see Note on F=6 vs protocol-listed 7 (ESC-A5-1).
- **Zero numeric constants calibrated against held-out cognitive data** — confirms the 2026-05-16 CODE-FIRST doctrine.
- **Engine FROZEN throughout** — no code modifications, SHA preserved.

## Per-agent totals

| Agent | Scope | N | %HIGH | Escalations | Web searches |
|---|---|---:|---:|---:|---:|
| 1 | F1 | 2435 | 99.5% | 3 | 2 |
| 2 | F2+F3 | 3607 | 100.0% | 0 | 4 |
| 3 | F4+F5 | 4883 | 98.7% | 2 | 4 |
| 4 | R³+T³ | 592 | 72.6% | 16 | 12 |
| 5 | F6+reward.py | 1415 | 99.8% | 3 | 3 |
| 6 | F7+F8 | 2998 | 99.0% | 2 | 7 |
| 7 | RAM+regions | 65 | 61.5% | 1 | 3 |
| 8 | cycle/neurochem/beliefs | 40 | 72.5% | 16 | 6 |
| 9 | scaffolding (contracts/scripts/data) | 213 | 98.6% | 3 | 9 |
| **Total** | | **16248** | **98.10%** | **46** | **~50** |

## Final category distribution

| Cat | Name | Count | % | Notes |
|---|---|---:|---:|---|
| A | LIT-VERBATIM | 67 | 0.41% | Mel formula 2595/700 (×18), MIDI A4=440/note=69, KK 24-key profiles, IEC A-weighting, Bark/Traunmüller, Sethares dyad, Stevens sone, Tonnetz 6D — all in `ear/r3/` |
| B | LIT-DERIVED | 19 | 0.12% | Hasson 32-horizon ladder, Plomp-Levelt 25% CB peak, Sethares parametric kernel, Tenney height, parabolic-interp form, Berlyne 4·x·(1-x) — form-LIT analytic derivations |
| C | STRUCTURAL | 9817 | 60.42% | H3DemandSpec positional args, R³ index aliases, mech OUTPUT_DIM, citation years, LayerSpec slice boundaries, MNI tuples, Brodmann area integers — topology / address-space / metadata |
| D | IDENTITY-PLACEHOLDER | 1182 | 7.27% | Unit-interval clamp endpoints, 0.5 BASELINE midpoints, 1.0 multiplicative neutrals, 0.0 additive neutrals — mathematical identities |
| E | ENGINEERING-CHOICE | 5157 | 31.74% | Mixer/blend coefficients, RegionLink/NeuroLink Likert weights, sigmoid gain/midpoint wrappers, predict-equation τ/W_TREND/W_PERIOD/W_CTX, Bayesian gain clamp [0.20,0.80], ε guards (E1) |
| F | HAND-SPECIFIED-DISCLOSED | 6 | 0.04% | Reward weights w_S/w_R/w_E/w_M/g_DA_wanting/g_DA_liking — paper-disclosed in `brain/reward.py`. **6 code-mapping constants, 7 protocol-listed** (phi_fam_star is kernel-peak identity, ESC-A5-1, paper revision R15) |
| G | DEAD-CODE-UNREACHABLE | 0 | 0.00% | No dead-code constants. (`brain/regions/` package is deprecated-unimported but its 65 constants tagged C with `notes` flag per ESC-A7-INFO-1.) |
| **Total** | | **16248** | **100.00%** | |

## E sub-category breakdown (aggregated from agent summaries)

| Sub-cat | Description | Approx count |
|---|---|---:|
| E1 | Numerical stability (ε guards 1e-8 etc.) | ~70 (R³: 61, F7/F8: 3, others scattered) |
| E2 | Clamp/bound operational gates (incl. Bayesian gain clamp [0.20, 0.80]) | ~70 (F7/F8: 47, F6: 13, scaffolding ~10) |
| E3 | Thresholds | ~18 (R³ only) |
| E4 | Mixer weights (incl. RegionLink/NeuroLink Likert + predict-eq W_TREND/W_PERIOD/W_CTX) | ~4,000 (dominant E sub-cat across C³ mechs) |
| E5 | Operational scaling (TAU, sigmoid gain/midpoint, ModelMetadata kw) | ~900 |

*(Sub-cat split estimated from agent §E breakdowns; per-row sub-cat not uniformly tracked.)*

## Key findings


### 1. F = 6, not 7 (ESC-A5-1; paper revision R15)

Agent 5 mapped 6 code constants to the protocol's 7-item F list. The 7th item, `phi_fam_star = 0.5`, is the *mathematical peak position* of the Berlyne familiarity kernel `4·f·(1-f)` (which attains its unit maximum at f = 0.5). There is no separately tunable code parameter for it; the engine never reads a variable named `phi_fam_star`. Tagging one of the two `0.5` literals on `brain/reward.py:83` as F would have been mis-attribution (they are the additive offset and kernel scale). **Paper revision R15:** §Reward should describe `phi_fam_star = 0.5` as a kernel-peak identity, not a 7th disclosed weight.


### 2. NEMAC `_SELF_SELECTED_BOOST = 1.2` documentation defect (ESC-A3-1; paper revision R16)

Agent 3 found NEMAC code comment cites Sakakibara 2025 `d = 0.88` but the paper reports Cohen's **r = 0.880** (correlation, not Cohen's d). The 1.2 multiplier itself is engine operationalization (R9 form-LIT/coeff-author → E PARTIAL). **Paper revision R16:** disclose comment defect in C³-Cognition §Limitations.


### 3. ESME `_ALPHA = 1.5` 'trainable' comment artifact (ESC-A6-2; paper revision R17)

Agent 6 found ESME `_ALPHA = 1.5` carries the word 'trainable' in its inline comment — a developmental artifact predating the zero-calibration doctrine. Under the FROZEN engine SHA `318eb2f5...` no constant is fit. **Paper revision R17:** either disclose the misleading comment in §Limitations or document the constant as 'α = 1.5 author-chosen amplification factor'.


### 4. R8 walker false-positives rejected at scale

AST walker auto-tagged hundreds of constants with `citation_author` based on co-located text:

- Agent 6 (F7/F8): ~750 false-positive walker auto-tags rejected (Zhang, Patel, Ross, Grahn, Crespo-Bojorque, etc.) — **100% rejection rate** to LIT.

- Agent 9 (scaffolding): 8 substring false-positives (e.g. 'ding' from 'padding', 'deco' from 'decode') rejected.

- Agent 8 (cycle): Schultz/Doya/Berridge channel-index co-locations rejected (channel indices are topology, not Schultz-published numbers).

- Doctrine: walker hints are evidence-only; 3-line locality + web search override.


### 5. R9 form-LIT / coefficient-author boundary applied consistently

R9 ('cited paper establishes functional FORM, code re-parameterizes coefficient') was the dominant source of MEDIUM/PARTIAL outcomes across the audit:

- Agent 1: MPG `_ALPHA = 0.70, _BETA = 0.30` (Rupp 2022 posterior-anterior gradient).

- Agent 3: NEMAC `_SELF_SELECTED_BOOST = 1.2` (Sakakibara 2025).

- Agent 4: Bismarck 1974 sharpness re-parameterization; Hasson 32-horizon ladder.

- Agent 5: Berlyne `4.0` in mixer contexts (E) vs kernel-pure context (B).

- Agent 6: PEOM `_TAU = 4.0` (Thaut 2015), ESME `_ALPHA = 1.5` (Criscuolo 2022 NEGATIVE).

- Agent 8: 11 `REFERENCE_VALUES` dict entries (Salimpoor/Aston-Jones/Mallik/Crockett/Blood-Zatorre).

- Total R9 PARTIAL outcomes: **~25** across the audit, all → E (not B). Conservative attribution preserved.


### 6. Berlyne `4.0` consistency note (ESC-A5-2; cross-agent boundary)

Agent 5 tagged `brain/reward.py:83 4.0` as B-PARTIAL (Berlyne kernel pure form). Three other `4.0` instances in F6 mechs (`iucp/extraction.py:86`, `ssps/extraction.py:136` × 2) tagged E because they appear inside multi-term mixer expressions, not as pure normalisation. Boundary documented; reviewer may apply a uniform rule if preferred.


## Paper revision items (consolidated)

| ID | Origin | Item | Paper section |
|---|---|---|---|
| **R14** | Existing | V-Reproduction channel mapping (Marjieh CSV mislabel) | C³-Cognition / Divan §3.1 |
| **R14b** | Existing | V1 → current channel rename (`tonal_clarity` → `stumpf_fusion`) | Methods / §Naming |
| **R15** | ESC-A5-1 (new) | `phi_fam_star = 0.5` is kernel-peak identity, not 7th tunable weight | C³-Reward §Disclosed weights |
| **R16** | ESC-A3-1 (new) | NEMAC code comment `d=0.88` → Sakakibara reports `r=0.880` (Cohen's r, not d) | C³-Cognition §Limitations |
| **R17** | ESC-A6-2 (new) | ESME `_ALPHA = 1.5` 'trainable' comment artifact under zero-calibration doctrine | C³-Cognition §Limitations |
| **R18** | ESC-A7-INFO-1 (new) | `brain/regions/` package is deprecated-unimported; 65 metadata constants are documentation-only | C³-Biology §Implementation note |

## Doctrine attestation

- **Zero numeric calibration confirmed.** Across 16248 numeric constants, zero are fit against held-out cognitive data. The 2 discrete structural-selection cells (HTP-E3, SPH-E3) involve formula-shape selection, not numeric optimization (documented in `2026-05-17_htp-sph-e3-structural-selection-audit.md`).

- **86 literature-anchored constants are traceable.** All POSITIVE web-verified, with the exception of 19 LIT-DERIVED constants that carry PARTIAL outcomes (Hasson 32-horizon ladder, Bismarck sharpness re-param, Plomp-Levelt 25% CB peak, Jiang 7-band cardinality, Berlyne 4·x·(1-x)).

- **Engineering choices are disclosed by location.** All E constants are mech mixer weights, RegionLink/NeuroLink Likert weights, predict-equation τ/W_*, Bayesian gain clamp [0.20, 0.80], or sigmoid wrappers — each documented as author choice by its module-level context.

- **F category is closed at 6** (engine code) / 7 (paper-listed); see R15 for the phi_fam_star reconciliation.

- **Engine FROZEN** at SHA `318eb2f5...`; aggregate SHA `482ade45...`. No code modifications introduced by the audit.


## Confidence summary

- **Overall %HIGH: 98.10%** (15939/16248)  
- **MEDIUM: 1.90%** (309/16248) — concentrated in R³/T³ literature-PARTIAL cells (Agent 4) and RAM MNI tuples (Agent 7) and `REFERENCE_VALUES` dicts (Agent 8)  
- **LOW: 0.0000%** (0/16248)  
- **Escalations: 46** (0.28%) — manual review queue assembled in `escalation_resolutions.md`


## Limitations

1. **46 escalations remain in queue** (0.28% of 16,248). All are documented MEDIUM/PARTIAL within their respective agent outputs; none destabilize the doctrinal headline. The escalations cluster around: 16 in Agent 4 (R³/T³ literature-PARTIAL cells — Hasson/Bismarck/Plomp-Levelt/Jiang/Houtgast/Bidelman) and 16 in Agent 8 (11 R9-PARTIAL `REFERENCE_VALUES` + 5 NEGATIVE-on-stored-value thresholds). See `escalation_resolutions.md` for theme groupings (~7 themes) and recommended manual review actions.

2. **JSON-stored belief priors out of scope.** 131-belief priors in `data/beliefs_registry.json` are not Python source literals; the AST walker does not enumerate them. Their provenance must be audited separately if reviewer requests.

3. **Pattern-batching audit (Rule 6).** Each of the 9 agents enforced per-row independent `reason` strings via dispatch on (kind, dtype, name, value, file). Spot-checks at 500-row checkpoints in each agent confirm no two rows share verbatim reason text. The reconciliation merge preserves per-row independence.

4. **Walker scope boundary.** AST walker captured 16,248 named-position numeric constants. Anonymous expression literals embedded inside multi-term expressions may not all be enumerated — e.g. the BCH 0.81 ceiling cap was enumerated, but some `0.5` midpoints inside `(0.5 + ...)` expressions may not have been. Per-agent verification logs document inventory matches with the canonical `raw_constants_inventory.csv`.

5. **One-shot reconciliation.** Agent 10 did not re-audit constants; it merged + cross-checked. Inconsistencies, if any, are surfaced for manual review (Step 6 of §9).
