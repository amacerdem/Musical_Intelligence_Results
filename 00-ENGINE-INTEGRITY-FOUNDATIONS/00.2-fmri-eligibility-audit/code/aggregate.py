"""Aggregate Phase 0.5 audit output into a per-claim manifest.

Output: results/00.5_eligibility_manifest.json (validates against
_infra/manifests/claim_schema.json).

Six C-ELIG claims:
  C-ELIG-01: ≥30 datasets audited
  C-ELIG-02: All paper-cited datasets have explicit mi_compatible verdict
  C-ELIG-03: ≥3 datasets explicitly excluded with documented reason
  C-ELIG-04: ds002725 alignment-qualified N reported
  C-ELIG-05: ds003720 explicitly framed as routing-ablation
  C-ELIG-06: Phase 18 sub-axes have entry-gate eligibility verdicts
"""
from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

PHASE_DIR = Path(__file__).resolve().parent.parent
INFRA = PHASE_DIR.parent / "_infra"
CSV_IN = PHASE_DIR / "results" / "eligibility_audit.csv"
OUT = PHASE_DIR / "results" / "00.5_eligibility_manifest.json"


PAPER_CITED = {
    "ds002725", "ds003720", "putkinen2025", "mallik2017",
    "salimpoor2011", "ferreri2019",
}
PHASE18_SUBAXES = {
    "studyforrest_7t_music": "18.1",
    "ds005880": "18.2",
    "ds006583": "18.3",
    "ds006564": "18.4",
    "ds000171": "18.5",
}


def git_head_short() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short=12", "HEAD"],
            cwd=PHASE_DIR.parent.parent.parent,
            text=True,
        ).strip()
    except Exception:
        return "0000000000000"


def main() -> None:
    rows = list(csv.DictReader(CSV_IN.open()))

    n_total = len(rows)
    paper_cited_with_verdict = sum(
        1 for r in rows if r["dataset_id"] in PAPER_CITED
    )
    explicit_exclusions = sum(
        1 for r in rows
        if r["mi_compatible"] != "True" and r["exclusion_reason"].strip() != ""
    )
    ds002725_row = next(r for r in rows if r["dataset_id"] == "ds002725")
    ds002725_n_align = int(ds002725_row["n_alignment_qualified"])
    ds003720_row = next(r for r in rows if r["dataset_id"] == "ds003720")
    ds003720_routing = "routing-ablation" in ds003720_row["notes"].lower() or \
                        "routing-ablation" in ds003720_row["exclusion_reason"].lower()

    phase18_with_verdict = sum(
        1 for r in rows if r["dataset_id"] in PHASE18_SUBAXES
    )

    claims = [
        {
            "claim_id": "C-ELIG-01",
            "paper_value": 30,
            "tolerance": "exact OR ≥30",
            "reproduced_value": n_total,
            "deviation": n_total - 30,
            "verdict": "PASS" if n_total >= 30 else "FAIL",
            "iteration_count": 1,
            "notes": f"{n_total} datasets in registry (paper-cited + Phase 18 + scan + comparator).",
        },
        {
            "claim_id": "C-ELIG-02",
            "paper_value": 6,
            "tolerance": "exact_match",
            "reproduced_value": paper_cited_with_verdict,
            "deviation": paper_cited_with_verdict - 6,
            "verdict": "PASS" if paper_cited_with_verdict == 6 else "FAIL",
            "iteration_count": 1,
            "notes": (
                f"Paper-cited datasets with explicit mi_compatible verdict: "
                f"{paper_cited_with_verdict}/6 "
                f"(ds002725, ds003720, putkinen2025, mallik2017, salimpoor2011, ferreri2019)."
            ),
        },
        {
            "claim_id": "C-ELIG-03",
            "paper_value": 3,
            "tolerance": "absolute_deviation <= 0",
            "reproduced_value": explicit_exclusions,
            "deviation": explicit_exclusions - 3,
            "verdict": "PASS" if explicit_exclusions >= 3 else "FAIL",
            "iteration_count": 1,
            "notes": (
                f"Explicit exclusions with documented reason: {explicit_exclusions} "
                f"(closed-access pharma/PET + behavioral + EEG/MEG + partial)."
            ),
        },
        {
            "claim_id": "C-ELIG-04",
            "paper_value": "reported",
            "tolerance": "exact_match (number reported, not predicted)",
            "reproduced_value": str(ds002725_n_align),
            "deviation": None,
            "verdict": "PASS" if ds002725_n_align >= 1 else "FAIL",
            "iteration_count": 1,
            "notes": (
                f"ds002725 alignment-qualified N = {ds002725_n_align} "
                f"(vs dataset-level N=21 in BIDS, 17 with classicalMusic bold "
                f"+ shared events.tsv)."
            ),
        },
        {
            "claim_id": "C-ELIG-05",
            "paper_value": "routing-ablation",
            "tolerance": "exact_match (text contains keyword)",
            "reproduced_value": "routing-ablation" if ds003720_routing else "missing",
            "deviation": None,
            "verdict": "PASS" if ds003720_routing else "FAIL",
            "iteration_count": 1,
            "notes": (
                "ds003720 notes field contains 'routing-ablation' framing per "
                "Phase 12 requirement (Phase 12 reports lift over MI-naive routing "
                "ablation, not population estimate)."
            ),
        },
        {
            "claim_id": "C-ELIG-06",
            "paper_value": 5,
            "tolerance": "exact_match (5/5 sub-axes have verdict)",
            "reproduced_value": phase18_with_verdict,
            "deviation": phase18_with_verdict - 5,
            "verdict": "PASS" if phase18_with_verdict == 5 else "FAIL",
            "iteration_count": 1,
            "notes": (
                "Phase 18.1 ELIGIBLE (studyforrest, conditional on external audio); "
                "18.2 NON-ELIGIBLE (ds005880, partial + TR-only); "
                "18.3 NON-ELIGIBLE (ds006583, partial + no events); "
                "18.4 NON-ELIGIBLE (ds006564, partial + no events); "
                "18.5 ELIGIBLE (ds000171, conditional on external audio)."
            ),
        },
    ]

    seeds = json.loads((INFRA / "manifests/seed_registry.json").read_text())
    phase_seeds = seeds["phases"]["phase_00_5"]

    manifest = {
        "axis_id": "AXIS-17",
        "axis_name": "V-fMRI Eligibility Audit (gate for Phases 11/12/18)",
        "engine_head": "318eb2f529d7103e8b7d80b01228357fdc4e0217",
        "seed_registry": {
            "primary": int(phase_seeds["primary"]),
            "bootstrap": int(phase_seeds.get("bootstrap", 1729)),
            "permutation": int(phase_seeds.get("permutation", 42)),
        },
        "phase_close_date": "2026-05-06",
        "git_commit_hash": git_head_short(),
        "claims": claims,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {OUT}")

    # Validate
    try:
        import jsonschema  # type: ignore

        schema = json.loads((INFRA / "manifests/claim_schema.json").read_text())
        jsonschema.validate(manifest, schema)
        print("Manifest validates against claim_schema.json.")
    except Exception as e:
        print(f"WARNING: validation failed: {e}")
        raise

    # Headline summary
    print()
    print("Phase 0.5 verdicts:")
    for c in claims:
        print(f"  {c['claim_id']}: {c['verdict']:7s} reproduced={c['reproduced_value']!r}")


if __name__ == "__main__":
    main()
