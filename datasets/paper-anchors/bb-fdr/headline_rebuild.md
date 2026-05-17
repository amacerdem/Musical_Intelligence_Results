# MR-05 Headline Pass Rate Rebuild

**Method:** Benjamini--Hochberg FDR applied globally across the full
paper-wide family of N=1496 enumerated significance tests
(see `V2/results/GT-0006/test_registry.csv`).

**Global summary:**

| Correction | Pass count | Pass fraction |
|-----------|-----------|--------------|
| Original within-mechanism BH | (varies per function) | see table below |
| **Global BH FDR (q<0.05)** | **1194/1496** | **79.8%** |
| Bonferroni (α/N, lower bound) | 444/1496 | 29.7% |

---

## Per-function comparison

| Function | Original pass | Original % | Extracted N | Global BH pass | Global BH % | Bonferroni pass | Bonferroni % | Note |
|----------|--------------|-----------|-------------|---------------|------------|----------------|-------------|------|
| F1 Sensory | 132/139 | 95% | 161 | 154 | 95.7% | 104 | 64.6% | ≈ within-mech rate |
| F2 Prediction | 107/110 | 97% | 160 | 156 | 97.5% | 41 | 25.6% | ≈ within-mech rate |
| F3 Attention | 39/56 | 70% | 290 | 151 | 52.1% | 28 | 9.7% | ↓ 17.6pp vs within-mech |
| F4 Memory | —/— | see paper | 169 | 132 | 78.1% | 87 | 51.5% |  |
| F5 Emotion | —/— | see paper | 156 | 148 | 94.9% | 54 | 34.6% |  |
| F6 Reward | —/— | see paper | 79 | 79 | 100.0% | 36 | 45.6% |  |
| F7 Motor | —/— | see paper | 315 | 213 | 67.6% | 63 | 20.0% |  |
| F8 Learning | 14/14 | 100% | 129 | 128 | 99.2% | 29 | 22.5% | ≈ within-mech rate |
| R³ Perceptual | 68/68 | 100% | 11 | 10 | 90.9% | 2 | 18.2% | ↓ 9.1pp vs within-mech |
| fMRI Region | 30/32 | 94% | 24 | 23 | 95.8% | 0 | 0.0% | ≥ within-mech rate |
| Neurochemical (pharma) | 11/11 | 100% | 2 | 0 | 0.0% | 0 | 0.0% | ↓ 100.0pp vs within-mech |

---

## Extraction coverage notes

The test registry captures **N=1496** tests with extractable
p-values from markdown tables in V1/results. Several test families are
**not captured** (documented gap; does not affect the global FDR logic):

| Source | Tests | Reason not extracted |
|--------|-------|---------------------|
| H³ design tests | 19 | PASS/FAIL only; no raw p-value in report |
| Neurochemical accumulation | 132 | Functional sanity checks; no p-value |
| fMRI region match p | 32 | p approximated (0.001 pass, 0.500 fail) |
| Pharmacological ordering | 6 | Structural consistency; no null hypothesis |

These gaps mean the true N is higher and the global BH threshold would be
even stricter if all tests were enumerated. Our reported global BH pass rate
is thus a **conservative over-estimate** (liberal direction): the true
global-FDR pass rate can only be equal or lower once the uncaptured test
families are added.

---

## Recommended paper language

**Abstract / Results headline:**
```
Under paper-wide global Benjamini--Hochberg FDR correction across
N=1496 enumerated tests (q<0.05), 1194/1496 (79.8%)
reach significance. Bonferroni-corrected (α/N) lower bound:
444/1496 (29.7%).
```

**Methods subsection text:** see §Methods §\ref{sec:global_fdr} in main.tex
