# Agent 4 — R³ + T³ audit summary

**Agent role:** Pilot agent (validating protocol before Agents 1-3, 5 launch)
**Scope:** `ear/r3/*` + `ear/h3/*` (R³ groups A-K + T³ infrastructure)
**Engine SHA:** `318eb2f5...`
**Engine aggregate:** `482ade45...`
**Total constants audited:** 592 (actual inventory; brief estimate of ~3,500 was high — engine inventory captured 592 named-position numeric constants in scope after AST walker filtering)

---

## Counts

- Total constants audited: **592**
- **A LIT-VERBATIM: 67 (11.3%)**
- **B LIT-DERIVED: 18 (3.0%)**
- **C STRUCTURAL: 153 (25.8%)**
- **D IDENTITY-PLACEHOLDER: 70 (11.8%)**
- **E ENGINEERING-CHOICE: 284 (48.0%)**
  - E1 numerical stability: 61
  - E2 clamp/bound: 0 (subsumed into D when at unit-interval/bipolar boundaries; E1 when at ε floors)
  - E3 threshold: 18
  - E4 mixer weight: 9
  - E5 operational scaling: 196
- **F HAND-SPECIFIED-DISCLOSED: 0** (correct per protocol §12.6 — F lives only in `brain/reward.py`, not in R³/T³ scope)
- **G DEAD-CODE: 0** (legacy `_clamp_bipolar` path mentioned but its constants are mathematical identities → tagged D)

---

## Confidence distribution

- HIGH: **430 (72.6%)**
- MEDIUM: 162 (27.4%)
- LOW: 0
- Escalation flag TRUE: 16 (2.7%)

---

## Web search summary

- Total web operations: **12** (11 WebSearch + 1 WebFetch)
- POSITIVE confirmations: 7 (Sethares dyad, Zwicker-Terhardt CB, KK profiles, mel formula, IEC A-weighting, Traunmüller Bark, Stevens loudness; also Zwicker 0.11 acum)
- PARTIAL confirmations: 3 (Jiang 7-band cardinality only, modulation rate ladder convention, Bidelman 65-cent)
- NEGATIVE / NEGATIVE-UNVERIFIABLE: 1 (Hasson/Lerner specific 32-horizon ladder)
- Hallucination guard triggered: 0 times — no fabricated POSITIVE

---

## Top literature anchors verified

| Citation | A+B count | Verification |
|---|---|---|
| O'Shaughnessy 1987 / Makhoul-Cosell 1976 (mel formula) | 18 | POSITIVE |
| Harte/Sandler/Gasser 2006 (Tonnetz) | 11 | POSITIVE |
| Hasson 2008 + Lerner 2011 (TRW inspiration) | 10 | PARTIAL — paper found but specific ladder author-derived |
| Sethares 1993 (dyad dissonance kernel) | 7 | POSITIVE bit-exact via comprog.html |
| Zwicker-Terhardt 1980 (critical bandwidth) | 7 | POSITIVE via Voelk 2015 DAGA |
| IEC 61672-1 (A-weighting filter) | 6 | POSITIVE bit-exact |
| Traunmüller 1990 (Bark scale formula) | 4 | POSITIVE bit-exact |
| Zwicker & Fastl 1990 (24 Bark cardinality) | 3 | POSITIVE |
| Krumhansl & Kessler 1982 (24 key profiles) | 2 | POSITIVE bit-exact via Krumhansl-Schmuckler implementations |
| MIDI/AES Standard (A4=440, note=69) | 2 | POSITIVE definitional |
| Grabe & Low 2002 (nPVI ×100) | 2 | POSITIVE |
| Stevens 1957 (sone exponent 0.3) | 2 | POSITIVE |
| Plomp & Levelt 1965 (25% CB roughness peak) | 1 | PARTIAL |
| Bidelman & Krishnan 2009 (65-cent FFR precision) | 1 | PARTIAL |
| Jiang 2002 (7-band spectral contrast cardinality) | 1 | PARTIAL |
| Houtgast 1985; Eyben 2015 (modulation rate ladder) | 1 | PARTIAL |
| Davis & Mermelstein 1980 (MFCC DCT-II) | 1 | POSITIVE (textbook DCT-II) |
| Bismarck 1974; Zwicker & Fastl 2007 (g(z) threshold z=15) | 1 | POSITIVE |
| Zwicker & Fastl 2007 / DIN 45692 (sharpness k=0.11) | 1 | POSITIVE |
| Fisher 1925 (kurtosis 4th moment) | 1 | POSITIVE textbook |
| Fisher 1925; Box-Jenkins 1970 (morph min-windows) | 1 | POSITIVE |
| Tenney 1988 (height +1 inside log2) | 1 | POSITIVE |

