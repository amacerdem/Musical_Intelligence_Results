#!/usr/bin/env python3
"""Reproducibility verifier for Musical_Intelligence_Results.

For every closed phase, this script counts the verdict atoms recorded in the
phase's canonical results file (CSV or JSON manifest) and compares them to
the documented PASS/FAIL/PARTIAL/CAVEAT headlines from CLAIMS_AND_EVIDENCE.md.

Usage:
    cd <REPO_ROOT>
    python3 _infra/verify_all_phases.py

Exit code 0 if every phase matches its documented verdict envelope; non-zero
otherwise.
"""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Per-phase expected verdicts from CLAIMS_AND_EVIDENCE.md.
# Each entry: phase_path (relative to REPO_ROOT), verdict source file
# (CSV row-counted, or JSON manifest with a "claims" list), and the pass
# envelope ((min_pass, max_fail)).
EXPECTED = {
    "00-ENGINE-INTEGRITY-FOUNDATIONS/00.1-architectural-cardinalities": {
        "doc_verdict": "10/10 PASS",
        "csv": "results/01_cardinalities_correlations.csv",
        "min_pass": 10, "max_fail": 0,
    },
    "00-ENGINE-INTEGRITY-FOUNDATIONS/00.2-fmri-eligibility-audit": {
        "doc_verdict": "6/6 PASS",
        "csv": "results/00.2_eligibility_correlations.csv",
        "min_pass": 6, "max_fail": 0,
    },
    "00-ENGINE-INTEGRITY-FOUNDATIONS/00.3-compute-profile": {
        "doc_verdict": "1 PASS / 5 CAVEAT (hardware)",
        "csv": "results/00.3_compute_profile_correlations.csv",
        "min_pass": 1, "max_fail": 0,
    },
    "01-R3-PERCEPTUAL-FRONT-END/01.2-r3-oos-consonance": {
        "doc_verdict": "8 PASS / 2 PARTIAL",
        "csv": "results/06_r3_oos_correlations.csv",
        "min_pass": 8, "max_fail": 0,
    },
    "01-R3-PERCEPTUAL-FRONT-END/01.3-cross-cultural-anchor": {
        "doc_verdict": "6/6 PASS",
        "csv": "results/14_cross_cultural_correlations.csv",
        "min_pass": 6, "max_fail": 0,
    },
    "03-C3-BEHAVIORAL-VALIDATION/03.1-c3-functional-anchors-F1-F8": {
        "doc_verdict": "26/26 PASS",
        "csv": "results/07_c3_anchors_correlations.csv",
        "min_pass": 26, "max_fail": 0,
    },
    "03-C3-BEHAVIORAL-VALIDATION/03.2-ece-belief-calibration": {
        "doc_verdict": "10 PASS / 1 CAVEAT",
        "csv": "results/per_claim_verdicts.csv",
        "min_pass": 10, "max_fail": 0,
    },
    "03-C3-BEHAVIORAL-VALIDATION/03.3-cheung-emergent-reward": {
        "doc_verdict": "7/7 PASS (Stage A) + 10 cells (Stage B)",
        "csv": "results/10_cheung_correlations.csv",
        "min_pass": 7, "max_fail": 0,
    },
    "04-C3-BIOLOGICAL-SUBSTRATE/04.1-neurochemistry-pharma": {
        "doc_verdict": "11/11 PASS",
        "csv": "results/04.1_neurochem_correlations.csv",
        "min_pass": 11, "max_fail": 0,
    },
    "04-C3-BIOLOGICAL-SUBSTRATE/04.2-ram-topology": {
        "doc_verdict": "5/5 PASS",
        "csv": "results/04.2_ram_topology_correlations.csv",
        "min_pass": 5, "max_fail": 0,
    },
    "05-FMRI-BRAIN-GROUNDING/05.1-mendelssohn-pilot": {
        "doc_verdict": "5 PASS / 1 PARTIAL",
        "csv": "results/05.1_mendelssohn_correlations.csv",
        "min_pass": 5, "max_fail": 0,
    },
    "05-FMRI-BRAIN-GROUNDING/05.2-mech-region-ds002725": {
        "doc_verdict": "11 PASS / 1 CAVEAT",
        "csv": "results/05.2_mech_region_correlations.csv",
        "min_pass": 11, "max_fail": 0,
    },
    "05-FMRI-BRAIN-GROUNDING/05.4-voxelwise-ds003720": {
        "doc_verdict": "18/18 PASS",
        "csv": "results/05.4_voxelwise_correlations.csv",
        "min_pass": 18, "max_fail": 0,
    },
    "06-PORTFOLIO-FALSIFIABILITY/06.1-falsifiable-table5": {
        "doc_verdict": "5/5 PASS",
        "csv": "results/06.1_falsifiable_table5_correlations.csv",
        "min_pass": 5, "max_fail": 0,
    },
}

