# Paper Text Fact-Check — "What is borrowed; what is introduced" + "Cross-domain syntheses"

**Date:** 2026-05-17
**Source of suspicion:** PI flag (yalan konusuyor)
**Audit anchor:** `_audits/audit_combined.csv` (16,248 constants, 9 agents) + `audit_summary.md` + `escalation_resolutions.md` + `2026-05-17_htp-sph-e3-structural-selection-audit.md`
**Engine pin:** SHA `318eb2f5...` / aggregate `482ade45...` (FROZEN)

---

## Headline verdict

Of **23 enumerated empirical claims** in the two passages, the audit data classifies them as follows:

- **ACCURATE: 6** — claims that match audit data at the granularity they operate (e.g. "529 RegionLinks", Friston-precision soft language, Doya-operationalization soft language, Salimpoor×Doya synthesis, atom-vs-system framing one-liner).
- **GRANULARITY-MISLEADING: 4** — atom-level provenance % framings that a reader will likely apply at the constant level, where the engine-wide LIT-anchoring rate collapses to **0.53%** (86 / 16,248).
- **MISSING-CAVEAT: 6** — soft-language anchors ("inspired by", "operationalised as", "applied as") that are individually defensible but omit the documented PARTIAL/R9 outcomes (Hasson 32-horizon ladder PARTIAL; Berlyne 4·x·(1−x) B-PARTIAL; Aston-Jones 0.50/0.75 NEGATIVE bit-exact; Doya BP_ND tags PARTIAL; Thaut τ=4.0 PARTIAL; Bismarck re-parameterization PARTIAL).
- **OVERSTATED: 2** — "literature-anchored by construction" for the 529 RegionLink edge weights (audit found these are **uniformly E4 mixer / author-Likert** with verdict "no paper publishes per-edge weights"), and **"re-instantiated as the substrate's Macro/Ultra horizon bands"** for Hasson TRWs (audit found HORIZON_MS is concept-LIT only; ladder is author-derived, B-PARTIAL with escalation).
- **INACCURATE: 1** — none of the seven introduced contributions are factually wrong, but item (ii) **"emergent ∼3.85% sparsity"** is paper-level numerical claim that does not appear in the audit; treat as PI-judgment.
- **OUT-OF-AUDIT-SCOPE: 4** — paper-level empirical claims (e.g. "+0.9 s caudate-leads-NAcc"; "four pre-registered architectural-null falsifications") that the constant-level audit cannot adjudicate.

The PI's instinct is **partly correct**. The passage is not technically dishonest at any single sentence, but it **systematically uses atom-level and concept-level framings that read at the constant level**, where the LIT-anchoring story is dramatically thinner (0.53%). The single most aggressive overclaim is **"C³ RegionLinks (529 edges) are literature-anchored by construction"** — audit-resolved verdict on those exact 573 RegionLink weight constants is "**No paper publishes per-edge weights**" (uniformly E4 mixer).

---

## Granularity primer (for reader)

Before the per-claim table:

| Granularity | Source | Numbers cited in passage | Audit-confirmed numbers |
|---|---|---|---|
| **Atom-level** (algorithm/computation block) | Papers 2 & 3 (R³/T³ companion papers) | R³ 46%/24%/20%/10%; T³ 45%/26%/19%/10% | Not directly verified by this audit (atom-level inventory is paper-side, not constant-side) |
| **Constant-level** (numeric Python literal) | THIS AUDIT (16,248 constants, 9 agents, 2026-05-17) | (none explicitly cited in passage) | A LIT-VERBATIM 67 / B LIT-DERIVED 19 = **86 = 0.53% engine-wide**; all 86 in `ear/r3/*` + 1 Berlyne in `brain/reward.py:83` |
| **Concept-level** (theoretical lineage) | Cross-domain syntheses paragraph | Hasson/Murray/Friston/Doya/Aston-Jones/Flash-Hogan/Berlyne/de Vries-Wurm/Guo/Nichols-Holmes | Audit verifies citation presence; bit-exact numeric values almost universally PARTIAL or NEGATIVE |

