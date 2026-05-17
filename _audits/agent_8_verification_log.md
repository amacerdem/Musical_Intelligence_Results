# Agent 8 — Verification Log

**Agent scope:** `brain/neurolink/*`, `brain/neurochemicals/*`, `brain/beliefs/*`, `brain/cycle/*` (per launch brief).

**Actual engine paths in scope (resolved):**
- `brain/neurolink/*` → not a directory; NeuroLink consumption logic lives in `brain/neurochemicals/manager.py::accumulate_neuro` (already covered) and per-mech `NeuroLink` declarations live under `brain/functions/f*/mechanisms/*/__init__.py` (those module-level declarations are Agent 1/2/3 territory by per-function decomposition; NeuroLink contract & accumulator logic is in scope here).
- `brain/neurochemicals/*` → 6 files in scope: `__init__.py`, `dopamine.py`, `norepinephrine.py`, `opioid.py`, `serotonin.py`, `manager.py`.
- `brain/beliefs/*` → not a directory; the kernel-level belief computation is in `brain/beliefs.py` (single file). Per-mech belief registry priors (131 beliefs) are loaded at runtime from `data/beliefs_registry.json` (a JSON data file, not numeric Python constants — out of constant-audit scope per AST-walker output). Per-mech belief Python source files live under `brain/functions/f*/beliefs/*` and are owned by Agents 1-3.
- `brain/cycle/*` → not a directory; the Bayesian cycle implementation is split between `brain/orchestrator.py` (top-level `BrainOrchestrator.process`) and `brain/executor.py` (depth-ordered `execute` loop with RAM + neuro accumulation). Both in scope.

**Constant population:** 40 attributed constants total. Lower than the ~2,500 estimate in launch brief — the estimate appears to have included per-mech belief priors (which live under `brain/functions/f*/beliefs/*` and are covered by Agents 1-3) and per-mech NeuroLink declarations (also under `brain/functions/f*/mechanisms/*`, owned by Agents 1-3). The kernel-level cycle/neurolink/neurochem/beliefs surface is intentionally small (40 constants) because the engine factors most belief/neurolink configuration into per-mechanism `__init__.py` declarations, not central module constants. This is a structural observation, not a coverage gap — the 40 constants comprise the 26 AST-walker-enumerated rows for these paths plus 14 `REFERENCE_VALUES` dict-tuple values the walker missed but I added by direct file inspection.

**Census breakdown:**

| File | Walker count | Audit count | Notes |
|------|--------------|-------------|-------|
| `brain/beliefs.py` | 9 | 9 | full coverage |
| `brain/executor.py` | 3 | 3 | full coverage |
| `brain/orchestrator.py` | 0 | 0 | only string-tuple `FUNCTION_ORDER` (no numeric literals); 26-string `_REGION_NAMES` lives in `executor.py` not orchestrator |
| `brain/neurochemicals/__init__.py` | 1 | 1 | `stacklevel=2` |
| `brain/neurochemicals/dopamine.py` | 3 | 8 | walker missed 5 `REFERENCE_VALUES` tuple values |
| `brain/neurochemicals/norepinephrine.py` | 2 | 5 | walker missed 3 dict tuple values |
| `brain/neurochemicals/opioid.py` | 2 | 5 | walker missed 3 dict tuple values |
| `brain/neurochemicals/serotonin.py` | 2 | 5 | walker missed 3 dict tuple values |
| `brain/neurochemicals/manager.py` | 4 | 4 | full coverage (3 walker hits + 1 `<expr-L>` 1.0) |
| **Total** | **26** | **40** | |

---

## Web search log

### Salimpoor 2011 — DA caudate/NAcc

- **Query 1:** `"Salimpoor 2011 Nature Neuroscience caudate nucleus accumbens BP_ND dopamine raclopride music chills"`
- **Outcome:** POSITIVE on paper identity (Nat Neurosci 14:257-262, 2011)
- **Specific values 0.78/0.88/0.35 verification:** NEGATIVE
- **Query 2 (refined):** `"Salimpoor" "binding potential" raclopride "5.7" OR "8.4" caudate accumbens percentage decrease`
- **Outcome:** PARTIAL — paper confirmed but specific BP_ND % decrease values not surfaced in abstract/snippet
- **WebFetch attempt on full PDF:** permission denied
- **Conclusion:** Salimpoor 2011 paper confirmed as legitimate reference for caudate-leads-NAcc DA dissociation; the stored 0.78/0.88/0.35 are clearly NOT raw BP_ND percentages (which would be 0.057/0.084 if normalized as decimals); they are author-normalized [0,1] reference values. **R9: Form-LIT, coefficients-author re-parameterization → E with PARTIAL verification.** Reference dict is documentation-only (not a runtime cycle constant) so the engineering attribution does not affect MI's zero-calibration doctrine.

