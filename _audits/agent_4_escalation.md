# Agent 4 — R³ + T³ escalation queue

**Engine SHA:** `318eb2f5...`
**Scope:** `ear/r3/*` + `ear/h3/*` (592 constants)
**Date:** 2026-05-17

16 constants flagged for manual review. All are B (LIT-DERIVED) or E (engineering-choice with literature-adjacent context) with MEDIUM confidence due to either (i) literature anchor present but specific value not bit-exact, (ii) author re-parameterization of cited functional form, or (iii) derived-from-parent inheritance chain where parent itself is B/PARTIAL.

---

## ESC-1 — T³ horizon duration ladder (load-bearing)

- Constant ID: `A4_0019`
- File: `ear/h3/constants/horizons.py:32`
- Name + Value: `HORIZON_MS = (5.8, 11.6, 17.4, 23.2, 34.8, 46.4, 200, 250, 300, 350, 400, 450, 525, 600, 700, 800, 1000, 1500, 2000, 3000, 5000, 8000, 15000, 25000, 36000, 60000, 120000, 200000, 414000, 600000, 800000, 981000)`
- Tentative category: **B (LIT-DERIVED)**
- Tentative confidence: MEDIUM
- Issue: The 32 specific ms values are engine-authored log-coverage motivated by but NOT bit-equal to Hasson 2008 / Lerner 2011 TRW papers. Context_brief §7.6 explicitly warns: "Do NOT tag these LIT-VERBATIM."
- Web search performed: yes (3 attempts: Hasson 2008 J Neurosci 28:2539; Lerner 2011 J Neurosci 31:2906; Murray 2014 Nat Neurosci 17:1661)
- Web search outcome: PARTIAL (TRW hierarchy concept confirmed; specific ladder NOT published)
- Verification source attempted: Hasson 2008 PMC2556707; Lerner 2011 PMC3089381
- Recommended resolution: Confirm B/MEDIUM tag is acceptable to reviewers. Could legitimately be downgraded to E (engineering choice) under strictest reading; context_brief §3 calls these "engine-authored ladder" — consider tagging as E with strong literature-inspiration note instead.

## ESC-2 through ESC-9 — Per-band DURATION_RANGE_MS / FRAME_RANGE

- Constants: `A4_0005, A4_0006, A4_0008, A4_0009, A4_0011, A4_0012, A4_0014, A4_0015`
- Files: `ear/h3/bands/{micro,meso,macro,ultra}.py`
- Category: B/MEDIUM (derived from HORIZON_MS / HORIZON_FRAMES)
- Issue: Chain-of-derivation from HORIZON_MS (itself B/MEDIUM). If ESC-1 resolves to E, these should follow.
- Recommended resolution: Inherit from ESC-1.

## ESC-10 — T³ HORIZON_FRAMES

- Constant ID: `A4_0020`
- File: `ear/h3/constants/horizons.py:77`
- Category: B/MEDIUM (derived from HORIZON_MS via max(1, round(ms/1000 * FRAME_RATE)))
- Issue: Same as ESC-1; chain-of-derivation.
- Recommended resolution: Inherit from ESC-1.

## ESC-11 — Sethares ratio tolerance σ=0.0383

- Constant ID: `A4_0199`
- File: `ear/r3/groups/a_consonance/group.py:55`
- Name + Value: `_RATIO_SIGMA = 0.0383`
- Tentative category: **B (LIT-DERIVED)**, confidence MEDIUM
- Issue: Code comment cites "Bidelman & Krishnan 2009" with "65 cents" annotation; 0.0383 ≈ log2(2^(65/1200)). Bidelman & Krishnan 2009 paper confirmed via PubMed 19925180 but specific 65-cent FFR encoding precision threshold not bit-exact in abstract/snippet.
- Web search performed: yes (3 attempts on Bidelman/Krishnan 2009 FFR + critical bandwidth + 65 cents)
- Web search outcome: PARTIAL — paper found, value not bit-exact
- Recommended resolution: B/MEDIUM with escalation note acceptable; could downgrade to E if reviewer requires bit-exact verification.

## ESC-12 — Plomp-Levelt 25% CB peak-roughness location

