# Agent 8 — Audit Summary

**Scope:** `brain/neurolink/* + brain/neurochemicals/* + brain/beliefs/* + brain/cycle/*`
**Resolved actual paths:** `brain/beliefs.py`, `brain/executor.py`, `brain/orchestrator.py`, `brain/neurochemicals/{__init__,manager,dopamine,norepinephrine,opioid,serotonin}.py`
**Engine SHA:** `318eb2f5...`
**Constants attributed:** 40 (26 from AST walker + 14 `REFERENCE_VALUES` dict-tuple values the walker missed, added by direct file inspection)

---

## Headline distribution

| Category | Count | % |
|---|---|---|
| **A — LIT-VERBATIM** | **0** | **0.0%** |
| **B — LIT-DERIVED** | **0** | **0.0%** |
| **C — STRUCTURAL** | **7** | **17.5%** |
| **D — IDENTITY-PLACEHOLDER** | **10** | **25.0%** |
| **E — ENGINEERING-CHOICE** | **23** | **57.5%** |
| **F — HAND-SPECIFIED-DISCLOSED** | **0** | **0.0%** (correct — F lives in `brain/reward.py`, Agent 3 scope) |
| **G — DEAD-CODE** | **0** | **0.0%** |

Confidence: HIGH=29 (72.5%), MEDIUM=11 (27.5%), LOW=0 (0%). Escalations: 16 (40%) — 11 R9-PARTIAL `REFERENCE_VALUES` entries + 5 NEGATIVE-on-stored-value BASELINE/threshold constants.

---

## Key findings

### 1. Zero LIT-VERBATIM in kernel-level cycle/neurolink/neurochem scope

This is the audit's most important finding. The kernel-level files in my scope contain **NO bit-exact published literature value**. Every constant is one of:
- **STRUCTURAL topology** (channel indices DA=0/NE=1/OPI=2/5HT=3, `_NUM_REGIONS=26`, `_NUM_NEURO=4`, Python `stacklevel=2` convention),
- **IDENTITY-PLACEHOLDER** (unit-interval clamp bounds 0.0/1.0, sentinel inits, complement expressions like `1.0 - x`),
- **ENGINEERING-CHOICE** (engine-convention baselines at midpoint 0.5, phasic threshold 0.6, robust-normalization percentiles 2.0/98.0, dynamic-range floor 0.01, and 15 author-normalized [0,1] reference values in `REFERENCE_VALUES` dicts).

This is consistent with — and strengthens — the **zero-calibration doctrine** (MEMORY: zero of 16,191 constants calibrated against cognitive data). The neurochemical kernel ships zero literature-fitted parameters.

### 2. `REFERENCE_VALUES` dicts are documentation, not runtime parameters

The 15 dict entries (0.78/0.88/0.35 caudate/NAcc/baseline DA; 0.92/0.28 levodopa/risperidone DA; 0.50/0.75/0.35 tonic/phasic/low NE; 0.85/0.30/0.40 chills/naltrexone/neutral OPI; 0.50/0.70/0.30 normal/elevated/depleted 5HT) are:

- **Form-LIT**: each cited paper (Salimpoor 2011, Ferreri 2019, Aston-Jones 2005, Blood-Zatorre 2001, Mallik 2017, Crockett 2009) is real and confirms the qualitative dissociation referenced;
- **Coefficients-author**: the stored [0,1] numeric is author re-parameterization, NOT bit-exact paper-published value. None of the cited papers publishes a 0.78 or 0.85 on a [0,1] scale; they publish raw BP_ND, rCBF changes, or VAS pleasure ratings.

Per **R9** (Form-LIT, coefficients-author → E with PARTIAL), all 15 are E-PARTIAL with escalation TRUE.

**Critical mitigation: these dicts are documentation only.** Grep confirms no import site outside the module reads `dopamine.REFERENCE_VALUES`, etc. `init_neuro` initializes only NE channel to BASELINE; `accumulate_neuro` reads per-mechanism `neuro_links` (not REFERENCE_VALUES). So the R9 PARTIAL attribution does NOT puncture zero-calibration — these are sensitivity-panel anchors / literature targets disclosed alongside the code, not load-bearing runtime weights.

### 3. Bayesian update / gain clamp `[0.20, 0.80]` NOT in my scope

The Bayesian belief cycle described in MEMORY ("predict: τμ + w_trend·M18 + w_period·M14 + w_ctx·b̄_{t-1}; gain κ ∈ [0.20, 0.80]") is NOT implemented at the kernel level. `brain/beliefs.py::compute_beliefs` is a pure weighted-sum decoder: `belief[t] = Σ(source_dim_value[t] × weight)` with clip to [0,1]. No `τ`, no `w_trend`, no `[0.20, 0.80]` gain clamp.

