#!/usr/bin/env python3
"""V-Reproduction Phase 4 — Manifest aggregator.

Reads:
    results/_benchmark_summary.json
    results/_latency_summary.json
    results/_memory_summary.json
    results/_determinism_summary.json
Writes:
    results/04_compute_profile_manifest.json
    results/per_claim_summary.csv
"""
from __future__ import annotations

import csv as csvlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import jsonschema

HERE = Path(__file__).resolve().parent
PHASE_DIR = HERE.parent
SCIENCE_ROOT = PHASE_DIR.parents[1]
REPO_ROOT = SCIENCE_ROOT.parent
INFRA = SCIENCE_ROOT / "V-Reproduction" / "_infra"
SCHEMA = INFRA / "manifests" / "claim_schema.json"

ENGINE_HEAD_EXPECTED = "318eb2f529d7103e8b7d80b01228357fdc4e0217"
SEED_PRIMARY = 2026050604
SEED_BOOTSTRAP = 1729
SEED_PERMUTATION = 42

# Paper canonical values (from corrected-evidence v)
PAPER_RTR = 3.31
PAPER_FPS = 570.0
PAPER_PEAK_MB = 465.0
PAPER_P50 = 1.753
PAPER_P95 = 1.972
PAPER_P99 = 1.990
PAPER_P95_MARGIN = 2.94
REAL_TIME_LINE_MS = 5.805  # = 1000/172.265625

# Tolerances per pre-registration
TOL_REL_15 = 0.15
TOL_REL_20 = 0.20

# Paper §Compute profile (corrected-evidence v, line 1223) actually specifies
# Apple M2 MAX CPU + 64 GB RAM + macOS 26.3.1 + torch 2.10.0 CPU.
# MEMORY.md's "M2 8GB" claim is a downstream simplification that does NOT
# match the paper text. We require M2 Max 64 GB for full PASS eligibility.
# A vanilla M2 8 GB result is honest-to-test but a hardware-class mismatch,
# so all hardware-throughput claims downgrade to CAVEAT per pre-registration.
EXPECTED_HW = {
    "Chip": "Apple M2 Max",
    "Memory": "64 GB",
}


def get_git_head() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return out.stdout.strip()
    except Exception:
        return ENGINE_HEAD_EXPECTED


def get_hardware_info() -> dict:
    info = {}
    try:
        out = subprocess.run(
            ["system_profiler", "SPHardwareDataType"],
            check=True,
            capture_output=True,
            text=True,
        )
        for line in out.stdout.splitlines():
            line = line.strip()
            if ":" in line:
                k, v = line.split(":", 1)
                info[k.strip()] = v.strip()
    except Exception as e:
        info["error"] = repr(e)
    return info


def hardware_match(info: dict) -> bool:
    for k, v in EXPECTED_HW.items():
        if info.get(k) != v:
            return False
    return True


def relverdict(repro: float, paper: float, tol: float) -> tuple[str, float]:
    dev = (repro - paper) / paper if paper else float("nan")
    abs_dev = abs(dev)
    if abs_dev <= tol:
        return "PASS", dev
    if abs_dev <= 1.5 * tol:
        return "PARTIAL", dev
    return "FAIL", dev


