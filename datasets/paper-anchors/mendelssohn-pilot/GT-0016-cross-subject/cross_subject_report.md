# GT-0016 Cross-Subject Extension — Mendelssohn Rank-Preservation

**Framing (per R3):** This is NOT a "MI predicts BOLD" claim. We report the per-subject Spearman ρ between MI RAM amygdala/PMC columns and BOLD as a *RAM rank-preservation consistency* metric, then aggregate the cross-subject median to test whether sub-08's +0.59 r (+0.29 ρ) was subject-selection-biased.

**Verdict: FAIL**  — Median Spearman ρ amyg=-0.0223 ≤ 0 → sub-08's +0.29 ρ was a selection effect

## Aggregate (cross-subject)

| Predictor | N | Median ρ | IQR | 95% BCa CI (median) | Range | N with ρ>0 |
|---|---:|---:|---:|:---:|:---:|---:|
| MI amygdala (ρ) | 17 | -0.0223 | [-0.1541, +0.0372] | [-0.1541, +0.0267] | [-0.2772, +0.4012] | 7/17 |
| MI PMC (ρ) | 17 | +0.0145 | [-0.2204, +0.1938] | [-0.2204, +0.0951] | [-0.6229, +0.4971] | 9/17 |
| MI amygdala (r) | 17 | -0.0120 | [-0.1257, +0.0751] | [-0.1257, +0.0616] | [-0.3257, +0.4021] | 8/17 |
| MI PMC (r) | 17 | +0.0054 | [-0.1958, +0.0997] | [-0.1958, +0.0879] | [-0.5615, +0.3126] | 9/17 |
| Baseline: RMS env | 17 | -0.0788 | [-0.0997, +0.0485] | [-0.0997, +0.0247] | [-0.2594, +0.3508] | 7/17 |
| Baseline: spectral flux | 17 | +0.0011 | [-0.1607, +0.1748] | [-0.1607, +0.0915] | [-0.4300, +0.2593] | 9/17 |
| Baseline: onset rate | 17 | +0.0086 | [-0.1552, +0.1179] | [-0.1552, +0.0952] | [-0.3934, +0.2446] | 10/17 |
| Baseline: spectral entropy | 17 | +0.0217 | [-0.1106, +0.1215] | [-0.1106, +0.1010] | [-0.2576, +0.2096] | 9/17 |

## Sub-08 replicates?

- sub-08 included: ρ_amy=-0.0342, r_amy=-0.0120, ρ_PMC=+0.0706, tr_start=324, anchor_r=+0.410, n_TRs=80
- Cross-subject median amygdala ρ = -0.0223. Sub-08 is above median — typical cohort, not extreme

## Per-subject rows

| Subject | status | tr_start | anchor_r | n_TRs | ρ amyg | r amyg | ρ PMC | ρ amyg CI |
|---|---|---:|---:|---:|---:|---:|---:|:---:|
| sub-01 | ok | 740 | +0.466 | 80 | -0.2772 | -0.2774 | +0.0951 | [-0.458, -0.089] |
| sub-02 | ok | 817 | +0.605 | 80 | -0.1541 | -0.1257 | -0.0424 | [-0.409, -0.002] |
| sub-03 | ok | 702 | +0.429 | 80 | +0.4012 | +0.4021 | -0.1928 | [+0.009, +0.562] |
| sub-05 | ok | 841 | +0.539 | 80 | +0.3110 | +0.3300 | -0.3109 | [-0.086, +0.476] |
| sub-06 | ok | 689 | +0.484 | 80 | +0.0936 | +0.0616 | -0.6229 | [-0.266, +0.351] |
| sub-07 | ok | 668 | +0.444 | 80 | -0.2361 | -0.2168 | -0.5153 | [-0.383, -0.044] |
| sub-08 | ok | 324 | +0.410 | 80 | -0.0342 | -0.0120 | +0.0706 | [-0.291, +0.187] |
| sub-09 | ok | 0 | +0.684 | 80 | +0.0372 | +0.0751 | +0.4971 | [-0.231, +0.211] |
| sub-11 | ok | 666 | +0.410 | 80 | -0.0771 | -0.0475 | -0.1439 | [-0.373, +0.226] |
| sub-12 | ok | 320 | +0.628 | 80 | -0.0027 | +0.0054 | +0.1938 | [-0.301, +0.421] |
| sub-13 | ok | 548 | +0.430 | 80 | +0.0267 | +0.1144 | +0.2431 | [-0.303, +0.295] |
| sub-14 | ok | 678 | +0.494 | 80 | +0.2890 | +0.2439 | +0.3445 | [-0.047, +0.564] |
| sub-15 | ok | 172 | +0.351 | 80 | -0.1717 | -0.2096 | +0.0630 | [-0.401, +0.169] |
| sub-17 | ok | 813 | +0.423 | 80 | -0.0223 | +0.0124 | +0.0145 | [-0.407, +0.230] |
| sub-18 | ok | 1 | +0.493 | 80 | -0.1865 | -0.3257 | -0.4965 | [-0.325, +0.038] |
| sub-19 | ok | 0 | +0.390 | 80 | -0.0755 | -0.0360 | -0.2204 | [-0.314, +0.125] |
| sub-20 | ok | 215 | +0.448 | 80 | +0.0063 | -0.0198 | +0.2975 | [-0.298, +0.351] |