- Constant ID: `A4_0288`
- File: `ear/r3/groups/a_consonance/group.py:362`
- Name + Value: `cb_ratio` argument `0.25` (peak roughness at dF ≈ 0.25 × CB)
- Category: B/HIGH
- Issue: Plomp & Levelt 1965 finding "maximum dissonance at ~25% of CB" verified via review literature snippets, but original 1965 paper bit-exact placement not confirmed via free DOI access.
- Recommended resolution: B/HIGH with PARTIAL verification — standard psychoacoustics result.

## ESC-13 — Jiang 2002 spectral-contrast 7-band mel partition

- Constant ID: `A4_0488`
- File: `ear/r3/groups/j_timbre_extended/group.py:21`
- Name + Value: `_CONTRAST_BANDS = [(0,4),(4,8),(8,16),(16,32),(32,64),(64,96),(96,128)]`
- Category: B/HIGH
- Issue: Jiang 2002 ICME 7-band scheme cardinality verified; specific mel-bin endpoint values (4, 8, 16, 32, 64, 96, 128) are author octave-mapping onto 128-mel grid — not bit-equal to any Jiang publication.
- Recommended resolution: B/HIGH with PARTIAL — cardinality LIT, bin endpoints author-mapped.

## ESC-14 — Modulation rate ladder

- Constant ID: `A4_0506`
- File: `ear/r3/groups/k_modulation/group.py:15`
- Name + Value: `_MOD_RATES = [0.5, 1.0, 2.0, 4.0, 8.0, 16.0]`
- Category: B/HIGH
- Issue: Octave-spaced ladder is MIR standard (Houtgast 1985, eGeMAPS Eyben 2015) but specific 6-rate 0.5-16 Hz choice is author selection from broader literature standard.
- Recommended resolution: B/HIGH with PARTIAL.

## ESC-15 — Zwicker sharpness g(z) coefficient 0.066

- Constant ID: `A4_0564`
- File: `ear/r3/groups/k_modulation/group.py:68`
- Name + Value: `0.066` in `0.066 * math.exp(0.171 * (z + 1))`
- Tentative category: **E (re-parameterization)**, confidence MEDIUM
- Issue: Bismarck 1974 / Zwicker-Fastl 2007 g(z) functional form (exponential above z=15 Bark) is LIT-VERBATIM, but standard Bismarck parametrization is `g(z) = 0.2*exp(0.308(z-15)) + 0.8` — engine uses different coefficients 0.066/0.171. This is engine re-parameterization.
- Web search performed: yes (Salford acoustics, ANSYS sharpness docs, Bismarck reference)
- Web search outcome: NEGATIVE for 0.066/0.171 specifically; standard form is 0.2/0.308
- Recommended resolution: Confirm E5 (operational scaling re-parameterization) — already correctly tagged.

## ESC-16 — Zwicker sharpness g(z) exponent 0.171

- Constant ID: `A4_0565`
- File: `ear/r3/groups/k_modulation/group.py:68`
- Name + Value: `0.171`
- Same as ESC-15. Both 0.066 and 0.171 together constitute the re-parameterization.

---

## General notes

**No LOW-confidence constants** were generated by the audit. All 592 constants resolved to HIGH (430) or MEDIUM (162) confidence based on the verification chain.

**No F (HAND-SPECIFIED-DISCLOSED) constants** found in R³/T³ scope — correct per protocol §12.6 (F lives in `brain/reward.py` only).

**No G (DEAD-CODE) constants** found in scope. The `_clamp_bipolar` path in `pipeline/normalization.py` is technically legacy (comment notes "after the Pairwise R3 refactor Group A produces [0, 1] outputs ... this dispatch path is therefore unused") but its 3 numeric constants (-1.0, 1.0) are mathematical clamp identities, not unique-to-dead-code values — tagging them as D (IDENTITY) is more honest than G.

**Pattern-batching audit:** 421 of 592 reasons are unique (71.1%). The 171 duplicate reasons are genuinely identical engineering patterns (e.g. 14× `f_min` clamp-min=1.0 inside Sethares formula, 36× `1e-08` eps guards). Each row keeps its own constant_id + file + line + name + value + kind; only the reason cell repeats when the engineering pattern is genuinely identical. Per Rule 6 this is correct (not pattern-batching).