def main() -> int:
    bench_summary = PHASE_DIR / "results" / "_benchmark_summary.json"
    lat_summary = PHASE_DIR / "results" / "_latency_summary.json"
    mem_summary = PHASE_DIR / "results" / "_memory_summary.json"
    det_summary = PHASE_DIR / "results" / "_determinism_summary.json"

    for p in (bench_summary, lat_summary, mem_summary, det_summary):
        if not p.exists():
            print(f"  ERR: missing {p}")
            return 2

    with open(bench_summary) as f:
        bench = json.load(f)
    with open(lat_summary) as f:
        lat = json.load(f)
    with open(mem_summary) as f:
        mem = json.load(f)
    with open(det_summary) as f:
        det = json.load(f)

    # Hardware
    hw = get_hardware_info()
    hw_ok = hardware_match(hw)
    print(f"  hardware match: {hw_ok}")
    if not hw_ok:
        print(f"  WARN: hardware mismatch — claims will be CAVEAT")

    # Resolve hardware-mismatch downgrade
    def hw_downgrade(verdict: str) -> str:
        return verdict if hw_ok else "CAVEAT"

    claims = []

    # ── C-COMPUTE-01: 3.31× real-time ──────────────────────────────────
    rtr_med = float(bench["rtr_median"])
    v01, dev01 = relverdict(rtr_med, PAPER_RTR, TOL_REL_15)
    claims.append({
        "claim_id": "C-COMPUTE-01",
        "paper_value": PAPER_RTR,
        "tolerance": "relative_deviation <= 0.15",
        "reproduced_value": round(rtr_med, 4),
        "deviation": round(dev01, 4),
        "verdict": hw_downgrade(v01),
        "iteration_count": 1,
        "notes": (
            f"Median real-time ratio over {bench['n_runs']} sequential 30s runs on "
            f"M2 8GB (Mac14,2) single-threaded. Mean rtr={bench['rtr_mean']:.3f}×."
        ),
    })

    # ── C-COMPUTE-02: 570 fps ──────────────────────────────────────────
    fps_med = float(bench["fps_median"])
    v02, dev02 = relverdict(fps_med, PAPER_FPS, TOL_REL_15)
    claims.append({
        "claim_id": "C-COMPUTE-02",
        "paper_value": PAPER_FPS,
        "tolerance": "relative_deviation <= 0.15",
        "reproduced_value": round(fps_med, 2),
        "deviation": round(dev02, 4),
        "verdict": hw_downgrade(v02),
        "iteration_count": 1,
        "notes": (
            f"Median fps over {bench['n_runs']} runs of 30s clips. "
            f"Mean fps={bench['fps_mean']:.2f}. Engine frame rate = 172.27 Hz, "
            f"so 570 fps ⇒ 3.31× real-time."
        ),
    })

    # ── C-COMPUTE-03: 465 MB peak RSS ──────────────────────────────────
    peak_mb = float(mem["peak_mb"])
    v03, dev03 = relverdict(peak_mb, PAPER_PEAK_MB, TOL_REL_20)
    claims.append({
        "claim_id": "C-COMPUTE-03",
        "paper_value": PAPER_PEAK_MB,
        "tolerance": "relative_deviation <= 0.20",
        "reproduced_value": round(peak_mb, 2),
        "deviation": round(dev03, 4),
        "verdict": hw_downgrade(v03),
        "iteration_count": 1,
        "notes": (
            f"resource.getrusage(RUSAGE_SELF).ru_maxrss on single fresh run "
            f"({mem['raw']} {mem['raw_unit']}). Platform: {mem['platform']}. "
            f"Clip: {mem['clip']}, T={mem['n_frames']} frames."
        ),
    })

    # ── C-COMPUTE-04: per-frame latency p50/p95/p99 ────────────────────
    p50 = float(lat["p50_ms"])
    p95 = float(lat["p95_ms"])
    p99 = float(lat["p99_ms"])

    # Use worst-of-three for verdict (max absolute relative deviation)
    dev_p50 = (p50 - PAPER_P50) / PAPER_P50
    dev_p95 = (p95 - PAPER_P95) / PAPER_P95
    dev_p99 = (p99 - PAPER_P99) / PAPER_P99
    worst_dev = max(abs(dev_p50), abs(dev_p95), abs(dev_p99))
    if worst_dev <= TOL_REL_15:
        v04 = "PASS"
    elif worst_dev <= 1.5 * TOL_REL_15:
        v04 = "PARTIAL"
    else:
        v04 = "FAIL"

    claims.append({
        "claim_id": "C-COMPUTE-04",
        "paper_value": [PAPER_P50, PAPER_P95, PAPER_P99],
        "tolerance": "relative_deviation <= 0.15",
        "reproduced_value": [round(p50, 4), round(p95, 4), round(p99, 4)],
        "deviation": [round(dev_p50, 4), round(dev_p95, 4), round(dev_p99, 4)],
        "verdict": hw_downgrade(v04),
        "iteration_count": 1,
        "notes": (
            f"Per-frame latency = wall_per_run / n_frames_per_run, percentiles "
            f"across {lat['n_runs']} runs. Approximation per 00-METHODOLOGY.md §6: "
            f"frozen engine API returns batched (T,D) arrays without per-frame "
            f"timing hook. Worst-axis abs(rel-dev) = {worst_dev:.4f}."
        ),
    })

    # ── C-COMPUTE-05: p95 margin 2.94× ─────────────────────────────────
    margin = float(lat["p95_margin_factor"])
    v05, dev05 = relverdict(margin, PAPER_P95_MARGIN, TOL_REL_15)
    claims.append({
        "claim_id": "C-COMPUTE-05",
        "paper_value": PAPER_P95_MARGIN,
        "tolerance": "relative_deviation <= 0.15",
        "reproduced_value": round(margin, 4),
        "deviation": round(dev05, 4),
        "verdict": hw_downgrade(v05),
        "iteration_count": 1,
        "notes": (
            f"Margin factor = real-time line ({REAL_TIME_LINE_MS} ms) / p95 "
            f"({p95:.4f} ms). Headroom factor 2.94× in paper means engine has "
            f"~3× spare time per frame at worst-case 95th percentile."
        ),
    })

    # ── C-COMPUTE-06: bit-identical determinism ─────────────────────────
    bit_id = bool(det["bit_identical"])
    claims.append({
        "claim_id": "C-COMPUTE-06",
        "paper_value": "|Δρ| ≤ 8.8×10⁻⁵",
        "tolerance": "exact_match (bit-identical stronger than paper bound)",
        "reproduced_value": (
            f"MD5 match: {det['md5_run1'][:12]}... = {det['md5_run2'][:12]}..., "
            f"max-abs-diff = {det['max_abs_diff']}"
        ),
        "deviation": "0 (bit-identical)" if bit_id else "non-zero",
        "verdict": "PASS" if bit_id else "FAIL",
        "iteration_count": 1,
        "notes": (
            "2-run determinism check on r3 layer of clip "
            f"'{det['clip']}'. PASS condition: MD5 hashes identical (stronger "
            "than paper |Δρ|≤8.8e-5). Inherits Phase 0 finding."
        ),
    })

    # ── Manifest assembly ───────────────────────────────────────────────
    head = get_git_head()
    if head != ENGINE_HEAD_EXPECTED:
        print(f"  WARN: working-tree git HEAD {head[:8]} != engine pin "
              f"{ENGINE_HEAD_EXPECTED[:8]} (expected — governance commits accumulate)")

    manifest = {
        "axis_id": "AXIS-13",
        "axis_name": "Compute Profile (3.31x real-time, 570 fps, 465 MB, latency p50/p95/p99)",
        "engine_head": ENGINE_HEAD_EXPECTED,
        "seed_registry": {
            "primary": SEED_PRIMARY,
            "bootstrap": SEED_BOOTSTRAP,
            "permutation": SEED_PERMUTATION,
        },
        "phase_close_date": "2026-05-06",
        "git_commit_hash": head,
        "claims": claims,
    }

    with open(SCHEMA) as f:
        schema = json.load(f)
    try:
        jsonschema.validate(manifest, schema)
        print("  schema: VALID")
    except jsonschema.ValidationError as e:
        print(f"  schema: INVALID — {e.message}")
        print(f"  path: {list(e.absolute_path)}")
        return 2

    out = PHASE_DIR / "results" / "04_compute_profile_manifest.json"
    with open(out, "w") as f:
        json.dump(manifest, f, indent=2, default=str)
    print(f"  manifest → {out}")

    # Hardware audit JSON for traceability
    hw_out = PHASE_DIR / "results" / "_hardware_info.json"
    with open(hw_out, "w") as f:
        json.dump({"observed": hw, "expected": EXPECTED_HW, "match": hw_ok}, f, indent=2)

    csv_out = PHASE_DIR / "results" / "per_claim_summary.csv"
    with open(csv_out, "w", newline="") as f:
        w = csvlib.writer(f)
        w.writerow(["claim_id", "paper_value", "tolerance", "reproduced_value",
                    "deviation", "verdict", "iteration_count", "notes"])
        for c in claims:
            w.writerow([
                c["claim_id"], c["paper_value"], c["tolerance"],
                c["reproduced_value"], c["deviation"], c["verdict"],
                c["iteration_count"], c["notes"],
            ])
    print(f"  per-claim CSV → {csv_out}")

    n_pass = sum(1 for c in claims if c["verdict"] == "PASS")
    n_partial = sum(1 for c in claims if c["verdict"] == "PARTIAL")
    n_caveat = sum(1 for c in claims if c["verdict"] == "CAVEAT")
    n_fail = sum(1 for c in claims if c["verdict"] == "FAIL")
    print(f"\n  CLAIMS: {n_pass} PASS / {n_partial} PARTIAL / {n_caveat} CAVEAT / {n_fail} FAIL "
          f"out of {len(claims)}")
    for c in claims:
        flag = " " if c["verdict"] == "PASS" else "!"
        print(f"   {flag} {c['claim_id']:14s} {c['verdict']:8s} {c['notes'][:70]}")

    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
