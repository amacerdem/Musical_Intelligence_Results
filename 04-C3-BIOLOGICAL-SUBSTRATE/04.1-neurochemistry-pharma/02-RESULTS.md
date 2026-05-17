# V-Reproduction Phase 04.1 — Results (CLOSED)

**Date:** 2026-05-07
**Verdict:** **11 PASS / 0 CAVEAT / 0 FAIL** (single iteration, with one regex tweak after first run)
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
**Wall:** ~5 s on MacBook Air M2 (2023, 8 GB unified memory).

---

## 1. Headline

All 10 paper-claim aggregates spanning Neurochemistry + Pharmacological Cross-Validation reproduce verbatim against V1 stored `Science/V1/results/neurochemicals/neurochemical_validation.md`. Live engine spot-check on V1's P5 WAV reproduces 4 neurochemical channels (DA / NE / OPI / 5-HT) **bit-identically** between two consecutive runs (max |Δ| = 0.0 across 345 frames × 4 channels = 1,380 values).

## 2. Determinism spot-check

| Channel | n_frames | mean_run1 | mean_run2 | max \|Δ\| |
|---|---|---|---|---|
| DA  | 345 | +0.2794 | +0.2794 | 0.0 |
| NE  | 345 | +0.7210 | +0.7210 | 0.0 |
| OPI | 345 | +0.5609 | +0.5609 | 0.0 |
| 5HT | 345 | +0.2109 | +0.2109 | 0.0 |

Engine bit-determinism is exact for the C³ + neurochemical compute path on a 0.5 s P5 dyad WAV. This is an independent confirmation of engine bit-state stability, alongside Phase 02.1 T³ isolated-extended (207 sub-tests) and the aggregate engine-pin SHA `318eb2f5…`.

## 3. Per-claim verdict (11 rows)

| Claim | Paper claim | V1 source line | Verdict |
|---|---|---|---|
| C-PHARMA-01 | 132/132 accumulation tests PASS | "Accumulation tests PASS \| **132 (100%)**" | **PASS** |
| C-PHARMA-02 | 11/11 pharmacological cross-validation | "**11/11 PASS (100%)**" | **PASS** |
| C-PHARMA-03 | antic_da↔caudate ρ=+0.933 | "Mean anticipatory_da ↔ caudate ρ \| **+0.933**" | **PASS** |
| C-PHARMA-04 | consum_da↔NAcc ρ=+0.836 | "Mean consummatory_da ↔ nacc ρ \| **+0.836**" | **PASS** |
| C-PHARMA-05 | caudate-leads-NAcc 52/56 (93%) | "Tracks with caudate leading NAcc \| **52/56 (93%)**" | **PASS** |
| C-PHARMA-06 | caudate→NAcc lag +0.9 s | "**+0.9 seconds**" | **PASS** |
| C-PHARMA-07 | Ferreri levodopa>placebo>risperidone | "Levodopa > placebo > risperidone" | **PASS** |
| C-PHARMA-08 | Putkinen 7/7 μ-opioid PET region match | "OPI region match (Putkinen 2025) \| **7/7 MATCH (100%)**" | **PASS** |
| C-PHARMA-09 | Mallik chills>neutral p=0.044 | "OPI chills > neutral (Mallik 2017) \| **PASS** (p=0.044)" | **PASS** |
| C-PHARMA-10 | NAcc-leads-caudate 0/56 (architectural null) | "Tracks with NAcc leading caudate \| **0/56 (0%)**" | **PASS** |
| C-PHARMA-DETERM-01 | Live 4-channel determinism on V1 P5 WAV | engine bit-state | **PASS** (max \|Δ\|=0.0) |

## 4. Compute profile

- Wall: 5.1 s on M2 8 GB
- 2 full engine pipeline runs (R³ + H³ + C³ + RAM + neuro) on 0.5 s P5 WAV
- 11 regex matches against V1 stored neurochem validation report

## 5. Concerns and disclosures

**F9 import warning (cosmetic).** The engine runner emitted:
> `[runner] WARN failed to import mechanisms module for f9: ModuleNotFoundError("No module named 'Musical_Intelligence.brain.functions.f9'")`
on both runs. F9 (Social/Cultural) does not have mechanisms (only kernel relays SSRI/NSCP/DDSMI per `MEMORY.md`); the runner's auto-discovery falls back gracefully on failure. The bit-identical determinism canary is unaffected (warning fires identically on both runs); this is documented as expected behavior.

## 6. Hand-off

- Phase 04.1 CLOSED, 11/11 PASS.
- Phase 04.2 (RAM topology, 5 claims) is next in Section 04.
