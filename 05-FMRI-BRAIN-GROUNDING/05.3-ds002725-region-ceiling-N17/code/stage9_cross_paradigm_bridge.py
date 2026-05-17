#!/usr/bin/env python3
"""Phase 21 — Stage 9 (Option F): Cross-paradigm bridge ds002725 ↔ ds003720.

Aggregates already-computed results from Stage 3 (ds002725 LOSO ceiling) and
Stage 8 (ds003720 per-region encoder) into a single comparison table.

For each region R:
  - r_002725_ceiling = Stage 3 LOSO ceiling (cross-subject BOLD reliability)
  - r_003720_encoder = Stage 8 mean encoder r (N=4 voxel-aware)
  - efficiency_F     = r_003720 / r_002725_ceiling (when ceiling > 0.05)
  - cross_paradigm_verdict = STRONG / MIXED / NULL based on both signs

Asks: where does MI prediction show paradigm-cross consistency?

Output:
  data/stage9_cross_paradigm_bridge.csv
  results/_logs/stage9_summary.json
"""
from __future__ import annotations

import csv
import json
import time
from datetime import datetime
from pathlib import Path

import numpy as np

PHASE21_ROOT = Path("/Volumes/SRC-9/SRC Musical Intelligence/Science/V8-Additional-fMRI/21-mi-fmri-rigorous-mapping")
DATA_DIR = PHASE21_ROOT / "data"
LOGS_DIR = PHASE21_ROOT / "results" / "_logs"

STAGE3_CSV = DATA_DIR / "stage3_ceiling_ds002725.csv"  # ds002725 full-scan ceiling
STAGE4_CSV = DATA_DIR / "stage4_encoder_ds002725.csv"  # ds002725 Mendelssohn encoder
STAGE8_CSV = DATA_DIR / "stage8_ds003720_per_region.csv"  # ds003720 N=4 encoder

EFFECT_FLOOR = 0.05


