# 06.2 — Unified Portfolio Aggregator (PENDING)

**Status:** ⏸ PENDING — defer until all phases (00.x–05.x) + Section 06 (06.1 falsifiable-table5 + 06.3 ai-baseline-ablation) are fully migrated and per-phase verdict CSVs are stable.

## Why deferred

Portfolio-level multiple-comparison aggregation is a **terminal** computation. It pulls per-cell evidence from every Section's verdict CSV. Running it mid-migration with partial evidence produces a number that:

1. Reflects only the subset of phases migrated so far (misleading)
2. Treats heterogeneous cells (fMRI vs behavioural vs pharmacological) as equal weight (statistically defensible but scientifically blunt)
3. Bakes in evidence-tier biases (volume-dominant behavioural cells crowd out high-evidence fMRI/pharma cells)

The right time to revisit this is **after every phase under 01-05 has migrated and produced a verdict CSV**.

## What the aggregator will eventually do

When triggered post-migration:

1. **Read** every `<phase>/results/<phase>_correlations.csv` from Sections 00–05.
2. **Stratify** cells into evidence tiers (fMRI cross-subject / pharmacology cross-val / held-out belief calibration / behavioural correlation).
3. **Compute** stratified pass-rate per tier + a unified hierarchical Benjamini–Bogomolov pass-rate across the portfolio (paper-canonical methodology).
4. **Compare** against the paper-canonical baseline (which previously aggregated a different cell mix; that 1,174 / 1,496 figure is retired with the post-freeze evidence restructuring).
5. **Publish** a single `bucket_distribution.csv` + `audit_summary.md` plus a per-tier headline.

## Inputs expected (will be wired at aggregator-build time)

- Section 00 (engine integrity): 00.1, 00.2, 00.3 verdict CSVs ✓ migrated
- Section 01 (R³ perceptual front-end): 01.1, 01.2, 01.3 verdict CSVs ✓ migrated
- Section 02 (T³ temporal layer): 02.1 ⏳ pending migration
- Section 03 (C³ behavioural validation): 03.1–03.7 ⏳ pending migration
- Section 04 (C³ biological substrate): 04.1, 04.2 ⏳ pending migration
- Section 05 (fMRI brain grounding): 05.1–05.7 ⏳ pending migration
- Section 06 (portfolio falsifiability): 06.1 falsifiable-table5 + 06.3 ai-baseline-ablation ⏳ pending migration

## Methodology questions to resolve at build time

Held open intentionally:
- Hierarchical Benjamini–Bogomolov (paper-canonical) vs unweighted global BH vs evidence-tier-weighted aggregation
- Weighting per cell (currently equal-weight, scientifically blunt)
- Inclusion / exclusion of post-freeze Gen 2 evidence into the portfolio universe
- Per-tier headline reporting (recommended) vs single aggregate (paper-canonical)

These decisions are not pre-committed; the build will surface options + recommend.

## Trigger

When Sections 00–05 are migrated and per-phase verdict CSVs are stable, this file gets replaced by the actual aggregator (`run_phase00_6_2.py` + `results/06.2_*.csv` + `02-RESULTS.md`).

Until then this file is the only artifact in `06.2-unified-bb-fdr-aggregator/`.
