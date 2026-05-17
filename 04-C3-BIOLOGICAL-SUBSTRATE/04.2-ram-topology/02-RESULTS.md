# V-Reproduction Phase 04.2 — Results (CLOSED)

**Date:** 2026-05-07
**Verdict:** **5 PASS / 0 CAVEAT / 0 FAIL** (V3 audit-anchored; single iteration)
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
**Wall:** ~3 s on M2 8 GB.

---

## 1. Headline

All 5 RAM-topology paper anchors reproduce exactly against the V2 T-R1-08 preserved permutation-null artefacts:

- **28/31 ≤10mm coord match** (paper headline)
- **Null-1 centroid-relocation p<0.0001** (10K perms)
- **Null-2 label-shuffle p<0.0001** (10K perms)
- **26/29 no-proxy robustness** (paper line 1322)
- **Radius-robust: 28 matches at 8/10/12 mm** all p<0.001 under both nulls

## 2. Per-claim verdict (5 rows)

| Claim ID | Paper claim | Reproduced | Verdict |
|---|---|---|---|
| C-RAM-COORD-28-31 | 28/31 @ ≤10mm coord criterion | 28/31 | **PASS** |
| C-RAM-NULL-1-CENTROID | Null-1 centroid-relocation p<0.0001 | p=9.999e-05 | **PASS** |
| C-RAM-NULL-2-LABEL | Null-2 label-shuffle p<0.0001 | p=9.999e-05 | **PASS** |
| C-RAM-NO-PROXY-26-29 | No-proxy robustness 26/29 | 26/29 | **PASS** |
| C-RAM-RADIUS-ROBUST | 28 matches at 8/10/12mm | [28, 28, 28] | **PASS** |

## 3. Anchor source

- `literature_coords_32.csv` — 31-row coord-eligible subset (1 atlas-centroid-proxy row pre-excluded by filename convention)
- `permutation_null_results.csv` — observed 28/31 @ 10mm, both nulls p<0.0001
- `permutation_null_results_no_proxy.csv` — 26/29 robustness
- `match_table_by_radius.csv` — per-row distances @ 8/10/12 mm

All four are preserved V2 T-R1-08 artefacts, vendored under `datasets/paper-anchors/ram-topology/`.

## 4. Compute profile

- Wall: ~3 s (CSV-only verification, no engine run)
- Memory peak: <100 MB
- 0 full-engine runs (this phase verifies pre-computed permutation-null statistics, not raw audio)

## 5. Concerns and disclosures

None. The literature coordinate set and permutation-null artefacts are paper-time outputs that V2's GT-0023 preserved verbatim; this phase confirms the headline rows reproduce row-for-row.

## 6. Hand-off

- Phase 04.2 CLOSED, 5/5 PASS.
- Section 04 (C³ Biological Substrate) complete: 04.1 (11/11) + 04.2 (5/5) = 16/16.
- Section 05 (fMRI Brain Grounding) is next in bottom-up order.
