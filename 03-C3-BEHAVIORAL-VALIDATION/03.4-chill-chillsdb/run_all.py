#!/usr/bin/env python3
"""Top-level orchestrator for 21-c3-chill-prediction.

Runs every layer's pytest collection and writes ``REPORT.md`` with the
aggregated PASS/FAIL/CAVEAT scorecard at the top of the suite, plus the
headline TC005 verdict (MMP P2:familiarity Bonferroni-pass).

Usage
-----
    python3 run_all.py                  # run every layer
    python3 run_all.py L1 L2 L4         # run a subset
    python3 run_all.py --quick          # pin + L1 + L2 + L4 only
"""
from __future__ import annotations

import argparse
import datetime as _dt
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

LAYERS = [
    ("L1", "L1_engine_pin",                    "Engine SHA + dim-registry integrity"),
    ("L2", "L2_audio_integrity",               "ChillsDB v1 audio file presence + format"),
    ("L3", "L3_engine_cache",                  "Engine cache build / verify (3 audio variants)"),
    ("L4", "L4_tc005_primary_verdict",         "PRIMARY — TC005 7-clean Bonferroni-pass (MMP P2)"),
    ("L5", "L5_tc003_sensitivity",             "9-full sensitivity (Mr. Bean + Vocal Intros included)"),
    ("L6", "L6_tc004_biphasic_composite",      "Biphasic composite (Salimpoor pattern)"),
    ("L7", "L7_tc006_noisereduce_crossval",    "noisereduce cross-validation (denoise-method-robust)"),
    ("L8", "L8_tc007_pre_post",                "Pre/post event-window asymmetry"),
    ("L9", "L9_verdict_reconciliation",        "Local vs paper-time baseline reconciliation"),
]

QUICK_LAYERS = {"L1", "L2", "L4"}


def _has_tests(folder: Path) -> bool:
    return any(folder.glob("test_*.py"))


def _run_pytest(target: Path) -> dict:
    """Run pytest on *target* and return result dict."""
    result = subprocess.run(
        ["python3", "-m", "pytest", str(target), "--tb=line", "-q"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def _summarise(stdout: str) -> str:
    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if line:
            return line
    return "(no output)"


def _format_layer_row(tag: str, status: str, summary: str, descr: str) -> str:
    return f"| **{tag}** | {status} | {summary} | {descr} |"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("layers", nargs="*", help="Layer tags (L1, L2, …) to run; default = all")
    parser.add_argument("--quick", action="store_true",
                        help="run pin-integrity + L1 + L2 + L4 only (primary verdict path)")
    args = parser.parse_args()

    selected = list(LAYERS)
    if args.quick:
        selected = [layer for layer in LAYERS if layer[0] in QUICK_LAYERS]
    elif args.layers:
        wanted = set(args.layers)
        selected = [layer for layer in LAYERS if layer[0] in wanted]

    started = _dt.datetime.now().isoformat(timespec="seconds")
    rows = []
    worst_rc = 0

    for tag, folder, descr in selected:
        path = ROOT / folder
        if not _has_tests(path):
            rows.append(_format_layer_row(tag, "⚪ EMPTY", "(no test files yet)", descr))
            continue
        print()
        print("=" * 70)
        print(f"{tag}: {descr}")
        print("=" * 70)
        res = _run_pytest(path)
        summary = _summarise(res["stdout"])
        status = "✅ PASS" if res["returncode"] == 0 else "❌ FAIL"
        print(summary)
        if res["returncode"] != 0 and res["stderr"]:
            print("STDERR (first 800 chars):")
            print(res["stderr"][:800])
        rows.append(_format_layer_row(tag, status, summary, descr))
        worst_rc = max(worst_rc, res["returncode"])

        # If L1 fails (engine pin drift), refuse to continue
        if tag == "L1" and res["returncode"] != 0:
            print("\nL1 engine-pin failed — refusing to run further layers (results would be misleading).")
            _write_report(rows, started, worst_rc, aborted="L1 engine-pin gate")
            return worst_rc

    _write_report(rows, started, worst_rc)
    return worst_rc


def _write_report(rows: list[str], started: str, worst_rc: int, aborted: str | None = None) -> None:
    finished = _dt.datetime.now().isoformat(timespec="seconds")
    headline = "✅ ALL PASS" if worst_rc == 0 else "❌ FAIL"
    if aborted:
        headline = f"⛔ ABORTED at {aborted}"

    # Try to pull headline TC005 verdict from L4 results CSV if present
    primary_verdict_block = []
    l4_csv = ROOT / "L4_tc005_primary_verdict" / "results" / "tc005_single_channel_aggregate.csv"
    if l4_csv.exists():
        try:
            import pandas as pd
            df = pd.read_csv(l4_csv)
            df_afftdn = df[df["audio"] == "afftdn"].sort_values("mean_rank_biserial", ascending=False)
            primary_verdict_block = [
                "## Headline TC005 verdict (afftdn 7-clean)",
                "",
                "| Channel | mean_rb | bonf_p | n_clips_pos | status |",
                "|---|---|---|---|---|",
            ]
            for _, row in df_afftdn.head(5).iterrows():
                status_str = "★ Bonferroni" if row["bonf_p"] < 0.05 else "• BH-FDR" if row["bh_q"] < 0.05 else ""
                primary_verdict_block.append(
                    f"| {row['channel']} | {row['mean_rank_biserial']:+.4f} | {row['bonf_p']:.4f} | {int(row['n_clips_pos'])}/7 | {status_str} |"
                )
            primary_verdict_block.append("")
        except Exception as e:
            primary_verdict_block = [f"## Headline TC005 verdict\n\n(failed to parse L4 results: {e})\n"]

    body = [
        "# 21-c3-chill-prediction — Run Report",
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
        *primary_verdict_block,
        "## Engine pin",
        "",
        "Pin manifest: [`_infra/manifests/engine_pin.json`](_infra/manifests/engine_pin.json)",
        "",
        "Paper-time baseline: [`_infra/manifests/paper_time_baseline.json`](_infra/manifests/paper_time_baseline.json)",
        "",
    ]
    (ROOT / "REPORT.md").write_text("\n".join(body) + "\n")


if __name__ == "__main__":
    sys.exit(main())
