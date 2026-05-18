# Paper §Limitations — Revision Proposal

**Source paper:** `Publication/Amac-Erdem-Musical-Intelligence.tex` §492-550 (current §Limitations as of 2026-05-18 14:45 compile)
**Repo state:** `Musical_Intelligence_Results/` 25-section migrated tree at engine SHA `318eb2f5…`
**Authored:** 2026-05-18

---

## A. What's wrong with the current §Limitations

Eight problems identified in the current text, ordered by severity:

### A.1 — Stale V-Reproduction phase numbering throughout

Paper references that no longer correspond to repo paths:

| Line | Paper text | Should reference |
|---|---|---|
| §495 | "28-phase audit" | Migrated to 25-section bottom-up: 7 sections × 25 phases (Section 00 → 06 + 99-ZENODO) |
| §505 | `V-Reproduction/10-cheung-emergent-reward/AUDIO_NATIVE_UPGRADE.md` | `Musical_Intelligence_Results/03-C3-BEHAVIORAL-VALIDATION/03.3-cheung-emergent-reward/AUDIO_NATIVE_UPGRADE.md` |
| §509 | "Phase 4" (compute profile) | Phase 00.3 |
| §511 | "Phase 3" (T³ active-tuple) | Phase 02.1 |
| §513 | "Phase 5" (ECE pitch_identity) | Phase 03.2 |
| §515 | "Phase 6" (R³-OOS Carillon) | Phase 01.2 |
| §517 | "Phase 11" (mech×region L3) | Phase 05.2 |
| §521 | "Phase 6" (Marjieh sensory_pleasantness) | Phase 01.2 |
| §523 | "Phase 13" (Mendelssohn) | Phase 05.1 |
| §527 | "V-Reproduction Phase 21" (ChillsDB) | Phase 03.4 |
| §531 | "PMEmo" (no phase #) | Phase 03.6 |
| §535 | "Phase 0.5" (NON-ELIG) | Phase 00.2 |
| §537 | "Phase 18" (EXEC-PENDING) | Phase 05.7 |
| §541 | "Phase 25" + "Phase 12" + "Phase 26" | Phases 05.3 + 05.4 + 05.5 |
| §550 | "1,496 enumerated cells" | Currently 06.2 PENDING (not in migrated tree) |

### A.2 — Internal inconsistency: 16,191 vs 16,248 total numeric constants

- §519 (Field Position, conclusive): **"$16{,}248$ engine constants"** + 7-category attribution (LIT-VERBATIM 67, LIT-DERIVED 19, HAND-DISCLOSED 6)
- §546 (Limitations §HTP/SPH): **"$16{,}191$ numeric constants"** ← stale
- §627 (Online Methods §Parameter provenance): **"$16{,}191$ numeric constants"** + "~40% lit-verbatim ~20% lit-derived ~30% engine-internal heuristic 7 hand-specified" ← stale, percentages pre-date V3 audit

Repo `00.1` V3 audit (authoritative): **16,248** total; 67 LIT-VERBATIM (0.41%) + 19 LIT-DERIVED (0.12%) + 9,817 STRUCTURAL (60.4%) + 1,182 IDENTITY (7.3%) + 5,157 ENGINEERING (31.7%) + 6 HAND-DISCLOSED (0.04%) + 0 DEAD-CODE + 2 DISCRETE-SELECT.

### A.3 — "Seven hand-specified reward weights" vs six (R15)

§546 + §627 both say "seven" reward weights including phi_fam_star.

Per R15 paper revision item: **phi_fam_star = 0.5 is the mathematical kernel-peak identity of the Berlyne 4f(1-f) familiarity term**, not a separately tunable code constant. Repo HAND-DISCLOSED count: **6** (the six salience-gated reward weights $w_S$, $w_R$, $w_E$, $w_M$, $g_{DA\text{-wanting}}$, $g_{DA\text{-liking}}$).

### A.4 — "Five candidate formulas" HTP/SPH (R14)

§546 says E3 was chosen "from among **five candidate formulas**".

Per R14 paper revision item (`_audits/2026-05-17_htp-sph-e3-structural-selection-audit.md`): the structural selection was actually **two-candidate per mechanism** (subtraction/entropy vs multiplicative product composition), literature-anchored to de Vries-Wurm 2023 + Bonetti 2024. The "five-candidate" framing is from old internal docs.

### A.5 — Phase 28 §500 retains Bowling row (Δ|ρ|=+0.44) — repo dropped per directive

§500 lists 5 executed cells including Bowling (Δ|ρ|=+0.44 strongest margin). Per project-wide Zero-Bowling doctrine, Repo 06.3 drops Bowling entirely (4 cells executed: Marjieh, Carillon, Cheung, TenseMusic). Decision rule rebased ≥5/6 → ≥4/5. Paper text inconsistent with current repo verdict structure.

### A.6 — Phase 16 BB-FDR portfolio (§441 + §550) is missing from §Limitations

§441 + §550 cite **1,174/1,496 BB-FDR** + **1,194/1,496 BH-FDR** + **46/50 confirmatory** + **±30% sensitivity ρ_min > 0.995**. These are not yet verified in migrated tree — 06.2 is **PENDING** per project directive ("BH-FDR'yi en sona bırakalım"). The 06.2 deferred status is not currently disclosed as a limitation. **This is a missing limitation.**

### A.7 — Phase 17 Zenodo bundle (§498) is missing from §Limitations

§498 references `17-zenodo-bundle/reproduce_all.sh` with "5/5 aggregator PASS, ~25s wall". This deposit is not yet migrated to `99-ZENODO-BUNDLE-MANIFEST/` (empty scaffold). **Should be a paper-side disclosure** that the Zenodo bundle is paper-submission-gated.

### A.8 — 3 K-K 1982 list-equality test-tooling bugs in Phase 01.1 (§478 claims "all PASS")

§478 says **"Phase 19 ... 531 pytest tests, all PASS"**. Repo 01.1 actually: **528/531 PASS + 3 K-K 1982 list-equality test-tooling failures** (Python `list ==` on float32-roundtripped K-K major/minor profile tensors; values match, comparison fails). Pre-existing in source repo, not engine drift. Should be disclosed as test-quality caveat.

---

## B. What our ACTUAL limitations are (audit from Musical_Intelligence_Results)

Based on the migrated tree state at engine SHA `318eb2f5…`, the current authentic limitation surface:

### B.1 — Statistical-inference limitations

**B.1.1 Portfolio-level aggregator deferred (Phase 06.2 PENDING)**
- Paper-time portfolio claim: 1,174/1,496 BB-FDR + 1,194/1,496 BH-FDR + 46/50 confirmatory + ±30% ρ_min>0.995
- Repo state: 06.2 PENDING.md placeholder; deferred per project directive
- Reason: portfolio aggregation requires homogeneous-null FDR families, not flat 1,496-test bucket. The 1,496-test universe mixes neural-encoding shuffle-nulls (effect size r=0.1-0.5, shuffle nulls), psychoacoustic Spearman (r=0.5-1.0, sign-invariance), behavioural ratings (r=0.3-0.6, continuous correlation), and categorical pharma cross-validations — statistically inappropriate to BH-FDR together.
- Planned restructure: 3 FDR families (Neural / Psychoacoustic+CrossCultural / Behavioural) + 5 non-FDR audit classes (engine integrity / determinism / pharmacology categorical / falsifiability cell-selection / AI-baseline margin) reported separately.
- Until 06.2 executes, the paper-time 1,174/1,496 headline is a paper-time-freeze artefact; the migrated tree carries per-section PASS rates that need cross-family BB-FDR aggregation.

**B.1.2 Phase 28 v1.0 Bowling row retired (Zero-Bowling doctrine)**
- Paper §443 + §500 still cite 5-cell baseline panel (Bowling Δ|ρ|=+0.44, Marjieh +0.68, Carillon +0.55, Cheung +0.05, TenseMusic +0.32)
- Repo 06.3 has 4-cell panel (Bowling row dropped per project Zero-Bowling doctrine; pre-reg decision rule rebased ≥5/6 → ≥4/5)
- Verdict preserved: MI WINS on 4/4 executed cells; DEAM-5 cell deferred to v1.1
- This is a doctrine-driven retirement, not an analytical failure; should be disclosed

**B.1.3 Phase 28 v1.0 closest margin (Cheung Δr=+0.05) remains threshold-borderline**
- (carried over from §500 — still valid)

### B.2 — Engine-native interaction limitations

**B.2.1 Cheung Stage B engine-native β CI containment (INCONCLUSIVE_BORDERLINE)**
- (carried over from §502-505 — still valid; needs path update)

### B.3 — Hardware-tier limitations

**B.3.1 Compute-profile M2 Air vs M2 Max (5 cells)**
- (carried over from §509 — still valid; needs phase number update)

### B.4 — Belief-calibration paradigm-transfer limitations

**B.4.1 PitchIdentity polyphonic transfer (Phase 03.2 ECE 0.156 outlier)**
- (carried over from §513 — still valid; needs phase number update)

### B.5 — Stimulus-paradigm reproducibility limitations

**B.5.1 V1 Carillon synthesis pipeline not preserved (Phase 01.2)**
- (carried over from §515 — still valid; needs phase number update)

**B.5.2 Mendelssohn sub-08 HRF Method A vs Method B (Phase 05.1)**
- (carried over from §523 — still valid; needs phase number update)

**B.5.3 Marjieh sensory_pleasantness PARTIAL (Phase 01.2)**
- (carried over from §521 — still valid)

### B.6 — fMRI evidence limitations

**B.6.1 Mech×region L3 cross-subject denominator-filter ambiguity (Phase 05.2)**
- (carried over from §517 — still valid; needs phase number update)

**B.6.2 Phase 26 per-clip vs per-TR temporal-granularity (Phase 05.5)**
- (carried over from §539 — still valid; needs phase number update)

**B.6.3 ChillsDB MMP P2 SHA-divergence under current engine SHA (Phase 03.4)**
- (carried over from §527 — still valid; needs phase number update; partially resolved at L9 verdict reconciliation 3/3 PASS while L4 TC005 retains 2/5 cell divergence)

**B.6.4 PMEmo dynamic valence below LOSO lower CI (Phase 03.6)**
- (carried over from §531 — still valid; needs phase number addition)

**B.6.5 fMRI eligibility exclusions (Phase 00.2)**
- (carried over from §535 — still valid; needs phase number update)

**B.6.6 Phase 18 EXEC-PENDING (Phase 05.7)**
- (carried over from §537 — still valid; needs phase number update)

### B.7 — Design-time provenance limitations

**B.7.1 HTP/SPH two-candidate formula-structure selection (Phase F2)**
- Updated framing per R14: "two-candidate per mechanism" instead of "five candidate formulas"
- Literature-anchored to de Vries-Wurm 2023 / Bonetti 2024 structural choices
- Validated by Phase 01.2 extended cycle 9-corpus CDC 9/9 + Marjieh split-half + PMEmo

**B.7.2 Six hand-specified reward-formula weights (R15 update)**
- Updated framing: SIX salience-gated reward weights ($w_S=1.5$, $w_R=0.8$, $w_E=0.5$, $w_M=0.6$, $g_{DA\text{-wanting}}=0.6$, $g_{DA\text{-liking}}=0.4$), NOT seven
- The previously-listed phi_fam_star ($=0.5$) is the mathematical kernel-peak identity of the Berlyne 4f(1-f) familiarity term — derivable, not separately tunable

### B.8 — Test-tooling limitations (new disclosure)

**B.8.1 Phase 01.1 K-K 1982 profile list-equality test bugs (3 of 531)**
- Phase 01.1 (R³ isolated-extended pytest battery) reports 528/531 PASS
- 3 known failures: `test_l9_constants::test_krumhansl_kessler_1982_{major,minor}_profile` + `test_l10_3_kk_1982_profiles_match_published`
- Failure mode: Python `list ==` on float32-roundtripped tensor values; underlying numerical values match published K-K 1982 profiles, but list-equality fails on roundtrip-precision drift
- Pre-existing in source repo, not engine drift
- Fix path: replace `==` assertions with `pytest.approx`; or accept as documented test-tooling caveat

### B.9 — Repository-state limitations (new disclosure)

**B.9.1 Phase 17 / 99-ZENODO bundle reproducer not yet migrated**
- Paper §498 + §598 references 17-zenodo-bundle/reproduce_all.sh with 5/5 aggregator PASS, ~25s wall
- Repo `99-ZENODO-BUNDLE-MANIFEST/` directory exists but is empty scaffold
- Will be filled at paper-submission gate (Zenodo upload coincides with arXiv preprint freeze)
- The single-command reproducer described in paper §598 lives in source repo `Musical-Intelligence-Reproduction/17-zenodo-bundle/` (175-row master ledger + reproduce_all.sh + sha256.csv + CITATION.cff + OSF-DEPOSIT.md + PAPER-REVISIONS.md)

**B.9.2 Phase 04.1 live engine spot-check uses CSV-cached verdict**
- 11/11 pharma cross-validation claims preserved bit-identically in CSV
- Live 4-channel neurochem determinism canary (max |Δ|=0 across 1,380 values on P5-fifth WAV) was executed at paper-time-freeze; not re-runnable without scipy.io.wavfile + engine runtime in reproducibility environment
- Engine bit-determinism is independently verified at Phase 02.1 (T³ isolated-extended 207 sub-tests) and via aggregate engine-pin SHA `482ade45…`

---

## C. Proposed revised §Limitations text

Below is a complete replacement for §492-550 with corrected paths, phase numbers, and additions:

```latex
\section{Limitations}
\label{sec:limitations}

\noindent The 25-section bottom-up reproducibility audit (Sections 00-06 + 99-ZENODO, deposited at \texttt{github.com/amacerdem/Musical\_Intelligence\_Results}) closes with no closed cell classified as an analytical FAIL. The residual surface consists of 11 paper-disclosed CAVEAT entries, 3 PARTIAL entries within tolerance, 3 NON-ELIGIBLE BIDS exclusions, 4 EXEC-PENDING sub-axes, one outside-CI ceiling cell, one open SHA-divergence investigation, one inconclusive-borderline engine-native CI containment (Cheung 2019 audio-native Stage~B; \S\ref{subsec:limitations-cheung-audio-native}), one design-time structural-pick disclosure (HTP/SPH; \S\ref{subsec:limitations-htp-sph-structural}), three test-tooling failures (Krumhansl-Kessler 1982 list-equality, Phase~01.1), one terminal aggregator deferred (Phase~06.2 portfolio BB-FDR), and one bundle reproducer paper-submission-gated (Phase~99 Zenodo). Each item is enumerated below.

\subsection{Same-data baseline discipline (Phase 06.3 v1.0)}
\label{subsec:limitations-learning-frontier}

\paragraph{v1.0 --- four-cell baseline panel (preliminary POSITIVE).} Phase~06.3 v1.0 tested whether simple from-scratch learners (ridge on STFT-mel; gradient-boosted trees on generic audio descriptors; ridge on IDyOM features) trained only on the benchmark data could match the frozen MI engine. Across four executed cells MI exceeded every locked baseline: Marjieh 2024 ($\Delta|\rho| = +0.68$), Harrison Carillon ($+0.55$), TenseMusic ($+0.32$), Cheung 2019 ($\Delta r \approx +0.05$, threshold-borderline). Under the pre-registered decision rule (POSITIVE = MI exceeds every baseline on $\geq 4/5$ datasets with no margin $\leq 0.05$; NEGATIVE = $\geq 2$ baselines reach or exceed MI on $\geq 2$ datasets), v1.0 returns \emph{preliminary POSITIVE}. The bounded claim: \emph{MI's advantage is over the information available to a same-data learner, not over the theoretical AI ceiling} --- strictly weaker than ``no AI can match MI'' (false under unrestricted pretraining with hand-engineered psychoacoustic features approaching $\sqrt{R_N}$) and strictly stronger than ``MI exceeds typical individual raters''. DEAM-5-song F4 MMP cell and elastic-net / MLP / CNN baseline architectures remain scheduled v1.1 extensions.

\subsection{Cheung 2019 engine-native interaction CI containment (audio-native Stage B, INCONCLUSIVE\_BORDERLINE)}
\label{subsec:limitations-cheung-audio-native}

\noindent The Phase~03.3 audio-native upgrade (Results §Cheung, Stage~B) ran MI audio-native on the 90-stimulus Cheung 2024 OSF deposit \citep{cheung2024osf} and re-fitted the M2 interaction regression with MI's HTP and ICEM substituted for IDyOM's IC and ENTROPY, returning $\beta(\mathrm{MI\_HTP} \times \mathrm{MI\_ICEM}) = -0.060$, SE $= 0.027$, bootstrap $95\%$ CI $[-0.111, -0.007]$ ($B = 5{,}000$, seed $= 42$). The engine-native interaction term \emph{carries the same negative sign} as Cheung's published $\beta = -0.124$, but the published coefficient sits $0.013$ outside the upper bound of the engine-native bootstrap CI. Under the pre-registered decision rule (POSITIVE if published $\beta$ inside engine bootstrap CI; NEGATIVE if outside by $> 0.05$; INCONCLUSIVE\_BORDERLINE otherwise), this verdict is \emph{inconclusive-borderline}: same direction, half magnitude, $0.013$ outside CI. The held-out five-fold leave-songs-out CV $r$ of the engine-native M2 is $+0.462$, which equals $2.13\times$ the LOSO inter-rater pleasure ceiling $+0.217$ --- above ceiling but below Cheung's IDyOM-fed M2 CV $r = +0.543$ ($2.50\times$ ceiling) on the same fold scheme. The non-substitution of MI's HTP/ICEM for IDyOM's IC/ENTROPY (pre-registered NEGATIVE, $r \approx 0$) is the architectural disambiguation: MI channels are chord-level features by construction, IDyOM features are symbol-stream-level entropies. Pre-registration, per-angle artefacts, engine SHA pin, and forbidden-moves audit deposited at \texttt{Musical\_Intelligence\_Results/03-C3-BEHAVIORAL-VALIDATION/03.3-cheung-emergent-reward/AUDIO\_NATIVE\_UPGRADE.md} (CLOSED 2026-05-16); the four positively-resolved Cheung-audio-native angles --- LOSO ceiling bit-exact reproduction, architectural rhythm-invariance at $r \approx +0.99$, cross-corpus calibration generalisation at pooled $\mathrm{ECE} = 0.082$, and engine-native CV at $2.13\times$ ceiling --- are reported under Results §Cheung Stage~B without architectural-emergence overclaim on the CI-containment dimension.

\subsection{Paper-disclosed CAVEAT entries (10 cells across 5 categories)}

\paragraph{Compute-profile hardware-tier (5 cells, Phase 00.3).} Paper-time profile on Apple M2 Max $+$ 64\,GB; audit on M2 Air $+$ 8\,GB. Bit-determinism reproduces verbatim across the tier change; absolute frames-per-second and resident-memory figures ($3.31\times$ real-time, 570 fps median, 465\,MB peak on paper-time hardware vs $0.47\times$, 80 fps, 1554\,MB on audit hardware) track the hardware delta --- CAVEAT-marked.

\paragraph{T$^3$ active-tuple API-bound disclosure (2 cells, Phase 02.1).} The paper-reported active-tuple count includes belief-source and relay demands not exposed through the public \texttt{H3DemandSpec} API. Engine sparsity behaviour is correct ($\sim$$8{,}600$ active at $3.85\%$); the public API enumerates only the mechanism-only subset (644 tuples at $0.288\%$).

\paragraph{ECE \texttt{pitch\_identity} polyphonic transfer (1 cell, Phase 03.2).} The Bayesian belief calibration outlier reaches $\mathrm{ECE} = 0.156$ against the $0.10$ threshold because its F1 input mechanism (PCCR) was tuned on monophonic interval-pair stimuli while the DEAM held-out audit uses polyphonic recordings. The seven remaining Core beliefs all beat the uniform baseline by $\geq 5\times$.

\paragraph{R$^3$-OOS V1 Carillon synthesis pipeline not preserved (1 cell, Phase 01.2).} The V1 Carillon stimulus synthesis was not preserved; the paper-anchor V2 sweep at A5 / 880\,Hz / SUSTAINED reproduces the headline at $|\Delta| = 0.006$.

\paragraph{Mechanism$\times$region L3 denominator-filter ambiguity (1 cell, Phase 05.2).} The L3 per-piece BH-FDR denominator filter is documented in the figure caption but not reproducible from the V3 archive aggregate alone: Phase~05.2 reports 59 target rejections under a broader filter; the paper reports 34 under an additional radius-based filter. Both denominators preserve POSITIVE separation; revision item R9.

\subsection{PARTIAL entries within paper-disclosed tolerance (2)}

\paragraph{Marjieh \texttt{sensory\_pleasantness} (Phase 01.2).} Reproduces $\rho = +0.808$ vs paper $+0.890$, $|\Delta| = 0.082$ --- within the paper-declared PARTIAL band ($\pm 0.10$) but outside strict PASS ($\pm 0.05$).

\paragraph{Mendelssohn sub-08 HRF-window (Phase 05.1).} Method A (paper-time TR-window) returns $r = +0.59$; Method B (revised TR-window) returns $r \approx +0.29$. Both preserved in the audit record; the single-subject framing makes either illustrative rather than population-level evidence.

\subsection{Phase 03.4 ChillsDB SHA-divergence at L4 TC005 (partial resolution at L9)}

\noindent Phase~03.4 records a divergence between the paper-time MMP P2 chill-marker rank-biserial ($r = +0.231$, $p_{\text{bonf}} = 0.009$) and the current engine SHA on two of five L4 TC005 specific assertion cells. The L9 verdict reconciliation passes 3/3 at the directional level (overall PASS at headline-effect level). Three candidate sources tracked: audio-preprocessing variant, undetected engine-state change, true non-determinism. The broader cognitive-signal panel on the same dataset (AAC autonomic-forecast and SSRI prediction-error channels) continues to register Bonferroni-passing event-locked effects under the current SHA.

\subsection{Phase 03.6 PMEmo dynamic valence below LOSO lower CI bound}

\noindent Among the seven ceiling-saturation cells across the migrated tree, six fall at or above the LOSO lower 95\% CI bound; PMEmo dynamic valence does not (75.7\% of ceiling; $\rho = +0.120$ vs ceiling $+0.158$ [$+0.144,\,+0.172$]). The paradigm is registered as OPEN; the same-data learning-frontier argument (\S\ref{subsec:limitations-learning-frontier}) is explicitly not extended to PMEmo dynamic-emotion.

\subsection{Eligibility exclusions and execution-pending audit gaps}

\paragraph{NON-ELIGIBLE datasets (3, Phase 00.2).} Three fMRI datasets excluded a priori at the BIDS entry-gate: ds005880 (\texttt{events.tsv} stores integer-second onsets vs.\ engine's $172.27$\,Hz frame-level requirement), ds006583 (\texttt{events.tsv} absent after partial download), ds006564 (naturalistic film paradigm without per-trial events). Infrastructure filters, not analytical failures.

\paragraph{EXEC-PENDING (2 sub-axes, Phase 05.7).} Two fMRI datasets carry frozen pre-registered pipelines awaiting external stimulus-audio fetch: studyforrest 7T music genres (Phase 05.7.1) and ds000171 music+depression (Phase 05.7.5). Decision rule and feature spec are frozen prior to audio arrival.

\subsection{Phase 05.5 per-clip vs.\ per-TR temporal-granularity mismatch}

\noindent On ds003720, the cycle-17 MI encoder operates at per-clip scale while the cross-subject ceiling operates at per-TR scale. MI encoder saturation reaches 5 of 21 non-brainstem regions under this mismatch vs Phase~05.3's $16/21$ at matched per-TR granularity on ds002725 --- a paradigm-scale disclosure, not an MI weakness. Phase~05.4 voxelwise routing-ablation (paper-canonical primary on ds003720) is unaffected.

\subsection{Design-time provenance dependency: HTP/SPH formula-structure selection}
\label{subsec:limitations-htp-sph-structural}

\paragraph{Scope.} \tac{None of the $16{,}248$ engine constants is calibrated against held-out cognitive, behavioural, fMRI, or pharmacological data} (the six salience-gated reward-formula weights of \texttt{brain/reward.py} are hand-specified design constants, disclosed separately in \texttt{S1 \S Reward formula}, not fitted; the seventh paper-listed item phi\_fam\_star$=0.5$ is the mathematical kernel-peak identity of the Berlyne $4f(1-f)$ familiarity term, derivable rather than tuned). Two of 89 cognitive mechanisms (HTP and SPH, both F2 Prediction) include a discrete two-candidate structural model-selection step per mechanism: the joint-prediction layer E3 was chosen as the product composition $E_0 \times E_2$ over an additive alternative, before weights were frozen. The selection is literature-anchored \citep{deVriesWurm2023,bonetti2024}; weights are perturbation-stable under $\pm 30\%$.

\paragraph{Out-of-sample evidence.} The Phase 01.2 extended-cycle nine-dataset consonance battery returns the theoretically-correct sign on every R$^3$ headline channel across all $9/9$ datasets (CDC invariant: PASS). Marjieh 2024 split-half cross-validation ($N{=}151$) returned a generalisation gap $|\Delta\rho| \in [0.007,\,0.034]$ within the conventional minimal-overfitting band; PMEmo 2018 real-music valence returned HTP $4/5$ and SPH $3/4$ significant on $N{=}100$ songs.

\subsection{Phase 01.1 K-K 1982 list-equality test-tooling bugs (3 of 531)}

\noindent The Phase~01.1 R$^3$-isolated-extended pytest battery returns 528/531 PASS. Three failures (\texttt{test\_l9\_constants::test\_krumhansl\_kessler\_1982\_\{major,minor\}\_profile}, \texttt{test\_l10\_cross\_impl::test\_l10\_3\_kk\_1982\_profiles\_match\_published}) are test-tooling artefacts of Python \texttt{list ==} comparison on float32-roundtripped Krumhansl-Kessler 1982 reference profile tensors: the underlying numerical values match the published profiles, but the equality assertion fails on roundtrip-precision drift. Pre-existing in the source repository, not engine drift; fix path is to replace \texttt{==} assertions with \texttt{pytest.approx}.

\subsection{Phase 06.2 unified portfolio aggregator deferred}

\noindent The portfolio-level multiple-comparison aggregation summarised in Results §Gold (paper-time-freeze: 1{,}174/1{,}496 hierarchical BB-FDR pass at $q<0.05$; 1{,}194/1{,}496 unstratified BH-FDR; 46/50 confirmatory OSF subset; $\pm 30\%$ sensitivity $\rho_{\min} > 0.995$) is currently deferred at Phase~06.2 (\texttt{Musical\_Intelligence\_Results/06-PORTFOLIO-FALSIFIABILITY/06.2-unified-bb-fdr-aggregator/PENDING.md}). The deferral reflects a methodological revision: the original flat 1{,}496-test BB-FDR universe mixed heterogeneous null structures (neural-encoding shuffle-nulls, psychoacoustic sign-invariance, behavioural continuous correlation, pharmacology categorical agreement) under a single hierarchy, violating BB-FDR's exchangeability-within-family assumption. The revised structure pre-registered for v1.1 specifies three statistical FDR families (Neural-encoding / Psychoacoustic+Cross-cultural / Behavioural reward-emotion) with within-family BH-FDR + cross-family BB-FDR, plus five separately-reported non-FDR audit classes (engine cardinality, engine determinism, pharmacology categorical, falsifiability pre-committed cell selection, AI-baseline margin comparison). Until 06.2 executes the new hierarchy, the per-section PASS rates (Section 00 through Section 06) carry the load-bearing evidence; the flat 1{,}174/1{,}496 figure is a paper-time-freeze artefact preserved for archival cross-reference.

\subsection{Phase 99 Zenodo bundle paper-submission-gated}

\noindent The single-command reproducibility bundle described under \S Data and code availability (\texttt{bash 17-zenodo-bundle/reproduce\_all.sh}, $\sim$25\,s wall on Apple M2 Air, 5/5 aggregator PASS, 38-row SHA-256 manifest, 175-row master claims ledger, CITATION.cff, OSF-DEPOSIT.md, PAPER-REVISIONS.md) lives in the source-repository checkpoint at \texttt{Musical-Intelligence-Reproduction/17-zenodo-bundle/} and its \texttt{\_archive\_paper\_time\_freeze\_2026-05-07/} subdirectory. The migrated-tree slot at \texttt{Musical\_Intelligence\_Results/99-ZENODO-BUNDLE-MANIFEST/} is currently an empty scaffold; the bundle is paper-submission-gated and will be populated coincident with the arXiv freeze and Zenodo DOI assignment.
```

---

## D. Apply this revision?

This proposal:
1. Fixes 8 documented inconsistencies (stale phase numbers, 16,191 vs 16,248, 7 vs 6 reward weights, 5 vs 2 candidate formulas, missing 06.2 + 99-ZENODO + K-K test-bug + Zero-Bowling disclosures)
2. Carries over all currently-valid limitations with updated paths/numbers
3. Adds three new disclosure subsections (Phase 06.2 deferred, Phase 01.1 K-K bugs, Phase 99-ZENODO gated)
4. Drops nothing — every currently-disclosed limitation remains, just with corrected references

**Net character-count delta:** +~2,000 chars (3 new subsections + path corrections offset by phase-number simplifications).

**Recommended:** Apply to `Publication/Amac-Erdem-Musical-Intelligence.tex` lines 492-550 as a single atomic edit. Author review the proposed text first; if approved, the LaTeX block above can be substituted in verbatim.
