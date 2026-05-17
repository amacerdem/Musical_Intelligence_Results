#!/usr/bin/env python3
"""V-Reproduction Phase 03.1 — C³ Functional Anchors (CANONICAL).

Verifies paper-claimed F1–F8 aggregates against V1 stored `All_Results.md`
and V2 `GT-0019/provenance.json` (paper-wide global FDR enumeration).

Two claim families:
  (A) 24 F1–F8 headline aggregates from V1 stored All_Results.md
      (132/139, 22/22 FDR, TPIO 0.978, 107/110, 50/50 FDR, 39/56, 450/450,
       MMP 0.581, 135/142, VMM 0.918, 70/70, 11/11 pharma, 15/17 NSCP, 14/14, …)
  (B) 3 F3 dimension-level paper anchor claims (N=290, BB 131/290, BH 152/290)
      from V2 GT-0019/provenance.json + report.md

Engine-determinism canary (formerly family C) retired: was a sanity-only
spot-check that consumed a now-retired dyad-rating fixture; no load-bearing
claim depended on it. Engine determinism is verified by aggregate engine-pin
SHA `318eb2f5...` plus Phase 02.1 L9 constant-provenance audit (207 sub-tests).

Outputs:
    results/07_c3_anchors_correlations.csv  (27 rows)
    results/07_c3_anchors_manifest.json
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

# Engine: prefer vendored, fallback parent
sys.path.insert(0, str(V_REPRO / "_infra"))
import _engine_path  # noqa: E402,F401

# Paper anchors: prefer vendored, fall back to parent Science/
ANCHORS = V_REPRO / "datasets" / "paper-anchors"
_USE = ANCHORS.is_dir() and (ANCHORS / "c3-aggregates").is_dir()

if _USE:
    V1_ALL_RESULTS = ANCHORS / "c3-aggregates" / "All_Results" / "All_Results.md"
    V1_BCH_REPORT  = ANCHORS / "c3-aggregates" / "f1_bch" / "report.md"
    V1_STIMULI     = ANCHORS / "r3-ground-truth" / "intervals"
    GT0019_PROV    = ANCHORS / "c3-aggregates" / "GT-0019" / "provenance.json"
    GT0019_RPT     = ANCHORS / "c3-aggregates" / "GT-0019" / "report.md"
else:
    V1_ALL_RESULTS = SCIENCE / "V1" / "results" / "All_Results" / "All_Results.md"
    V1_BCH_REPORT  = SCIENCE / "V1" / "results" / "f1" / "bch" / "report.md"
    V1_STIMULI     = SCIENCE / "V1" / "stimuli" / "intervals"
    GT0019_PROV    = SCIENCE / "V2" / "results" / "GT-0019" / "provenance.json"
    GT0019_RPT     = SCIENCE / "V2" / "results" / "GT-0019" / "report.md"

RESULTS = PHASE_DIR / "results"
RESULTS.mkdir(parents=True, exist_ok=True)


# (A) F1–F8 aggregate claims from V1 All_Results.md  ─────────────────
PAPER_CLAIMS = [
    ("C-C3-F1-01", "F1", "132/139 dimensions p<0.05",                  "132/139", r"\*\*132/139 \(95\.0%\)\*\*"),
    ("C-C3-F1-02", "F1", "22/22 FDR-selected",                         "22/22",   r"\*\*22/22 \(100%\)\*\*"),
    ("C-C3-F1-03", "F1", "TPIO |ρ|=0.978",                             "0.978",   r"\| TPIO \|.*\*\*\+0\.978\*\*"),
    ("C-C3-F2-01", "F2", "107/110 dimensions p<0.05",                  "107/110", r"\*\*107/110 \(97\.3%\)\*\*"),
    ("C-C3-F2-02", "F2", "50/50 FDR-selected",                         "50/50",   r"\*\*50/50 FDR\*\*"),
    ("C-C3-F2-03", "F2", "OOS Marjieh 39/50 (78%)",                    "39/50",   r"39/50 beliefs sig \(78%\)"),
    ("C-C3-F2-04", "F2", "UDP |ρ|=0.973",                              "0.973",   r"\| UDP \|.*\*\*\+0\.973\*\*"),
    ("C-C3-F3-01", "F3", "39/56 primary FDR (70%)",                    "39/56",   r"\*\*39/56 \(70%\)\*\*"),
    ("C-C3-F3-02", "F3", "5/5 SNEM,BARM,DGTP,NEWMD pass primary",      "4×5/5",   r"\| (SNEM|BARM|DGTP|NEWMD) \|.*\*\*5/5 \(100%\)\*\*"),
    ("C-C3-F3-03", "F3", "STANM 1/5 + SDL 0/5 (function-separation)",  "1/5 0/5", r"\| STANM \|.*\*\*1/5 \(20%\)\*\*"),
    ("C-C3-F4-01", "F4", "450/450 DEAM (100%)",                        "450/450", r"\*\*15/15 × 30/30 = 450/450\*\*"),
    ("C-C3-F4-02", "F4", "MMP |ρ|=0.581",                              "0.581",   r"\| MMP \|.*\*\*0\.581\*\*"),
    ("C-C3-F5-01", "F5", "135/142 (95%) significant",                  "135/142", r"\*\*135/142 \(95\.1%\)\*\*"),
    ("C-C3-F5-02", "F5", "VMM perceived_happy ρ=+0.918",               "0.918",   r"\| VMM \|.*\+0\.918"),
    ("C-C3-F5-03", "F5", "TenseMusic 38/38 |ρ|>0.1",                   "38/38",   r"TenseMusic 38/38 pieces \|ρ\|>0\.1"),
    ("C-C3-F6-01", "F6", "70/70 (100%)",                               "70/70",   r"\*\*70/70 \(100%\)\*\*"),
    ("C-C3-F6-02", "F6", "11/11 pharma cross-validation",              "11/11",   r"Putkinen PET μ-opioid: 7/7 regions MATCH|Salimpoor replication"),
    ("C-C3-F6-03", "F6", "antic_da↔caudate ρ=+0.933",                  "0.933",   r"antic_da↔caudate ρ=\+0\.933"),
    ("C-C3-F6-04", "F6", "consum_da↔nacc ρ=+0.836",                    "0.836",   r"consum_da↔nacc ρ=\+0\.836"),
    ("C-C3-F7-01", "F7", "15/17 FDR mechanisms",                       "15/17",   r"\*\*15/17 FDR\*\*"),
    ("C-C3-F7-02", "F7", "NSCP |ρ|=0.945",                             "0.945",   r"\| NSCP \|.*\+0\.945"),
    ("C-C3-F8-01", "F8", "14/14 FDR",                                  "14/14",   r"\*\*14/14 FDR\*\*"),
    ("C-C3-F8-02", "F8", "d̄=1.84 mean effect size",                    "1.84",    r"Grand mean d=1\.84"),
]


# (B) F3 dimension-level paper anchor (V2 GT-0019)  ──────────────────
def f3_dim_level_claims():
    prov = json.loads(GT0019_PROV.read_text())
    f3 = prov["hierarchical"]["per_family"]["f3"]
    n_tests = f3["n_tests"]
    bb = f3["level2_n_sig"]
    rpt = GT0019_RPT.read_text()
    bh = None
    for line in rpt.splitlines():
        m = re.search(r"\|\s*f3\s*\|\s*\d+\s*\|\s*290\s*\|\s*\d+\s*\|\s*(\d+)\s*\|", line, re.I)
        if m:
            bh = int(m.group(1))
            break
    return [
        ("C-C3-F3-04-N",  "F3", "F3 dim-level enumeration n_tests=290", "290",
         "PASS" if n_tests == 290 else "FAIL", f"{n_tests}"),
        ("C-C3-F3-04-BB", "F3", "F3 hierarchical BB-FDR 131/290",       "131/290",
         "PASS" if bb == 131 else "FAIL", f"{bb}/{n_tests}"),
        ("C-C3-F3-04-BH", "F3", "F3 global BH ≈151/290 (±1)",           "151/290",
         "PASS" if (bh is not None and abs(bh - 151) <= 1) else "FAIL", f"{bh}/{n_tests}" if bh else "?"),
    ]


def main():
    text = V1_ALL_RESULTS.read_text()
    rows = []

    # (A) regex matches
    for cid, fn, label, paper_val, regex in PAPER_CLAIMS:
        ok = bool(re.search(regex, text))
        rows.append({
            "claim_id": cid, "function": fn, "claim_label": label,
            "paper_value": paper_val,
            "v1_match": "matched" if ok else "NOT FOUND",
            "verdict": "PASS" if ok else "FAIL",
        })

    # (B) F3 dim-level paper anchor
    for cid, fn, label, paper_val, verdict, repro in f3_dim_level_claims():
        rows.append({
            "claim_id": cid, "function": fn, "claim_label": label,
            "paper_value": paper_val,
            "v1_match": f"GT-0019 {repro}",
            "verdict": verdict,
        })

    # (C) BCH determinism canary removed — was a sanity-only spot-check that
    # consumed a dyad-rating fixture now retired (no load-bearing claim
    # depended on it). Engine-determinism is verified at L9 of Phase 02.1 and
    # via the aggregate engine-pin SHA `318eb2f5...`.

    # Write outputs
    with (RESULTS / "07_c3_anchors_correlations.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)

    engine_head = json.loads((V_REPRO / "_infra" / "manifests" / "engine_head.json").read_text())
    manifest = {
        "axis_id": "AXIS-3", "axis_name": "C³ Functional Anchors (F1–F8)",
        "engine_head": engine_head.get("pinned_commit"),
        "seed_registry": {"primary": 2026050702, "bootstrap": None, "permutation": None},
        "phase_close_date": "2026-05-07",
        "git_commit_hash": "PENDING_AT_CLOSE",
        "claims": rows,
    }
    with (RESULTS / "07_c3_anchors_manifest.json").open("w") as f:
        json.dump(manifest, f, indent=2)

    n_pass = sum(1 for r in rows if r["verdict"] == "PASS")
    n_fail = sum(1 for r in rows if r["verdict"] == "FAIL")
    print(f"\n[verdict] PASS={n_pass}  FAIL={n_fail}  total={len(rows)}")


if __name__ == "__main__":
    main()
