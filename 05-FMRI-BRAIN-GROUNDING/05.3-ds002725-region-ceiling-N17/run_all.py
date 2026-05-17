#!/usr/bin/env python3
"""Top-level orchestrator for 05.3-ds002725-region-ceiling-N17.

Runs each layer's pytest collection and writes REPORT.md.

Usage:
    python3 run_all.py
    python3 run_all.py L1 L4 L5
    python3 run_all.py --quick   # L1 + L4 + L5 + L6 + L9 only
"""
from __future__ import annotations

import argparse
import datetime as _dt
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

LAYERS = [
    ("L1", "L1_engine_pin", "Engine SHA aggregate integrity + paper-baseline structural checks"),
    ("L2", "L2_data_integrity", "ds002725 BOLD cache (N=17) + MI engine cache (Mendelssohn) present"),
    ("L3", "L3_engine_cache", "Mendelssohn MI engine cache (RAM 26 regions) integrity"),
    ("L4", "L4_ceiling_check", "Stage 3 full-scan LOSO ceiling reproduction (15/21 PASS locked)"),
    ("L5", "L5_primary_test", "Stage 4 Mendelssohn-window encoder + saturation verdict (16/21 saturating)"),
    ("L6", "L6_cross_paradigm_bridge", "Stage 9 cross-paradigm bridge ds002725 ↔ ds003720 (1 STRONG + 5 MIXED)"),
    ("L9", "L9_verdict_reconciliation", "All four paper-headline numbers locked"),
]

QUICK_LAYERS = {"L1", "L4", "L5", "L6", "L9"}


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
        print(f"\n{'=' * 70}\n{tag}: {descr}\n{'=' * 70}")
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
        "# 05.3-ds002725-region-ceiling-N17 — Run Report",
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
        "## Paper-time baseline (positive evidence only)",
        "",
        "**Four NEW positive evidence axes** added to V-Reproduction:",
        "1. Stage 3 ds002725 N=17 LOSO per-region ceiling: 15/21 stimulus-driven, top putamen +0.442, amygdala +0.383, MGB +0.346",
        "2. Stage 4 Mendelssohn-window MI encoder: **16/21 ceiling-saturating** (11 AT_CEILING + 5 EXCEEDS), max A1_HG +0.509",
        "3. Mendelssohn pilot paradox resolved: BOLD reliability (full-scan +0.383) vs encoder fidelity (Mendelssohn-window +0.012) separable",
        "4. Cross-paradigm bridge ds002725 ↔ ds003720: 1 STRONG (STG) + 5 MIXED (IFG/OFC/MGB/hypothalamus/insula)",
        "",
        "See `_infra/manifests/paper_time_baseline.json` for full locked numbers.",
        "",
    ]
    (ROOT / "REPORT.md").write_text("\n".join(body) + "\n")


if __name__ == "__main__":
    sys.exit(main())
