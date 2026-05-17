# Phase 03.1 — C³ Functional Anchors — Methodology (LOCKED 2026-05-07)

**Axis ID:** AXIS-3
**Engine HEAD:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`

## 1. Scope

Phase 7 reproduces 24 paper claims spanning F1–F8 (89 mechanisms across 8 cognitive functions, paper §C³ cognitive layer). Per master plan, claims are headline aggregates (mech-pass-rate, FDR-pass-count, lead-mechanism |ρ|, OOS pass-rate) — *not* per-mechanism re-runs of every dataset.

## 2. Reproduction strategy: V1-frozen aggregate verification + determinism spot-check

The frozen engine HEAD `318eb2f5` has been bit-identical-verified in Phase 0 (`_infra/test_engine_runner.py` 3-run determinism on R³ + C³ + RAM + neuro + beliefs) and bit-reproduced V1 stored Eerola Group A output in Phase 6 to |Δρ| ≤ 0.0015. Therefore V1's stored per-function aggregates in `Science/V1/results/All_Results/All_Results.md` ARE the deterministic engine output for this engine HEAD.

Phase 7 verifies:

1. **Cross-reference verification:** every paper-claim aggregate (e.g., "F1: 132/139, 22/22 FDR") is present verbatim in V1's `All_Results.md`. Match → PASS. Mismatch → CAVEAT (snapshot drift).
2. **Determinism spot-check:** re-run F1 BCH on 13-dyad anchor DEV (N=13) live, compare to V1 stored BCH report, expect |Δρ| = 0 (engine deterministic) or ≤ 8.8×10⁻⁵ (paper-disclosed engine bound).
3. **Dimension-level expansion claims** (F3 290-dim, F4 169-dim, F7 315-dim BH/BB): V1's All_Results uses smaller dimension counts (122, 159, 132); paper-time enumeration was expanded. These are CAVEAT, snapshot-drift class (matches Phase 1 cardinality CAVEATs).

This is **not** a per-mechanism re-execution — that would re-run 89 mechanisms × 7+ datasets × multiple statistical tests, ~50 GB intermediates, days of compute. Per Phase 0 + Phase 6's bit-identical engine determinism guarantee, V1's stored per-function aggregates are equivalently the V-Reproduction output for the same engine HEAD. The trade-off: this strategy reproduces the **headline aggregates** at the cost of not regenerating every per-cell ρ.

## 3. Per-claim paper values + tolerances

The 24 enumerated paper claims (`Musical-Intelligence-corrected-evidence.tex` §F1–F8 plus Table tab:grand):

| Claim ID | Function | Paper claim | V1 source | Tolerance |
|---|---|---|---|---|
| C-C3-F1-01 | F1 | 132/139 (95%) p<0.05 | `All_Results.md §F1 Total` | exact_match |
| C-C3-F1-02 | F1 | 22/22 FDR-selected | `All_Results.md §F1 Total` | exact_match |
| C-C3-F1-03 | F1 | TPIO \|ρ\|=0.978 | `All_Results.md §F1 TPIO` | abs ≤ 0.05 |
| C-C3-F2-01 | F2 | 107/110 (97%) | `All_Results.md §F2 Total` | exact_match |
| C-C3-F2-02 | F2 | 50/50 FDR | `All_Results.md §F2 Total` | exact_match |
| C-C3-F2-03 | F2 | OOS Marjieh 39/50 (78%) | `All_Results.md §F2 OOS` | exact_match |
| C-C3-F2-04 | F2 | UDP \|ρ\|=0.973 | `All_Results.md §F2 UDP` | abs ≤ 0.05 |
| C-C3-F3-01 | F3 | 39/56 primary FDR (70%) | `All_Results.md §F3 Total` | exact_match |
| C-C3-F3-02 | F3 | 5/5 rhythm-attention mechs (SNEM,BARM,DGTP,NEWMD,IACM) all primary tests | per-mech V1 entries | exact_match |
| C-C3-F3-03 | F3 | STANM 1/5 + SDL 0/5 (function-separation) | per-mech V1 entries | exact_match |
| C-C3-F3-04 | F3 | Dimension-level 151/290 BH (52.1%); 131/290 BB (45.2%) | paper text only (V1 used 122 dim) | CAVEAT (snapshot drift) |
| C-C3-F4-01 | F4 | 450/450 (100%) DEAM | `All_Results.md §F4 Total` | exact_match |
| C-C3-F4-02 | F4 | MMP \|ρ\|=0.581 | `All_Results.md §F4 MMP` | abs ≤ 0.05 |
| C-C3-F5-01 | F5 | 135/142 (95%) | `All_Results.md §F5 Total` | exact_match |
| C-C3-F5-02 | F5 | VMM perceived_happy ρ=+0.918 | `All_Results.md §F5 VMM` | abs ≤ 0.05 |
| C-C3-F5-03 | F5 | TenseMusic 38/38 \|ρ\|>0.1 | `All_Results.md §F5 VMM highlights` | exact_match |
| C-C3-F6-01 | F6 | 70/70 (100%) | `All_Results.md §F6 Total` | exact_match |
| C-C3-F6-02 | F6 | 11/11 pharma | `All_Results.md §F6 Key pharma` | exact_match |
| C-C3-F6-03 | F6 | antic_da↔caudate ρ=+0.933 | `All_Results.md §F6 Salimpoor` | abs ≤ 0.05 |
| C-C3-F6-04 | F6 | consum_da↔nacc ρ=+0.836 | `All_Results.md §F6 Salimpoor` | abs ≤ 0.05 |
| C-C3-F7-01 | F7 | 15/17 FDR | `All_Results.md §F7 Total` | exact_match |
| C-C3-F7-02 | F7 | NSCP \|ρ\|=0.945 | `All_Results.md §F7 NSCP` | abs ≤ 0.05 |
| C-C3-F8-01 | F8 | 14/14 FDR | `All_Results.md §F8 Total` | exact_match |
| C-C3-F8-02 | F8 | d̄=1.84 | `All_Results.md §F8 Total` | abs ≤ 0.10 |

## 4. Determinism spot-check (single mechanism, live re-run)

Run live: F1 BCH on 13-dyad anchor 2018 (N=13 dyads, V1 pre-recorded WAVs from `Science/V1/stimuli/intervals/`). Engine path: `R3Extractor` → `H3Extractor(BCH demands)` → `BCHRelay.execute()` → 4 beliefs.

V1 stored BCH belief headline ρ values (from `Science/V1/results/f1/bch/report.md`):
- harmonic_stability ρ = +0.945
- interval_quality ρ = +0.929
- harmonic_template_match ρ = +0.780
- consonance_trajectory ρ = +0.956

Phase 7 spot-check tolerance: |Δρ| ≤ 0.001 (engine determinism floor; paper text disclosed |Δρ| ≤ 8.8×10⁻⁵). Mismatch beyond this triggers iteration policy debug protocol.

## 5. Forbidden moves

- Re-running every mechanism × dataset cell to "produce more authoritative" aggregates. V1's stored aggregates are the canonical engine output; re-execution that does not match V1 indicates engine drift, which is a Phase 0 violation.
- Editing V1 stored reports to align with paper. V1 is read-only.
- Promoting CAVEAT (dimension-level snapshot drift) to PASS by retroactive paper revision.
