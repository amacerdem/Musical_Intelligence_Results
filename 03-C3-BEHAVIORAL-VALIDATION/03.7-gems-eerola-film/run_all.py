#!/usr/bin/env python3
"""Top-level orchestrator for 24-h18-h25-eerola-film-gems.

Runs every layer's pytest collection and writes ``REPORT.md``.

Usage
-----
    python3 run_all.py
    python3 run_all.py L1 L5
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
    ("L1", "L1_engine_pin",               "Engine SHA aggregate integrity + paper-baseline structural checks"),
    ("L2", "L2_data_integrity",           "Eerola Set 2 + Set 1 ratings CSVs + engine .npz files present"),
    ("L3", "L3_engine_cache",             "Engine cache integrity (NEMAC + DAP + CDMR + AAC + SRP + TAR + PNH + VMM)"),
    ("L4", "L4_label_correlation",        "Rating distributions + paper-time channel route validation"),
    ("L5", "L5_primary_test",             "PRIMARY — Set 2 (n=110) 8 GEMS labels cross-clip Spearman + Bonferroni"),
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
        "# 24-h18-h25-eerola-film-gems — Run Report",
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
        "**Set 2 (n=110):** 8/8 GEMS labels Bonferroni-pass, 7/8 R³-residual survive.",
        "**Set 1 (n=360):** 4/8 identical-channel replication (fear/sad/tender + tension cluster).",
        "",
        "**Mechanistic specificity:**",
        "- sad ↔ NEMAC mPFC activation (+0.741, Janata 2009 default-mode anchor)",
        "- tender ↔ DAP familiarity_warmth (+0.722, affiliative-intimacy)",
        "- tension ↔ CDMR mismatch_amplitude (−0.683, expectancy-violation)",
        "- energy ↔ AAC heart-rate (+0.672, cross-paradigm TenseMusic AAC cluster)",
        "- valence ↔ SRP liking (+0.424, Berridge wanting-vs-liking)",
        "",
        "**Critical caveat:** No per-rater data publicly deposited; LOSO ceiling NOT computable.",
        "Bonferroni + R³-residual ablation are the load-bearing metrics.",
        "",
    ]
    (ROOT / "REPORT.md").write_text("\n".join(body) + "\n")


if __name__ == "__main__":
    sys.exit(main())
