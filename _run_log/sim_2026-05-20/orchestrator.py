#!/usr/bin/env python3
"""Tam simülasyon orchestrator — read-only engine_outputs, analysis-only reproduction.

Her phase için:
  1. results/ baseline hash snapshot
  2. results/ → results.before_sim/ (taşı)
  3. mkdir results/
  4. Runner çalıştır
  5. Yeni results/ hash
  6. Diff vs baseline: per-file MATCH/DIFFER/NEW/MISSING
  7. MISSING dosyaları results.before_sim/'den restore et
  8. results.before_sim/ sil

Çıktılar:
  _run_log/sim_2026-05-20/phase_<id>_diff.json
  _run_log/sim_2026-05-20/orchestrator_summary.json
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = Path(__file__).resolve().parent
VENV_PY = REPO_ROOT / ".venv" / "bin" / "python"

# Phase tanımları: (id, path, runner_kind, runner_args)
#   runner_kind: "python", "shell", "pytest_runall", "ai_ablation_loop"
PHASES = [
    # 00 Engine Integrity (3)
    ("00.1", "00-ENGINE-INTEGRITY-FOUNDATIONS/00.1-architectural-cardinalities", "python", ["code/run_phase1.py"]),
    ("00.2", "00-ENGINE-INTEGRITY-FOUNDATIONS/00.2-fmri-eligibility-audit", "python", ["code/run_phase00_2.py"]),
    ("00.3", "00-ENGINE-INTEGRITY-FOUNDATIONS/00.3-compute-profile", "python", ["code/run_phase00_3.py"]),
    # 01 R³ (3)
    ("01.1", "01-R3-PERCEPTUAL-FRONT-END/01.1-r3-isolated-extended", "pytest_runall", ["run_all.py"]),
    ("01.2", "01-R3-PERCEPTUAL-FRONT-END/01.2-r3-oos-consonance", "python", ["code/run_phase6.py"]),
    ("01.3", "01-R3-PERCEPTUAL-FRONT-END/01.3-cross-cultural-anchor", "python", ["code/run_phase14.py"]),
    # 02 T³ (1)
    ("02.1", "02-T3-TEMPORAL-LAYER/02.1-t3-isolated-extended", "pytest_runall", ["run_all.py"]),
    # 03 C³ Behavioral (7)
    ("03.1", "03-C3-BEHAVIORAL-VALIDATION/03.1-c3-functional-anchors-F1-F8", "python", ["code/run_phase7.py"]),
    ("03.2", "03-C3-BEHAVIORAL-VALIDATION/03.2-ece-belief-calibration", "shell", ["code/run.sh"]),
    ("03.3", "03-C3-BEHAVIORAL-VALIDATION/03.3-cheung-emergent-reward", "python", ["code/run_phase10.py"]),
    ("03.4", "03-C3-BEHAVIORAL-VALIDATION/03.4-chill-chillsdb", "pytest_runall", ["run_all.py"]),
    ("03.5", "03-C3-BEHAVIORAL-VALIDATION/03.5-tension-tensemusic", "pytest_runall", ["run_all.py"]),
    ("03.6", "03-C3-BEHAVIORAL-VALIDATION/03.6-emotion-pmemo-dynamic", "pytest_runall", ["run_all.py"]),
    ("03.7", "03-C3-BEHAVIORAL-VALIDATION/03.7-gems-eerola-film", "pytest_runall", ["run_all.py"]),
    # 04 C³ Biological (2)
    ("04.1", "04-C3-BIOLOGICAL-SUBSTRATE/04.1-neurochemistry-pharma", "python", ["code/run_phase04_1.py"]),
    ("04.2", "04-C3-BIOLOGICAL-SUBSTRATE/04.2-ram-topology", "python", ["code/run_phase04_2.py"]),
    # 05 fMRI (6, 05.7 deferred)
    ("05.1", "05-FMRI-BRAIN-GROUNDING/05.1-mendelssohn-pilot", "python", ["code/run_phase05_1.py"]),
    ("05.2", "05-FMRI-BRAIN-GROUNDING/05.2-mech-region-ds002725", "python", ["code/run_phase05_2.py"]),
    ("05.3", "05-FMRI-BRAIN-GROUNDING/05.3-ds002725-region-ceiling-N17", "pytest_runall", ["run_all.py"]),
    ("05.4", "05-FMRI-BRAIN-GROUNDING/05.4-voxelwise-ds003720", "python", ["code/run_phase05_4.py"]),
    ("05.5", "05-FMRI-BRAIN-GROUNDING/05.5-ds003720-region-ceiling-N4", "pytest_runall", ["run_all.py"]),
    ("05.6", "05-FMRI-BRAIN-GROUNDING/05.6-cross-dataset-region-prediction", "pytest_runall", ["run_all.py"]),
    # 06 Portfolio (2, 06.2 deferred)
    ("06.1", "06-PORTFOLIO-FALSIFIABILITY/06.1-falsifiable-table5", "python", ["code/run_phase06_1.py"]),
    ("06.3", "06-PORTFOLIO-FALSIFIABILITY/06.3-ai-baseline-ablation", "ai_ablation_loop",
        ["code/baseline_marjieh.py", "code/baseline_carillon.py", "code/baseline_cheung.py", "code/baseline_tensemusic.py"]),
]


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_results_tree(results_dir: Path) -> dict[str, str]:
    """SHA-256 of every file under results_dir, keyed by relative path."""
    out = {}
    if not results_dir.exists():
        return out
    for p in sorted(results_dir.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(results_dir))
            out[rel] = file_sha256(p)
    return out


def run_phase(phase_id: str, phase_path: str, kind: str, args: list[str]) -> dict:
    """Run one phase. Returns diff dict."""
    phase_dir = REPO_ROOT / phase_path
    results_dir = phase_dir / "results"
    backup_dir = phase_dir / "results.before_sim"

    record = {
        "phase_id": phase_id,
        "phase_path": phase_path,
        "kind": kind,
        "args": args,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results_existed_before": results_dir.exists(),
    }

    # 1. Baseline hash
    baseline_hashes = hash_results_tree(results_dir)
    record["baseline_file_count"] = len(baseline_hashes)

    # 2. Backup results/ → results.before_sim/ (copy, don't move — some runners read from results/ as upstream input)
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    if results_dir.exists():
        shutil.copytree(str(results_dir), str(backup_dir))
    else:
        results_dir.mkdir(parents=True, exist_ok=True)

    # 3. Run runner
    t0 = time.time()
    if kind == "python":
        cmd = [str(VENV_PY), args[0]]
        proc = subprocess.run(cmd, cwd=phase_dir, capture_output=True, text=True, timeout=14400)
        record["returncode"] = proc.returncode
        record["stdout_tail"] = proc.stdout[-2000:] if proc.stdout else ""
        record["stderr_tail"] = proc.stderr[-2000:] if proc.stderr else ""
    elif kind == "shell":
        import os
        cmd = ["bash", args[0]]
        # Provide venv on PATH + _infra on PYTHONPATH so `import _engine_path` works
        env = {**os.environ,
               "PATH": f"{VENV_PY.parent}:{os.environ.get('PATH', '')}",
               "PYTHONPATH": f"{REPO_ROOT / '_infra'}:{os.environ.get('PYTHONPATH', '')}"}
        proc = subprocess.run(cmd, cwd=phase_dir, capture_output=True, text=True, timeout=14400, env=env)
        record["returncode"] = proc.returncode
        record["stdout_tail"] = proc.stdout[-2000:] if proc.stdout else ""
        record["stderr_tail"] = proc.stderr[-2000:] if proc.stderr else ""
    elif kind == "pytest_runall":
        # Run full pytest from REPO_ROOT (cwd=phase_dir breaks _infra import).
        cmd = [str(VENV_PY), "-m", "pytest", str(phase_dir), "--tb=line", "-q"]
        proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, timeout=14400)
        record["returncode"] = proc.returncode
        record["stdout_tail"] = proc.stdout[-2000:] if proc.stdout else ""
        record["stderr_tail"] = proc.stderr[-2000:] if proc.stderr else ""
    elif kind == "ai_ablation_loop":
        record["sub_runs"] = []
        for script in args:
            cmd = [str(VENV_PY), script]
            proc = subprocess.run(cmd, cwd=phase_dir, capture_output=True, text=True, timeout=14400)
            record["sub_runs"].append({
                "script": script,
                "returncode": proc.returncode,
                "stdout_tail": proc.stdout[-1000:] if proc.stdout else "",
                "stderr_tail": proc.stderr[-1000:] if proc.stderr else "",
            })
        record["returncode"] = max((s["returncode"] for s in record["sub_runs"]), default=0)
    else:
        record["returncode"] = -1
        record["error"] = f"unknown kind: {kind}"
    record["wall_seconds"] = round(time.time() - t0, 2)

    # 4. New hash
    new_hashes = hash_results_tree(results_dir)
    record["new_file_count"] = len(new_hashes)

    # 5. Per-file diff
    all_files = sorted(set(baseline_hashes) | set(new_hashes))
    match, differ, new, missing = [], [], [], []
    for f in all_files:
        if f in baseline_hashes and f in new_hashes:
            if baseline_hashes[f] == new_hashes[f]:
                match.append(f)
            else:
                differ.append({"file": f, "baseline": baseline_hashes[f], "new": new_hashes[f]})
        elif f in new_hashes:
            new.append({"file": f, "new": new_hashes[f]})
        else:
            missing.append({"file": f, "baseline": baseline_hashes[f]})
    record["match"] = match
    record["differ"] = differ
    record["new"] = new
    record["missing"] = missing
    record["counts"] = {
        "match": len(match), "differ": len(differ),
        "new": len(new), "missing": len(missing),
    }

    # 6. Restore MISSING files from backup (runner didn't regenerate them)
    restored = []
    for m in missing:
        src = backup_dir / m["file"]
        dst = results_dir / m["file"]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        restored.append(m["file"])
    record["restored_missing"] = restored

    # 7. Cleanup backup
    if backup_dir.exists():
        shutil.rmtree(backup_dir)

    record["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Persist per-phase JSON
    (LOG_DIR / f"phase_{phase_id}_diff.json").write_text(json.dumps(record, indent=2))
    return record


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    print(f"=== Orchestrator start {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    print(f"REPO_ROOT: {REPO_ROOT}")
    print(f"VENV_PY:   {VENV_PY}")
    if only:
        print(f"FILTER: only phases matching '{only}'")
    print()
    summary = []
    for phase_id, phase_path, kind, args in PHASES:
        if only and only not in phase_id:
            continue
        print(f"[{phase_id}] {phase_path}  ({kind})")
        try:
            r = run_phase(phase_id, phase_path, kind, args)
            c = r["counts"]
            wall = r["wall_seconds"]
            rc = r["returncode"]
            verdict = "✓ BIT-IDENTICAL" if c["differ"] == 0 and rc == 0 else (
                "⚠ DIFFER" if c["differ"] > 0 else f"✗ rc={rc}")
            print(f"    rc={rc}  wall={wall:.1f}s  match={c['match']} differ={c['differ']} "
                  f"new={c['new']} missing={c['missing']}  → {verdict}")
            summary.append({
                "phase_id": phase_id, "returncode": rc, "wall_seconds": wall,
                "counts": c, "verdict": verdict,
            })
        except Exception as e:
            print(f"    EXCEPTION: {e}")
            summary.append({"phase_id": phase_id, "error": str(e)})
    (LOG_DIR / "orchestrator_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\n=== Orchestrator done {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    n_clean = sum(1 for s in summary if s.get("counts", {}).get("differ") == 0
                  and s.get("returncode") == 0)
    print(f"Bit-identical phases: {n_clean} / {len(summary)}")


if __name__ == "__main__":
    main()