---

## Risk areas surfaced

1. **R³ companion atom-level 46% rate does NOT extend to constant-level audit.** Constant-level LIT-VERBATIM rate is **11.3%** (67/592) for R³+T³ — within the expected 5-15% band from context_brief §5. Agents 1, 2, 3, 5 should anticipate similar or **lower** rates (their scopes have heavier engineering content: belief precision, RAM weights, mechanism mixers).

2. **T³ horizon ladder is the largest "near-miss" LIT case.** HORIZON_MS (32 values) and HORIZON_FRAMES (32 derived values) are inspired by Hasson 2008 / Lerner 2011 TRW papers but NOT bit-equal to either publication. Tagged B/MEDIUM with PARTIAL outcome + escalation. **Honest negative** per Rule 5 — could legitimately be downgraded to E by stricter reviewer. This is a load-bearing 64-constant block — Agents 1-3, 5 should expect similar "inspirational-only literature" patterns and resist over-attribution to LIT.

3. **Sethares formula has 14 nested `clamp(min=1.0)` engineering safeguards.** Co-location ≠ derivation: the 1.0 floor inside Sethares S=D*/(S1*f+S2) is engine numerical safeguard, NOT part of Sethares 1993 formula. Correctly tagged E1 (14 sites). Other agents will see similar patterns (ε guards inside LIT kernels) — must apply context_brief §7.8 "wrapper constants ENGINEERING even when wrapping LIT kernels" strictly.

4. **Zwicker sharpness g(z) re-parameterization.** Standard Bismarck 1974 form `0.2·exp(0.308(z-15))+0.8` vs engine `0.066·exp(0.171·(z+1))` — same functional FORM, different coefficients. Tagged E5 (re-parameterization) with PARTIAL verification + escalation. Agents may encounter similar "form-LIT, coefficients-engineering" cases — escalate them.

5. **Sigmoid/tanh wrapper density.** R³ groups B, C, D, A, G, K all contain `σ(scale·(x − midpoint))` and `tanh(x/scale)` final layers. The wrapper midpoints (0.25, 0.5, 0.3, 0.15, 0.7) and scales (8, 6, 12, 10, 4, 5) are explicitly disclosed in comments as "engine-internal" and correctly tagged E5. 47 such constants in scope — all E5.

6. **MIDI tuning constants (A4=440, note=69, 12-TET semitone count).** These are universal definitions, not single-paper citations. Tagged A with citation "MIDI/AES Standard" — defensible under "definitional" verification method.

7. **Mel-scale formula 2595/700 appears 18 times.** Standard O'Shaughnessy 1987 parametrization, used in chroma + Bark + A-weight builders. All correctly tagged A LIT-VERBATIM with POSITIVE verification. Other agents will encounter mel-scale references in MFCC; should propagate the same verification (don't re-verify each occurrence).

---

## Pilot validation feedback for protocol launch of Agents 1-3, 5

### What worked well

- **The 3-attempt hallucination guard (§3.4) is critical.** Hasson/Lerner search returned NEGATIVE bit-exact verification — the protocol correctly forced B/MEDIUM with PARTIAL outcome rather than fabricated POSITIVE. This is the audit's load-bearing anti-overclaim mechanism.
- **Rule 6 per-constant independence held up.** Even within `a_consonance/group.py` (121 constants), each row received independent attribution: 7 LIT-VERBATIM Sethares constants, 14 engineering clamps, 16 IDENTITY (clamp endpoints, inversions), 4 LIT-DERIVED (PL 25%, Sethares-σ, Tenney, parabolic-interp), and 80 ENGINEERING (sigmoid wrappers, mixer weights, thresholds). Pattern-batching avoided despite high density.
- **Context_brief §7 risk areas were correctly anticipated.** §7.6 (Hasson horizons), §7.7 (KK key_clarity 5× scaling), §7.8 (sigmoid wrappers) all surfaced in the audit at expected locations and were tagged correctly.
- **Co-location ≠ derivation enforced.** AST walker auto-tagged ~70 rows with `citation_author=helmholtz/sethares/zwicker/stumpf/ding/hannon` based on nearby docstring text. The audit ignored those false-positive auto-citations and re-evaluated each constant on its own merits — most were E or D, not A/B.

