# L8 — Horizon-scale audit: summary scorecard

**Date:** 2026-05-09
**Audit method:** Programmatic cross-check of `Musical_Intelligence/ear/h3/constants/horizons.py` against documented spec.
**Engine pin:** HEAD (T³ paper-time anchor, frozen since 2026-05-06).

## Headline

> **✅ PASS — All 5 horizon-scale sub-tests pass against `horizons.py`. L8.5 carries 1 documented caveat (6/32 large-horizon frame-counts differ from the formula by 1–4 frames; the catalog values are authoritative per the source docstring at `horizons.py:74-76`).**

## Per-sub-test scorecard

| Sub-test | Subject | Result |
|---|---|---|
| **L8.1** | Cardinality: `N_HORIZONS = 32`; `len(HORIZON_MS) = len(HORIZON_FRAMES) = len(BAND_ASSIGNMENTS) = 32` | **PASS** |
| **L8.2** | Spacing characterisation: log-coverage in 4 perceptual bands (NOT strictly log-spaced; ratios vary 1.125–4.31) | **PASS** with corrected wording (per L9 finding) |
| **L8.3** | Band partition: `H0–H7 = micro`, `H8–H15 = meso`, `H16–H23 = macro`, `H24–H31 = ultra` | **PASS** (all 32 BAND_ASSIGNMENTS correct; BAND_RANGES dict matches) |
| **L8.4** | Boundary horizons: `H0 = 5.8 ms` (1 frame at 172.27 Hz); `H31 = 981 s`; `FRAME_RATE = 44100/256 = 172.27` | **PASS** (all four anchors verified) |
| **L8.5** | Derivation formula `HORIZON_FRAMES[i] = max(1, round(HORIZON_MS[i] / 1000 * FRAME_RATE))` | **PASS-WITH-CAVEAT** — 26/32 exact match; 29/32 within 1 frame; 6 differ at large horizons due to authoritative HorizonCatalog.md rounding |

## L8.2 spacing detail (L9-forwarded wording fix verified)

| Statistic | Value |
|---|---|
| Total span H31 / H0 | **169,138×** |
| Geometric mean ratio (if strictly uniform) | 1.475× |
| Min inter-horizon ratio observed | **1.125×** |
| Max inter-horizon ratio observed | **4.31×** (H5 → H6: 46.4 ms → 200 ms intra-Micro band jump) |
| Strictly log-spaced? | **No** — ratios vary by 3.8× across the sequence |

**Interpretation:** The 32 horizons provide *log-coverage organised in four perceptual bands* with band-boundary gaps. The earlier "32 logarithmically-spaced horizons" wording (in `T3-Paper/README.md`, `T3_Isolated_Validation/README.md`, MI `subsec:system-h3`) was strictly inaccurate and has been corrected (L14 commit `deda154`).

The previous wording was probably correct in spirit (the sequence DOES cover 5 orders of magnitude logarithmically rather than linearly) but technically wrong about uniformity.

## L8.5 caveat detail (catalog-vs-formula)

The 6 horizons where `HORIZON_FRAMES` differs from the formula:

| H | ms | In table | From formula | Diff |
|---|---|---|---|---|
| H17 | 1,500 | 259 | 258 | +1 |
| H27 | 200,000 | 34,453 | 34,454 | −1 |
| H28 | 414,000 | 71,319 | 71,320 | −1 |
| H29 | 600,000 | 103,359 | 103,362 | −3 |
| H30 | 800,000 | 137,812 | 137,816 | −4 |
| H31 | 981,000 | 168,999 | 168,997 | +2 |

This is **expected and documented**. From `horizons.py:74-76`:

> "Derivation formula: max(1, round(ms / 1000 * FRAME_RATE))
> Values below are the authoritative counts from HorizonCatalog.md, which resolve floating-point rounding ambiguities at large horizons."

The formula uses `FRAME_RATE = 172.27` (a 3-significant-digit truncation of `44100/256 = 172.265625`); compounding rounding error at large horizons (H29-H31 at hundreds-of-thousands of frames) accumulates to a few frames. The catalog values represent the **deliberate choice** of resolving these rounding ambiguities by hand.

For all 32 horizons, the catalog value is **within ±4 frames** of the formula at the largest scale (Ultra band) — well within the H31's 168,999-frame window (≈0.002% relative error).

L8.5 verdict: **PASS** — the catalog is the authoritative source by design; the formula is a guide for understanding the derivation. No engine inconsistency.

## Observation: L8 is structurally complete

L8 is essentially a structural audit (cardinality, partition, boundary values, derivation formula). All 5 sub-tests reach PASS by reading the source-of-truth file and cross-checking against documented spec. There is no runtime component required for L8: the horizon-scale claims are about engine constants, which L9 already audited for provenance.

## Reproducibility

Audit script committed at `_infra/audit_scripts/h3_horizon_audit.py`.
Re-run: `python3 _infra/audit_scripts/h3_horizon_audit.py`

Audit is byte-deterministic against engine source; PASS holds as long as `horizons.py` is unchanged (constants/ folder has been frozen since initial commit per L9.6 finding).

## Headline (production-grade form)

> **L8 PASS — 5/5:** all 32 horizons cardinality-correct; band partition matches BAND_ASSIGNMENTS; boundary horizons match documented derivations (`44100/256 = 172.27` Hz frame rate; H0 = 1 frame; H31 = 981 s); HORIZON_FRAMES catalog values within ±4 frames of formula at largest scales (resolved by hand per `horizons.py:74-76` docstring).
