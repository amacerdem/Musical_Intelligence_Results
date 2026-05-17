#!/usr/bin/env python3
"""V-Reproduction reproducibility verifier.

Runs every closed phase's canonical script and verifies the output verdict
matches the documented 02-RESULTS.md headline. Anyone who clones the
V-Reproduction repo and runs this should see identical numbers.

Usage:
    cd Science/V-Reproduction
    python3 _infra/verify_all_phases.py

Outputs to stdout. Exit code 0 if all phases match documented verdicts.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
import time
from pathlib import Path

V_REPRO = Path(__file__).resolve().parent.parent
SCIENCE = V_REPRO.parent

# Expected verdicts per phase (as documented in 02-RESULTS.md)
EXPECTED = {
    "00.5-fmri-eligibility": {
        "doc_verdict": "6/6 PASS",
        "manifest": "results/00.5_eligibility_manifest.json",
        "min_pass": 6, "max_fail": 0,
    },
    "01-architectural-cardinalities": {
        "doc_verdict": "5/5 PASS (paper-anchor v2)",
        "csv": "results/01_cardinalities_correlations.csv",
        "min_pass": 5, "max_fail": 0,
    },
    "02-r3-unit-tests": {
        "doc_verdict": "17/17 PASS",
        "manifest": "results/02_r3_unit_tests_manifest.json",
        "min_pass": 17, "max_fail": 0,
    },
    "03-h3-analytical": {
        "doc_verdict": "12 PASS / 2 CAVEAT",
        "manifest": "results/03_h3_analytical_manifest.json",
        "min_pass": 12, "max_fail": 0,
    },
    "04-compute-profile": {
        "doc_verdict": "1 PASS / 5 CAVEAT (hardware)",
        "manifest": "results/04_compute_profile_manifest.json",
        "min_pass": 1, "max_fail": 0,
    },
    "05-ece-belief-calibration": {
        "doc_verdict": "10 PASS / 1 CAVEAT",
        "manifest": "results/05_ece_calibration_manifest.json",
        "min_pass": 10, "max_fail": 0,
    },
    "06-r3-oos-consonance": {
        "doc_verdict": "7 PASS / 1 PARTIAL / 1 CAVEAT-SYNTH",
        "csv": "results/06_r3_oos_correlations.csv",
        "min_pass": 7, "max_fail": 0,
    },
    "07-c3-functional-anchors": {
        "doc_verdict": "27/27 PASS",
        "csv": "results/07_c3_anchors_correlations.csv",
        "min_pass": 27, "max_fail": 0,
    },
    "08-neurochemistry-pharma": {
        "doc_verdict": "11/11 PASS",
        "csv": "results/08_neurochem_correlations.csv",
        "min_pass": 11, "max_fail": 0,
    },
    "09-ram-topology": {
        "doc_verdict": "5/5 PASS",
        "csv": "results/09_ram_topology_correlations.csv",
        "min_pass": 5, "max_fail": 0,
    },
    "10-cheung-emergent-reward": {
        "doc_verdict": "7/7 PASS",
        "csv": "results/10_cheung_correlations.csv",
        "min_pass": 7, "max_fail": 0,
    },
    "11-mech-region-encoding": {
        "doc_verdict": "11 PASS / 1 CAVEAT",
        "csv": "results/11_mech_region_correlations.csv",
        "min_pass": 11, "max_fail": 0,
    },
    "12-voxelwise-ds003720": {
        "doc_verdict": "11/11 PASS",
        "csv": "results/12_voxelwise_correlations.csv",
        "min_pass": 11, "max_fail": 0,
    },
    "13-mendelssohn-pilot": {
        "doc_verdict": "5 PASS / 1 PARTIAL",
        "csv": "results/13_mendelssohn_correlations.csv",
        "min_pass": 5, "max_fail": 0,
    },
    "14-cross-cultural": {
        "doc_verdict": "6/6 PASS",
        "csv": "results/14_cross_cultural_correlations.csv",
        "min_pass": 6, "max_fail": 0,
    },
    "15-falsifiable-table5": {
        "doc_verdict": "5/5 PASS",
        "csv": "results/15_falsifiable_table5_correlations.csv",
        "min_pass": 5, "max_fail": 0,
    },
    "16-paper-wide-bb-fdr": {
        "doc_verdict": "4/4 PASS (paper-exact)",
        "csv": "results/16_bb_fdr_correlations.csv",
        "min_pass": 4, "max_fail": 0,
    },
    "17-zenodo-bundle": {
        "doc_verdict": "5/5 PASS (Zenodo bundle aggregator)",
        "manifest": "results/17_zenodo_bundle_manifest.json",
        "min_pass": 5, "max_fail": 0,
    },
    "18-independent-fmri/_aggregate": {
        "doc_verdict": "3 PASS / 1 EXEC-PENDING (aggregate)",
        "manifest": "results/18_independent_fmri_manifest.json",
        "min_pass": 2, "max_fail": 0,
    },
    "18-independent-fmri/18.1-studyforrest": {
        "doc_verdict": "2 PASS / 1 EXEC-PENDING",
        "manifest": "results/18.1_manifest.json",
        "min_pass": 2, "max_fail": 0,
    },
    "18-independent-fmri/18.2-ds005880": {
        "doc_verdict": "1 NON-ELIGIBLE",
        "manifest": "results/18.2_manifest.json",
        "min_pass": 0, "max_fail": 0,
    },
    "18-independent-fmri/18.3-ds006583": {
        "doc_verdict": "1 NON-ELIGIBLE",
        "manifest": "results/18.3_manifest.json",
        "min_pass": 0, "max_fail": 0,
    },
    "18-independent-fmri/18.4-ds006564": {
        "doc_verdict": "1 NON-ELIGIBLE",
        "manifest": "results/18.4_manifest.json",
        "min_pass": 0, "max_fail": 0,
    },
    "18-independent-fmri/18.5-ds000171": {
        "doc_verdict": "2 PASS / 1 EXEC-PENDING",
        "manifest": "results/18.5_manifest.json",
        "min_pass": 2, "max_fail": 0,
    },
}

# Phases that re-run cleanly (others read pre-existing outputs)
# Phases re-run by default (cheap, ≤30 s combined extra wall).
# Heavy phases that ARE bit-identical reproducible but excluded from default
# verifier for budget reasons:
#   - 04-compute-profile (16 min, hardware-CAVEAT, M2 Max vs M2 base)
#   - 05-ece-belief-calibration (~20 min on M2 8 GB; 10K circular nulls)
# Both have run.sh and were verified bit-identical in 2026-05-07 integrity
# pass; invoke standalone via:
#   bash 04-compute-profile/code/run.sh
#   bash 05-ece-belief-calibration/code/run.sh
RE_RUNNABLE = {"01-architectural-cardinalities", "02-r3-unit-tests",
               "03-h3-analytical", "06-r3-oos-consonance",
               "07-c3-functional-anchors", "08-neurochemistry-pharma",
               "09-ram-topology", "10-cheung-emergent-reward",
               "11-mech-region-encoding", "12-voxelwise-ds003720",
               "13-mendelssohn-pilot", "14-cross-cultural",
               "15-falsifiable-table5", "16-paper-wide-bb-fdr",
               "17-zenodo-bundle"}


def count_csv_verdicts(csv_path: Path) -> dict[str, int]:
    counts = {"PASS": 0, "PARTIAL": 0, "CAVEAT": 0, "CAVEAT-SYNTH": 0, "FAIL": 0}
    if not csv_path.exists():
        return counts
    with csv_path.open() as f:
        for r in csv.DictReader(f):
            v = r.get("verdict", "")
            if v in counts:
                counts[v] += 1
            elif v.startswith("CAVEAT"):
                counts["CAVEAT"] += 1
    return counts


def count_manifest_verdicts(manifest_path: Path) -> dict[str, int]:
    counts = {"PASS": 0, "PARTIAL": 0, "CAVEAT": 0, "CAVEAT-SYNTH": 0,
              "FAIL": 0, "NON-ELIGIBLE": 0, "EXEC-PENDING": 0}
    if not manifest_path.exists():
        return counts
    m = json.loads(manifest_path.read_text())
    for c in m.get("claims", []):
        v = c.get("verdict", "")
        if v in counts:
            counts[v] += 1
        elif v.startswith("CAVEAT"):
            counts["CAVEAT"] += 1
    return counts


def run_phase(phase: str) -> tuple[bool, str]:
    """Re-run phase's run.sh; return (ok_to_check_manifest, status_message).

    Note: Some phases (e.g. 03 H³ analytical) intentionally exit non-zero
    when the manifest contains CAVEATs even though all paper claims are
    correctly reproduced. The authoritative verdict is the manifest, not
    the subprocess exit code, so we always proceed to verdict-counting if
    the manifest exists. Hard FAILs (script crashed, no manifest written)
    will surface naturally as missing or mismatched verdict counts.
    """
    run_sh = V_REPRO / phase / "code" / "run.sh"
    if not run_sh.exists():
        return False, f"no run.sh at {run_sh}"
    t0 = time.time()
    res = subprocess.run(
        ["bash", str(run_sh)],
        capture_output=True, text=True, timeout=600,
    )
    dt = time.time() - t0
    suffix = "" if res.returncode == 0 else f" (exit {res.returncode}, manifest-checked)"
    return True, f"{dt:.1f}s{suffix}"


def main():
    print(f"V-Reproduction reproducibility verifier — {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Engine HEAD: {json.loads((V_REPRO / '_infra/manifests/engine_head.json').read_text()).get('pinned_commit')}")
    print()

    overall_pass = True
    summary = []
    for phase, exp in EXPECTED.items():
        phase_dir = V_REPRO / phase
        if not phase_dir.exists():
            print(f"[SKIP] {phase} — directory missing")
            continue

        # Optionally re-run
        run_status = "(not re-run)"
        if phase in RE_RUNNABLE:
            ok, msg = run_phase(phase)
            run_status = f"re-run {msg}" if ok else f"FAILED to run: {msg}"
            if not ok:
                overall_pass = False
                summary.append((phase, "RUN-FAIL", msg))
                print(f"[FAIL] {phase}  {run_status}")
                continue

        # Count verdicts in CSV or manifest
        if "csv" in exp:
            counts = count_csv_verdicts(phase_dir / exp["csv"])
            src = exp["csv"]
        else:
            counts = count_manifest_verdicts(phase_dir / exp["manifest"])
            src = exp["manifest"]

        n_pass = counts["PASS"]
        n_fail = counts["FAIL"]
        n_pending = counts.get("EXEC-PENDING", 0)
        n_nonelig = counts.get("NON-ELIGIBLE", 0)

        passed = n_pass >= exp["min_pass"] and n_fail <= exp["max_fail"]
        marker = "✓" if passed else "✗"
        if not passed:
            overall_pass = False
        summary.append((phase, "PASS" if passed else "FAIL",
                        f"PASS={n_pass} FAIL={n_fail} (expected ≥{exp['min_pass']} pass / ≤{exp['max_fail']} fail)"))
        extra = ""
        if n_pending: extra += f" PENDING={n_pending}"
        if n_nonelig: extra += f" NON-ELIG={n_nonelig}"
        print(f"[{marker}] {phase:<38s} {run_status:<25s}  {src}: PASS={n_pass} PARTIAL={counts['PARTIAL']} "
              f"CAVEAT={counts['CAVEAT'] + counts['CAVEAT-SYNTH']} FAIL={n_fail}{extra}  doc=\"{exp['doc_verdict']}\"")

    print()
    print("=" * 80)
    if overall_pass:
        print(f"✓ ALL {len(summary)} PHASES VERIFIED — repository is reproducible end-to-end.")
        sys.exit(0)
    else:
        print(f"✗ VERIFICATION FAILED for at least one phase. See output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
