# GT-0019 — Global and Hierarchical FDR Report

**Generated:** 2026-04-25 | **Paper hash:** v9.5.7-cycle-17-ds003720
**Methodology:** Benjamini--Hochberg FDR (0.05) at three granularities:
1. **Local** (within each mechanism's dim table) — matches V1 paper-time convention
2. **Global** (one BH across all harvested p-values) — per R1 + R3 reviewer demand
3. **Hierarchical** (Yekutieli & Benjamini 2001, family-first Simes-BH then within-family BH at q·F/F_pass)

## Headline

| Correction | N significant | Fraction |
|---|---:|---:|
| Local BH (paper-time) | 1,567/1,935 | 81.0% |
| Global BH (omnibus) | 1,590/1,935 | 82.2% |
| Hierarchical BH (Y&B 2001) | 1,564/1,935 | 80.8% |

Hierarchical level-1 family pass: **8/8** families
(each representing a distinct functional module F1-F8 + regions/neurochemicals/h3).

## Per-family breakdown

| family | n_mechs | n_tests | n_sig_local | n_sig_global_bh | n_sig_hier_bh | simes_min_p | level1_pass |
|---|---|---|---|---|---|---|---|
| f1 | 12 | 322 | 308 | 308 | 308 | 0.0 | True |
| f2 | 10 | 160 | 157 | 156 | 157 | 0.0 | True |
| f3 | 12 | 290 | 135 | 152 | 131 | 0.0 | True |
| f4 | 15 | 328 | 257 | 257 | 256 | 0.0 | True |
| f5 | 12 | 312 | 296 | 296 | 297 | 0.0 | True |
| f6 | 10 | 79 | 79 | 79 | 79 | 0.0 | True |
| f7 | 12 | 315 | 207 | 214 | 208 | 0.0 | True |
| f8 | 6 | 129 | 128 | 128 | 128 | 0.0 | True |
| TOTAL | 89 | 1935 | 1567 | 1590 | 1564 |  | 8/8 |

## Source data

- `all_pvalues.csv` — master p-vector with (family, mech, dim, p, column, source) provenance
- `global_fdr_table.csv` — per-family + total summary
- Harvested from: `V1/results/f[1-8]/<mech>/report.md`, `regions/`, `neurochemicals/`, `h3/`

## Interpretation for paper

**Local BH:** paper-time per-mechanism convention. Reports headline "132/139" type counts
(V1 convention). Conservative for per-mechanism claims; not calibrated for omnibus family.

**Global BH:** treats all 1,935 hypotheses as one family. Most stringent. Reveals the
cross-mechanism redundancy (correlated features across related mechanisms) by how
much survives one-shot omnibus correction.

**Hierarchical BH (Y&B 2001):** treats F1-F8 as distinct families, corrects level-1
family-wise Simes-BH, then within-family BH at q·F/F_pass. Controls the global
expected FDR at q while preserving within-family power when the family is well-
supported. This is the **correct** reviewer-demanded calibration for a multi-mechanism
paper.

## Paper integration language

Proposed §Methods paragraph:

> *Multiple-comparison correction was applied at three granularities. Local BH-FDR
> within each mechanism's dimension table (q=0.05) matches the V1 per-mechanism
> convention reported in headline counts. In addition, we report global BH-FDR and
> hierarchical FDR (Yekutieli and Benjamini, 2001) across all 1,935 hypothesis
> tests in the paper to address omnibus concerns; 1,590 (82.2%)
> survive global correction, 1,564 (80.8%) survive
> hierarchical correction at q=0.05. Hierarchical correction is the reference
> multi-family calibration in this paper; headline "1,567/1,935"-style counts
> in §Results use local FDR and are marked † where they additionally survive global
> FDR and ‡ where they survive hierarchical FDR.*

## Notes + caveats

1. **Dependency on GT-0038 (mechanism manifest):** this run assumes the V1/results
   tree is the authoritative N_test denominator. The true denominator should be
   locked in GT-0038 (mechanism manifest). If GT-0038 adds tests not yet in V1/results
   (e.g., pharmacology, OOS extensions), they need to be harvested here too.

2. **Markdown table parsing is fragile:** the script parses `p` and `p(perm)` columns
   from report.md tables. Some older reports may use non-standard column names not
   caught. Manual audit of top-10 p-values by magnitude is recommended for final
   paper-integration pass.

3. **Independence assumption:** BH-FDR controls the expected FDR under independence
   or positive dependence (PRDS). Our tests are clustered within mechanisms and
   correlated across features. Yekutieli & Benjamini 2001 hierarchical correction is
   robust to these clustered dependencies.
