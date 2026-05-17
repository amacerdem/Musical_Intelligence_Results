# V5 Decision Gate Verdict

**Generated:** 2026-05-05T02:14:54.099657
**Engine pin:** 15df5177 (V3 architectural anchor) · ENGINE_HEAD_ACTUAL=5b9aba41
**Composite:** **NEGATIVE**

## Tier 1 PRIMARY (FAIL)

- Pass rate: **2/4**
- Per-test pass criterion: pre-registered in `01-pre-registration.md`

```
pair_id                     rho  pass  note
----------------------------------------------------------------------------------------------------
P1.composite            +0.0737  False  per-pop ρ: {'UK': 0.22516562387226202, 'Kalash': -0.13843903084444323, 'Khow': 0.13431825764024777}; 0/3 ≥+0.4 ∧ 2/3 sig
P2.composite            +0.5652   True  top-7 ragas (data-limited from top-10), 7/7 with ρ>0; PASS = mean≥0.4 AND ≥5/7 positive
P3.composite            +0.2208  False  ρ_bonang=+0.221, ρ_harmonic=+0.404, |bonang|/|harmonic|=0.55; PASS = sign+ AND ρ_bonang≥0.4 AND ratio≥0.5
P4.composite            +0.4076   True  convention-corrected mean signed ρ across 7 datasets; 6/7 positive; PASS = mean≥0.4 AND ≥6/7 positive
```

## Composite

| Tier 1 | Composite |
|---|---|
| FAIL | **NEGATIVE** |

## Stop-loop trigger

V5 NEGATIVE — V4 v3 published as canonical with overfit disclosures already in `V4/POSITIVE-FINDINGS-stage-3.md`. V5 supplementary failure-mode report.