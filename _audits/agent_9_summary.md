# Agent 9 Audit Summary

**Audit window:** 2026-05-17
**Engine SHA:** `318eb2f5...` (frozen)
**Aggregate SHA:** `482ade45...`
**Investigation rules version:** v1.2 (R1-R9 integrated)
**Wall-clock time:** ~45 min (smaller scope than agents 1-8)

---

## Scope and inventory

**Agent 9 scope** (catch-all for engine paths NOT covered by agents 1-8):
- `brain/` paths NOT in `functions/`, `ram/`, `regions/`, `neurolink/`, `neurochemicals/`, `beliefs/`, `cycle/`, AND NOT `brain/reward.py`
- `scripts/*`, `contracts/*`, `data/*`, `utils/*`

**Inventory size:** 213 constants across 16 source files (full population per AST walker inventory `Musical_Intelligence_Results/datasets/paper-anchors/cardinality/raw_constants_inventory.csv`, filtered to Agent 9 path scope).

The expected ~430 sabit figure in the launch brief over-estimated; the actual walker inventory shows 213 in this scope. The discrepancy is because the walker did not index empty `brain/__init__.py` / `brain/dimensions/__init__.py` / `brain/orchestrator.py` (no numeric literals — only docstring and string tuples).

**Files audited:**

| File | Constants | Role |
|---|---|---|
| `brain/beliefs.py` | 9 | Belief computation (normalize_mechanism_outputs + compute_beliefs) |
| `brain/executor.py` | 3 | RAM accumulation + depth-ordered nucleus execution |
| `contracts/bases/base_spectral_group.py` | 4 | R³ group ABC |
| `contracts/bases/belief.py` | 25 | Core/Appraisal/Anticipation belief ABC + Bayesian cycle |
| `contracts/bases/nucleus.py` | 3 | Relay/Encoder/Associator/Integrator/Hub ABC |
| `contracts/dataclasses/__init__.py` | 9 | H3DemandSpec, LayerSpec, RegionLink, NeuroLink, Citation, CrossUnitPathway, ModelMetadata |
| `data/augmentation.py` | 19 | SpecAugment + GaussianNoise + RandomGain (training-only) |
| `data/collator.py` | 1 | MICollator (training-only) |
| `data/mi_dataset.py` | 2 | MIDataset HDF5 loader (training-only) |
| `data/precompute_cache.py` | 1 | PrecomputeCache manifest serializer (training-only) |
| `data/preprocessing.py` | 7 | Audio loading + mel-spectrogram (training utility) |
| `scripts/cleanup_dataset.py` | 18 | Dataset cleanup CLI |
| `scripts/download_playlist.py` | 7 | Spotify/YouTube downloader CLI |
| `scripts/run_pipeline.py` | 15 | Standalone pipeline CLI driver |
| `scripts/runpod_train.py` | 72 | RunPod training CLI (inline R³/H³ reimplementation) |
| `scripts/segment_dataset.py` | 18 | Audio segmenter CLI |
| **TOTAL** | **213** | |

**Note on `utils/`:** The `Musical_Intelligence/utils/` directory exists with only an empty `__init__.py` (no Python files, no numeric literals). Walker correctly skipped it.

---

## Distribution

| Category | Count | % |
|---|---|---|
| A — LIT-VERBATIM | 0 | 0.0% |
| B — LIT-DERIVED | 0 | 0.0% |
| C — STRUCTURAL | 98 | 46.0% |
| D — IDENTITY-PLACEHOLDER | 38 | 17.8% |
| E — ENGINEERING-CHOICE | 77 | 36.2% |
| F — HAND-SPECIFIED-DISCLOSED | 0 | 0.0% ✓ (mandatory 0 for this scope) |
| G — DEAD-CODE-UNREACHABLE | 0 | 0.0% |
| **Total** | **213** | **100.0%** |

**Confidence distribution:**
- HIGH: 210 (98.6%)
- MEDIUM: 3 (1.4%)
- LOW: 0 (0.0%)

**Escalations:** 3 (1.4%) — all R9 form-LIT/coeff-author boundary cases in `scripts/runpod_train.py` (CLI driver outside engine call-graph). See `agent_9_escalation.md`.

---

## Key findings

### Finding 1 — F category correctly empty (0/213)
Per investigation rules §F: "STRICTLY 7 reward weights" — all 7 disclosed weights live in `brain/reward.py` (Agent 3/5 scope; Agent 9 explicitly excludes `brain/reward.py`). Agent 9's F count must be 0 — **VERIFIED 0**.

