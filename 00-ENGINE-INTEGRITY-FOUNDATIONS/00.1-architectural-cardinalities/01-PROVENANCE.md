# Phase 00.1 — Architectural Cardinalities — Provenance Chain (V3)

**Engine SHA pin:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
**Aggregate SHA:** `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`

## Paper anchor (post R15-R18 revision)

**Source:** `Publication/Amac-Erdem-Musical-Intelligence.tex`, §Architecture §Parameter provenance

Revised paper headline (per `_audits/audit_summary.md`):

> Of 16,248 numeric constants in the frozen Musical Intelligence engine, zero are calibrated against held-out cognitive behavior data. 86 (0.53%) are literature-anchored — 67 bit-exact to published primary sources (Sethares 1993, Krumhansl-Kessler 1982, IEC 61672-1, Traunmüller 1990 Bark, Stevens 1957, O'Shaughnessy 1987 mel) and 19 derive analytically from cited form (Hasson temporal-window ladder, Plomp-Levelt 25% critical-band peak, Sethares parametric kernel, Berlyne 4·x·(1-x)). 6 are paper-disclosed reward weights in `brain/reward.py` (1 additional paper-listed item, `phi_fam_star = 0.5`, is a kernel-peak mathematical identity per **paper revision R15**). The remaining 16,156 are structural topology (9,817), identity placeholders (1,182), or transparent engineering choices (5,157). Two mechanisms (HTP-E3, SPH-E3) include a discrete structural model-selection step (formula-form choice between two candidates, literature-anchored), not a numeric fit.

## V2 → V3 supersession

Earlier paper text (pre-2026-05-16) referenced a coarser 5-bucket classifier that included a calibration category (~246 constants). Per the CODE-FIRST audit:

- Engine source contains **zero** `calibrat` references in the runtime call-graph
- V3 classifier under no-calibration rule redistributes those constants to LIT-VERBATIM (file-citation inheritance via Sethares/Plomp-Levelt/Helmholtz/Bidelman) or STRUCTURAL (dim/index codes in F1 BCH module)
- Constant-level audit (2026-05-17) confirms zero attributions to any calibration category

The calibration category is **retired** doctrinally and operationally. Paper text is revised accordingly (R15-R18 revision items).

## Code provenance

**Engine root:** `Musical_Intelligence/` (at project root); bit-identical to engine HEAD `318eb2f5...`.

**Audit anchors (read-only inputs to this phase):**

- `_audits/audit_combined.csv` — 16,248 rows × 16 columns; full constant-level attribution (9-agent merge)
- `_audits/bucket_distribution_real.csv` — 7-category summary (canonical headline numbers)
- `_audits/audit_summary.md` — reviewer-facing synthesis
- `_audits/escalation_resolutions.md` — 46 escalation theme-groupings for manual review
- `_audits/INVESTIGATION-RULES.md` — protocol v1.2 (R1-R9 integrated)
- `_audits/2026-05-17_htp-sph-e3-structural-selection-audit.md` — HTP-E3/SPH-E3 discrete model-selection trail

**Per-agent CSVs (9):**

- `agent_1_audit.csv` — F1 mechs (2,435)
- `agent_2_audit.csv` — F2+F3 mechs (3,607)
- `agent_3_audit.csv` — F4+F5 mechs (4,883)
- `agent_4_audit.csv` — R³+T³ (592) — pilot, 67 A + 18 B
- `agent_5_audit.csv` — F6+reward.py (1,415) — 6 F
- `agent_6_audit.csv` — F7+F8 mechs (2,998)
- `agent_7_audit.csv` — RAM+regions (65)
- `agent_8_audit.csv` — neurolink+neurochem+beliefs+cycle (40)
- `agent_9_audit.csv` — scaffolding+contracts+scripts+data (213)

Sum: 16,248 = 2,435 + 3,607 + 4,883 + 592 + 1,415 + 2,998 + 65 + 40 + 213 ✓

## Engine HEAD pin

Frozen pre-V1 per user confirmation 2026-05-06; all V1/V2/V3/V4/V5/V6 reproduction cycles and the V3 constant-level audit ran against this engine. No engine modifications introduced by any audit phase.

## Date of reproduction

2026-05-17 (V3 audit-anchored verdict).

## Confidence summary

- **98.10% HIGH** confidence across 16,248 attributions (15,939 HIGH / 309 MEDIUM / 0 LOW)
- **46 escalations** queued (0.28%) — all MEDIUM/PARTIAL outcomes, none destabilize the headline
- **0 fabricated POSITIVE** web-search confirmations (3-attempt hallucination guard enforced)

## Honesty notes carried forward

1. **F = 6 not 7.** The protocol lists 7 HAND-SPECIFIED-DISCLOSED weights; the engine maps only 6 as named code constants. The 7th (`phi_fam_star = 0.5`) is the mathematical peak of the Berlyne familiarity kernel `4·f·(1-f)`. **Paper revision R15** reconciles.
2. **NEMAC documentation defect.** `brain/functions/f5/mechanisms/nemac/extraction.py:67` comments cite Sakakibara 2025 `d = 0.88` but the paper reports Cohen's `r = 0.880`. **Paper revision R16** discloses.
3. **ESME `_ALPHA` comment artifact.** `brain/functions/f8/mechanisms/esme/extraction.py` comment word "trainable" predates the zero-calibration doctrine. **Paper revision R17** clarifies.
4. **`brain/regions/` deprecated.** Package is import-unreachable; its 65 constants are documentation-only. **Paper revision R18** notes.
5. **Walker boundary.** Anonymous expression literals inside multi-term expressions may not all be enumerated by the AST walker. Per-agent verification logs document inventory alignment.

## Iteration history

V2 (2026-05-07, paper-canonical) → V3 (2026-05-17, zero-calibration CODE-FIRST). V3 supersedes V2 entirely. V2 results CSV is no longer canonical; the 5-claim V2 verdict has been replaced by the 10-claim V3 verdict in this phase's `results/01_cardinalities_correlations.csv`.
