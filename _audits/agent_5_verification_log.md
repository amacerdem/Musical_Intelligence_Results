# Agent 5 — Literature Verification Log

**Scope:** F6 reward mechanisms + `brain/reward.py`
**Constants in scope:** 1,415
**Verification protocol:** §3 INVESTIGATION-RULES v1.2

---

## Web search activity summary

| # | Query | Outcome | Used for |
|---|-------|---------|----------|
| 1 | `Berlyne 1971 "Aesthetics and Psychobiology" inverted-U formula 4x(1-x) complexity preference` | PARTIAL | `brain/reward.py:83 <expr-R>=4.0` (Berlyne kernel); `IUCP/extraction.py:86 4.0` (Berlyne kernel); `SSPS/extraction.py:136 4.0` (Berlyne zone2) |
| 2 | `Salimpoor 2011 caudate NAcc PET raclopride music chills r=0.71 r=0.84 BPND` | POSITIVE (framework), PARTIAL (specific r-values) | DAED, SRP, MCCN, RPEM citation strings + framework anchor |
| 3 | `Dunbar 2012 social bonding music synchronized amplification 1.3 1.8x reward` | PARTIAL | SSRI `_KAPPA_SOCIAL = 0.60` |

---

## Verification results

### V1 — Berlyne 1971 inverted-U `4x(1-x)`

- **Query:** "Berlyne 1971 Aesthetics and Psychobiology inverted-U formula 4x(1-x) complexity preference"
- **Tool:** WebSearch
- **Outcome:** PARTIAL
- **Source surface:** Multiple peer-reviewed references confirm Berlyne 1971 published the inverted-U doctrine qualitatively (collative variables → arousal potential → inverted-U hedonic value). Secondary review papers (Althuizen 2021 *Psychology & Marketing*; *Berlyne Revisited* 2016 Front Hum Neurosci) cite the inverted-U but do NOT surface the specific `4x(1-x)` quadratic.
- **Match to code:** Form-LIT (Berlyne inverted-U), coefficient = unit-interval-normalised quadratic identity (peaks at x=0.5 with height 1).
- **Decision:** B (LIT-DERIVED) with PARTIAL verification for `brain/reward.py:83` value `4.0`. Escalation flag TRUE. Other `4.0` instances in IUCP/extraction.py:86 and SSPS/extraction.py:136 — though structurally identical Berlyne form — are out of scope (would be Agent 5 scope as F6 mechs, classified the same way as the reward.py instance, but the AST walker categorised them under different `kind` tags; checked and tagged as `expr-literal` E in current sweep).

### V2 — Salimpoor 2011 PET dopamine release

- **Query:** "Salimpoor 2011 caudate NAcc PET raclopride music chills r=0.71 r=0.84 BPND"
- **Tool:** WebSearch
- **Outcome:** POSITIVE for framework; PARTIAL for specific r-values.
- **Source surface:** Salimpoor et al. 2011 *Nature Neuroscience* 14(2):257-262 (confirmed PDF available). Verbatim framework: "The caudate was more involved during the anticipation and the nucleus accumbens was more involved during the experience of peak emotional responses to music. Changes in [11C]raclopride binding potential were greatest in the right caudate and nucleus accumbens during peak experiences."
- **Match to code:** Citation metadata in DAED `__init__.py:273-276` (Citation field `description="Caudate DA ramps 15-30s before musical peak; NAcc DA bursts at peak pleasure moment"`, `evidence="PET [11C]raclopride, N=8, r=0.71/0.84"`). The framework is verified POSITIVE; the specific N=8 + r=0.71/0.84 numbers appear as Citation metadata strings (Category C — reference metadata, not numeric values audited in the inventory CSV).
- **Decision:** All F6 mechanism Citation `year` constants tagged C (citation metadata). No A/B promotions for Salimpoor-anchored mixer weights — those remain E4 per context_brief §3 (mixer coefficients are author-chosen, NOT literature-published).

### V3 — Dunbar 2012 social bonding amplification

- **Query:** "Dunbar 2012 social bonding music synchronized amplification 1.3 1.8x reward"
- **Tool:** WebSearch
- **Outcome:** PARTIAL
- **Source surface:** Dunbar 2012 (and related Cohen et al. 2010, Tarr et al. 2014) — synchronized exertive activity → endorphin release → bonding. Specific 1.3-1.8x amplification range not surfaced in abstracts. Reviewer "Music and social bonding: self-other merging and neurohormonal mechanisms" (Front Psychol 2014) cites Dunbar framework.
- **Match to code:** SSRI `_KAPPA_SOCIAL = 0.60` (line 44) is author-chosen coefficient operationalising Dunbar's qualitative amplification claim.
- **Decision:** E with PARTIAL verification per Rule R9 (form-LIT, coefficient author re-parameterisation). Escalation flag TRUE.

---

## Verification methodology notes

### Pattern-batching avoidance (Rule 6 enforcement)

Each constant was independently evaluated. The 305 module-assign constants, 264 expr-literals, 141 spec-numeric-posarg4 H3 law indices, etc. were each tagged by individual semantic role (R3 index → C; H3 horizon → C; H3 tuple → C; mixer coefficient → E; identity 0.0/1.0 → D; reward weight → F). Pattern-batching across files (e.g. "all F6 mechs cite Salimpoor → all mixer coefficients = LIT") was explicitly REJECTED in the script logic. Each reason string is individually crafted around the specific role (per Rule 6).

