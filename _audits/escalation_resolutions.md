# Escalation Resolutions (Draft for Manual Review)

**Compiled by:** Agent 10 reconciliation, 2026-05-17  
**Source:** 9 agent escalation queues merged + theme-grouped  
**Total escalated constants:** 46 (0.28% of 16248)  
**Engine SHA:** `318eb2f5...` (FROZEN)

---

## Theme groupings

### Theme 1 — phi_fam_star kernel identity (paper revision R15)

- **ESC-A5-1** (Agent 5): protocol enumerates 7 F-list items; engine has 6 code-mapping constants. `phi_fam_star = 0.5` is the arg-max of `4f(1-f)` and is never a named code variable.

  - Recommended action: paper §Reward to clarify `phi_fam_star = 0.5` as kernel-peak identity (mathematical), not a 7th tunable weight. NO engine change.


### Theme 2 — NEMAC documentation defect (paper revision R16)

- **ESC-A3-1 / ESC-A3-2** (Agent 3): NEMAC `_SELF_SELECTED_BOOST = 1.2` × 2 occurrences (extraction.py + temporal_integration.py). Code comment cites Sakakibara 2025 `d=0.88`; paper reports Cohen's `r=0.880`. The 1.2 multiplier itself is engine operationalization (R9).

  - Recommended action: confirm E PARTIAL classification; disclose comment metric mislabel in C³-Cognition §Limitations. NO engine change.


### Theme 3 — ESME _ALPHA naming/comment (paper revision R17)

- **ESC-A6-2** (Agent 6): ESME `_ALPHA = 1.5` comment uses the word 'trainable' — developmental artifact, no longer accurate under FROZEN engine + zero-calibration doctrine.

  - Recommended action: confirm E classification; disclose stale comment text in C³-Cognition §Limitations OR document constant as 'α = 1.5 author-chosen amplification factor operationalising Pantev/Koelsch/Criscuolo expertise gradient principle'. NO engine change.


### Theme 4 — R9 form-LIT / coefficient-author boundary cases

Total R9 escalations across audit: ~25. All resolved as **E with PARTIAL verification outcome** (not B). Doctrine consistent.

- **ESC-F1-002, ESC-F1-003** (Agent 1): MPG `_ALPHA = 0.70` / `_BETA = 0.30` — Rupp 2022 posterior-anterior gradient. Form-LIT, coefficients author-re-parameterized.

- **ESC-A4-***  (Agent 4): Bismarck 1974 Zwicker sharpness `0.066·exp(0.171·(z+1))` vs published `0.2·exp(0.308·(z-15))·0.8` — same form, different coefficients. PARTIAL.

- **ESC-A4-** (Agent 4): Hasson 32-horizon ladder — concept-LIT, ladder values author-derived. PARTIAL.

- **ESC-A4-** (Agent 4): Jiang 2002 7-band cardinality only; Houtgast 1985 / Eyben 2015 modulation rate ladder convention only; Bidelman 65-cent FFR precision PARTIAL.

- **ESC-A5-2** (Agent 5): Berlyne `4·x·(1-x)` kernel `4.0` in `brain/reward.py:83` tagged B-PARTIAL (pure kernel form). Three other `4.0` instances in F6 mechs tagged E because embedded in multi-term mixer.

- **ESC-A6-1** (Agent 6): PEOM `_TAU = 4.0` — Thaut 2015 period entrainment dP/dt model. Form-LIT, coefficient author-re-param.

- **ESC-A8-* × 11** (Agent 8): `REFERENCE_VALUES` dict entries (Salimpoor BP_ND 0.78/0.88/0.35; Ferreri 0.92/0.28; Aston-Jones 0.50/0.75/0.35; Mallik 0.85/0.30/0.40; Crockett 0.50/0.70/0.30). All form-LIT, coefficients author-renormalized to [0, 1] for sensitivity-panel documentation. **Mitigation:** dicts are not consumed by the runtime cycle — documentation-only.