### Issues encountered

- **AST walker citation-author field is unreliable.** It picks up `cit=hannon` / `cit=ding` from comments that don't actually mention these authors as the *constant's* primary source. Agents 1-3, 5 should NOT use `citation_author` as a hint without verifying the locality independently. Recommended addition to launch command: "AST walker's citation_author column is co-location-only; verify per Rule 1 3-line locality."

- **F-category boundary is razor-sharp.** F is strictly the 7 reward weights. The "F? Maybe?" decision tree never triggered in R³/T³ (correctly — F is brain/reward.py only). Agents 1, 2 should be especially careful in F2 HTP-E3 + F5 mechanisms where reward-like constants appear; refer back to §12.6 explicitly.

- **C vs D boundary needs sharpening.** Initially had ambiguity around `1.0` constants in `1.0 - x` inversion patterns — are these IDENTITY (1.0 is mathematical identity element) or STRUCTURAL? Settled on D (IDENTITY-PLACEHOLDER) per §2 example "1.0 init/sentinel". Recommendation: launch command could clarify "1.0 inside (1.0 - x) inversion = IDENTITY; 1.0 as clamp endpoint = IDENTITY; 1.0 as multiplicative gain = ENGINEERING."

- **Verification source field for definitional citations.** Used "definitional" as verification_method for MIDI tuning (A4=440) and 12-TET (12 semitones/octave) — these are universal standards without a single-paper anchor. Agents 5 (working on neurochem channels DA/NE/OPI/5HT) will encounter similar "no single primary paper" cases for foundational pharmacology constants.

### Recommended additions to launch command for other agents

```
6.5. (NEW) AST walker's citation_author column is co-location only; verify 
     independently per Rule 1 3-line locality. Many auto-tagged authors 
     (e.g. "hannon", "ding") are false-positives from nearby unrelated comment 
     mentions. The walker correctly captures author names that appear nearby 
     but doesn't verify that the citation applies to the specific constant.

11.5. (NEW) If a literature anchor is verified as functional FORM but coefficients 
      differ (e.g. cited paper says exp(a·z) but code uses different a), tag E 
      (re-parameterization) with PARTIAL verification + escalation, not B. Form-LIT 
      / coefficients-author cases are E.
```

### Time budget actually consumed

- File reads + scope inventory: ~25 minutes
- Web verification (12 queries): ~30 minutes
- Decision-tree implementation: ~45 minutes
- Final pass + escalation log + verification log + summary: ~30 minutes
- **Total: ~2 hours wall-clock** (well under the 4-6 hour budget)

The lower-than-budget time is because R³/T³ scope was 592 constants (not 3,500 estimated). Per-constant pace was actually ~12 seconds/constant average, which is consistent with the time-budget assumption of "C/D/E fast triage 2-5s, A/B verification 1-2 min." Other agents with larger scopes (Agent 1-3 at ~3,000+ each, Agent 5 at ~3,700) should still budget 4-6 hours for their bigger queues.

### Expected dispersion for other agents (calibrated by Agent 4 results)

- Agent 1 (F1+F2 mechanisms): expect LIT-VERBATIM ~5-10% (less than R³ because F2 mixer-heavy)
- Agent 2 (F3+F4+F5): expect LIT-VERBATIM ~3-7% (heavy on engineering mixers + clamp endpoints)
- Agent 3 (F6+F7+F8): expect LIT-VERBATIM ~5-10% (Salimpoor/Doya BP_ND constants are clean LIT)
- Agent 5 (RAM+NeuroLink+reward+scaffolding): expect LIT-VERBATIM ~10-15% (MNI centroids + pharma reference values; but RAM 529 edge weights are E4)

Total engine-wide estimate: A 6-10% (1,000-1,600 of 16,191), B 4-8%, C 30-35%, D 8-12%, E 35-45%, F=7 (exact), G ~50-150. **This bounds the audit's load-bearing finding: zero-calibration doctrine is honest only if the 90+% non-LIT constants are E/C/D — not F or undisclosed.**