### Mallik 2017 — naltrexone musical anhedonia

- **Query:** `"Mallik 2017 naltrexone music pleasure reduction percent Scientific Reports"`
- **Outcome:** POSITIVE on paper identity (Sci Rep 7:41952, 2017; N=17 → 15 after exclusions; subjective MIDI-slider 0-100; p<0.05 reduction for pleasurable music)
- **Specific value 0.30 verification:** NEGATIVE — no published "0.30" subjective rating value
- **Conclusion:** R9 re-parameterization; author normalization on [0,1] of 0-100 MIDI slider scale → E PARTIAL.

### Ferreri 2019 — levodopa/risperidone

- **Query:** `"Ferreri 2019 PNAS levodopa risperidone music pleasure percentage change"`
- **Outcome:** POSITIVE on paper identity (PNAS 116:3793-3798, 2019; N=27 double-blind crossover)
- **Specific values 0.92/0.28 verification:** NEGATIVE
- **Conclusion:** R9 re-parameterization → E PARTIAL.

### Blood & Zatorre 2001 — chills PET

- **Query:** `"Blood Zatorre 2001 PNAS music chills regional cerebral blood flow nucleus accumbens"`
- **Outcome:** POSITIVE on paper identity (PNAS 98:11818-11823, 2001)
- **Specific value 0.85 verification:** NEGATIVE — paper measures rCBF changes, not normalized [0,1] OPI values; no published "0.85" baseline
- **Conclusion:** R9 → E PARTIAL.

### Aston-Jones & Cohen 2005 — LC-NE adaptive gain

- **Query:** `"Aston-Jones Cohen 2005 locus coeruleus norepinephrine tonic phasic baseline 0.50 0.75 values"`
- **Outcome:** POSITIVE on paper identity (Annu Rev Neurosci 28:403-450, 2005)
- **Specific values 0.50/0.75 verification:** NEGATIVE — paper describes phasic/tonic LC modes qualitatively; the specific 0.50 baseline and 0.75 burst values are not in the published abstract/snippet
- **Conclusion:** R9 → E PARTIAL.

### Doya 2002 — neuromodulator metalearning framework

- **Query:** `"Doya 2002 Neural Networks metalearning dopamine serotonin norepinephrine acetylcholine framework table"`
- **Outcome:** POSITIVE on paper identity (Neural Networks 15:495-506, 2002); framework confirmed (DA = TD-error, 5HT = γ discount factor, NE = β inverse temperature, ACh = α learning rate)
- **Numeric values verification:** N/A — Doya 2002 is a framework paper, no specific numeric calibration values
- **Conclusion:** Doya 2002 is a STRUCTURAL framework citation, not a numeric provenance source. The channel-index assignments (DA=0, NE=1, OPI=2, 5HT=3) are STRUCTURAL topology choices, not Doya-derived.

### Berridge 2003 — wanting/liking dissociation

- **Query:** `"Berridge Robinson 2003 wanting liking dopamine opioid dissociation reward"`
- **Outcome:** POSITIVE — wanting/liking framework confirmed (DA = wanting, OPI = liking; hedonic hotspots opioid-mediated)
- **Numeric values verification:** N/A — framework paper, no numeric anchors for the stored normalized values
- **Conclusion:** STRUCTURAL framework citation; supports OPI channel existence but not numeric values.

---

## Category distribution (40 total)

| Category | Count | % | Notes |
|---|---|---|---|
| A — LIT-VERBATIM | 0 | 0.0% | No bit-exact literature-published value in scope |
| B — LIT-DERIVED | 0 | 0.0% | No deterministic literature-formula derivation in scope |
| C — STRUCTURAL | 7 | 17.5% | 4 channel indices (DA=0/NE=1/OPI=2/5HT=3) + `_NUM_REGIONS=26` + `_NUM_NEURO=4` + `stacklevel=2` (Python warnings convention) |
| D — IDENTITY-PLACEHOLDER | 10 | 25.0% | Unit-interval clamp bounds (0.0/1.0), sentinel inits (T=0), complement expressions (1.0 in 1-x) |
| E — ENGINEERING-CHOICE | 23 | 57.5% | Author-normalized [0,1] reference values + percentile thresholds + baseline midpoints + phasic threshold |
| F — HAND-SPECIFIED-DISCLOSED | 0 | 0.0% | Correct — F is strictly 7 reward weights in `brain/reward.py` (Agent 3 scope), MUST be 0 here |
| G — DEAD-CODE | 0 | 0.0% | `brain/neurochemicals/__init__.py` is deprecated (emits DeprecationWarning) but still in import path used by `brain/executor.py`; not unreachable |

**Verified counts (from CSV grep):**
- C: 7
- D: 10
- E: 23
- Total: 7 + 10 + 23 = 40 ✓

