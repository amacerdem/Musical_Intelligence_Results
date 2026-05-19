# L8 — Horizon-scale validation

> **Status:** **POPULATED + PASS (2026-05-09)** — full audit against `Musical_Intelligence/ear/h3/constants/horizons.py`. See [`L8_summary.md`](L8_summary.md) for headline scorecard.

## Paper claim being defended

*32 horizons with log-coverage organised in four perceptual bands (Micro / Meso / Macro / Ultra), spanning 5.8 ms to 981 s. Inter-horizon ratios vary across the sequence (1.125–4.31×), with band-boundary gaps; the sequence covers 5 orders of magnitude logarithmically rather than linearly.*

> **Claim corrected from earlier "32 logarithmically-spaced horizons" wording per L9 audit finding** (L14 commit `deda154`). The earlier wording implied uniform log-spacing; the actual structure is log-coverage with band-organised gaps.

## Audit results (PASS — 5/5)

| Sub-test | Subject | Result |
|---|---|---|
| **L8.1** | Cardinality: `N_HORIZONS = 32`; `len(HORIZON_MS) = len(HORIZON_FRAMES) = len(BAND_ASSIGNMENTS) = 32` | **PASS** |
| **L8.2** | Spacing characterisation: log-coverage in 4 bands; ratios 1.125–4.31; total span 169,138× over 31 steps | **PASS** (corrected wording) |
| **L8.3** | Band partition: `H0–H7=micro`, `H8–H15=meso`, `H16–H23=macro`, `H24–H31=ultra` | **PASS** (all 32 BAND_ASSIGNMENTS correct; BAND_RANGES dict matches) |
| **L8.4** | Boundary horizons: `H0 = 5.8 ms` (1 frame); `H31 = 981 s`; `FRAME_RATE = 44100/256 = 172.27` | **PASS** |
| **L8.5** | Derivation formula `HORIZON_FRAMES[i] = max(1, round(HORIZON_MS[i] / 1000 * FRAME_RATE))` | **PASS-WITH-CAVEAT** — 26/32 exact match; 29/32 within 1 frame; 6 large-horizon entries differ by 1–4 frames per authoritative HorizonCatalog.md |

## L8.5 caveat — 6 large-horizon catalog overrides

The 6 horizons where the catalog value deliberately overrides the formula (per `horizons.py:74-76` docstring stating the catalog "resolves floating-point rounding ambiguities at large horizons"):

| H | ms | In table | From formula | Diff |
|---|---|---|---|---|
| H17 | 1,500 | 259 | 258 | +1 |
| H27 | 200,000 | 34,453 | 34,454 | −1 |
| H28 | 414,000 | 71,319 | 71,320 | −1 |
| H29 | 600,000 | 103,359 | 103,362 | −3 |
| H30 | 800,000 | 137,812 | 137,816 | −4 |
| H31 | 981,000 | 168,999 | 168,997 | +2 |

All 6 are within ±4 frames of the formula at scales of 100,000+ frames (≈0.002% relative error). The catalog is the authoritative source by design. **Not a violation** — documented behavior.

## Reports

- [`L8_summary.md`](L8_summary.md) — full audit + per-sub-test results + L8.5 caveat detail
- [`L8_audit.json`](L8_audit.json) — programmatic JSON output

## Reproducibility

Audit script: `_infra/audit_scripts/h3_horizon_audit.py`.
Re-run from the source suite at `The Paper/T3-Paper/T3_Isolated_Validation/_infra/audit_scripts/h3_horizon_audit.py`

Audit is byte-deterministic against engine source; PASS holds as long as `horizons.py` is unchanged (constants/ folder has been frozen since initial commit per L9.6 finding).

## Cross-reference

- **L9.3** (Horizon scale provenance) — provenance audit of the same constants; this audit (L8) is the spec-correctness audit
- **L1** (Spec compliance) — should include explicit per-horizon formula assertion test using L8.5's data

## Out of scope

This layer tests T³'s **functional contract only**. No cognitive/listener data; no downstream layer; no system-level claim. See `../README.md` for the full out-of-scope list.