### Finding 2 — Zero LIT-VERBATIM or LIT-DERIVED (0/213)
This scope contains no literature-verbatim or literature-derived numeric constants. The closest cases are:
- IEC 60908 sample rate 44.1 kHz — categorized STRUCTURAL (signal-processing standard, not author-tunable value) per §6.10
- Davis-Mermelstein 1980 13-MFCC, Harte 2006 6D Tonnetz, Jiang 2002 7-band spectral contrast — these are **structural cardinalities** anchored in literature but per §C "Citation metadata / topology / cardinality → STRUCTURAL"
- 3 R9 boundary cases (rolloff 0.85, modulation rates, horizons ladder) — categorized E with PARTIAL per R9 form-LIT/coeff-author rule

This **strongly supports the zero-calibration doctrine** for this scope: no constant in brain scaffolding remainder / contracts / scripts / data is a fitted literature-anchored numeric value.

### Finding 3 — STRUCTURAL dominance (98/213 = 46%)
Distribution skews heavily STRUCTURAL because contracts/, dataclasses, and CLI scripts are largely:
- API-shape constants (arg-count discriminators, positional-arg indices, tensor-rank checks)
- Cardinality constants (`_NUM_REGIONS=26`, `NUM_CHANNELS=4`, R³ dim 97, chroma 12, Tonnetz 6, MFCC 13, spectral contrast 7)
- Channel index assignments (DA=0, NE=1, OPI=2, _5HT=3)
- Depth-ordering integers (Relay=0, Integrator=3, Hub=4)
- Byte unit conversions (1024 binary KiB/MiB/GiB)
- Tensor axis specifications

This matches the expected distribution from the launch brief: "contracts/ — many citation_year values ... → STRUCTURAL (citation-metadata)".

### Finding 4 — IDENTITY-PLACEHOLDER cluster (38/213 = 17.8%)
A high fraction of constants are trivial 0.0/1.0/0.5 endpoints (clamp bounds for unit interval), counter inits, and ABC class defaults (`OUTPUT_DIM=0`, `INDEX_RANGE=[0,0]` placeholders to be overridden). Notable cluster in `contracts/bases/belief.py`: 11 IDENTITY-PLACEHOLDERs (BASELINE=0.5 midpoint; multiple `(...).clamp(0.0, 1.0)` patterns; multiplicative identity `1.0/(... + 0.1)`).

### Finding 5 — ENGINEERING-CHOICE distribution (77/213 = 36.2%)
ENGINEERING-CHOICE constants cluster in:
- **Bayesian belief base class** (`contracts/bases/belief.py`): PRECISION_SCALE=12.0, PRECISION_WINDOW=16, sigmoid slope 6.0, variability multiplier 3.0, precision clamp [0.05, 0.95], **Bayesian gain clamp [0.20, 0.80]** (explicit engineering safeguard per context_brief §2), epsilon 1e-8 numerical guards, 0.1 denominator-floor epsilons, tau_factor 0.5 offset
- **Training utilities** (`data/augmentation.py`): SpecAugment hyperparameters (F=20, T=50, mF=mT=2), GaussianNoise std=0.01, RandomGain [0.8, 1.2] symmetric range
- **CLI scripts** (`scripts/*`): subprocess timeouts (10-300s), sleep intervals, JSON pretty-print indents, terminal formatting widths, CLI argparse defaults

All consistent with context brief §2 doctrine: "Numerous σ(8·(x − 0.25)) and tanh(D/50) sigmoid wrappers across R³ atoms have engine-chosen midpoints/slopes — these are ENGINEERING-CHOICE, not LIT-DERIVED."

### Finding 6 — Bayesian gain clamp [0.20, 0.80] disclosed-doctrine consistent
The Bayesian gain `[0.20, 0.80]` clamp at `contracts/bases/belief.py:204` (A9_0036, A9_0037) is correctly tagged **ENGINEERING-CHOICE** with explicit safeguard tag per context_brief §2: "The Bayesian gain clamp `[0.20, 0.80]` is an explicit engineering safeguard preventing runaway gain at low-signal frames, documented as such (not fit)." Docstring at L192-194 ("even low-precision observations get some weight... high-precision observations don't fully override prediction") confirms engineering rationale; not literature-derived.

### Finding 7 — Scripts/ training utilities outside engine runtime call-graph
The 130 constants in `scripts/*` are CLI utilities. Internal cross-check: nothing in `brain/`, `ear/`, or `contracts/` imports from `scripts/`. Scripts CONSUME engine modules but are not consumed BY them. They are therefore **not in the engine runtime call-graph** that pins paper claims and Zenodo SHA `318eb2f5...`.

