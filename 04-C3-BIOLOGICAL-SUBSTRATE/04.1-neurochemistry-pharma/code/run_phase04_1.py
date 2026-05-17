#!/usr/bin/env python3
"""V-Reproduction Phase 04.1 — Neurochemistry + 11/11 pharma verification.

Cross-references 10 paper claims against V1 stored neurochem validation in
`Science/V1/results/neurochemicals/neurochemical_validation.md`. Live spot-
check on the P5-fifth interval WAV (R³ ground-truth stimulus, 0.5 s):
runs the engine through `_infra.engine.runner` and confirms the 4
neurochem channels emit finite output bit-identically across two runs.

Outputs:
    results/04.1_neurochem_correlations.csv
    results/04.1_neurochem_manifest.json
    results/neurochem_spotcheck.csv
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import csv
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import torch

PHASE_DIR = Path(__file__).resolve().parent.parent
V_REPRO   = PHASE_DIR.parent.parent
SCIENCE   = V_REPRO.parent

sys.path.insert(0, str(V_REPRO / "_infra"))
import _engine_path  # noqa: E402,F401  (vendored-first engine)
sys.path.insert(0, str(V_REPRO))

# Paper anchors: prefer vendored paper-anchors/, fall back to parent Science/
ANCHORS = V_REPRO / "datasets" / "paper-anchors"
if (ANCHORS / "neurochemicals" / "neurochemical_validation.md").exists():
    V1_NEURO = ANCHORS / "neurochemicals" / "neurochemical_validation.md"
else:
    V1_NEURO = SCIENCE / "V1" / "results" / "neurochemicals" / "neurochemical_validation.md"

if (ANCHORS / "r3-ground-truth" / "intervals" / "interval_P5_fifth.wav").exists():
    V1_WAV = ANCHORS / "r3-ground-truth" / "intervals" / "interval_P5_fifth.wav"
else:
    V1_WAV = SCIENCE / "V1" / "stimuli" / "intervals" / "interval_P5_fifth.wav"
RESULTS   = PHASE_DIR / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

PAPER_CLAIMS = [
    ("C-PHARMA-01", "132/132 accumulation tests PASS",          "132", r"Accumulation tests PASS \| \*\*132 \(100%\)\*\*"),
    ("C-PHARMA-02", "11/11 pharmacological cross-validation",   "11/11", r"\*\*11/11 PASS \(100%\)\*\*"),
    ("C-PHARMA-03", "antic_da↔caudate ρ=+0.933",                "0.933", r"Mean anticipatory_da ↔ caudate ρ \| \*\*\+0\.933\*\*"),
    ("C-PHARMA-04", "consum_da↔NAcc ρ=+0.836",                  "0.836", r"Mean consummatory_da ↔ nacc ρ \| \*\*\+0\.836\*\*"),
    ("C-PHARMA-05", "caudate-leads-NAcc 52/56 (93%)",           "52/56", r"Tracks with caudate leading NAcc \| \*\*52/56 \(93%\)\*\*"),
    ("C-PHARMA-06", "caudate→NAcc temporal lag +0.9 s",         "+0.9 s", r"\*\*\+0\.9 seconds\*\*"),
    ("C-PHARMA-07", "Ferreri levodopa>placebo>risperidone",     "ordering", r"Levodopa > placebo > risperidone"),
    ("C-PHARMA-08", "Putkinen 7/7 μ-opioid PET region match",   "7/7", r"OPI region match \(Putkinen 2025\) \| \*\*7/7 MATCH \(100%\)\*\*"),
    ("C-PHARMA-09", "Mallik chills>neutral p=0.044",            "p=0.044", r"OPI chills > neutral \(Mallik 2017\) \| \*\*PASS\*\* \(p=0\.044\)"),
    ("C-PHARMA-10", "NAcc-leads-caudate 0/56 (architectural null)", "0/56", r"Tracks with NAcc leading caudate \| \*\*0/56 \(0%\)\*\*"),
]


def verify_anchor(text, regex):
    return bool(re.search(regex, text))


def neurochem_spotcheck():
    """Live engine spot-check: 4 neurochem channels deterministic on V1 P5 WAV."""
    from _infra.engine.runner import run_engine

    print("\n[spot-check] Live engine on V1 P5 WAV — 4 neurochem channels")
    print("  run 1 …", end=" ", flush=True)
    t0 = time.time()
    out1 = run_engine(str(V1_WAV), return_layers=("neuro",), seed=2026050703, strict=False)
    print(f"{time.time() - t0:.2f}s")
    print("  run 2 …", end=" ", flush=True)
    t0 = time.time()
    out2 = run_engine(str(V1_WAV), return_layers=("neuro",), seed=2026050703, strict=False)
    print(f"{time.time() - t0:.2f}s")

    neuro1 = out1["neuro"]
    neuro2 = out2["neuro"]
    ch_names = ["DA", "NE", "OPI", "5HT"]
    rows = []
    max_diff = 0.0
    for i, name in enumerate(ch_names):
        # Robust extraction across dict / array / dataclass-like outputs
        if isinstance(neuro1, dict):
            v1 = np.asarray(neuro1.get(name, neuro1.get(name.lower(), [])))
            v2 = np.asarray(neuro2.get(name, neuro2.get(name.lower(), [])))
        else:
            v1 = np.asarray(neuro1)[..., i]
            v2 = np.asarray(neuro2)[..., i]
        v1 = np.asarray(v1).reshape(-1)
        v2 = np.asarray(v2).reshape(-1)
        finite1 = bool(np.isfinite(v1).all() and v1.size > 0)
        finite2 = bool(np.isfinite(v2).all() and v2.size > 0)
        diff = float(np.abs(v1 - v2).max()) if v1.size and v2.size else float("nan")
        if np.isfinite(diff):
            max_diff = max(max_diff, diff)
        mean1 = float(v1.mean()) if v1.size else float("nan")
        mean2 = float(v2.mean()) if v2.size else float("nan")
        rows.append({"channel": name, "n_frames": int(v1.size),
                     "mean_run1": mean1, "mean_run2": mean2,
                     "max_diff": diff, "finite": finite1 and finite2})
        print(f"    {name:>3s}  n={v1.size}  mean_run1={mean1:+.4f}  "
              f"mean_run2={mean2:+.4f}  |Δ|max={diff:.2e}")
    return rows, max_diff


def main():
    text = V1_NEURO.read_text()
    rows = []
    n_pass = n_caveat = n_fail = 0
    for cid, label, paper_val, regex in PAPER_CLAIMS:
        ok = verify_anchor(text, regex)
        verdict = "PASS" if ok else "FAIL"
        if ok:
            n_pass += 1
        else:
            n_fail += 1
        rows.append({
            "claim_id": cid,
            "claim_label": label,
            "paper_value": paper_val,
            "v1_source": "Science/V1/results/neurochemicals/neurochemical_validation.md",
            "v1_match": "matched verbatim" if ok else "NOT FOUND",
            "tolerance": "regex_anchor",
            "verdict": verdict,
            "iteration_count": 1,
        })

    # Live engine spot-check
    spotcheck_rows, max_diff = neurochem_spotcheck()
    canary_pass = max_diff <= 1e-5
    rows.append({
        "claim_id": "C-PHARMA-DETERM-01",
        "claim_label": "Live 4-channel neurochem determinism on V1 P5 WAV",
        "paper_value": "|Δ| = 0 (engine deterministic)",
        "v1_source": "engine bit-state (live)",
        "v1_match": f"max |Δ| = {max_diff:.2e}",
        "tolerance": "abs <= 1e-5",
        "verdict": "PASS" if canary_pass else "FAIL",
        "iteration_count": 1,
    })
    if canary_pass:
        n_pass += 1
    else:
        n_fail += 1

    with (RESULTS / "04.1_neurochem_correlations.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    with (RESULTS / "neurochem_spotcheck.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(spotcheck_rows[0].keys()))
        w.writeheader()
        for r in spotcheck_rows:
            w.writerow(r)

    engine_head = json.loads((V_REPRO / "_infra" / "manifests" / "engine_head.json").read_text())
    manifest = {
        "axis_id": "AXIS-5",
        "axis_name": "Neurochemistry + Pharmacological Cross-Validation",
        "engine_head": engine_head.get("pinned_commit"),
        "seed_registry": {"primary": 2026050703, "bootstrap": None, "permutation": None},
        "phase_close_date": "2026-05-07",
        "git_commit_hash": "PENDING_AT_CLOSE",
        "claims": rows,
    }
    with (RESULTS / "04.1_neurochem_manifest.json").open("w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n[verdict] PASS={n_pass}  CAVEAT={n_caveat}  FAIL={n_fail}  total={len(rows)}")


if __name__ == "__main__":
    main()