---

## Confidence distribution

| Confidence | Count | % |
|---|---|---|
| HIGH | 29 | 72.5% |
| MEDIUM | 11 | 27.5% |
| LOW | 0 | 0.0% |

Escalation flag: TRUE in 16 of 40 (40%). 11 MEDIUM-confidence R9 cases (REFERENCE_VALUES dict entries) + 5 HIGH-confidence NEGATIVE-on-stored-value cases (BASELINE / PHASIC_THRESHOLD constants where the stored numeric is engine-convention midpoint with no literature anchor — high confidence in the negative result).

---

## Critical attention-area findings

1. **NeuroLink call-site count (54: 45 canonical + 9 fallback + 2 alias):** Not enumerable from kernel scope. NeuroLink declarations live in per-mechanism `__init__.py` files under `brain/functions/f*/mechanisms/*`, each declaring a `neuro_links` tuple. Those are Agent 1-3 territory. The kernel-level accumulator in `brain/neurochemicals/manager.py::accumulate_neuro` is generic dispatch logic — it does not encode which mech routes to which channel.

2. **Pharmacology reference values (Salimpoor 0.78/0.88/0.35, Aston-Jones 0.50/0.75, Blood-Zatorre 0.85, Mallik 0.30, Ferreri 0.92/0.28):** ALL E (ENGINEERING-CHOICE) with PARTIAL verification. The papers are real and confirm the qualitative findings, but **none of the stored numeric values is bit-exact from the cited paper**. They are author-normalized [0,1] reference values. Critically: these dict entries are documentation/reference-only — they are NOT consumed by the runtime cycle. `init_neuro` initializes only `NE` to BASELINE=0.5; `accumulate_neuro` reads only NeuroLink weights (per-mech declarations, Agent 1-3 scope), not REFERENCE_VALUES. So even though they are E (not A/B), they do NOT puncture the zero-calibration doctrine — they are sensitivity-panel anchors / documentation, not runtime parameters.

3. **Bayesian gain clamp `[0.20, 0.80]`:** NOT in my scope. The kernel-level Bayesian belief cycle in `brain/beliefs.py` does NOT implement Bayesian update — it only computes weighted-sum belief traces from mechanism outputs and clips to [0.0, 1.0] (D, identity bounds). The Bayesian update (predict: τμ + w_trend·M18 + w_period·M14 + w_ctx·b̄; gain κ ∈ [0.20, 0.80]) appears to live in per-mechanism belief `.py` files under `brain/functions/f*/beliefs/*/*.py`, owned by Agents 1-3. **My scope contains no [0.20, 0.80] clamp.**

4. **131 belief priors:** Not in my Python-constant scope. The 131-belief registry is loaded from `data/beliefs_registry.json` at runtime by `brain/beliefs.py::get_beliefs_registry`. Per-belief weights and priors live in the JSON, not as named Python constants. JSON data is out of the AST-walker numeric-literal census.

5. **4-neuromodulator channels (DA=0, NE=1, OPI=2, 5HT=3) reference values:** Channel indices = STRUCTURAL (C). Engine-convention BASELINE=0.5 on each = ENGINEERING (E5). Reference dicts = ENGINEERING (E5) PARTIAL.

6. **F category strictly 0 in my scope:** Confirmed. The 7 disclosed reward weights live in `brain/reward.py` (Agent 3 scope), not anywhere in my files.

---

## R-rule applications

- **R5 (DEAD-CODE):** None found. `brain/neurochemicals/__init__.py` emits `DeprecationWarning` but is still in the active import path used by `brain/executor.py:21` → `from Musical_Intelligence.brain.neurochemicals.manager import accumulate_neuro, init_neuro`. The package-level deprecation is for downstream imports; the inner module `manager.py` is reachable runtime code.

- **R8 (AST walker citation_author hint only):** Applied. Walker tagged `dopamine.py:14` with `citation_author=Schultz` and `serotonin.py:14` with `citation_author=Doya`. I independently verified via 3-line locality (citations are in module docstring) and web search (papers confirmed) before assigning category — the channel-index constants remain STRUCTURAL regardless of citation co-location because they encode topology, not empirical value.

- **R9 (form-LIT / coefficients-author re-parameterization):** Applied to all 15 `REFERENCE_VALUES` dict entries. Form (caudate>NAcc anticipatory bias; OPI peak during chills; naltrexone reduces pleasure; levodopa enhances / risperidone blocks; tonic vs phasic LC) is literature-confirmed; coefficients (0.78, 0.88, 0.35, 0.85, 0.30, 0.92, 0.28, 0.50, 0.75, 0.35, 0.40, 0.50, 0.70, 0.30) are author re-parameterization onto [0,1] scale → E with PARTIAL, escalation TRUE.
