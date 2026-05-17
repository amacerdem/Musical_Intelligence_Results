#!/usr/bin/env python3
"""V-Reproduction Phase 06.1 — Falsifiable Table 5 Aggregator (CANONICAL).

Aggregates the 5 pre-committed falsifiable tests across Phases 6, 10, 11, 12, 13:
  #1: Carillon ρ_stumpf = -0.824 anti-overfit invariant (Phase 01.2)
  #2: ds003720 voxelwise routing-ablation 4/4 vs 1/4 vs 0/4 (Phase 05.4)
  #3: Cheung 2019 IC×ENTROPY interaction β=-0.158 (Phase 03.3)
  #4: Mendelssohn piece-specificity rank 1/7 (Phase 05.1)
  #5: Pre-reg mech×region 16/22 BH-FDR pass (Phase 05.2)

Produces single decision-gate verdict for paper Falsifiable Table 5.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

PHASE_DIR = Path(__file__).resolve().parent.parent
SECTION_06 = PHASE_DIR.parent
V_REPRO    = SECTION_06.parent

# Source phases (bottom-up Section-prefixed layout)
PHASES = {
    "r3_oos":      V_REPRO / "01-R3-PERCEPTUAL-FRONT-END"  / "01.2-r3-oos-consonance",
    "cheung":      V_REPRO / "03-C3-BEHAVIORAL-VALIDATION" / "03.3-cheung-emergent-reward",
    "mech_region": V_REPRO / "05-FMRI-BRAIN-GROUNDING"     / "05.2-mech-region-ds002725",
    "voxelwise":   V_REPRO / "05-FMRI-BRAIN-GROUNDING"     / "05.4-voxelwise-ds003720",
    "mendelssohn": V_REPRO / "05-FMRI-BRAIN-GROUNDING"     / "05.1-mendelssohn-pilot",
}


def read_phase_csv(phase_dir, csv_name):
    csv_path = phase_dir / "results" / csv_name
    return list(csv.DictReader(csv_path.open()))


def main():
    rows = []

    # #1 Carillon anti-overfit invariant (Phase 01.2 C-R3OOS-CARILLON-STUMPF)
    p6 = read_phase_csv(PHASES["r3_oos"], "06_r3_oos_correlations.csv")
    car_stumpf = next((r for r in p6 if r["claim_id"] == "C-R3OOS-CARILLON-STUMPF"), None)
    rows.append({
        "table5_id": "FT5-#1",
        "test": "Carillon ρ_stumpf = −0.824 anti-overfitting invariant",
        "source_phase": "Phase 01.2 / C-R3OOS-CARILLON-STUMPF",
        "paper_claim": "−0.824 (engine inharmonicity at A5_880Hz SUSTAINED)",
        "reproduced": car_stumpf["reproduced_value"] if car_stumpf else "MISSING",
        "verdict": car_stumpf["verdict"] if car_stumpf else "FAIL",
    })

    # #2 ds003720 voxelwise (Phase 05.4 C-VOXEL-02 + C-VOXEL-03 + C-VOXEL-04 contrast)
    p12 = read_phase_csv(PHASES["voxelwise"], "05.4_voxelwise_correlations.csv")
    v_mi = next(r for r in p12 if r["claim_id"] == "C-VOXEL-02")
    v_naive = next(r for r in p12 if r["claim_id"] == "C-VOXEL-03")
    v_random = next(r for r in p12 if r["claim_id"] == "C-VOXEL-04")
    contrast_pass = (v_mi["verdict"] == "PASS" and v_naive["verdict"] == "PASS" and v_random["verdict"] == "PASS")
    rows.append({
        "table5_id": "FT5-#2",
        "test": "ds003720 voxelwise routing-ablation 4/4 vs 1/4 vs 0/4",
        "source_phase": "Phase 05.4 / C-VOXEL-02..04",
        "paper_claim": "MI 4/4 vs MI-naive 1/4 vs Random-26 0/4 shuffle-null",
        "reproduced": f"MI {v_mi['reproduced']} / MI-naive {v_naive['reproduced']} / Random-26 {v_random['reproduced']}",
        "verdict": "PASS" if contrast_pass else "FAIL",
    })

    # #3 Cheung interaction (Phase 03.3 C-CHEUNG-01 β = -0.158)
    p10 = read_phase_csv(PHASES["cheung"], "10_cheung_correlations.csv")
    cheung_beta = next((r for r in p10 if r["claim_id"] == "C-CHEUNG-01"), None)
    cheung_in_ci = next((r for r in p10 if r["claim_id"] == "C-CHEUNG-03"), None)
    cheung_pass = (cheung_beta and cheung_beta["verdict"] == "PASS"
                   and cheung_in_ci and cheung_in_ci["verdict"] == "PASS")
    rows.append({
        "table5_id": "FT5-#3",
        "test": "Cheung 2019 IC×ENTROPY interaction β=−0.158, Cheung's −0.124 inside CI",
        "source_phase": "Phase 03.3 / C-CHEUNG-01 + C-CHEUNG-03",
        "paper_claim": "β=−0.158, CI [−0.228, −0.084] containing Cheung's −0.124",
        "reproduced": f"β={cheung_beta['reproduced_value']} / Cheung in CI: {cheung_in_ci['reproduced_value']}" if cheung_beta and cheung_in_ci else "MISSING",
        "verdict": "PASS" if cheung_pass else "FAIL",
    })

    # #4 Mendelssohn rank 1/7 (Phase 05.1 C-MEND-06)
    p13 = read_phase_csv(PHASES["mendelssohn"], "05.1_mendelssohn_correlations.csv")
    mend_rank = next((r for r in p13 if r["claim_id"] == "C-MEND-06"), None)
    rows.append({
        "table5_id": "FT5-#4",
        "test": "Mendelssohn piece-specificity rank 1/7, 2.2× lift",
        "source_phase": "Phase 05.1 / C-MEND-06",
        "paper_claim": "rank 1/7 across 7 pieces in TR 556 window, 2.2× over next-best (CAVEAT-PASS at rank-statistic level)",
        "reproduced": "documented in V2 v9.5.6 deneyler-rescore.md (next-best +0.246; 2.2× separation)",
        "verdict": "PASS" if mend_rank and mend_rank["verdict"] == "PASS" else "FAIL",
    })

    # #5 Pre-reg mech×region (Phase 05.2 C-MXREG-01 16/22)
    p11 = read_phase_csv(PHASES["mech_region"], "05.2_mech_region_correlations.csv")
    mxreg_16 = next((r for r in p11 if r["claim_id"] == "C-MXREG-01"), None)
    rows.append({
        "table5_id": "FT5-#5",
        "test": "Pre-reg mech×region encoding ds002725: 16/22 target BH-FDR pass",
        "source_phase": "Phase 05.2 / C-MXREG-01",
        "paper_claim": "16/22 target pairs survive BH-FDR at q<0.05, separation +0.105 vs 2×SE 0.048",
        "reproduced": mxreg_16["reproduced"] if mxreg_16 else "MISSING",
        "verdict": mxreg_16["verdict"] if mxreg_16 else "FAIL",
    })

    n_pass = sum(1 for r in rows if r["verdict"] == "PASS")
    n_fail = sum(1 for r in rows if r["verdict"] == "FAIL")
    print(f"\n[Falsifiable Table 5 aggregator] {n_pass}/{len(rows)} PASS")
    for r in rows:
        marker = "✓" if r["verdict"] == "PASS" else "✗"
        print(f"  {marker} {r['table5_id']:<8} {r['test'][:60]:<60} {r['verdict']}")

    fieldnames = ["table5_id", "test", "source_phase", "paper_claim", "reproduced", "verdict"]
    with (PHASE_DIR / "results" / "06.1_falsifiable_table5_correlations.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    engine_head = json.loads((V_REPRO / "_infra" / "manifests" / "engine_head.json").read_text())
    manifest = {
        "axis_id": "AXIS-12",
        "axis_name": "Falsifiable Table 5 Aggregator",
        "engine_head": engine_head.get("pinned_commit"),
        "phase_close_date": "2026-05-07",
        "git_commit_hash": "PENDING_AT_CLOSE",
        "claims": rows,
        "aggregate_verdict": "PASS" if n_pass == len(rows) else "PARTIAL",
    }
    with (PHASE_DIR / "results" / "06.1_falsifiable_table5_manifest.json").open("w") as f:
        json.dump(manifest, f, indent=2)


if __name__ == "__main__":
    main()
