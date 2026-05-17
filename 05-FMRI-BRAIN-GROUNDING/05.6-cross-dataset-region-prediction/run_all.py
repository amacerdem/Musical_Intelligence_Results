#!/usr/bin/env python3
"""Top-level orchestrator for 05.6-cross-dataset-region-prediction."""
from __future__ import annotations
import argparse, datetime as _dt, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LAYERS = [
    ("L1", "L1_engine_pin", "Engine SHA + paper-baseline structural"),
    ("L2", "L2_data_integrity", "V-Repro 25/26 inputs + cycle-17 encoder + MI cache"),
    ("L3", "L3_engine_cache", "Phase 05.6 outputs (CSV + JSON) exist"),
    ("L4", "L4_ceiling_check", "C1+C2 paradigm-invariance within tolerance"),
    ("L5", "L5_primary_test", "B directional trend + A paradigm-specific + 3-way separation"),
    ("L9", "L9_verdict_reconciliation", "Verdict + companion V-Repros untouched"),
]
QUICK = {"L1", "L4", "L5", "L9"}


def _has_tests(folder):
    return any(folder.glob("test_*.py"))


def _run(target):
    res = subprocess.run(["python3", "-m", "pytest", str(target), "--tb=line", "-q"],
                         cwd=str(ROOT), capture_output=True, text=True)
    return {"rc": res.returncode, "stdout": res.stdout, "stderr": res.stderr}


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
        st = "✅ PASS" if r["rc"] == 0 else "❌ FAIL"
        print(sm)
        if r["rc"] != 0 and r["stderr"]:
            print(r["stderr"][:800])
        rows.append(_row(tag, st, sm, descr))
        worst = max(worst, r["rc"])
        if tag == "L1" and r["rc"] != 0:
            _write_report(rows, started, worst, "L1 engine-pin gate"); return worst
    _write_report(rows, started, worst)
    return worst


def _write_report(rows, started, worst, aborted=None):
    finished = _dt.datetime.now().isoformat(timespec="seconds")
    headline = "✅ ALL PASS" if worst == 0 else "❌ FAIL"
    if aborted: headline = f"⛔ ABORTED at {aborted}"
    body = [
        "# 05.6-cross-dataset-region-prediction — Run Report",
        "", f"- **Started:**  {started}", f"- **Finished:** {finished}",
        f"- **Headline:** {headline}", "", "## Layer scorecard", "",
        "| Layer | Status | pytest summary | Coverage |",
        "|-------|--------|----------------|----------|", *rows, "",
        "## Paper-time baseline",
        "",
        "**Cross-dataset fMRI consistency (ds002725 N=17 ↔ ds003720 N=4):**",
        "- C1 MI mean|RAM| paradigm-invariance: **Pearson +0.998, Spearman +0.988**, p<0.001",
        "- C2 MI variance paradigm-invariance:  **Pearson +0.968, Spearman +0.952**, p<0.001",
        "- B  MI encoder cross-paradigm: Pearson +0.237 (directional trend, n.s.)",
        "- A  BOLD ceiling cross-paradigm: Pearson −0.161 (paradigm-specific, n.s.)",
        "",
        "**Three-way framing:** Engine paradigm-invariant + Encoder transfers directionally + Brain response paradigm-specific.",
        "",
    ]
    (ROOT / "REPORT.md").write_text("\n".join(body) + "\n")


if __name__ == "__main__":
    sys.exit(main())
