#!/usr/bin/env python3
"""MI_Results full claim ledger verifier (paper headline reproducer).

Computes the paper's "1,137 pass/fail verdicts (219 claim-style CSV records
+ 918 pytest sub-tests)" headline by counting:

  CSV CLAIM ATOMS
    A) 14 CSV-verdict phase results/<phase>_correlations.csv (per-row)
    B) 05.7 independent-fmri sub-axis manifests (5 + 1 aggregate)
    C) 06.3 ai-baseline-ablation baseline JSON files
    D) per-phase L9 verdict reconciliation test counts (claim-style records)

  PYTEST SUB-TESTS
    E) 9 pytest phase test functions (via pytest --collect-only)
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VENV_PY = REPO_ROOT / ".venv" / "bin" / "python"

# A) 14 CSV-verdict phases
CSV_PHASES = [
    ("00.1", "00-ENGINE-INTEGRITY-FOUNDATIONS/00.1-architectural-cardinalities/results/01_cardinalities_correlations.csv"),
    ("00.2", "00-ENGINE-INTEGRITY-FOUNDATIONS/00.2-fmri-eligibility-audit/results/00.2_eligibility_correlations.csv"),
    ("00.3", "00-ENGINE-INTEGRITY-FOUNDATIONS/00.3-compute-profile/results/00.3_compute_profile_correlations.csv"),
    ("01.2", "01-R3-PERCEPTUAL-FRONT-END/01.2-r3-oos-consonance/results/06_r3_oos_correlations.csv"),
    ("01.3", "01-R3-PERCEPTUAL-FRONT-END/01.3-cross-cultural-anchor/results/14_cross_cultural_correlations.csv"),
    ("03.1", "03-C3-BEHAVIORAL-VALIDATION/03.1-c3-functional-anchors-F1-F8/results/07_c3_anchors_correlations.csv"),
    ("03.2", "03-C3-BEHAVIORAL-VALIDATION/03.2-ece-belief-calibration/results/per_claim_verdicts.csv"),
    ("03.3", "03-C3-BEHAVIORAL-VALIDATION/03.3-cheung-emergent-reward/results/10_cheung_correlations.csv"),
    ("04.1", "04-C3-BIOLOGICAL-SUBSTRATE/04.1-neurochemistry-pharma/results/04.1_neurochem_correlations.csv"),
    ("04.2", "04-C3-BIOLOGICAL-SUBSTRATE/04.2-ram-topology/results/04.2_ram_topology_correlations.csv"),
    ("05.1", "05-FMRI-BRAIN-GROUNDING/05.1-mendelssohn-pilot/results/05.1_mendelssohn_correlations.csv"),
    ("05.2", "05-FMRI-BRAIN-GROUNDING/05.2-mech-region-ds002725/results/05.2_mech_region_correlations.csv"),
    ("05.4", "05-FMRI-BRAIN-GROUNDING/05.4-voxelwise-ds003720/results/05.4_voxelwise_correlations.csv"),
    ("06.1", "06-PORTFOLIO-FALSIFIABILITY/06.1-falsifiable-table5/results/06.1_falsifiable_table5_correlations.csv"),
]

# B) 05.7 manifests
M057 = [
    "05-FMRI-BRAIN-GROUNDING/05.7-independent-fmri/_aggregate/results/05.7_independent_fmri_manifest.json",
    "05-FMRI-BRAIN-GROUNDING/05.7-independent-fmri/05.7.1-studyforrest/results/05.7.1_manifest.json",
    "05-FMRI-BRAIN-GROUNDING/05.7-independent-fmri/05.7.2-ds005880/results/05.7.2_manifest.json",
    "05-FMRI-BRAIN-GROUNDING/05.7-independent-fmri/05.7.3-ds006583/results/05.7.3_manifest.json",
    "05-FMRI-BRAIN-GROUNDING/05.7-independent-fmri/05.7.4-ds006564/results/05.7.4_manifest.json",
    "05-FMRI-BRAIN-GROUNDING/05.7-independent-fmri/05.7.5-ds000171/results/05.7.5_manifest.json",
]

# C) 06.3 baseline JSON files (each = 1 claim cell)
M063 = list((REPO_ROOT / "06-PORTFOLIO-FALSIFIABILITY/06.3-ai-baseline-ablation/results").glob("baseline_*.json"))

# D + E) pytest phases (test count = sub-tests; L9 dir = claim records)
PYTEST_PHASES = [
    "01-R3-PERCEPTUAL-FRONT-END/01.1-r3-isolated-extended",
    "02-T3-TEMPORAL-LAYER/02.1-t3-isolated-extended",
    "03-C3-BEHAVIORAL-VALIDATION/03.4-chill-chillsdb",
    "03-C3-BEHAVIORAL-VALIDATION/03.5-tension-tensemusic",
    "03-C3-BEHAVIORAL-VALIDATION/03.6-emotion-pmemo-dynamic",
    "03-C3-BEHAVIORAL-VALIDATION/03.7-gems-eerola-film",
    "05-FMRI-BRAIN-GROUNDING/05.3-ds002725-region-ceiling-N17",
    "05-FMRI-BRAIN-GROUNDING/05.5-ds003720-region-ceiling-N4",
    "05-FMRI-BRAIN-GROUNDING/05.6-cross-dataset-region-prediction",
]


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open() as f:
        return sum(1 for _ in csv.DictReader(f))


NON_CLAIM_VERDICTS = {"EXEC-PENDING", "NON-ELIGIBLE", "PENDING"}


def count_manifest_claims(path: Path) -> int:
    """Count only real verdicts (PASS/FAIL/PARTIAL/CAVEAT). Skip non-claim status."""
    if not path.exists():
        return 0
    try:
        claims = json.loads(path.read_text()).get("claims", [])
        return sum(1 for c in claims if c.get("verdict", "").upper() not in NON_CLAIM_VERDICTS)
    except Exception:
        return 0


def count_csv_rows_real_verdict(path: Path) -> int:
    """Count CSV rows whose verdict is a real claim (not EXEC-PENDING/NON-ELIGIBLE)."""
    if not path.exists():
        return 0
    with path.open() as f:
        return sum(1 for r in csv.DictReader(f)
                   if (r.get("verdict") or "").upper() not in NON_CLAIM_VERDICTS)


def count_pytest_tests(phase_path: Path) -> int:
    proc = subprocess.run(
        [str(VENV_PY), "-m", "pytest", str(phase_path), "--collect-only", "-q"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=300,
    )
    for line in (proc.stdout + proc.stderr).splitlines():
        line = line.strip()
        if line.endswith("tests collected") or "tests collected" in line:
            num = line.split()[0].replace(",", "")
            try:
                return int(num)
            except ValueError:
                continue
    return 0


def count_l9_test_fns(phase_path: Path) -> int:
    l9_dirs = list(phase_path.glob("L9_*"))
    n = 0
    for d in l9_dirs:
        for py in d.glob("*.py"):
            n += sum(1 for line in py.read_text().splitlines() if line.startswith("def test_"))
    return n


def main():
    print("=" * 70)
    print("MI_Results FULL CLAIM LEDGER VERIFIER")
    print("Paper headline target: 1,137 pass/fail verdicts")
    print("                       (219 claim-style CSV records + 918 pytest sub-tests)")
    print("=" * 70)
    print()

    # A
    print("─" * 70)
    print("A) 14 CSV-verdict phase atoms (real verdicts: PASS/FAIL/PARTIAL/CAVEAT)")
    print("─" * 70)
    total_csv = 0
    for ph, rel in CSV_PHASES:
        n = count_csv_rows_real_verdict(REPO_ROOT / rel)
        total_csv += n
        print(f"  {ph:<6} {n:>4}  {rel}")
    print(f"  {'TOTAL':<6} {total_csv:>4}")
    print()

    # B
    print("─" * 70)
    print("B) 05.7 independent-fmri sub-axis manifests")
    print("─" * 70)
    total_057 = 0
    for rel in M057:
        n = count_manifest_claims(REPO_ROOT / rel)
        total_057 += n
        print(f"  {n:>3}  {rel.split('/')[-1]}")
    print(f"  TOTAL 05.7: {total_057}")
    print()

    # C
    print("─" * 70)
    print("C) 06.3 ai-baseline-ablation baseline JSONs")
    print("─" * 70)
    total_063 = len(M063)
    for p in M063:
        print(f"  1  {p.name}")
    print(f"  TOTAL 06.3: {total_063}")
    print()

    # D
    print("─" * 70)
    print("D) Per-phase L9 verdict-reconciliation test functions")
    print("─" * 70)
    total_l9 = 0
    for rel in PYTEST_PHASES:
        n = count_l9_test_fns(REPO_ROOT / rel)
        total_l9 += n
        print(f"  {n:>3}  {rel}")
    print(f"  TOTAL L9 verdicts: {total_l9}")
    print()

    # E
    print("─" * 70)
    print("E) Pytest sub-test count per phase (via --collect-only)")
    print("─" * 70)
    total_pyt = 0
    for rel in PYTEST_PHASES:
        n = count_pytest_tests(REPO_ROOT / rel)
        total_pyt += n
        print(f"  {n:>4}  {rel}")
    print(f"  TOTAL pytest sub-tests: {total_pyt}")
    print()

    # Summary
    csv_records = total_csv + total_057 + total_063 + total_l9
    grand = csv_records + total_pyt
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  CSV claim-style records: {csv_records}  (A {total_csv} + B {total_057} + C {total_063} + D {total_l9})")
    print(f"  Pytest sub-tests:        {total_pyt}")
    print(f"  GRAND TOTAL:             {grand}")
    print()
    print(f"  Paper headline: 219 CSV records + 918 pytest sub-tests = 1,137")
    print(f"  Δ csv:   {csv_records - 219:+d}")
    print(f"  Δ pyt:   {total_pyt - 918:+d}")
    print(f"  Δ grand: {grand - 1137:+d}")


if __name__ == "__main__":
    sys.exit(main() or 0)