def main():
    t_start = time.time()
    log_path = LOGS_DIR / "stage9.log"
    log_fp = open(log_path, "a")
    def log(msg=""):
        print(msg)
        log_fp.write(msg + "\n")
        log_fp.flush()

    log(f"\n=== Stage 9 cross-paradigm bridge ds002725 ↔ ds003720 @ {datetime.utcnow().isoformat()}Z ===")

    # Read Stage 3 (ds002725 full-scan ceiling)
    ds002725_ceiling = {}
    with open(STAGE3_CSV) as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            try:
                r_idx = int(row["region_idx"])
            except ValueError:
                continue
            if row["status"] != "OK":
                continue
            ds002725_ceiling[r_idx] = {
                "region_name": row["region_name"],
                "is_brainstem": row["is_brainstem"] == "True",
                "ceiling_point": float(row["point_estimate"]),
                "ceiling_ci_lo": float(row["ci_95_lo"]),
                "ceiling_ci_hi": float(row["ci_95_hi"]),
                "p_null": float(row["p_null"]),
                "passes_floor": row["passes_floor"] == "True",
            }
    log(f"  Loaded ds002725 Stage 3 ceilings: {len(ds002725_ceiling)} regions")

    # Read Stage 4 (ds002725 Mendelssohn encoder)
    ds002725_encoder = {}
    with open(STAGE4_CSV) as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            try:
                r_idx = int(row["region_idx"])
            except ValueError:
                continue
            if row["status"] != "OK":
                continue
            ds002725_encoder[r_idx] = {
                "r_mi": float(row["r_mi_point"]),
                "verdict": row["verdict"],
                "p_null": float(row["p_null"]),
            }
    log(f"  Loaded ds002725 Stage 4 encoder: {len(ds002725_encoder)} regions")

    # Read Stage 8 (ds003720 per-region encoder)
    ds003720_encoder = {}
    with open(STAGE8_CSV) as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            try:
                r_idx = int(row["region_idx"])
            except ValueError:
                continue
            ds003720_encoder[r_idx] = {
                "fz_mean_r": float(row["fz_mean_r"]),
                "verdict": row["verdict"],
            }
    log(f"  Loaded ds003720 Stage 8 encoder: {len(ds003720_encoder)} regions")

    # Cross-paradigm comparison
    log(f"\n  Per-region cross-paradigm comparison:")
    log(f"  {'idx':>4} {'region':<14} {'BS':<3} {'002725_ceil':>12} {'002725_enc':>12} {'002725_vrd':<14} {'003720_enc':>12} {'003720_vrd':<14} {'cross_pdgm':<10}")

    rows = []
    for r_idx in sorted(ds002725_ceiling.keys()):
        c = ds002725_ceiling[r_idx]
        e002 = ds002725_encoder.get(r_idx, {})
        e003 = ds003720_encoder.get(r_idx, {})

        ds002725_pass = c["passes_floor"] and c["p_null"] < 0.05
        ds002725_saturating = e002.get("verdict", "") in ("AT_CEILING", "EXCEEDS")
        ds003720_above_floor = e003.get("fz_mean_r", 0) > EFFECT_FLOOR

        # Cross-paradigm verdict
        if ds002725_saturating and ds003720_above_floor:
            cross_verdict = "STRONG"
        elif ds002725_saturating and e003.get("fz_mean_r", 0) > 0:
            cross_verdict = "MIXED"
        elif ds002725_pass and not ds003720_above_floor:
            cross_verdict = "DS002725_ONLY"
        elif not ds002725_pass and ds003720_above_floor:
            cross_verdict = "DS003720_ONLY"
        else:
            cross_verdict = "NULL_BOTH"

        is_bs_short = "BS" if c["is_brainstem"] else ""
        log(f"  {r_idx:>4} {c['region_name']:<14} {is_bs_short:<3} "
            f"{c['ceiling_point']:>+12.4f} "
            f"{e002.get('r_mi', float('nan')):>+12.4f} {e002.get('verdict', '-'):<14} "
            f"{e003.get('fz_mean_r', float('nan')):>+12.4f} {e003.get('verdict', '-'):<14} "
            f"{cross_verdict:<10}")

        rows.append({
            "region_idx": r_idx,
            "region_name": c["region_name"],
            "is_brainstem": c["is_brainstem"],
            "ds002725_ceiling": c["ceiling_point"],
            "ds002725_encoder": e002.get("r_mi"),
            "ds002725_verdict": e002.get("verdict"),
            "ds003720_encoder": e003.get("fz_mean_r"),
            "ds003720_verdict": e003.get("verdict"),
            "cross_paradigm_verdict": cross_verdict,
        })

    # Tally
    non_bs = [r for r in rows if not r["is_brainstem"]]
    counts = {}
    for r in non_bs:
        v = r["cross_paradigm_verdict"]
        counts[v] = counts.get(v, 0) + 1
    log(f"\n  ===  CROSS-PARADIGM SUMMARY (21 non-brainstem) ===")
    for v in ("STRONG", "MIXED", "DS002725_ONLY", "DS003720_ONLY", "NULL_BOTH"):
        log(f"    {v:<16}: {counts.get(v, 0):>2}")

    # Write CSV
    with open(DATA_DIR / "stage9_cross_paradigm_bridge.csv", "w") as f:
        f.write("region_idx,region_name,is_brainstem,ds002725_ceiling,ds002725_encoder,ds002725_verdict,ds003720_encoder,ds003720_verdict,cross_paradigm_verdict\n")
        for r in rows:
            f.write(f"{r['region_idx']},{r['region_name']},{r['is_brainstem']},"
                    f"{r['ds002725_ceiling']},{r['ds002725_encoder']},{r['ds002725_verdict']},"
                    f"{r['ds003720_encoder']},{r['ds003720_verdict']},{r['cross_paradigm_verdict']}\n")
    log(f"\n  wrote: {DATA_DIR / 'stage9_cross_paradigm_bridge.csv'}")

    summary = {
        "_meta": {
            "phase": "21-mi-fmri-rigorous-mapping",
            "stage": 9,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "pre_reg_version": "v1.4",
            "wallclock_s": time.time() - t_start,
            "n_regions_non_brainstem": len(non_bs),
        },
        "headline": counts,
        "per_region": rows,
    }
    (LOGS_DIR / "stage9_summary.json").write_text(json.dumps(summary, indent=2))
    log(f"  wrote: {LOGS_DIR / 'stage9_summary.json'}")
    log(f"  wallclock: {summary['_meta']['wallclock_s']:.3f}s")
    log_fp.close()


if __name__ == "__main__":
    main()
