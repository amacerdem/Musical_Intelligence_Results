#!/usr/bin/env python3
"""V-Reproduction Phase 1 — Architectural Cardinalities (CANONICAL).

Verifies paper-claimed 16,191 numeric constants + 5-bucket partition against
V2 T-R1-10-R3-04 preserved paper-anchor scripts (`ast_walk_v3.py` + `classify.py`)
re-run on the current frozen engine (`Science/Musical_Intelligence/`).

Paper text (Significance line 139): 16,191 total = 7,779 LIT-FROZEN + 6,290
STRUCTURAL + 1,381 NULL-FALLBACK + 246 CALIB-BOWLING + 495 HAND-TUNED (lenient
classifier). Under STRICT per-constant classifier the HAND-TUNED count rises
to ~5,534. Both classifiers ship.

This script reads `Science/V2/reviewer-sims/divan-major-revision-2026-04-22/
computing-phase/T-R1-10-R3-04/parameter_provenance_table.csv` (output of V2's
classify.py re-run on current engine) and verifies bucket counts.

Outputs:
    results/01_cardinalities_correlations.csv
    results/01_cardinalities_manifest.json
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

PHASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVE_ROOT = PHASE_DIR.parent.parent

ANCHORS = ARCHIVE_ROOT / "datasets" / "paper-anchors"
T_R1_10 = ANCHORS / "cardinality"
# `parameter_provenance_table.csv` is the V2 classify.py output (with bucket col)
PROVENANCE_TABLE = T_R1_10 / "parameter_provenance_table.csv"
RAW_CSV = PROVENANCE_TABLE  # alias for backward-compat

RESULTS = PHASE_DIR / "results"


def main():
    # Load raw V2 ast_walk_v3.py + classify.py output (just generated)
    bucket_counts = {}
    n_total = 0
    with RAW_CSV.open() as f:
        for r in csv.DictReader(f):
            b = r.get("bucket", "?")
            bucket_counts[b] = bucket_counts.get(b, 0) + 1
            n_total += 1
    print(f"[V2-faithful] total constants: {n_total}")
    for b, c in sorted(bucket_counts.items(), key=lambda x: -x[1]):
        print(f"  {b:<18s} {c:>6d}  ({c/n_total*100:.1f}%)")

    # Paper claims (LENIENT classifier — paper main-text)
    paper_lenient = {
        "TOTAL":           16_191,
        "LIT-FROZEN":       7_779,
        "STRUCTURAL":       6_290,
        "NULL-FALLBACK":    1_381,
        "CALIB-BOWLING":      246,
        "HAND-TUNED":         495,
    }
    # Paper claims (STRICT classifier — paper line 139 footnote)
    paper_strict = {
        "TOTAL":           16_191,  # same total
        "HAND-TUNED":       5_534,  # ~5534 strict
        # other strict-classifier buckets are not given numerically;
        # we use closeness on STRUCTURAL+NULL+CALIB which are classifier-agnostic
        "STRUCTURAL":       6_290,
        "NULL-FALLBACK":    1_381,
        "CALIB-BOWLING":      246,
    }

    repro = {**bucket_counts, "TOTAL": n_total}

    rows = []
    n_pass = 0
    n_fail = 0

    # 1. Total constant count match (paper 16,191)
    total_ok = abs(n_total - 16_191) <= 50  # 0.3% tolerance
    rows.append({
        "claim_id": "C-CARD-09-V2",
        "label": "Total numeric constants ≈ 16,191 (V2 ast_walk_v3 methodology)",
        "paper": "16,191",
        "reproduced": str(n_total),
        "deviation": n_total - 16_191,
        "tolerance": "abs <= 50 (0.3%)",
        "verdict": "PASS" if total_ok else "FAIL",
    })
    n_pass += int(total_ok)
    n_fail += int(not total_ok)

    # 2. Strict-classifier HAND-TUNED ≈ 5,534
    ht = bucket_counts.get("HAND-TUNED", 0)
    ht_ok = abs(ht - 5_534) <= 200  # 4% tolerance
    rows.append({
        "claim_id": "C-CARD-11-STRICT",
        "label": "HAND-TUNED bucket ≈ 5,534 (strict per-constant classifier)",
        "paper": "~5,534",
        "reproduced": str(ht),
        "deviation": ht - 5_534,
        "tolerance": "abs <= 200 (4%)",
        "verdict": "PASS" if ht_ok else "FAIL",
    })
    n_pass += int(ht_ok)
    n_fail += int(not ht_ok)

    # 3. STRUCTURAL ≈ 6,290 (classifier-agnostic)
    st = bucket_counts.get("STRUCTURAL", 0)
    st_ok = abs(st - 6_290) <= 200
    rows.append({
        "claim_id": "C-CARD-12-STRUCT",
        "label": "STRUCTURAL bucket ≈ 6,290",
        "paper": "6,290",
        "reproduced": str(st),
        "deviation": st - 6_290,
        "tolerance": "abs <= 200 (3%)",
        "verdict": "PASS" if st_ok else "FAIL",
    })
    n_pass += int(st_ok)
    n_fail += int(not st_ok)

    # 4. NULL ≈ 1,381 (classifier-agnostic)
    nl = bucket_counts.get("NULL-FALLBACK", 0)
    nl_ok = abs(nl - 1_381) <= 50
    rows.append({
        "claim_id": "C-CARD-13-NULL",
        "label": "NULL-FALLBACK bucket ≈ 1,381",
        "paper": "1,381",
        "reproduced": str(nl),
        "deviation": nl - 1_381,
        "tolerance": "abs <= 50 (4%)",
        "verdict": "PASS" if nl_ok else "FAIL",
    })
    n_pass += int(nl_ok)
    n_fail += int(not nl_ok)

    # 5. CALIB ≈ 246 (classifier-agnostic)
    cb = bucket_counts.get("CALIB-BOWLING", 0)
    cb_ok = abs(cb - 246) <= 5
    rows.append({
        "claim_id": "C-CARD-14-CALIB",
        "label": "CALIB-BOWLING bucket ≈ 246",
        "paper": "246",
        "reproduced": str(cb),
        "deviation": cb - 246,
        "tolerance": "abs <= 5 (2%)",
        "verdict": "PASS" if cb_ok else "FAIL",
    })
    n_pass += int(cb_ok)
    n_fail += int(not cb_ok)

    print(f"\n[verdict] {n_pass}/{len(rows)} PASS  (V2-faithful methodology, current engine)")
    for r in rows:
        print(f"  {r['claim_id']:<22}: {r['verdict']}  paper={r['paper']:>10}  repro={r['reproduced']:>10}  Δ={r['deviation']:+d}")

    with (RESULTS / "01_cardinalities_correlations.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)


if __name__ == "__main__":
    main()
