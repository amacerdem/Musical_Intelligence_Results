# Agent 5 — F6 + reward.py Audit Summary

**Scope:** `brain/functions/f6/*` + `brain/reward.py`
**Engine SHA:** `318eb2f5...` (frozen 2026-05-15)
**Constants audited:** 1,415
**Audit completion:** 2026-05-17
**Special role:** F-category enforcement (only scope in engine containing F constants)

---

## Headline distribution

| Cat | Count | % | Description |
|-----|-------|---|-------------|
| A | 0 | 0.0% | LIT-VERBATIM |
| B | 1 | 0.1% | LIT-DERIVED (Berlyne `4.0`) |
| C | 876 | 61.9% | STRUCTURAL (indices, dims, citation years, H3 tuples) |
| D | 35 | 2.5% | IDENTITY-PLACEHOLDER (0.0, 1.0, baseline midpoints, SOURCE_DIMS=1.0) |
| E | 497 | 35.1% | ENGINEERING-CHOICE (mixer weights, clamps, gains, predict-eq taus) |
| F | 6 | 0.4% | HAND-SPECIFIED-DISCLOSED (reward weights, ESC-1) |
| G | 0 | 0.0% | DEAD-CODE-UNREACHABLE |

**Confidence:** 99.79% HIGH, 0.21% MEDIUM, 0% LOW
**Escalations:** 3 formal + 1 critical structural (ESC-1)

---

## F-category strict enforcement (load-bearing finding)

**6 F constants found, all in `brain/reward.py`:**

| # | F symbol | Code constant | File:line | Value |
|---|----------|--------------|-----------|-------|
| 1 | w_S | W_SURPRISE | brain/reward.py:24 | 1.5 |
| 2 | w_R | W_RESOLUTION | brain/reward.py:25 | 0.8 |
| 3 | w_E | W_EXPLORATION | brain/reward.py:26 | 0.5 |
| 4 | w_M | W_MONOTONY | brain/reward.py:27 | -0.6 |
| 5 | phi_fam_star | NOT FOUND as code constant | (peak of 4f(1-f)) | 0.5 |
| 6 | g_DA_wanting | expr-literal | brain/reward.py:89 | 0.6 |
| 7 | g_DA_liking | expr-literal | brain/reward.py:89 | 0.4 |

**Critical (ESC-1):** Protocol enumerates 7 F-category items; engine code contains 6 with mappable code constants. The 7th (`phi_fam_star = 0.5`) is the mathematical-identity peak position of the `4f(1-f)` familiarity kernel — there is no separately tunable code parameter for it. Tagging one of the two `0.5` values on `brain/reward.py:83` as F would have been mis-attribution (they are the additive offset and the kernel scale, NOT the peak position). Per Rule 5 (conservative attribution) and the F-closed-list enforcement directive ("If you find an F candidate outside the 7-list above: escalate immediately"), Agent 5 reported 6 F and escalated the structural mismatch.

**Zero F constants in F6 mechanisms** — confirms the protocol prediction: "F6 mechs → must have 0 F-category constants. Reward mechs cite Salimpoor, Schultz, Berridge-Kringelbach, Mallik, Putkinen, Ferreri (LIT) and have mixer weights (E). F lives only in reward.py."

---

## Category breakdown rationale

### C (61.9%) — STRUCTURAL

Dominated by:
- **141** H3DemandSpec law-arg (T3 law field 0/1/2 — memory/forward/integration) → C
- **172** H3DemandSpec morph-arg (T3 morph operator index 0-23) → C
- **172** H3DemandSpec horizon-arg (T3 horizon index, e.g. 3, 4, 8, 16) → C
- **48** H3DemandSpec r3_idx-arg (R3 channel index 0-96) → C
- **165** module-level tuple-numeric (H3 demand tuples `(r3_idx, horizon, morph, law)`) → C
- **165** module-level int (R3 indices `_ROUGHNESS=0`, output indices `_CAUDATE_ACTIVATION=6`, etc.) → C
- **41** Citation arg1 (year metadata: 2011, 2007, etc.) → C
- **10** mechanism `OUTPUT_DIM` class attrs → C (cardinality of layer output)
- **5** torch.zeros dim args → C (fallback-tensor dimensionality)

### E (35.1%) — ENGINEERING-CHOICE

Dominated by:
- **264** expr-literal mixer coefficients (0.30, 0.25, 0.50, etc. in sigmoid/affine blends) → E4
- **74** RegionLink/NeuroLink weight args (0.75, 0.80, 0.85, 0.90, etc.) → E4
- **10** ModelMetadata confidence_range tuples (e.g. (0.85, 0.92)) → E
- **13** call-kw clamp(min=...) → E2
- **8** belief-level `_W_TREND = 0.05`, `_W_CTX = 0.02` predict-equation weights → E4
- **12** class-attr TAU (0.55, 0.6, 0.65, 0.7) belief temporal decay → E4
- **1** `_KAPPA_SOCIAL = 0.60` → E with PARTIAL (Rule R9, ESC-3)
- **1** SSRI clamp upper bound `3.0` → E with PARTIAL (ESC-4)
- Misc clamp endpoints (0.0, 1.0 as clamp args), reward.py mixer/gain constants outside F-list (PRECISION_SCALE=12.0, 0.85/0.15 emo_mod, 0.25 da_gain outer scale) → E

### D (2.5%) — IDENTITY-PLACEHOLDER

- **20+** expr-literal 1.0 (multiplicative neutral, complement in `1.0 - x`) → D
- **5** expr-literal 0.0 (additive neutral, zero-init) → D
- **11** SRP belief SOURCE_DIMS tuples with weight 1.0 (direct observe from mechanism output) → D
- **2** BASELINE = 0.5 (symmetric midpoint), **3** BASELINE = 0.0 (zero prior) → D