Reader expectation: when a paper says "atomic computations are largely literature-anchored ports", a reader steeped in software/replicability discourse will likely picture **bit-exact constants** (the 0.53% figure), not **algorithm blocks** (the 46% figure). The passage does not signpost this distinction — that is the structural fairness problem.

---

## Per-claim fact-check table

### Paragraph 1 — "What is borrowed; what is introduced"

| # | Claim (paraphrase) | Audit data | Classification | Recommended fix |
|---|---|---|---|---|
| 1 | "Atomic computations are largely literature-anchored ports of cited primary sources." | Atom level (Papers 2/3): R³ 46%/24%/20%/10% lit-direct/adapted/composed/novel; T³ 45%/26%/19%/10%. **Constant level (this audit): 0.53% engine-wide LIT (67 A + 19 B = 86 / 16,248).** | **GRANULARITY-MISLEADING** | Add signpost: "(at the atom/algorithm level; constant-level analysis gives 0.53% LIT-anchored engine-wide — see Paper 4 §Parameter provenance.)" |
| 2 | "R³ (102 atoms): 46% literature-direct, 24% literature-adapted, 20% literature-composed, 10% novel" | Atom-level rate not directly audited at constant level. **Constant-level rate in R³+T³ scope: 67 A / 592 = 11.3% LIT-VERBATIM, 18 B / 592 = 3.0% LIT-DERIVED (Agent 4 pilot).** All other audit scopes (F1-F9 mechs, RAM, neurochem, cycle, scaffolding): **A=0, B=1 — the only non-R³/T³ B is Berlyne `4.0` in `brain/reward.py`**. | **GRANULARITY-MISLEADING** (true at atom level; reader will conflate) | Same signpost as #1; cite the 11.3% A figure in Paper 2 §Constant-level provenance as a reader anchor. |
| 3 | "T³ (42 atoms): 45%/26%/19%/10% under the same four-tier scheme" | Same atom-level framing; constant level: Agent 4 includes T³ within R³+T³ pooled 592 → 67 A + 18 B = 14.4% LIT. Hasson 32-horizon ladder (HORIZON_MS) is B/MEDIUM with PARTIAL outcome + escalation (NEGATIVE-UNVERIFIABLE on bit-exact Hasson value). | **GRANULARITY-MISLEADING + MISSING-CAVEAT** | Add: "(T³ horizon ladder is B-PARTIAL — concept-LIT to Hasson 2008 / Lerner 2011 with author-derived ladder values.)" |
| 4 | "C³ RegionLinks (529 edges) are literature-anchored by construction (Paper 4)." | Cardinality "529 edges" **ACCURATE** at structural-cardinality level. But the **per-edge weight constants are uniformly E4 (ENGINEERING-CHOICE)** across all 9 agents. Cross-agent pattern audit: **573 RegionLink weights → 573 E (100% dominant)**. Per-row reason text: "**No paper publishes per-edge weights** — author-normalized Likert-style scaling over a literature-cited edge set." Same verdict for the 70 NeuroLink weights. | **OVERSTATED** (claim implies LIT anchoring of edge *weights*; audit confirms only edge *existence* is literature-cited, magnitudes are author-Likert) | Replace "literature-anchored by construction" with "literature-anchored at the *edge-existence* level (each edge is cited to a primary functional fMRI study); per-edge weight magnitudes are author-normalized Likert [0.40-0.95] — disclosed as E4 ENGINEERING-CHOICE in Paper 4 §Parameter provenance." |
| 5 | "(i) the four-axis cognitive ontology and function-as-runtime-container split (Paper 4)" | Out of constant-level audit scope; system-design claim. | **OUT-OF-AUDIT-SCOPE** (no audit data refutes) | No change. |
| 6 | "(ii) the demand-driven 4-tuple T³ grammar and its emergent ∼3.85% sparsity" | The 4-tuple grammar is confirmed by audit (5,580 H3DemandSpec positional args, all C STRUCTURAL across 9 agents). The "∼3.85% sparsity" figure is paper-side claim (MEMORY notes ~3.9% / 8,600 active demand tuples / 223,488 theoretical max). Constant-level audit does not verify the 3.85% number directly. | **OUT-OF-AUDIT-SCOPE** for the sparsity figure; **ACCURATE** for the grammar claim. | If paper says "3.85%" verify MEMORY-cited "3.9%" or 8,600/223,488=3.85% holds at the FROZEN SHA. (PI-judgment item.) |
| 7 | "(iii) the F0-free pairwise consonance reformulation in R3 Group A (Paper 2)" | Group A audit (Agent 4): 7 LIT-VERBATIM Sethares constants + 14 engineering clamps + 4 LIT-DERIVED (PL 25%, Sethares-σ, Tenney, parabolic-interp) + 80 E. The "F0-free pairwise reformulation" is a *structural-design claim* about how Group A is composed, not a constant-level claim. | **ACCURATE** at structural level. | No change. |
| 8 | "(iv) the 529-edge per-mechanism RegionLink fabric with emergent hub structure (Paper 4)" | Cardinality 529 confirmed at structural level (RegionLink call sites in `brain/functions/f{1..8}/mechanisms/*/__init__.py`). Hub structure is a paper-side emergent-property claim, not constant-audit testable. | **ACCURATE** at cardinality level. | No change. |
| 9 | "(v) the dual-DA architectural commitment and the +0.9 s caudate-leads-NAcc latency prediction (Paper 4)" | Dual-DA channel split is confirmed by audit: `dopamine.py` has CHANNEL=0 + REFERENCE_VALUES dict {caudate=0.78, NAcc=0.88, baseline=0.35} → tags PARTIAL (R9 form-LIT/coeff-author, Agent 8 ESC-A8-*×3). The +0.9 s lag is empirical analysis result not in constant scope. | **ACCURATE** for architectural claim; **OUT-OF-AUDIT-SCOPE** for the +0.9 s number. | No change at constant audit level. |
| 10 | "(vi) the pre-registered architectural-null falsification discipline (four F3/F4/F7 cross-domain nulls...)" | Validation result, not a constant. | **OUT-OF-AUDIT-SCOPE** | No change. |
| 11 | "(vii) the frozen, calibration-free, bit-identical reproduction methodology" | Audit's headline finding: **zero of 16,248 numeric constants calibrated against held-out cognitive data**. Engine FROZEN at SHA `318eb2f5...`. 2 mechs (HTP-E3, SPH-E3) have a discrete structural-selection step (2-candidate per mech, NOT 5 as MEMORY previously stated — see `2026-05-17_htp-sph-e3-structural-selection-audit.md` R14). | **ACCURATE** | If paper anywhere repeats "5 candidate formulas" for HTP-E3/SPH-E3, change to "**two-candidate discrete formula-form selection per mechanism**" (R14). |
| 12 | "Borrow concentrates at the atomic level; introduction concentrates at the system level." | Audit data supports this asymmetry directionally — atom-level LIT (R³ 46%, Papers 2/3) is dense; system-level constants (5,157 E + 9,817 C + 1,182 D) are author/topology. | **ACCURATE** (one-liner is fair) | No change. |