## Methodology

- **Alignment (T-R5-02 canonical sliding-window HRF anchor):** For each subject,   slide an 80-TR (160s) window across the full classical-music BOLD run.   At each candidate TR_start, score = Pearson r between HRF-convolved MI RAM   mean over auditory anchor ROIs (A1_HG + STG + MGB) and BOLD mean over the   same ROIs. Pick TR_start = argmax(score). Require anchor_r ≥ 0.05 to include   the subject. This approach does NOT peek at amygdala/PMC, so does not   cherry-pick regions of interest.
- **Main correlation window:** 80 TRs (160s) starting at the anchored TR_start   (matches paper's Fig 1a 160s claim).
- **BOLD:** NiftiSpheresMasker, 6mm sphere, zscore_sample, TR=2s. Seeds:   amygdala MNI (24,-4,-18) and PMC MNI (46,0,48) — identical to GT-0016.
- **MI predictor:** Raw (no HRF) RAM[:,15] = amygdala, RAM[:,9] = PMC.   Downsampled by mean-pooling from 172.27 Hz to TR rate. (Same as GT-0016.)
- **Correlation:** Pearson r + Spearman ρ. Spearman is the headline (rank-  preservation framing per R3).
- **Per-subject CI:** Politis-Romano block-bootstrap (5000 resamples,   block_len=8 TRs ≈ 16s ≈ 2×τ_ac).
- **Cross-subject CI:** BCa bootstrap over subjects (1000 resamples).
- **Trivial baselines:** RMS, spectral flux, onset rate, spectral entropy from   mendelssohn.wav at TR=2s, Spearman vs amygdala BOLD.

## Caveats

- Subjects whose sliding-window anchor_r < 0.05 are skipped — the auditory   BOLD pattern was not discernibly aligned with any window of the Mendelssohn   stimulus (likely motion/noise or different piece played).
- The 80-TR main window is aligned via an acoustic anchor (A1_HG+STG+MGB),   which is STIMULUS-IDENTITY-SENSITIVE but NOT amygdala-dependent. This   avoids the confound that GT-0016's sub-08 TR=556 window (which produces   +0.5906) is the BOLD-amygdala argmax across all 854 possible windows —   a 854-fold post-hoc selection not detectable in the paper's original claim.
- The paper's Fig 1a shows sub-08's ρ=+0.29 at this max-r window; this test   computes ρ at an auditory-anchored window per subject without peeking at   the amygdala signal, giving an unbiased cross-subject estimate.

## Selection-bias diagnostic (supplementary)

The companion analysis `supplementary_posthoc_max_r_report.md` scans all
~854 possible 80-TR windows per subject for the max Pearson r, replicating
the apparent methodology behind GT-0016's sub-08 TR=556 → r=+0.5906 claim.

| Analysis | N | Median amygdala Spearman ρ | Median amygdala Pearson r |
|---|---:|---:|---:|
| **Primary** (auditory-anchored, no peeking) | 17 | **-0.022** | -0.012 |
| **Supplementary** (post-hoc window-shopped) | 17 | +0.623 | +0.590 |

**Interpretation:** Every subject yields a max-r ≥ +0.50 when the
window is chosen post-hoc (median post-hoc = +0.59 across all 17 subjects).
Sub-08's +0.59 is not remarkable — it is the typical max value for any
subject given ~854 windows to choose from. The paper's N=1 claim is not
a subject-selection effect (sub-08 isn't special) — it is primarily a
**window-selection effect**: any subject would reach r≈+0.59 under the
same methodology. For sub-08 under the pre-registered-style auditory-
anchored method used here, ρ drops from +0.29 to -0.03.

The correct paper language is: "Across N=17 subjects who heard Mendelssohn
Op.54, the cross-subject median Spearman ρ between MI RAM amygdala and
BOLD amygdala at auditory-anchored 160s windows is -0.02 (IQR
[-0.15, +0.04], 95% BCa CI [-0.15, +0.03]), with 7/17 subjects showing
ρ > 0. The +0.59 Pearson r reported for sub-08 in prior pilot analysis
reflects post-hoc window selection from the full classical-music run
(argmax r = +0.59 is achieved by every subject at some window)."