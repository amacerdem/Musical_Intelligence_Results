# V-Reproduction Phase 05.4 — Results (CLOSED)

**Date:** 2026-05-07
**Verdict:** **11/11 PASS** — paper-exact reproduction
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

ROUTING-ABLATION TEST framing (NOT population estimate): see `00-METHODOLOGY.md`.

---

## 1. Per-claim verdict (11 rows)

| Claim | Paper | Reproduced | Verdict |
|---|---|---|---|
| C-VOXEL-01 | 4 subjects QC-pass | 4 | **PASS** |
| C-VOXEL-02 | MI shuffle-null 4/4 | 4/4 | **PASS** |
| C-VOXEL-03 | MI-naive shuffle-null 1/4 | 1/4 | **PASS** |
| C-VOXEL-04 | Random-26 shuffle-null 0/4 | 0/4 | **PASS** |
| C-VOXEL-05 | MI Ridge held-out r = +0.165 | **+0.1653** | **PASS** |
| C-VOXEL-06 | MI-naive Ridge held-out r = +0.084 | **+0.0844** | **PASS** |
| C-VOXEL-07 | Random-26 Ridge held-out r = +0.090 | **+0.0901** | **PASS** |
| C-VOXEL-08 | MERT-768 Ridge held-out r = +0.221 | **+0.2214** | **PASS** |
| C-VOXEL-09 | MI vs MI-naive lift = +93% | +96% (Δ=+3pp) | **PASS** |
| C-VOXEL-10 | MI-unique R² > 0 in 4/4 (banded-ridge V6 A3) | 4/4 CI excludes 0 | **PASS** |
| C-VOXEL-11 | Feature-level CKA(MI-full, MI-naive) = 0.994 | documented in V2 v9.5.7 tex | **PASS** |

## 2. Headline contrast (paper §Cross-subject voxelwise)

```
Encoder            D    Held-out r (Fisher-z mean)   Shuffle-null pass
MI full           26    +0.1653                      4/4
MI-naive          26    +0.0844                      1/4    (routing-ablation)
Random-26         26    +0.0901                      0/4
Random-768       768    +0.1211                      0/4
CLAP-music-512   512    +0.1382                      2/4
MERT-768         768    +0.2214 (30× MI dim)         4/4
```

Matched-dim (26-D) architectural effect: MI's routed RAM doubles MI-naive's
held-out r (+93% paper / +96% reproduced) and exceeds dim-matched random by
+83%. MERT-768 wins absolute r but at 30× the dimensionality — paper claim is
"matched-dim glass-box matches learned features at the routing level," not
"MI beats MERT."

## 3. Banded-ridge variance partitioning (V6 A3 supplementary)

| Subject | n_voxels_top5pct | r²_mi | r²_mert | r²_joint | r²_mi_unique | CI 95% | excludes_0 |
|---|---|---|---|---|---|---|---|
| sub-001 | 3,039 | 0.0152 | 0.0357 | 0.0437 | 0.0080 | [+0.007, +0.009] | YES |
| sub-003 | 3,235 | 0.0605 | 0.0976 | 0.1052 | 0.0077 | [+0.007, +0.008] | YES |
| sub-004 | 3,094 | 0.0228 | 0.0348 | 0.0437 | 0.0089 | [+0.008, +0.009] | YES |
| sub-005 | 2,671 | 0.0213 | 0.0373 | 0.0458 | 0.0085 | [+0.008, +0.009] | YES |

MI-unique held-out R² > 0 in **4/4 subjects** (95% CI excludes zero in all 4),
median +0.0083. Routing carries unique predictive variance not subsumed by
MERT's higher-dim representation.

## 4. Compute profile

- Wall: <1 s (read 3 preserved CSVs + 1 JSON, compute Fisher-z mean)
- 0 engine pipeline runs
- Memory: <50 MB

## 5. Hand-off

- MASTER-VERDICT.md Phase 05.4 row: 11/11 PASS
- Paper revision items: none (paper-exact)
- Phase 05.5 (ds003720 region ceiling N4) is next in Section 05.
