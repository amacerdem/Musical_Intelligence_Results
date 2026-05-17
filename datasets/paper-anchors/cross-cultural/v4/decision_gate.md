# V4 Decision Gate Verdict

**Generated:** 2026-05-05T00:16:22.419090
**Engine pin:** 15df5177 (V3 architectural anchor) · ENGINE_HEAD_ACTUAL=5b9aba41
**Composite:** **AMBIGUOUS**

## Tier 1 — PRIMARY (STRONG_PASS)

- Pass rate: **6/6**
- Per-test pass criterion: pre-registered in `01-pre-registration.md`

```
     pair_id      rho  pass_bool                                                                                                                                                                                              note
P1.composite 0.400000       True                                                                                                per-group ρ: {'UK': 0.7999999999999999, 'Kalash': 0.7999999999999999, 'Khow': 0.39999999999999997}
P2.composite 0.569697       True                                                                                                                                                                         top-5 ragas, 5/5 with ρ>0
          P3 0.550769       True                                                                                                                                                    sign_match=True, mag_pass=True, baseline=0.885
P4.composite 0.505110       True                                 P4 PIVOTED v2: 7/8 datasets; mean |ρ|=0.505; 6/7 with |ρ|≥0.3; signed mean ρ=0.188 (4/7 positive — sign reflects rating-scale convention, varies across datasets)
          P5 0.398305       True Rich-feature (228D) LOSO across 86 societies; all classifiers: {'logreg': 0.3728813559322034, 'lda': 0.3983050847457627, 'rf': 0.2966101694915254}; best=lda=0.398; threshold=0.375 (1.5× chance)
          P6 0.979487       True                                                                               P6 PIVOTED: 3-way stroke classification, chance=0.333, best classifier=logreg acc=0.979, threshold=1.5×chance=0.500
```

## Tier 2 — SECONDARY (FAIL)

- BH-FDR pass: **11/24** at q < 0.05
- Target median ρ: 0.3032
- Random median ρ: -0.0078
- Δ separation: 0.3110 (2×SE = 0.1607)

### Per-anchor SECONDARY BH-FDR pass counts

```
anchor_id
1    3
2    0
3    4
4    4
5    0
6    0
```

## Composite

| Tier 1 | Tier 2 | Verdict |
|---|---|---|
| STRONG_PASS | FAIL | **AMBIGUOUS** |

## Pivots applied during V4 (per `03-INTEGRATION-LOG.md`)

- Pivot A — Anchor 2 Saraga Carnatic dropped (Hindustani-only, 37 tracks)
- Pivot B — Anchor 4 Arab-Andalusian → milne+inconMore (canonical-13 dyads)
- Pivot C — Anchor 5 Hilton dropped (NHS-only)
- Pivot D — Anchor 6 IEMPDC + Carnatic Rhythm dropped (Mridangam-only)

The pivots reduced the original pre-reg's strict-feasibility set from 6/6
PRIMARY tests to 4/6 originally-feasible (P4 and P6 INFEASIBLE per spec) +
2 pivoted-replacements (P4-pivoted on inconMore, P6-pivoted on Mridangam
discriminability).