The Bayesian update + gain clamp constants live in per-mechanism belief Python files under `brain/functions/f*/beliefs/*/*.py`, which are Agent 1-3 territory. Agent 6 should reconcile this with their findings.

### 4. NeuroLink call sites NOT in my scope

The 54-NeuroLink (45 canonical + 9 fallback ACh/Glu/BDNF→DA + 2 alias oxytocin→OPI / cortisol→NE) routing graph is declared in per-mechanism `__init__.py` files under `brain/functions/f*/mechanisms/*`, not in the kernel-level neurochemicals package. The kernel-level `accumulate_neuro` is a generic dispatcher that reads `nucleus.neuro_links` at runtime — it does not encode routing. The 54 routings and their weights are Agent 1-3 territory.

### 5. 131 belief priors NOT in Python-constant scope

The 131-belief registry is loaded from `data/beliefs_registry.json` (a JSON data file, not Python source). Per-belief priors and source-dim weights live in JSON. The AST walker does not enumerate JSON literals. Belief priors are out of the constant-level Python audit scope.

### 6. F category strictly 0 — confirmed

The 7 HAND-SPECIFIED-DISCLOSED reward weights (`w_S=1.5, w_R=0.8, w_E=0.5, w_M=-0.6, phi_fam_star=0.5, g_DA_wanting=0.6, g_DA_liking=0.4`) live in `brain/reward.py` (Agent 3 scope). None in my files. F count = 0 ✓.

### 7. Schultz 1997 channel-index citation — co-located but not source of value

`dopamine.py:14` has `CHANNEL: int = 0` immediately following a docstring citing Schultz 1997. AST walker flagged `citation_author=Schultz`. Per **R8** (walker hint only, not evidence), I independently verified: Schultz 1997 does not "publish" the integer 0; the channel index is engine topology choice (DA happens to be in channel slot 0). Tagged STRUCTURAL (C), not LIT-VERBATIM. Same for Doya 2002 / Berridge 2003 docstring co-locations on NE/OPI/5HT channel indices.

---

## Paper revision implications

The kernel-level cycle/neurochem audit returns:
- **0% LIT-VERBATIM** in 41 constants → consistent with zero-calibration doctrine
- **15 R9 PARTIAL cases**: all in `REFERENCE_VALUES` documentation dicts, not runtime path → defensible as "literature-anchored sensitivity targets", not calibration
- **No F in scope** → confirms F is strictly closed at 7 reward weights
- **No `[0.20, 0.80]` gain clamp in scope** → kernel-level `compute_beliefs` is a pure decoder, Bayesian update lives in per-mechanism belief files (Agent 1-3 to verify)

Recommendation for §Parameter provenance / §Limitations:
- Disclose that 15 `REFERENCE_VALUES` dict entries are author-normalized [0,1] anchors (NOT bit-exact paper values) used for documentation + ±30% sensitivity panel design, not runtime cycle.
- Confirm that the four `BASELINE = 0.5` declarations are engine-convention midpoints of the unit interval (mathematical identity / engineering scaling), not literature-fitted.
- Note that the kernel-level Bayesian decoder (`compute_beliefs`) does NOT contain the Bayesian update — that lives downstream in per-mechanism belief files.

---

## Cross-agent reconciliation pointers (for Agent 6)

- **Per-mech NeuroLink declarations** (54 routings, 45 canonical + 9 fallback + 2 alias) → Agents 1-3 to enumerate at `brain/functions/f*/mechanisms/*/__init__.py`.
- **Bayesian gain clamp `[0.20, 0.80]`** → Agents 1-3 to locate in `brain/functions/f*/beliefs/*/*.py`.
- **131 belief priors** → JSON file `data/beliefs_registry.json`, out of Python-constant scope; handle separately.
- **7 F reward weights** → Agent 3 scope `brain/reward.py:33-94`.
- **RAM 529 RegionLink weights** → Agent 5 scope `brain/regions/*` per launch brief; my `executor.py:62-70` reads `n.region_links` generically but does not declare weights.
- **`brain/orchestrator.py` `FUNCTION_ORDER` tuple** → string tuple, no numeric literals; not counted.

---

## Engine state preserved

No modifications to engine code. SHA `318eb2f5...` intact.

**Deliverables:**
- `agent_8_audit.csv` (41 rows + header)
- `agent_8_escalation.md` (16 escalations, all R9 / NEGATIVE-on-stored-value pattern)
- `agent_8_verification_log.md` (per-paper web search log + R-rule application)
- `agent_8_summary.md` (this file)
