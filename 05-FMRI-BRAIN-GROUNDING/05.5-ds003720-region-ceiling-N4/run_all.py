#!/usr/bin/env python3
"""Top-level orchestrator for 05.5-ds003720-region-ceiling-N4."""
from __future__ import annotations
import argparse, datetime as _dt, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAYERS = [
    ("L1", "L1_engine_pin", "Engine SHA + paper-baseline structural checks"),
    ("L2", "L2_data_integrity", "Cycle-17 ckpt_bold + encoder r CSV present"),
    ("L3", "L3_engine_cache", "Phase 05.5 output CSVs + manifest exist"),
    ("L4", "L4_ceiling_check", "Per-region ceiling matches paper baseline"),
    ("L5", "L5_primary_test", "Saturation verdict distribution within tolerance"),
    ("L9", "L9_verdict_reconciliation", "Verdict reconciliation + V-Repro 12 untouched"),
]
QUICK = {"L1", "L4", "L5", "L9"}


def _has_tests(folder):
    return any(folder.glob("test_*.py"))


def _run(target):
    res = subprocess.run(["python3", "-m", "pytest", str(target), "--tb=line", "-q"],
                         cwd=str(ROOT), capture_output=True, text=True)
    return {"returncode": res.returncode, "stdout": res.stdout, "stderr": res.stderr}


def _summarise(s):
    for ln in reversed(s.strip().splitlines()):
        ln = ln.strip()
        if ln: return ln
    return "(no output)"


def _row(tag, st, sm, d):
    return f"| **{tag}** | {st} | {sm} | {d} |"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("layers", nargs="*")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    selected = list(LAYERS)
    if args.quick:
        selected = [l for l in LAYERS if l[0] in QUICK]
    elif args.layers:
        wanted = set(args.layers)
        selected = [l for l in LAYERS if l[0] in wanted]

    started = _dt.datetime.now().isoformat(timespec="seconds")
    rows, worst = [], 0
    for tag, folder, descr in selected:
        path = ROOT / folder
        if not _has_tests(path):
            rows.append(_row(tag, "⚪ EMPTY", "(no tests)", descr)); continue
        print(f"\n{'='*70}\n{tag}: {descr}\n{'='*70}")
        r = _run(path)
        sm = _summarise(r["stdout"])
        st = "✅ PASS" if r["returncode"] == 0 else "❌ FAIL"
        print(sm)
        if r["returncode"] != 0 and r["stderr"]:
            print(r["stderr"][:800])
        rows.append(_row(tag, st, sm, descr))
        worst = max(worst, r["returncode"])
        if tag == "L1" and r["returncode"] != 0:
            _write_report(rows, started, worst, "L1 engine-pin gate"); return worst
    _write_report(rows, started, worst)
    return worst


def _write_report(rows, started, worst, aborted=None):
    finished = _dt.datetime.now().isoformat(timespec="seconds")
    headline = "✅ ALL PASS" if worst == 0 else "❌ FAIL"
    if aborted: headline = f"⛔ ABORTED at {aborted}"
    body = [
        "# 05.5-ds003720-region-ceiling-N4 — Run Report",
        "", f"- **Started:**  {started}", f"- **Finished:** {finished}",
        f"- **Headline:** {headline}", "", "## Layer scorecard", "",
        "| Layer | Status | pytest summary | Coverage |",
        "|-------|--------|----------------|----------|", *rows, "",
        "## Paper-time baseline", "",
        "Companion to V-Repro 12 (paper-canonical voxelwise). This package adds per-region",
        "cross-subject LOSO ceiling on ds003720 N=4 at cycle-17 26-region BOLD scale.",
        "",
        "**Top regions:** hippocampus +0.354, dlPFC +0.319, AG +0.243, IFG +0.233, PMC +0.193.",
        "**N pass floor+q05 (non-brainstem):** 16/21.",
        "**MI encoder saturation:** 5/21 (scale mismatch: cycle-17 per-clip vs ceiling per-TR).",
        "",
    ]
    (ROOT / "REPORT.md").write_text("\n".join(body) + "\n")


if __name__ == "__main__":
    sys.exit(main())
