# Phase 00.1 — Architectural Cardinalities — Methodology (V3 audit-anchored)

**Locked:** 2026-05-17
**Engine SHA pin:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
**Aggregate SHA:** `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`
**Supersedes:** V2 methodology (5-bucket classifier including a calibration category — retired per zero-calibration doctrine)
**Audit anchor:** `_audits/audit_combined.csv` + `_audits/INVESTIGATION-RULES.md` v1.2

## Scope

Reproduce the architectural inventory of the frozen Musical Intelligence engine: total numeric-constant count, 7-category provenance distribution, zero-calibration attestation, and discrete structural model-selection enumeration. All claims anchored on the 2026-05-17 constant-level provenance audit (9 parallel agents + reconciliation).

## Doctrine

**Zero-calibration (CODE-FIRST, 2026-05-16, refined 2026-05-17):** No numeric constant in the FROZEN engine is calibrated against cognitive data. Every constant traces to one of seven attribution categories (A-G in `INVESTIGATION-RULES.md` §2). The doctrine is operationally testable by:

1. Grep audit for `calibrated`, `fit_to`, `loss=`, optimizer call patterns in engine call-graph → ZERO matches
2. Audit attribution table → ZERO `category == "F"` outside `brain/reward.py`; ZERO `category == "A"` or `"B"` derive from optimization fit
3. The 2 discrete structural-selection picks (HTP-E3, SPH-E3) are formula-form choices, not numeric fits

## Attribution categories

| Cat | Name | What it captures |
|---|---|---|
| **A** | LIT-VERBATIM | Bit-exact published primary-source values (web-verified) |
| **B** | LIT-DERIVED | Deterministic analytical derivation from cited literature form |
| **C** | STRUCTURAL | Topology/dim/index/anatomy/citation-metadata |
| **D** | IDENTITY-PLACEHOLDER | Trivial 0/1/-1/ε guards |
| **E** | ENGINEERING-CHOICE | Mixer/clamp/sigmoid/threshold author choice (E1-E5 sub-buckets) |
| **F** | HAND-SPECIFIED-DISCLOSED | Paper §Reward disclosed weights only (closed list, 6 code-mapping constants) |
| **G** | DEAD-CODE-UNREACHABLE | Code-present-but-unreachable (zero in current engine) |

## Engine HEAD

`318eb2f529d7103e8b7d80b01228357fdc4e0217` — bit-identical to paper-freeze. Aggregate SHA-256 of all sorted `Musical_Intelligence/**/*.py` (excluding `__pycache__`): `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`.

Verifiable:

```bash
find Musical_Intelligence -type f -name "*.py" -not -path "*__pycache__*" \
  | sort | xargs -I {} shasum -a 256 {} | awk '{print $1}' | shasum -a 256 | awk '{print $1}'
```

## Audit methodology (constant-level provenance, 2026-05-17)

### Step 1 — AST inventory

The canonical AST walker (`datasets/paper-anchors/cardinality/ast_walk_v3.py`) enumerates every named-position numeric literal in the engine tree: module-level assignments, class attributes, ann-assigns, function defaults, kwargs, call positional/keyword args, and spec constructors (`LayerSpec`, `H3DemandSpec`, `RegionLink`, `NeuroLink`, `Citation`). Anonymous expression literals embedded in multi-term expressions may not all be enumerated; this is a known walker boundary.

Total enumerated: **16,248** constants.

### Step 2 — Constant-level attribution (9 parallel agents)

Each agent independently attributed every constant in its scope using a 7-rule investigation procedure (`INVESTIGATION-RULES.md` §5 v1.2):

- **Rule 1** — 3-line locality test (citation within ±2 lines of the constant)
- **Rule 2** — Block-level scope (enclosing function/method/class)
- **Rule 3** — Web search verification (mandatory for A/B; 3-attempt hallucination guard)
- **Rule 4** — Value semantics (topology/identity/reward-list/engineering/literature)
- **Rule 5** — Conservative attribution (when in doubt → E)
- **Rule 6** — Per-constant independence (no pattern-batching)
- **Rule 7** — Documentation completeness (15-column CSV)
- **Rule 8** — Checkpoint every 500 constants
- **Rule R8** (v1.2) — AST walker `citation_author` column is hint only, not evidence
- **Rule R9** (v1.2) — Form-LIT + author-coefficient → E with PARTIAL, not B

### Step 3 — Agent 10 reconciliation

After all 9 audit agents completed, Agent 10 merged the per-agent CSVs into `audit_combined.csv`, performed 5 cross-checks (duplicate, pattern, citation, confidence, distribution), and produced `bucket_distribution_real.csv` + `audit_summary.md` + `escalation_resolutions.md`.

### Step 4 — Phase 00.1 verdict

`code/run_phase1.py` reads `audit_combined.csv`, computes per-category counts, compares against paper-headline targets (post R15-R18 revision), and produces a 10-row verdict CSV at `results/01_cardinalities_correlations.csv`.

## Tolerance windows

| Claim | Tolerance |
|---|---|
| C-CARD-01-TOTAL (16,248 paper) | abs ≤ 100 (accommodates AST-walker boundary effects across version-frozen engine; current reproduction is an exact match) |
| C-CARD-02-ZERO-CALIB | exact (= 0) |
| C-CARD-03-LIT-VERBATIM (67) | abs ≤ 5 |
| C-CARD-04-LIT-DERIVED (19) | abs ≤ 5 |
| C-CARD-05-STRUCTURAL (9,817) | abs ≤ 200 |
| C-CARD-06-IDENTITY (1,182) | abs ≤ 100 |
| C-CARD-07-ENGINEERING (5,157) | abs ≤ 200 |
| C-CARD-08-HAND-DISCLOSED (6) | exact |
| C-CARD-09-DEAD-CODE (0) | exact |
| C-CARD-10-DISCRETE-SELECT (2) | exact |

## What this phase does NOT verify

- **Individual constant correctness.** This phase verifies the *distribution*; per-constant attribution is in `audit_combined.csv` and per-agent CSVs.
- **Web-search verification details.** Documented in per-agent `agent_N_verification_log.md` files.
- **Escalation queue resolution.** 46 escalations remain in `escalation_resolutions.md` for manual review; they are MEDIUM/PARTIAL outcomes that do not destabilize the verdict.
- **Engine source bytes.** Bit-identicality is verified separately via aggregate SHA-256.

## Iteration policy

The audit is one-shot at engine SHA `318eb2f5...`. The engine is FROZEN; this phase is reproducible deterministically from the vendored audit artifacts. No iteration is required.

## Outputs (canonical)

- `results/01_cardinalities_correlations.csv` — 10-row per-claim verdict
- Read-only inputs:
  - `_audits/audit_combined.csv` — 16,248-row attribution aggregate
  - `_audits/bucket_distribution_real.csv` — 7-category summary
  - `_audits/INVESTIGATION-RULES.md` — protocol v1.2
  - `_audits/audit_summary.md` — reviewer-facing synthesis