### B (0.1%) — LIT-DERIVED

- **1**: `4.0` on `brain/reward.py:83` (Berlyne 1971 inverted-U kernel `4f(1-f)`; form-LIT, coefficient = unit-interval normalisation identity). ESC-2.

Three additional Berlyne `4.0` instances exist in F6 mechs (`iucp/extraction.py:86`, `ssps/extraction.py:136`, embedded `zone2` in SSPS) — these were tagged E (mixer/Berlyne form embedded in a larger linear combination) rather than separately B because they are not pure normalisation of an isolated `f(1-f)` kernel but appear within multiplicative composite expressions. Reconciliation agent (Agent 6) may wish to revisit this for consistency with `brain/reward.py:83`.

### A (0.0%) — LIT-VERBATIM

Zero. No constant in F6+reward.py scope is a bit-equal published literature value. The closest candidates would have been per-edge RegionLink/NeuroLink weights (rejected per context_brief §3 — "RegionLink weights are author-normalized over a literature-cited edge set; no paper publishes per-edge weight") and Salimpoor/Berridge/Mallik citation-string r-values (these are Citation dataclass metadata, not audited constants).

### G (0.0%) — DEAD-CODE

Zero. F6 is an active code path; all 10 mechs run in the engine pipeline.

---

## Risk-area coverage

Context brief §7 risks specifically applicable to Agent 5 scope:

| Risk | Status |
|------|--------|
| §7.4 — reward.py 7 F-list strict | ENFORCED: 6 found, ESC-1 for the structural mismatch on phi_fam_star. PRECISION_SCALE=12.0 correctly DEMOTED to E. |
| §7.5 — Berlyne `4*x*(1-x)` in IUCP | Treated as B-PARTIAL in reward.py and as embedded-mixer E in IUCP/SSPS. Consistent with context_brief §7.5 caveat that the "4 and (1-x) form" might be A but here treated conservatively. |

**Not in Agent 5 scope but relevant context:** Risks §7.1 (BCH/PNH F1 mechs), §7.2 (HTP-E3/SPH-E3 structural-HYBRID), §7.3 (RAM RegionLink weights — covered by Agent 5 only for F6-local edges), §7.6 (Hasson TRW 32 horizons), §7.7 (KK 24-key profiles), §7.8 (R³ sigmoid wrappers) — these are Agents 1, 4, and 6 territory.

**Salimpoor BP_ND 0.78/0.88/0.35** — context_brief mentions these as candidate A constants in `brain/neurochemicals/{dopamine,etc.}.py`. Those files are out of Agent 5 scope (they fall under Agent 5 wider brain-infrastructure if expanded per R2, but per the agent's explicit scope filter "brain/functions/f6/* OR brain/reward.py", they were NOT audited here). Agent 6 reconciliation should confirm coverage.

---

## Doctrine compliance

- **Zero-calibration doctrine:** Confirmed — 0 LIT-VERBATIM, 0 calibrated parameters. The 6 F constants are paper-disclosed engineering choices against qualitative desiderata (per protocol). The 35.1% E rate reflects compositional engineering authorship (sigmoid mixer wrappers, channel blends, clamp endpoints).
- **Co-location ≠ derivation:** Each F6 mech `__init__.py` cites Salimpoor 2011, Berridge 2007, Mallik 2017, etc., but ZERO mixer-coefficient constants were promoted to A/B on that basis. Only the citation-metadata year fields were tagged C (structural).
- **Conservative attribution:** Every doubt resolved toward E. The single B (Berlyne `4.0`) carries a PARTIAL verification flag with escalation.
- **F-category strict:** 6 F constants, all in `brain/reward.py`. Zero F constants in 10 F6 mechs × 16 beliefs. Per protocol expectation.

---

## Files written

- `agent_5_audit.csv` — 1,415 rows, full per-constant attribution
- `agent_5_escalation.md` — 4 escalations + critical ESC-1
- `agent_5_verification_log.md` — 3 web searches + verification methodology
- `agent_5_summary.md` — this file

---

## Reconciliation hand-off notes for Agent 6

1. **ESC-1 (phi_fam_star):** The protocol's F-list says 7; Agent 5 found 6 code-mapping F constants. The 7th is a mathematical identity, not a separately tunable code parameter. If reconciliation wishes to keep "7 F" in the headline doctrine, paper §Reward should either (a) explicitly name `phi_fam_star = 0.5` in code, or (b) describe it as a kernel-peak identity rather than a 7th disclosed weight.

2. **Berlyne `4.0` consistency:** `brain/reward.py:83 4.0` is tagged B-PARTIAL. F6 mech instances (`iucp/extraction.py:86`, `ssps/extraction.py:136`) were tagged E because they appear inside multi-term mixer expressions, not as pure normalisation. Agent 6 may wish to apply a uniform decision rule across all Berlyne `4.0` instances (4 total in F6 scope).

3. **RegionLink/NeuroLink weights:** 74 link weights uniformly tagged E4 (author-normalised Likert over literature-cited edges). Agent 5 (RAM/NeuroLink scope) per protocol R2 also handles non-F6 RegionLinks — coordinate at reconciliation.

4. **Salimpoor BP_ND 0.78/0.88/0.35:** These specific values are cited in F6 mech docstrings + Citation metadata but appear as text/strings, NOT as audited numeric constants in `/tmp/agent5_scope.csv`. Agent 5 (RAM/NeuroLink scope) audits `brain/neurochemicals/*.py` where these may appear as numeric module constants.