Per launch brief: "scripts/ may contain dead-code (training utilities not exercised by engine runtime). Use call-graph reachability where possible." Following Agent 5 precedent's note: "scripts/ — training utilities, not engine runtime", AND investigation rules §G: "Şüphe varsa E5 + `unreachable` tag" — these constants are tagged **E (ENGINEERING-CHOICE)** with "unreachable from engine call-graph" notes. They are not tagged G outright because they could be invoked as engine-driver entry points (e.g. `python -m run_pipeline track.mp3`), but their constants do NOT participate in the canonical orchestrator-driven engine path.

### Finding 8 — `scripts/runpod_train.py` is a parallel inline reimplementation
The 72 constants in `runpod_train.py` include duplicates of canonical engine constants (R³ dim 97, chroma 12, MFCC 13, spectral contrast 7-band, 6D Tonnetz, sample rate 44.1 kHz) because this CLI driver **reimplements** R³ feature extraction inline rather than calling `Musical_Intelligence.ear.r3`. The constants are categorized identically to their canonical counterparts in `ear/r3/groups/*` (Agent 4 scope). This duplication is not a calibration concern; it is an inline-reproduction shortcut for offline RunPod training-dataset generation.

### Finding 9 — R8 AST walker false-positive citations detected
8 distinct `citation_author` hints from the AST walker were investigated and found to be **substring false-positives** (e.g. "ding" from "padding"/"reading", "large" from "MAX_FILE_SIZE large file" comment, "deco" from "decode", "chi" from "architecture"). All independently re-categorized via 3-line locality + value semantics. See `agent_9_verification_log.md` §R8 table for full list. No misattribution to final CSV.

---

## Cross-agent reconciliation hooks

For Agent 6/10 reconciliation:

**Pattern consistency:** 
- `SAMPLE_RATE=44100` appears in 5 files (Agent 4 scope ear/r3 + Agent 9 scope data/preprocessing.py + 3 scripts). All should resolve to STRUCTURAL per §6.10. Agent 9 has tagged all 5 consistently STRUCTURAL.
- `HOP_LENGTH=256`, `N_MELS=128`, `N_FFT=2048`, `MelSpectrogram.power=2.0` similarly appear in 4 places each — all STRUCTURAL.
- `_NUM_REGIONS=26` (executor) + `26 regions` enumerated in `_REGION_NAMES` list — STRUCTURAL.
- `NUM_CHANNELS=4` (contracts/dataclasses) + `_NUM_NEURO=4` (brain/executor) — same constant in two locations, both STRUCTURAL.
- IDENTITY-PLACEHOLDER `0.0/1.0` clamp pairs — many duplicates across belief.py, beliefs.py, augmentation.py. All consistently tagged D.

**Citation consistency:**
- `IEC 60908` cited 5 times — all STRUCTURAL (per §6.10 SP standard, citation does NOT promote to A).
- `Park et al. 2019 SpecAugment` cited 4 times — all E with PARTIAL (R9 form-LIT/coeff-author boundary).
- `Davis & Mermelstein 1980`, `Harte 2006`, `Jiang 2002` — all STRUCTURAL (LIT-anchored cardinality per §C).

**Verification reuse:**
Agent 9 performed 9 distinct web queries spanning 18 constants with web-verifiable anchors. Agents 1-4 likely re-verified the same anchors (Sethares, Plomp-Levelt, Davis-Mermelstein, etc.) in their own scopes; Agent 6 should detect and consolidate.

---

## Output files

1. `agent_9_audit.csv` — 213 constants with full attribution chain
2. `agent_9_escalation.md` — 3 R9 boundary escalations (all in scripts/runpod_train.py)
3. `agent_9_verification_log.md` — 9 web verifications + R8 AST false-positive table
4. `agent_9_summary.md` — this file

---

## Audit philosophy adherence

- Per-constant independence (Rule 6): ✓ No pattern-batching; each of 213 constants has independent reason cell
- 3-line locality (Rule 1): ✓ Applied before web-search for any LIT candidate
- Conservative attribution (Rule 5): ✓ When in doubt, E. Zero A and zero B in this scope despite some literature-anchored cardinalities (correctly STRUCTURAL).
- Hallucination guard (Rule R3): ✓ Zero fabricated POSITIVE confirmations; 4 honest PARTIAL outcomes documented
- R8 AST walker hint discipline: ✓ 8 false-positive citations identified and rejected
- R9 form-LIT/coeff-author boundary: ✓ 3 escalations correctly tagged E with PARTIAL not B
- F category integrity: ✓ 0 F constants (none of the 7 disclosed weights live in this scope)

**No engine modifications made** (engine FROZEN at SHA `318eb2f5...`).