# Phases with pytest-based verification (no flat verdict CSV); reported
# separately for visibility but not strictly required for a green run.
PYTEST_PHASES = (
    "01-R3-PERCEPTUAL-FRONT-END/01.1-r3-isolated-extended",
    "02-T3-TEMPORAL-LAYER/02.1-t3-isolated-extended",
    "03-C3-BEHAVIORAL-VALIDATION/03.4-chill-chillsdb",
    "03-C3-BEHAVIORAL-VALIDATION/03.5-tension-tensemusic",
    "03-C3-BEHAVIORAL-VALIDATION/03.6-emotion-pmemo-dynamic",
    "03-C3-BEHAVIORAL-VALIDATION/03.7-gems-eerola-film",
    "05-FMRI-BRAIN-GROUNDING/05.3-ds002725-region-ceiling-N17",
    "05-FMRI-BRAIN-GROUNDING/05.5-ds003720-region-ceiling-N4",
    "05-FMRI-BRAIN-GROUNDING/05.6-cross-dataset-region-prediction",
)

# Deferred / EXEC-PENDING / placeholder phases (not verified):
#   06-PORTFOLIO-FALSIFIABILITY/06.2-unified-bb-fdr-aggregator (DEFERRED)
#   05-FMRI-BRAIN-GROUNDING/05.7-independent-fmri (EXEC-PENDING)
#   99-ZENODO-BUNDLE-MANIFEST (scaffold)


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
            elif v.startswith("PASS"):
                counts["PASS"] += 1
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


def main() -> int:
    print(f"Musical_Intelligence_Results reproducibility verifier "
          f"— {time.strftime('%Y-%m-%d %H:%M:%S')}")
    pin_file = REPO_ROOT / "_infra" / "manifests" / "engine_head.json"
    if pin_file.exists():
        pin = json.loads(pin_file.read_text())
        print(f"Engine HEAD: {pin.get('pinned_commit')}")
    print()

    overall_pass = True
    for phase, exp in EXPECTED.items():
        phase_dir = REPO_ROOT / phase
        if not phase_dir.exists():
            print(f"[SKIP] {phase} — directory missing")
            overall_pass = False
            continue

        if "csv" in exp:
            counts = count_csv_verdicts(phase_dir / exp["csv"])
            src = exp["csv"]
        else:
            counts = count_manifest_verdicts(phase_dir / exp["manifest"])
            src = exp["manifest"]

        n_pass = counts["PASS"]
        n_fail = counts["FAIL"]
        passed = n_pass >= exp["min_pass"] and n_fail <= exp["max_fail"]
        marker = "PASS" if passed else "FAIL"
        if not passed:
            overall_pass = False
        print(f"[{marker}] {phase:<60s}  {src}: "
              f"PASS={n_pass} PARTIAL={counts['PARTIAL']} "
              f"CAVEAT={counts['CAVEAT'] + counts['CAVEAT-SYNTH']} "
              f"FAIL={n_fail}  doc=\"{exp['doc_verdict']}\"")

    print()
    print("Pytest-based phases (run `python3 -m pytest <phase>` to verify):")
    for phase in PYTEST_PHASES:
        present = "present" if (REPO_ROOT / phase).exists() else "MISSING"
        print(f"  [{present}] {phase}")

    print()
    print("=" * 80)
    if overall_pass:
        print(f"All CSV-verdict phases verified against documented envelopes.")
        return 0
    print("Verification FAILED for at least one phase.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
