# Phase 04.1 — Neurochemistry + Pharmacological Cross-Validation — Methodology (LOCKED 2026-05-07)

**Section:** 04 — C³ Biological Substrate
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

## 1. Scope

Phase 04.1 reproduces 10 paper claims spanning neurochemistry accumulation tests + pharmacological cross-validation (paper §F6 Reward + Methods §Neurochemistry):

- **132/132** accumulation tests (DA/NE/OPI/5-HT, 33 tests × 4 channels)
- **11/11** pharmacological cross-validation tests
- **Salimpoor 2011** dopamine wanting/liking dissociation: caudate vs NAcc
- **Ferreri 2019** dose ordering: levodopa > placebo > risperidone
- **Putkinen 2025** μ-opioid PET 7/7 region match
- **Mallik 2017** naltrexone chills > neutral p=0.044

## 2. Reproduction strategy: V1 stored verification + live spot-check

V1 produced all 10 paper claims under the frozen engine HEAD. Engine bit-reproducibility is verified at Phase 02.1 (T³ isolated-extended, 207 sub-tests) and via the aggregate engine-pin SHA `318eb2f5…`. Phase 04.1 verifies the V1 stored neurochemistry validation (`Science/V1/results/neurochemicals/neurochemical_validation.md`) against paper §F6 + §Neurochemistry, with a live engine spot-check that:

- Runs the canonical engine on one DEAM track via `_infra/engine/runner.py`
- Confirms 4 neurochemical channels (DA, NE, OPI, 5-HT) emit non-trivial output
- Confirms output is bit-identical between two consecutive runs

## 3. Per-claim paper values + tolerances

| Claim ID | Paper value | V1 source line | Tolerance |
|---|---|---|---|
| C-PHARMA-01 | 132/132 accumulation tests PASS | "Accumulation tests PASS \| **132 (100%)**" | exact_match |
| C-PHARMA-02 | 11/11 pharmacological cross-validation | "11/11 PASS (100%)" | exact_match |
| C-PHARMA-03 | antic_da↔caudate ρ=+0.933 | "Mean anticipatory_da ↔ caudate ρ \| **+0.933**" | abs ≤ 0.05 |
| C-PHARMA-04 | consum_da↔NAcc ρ=+0.836 | "Mean consummatory_da ↔ nacc ρ \| **+0.836**" | abs ≤ 0.05 |
| C-PHARMA-05 | caudate-leads-NAcc 52/56 tracks | "Tracks with caudate leading NAcc \| **52/56" | exact_match |
| C-PHARMA-06 | caudate→NAcc temporal lag +0.9 s | "**+0.9 seconds**" | abs ≤ 0.2 s |
| C-PHARMA-07 | Ferreri levodopa>placebo>risperidone | per V1 ferreri test | exact_match (ordering) |
| C-PHARMA-08 | Putkinen 7/7 PET regions | "OPI region match (Putkinen 2025) \| **7/7 MATCH (100%)**" | exact_match |
| C-PHARMA-09 | Mallik p=0.044 chills>neutral | "OPI chills > neutral (Mallik 2017) \| **PASS** (p=0.044)" | exact_match |
| C-PHARMA-10 | NAcc-leads-caudate 0/56 (architectural null) | "Tracks with NAcc leading caudate \| **0/56" | exact_match |

## 4. Live engine spot-check

Run `_infra.engine.runner.run_engine(audio, return_layers=("neuro",))` on a single DEAM 30-second clip; verify:
- 4 neurochem channels present (DA, NE, OPI, 5-HT)
- Output finite (no NaN/Inf)
- Bit-identical between two runs (engine determinism floor)

## 5. Forbidden moves

- Mutating engine constants to chase pharma direction (engine frozen).
- Re-running every Salimpoor track on different DEAM segments to find a better caudate-NAcc lag (would be selective sampling).
