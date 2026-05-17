#!/usr/bin/env python3
"""Top-level orchestrator for the T³ Isolated Validation suite.

Runs every layer's pytest collection and writes a single ``REPORT.md``
with the aggregated PASS/FAIL/EMPTY scorecard at the top of the suite.

Usage
-----
    python3 run_all.py                  # run every layer, write REPORT.md
    python3 run_all.py L1                # run only L1
    python3 run_all.py L1 L3 L4          # run a subset
    python3 run_all.py --quick           # pin-integrity + L1 only

Exit code is the worst pytest exit code observed (0 = all PASS).

Status of the T³ suite at copy time (V-Reproduction 20-t3-isolated-validation):
runtime-tested layers are Pin + L1 + L3 + L4 + L5 + L6 + L13. Layers L2, L7–L12
ship pre-computed audit artefacts (JSON + summary MD) but carry no pytest-side
runtime tests yet; they appear in the scorecard as ⚪ EMPTY. The source suite
at ``The Paper/T3-Paper/T3_Isolated_Validation/`` is the canonical home for
populating the remaining layers.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Layers in canonical execution order. Empty layers (no test_*.py yet) are
# listed for completeness — they surface as ⚪ EMPTY in the scorecard rather
# than silently disappearing.
LAYERS = [
    ("L1",  "L1_spec_compliance",       "Per-tuple (r,h,m,ℓ) formula re-implementation, bit-identical to engine"),
    ("L2",  "L2_statelessness",         "Statelessness: no self._ema / hidden state across frames"),
    ("L3",  "L3_determinism",           "Bit-identicality across run/seed/thread axes"),
    ("L4",  "L4_output_guarantees",     "Range, shape, no-NaN, dataclass guarantees on H3Output"),
    ("L5",  "L5_robustness",            "Pathological-input robustness (silence, single-frame, post-warm-up)"),
    ("L6",  "L6_operator_correctness",  "24 morphs × 3 laws correctness via analytical anchors"),
    ("L7",  "L7_pipeline_dag",          "Demand-driven sparsity & embarrassingly parallel staging"),
    ("L8",  "L8_horizon_scale",         "32 horizons log-coverage, 4 perceptual bands"),
    ("L9",  "L9_constants",             "Constant provenance audit (zero-calibration)"),
    ("L10", "L10_cross_impl",           "Cross-implementation cross-validation"),
    ("L11", "L11_anti_features",        "Anti-feature / hidden-state probes"),
    ("L12", "L12_api",                  "API contract; H3Output frozen, H3DemandSpec slot-restricted"),
    ("L13", "L13_performance",          "T³-stage real-time-factor & memory budget"),
    # L14 (Documentation ↔ code consistency) lives only in the source suite at
    # The Paper/T3-Paper/T3_Isolated_Validation/. The V-Reproduction copy is
    # decoupled from the paper tree (no .tex dependency), so the doc-consistency
    # layer is intentionally omitted here.
]


def _has_tests(folder: Path) -> bool:
    return any(folder.glob("test_*.py"))


def _run_pytest(target: Path) -> dict:
    """Run pytest on *target* and capture stdout/stderr + returncode."""
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
    """Return the last non-empty line of pytest stdout (its summary)."""
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
                        help="run pin-integrity + L1 only")
    args = parser.parse_args()

    selected = list(LAYERS)
    if args.quick:
        selected = [layer for layer in LAYERS if layer[0] == "L1"]
    elif args.layers:
        wanted = set(args.layers)
        selected = [layer for layer in LAYERS if layer[0] in wanted]

    started = _dt.datetime.now().isoformat(timespec="seconds")
    rows = []
    worst_rc = 0

    # Pin-integrity gate first, always.
    print("=" * 70)
    print("Pin-integrity gate")
    print("=" * 70)
    pin_res = _run_pytest(ROOT / "_infra" / "test_pin_integrity.py")
    pin_summary = _summarise(pin_res["stdout"])
    pin_status = "✅ PASS" if pin_res["returncode"] == 0 else "❌ FAIL"
    print(pin_summary)
    rows.append(_format_layer_row("Pin", pin_status, pin_summary, "Engine SHA + H³ registry integrity"))
    worst_rc = max(worst_rc, pin_res["returncode"])

    if pin_res["returncode"] != 0:
        print("\nPin integrity failed — refusing to run further layers.")
        _write_report(rows, started, worst_rc, aborted="pin-integrity gate")
        return worst_rc

    for tag, folder, descr in selected:
        path = ROOT / folder
        if not path.exists():
            rows.append(_format_layer_row(tag, "❌ MISSING", "(folder absent)", descr))
            worst_rc = max(worst_rc, 1)
            continue
        if not _has_tests(path):
            rows.append(_format_layer_row(tag, "⚪ EMPTY", "(no test files — audit artefacts only)", descr))
            continue
        print()
        print("=" * 70)
        print(f"{tag}: {descr}")
        print("=" * 70)
        res = _run_pytest(path)
        summary = _summarise(res["stdout"])
        status = "✅ PASS" if res["returncode"] == 0 else "❌ FAIL"
        print(summary)
        rows.append(_format_layer_row(tag, status, summary, descr))
        worst_rc = max(worst_rc, res["returncode"])

    _write_report(rows, started, worst_rc)
    return worst_rc


def _write_report(rows: list[str], started: str, worst_rc: int, aborted: str | None = None) -> None:
    finished = _dt.datetime.now().isoformat(timespec="seconds")
    headline = "✅ ALL PASS" if worst_rc == 0 else "❌ FAIL"
    if aborted:
        headline = f"⛔ ABORTED at {aborted}"
    body = [
        "# T³ Isolated Validation — Run Report",
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
        "## Engine pin",
        "",
        "Pin manifest: [`_infra/manifests/engine_pin.json`](_infra/manifests/engine_pin.json)",
        "",
    ]
    (ROOT / "REPORT.md").write_text("\n".join(body) + "\n")


if __name__ == "__main__":
    sys.exit(main())
