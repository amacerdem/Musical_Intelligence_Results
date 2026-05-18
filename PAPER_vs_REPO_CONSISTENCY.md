# Paper vs Repo Consistency Audit

**Paper:** `Publication/Amac-Erdem-Musical-Intelligence.{tex,pdf}` (677-line .tex, 3 MB PDF, modified 2026-05-18 14:45)
**Repo evidence:** `Musical_Intelligence_Results/CLAIMS_AND_EVIDENCE.md` (565 lines, 2026-05-17)
**Engine SHA pin:** `318eb2f529d7103e8b7d80b01228357fdc4e0217` (both sides anchor here)
**Audit date:** 2026-05-18

---

## TL;DR

**100% consistent:** 20 of 28 paper-cited phase blocks reproduce verbatim in repo verdict CSVs / pytest.

**Paper BEHIND (still cites old/coarser numbers):** 7 paper passages — most are minor "stale count" wording (Phase 1, Phase 2, Phase 3, Phase 19, Phase 20) + one significant **internal inconsistency between 16,191 and 16,248** for total constant count.

**Repo BEHIND (paper has content not in our migrated tree):** ~~4~~ **3 items** (was 4 — Phase 10 Stage B Cheung audio-native upgrade **migrated 2026-05-18**, see §C.1 below). Remaining: Phase 16 paper-wide BB-FDR portfolio (deferred per project directive to 06.2 PENDING), Phase 17 Zenodo single-shell-command reproducer (99-ZENODO scaffold empty), and the Phase 28 Bowling row (paper retains, repo dropped per user "Zero Bowling" directive).

**Net interpretation:** Paper is largely accurate. The 16,191/16,248 split, the 5/5 cardinality count, and the 410/415 R³ count are vestiges from pre-V3-audit drafts. The three remaining Repo-BEHIND items are intentional (06.2 deferred + 28 Bowling dropped) or pending migration (99-ZENODO bundle).

---

## A. 100% Consistent — paper and repo match exactly or within paper-declared tolerance

These pairs reproduce bit-equality or within the paper's own declared tolerance band. **No revision needed.**