- **ESC-A9-* × 3** (Agent 9): scripts/runpod_train.py R9 boundary cases (rolloff 0.85, modulation rate ladder convention, horizon ladder duplicate).

  - Recommended global action: confirm all as E PARTIAL; disclose form-LIT/coefficient-author boundary in §Parameter provenance (S1 of master MI paper).


### Theme 5 — BCH 0.81 ceiling cap numeric coincidence

- **ESC-F1-001** (Agent 1): BCH E3 ceiling cap `0.81 * (e0 + e1) / 2.0` numerically matches Bidelman 2009 r=0.81. Role is a clamp, not a parameter reproduction. Per context_brief §7-1 doctrine, ceiling caps are E.

  - Recommended action: confirm E (not A); disclose numeric coincidence in §Parameter provenance if reviewer requests. NO engine change.


### Theme 6 — RAM MNI tuples (Agent 7)

- **ESC-A7-1** (Agent 7): NAcc MNI (10, 12, -8) cannot bit-exact verify to Salimpoor 2011 via 2 web-search attempts. Tagged C MEDIUM.

  - Recommended action: manual Supplementary Table check; if Salimpoor publishes a different NAcc centroid, decide whether to keep MI's stitched representative (C) or re-tag (E5 if author-chosen). Either way, NO engine change.

- **ESC-A7-SCOPE-1**: 529 RegionLink weights are in C³ mech `__init__.py` files (Agents 1-6 scope), not Agent 7. Confirmed across agent CSVs as uniformly E4 mixer.

- **ESC-A7-INFO-1**: `brain/regions/` package is deprecated-unimported (zero grep hits across engine). Agent 7 chose C with notes flag over G dead-code. Manual review: confirm interpretation. Paper revision R18 candidate.


### Theme 7 — Cycle/neurochem operational thresholds (Agent 8 NEGATIVE-on-stored-value cases)

- **ESC-A8-* × 5** (Agent 8): BASELINE 0.5, phasic threshold 0.6, robust normalization percentiles 2.0/98.0, dynamic range floor 0.01. NEGATIVE on stored-value web search — i.e. these are engine-convention thresholds not literature-published.

  - Recommended action: confirm E (E2/E3) classification. Disclose in §Parameter provenance. NO engine change.


## Summary table

| Agent | Escalations | Theme(s) |
|---|---:|---|
| 1 (F1) | 3 | R9 MPG ALPHA/BETA; BCH 0.81 ceiling |
| 2 (F2+F3) | 0 | — |
| 3 (F4+F5) | 2 | R16 NEMAC documentation defect |
| 4 (R³+T³) | 16 | R9 Bismarck/Hasson/Jiang/Houtgast/Bidelman PARTIALs |
| 5 (F6+reward) | 4 | R15 phi_fam_star; ESC-A5-2 Berlyne consistency; SSRI 3.0 clamp; KAPPA_SOCIAL R9 |
| 6 (F7+F8) | 2 | R17 ESME _ALPHA; PEOM _TAU=4.0 Thaut |
| 7 (regions) | 3 | NAcc MNI verification; scope reconciliation; deprecated-unimported package |
| 8 (cycle/neurochem) | 16 | 11 R9 REFERENCE_VALUES + 5 NEGATIVE-on-stored-value thresholds |
| 9 (scaffolding) | 3 | R9 rolloff/modulation/horizon in runpod_train.py |
| **Total** | **46** | |


## Recommended bulk action

All ~30 escalations are **MEDIUM/PARTIAL** — none warrant LIT upgrades and none disturb the zero-calibration doctrine. The bulk action is:

1. Confirm category attributions in next reviewer pass (no re-categorization needed; agents already converged on conservative E).

2. Add §Parameter provenance / §Limitations disclosures for R15 (phi_fam_star), R16 (NEMAC), R17 (ESME), R18 (deprecated regions package).

3. Cite R9 form-LIT / coefficient-author doctrine in the master MI.tex §Parameter provenance to pre-empt reviewer 'why isn't this LIT-DERIVED' questions.

4. Make ESC-A5-2 (Berlyne consistency) explicit: pure-kernel context = B PARTIAL, embedded-mixer context = E. One-line table in §Reward.
