# Phase 1 — Architectural Cardinalities — Provenance Chain

## Paper anchor

**Source:** `The Paper/Nature-Neuroscience/revision/Musical_Intelligence_AE.tex`

- **Line 585** (§Architectural cardinalities): "97 R³ … 32 × 24 × 3 = 223,488 theoretical 4-tuples (~8,600 active at runtime, ~3.85% sparsity); 89 mechanism modules across F1-F8; 121 belief classes in F1-F8 (34 Core + 59 Appraisal + 28 Anticipation), with 10 additional F9-bound kernel-only beliefs (SSRI, NSCP, DDSMI relays) bringing the full runtime registry to 131; 26-dimensional Region Activation Map (12 cortical, 9 subcortical, 5 brainstem); 4 canonical neurochemical channels (DA, NE, OPI, 5-HT) with 48 NeuroLink resolutions; 529 RegionLinks; and 16,191 declared numeric constants (full inventory in Supplementary Table S-Provenance)."

- **Line 581** (§Three constant counts): "16,191 declared numeric constants … 856 .py files … 7,517 compute-path total = 7,256 static-array elements + 261 compile-time scalars … lenient classifier: HAND-TUNED = 495 / 3.1%, CALIB-BOWLING = 246 / 1.5%."

- **Line 575** (§PRISMA): "Mechanism-to-region routing edges (529 RegionLinks) and mechanism-to-neuromodulator-channel routing (48 NeuroLinks) were declared per-mechanism from the cited fMRI/PET/pharmacology evidence, not learned from data."

## Code provenance

**Engine root:** `Science/Musical_Intelligence/` (in this repo). Bit-identical to engine HEAD `318eb2f529d7103e8b7d80b01228357fdc4e0217` per `git diff 318eb2f5 HEAD -- Science/Musical_Intelligence/` (empty diff, verified 2026-05-06).

**Per-mechanism RegionLink declarations:** `Science/Musical_Intelligence/brain/functions/{f1..f8}/mechanisms/<mech>/__init__.py` (each mechanism class exposes `region_links` and `neuro_links` properties).

**RegionLink dataclass:** `Science/Musical_Intelligence/contracts/dataclasses/__init__.py:77-95` (slots: `dim_name`, `region`, `weight`, `citation`).

**NeuroLink dataclass:** `Science/Musical_Intelligence/contracts/dataclasses/__init__.py:106-168` (channel mapping `_MODULATOR_TO_CHANNEL` collapses raw call sites — DA/NE/OPI/5HT canonical labels + variants like `dopamine`, `Dopamine`, `oxytocin→OPI`, `cortisol→NE`).

**Region registry:** `Science/Musical_Intelligence/brain/regions/registry.py:50-67` (`ALL_REGIONS` tuple of 26 items, `assert NUM_REGIONS == 26`).

**Mechanism base:** `Science/Musical_Intelligence/contracts/bases/nucleus.py` (`_NucleusBase` exposes `region_links`, `neuro_links`, `h3_demand`).

**Executor (RAM accumulation path):** `Science/Musical_Intelligence/brain/executor.py:62` (iterates `n.region_links` per mechanism for RAM accumulation).

## V1 cross-check

**Source:** `Science/V1/results/All_Results/All_Results.md`

- Line 232–233: "Total RegionLinks 529 … Canonical matches 529/529 (100%)"
- Line 264: "Total NeuroLinks 48"
- Line 234: "RAM accumulation tests 445/445 (100%)"

V1 was the paper-submission v1 evidence base; results are FROZEN per `Science/V1/CLAUDE.md`. V-Reproduction does not modify V1. Phase-1 reproduces these counts independently from V1's run.

## Engine HEAD pin

`_infra/manifests/engine_head.json` — `318eb2f529d7103e8b7d80b01228357fdc4e0217` (frozen since pre-V1 per user 2026-05-06 confirmation; all V1/V2/V3/V4/V5/V6 cycles ran against this engine).

## Seed registry

`_infra/manifests/seed_registry.json` — `phase_01.primary = 2026050601`, `bootstrap = 1729`, `permutation = 42`. LOCKED.

## Date of reproduction

2026-05-06 (Phase-1 first run).

## Iteration history

Recorded in `04-INTEGRATION-LOG.md` as iterations occur. Each iteration preserves a results snapshot under `results/iterations/iter_NN_<timestamp>/`.

## Honesty note on F9

The paper says "10 additional F9-bound kernel-only beliefs (SSRI, NSCP, DDSMI relays)". On disk this engine has no `Musical_Intelligence/brain/functions/f9/` directory; F9 is consumed by the kernel via different paths (likely re-exported through F1-F8 belief modules tagged `F9-relay` or via a kernel-side registry). The Phase-1 belief-enumeration script tries `f9` first; if absent it records `F9 = 0` and the C-CARD-05 verdict will reflect actual on-disk count (121 F1-F8 + 0 F9 = 121, not 131). This will be a documented divergence from the paper, attributable to where F9 relays live in the codebase versus how the paper counts them.
