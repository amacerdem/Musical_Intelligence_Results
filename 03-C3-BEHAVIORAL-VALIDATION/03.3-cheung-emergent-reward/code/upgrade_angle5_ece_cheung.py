"""Phase 10 Audio-Native Upgrade — Angle 5 — Per-belief ECE on Cheung corpus.

Pre-registration: ../AUDIO_NATIVE_UPGRADE.md §2 Angle 5 (frozen 2026-05-16).
Engine SHA pin: 318eb2f529d7103e8b7d80b01228357fdc4e0217.

Applies Phase 5 ECE methodology (held-out N=206k DEAM frames, ECE=0.079 pooled)
verbatim to Cheung corpus. Tests cross-corpus calibration generalization.

Pipeline:
  1. Import Phase 5 belief-trace extraction machinery (verbatim, no logic edits).
  2. Iterate over 30 Cheung WAVs (rhythm1 only; sufficient sample size for
     cross-corpus generalization test).
  3. Per stim: run engine, extract (π_pred, PE) traces for 8 Core beliefs.
  4. Pool traces across stim × belief, compute ECE + Brier vs uniform baseline.
  5. Apply pre-registered decision rule.

Methodological notes:
  - MAX_DURATION_S = 30s (matches Phase 5 DEAM convention verbatim).
  - WARMUP_FRAMES = 16 (matches Phase 5).
  - rhythm1 only (90 WAVs total would give 3× the data but each stim only
    differs by rhythm timing, not chord identity — for ECE generalization,
    rhythm1 alone is sufficient; cross-rhythm validation in Angle 4).
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

PHASE_DIR = Path(__file__).resolve().parent.parent
ENGINE_ROOT = PHASE_DIR.parent.parent
PHASE5_CODE = ENGINE_ROOT / "Musical-Intelligence-Reproduction" / "05-ece-belief-calibration" / "code"

# Engine + Phase 5 imports
sys.path.insert(0, str(ENGINE_ROOT))                          # Musical_Intelligence package
sys.path.insert(0, str(PHASE5_CODE.parent.parent / "_infra")) # _engine_path
sys.path.insert(0, str(PHASE5_CODE))                          # Phase 5 module

# Phase 5 machinery (canonical, no edits)
from extract_belief_traces import (   # type: ignore
    collect_mechanisms,
    run_engine_on_song,
    extract_belief_trace,
    PAPER_BELIEFS,
    WARMUP_FRAMES,
    SAMPLE_RATE,
    N_FFT,
    HOP_LENGTH,
    N_MELS,
    MAX_DURATION_S,
)
import importlib

WAV_DIR = PHASE_DIR / "data" / "cheung_audio" / "stimuli_rhythm1"
OUT_DIR = PHASE_DIR / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TRACES_DIR = PHASE_DIR / "data" / "cheung_audio_outputs" / "belief_traces_rhythm1"
TRACES_DIR.mkdir(parents=True, exist_ok=True)

ENGINE_AGGREGATE_SHA_EXPECTED = "482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88"
N_BINS = 10
SEED = 42


def file_sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def aggregate_engine_sha():
    engine_dir = ENGINE_ROOT / "Musical_Intelligence"
    files = sorted(p for p in engine_dir.rglob("*.py") if "__pycache__" not in p.parts)
    h = hashlib.sha256()
    for fp in files:
        sub = hashlib.sha256()
        with open(fp, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                sub.update(chunk)
        h.update((sub.hexdigest() + "\n").encode("ascii"))
    return h.hexdigest()


def equal_mass_ece(pi_pred: np.ndarray, y: np.ndarray, n_bins: int = N_BINS) -> dict:
    """Equal-mass binning ECE — same as Phase 5 compute_metrics.equal_mass_ece."""
    n = len(pi_pred)
    if n < n_bins:
        return {"ece": np.nan, "bin_count": 0}
    order = np.argsort(pi_pred)
    sp = pi_pred[order]
    sy = y[order]
    bin_size = n // n_bins
    gaps = []
    weights = []
    bins_data = []
    for k in range(n_bins):
        lo = k * bin_size
        hi = (k + 1) * bin_size if k < n_bins - 1 else n
        if hi <= lo:
            continue
        mean_pp = float(sp[lo:hi].mean())
        mean_y = float(sy[lo:hi].mean())
        gap = abs(mean_pp - mean_y)
        gaps.append(gap)
        weights.append(hi - lo)
        bins_data.append({"bin": k, "mean_pi_pred": mean_pp, "mean_y": mean_y, "gap": gap, "n": hi - lo})
    weights = np.array(weights, dtype=np.float64)
    gaps_arr = np.array(gaps, dtype=np.float64)
    ece = float(np.sum(weights * gaps_arr) / weights.sum())
    return {"ece": ece, "bin_count": len(gaps), "bins": bins_data}


def brier_score(pi_pred: np.ndarray, y: np.ndarray) -> float:
    return float(np.mean((pi_pred - y) ** 2))


def uniform_baseline_brier(y: np.ndarray) -> float:
    return brier_score(np.full_like(y, fill_value=0.5), y)


def main():
    print("Phase 10 Audio-Native Upgrade — Angle 5 — ECE on Cheung corpus")
    print("=" * 70)

    actual_sha = aggregate_engine_sha()
    if actual_sha != ENGINE_AGGREGATE_SHA_EXPECTED:
        print(f"ERROR: engine SHA mismatch", file=sys.stderr); return 2
    print(f"Engine SHA verified: {actual_sha[:16]}...")

    print(f"\nPhase 5 conventions inherited:")
    print(f"  SAMPLE_RATE = {SAMPLE_RATE}, N_FFT = {N_FFT}, HOP = {HOP_LENGTH}, N_MELS = {N_MELS}")
    print(f"  MAX_DURATION_S = {MAX_DURATION_S} (cap matches Phase 5)")
    print(f"  WARMUP_FRAMES = {WARMUP_FRAMES}")

    print("\nCollecting mechanisms (auto-discover F1-F9) ...")
    t0 = time.time()
    nuclei, h3_demands = collect_mechanisms()
    print(f"  built {len(nuclei)} nuclei, {len(h3_demands)} H3 demands in {time.time()-t0:.1f}s")

    # Load 8 Core belief instances
    print(f"\nLoading {len(PAPER_BELIEFS)} Core belief instances ...")
    belief_instances = []
    for (fn, mech, module_path, class_name) in PAPER_BELIEFS:
        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name)
        inst = cls()
        belief_instances.append((fn, mech, class_name, inst))
        print(f"  {fn} {mech:<6s} {class_name}")

    # Iterate over 30 Cheung WAVs (rhythm1)
    wavs = sorted(WAV_DIR.glob("*.wav"))
    print(f"\nProcessing {len(wavs)} Cheung rhythm1 stimuli ...")

    per_stim_records = []
    per_belief_pool = {cls: {"pi_pred": [], "y_continuous": [], "pe": []}
                        for (_, _, cls, _) in [(fn, m, c, i) for fn, m, c, i in [
                            (b[0], b[1], b[2], b[3]) for b in belief_instances]]}
    # Actually keep it simple:
    per_belief_pool = {b[2]: {"pi_pred": [], "y_continuous": [], "pe": []} for b in belief_instances}

    t_start = time.time()
    for wi, wav_path in enumerate(wavs, 1):
        t0 = time.time()
        engine_out = run_engine_on_song(wav_path, nuclei, h3_demands)
        t_engine = time.time() - t0

        stim_traces = {}
        for fn, mech, class_name, inst in belief_instances:
            try:
                mech_output = engine_out["outputs"][mech]   # mechanism output for this belief
            except KeyError:
                print(f"    [{wav_path.stem}] {class_name}: mech output {mech} missing", file=sys.stderr)
                continue
            try:
                trace = extract_belief_trace(inst, mech_output, engine_out["h3_features"])
            except Exception as exc:
                print(f"    [{wav_path.stem}] {class_name}: extract failed: {exc}", file=sys.stderr)
                continue
            stim_traces[class_name] = {
                "pi_pred": trace["pi_pred"].astype(np.float32),
                "pe": trace["pe"].astype(np.float32),
                "y_continuous": trace["y_continuous"].astype(np.float32),
            }
            per_belief_pool[class_name]["pi_pred"].append(trace["pi_pred"])
            per_belief_pool[class_name]["y_continuous"].append(trace["y_continuous"])
            per_belief_pool[class_name]["pe"].append(trace["pe"])

        # Save per-stim traces (compact)
        out_npz = TRACES_DIR / f"{wav_path.stem}.npz"
        npz_args = {}
        for cls, t in stim_traces.items():
            npz_args[f"{cls}_pi_pred"] = t["pi_pred"]
            npz_args[f"{cls}_pe"] = t["pe"]
            npz_args[f"{cls}_y"] = t["y_continuous"]
        np.savez_compressed(out_npz, **npz_args)

        per_stim_records.append({
            "stim_id": wav_path.stem,
            "n_beliefs_ok": len(stim_traces),
            "n_frames_post_warmup": int(len(next(iter(stim_traces.values()))["pi_pred"])) if stim_traces else 0,
            "wall_engine_s": t_engine,
            "wall_total_s": time.time() - t0,
            "traces_npz": str(out_npz.relative_to(PHASE_DIR)),
        })
        elapsed = time.time() - t_start
        eta = elapsed / wi * (len(wavs) - wi)
        print(f"  [{wi:2d}/{len(wavs)}] {wav_path.stem}: "
              f"engine={t_engine:.1f}s, beliefs={len(stim_traces)}/{len(belief_instances)}, "
              f"elapsed={elapsed:.0f}s, ETA={eta:.0f}s")

    # Pool per-belief
    per_belief_ece = {}
    for class_name, pool in per_belief_pool.items():
        if not pool["pi_pred"]:
            per_belief_ece[class_name] = {"error": "no traces"}
            continue
        pi_pred = np.concatenate(pool["pi_pred"])
        y = np.concatenate(pool["y_continuous"])
        pe = np.concatenate(pool["pe"])
        ece_res = equal_mass_ece(pi_pred, y, n_bins=N_BINS)
        brier_mi = brier_score(pi_pred, y)
        brier_uniform = uniform_baseline_brier(y)
        per_belief_ece[class_name] = {
            "n_frames_pooled": int(len(pi_pred)),
            "mean_pi_pred": float(pi_pred.mean()),
            "mean_y": float(y.mean()),
            "mean_abs_pe": float(np.abs(pe).mean()),
            "ece_equal_mass_10bin": ece_res["ece"],
            "brier_mi": brier_mi,
            "brier_uniform": brier_uniform,
            "brier_ratio_uniform_to_mi": float(brier_uniform / brier_mi) if brier_mi > 0 else None,
        }

    # Pooled across all 8 beliefs
    all_pp = np.concatenate([np.concatenate(per_belief_pool[c]["pi_pred"]) for c in per_belief_pool if per_belief_pool[c]["pi_pred"]])
    all_y = np.concatenate([np.concatenate(per_belief_pool[c]["y_continuous"]) for c in per_belief_pool if per_belief_pool[c]["y_continuous"]])
    pooled_ece = equal_mass_ece(all_pp, all_y, n_bins=N_BINS)
    pooled_brier_mi = brier_score(all_pp, all_y)
    pooled_brier_uniform = uniform_baseline_brier(all_y)

    # Decision rule per spec §2 Angle 5
    ece_value = pooled_ece["ece"]
    brier_ratio = pooled_brier_uniform / pooled_brier_mi if pooled_brier_mi > 0 else 0
    pos = ece_value <= 0.10 and brier_ratio >= 5.0
    neg = ece_value > 0.15 or brier_ratio < 3.0
    if pos and not neg:
        verdict = "POSITIVE_CHEUNG_CALIBRATED"
    elif neg and not pos:
        verdict = "NEGATIVE_CHEUNG_NOT_CALIBRATED"
    else:
        verdict = "INCONCLUSIVE"

    summary = {
        "stage": "Phase 10 Audio-Native Upgrade — Angle 5",
        "engine_pin_commit": "318eb2f529d7103e8b7d80b01228357fdc4e0217",
        "engine_aggregate_sha256": actual_sha,
        "n_stim": len(per_stim_records),
        "rhythm_condition": 1,
        "max_duration_s": MAX_DURATION_S,
        "warmup_frames": WARMUP_FRAMES,
        "n_beliefs": len(belief_instances),
        "belief_list": [{"function": b[0], "mech": b[1], "class": b[2]} for b in belief_instances],
        "per_belief_ece": per_belief_ece,
        "pooled": {
            "n_frames": int(len(all_pp)),
            "ece_equal_mass_10bin": pooled_ece["ece"],
            "brier_mi": pooled_brier_mi,
            "brier_uniform": pooled_brier_uniform,
            "brier_ratio_uniform_to_mi": float(brier_ratio),
        },
        "decision": {
            "verdict": verdict,
            "rule_pos": "pooled ECE ≤ 0.10 AND Brier ratio ≥ 5×",
            "rule_neg": "pooled ECE > 0.15 OR Brier ratio < 3×",
            "phase5_paper_anchor_ece_DEAM": 0.079,
        },
        "per_stim_records": per_stim_records,
    }
    with open(OUT_DIR / "angle5_results.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print()
    print("=" * 70)
    print(f"VERDICT: {verdict}")
    print(f"  Pooled ECE (equal-mass 10-bin) = {pooled_ece['ece']:.4f}")
    print(f"  Pooled Brier MI               = {pooled_brier_mi:.4f}")
    print(f"  Pooled Brier uniform          = {pooled_brier_uniform:.4f}")
    print(f"  Brier ratio uniform/MI        = {brier_ratio:.2f}× (DEAM paper-anchor: 10.8×)")
    print(f"  Phase 5 DEAM paper-anchor ECE = 0.079")
    print()
    print(f"Per-belief ECE:")
    for cls, m in per_belief_ece.items():
        if "error" in m: continue
        print(f"  {cls:<22s} ECE={m['ece_equal_mass_10bin']:.4f}  brier_ratio={m.get('brier_ratio_uniform_to_mi') or 0:.2f}×")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