### Paragraph 2 — "Cross-domain syntheses"

| # | Claim (paraphrase) | Audit data | Classification | Recommended fix |
|---|---|---|---|---|
| 13 | "Hasson temporal receptive windows from narrative listening (ref 15) re-instantiated as the substrate's Macro/Ultra horizon bands" | Agent 4: Hasson 2008 + Lerner 2011 cited; HORIZON_MS (32 values) + HORIZON_FRAMES tagged **B/MEDIUM with PARTIAL + escalation**. Web search returned **NEGATIVE-UNVERIFIABLE** on the specific 32-horizon ladder bit-equal to Hasson. Agent 4 summary §risk-2: "TRW inspirational only — could legitimately be downgraded to E by stricter reviewer." | **OVERSTATED** ("re-instantiated as" implies bit-equal port; audit finding is concept-LIT only with author-derived ladder values) | Soften to "**inspired by**" or "**conceptually anchored on**"; add: "(ladder values are author-derived; concept-LIT only — disclosed in Paper 3 §Parameter provenance and §Limitations.)" |
| 14 | "Murray 2014 intrinsic timescales from primate-cortex electrophysiology motivate horizon spacing" | "Motivate" is soft language. Audit found **no Murray 2014 constant** mapped to any LIT/B; Murray appears (if anywhere) in docstrings only. The horizon ladder itself is B-PARTIAL anchored to Hasson, not Murray. | **MISSING-CAVEAT** (soft "motivate" is defensible, but Murray is not separately anchored in constants — it's a co-citation of the Hasson concept-LIT) | Combine with #13: "...horizon spacing inspired jointly by Hasson narrative-listening hierarchies and Murray 2014 intrinsic-timescale measurements; specific ladder values are author-derived (B-PARTIAL)." |
| 15 | "Friston precision-weighted update from sensorimotor active inference (ref 14) industrialised as a per-belief cycle across the C³ ontology" | Bayesian belief cycle implementation confirmed by audit: `contracts/bases/belief.py` (Agent 9) holds PRECISION_SCALE=12.0, PRECISION_WINDOW=16, Bayesian gain clamp [0.20, 0.80]. All tagged **E (ENGINEERING-CHOICE) with HIGH confidence**, explicit "**Not in Friston 2005**" attribution. Friston cited as RegionLink existence anchor only (PARTIAL). | **MISSING-CAVEAT** (the soft "industrialised as" word is defensible; reader may infer Friston-bit-exact precision parameters, which the audit refutes) | Add: "(precision-scale and gain-clamp magnitudes are engine-authored operational safeguards, not Friston-published; see Paper 4 §Parameter provenance.)" |
| 16 | "Doya 2002 neuromodulator roles from RL meta-theory operationalised as the four-channel accumulator with typed effect semantics" | Four-channel topology (DA/NE/OPI/5HT = channels 0/1/2/3) confirmed STRUCTURAL across Agents 7/8. Doya cited as channel-index co-locator (Agent 8: "Schultz 1997 does not 'publish' the integer 0 — channel index is engine topology choice"). BASELINE=0.5 per channel = E5 (NEGATIVE-on-stored-value). REFERENCE_VALUES dict entries = E PARTIAL (R9). **No A/B constants in Agent 8 scope.** | **ACCURATE** (soft "operationalised as" is the precise word; audit confirms Doya 2002 is concept-LIT for the four-channel layout, no bit-exact numeric port) | Optional: add "(channel topology is Doya-anchored; per-channel baselines and reference dicts are author-normalized — E with R9 PARTIAL.)" |
| 17 | "Aston-Jones locus-coeruleus arousal from general decision-making applied to music-evoked surprise on the NE channel" | Aston-Jones 2005 cited in `norepinephrine.py` REFERENCE_VALUES (resting=0.50, unexpected=0.75, familiar=0.35). All three tagged **E PARTIAL (R9)** with NEGATIVE bit-exact verification: "Aston-Jones 2005 framework confirmed qualitatively (phasic burst > tonic); specific normalized burst value not published." | **MISSING-CAVEAT** (soft "applied to" is defensible; reader may believe 0.50/0.75 are Aston-Jones-published) | Add: "(specific 0.50/0.75/0.35 normalized values are author-Likert references; Aston-Jones 2005 publishes phasic/tonic qualitatively only — R9 form-LIT/coeff-author.)" |
| 18 | "Flash–Hogan minimum-jerk from motor control repurposed as the audio-feature smoothness morph M15" | Audit: M15 (smoothness morph) appears in `ear/h3/morphology/dynamics/smoothness.py:33` as `1/(1+vel_std)`; literal `1.0` tagged **D IDENTITY-PLACEHOLDER** (additive identity). No Flash-Hogan citation in audit trail; no bit-exact constant. The morph FORM is the velocity-std-inverted scalar, not the minimum-jerk integral. | **MISSING-CAVEAT** (the connection is conceptual; "repurposed as" overstates the structural fidelity) | Soften: "informed by" or "conceptually echoes"; or be specific: "the M15 smoothness morph operationalizes the inverse-velocity-variance principle motivating Flash-Hogan minimum-jerk in motor control." Audit does not refute the inspiration, only the bit-exact import. |
| 19 | "Berlyne's inverted-U from general aesthetics instantiated as the IUCP 4x(1−x) kernel" | Agent 5: Berlyne `4.0` in `brain/reward.py:83` is the **only B-tagged constant outside R³/T³** (audit-wide). Tagged **B-PARTIAL** with web-search NEGATIVE bit-exact: "Berlyne 1971 publishes inverted-U qualitatively; 4x(1-x) is canonical unit-interval-normalized parabola; specific coefficient not bit-published." **Three other `4.0` instances in F6 mechs (IUCP `extraction.py:86`, SSPS `extraction.py:136`×2) tagged E**, not B (consistency note ESC-A5-2). The IUCP-specific 4.0 is **E**, not B — the only B kernel sits in `brain/reward.py`, not IUCP. | **GRANULARITY-MISLEADING** (the passage attributes the kernel to IUCP; audit confirms IUCP's `4.0` is E mixer, with the B-tagged Berlyne kernel actually living in `brain/reward.py`) | Either: (a) Move attribution to `brain/reward.py:83 fam_mod = 0.5 + 0.5·4f(1-f)`; or (b) Note that the IUCP `4x(1-x)` form is the same structural kernel embedded in mixer context. Either way, add: "(form-LIT to Berlyne 1971; specific 4·x·(1−x) coefficient is canonical unit-interval-normalized parabola peak-at-x=0.5 — B-PARTIAL, ESC-A5-2.)" |
| 20 | "de Vries–Wurm hierarchical predictive timescales from vision seeding the F2 HTP mechanism" | 2026-05-17 HTP/SPH-E3 audit: HTP-E3 is a **literature-anchored discrete model selection** (multiplicative composition E0 × E2) operationalizing de Vries & Wurm 2023's interaction effect (ηp² = 0.49) as a multiplicative term. Selection is **two-candidate per mechanism** (multiplicative vs subtractive), NOT bit-exact port of timescale values. The 500/200/110 ms timescales appear in HTP docstrings ONLY (Agent 2 §4), encoded indirectly via T³ horizon-index references. | **ACCURATE** (soft "seeding" is the precise word; audit confirms structural-anchoring without bit-exact port) | Optionally add: "(implemented as a 2-candidate discrete formula-form selection — multiplicative E0×E2 — operationalizing the interaction effect; see Paper 3 §Design-time structural choices and `2026-05-17_htp-sph-e3-structural-selection-audit.md`.)" Also note: if the paper says "5 candidate formulas" anywhere for HTP-E3, that's a separate R14 revision. |
| 21 | "Guo 2017 expected-calibration-error from ML calibration (refs 18, 19) transferred to per-mechanism Bayesian belief calibration on continuous music ratings" | Validation methodology claim. Audit cannot adjudicate ECE methodology; constant-level relevance is the `[0.20, 0.80]` Bayesian gain clamp in `contracts/bases/belief.py:204` (Agent 9, E HIGH, "engineering safeguard documented as such (not fit)"). | **OUT-OF-AUDIT-SCOPE** (methodology import, not a constant) | No change. |
| 22 | "Nichols–Holmes nonparametric permutation from general fMRI methodology applied as the two-orthogonal-null RAM-topology test" | Validation methodology claim (10K permutations under centroid-relocation + label-shuffle nulls). Not a constant. | **OUT-OF-AUDIT-SCOPE** | No change. |
| 23 | "At least ten novel intra-domain couplings (Salimpoor×Doya; Sethares×Friston; Cheung×Berlyne×additive reward; Hasson×Murray×multi-scale descriptors)" | Audit data: Salimpoor BP_ND × Doya channel topology = combination of two PARTIAL-anchored components (Agent 8 + REFERENCE_VALUES dicts). Sethares (R³ A LIT) × Friston (cycle E with PARTIAL existence) = combination. Cheung 2019 cited × Berlyne 4x(1-x) kernel = combination (β=−0.124 appears in comments only per Agent 2). Hasson × Murray × multi-scale descriptors = combination of Hasson B-PARTIAL with conceptual Murray and multi-scale-morph E5. Audit confirms the components exist; the "novel coupling" claim is a system-level synthesis claim. | **ACCURATE** as a system-level synthesis statement | No change. |

---

## Most critical issues (top 5)

### 1. "C³ RegionLinks (529 edges) are literature-anchored by construction" — OVERSTATED

This is the strongest candidate for the PI's "yalan konusuyor" instinct.

**Audit verdict (cross-agent pattern check, reconciliation_log.md §3):** **573 RegionLink weight constants → 573 E (100% dominant)**, with uniform per-row reason: "**No paper publishes per-edge weights — author-normalized Likert-style scaling over a literature-cited edge set.**" Same verdict for 70 NeuroLink weights. RegionLink *existence* is literature-anchored (each call site cites a primary functional fMRI study); RegionLink *weight magnitude* is E4 mixer with PARTIAL verification (citation grounds the edge, not the weight).

**The phrase "literature-anchored by construction" reads at a reviewer as if the 0.40-0.95 numeric weights are published.** They are not. Context_brief §7 risk-3 explicitly enumerates this as a known-overclaim risk.

**Recommended revision:**

> "C³ RegionLinks (529 edges) are literature-anchored at the *edge-existence* level — each edge is cited to a primary functional fMRI study — while per-edge weight magnitudes are author-normalized Likert [0.40-0.95] disclosed as engineering choice (Paper 4 §Parameter provenance)."

### 2. "Atomic computations are largely literature-anchored ports" — GRANULARITY-MISLEADING

The atom-level 46% figure for R³ is correct in Papers 2/3. But the same passage operates *immediately* in a registration-of-contributions context, and a software-paper reviewer will read "atomic computations" as "computational atoms in the engine"; the constant-level audit gives **0.53% engine-wide LIT**, and even the R³+T³ pilot scope (where literature density is highest) gives 14.4% A+B.

The two granularities are both honest but only one is signposted in the passage. **A reviewer who anchors on this paragraph and then opens the audit will feel deceived even if no individual sentence is technically false.**

**Recommended revision:** Insert a one-sentence granularity primer immediately after the sentence:

> "(Granularity note: these classifications are *atom-level* — they describe algorithm blocks, not numeric Python literals. At the constant level, where the FROZEN engine ships 16,248 numeric literals, 0.53% are literature-anchored — see Paper 4 §Parameter provenance.)"

### 3. "Hasson temporal receptive windows... re-instantiated as the substrate's Macro/Ultra horizon bands" — OVERSTATED

Audit verdict (Agent 4 ESC-A4-Hasson): HORIZON_MS / HORIZON_FRAMES are tagged **B-PARTIAL with MEDIUM confidence + escalation flag TRUE**. Web search NEGATIVE-UNVERIFIABLE on bit-exact 32-horizon ladder. Agent 4 summary §risk-2 explicitly: "Hasson is the largest 'near-miss' LIT case; could legitimately be downgraded to E by stricter reviewer."

"Re-instantiated as" is the wrong verb. The horizon **concept** is Hasson/Lerner-anchored; the specific **32-horizon ladder** is author-derived geometric/temporal spacing. "Re-instantiated" implies a port of the ladder values, which the audit rejects.

**Recommended revision:** Replace "re-instantiated as" with "**inspired by**" or "**conceptually anchored on**". This matches the corresponding paper-side §Limitations disclosure that the ladder is concept-LIT only.

### 4. "Berlyne's inverted-U... instantiated as the IUCP 4x(1−x) kernel" — GRANULARITY-MISLEADING + ATTRIBUTION-OFF

Two issues:
1. The B-tagged Berlyne `4.0` kernel **lives in `brain/reward.py:83`, not IUCP**. The IUCP `4.0` at `iucp/extraction.py:86` is **E** (not B), because Agent 5 ESC-A5-2 ruled that embedded-mixer 4.0 instances are E, only pure-kernel 4.0 in `reward.py:83` is B.
2. Even the B-tagged `4.0` is **B-PARTIAL** with NEGATIVE bit-exact verification: Berlyne 1971 publishes inverted-U qualitatively, not the specific 4·x·(1−x) coefficient.

**Recommended revision:** "Berlyne's inverted-U from general aesthetics **operationalised** as the 4·x·(1−x) familiarity kernel (`brain/reward.py:83`); the same kernel form is embedded in F6 IUCP/SSPS mixers." Optionally add the ESC-A5-2 PARTIAL caveat.

### 5. HTP-E3 "5 candidate formulas" vs "2 candidate per mechanism" — INACCURATE if paper still says 5

The 2026-05-17 HTP/SPH-E3 structural-selection audit found that MEMORY note `project_zero_calibration_doctrine.md` previously said "5 candidate formula compositions" but audit verified **2 candidates per mechanism** (HTP-E3: multiplicative vs subtractive; SPH-E3: multiplicative vs entropy-difference). MEMORY note and paper §Limitations §5.9 both flagged for R14 revision.

**The passage under review does NOT cite "5 candidate" — this is good.** But if the §Limitations or Methods of the master MI paper still says "five candidate formulas", that must be revised to "two-candidate discrete formula-form selection per mechanism" (audit document §6 R14).

---

## Recommended revisions (concrete paragraph rewrites for worst offenders)

### Revision A — Paragraph 1, sentence 1-3 (granularity signpost + RegionLink fix)

**Original:**

> Atomic computations are largely literature-anchored ports of cited primary sources. The two component-paper provenance tallies report concrete breakdowns: R3 (102 atoms) classifies as 46% literature-direct, 24% literature-adapted, 20% literature-composed, 10% novel; T3 (42 atoms) classifies as 45%/26%/19%/10% under the same four-tier scheme (Papers 2 and 3). C3 RegionLinks (529 edges) are literature-anchored by construction (Paper 4).

**Revised:**

> Atomic computations are largely literature-anchored ports of cited primary sources **at the algorithm-block level**. The two component-paper provenance tallies report concrete breakdowns: R3 (102 atoms) classifies as 46% literature-direct, 24% literature-adapted, 20% literature-composed, 10% novel; T3 (42 atoms) classifies as 45%/26%/19%/10% under the same four-tier scheme (Papers 2 and 3). **At the numeric-constant level the engine ships 16,248 Python literals; a recent provenance audit found 0.53% (86 / 16,248) literature-anchored, concentrated in the R³/T³ early-perceptual front-end (Paper 4 §Parameter provenance).** C3 RegionLinks (529 edges) **are literature-anchored at the edge-existence level — each edge cites a primary functional fMRI study — while per-edge weight magnitudes are author-normalized Likert [0.40-0.95] disclosed as engineering choice** (Paper 4).

### Revision B — Paragraph 2, sentence 1-2 (Hasson + Berlyne softening)

**Original:**

> Hasson temporal receptive windows from narrative listening15 re-instantiated as the substrate's Macro/Ultra horizon bands; Murray 2014 intrinsic timescales from primate-cortex electrophysiology motivate horizon spacing; ... Berlyne's inverted-U from general aesthetics instantiated as the IUCP 4𝑥(1−𝑥) kernel; ...

**Revised:**

> Hasson temporal receptive windows from narrative listening15 **inspired** the substrate's Macro/Ultra horizon bands (specific 32-value ladder is author-derived; see Paper 3 §Parameter provenance); Murray 2014 intrinsic timescales from primate-cortex electrophysiology motivate horizon spacing; ... Berlyne's inverted-U from general aesthetics **operationalised as the 4·𝑥·(1−𝑥) familiarity kernel in `brain/reward.py` and embedded in the F6 IUCP/SSPS mixers** (form-LIT to Berlyne 1971; specific coefficient is canonical unit-interval-normalized parabola peak-at-𝑥=0.5); ...

### Revision C — Paragraph 1, item (vii) preservation + R14 sync

If anywhere in the paper §Limitations §5.9 or §Methods says "five candidate formulas" for HTP-E3 / SPH-E3 selection, replace with: **"two-candidate discrete formula-form selection per mechanism"** (per `2026-05-17_htp-sph-e3-structural-selection-audit.md` §6 R14). The contributions list item (vii) in the passage under review is untouched.

---

## Items requiring PI judgment

These are claims where the audit cannot fully adjudicate but the PI may want to verify:

1. **"emergent ∼3.85% sparsity"** (claim 6) — Audit confirms 5,580 H3DemandSpec positional args and the 4-tuple grammar but does not enumerate "active vs theoretical" demand tuples. MEMORY says ~3.9% / 8,600 active / 223,488 theoretical. PI to confirm if "3.85%" is the FROZEN-SHA-recomputed figure or an older estimate.

2. **"+0.9 s caudate-leads-NAcc latency prediction"** (claim 9) — Empirical analysis result; PI to confirm the +0.9 s number is stable across paper drafts and matches Paper 4 / C³-Biology figure. (MEMORY confirms: "DA caudate-leads-NAcc 52/56 tracks at +0.9s lag; Putkinen μ-opioid PET 7/7" — consistent.)

3. **"four F3/F4/F7 cross-domain nulls registered as expected-fail"** (claim 10) — Pre-registration claim, requires PI to confirm the four nulls are documented in the pre-reg manifest with the "expected-fail" framing.

4. **"At least ten novel intra-domain couplings"** (claim 23) — Audit confirms component existence for the four listed examples (Salimpoor×Doya, Sethares×Friston, Cheung×Berlyne×additive reward, Hasson×Murray×multi-scale descriptors). The "at least ten" claim is unverified at audit level — PI to enumerate.

---

## Summary table by classification

| Classification | Claims | % of 23 |
|---|---|---|
| ACCURATE | 5, 7, 8, 9, 11, 12, 16, 20, 23 | 39% (9) |
| GRANULARITY-MISLEADING | 1, 2, 3, 19 | 17% (4) |
| MISSING-CAVEAT | 14, 15, 17, 18 | 17% (4) |
| OVERSTATED | 4, 13 | 9% (2) |
| OUT-OF-AUDIT-SCOPE | 6 (partial), 10, 21, 22 | 17% (4) |

**Aggregate verdict:** The passage is **structurally accurate at the system level** but **systematically under-signposts the atom-vs-constant granularity gap** and **uses one definitively overstated phrase** ("literature-anchored by construction" for RegionLink weights). With Revisions A and B applied — plus the R14 HTP/SPH-E3 cleanup elsewhere in the paper — the passage moves from "technically defensible but reviewer-misleading" to "audit-aligned."

---

## Audit-data provenance for this fact-check

- All claim attributions cross-checked against:
  - `audit_combined.csv` (16,248 rows, 9 agents merged 2026-05-17)
  - `audit_summary.md` (§Headline + §Final category distribution + §Paper revision items)
  - `escalation_resolutions.md` (46 escalations across 7 themes)
  - `2026-05-17_htp-sph-e3-structural-selection-audit.md` (R14, R14b)
  - `reconciliation_log.md` (Steps 3, 4 — pattern + citation cross-checks)
  - Per-agent summaries: Agent 1 (F1), Agent 2 (F2+F3), Agent 3 (F4+F5), Agent 4 (R³+T³), Agent 5 (F6+reward.py), Agent 6 (F7+F8), Agent 7 (RAM+regions), Agent 8 (cycle+neurochem+beliefs), Agent 9 (scaffolding).
- Targeted CSV greps performed for: Hasson, Murray, Friston, Doya, Aston-Jones, Flash-Hogan, Berlyne, IUCP, reward.py, M15/smoothness, horizon ladder, RegionLink weights — see fact-check chat trail for raw evidence rows.

**Engine state at audit close:** SHA `318eb2f5...` (FROZEN), aggregate `482ade45...`. No engine modifications introduced. This fact-check is a documentation pass over the existing audit; no source code touched.
