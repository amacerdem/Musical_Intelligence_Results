#!/usr/bin/env python3
"""Top-level orchestrator for 22-h8-tensemusic-tension-prediction.

Runs every layer's pytest collection and writes ``REPORT.md``.

Usage
-----
    python3 run_all.py
    python3 run_all.py L1 L4 L5
    python3 run_all.py --quick     # pin + L1 + L4 + L5 only
"""
from __future__ import annotations

import argparse
import datetime as _dt
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

LAYERS = [
    ("L1", "L1_engine_pin",               "Engine SHA aggregate integrity"),
    ("L2", "L2_data_integrity",           "TenseMusic CSVs + engine .npz files present"),
    ("L3", "L3_engine_cache",             "Engine cache per-frame integrity (38 pieces)"),
    ("L4", "L4_ceiling_check",            "LOSO inter-rater ceiling +0.386 [0.36, 0.41] reproduction"),
    ("L5", "L5_primary_test",             "PRIMARY — TENSION-15 lag-aware Spearman + Bonferroni"),
    ("L9", "L9_verdict_reconciliation",   "Local vs paper-time baseline tolerance check"),
]

QUICK_LAYERS = {"L1", "L4", "L5"}


def _has_tests(folder: Path) -> bool:
    return any(folder.glob("test_*.py"))


def _run_pytest(target: Path) -> dict:
    result = subprocess.run(
        ["python3", "-m", "pytest", str(target), "--tb=line", "-q"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def _summarise(stdout: str) -> str:
    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if line:
            return line
    return "(no output)"


def _row(tag: str, status: str, summary: str, descr: str) -> str:
    return f"| **{tag}** | {status} | {summary} | {descr} |"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("layers", nargs="*")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    selected = list(LAYERS)
    if args.quick:
        selected = [l for l in LAYERS if l[0] in QUICK_LAYERS]
    elif args.layers:
        wanted = set(args.layers)
        selected = [l for l in LAYERS if l[0] in wanted]

    started = _dt.datetime.now().isoformat(timespec="seconds")
    rows = []
    worst_rc = 0

    for tag, folder, descr in selected:
        path = ROOT / folder
        if not _has_tests(path):
            rows.append(_row(tag, "⚪ EMPTY", "(no tests)", descr))
            continue
        print(f"\n{'='*70}\n{tag}: {descr}\n{'='*70}")
        res = _run_pytest(path)
        summary = _summarise(res["stdout"])
        status = "✅ PASS" if res["returncode"] == 0 else "❌ FAIL"
        print(summary)
        if res["returncode"] != 0 and res["stderr"]:
            print("STDERR (first 800 chars):")
            print(res["stderr"][:800])
        rows.append(_row(tag, status, summary, descr))
        worst_rc = max(worst_rc, res["returncode"])

        if tag == "L1" and res["returncode"] != 0:
            print("\nL1 engine-pin failed — refusing further layers.")
            _write_report(rows, started, worst_rc, aborted="L1 engine-pin gate")
            return worst_rc

    _write_report(rows, started, worst_rc)
    return worst_rc


def _write_report(rows, started, worst_rc, aborted=None):
    finished = _dt.datetime.now().isoformat(timespec="seconds")
    headline = "✅ ALL PASS" if worst_rc == 0 else "❌ FAIL"
    if aborted:
        headline = f"⛔ ABORTED at {aborted}"

    body = [
        "# 22-h8-tensemusic-tension-prediction — Run Report",
        "",
        f"- **Started:**  {started}",
        f"- **Finished:** {finished}",
        f"- **Headline:** {headline}",
        "",
        "## Layer scorecard",
        "",
        "| Layer | Status | pytest summary | Coverage |",
        "|-------|--------|----------------|----------|",
        *rows,
        "",
        "## Paper-time baseline",
        "",
        "See `_infra/manifests/paper_time_baseline.json` for locked numbers.",
        "Top: `MECH_AAC__F1:hr_pred_2s` ρ=+0.421, dir=89.5 %, 15/15 Bonferroni, 109 % of ceiling.",
        "",
    ]
    (ROOT / "REPORT.md").write_text("\n".join(body) + "\n")


if __name__ == "__main__":
    sys.exit(main())