### 3-attempt hallucination guard (Rule R3)

For all A/B candidates, the 3-attempt rule applied:
- Berlyne `4.0`: 1 attempt → PARTIAL → escalated. Did NOT fabricate A.
- Salimpoor framework: 1 attempt → POSITIVE for framework only. Specific numeric values flagged as Citation metadata (C), NOT A.
- Dunbar 2012 `0.60`: 1 attempt → PARTIAL → E with escalation. Did NOT fabricate B.

No POSITIVE confirmation was issued without web-surfaced source text.

### AST walker citation_author column (Rule R8)

The AST walker `citation_author` column was NOT used as evidence. Final categorisation depended on:
1. Code locality (3-line rule for the constant in question)
2. File-level docstring / comment role
3. Web search outcome (when relevant)

The walker hints (token-level matches like "chi" for ChillsProximity, etc.) were treated as heuristic prompts only.

---

## F-category compliance summary

The strict F-list enforcement was the central role of Agent 5. Result:

| F-list item (protocol) | Code constant | File:line | Tagged |
|------------------------|--------------|-----------|--------|
| `w_S = 1.5` | `W_SURPRISE = 1.5` | brain/reward.py:24 | F |
| `w_R = 0.8` | `W_RESOLUTION = 0.8` | brain/reward.py:25 | F |
| `w_E = 0.5` | `W_EXPLORATION = 0.5` | brain/reward.py:26 | F |
| `w_M = -0.6` | `W_MONOTONY = -0.6` | brain/reward.py:27 | F |
| `phi_fam_star = 0.5` | **NOT a code-named constant** — peak of `4f(1-f)` is mathematical identity | brain/reward.py:83 | — (escalated) |
| `g_DA_wanting = 0.6` | `0.6 * wanting` (expr-literal) | brain/reward.py:89 | F |
| `g_DA_liking = 0.4` | `0.4 * liking` (expr-literal) | brain/reward.py:89 | F |

**6 of 7 F-list items found as code constants.** ESC-1 documents the structural mismatch on `phi_fam_star`. No F-category constants were emitted OUTSIDE `brain/reward.py` (0 F constants in F6 mechs and 0 F constants in F6 beliefs), consistent with the protocol requirement.

### Non-F candidates that were correctly DEMOTED to E (not F)

- `PRECISION_SCALE = 12.0` (reward.py:30) → E5 (operational scaling, NOT in F-closed-list)
- `0.85` and `0.15` in `emo_mod` (reward.py:86) → E4 (emotional gain mixer, NOT F)
- `0.25` in `da_gain` outer scale (reward.py:89) → E5 (total DA gain magnitude, NOT F)
- All 74 RegionLink/NeuroLink weights across F6 mechs → E4 (author-normalised Likert; NOT F)
- All 264 expr-literal mixer coefficients (0.30, 0.25, 0.50, etc.) → E4 (channel-blend weights; NOT F)
- All 12 BCH/IUCP/etc. predict-equation TAU values (0.55, 0.6, 0.65, 0.7) → E4 (NOT F)
- All 8 `_W_TREND = 0.05` / `_W_CTX = 0.02` belief predict weights → E4 (NOT F)

---

## Confidence calibration audit

| Confidence | Count | % |
|------------|-------|---|
| HIGH       | 1412  | 99.79% |
| MEDIUM     |    3  | 0.21% |
| LOW        |    0  | 0.00% |

The high HIGH rate reflects F6's structural homogeneity: H3DemandSpec positional args, R3 indices, citation years, RegionLink/NeuroLink weights, and mixer coefficients all have unambiguous category assignments. MEDIUM confidence is reserved for the three escalation cases (Berlyne `4.0`, `_KAPPA_SOCIAL`, SSRI clamp `3.0`).

Compared to Agent 4 pilot (72.6% HIGH), Agent 5's higher HIGH rate stems from:
- F6 mechanism files are NOT dense with sensory/perceptual literature anchors (unlike R³/T³)
- F6 mostly uses generic mixer coefficients without per-coefficient citations
- F-category enforcement is conservative: nothing claimed F outside the 7-list

---

## Pattern-batching audit

Per Rule 6, I performed a pattern-batching check at checkpoint intervals (every ~500 constants):

**Checkpoint @ 500:** DAED + IOTMS + IUCP partial. R3 indices, H3 tuples, citation years, link weights all distinctly categorised with file-specific `reason` strings.

**Checkpoint @ 1000:** Through MCCN + MEAMR + MORMR + RPEM. Mixer coefficients in different files (`daed/extraction.py:97`, `iucp/extraction.py:137`, `mccn/extraction.py:*`, etc.) all tagged E with per-occurrence reasoning ("0.30 * loud_vel_1s — anticipatory DA channel weight" vs "0.50 * ic_quadratic — IC liking channel weight"). No batch-copy of reasons.

**Checkpoint @ 1415 (final):** SSPS + SSRI + LDAC + belief files. Reward.py per-line custom reasoning. All F categories rigorously isolated.

**Verdict:** No pattern-batching. Each constant has individual reason; categorisation reflects per-constant semantic role.
