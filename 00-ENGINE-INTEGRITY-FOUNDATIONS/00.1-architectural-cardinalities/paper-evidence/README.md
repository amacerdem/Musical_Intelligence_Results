# Phase 1 — paper-evidence/ (POINTERS ONLY)

This directory holds no copies of the paper. Pointers to the canonical paper:

## Primary anchor

**File:** `The Paper/Nature-Neuroscience/revision/Musical_Intelligence_AE.tex`

Relevant lines:

- **Line 585** — §Architectural cardinalities (THE 16-cardinality paragraph)
- **Line 581** — §Three constant counts (16,191 / 7,517 / ~97; 495 hand-tuned, 246 calib)
- **Line 575** — §PRISMA (529 RegionLinks, 48 NeuroLinks declared per-mechanism)
- **Line 573** — §Cao tier system (α/β/γ region confidence)
- **Line 270** — §Neurochemical channels (DA/NE/OPI/5HT, 132 numerical checks)
- **Line 266** — §RegionLink topology (529, MNI152 centroids, 30/32 name match)

## Supplementary tables referenced

- **Table S-Provenance** — full 16,191-row inventory with 5-bucket labels (lenient classifier)
- **Table S-Compute** — 7,517 compute-path constants breakdown (7,256 array + 261 scalar)
- **Table S-MechLedger** — per-mechanism literature anchors, citations, MNI coords
- **Table c3_functions** (referenced from MEMORY) — 8 primary functions × mech/dim/belief counts

## Audit-trail JSON ledger

`Science/Musical_Intelligence/c3/literature/` (per paper line 575) — per-mechanism citation JSON.

## Engine HEAD ↔ paper version

Engine HEAD `318eb2f529d7103e8b7d80b01228357fdc4e0217` is the snapshot the paper was written against. Phase 1 reproduces every cardinality at this HEAD with no engine modification.

## How to verify a number

For any cardinality C-CARD-NN:
1. Find it in `Musical_Intelligence_AE.tex` line ~585 or §S-Provenance.
2. Cross-check against `Science/V1/results/All_Results/All_Results.md` (frozen V1 evidence).
3. Re-run the corresponding script in `code/`.
4. Compare against `results/01_cardinalities_manifest.json` claim entry.

If divergence > tolerance, trigger debug protocol from `_audits/INVESTIGATION-RULES.md`.