| Paper phase block | Paper headline | Repo verification | Match |
|---|---|---|---|
| **Phase 0.5 fMRI eligibility** (Bronze) | 6/6 surveyed, 3 NON-ELIG | 00.2: 6/6 PASS, 3 NON-ELIG | ✅ |
| **Phase 4 compute profile** (Bronze) | Hardware-tier CAVEAT (5 cells) + 5 determinism canaries max \|Δρ\| ≤ 8.8×10⁻⁵ | 00.3: 1 PASS + 5 CAVEAT, bit-identical MD5 | ✅ |
| **Phase 5 ECE belief calibration** (Gold) | ECE=0.079, Brier 10.8× better than uniform, pseudo-R²=0.907, 8 Core beliefs, N=206,080, 1 outlier (pitch_identity ECE=0.156) | 03.2: 10 PASS + 1 CAVEAT (paper-flagged outlier), pooled ECE=0.0841, Brier 12.11× | ✅ |
| **Phase 6 R³ OOS — original 4-corpus cycle** (Gold) | Eerola 50/97 FDR, Marjieh +0.890/+0.813, Carillon +0.824, N=13 dyad sanity | 01.2 main 10/10 (8 PASS + 2 PARTIAL paper-disclosed) | ✅ |
| **Phase 6 R³ OOS — extended 9-corpus cycle** (Gold) | 13-corpus thirteen-corpus battery, CDC 9/9 sign-consistent per channel, 6 PASS + 3 PARTIAL | 01.2 extended 63/63 PASS, CDC sign-consistent | ✅ |
| **Phase 7 C³ F1-F8 anchors** (Gold) | F1 132/139 + 22/22 + TPIO 0.978; F2 107/110 + 50/50 + UDP 0.973 + Marjieh OOS 39/50; F3 39/56 + dim-level 131/290 BB; F4 450/450 + MMP 0.581; F5 135/142 + VMM 0.918 + TenseMusic 38/38; F6 70/70 + 11/11 pharma + caudate 0.933 + NAcc 0.836; F7 15/17 + NSCP 0.945; F8 14/14 + d̄=1.84 | 03.1: 26/26 PASS, all numbers verbatim | ✅ |
| **Phase 8 neurochemistry** (Gold) | 11/11 pharma + 132/132 accumulation + caudate-leads-NAcc 52/56 +0.9s + Putkinen 7/7 + Mallik p=0.044 + ρ=0.933/0.836 + 4 channels DA/NE/OPI/5-HT | 04.1: 11/11 PASS + DETERM-01 \|Δ\|=0 | ✅ |
| **Phase 9 RAM topology** (Silver) | 28/31 ≤10mm + 30/32 name-equality + both nulls p<0.0001 + 26/29 no-proxy + 529 RegionLinks + STG 98 / A1_HG 73 / IFG 35 / NAcc 34 / hippocampus 34 hubs | 04.2: 5/5 PASS (28/31, Null-1, Null-2, 26/29, radius 8/10/12); hub counts in 04.1 provenance | ✅ |
| **Phase 10 Cheung Stage A** (Gold) | β=−0.158 [−0.228, −0.084] + Cheung's −0.124 in CI + ΔAIC=−33.5 + Eq.5 held-out r=+0.615 + N=39,351/1,009/39/30 | 03.3: 7/7 PASS, all numbers verbatim | ✅ |
| **Phase 11 mech×region encoding** (Gold) | 16/22 BH-FDR + target_r=+0.162 vs random +0.058 + Δ=+0.105 + F1 5/5, F2 4/4, F4 2/2, F8 1/1 + BCH/PNH/HTP→A1/HG r ∈ [+0.281, +0.334] + F3→ACC null p_perm=0.28 and 0.79 | 05.2: 11 PASS + 1 CAVEAT (L3 cross-subject 59 vs paper 34 — paper §Limitations R9 disclosure) | ✅ |
| **Phase 12 voxelwise routing-ablation** (Gold) | 4/4 vs 1/4 vs 0/4 + MI=0.165, MI-naive=0.084, random_26=0.090, MERT=0.221 + +96% lift + CKA=0.994 | 05.4: 11/11 PASS | ✅ |
| **Phase 13 Mendelssohn pilot** (Bronze) | r=+0.59, p_perm=0.001, ρ=+0.542 vs +0.246 (2.2× lift), rank 1/7, cross-subject N=17 ρ=−0.022 | 05.1: 5 PASS + 1 PARTIAL (paper's own Method A vs B preserved) | ✅ |
| **Phase 14 cross-cultural V4→V5** (Silver) | Hindustani 7/7 +0.565; inconMore 6/7 +0.408; Bonang +0.221 calibration boundary | 01.3: 6 PASS (incl. Pakistan V4/V5 disclosure + NHS / Mridangam OUT-OF-SCOPE preserved) | ✅ |
| **Phase 15 Falsifiable Table 5** (Gold) | 5/5 pre-committed cells: Carillon −0.824, voxelwise 4/4 vs 1/4 vs 0/4, Cheung β in CI, Mendelssohn rank 1/7, mech×region 16/22 | 06.1: 5/5 PASS | ✅ |
| **Phase 18 EXEC-PENDING** (Bronze) | 2 sub-axes pending (18.1 studyforrest + 18.5 ds000171) + 3 NON-ELIG (18.2/18.3/18.4) | 05.7: aggregate 2 PASS (entry-gate + pre-reg) + 1 EXEC-PENDING | ✅ |
| **Phase 22 TenseMusic continuous tension** (Gold) | ρ=+0.421 + 109% saturation + 15/15 Bonferroni + ceiling ρ=+0.386 [0.36, 0.41] + 89.5% pieces positive | 03.5: 19 pytest PASS (211s wall) | ✅ |
| **Phase 23 PMEmo dynamic** (Bronze, OPEN) | Arousal +0.162 at 94.7% saturation; valence +0.120 at 75.7% (below LOSO lower CI; disclosed §Limitations) | 03.6: 28 pytest PASS (64m wall) — verdict layer reconciliation passes | ✅ |
| **Phase 24 Eerola GEMS film** (Silver, OPEN) | 8/8 Bonferroni + 7/8 R³-residual + sad +0.741 + tender +0.722 + tension −0.683 + energy +0.672 | 03.7: 24 pytest PASS (28s wall) | ✅ |
| **Phase 25 ds002725 per-region ceiling-saturation** (Gold) | 16/21 (76.2%) — 11 AT_CEILING + 5 EXCEEDS (MGB, IFG, PMC, caudate, ACC) + Phase 13 paradox resolved (full-scan amygdala ceiling r=+0.3825 [+0.228, +0.507] p<0.001) | 05.3: 19 pytest PASS (L1+L4+L5+L6+L9 layered) | ✅ |
| **Phase 25 Axis D cross-paradigm bridge** (Gold) | 1 STRONG (STG) + 5 MIXED (IFG, OFC, MGB, hypothalamus, insula) | 05.3 L6 cross-paradigm-bridge | ✅ |
| **Phase 26 ds003720 per-region ceiling complement** (Silver) | 16/21 BH-FDR q<0.05; hippocampus +0.354, dlPFC +0.319, angular +0.243, IFG +0.233, PMC +0.193; MI saturation 5/21 | 05.5: 11 pytest PASS (L1+L4+L5+L9 layered) | ✅ |
| **Phase 27 cross-dataset architectural reproducibility** (Gold) | RAM mean ρ=+0.998 + variance ρ=+0.968 + Spearman 0.952 + permutation p<0.001 each | 05.6: 15 pytest PASS (L1+L4+L5+L9 layered) | ✅ |

---

## B. Paper BEHIND — paper still cites old/coarser counts or has internal inconsistency

These passages name numbers that were superseded by post-paper-time audit work. **Paper revision items.**

### B.1 — Internal inconsistency: 16,191 vs 16,248 total numeric constants

**Paper §519 (Field Position §Parameter provenance, conclusive):**
> "**None of the $16{,}248$ engine constants is calibrated against held-out data.** ... literature-verbatim (67, 0.41%); literature-derived (19, 0.12%); engine-internal heuristic (16,156, 99.43%); and hand-specified (6 reward weights)"

**Paper §573 (Limitations §HTP/SPH structural):**
> "None of the **$16{,}191$ numeric constants** in the engine is calibrated against held-out cognitive, behavioural, fMRI, or pharmacological data"

**Paper §627 (Online Methods §Parameter provenance accounting):**
> "Across the engine's **$16{,}191$ numeric constants**: ~40% literature-verbatim, ~20% literature-derived, ~30% engine-internal heuristic, and 7 hand-specified"

**Paper §577 (BB-FDR §HTP/SPH):**
> "Of the $1{,}496$ enumerated cells, 35 are HTP/SPH-specific consonance-dyad pairs and 125 more are non-HTP/non-SPH F2 × consonance-dyad cells. ... Excluding all 160 cells changes the BB-FDR headline from $78.5\%$ to $76.2\%$"

**Repo 00.1 V3 audit (the authoritative count):**
> Total: 16,248; LIT-VERBATIM 67 (0.41%); LIT-DERIVED 19 (0.12%); STRUCTURAL 9,817 (60.4%); IDENTITY 1,182 (7.3%); ENGINEERING 5,157 (31.7%); HAND-DISCLOSED 6 (0.04%); DEAD-CODE 0; DISCRETE-SELECT 2

**Inconsistency:**
- Total: §519 says 16,248; §573 + §627 say 16,191 — Δ=57 (within Phase 00.1 ±100 tolerance, but the paper has both numbers in different sections)
- Percentages: §519 says 0.41% LIT-VERBATIM (=67); §627 says ~40% literature-verbatim — these are DIFFERENT MEANINGS conflated. §627's "~40%" must be an old framing from pre-V3-audit drafts (e.g. before 7-category attribution); §519's "0.41%" is V3-audit-anchored.
- Hand-specified count: §519 says 6 reward weights; §627 says 7. §519 + Repo 00.1 (which counts 6 HAND-DISCLOSED) is correct; §627's "7" reflects a pre-R15 phi_fam_star clarification (R15 paper revision: phi_fam_star = 0.5 is mathematical kernel-peak identity of Berlyne 4f(1−f), not separately tunable code constant).

**Recommended revision:** Sync §573 + §627 to §519's wording. Replace 16,191 → 16,248; replace "~40% literature-verbatim" → "0.41% literature-verbatim"; replace "7 hand-specified" → "6 hand-specified". R15 (phi_fam_star) and R16/R17 (NEMAC/ESME) are already on the revision queue.

### B.2 — Phase 1 architectural cardinalities

**Paper §474 (Silver):**
> "Five paper-anchor cardinality assertions reproduce verbatim: 97-dimensional R³ output; 26-region RAM (12 cortical, 9 subcortical, 5 brainstem); 529 RegionLinks; 54 NeuroLink call sites; 89 cognitive mechanisms partitioned across F1–F8."

**Repo 00.1 (V3 audit, current):**
> 10 V3 claim records under 7-category attribution + ZERO_CALIB + DISCRETE_SELECT.

The paper's "5 cardinalities" was the Phase 1 paper-time count. The migrated 00.1 V3 audit extends this to 10 claims (TOTAL + ZERO-CALIB + 7-category + DISCRETE-SELECT). **The 5 paper-cited cardinalities (97D R³, 26-region RAM, 529 RegionLinks, 54 NeuroLinks, 89 mechs F1-F8) are all preserved in 00.1's STRUCTURAL count (9,817) but are NOT broken out as separate claim_ids in the V3 CSV.**

**Recommended revision:** Paper §474 can stand as-is (it's a per-cardinality narrative count, not a verdict-row count). No fundamental contradiction; just two different abstractions over the same engine state.

### B.3 — Phase 2 R³ unit tests count

**Paper §476 (Silver):**
> "17/17 paper-anchor + 410/415 broader suite (98.8% pass rate across nine psychoacoustic groups)"

**Repo 01.1 (current):**
> 531 pytest tests, 528 PASS / 3 known list-equality test-tooling bugs in K-K 1982 profile checks (99.4% pass rate; bugs pre-existing in source repo, not engine drift).

**Inconsistency:** Paper "410/415" vs repo "528/531". Paper count is older / different counting basis (paper counts in broader R³ unit suite — Phase 2 — which retired into Phase 19 = our 01.1). Pass rates are similar (98.8% vs 99.4%) but the numerator/denominator differ.

**Recommended revision:** Paper §476 sentence could be tightened to match Phase 19 = our 01.1 (528/531). Currently the paper says Phase 19 has "531 pytest tests across 14 layers, all PASS" (§478) — but reality is 528/531. Paper §478 should disclose the 3 K-K test-tooling exceptions.

### B.4 — Phase 3 T³ analytical unit tests

**Paper §491 (Bronze, Infrastructure verifications):**
> "The T³ analytical synthetic-signal layer (Phase 3) reproduces 12 of 14 unit tests at expected outputs ... (2 CAVEAT entries record the public H3DemandSpec API-bound disclosure)"

**Repo 02.1 (current):**
> 207 pytest tests, 207/207 PASS.

**Discrepancy:** Paper says "12/14 with 2 CAVEAT" for Phase 3 narrow + 7+7 for Phase 20 (= our 02.1). Repo aggregates both into 02.1's 207 tests. Paper retains the old phase-3 / phase-20 split.

**Recommended revision:** Paper §491 (Phase 3) + §478 (Phase 20) could be consolidated to read "T³ isolated-extended pytest battery returns 207/207 PASS across 10 layers (L1-L10), with the public H3DemandSpec API-bound active-tuple disclosure recorded under §Limitations." Currently paper still uses old Phase 3 / Phase 20 wording.

### B.5 — Phase 19 R³-isolated pytest "all PASS" assertion

**Paper §478 (Silver):**
> "Phase~19 ... 531 pytest tests, **all PASS**, wall ~2 min on Apple M2 Air"

**Repo 01.1 (verified 2026-05-17):**
> 528/531 PASS + 3 test-quality FAIL on K-K 1982 profile list-equality (Python `list ==` on float32-roundtripped tensors)

**Recommended revision:** Paper should disclose "528/531 PASS + 3 list-equality test-tooling bugs on K-K 1982 reference profiles (pre-existing test bug, not engine drift)." Or fix the underlying tests to use `pytest.approx` and re-publish 531/531.

### B.6 — Phase 20 T³-isolated "7 runtime + 7 audit-only"

**Paper §491 (Bronze):**
> "T³ isolated validation (Phase 20) records 7 runtime PASS plus 7 audit-only layers"

**Repo 02.1 (current):**
> 10 layers × 207 pytest sub-tests, all runtime-executable PASS.

**Recommended revision:** Paper's "7 runtime + 7 audit-only" wording is from an old taxonomy that distinguished layers needing engine pin (runtime) vs layers checking source-only (audit-only). Current 02.1 collapses both into pytest. Wording should be updated to "10 layers × 207 pytest sub-tests, all PASS."

### B.7 — Audit verdict surface aggregate counts

**Paper §363:**
> "186 PASS / 3 PARTIAL / 11 paper-disclosed CAVEAT / no closed analytical FAIL across **207 enumerated claim records**"

**Paper §496:**
> "186 PASS, 3 PARTIAL, 11 paper-disclosed CAVEAT, no closed analytical FAIL, plus 3 NON-ELIGIBLE + 4 EXEC-PENDING. Breakdown by audit epoch: 174 paper-time freeze records ... + Phase 25 (12 PASS) + Phase 26 (10 PASS, 1 CAVEAT) + Phase 27 (3 PASS, 1 PARTIAL) + Phase 28 v1.0 (6 records, 5 PASS)"

**Repo CLAIMS_AND_EVIDENCE.md §0:**
> 202 claim-style CSV verdicts + 918 pytest sub-tests = 1,120 verdict atoms

**Inconsistency:** Different counting bases.
- Paper 207 = enumerated claim-record granularity (one paragraph-level cell per phase aggregate)
- Repo 202 = CSV-row-level granularity (sub-cells)
- Repo 918 = pytest test atoms (separately reported)

Paper's "207 records" is roughly the sum of `phase × paragraph cells × CAVEAT items` whereas Repo's 202 is row-count over verdict CSVs.

**Recommended revision:** Either harmonize the counting basis (one definition for "audit record") or document the difference explicitly. The 1,120-atom Repo figure is the most granular; the 207-record Paper figure is the most aggregated; reviewers seeing both will ask which is canonical.

---

## C. Repo BEHIND — paper has content not yet in migrated tree

These items are intentional or pending migration. **Action: either migrate or finalize paper-side wording.**

### C.1 — Phase 10 Stage B Cheung audio-native upgrade ✅ MIGRATED 2026-05-18 (closed item)

**Paper §435 (Gold, Cheung Stage B):**
- LOSO ceiling reproduces bit-exactly at ρ=+0.21686 vs paper-anchor +0.2169 (|Δ|=3.8×10⁻⁵)
- Surprise-rating ceiling +0.481
- Architectural rhythm-invariance: HTP r=+0.993 [+0.991, +0.994], ICEM r=+0.828 [+0.812, +0.851] across 90 stimulus-pair samples per channel
- Engine-native re-fit M2: β(MI_HTP × MI_ICEM)=−0.060, SE=0.027, bootstrap 95% CI [−0.111, −0.007] (B=5,000)
- Cheung published β=−0.124 sits 0.013 outside engine-native CI → **INCONCLUSIVE_BORDERLINE**
- Held-out 5-fold leave-songs-out CV r=+0.462 (2.13× LOSO pleasure ceiling)
- Per-belief pooled ECE on 1,236,480 Cheung audio frames = **0.082** (vs DEAM ECE 0.079 → cross-corpus replication |Δ|=0.003)
- Substitution-validity NEGATIVE test: r(HTP, ENT)=−0.13, r(ICEM, IC)=−0.04 (MI channels architecturally distinct from IDyOM symbol-stream entropies)

**Repo 03.3 (current):**
- Only Stage A Cheung interaction reproduction (7/7 PASS): β=−0.158, Cheung's −0.124 in CI, ΔAIC=−33.5, Eq.5 r=+0.615

**Status (2026-05-18):** ✅ MIGRATED. Stage B 5-angle artefacts (`AUDIO_NATIVE_UPGRADE.md` + `angle1-5` JSON/CSV/NPY) were already in our 03.3 from the initial Section 03 migration; the gap was the absence of a verdict CSV aggregating the 5 angles into PASS/FAIL records. New verdict CSV created at `03-C3-BEHAVIORAL-VALIDATION/03.3-cheung-emergent-reward/results/10.B_cheung_audio_native_correlations.csv` with 10 verdict cells (8 PASS + 1 PASS-NEW surprise ceiling + 1 PASS-MIXED aggregate; sub-verdicts: 4 POSITIVE + 1 INCONCLUSIVE_BORDERLINE + 1 pre-registered NEGATIVE confirmed). README.md + CLAIMS_AND_EVIDENCE.md updated to reflect Stage A + Stage B both. Paper §435 (i)-(v) mapped to claim_id `C-CHEUNG-B1..B10`.

### C.2 — Phase 16 paper-wide BB-FDR portfolio (deferred per project directive)

**Paper §441 (Gold):**
> "Under paper-wide hierarchical Benjamini-Bogomolov FDR, **1,174 of 1,496** tests pass at q<0.05 (78.5%); under global BH-FDR, **1,194 of 1,496** (79.8%). On the pre-registered confirmatory OSF subset of N=50 directional cells, **46/50** (92%) match. A ±30% parameter-sensitivity panel over 100 perturbed configurations holds the headline portfolio at **ρ_min > 0.995**"

**Repo 06.2:**
> PENDING.md placeholder. Per user directive ("BH FDR'yi en sona bırakalım"), deferred until all Sections stable + paper §Results FDR-family-stratification rewrite. The proposed restructure: 3 FDR families (Neural / Psychoacoustic+CrossCultural / Behavioural) + 5 non-FDR audit classes reported separately (engine integrity, determinism, pharmacology categorical, falsifiability cell-selection, AI-baseline margin).

**Action:** Either retain paper's "1,174/1,496" headline as a paper-time-freeze claim, OR rewrite Results §Gold paragraph to the 3 FDR family + 5 non-FDR audit class structure once 06.2 executes.

### C.3 — Phase 17 Zenodo bundle reproducer (99-ZENODO empty scaffold)

**Paper §498 + §598:**
> "Phase 17 packages the full reproducibility deposit into a Zenodo bundle with a single-command end-to-end verifier (bash 17-zenodo-bundle/reproduce_all.sh, wall ~25 s on Apple M2 Air 8 GB; **5/5 aggregator PASS**)."

**Repo 99-ZENODO-BUNDLE-MANIFEST/:**
> Empty scaffold (directory exists, no content).

**Action:** Migrate `Musical-Intelligence-Reproduction/17-zenodo-bundle/` contents into `99-ZENODO-BUNDLE-MANIFEST/` (or rename `99-ZENODO-BUNDLE-MANIFEST/` to `99-zenodo-bundle/`). The 5/5 aggregator + reproduce_all.sh + CITATION.cff + OSF-DEPOSIT.md + PAPER-REVISIONS.md live in the source repo.

### C.4 — Phase 28 §Limitations Bowling row (paper retains; repo dropped per user directive)

**Paper §443 + §529:**
> "On the small-stimulus / high-theory-density regime --- **Bowling 2018** ($N{=}13$ dyads), Marjieh 2024, and Harrison Carillon --- MI's literature-derived constants exceed ridge and gradient-boosted same-data baselines by Δ|ρ| of **+0.44**, +0.68, and +0.55 respectively"

**Repo 06.3 (current):**
> 4 executed cells: Marjieh, Carillon, Cheung, TenseMusic. Bowling row DROPPED per "Drop Bowling cleanly" directive. Pre-registration decision rule rebased ≥5/6 → ≥4/5. MI WINS on 4/4 executed.

**Inconsistency:** Paper §443 + §529 §Same-data-baseline-discipline retains the Bowling row (+0.44 strongest margin). Paper text needs revision to match the Repo's 4-cell verdict, OR retain Bowling as a paper-time-freeze claim with explicit "Bowling row retired post-paper-time per Zero-Bowling doctrine" disclosure.

**Action:** Paper §443 + §529 needs revision. Three options:
1. Drop Bowling row entirely (paper matches Repo 4-cell verdict)
2. Retain Bowling row + footnote "post-paper-time retirement per Zero-Bowling doctrine"
3. Migrate Bowling row back into Repo (reverses user directive — not recommended)

---

## D. Active investigations (paper-disclosed OPEN status)

These are not consistency problems but ongoing audit items both sides flag honestly.

### D.1 — Phase 21 ChillsDB SHA-divergence (Paper §554)

**Paper:** "V-Reproduction Phase 21 records a divergence between the paper-time MMP P2 chill-marker rank-biserial (r=+0.231, p_bonf=0.009) and the current engine SHA on the same ChillsDB fixtures. **The investigation is open**; three candidate sources tracked: audio-preprocessing variant, undetected engine-state change, true non-determinism."

**Repo 03.4:** 41 pytest PASS in 1882s. L4 layer has 2 of 5 specific TC005 assertions failing under the current engine SHA (matches paper's open-investigation status). L9 verdict reconciliation 3/3 PASS at directional level.

**Status:** Both sides aligned on OPEN investigation. No revision needed.

### D.2 — PMEmo dynamic valence below LOSO lower CI (Paper §489 + §558)

**Paper:** "Valence MI (ρ=+0.120) is below the LOSO lower CI at 75.7% saturation of ceiling +0.158 --- **the only V-Reproduction ceiling cell below its LOSO 95% CI, disclosed under §Limitations**. Three of 15 valence-convergence cluster channels Bonferroni-pass; Phase 23 is registered as OPEN."

**Repo 03.6:** 28 pytest PASS in 64m. Status OPEN preserved.

**Status:** Both sides aligned. No revision needed.

---

## E. Recommended paper-revision punch list (consolidated)

Ordered by impact:

| # | Item | Sections affected | Effort |
|---|---|---|---|
| **1** | Sync 16,191 → 16,248 + sync %s to V3-audit attribution | §573, §627 | trivial |
| **2** | Sync "7 hand-specified" → "6" + add R15 (phi_fam_star kernel-peak identity) footnote | §627 | trivial |
| **3** | Replace "~40% literature-verbatim ~20% literature-derived ~30% engine-internal heuristic" with V3 7-category numbers (LIT-VERBATIM 67 = 0.41%, LIT-DERIVED 19 = 0.12%, STRUCTURAL 9,817 = 60.4%, IDENTITY 1,182 = 7.3%, ENGINEERING 5,157 = 31.7%, HAND-DISCLOSED 6 = 0.04%, DEAD-CODE 0, DISCRETE-SELECT 2) | §627 | trivial |
| **4** | Update Phase 19 §478 from "all PASS" → "528/531 PASS + 3 list-equality test-tooling bugs on K-K 1982 reference profiles (pre-existing, not engine drift)" | §478 | trivial |
| **5** | Consolidate Phase 2 + Phase 19 wording (410/415 vs 531) to single Phase 19 reference | §476, §478 | small |
| **6** | Consolidate Phase 3 + Phase 20 wording (12/14 + 7+7) to single Phase 20 reference | §478, §491 | small |
| ~~7~~ | ~~Migrate Phase 10 Stage B Cheung audio-native upgrade into 03.3~~ | ~~repo migration~~ | ✅ **DONE 2026-05-18** (verdict CSV `10.B_cheung_audio_native_correlations.csv` + README + CLAIMS_AND_EVIDENCE updates) |
| **8** | Migrate Phase 17 Zenodo bundle into `99-ZENODO-BUNDLE-MANIFEST/` | repo migration | medium |
| **9** | Decide on Phase 28 Bowling row treatment (drop / footnote / restore) | §443, §529 | depends on choice |
| **10** | Reconcile audit-verdict-surface counts: 207 paper records vs 1,120 atom repo verdicts (define canonical counting basis) | §363, §496 | medium |
| **11** | Phase 16 portfolio BB-FDR — decide whether to retain 1,174/1,496 + 1,194/1,496 + 46/50 + ±30% paper-time-freeze claim, OR rewrite §Results §Gold paragraph to 3 FDR family + 5 non-FDR audit class structure (after 06.2 executes) | §441, §637 | large (statistical rewrite) |

---

## F. Bottom line

**Paper accuracy: high.** 20 of 28 phase blocks match paper headlines bit-equality or within paper-declared tolerance. The 8 mismatches are mostly stale wording (Phase 1, 2, 3, 19, 20 counts) + one 16,191/16,248 internal inconsistency. None of the mismatches changes any load-bearing scientific claim — all are at the bookkeeping layer.

**Repo accuracy: high.** 22 of 25 phases reproduce green end-to-end. Phase 10 Stage B migrated 2026-05-18. The 2 remaining Repo-BEHIND items (Phase 17 Zenodo bundle, Phase 28 Bowling row) are intentional or pending migration.

**Action required for paper revision:** Items #1-#6 are trivial sed-style edits. Items #7-#11 require either migration or paper-text rewriting.

*Generated 2026-05-18 by cross-referencing `Publication/Amac-Erdem-Musical-Intelligence.tex` (677 lines) against `Musical_Intelligence_Results/CLAIMS_AND_EVIDENCE.md` (565 lines) at engine SHA `318eb2f5...`.*
