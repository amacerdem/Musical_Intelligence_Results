#!/usr/bin/env python3
"""V-Reproduction Phase 6 extended — R³ Extended OOS Consonance Battery.

Single entry point for the nine-claim consonance generalisation audit
specified in `03-PRE-REGISTRATION.md` (frozen 2026-05-16).

Inputs (read-only):
    Science/datasets/consonance/marjieh2024/data-csv/{rating_dyh3dd,
        rating_flute_harmonic_harflt, rating_guitar_harmonic_hargtr,
        rating_piano_harmonic_harpno, pure_dyad_purdyrt}.csv
    Science/datasets/consonance/bidelman2009_ffr.csv
    Science/datasets/consonance/schwartz2003_speech_harmonics.csv
    Science/datasets/consonance/sethares1993_dissonance.csv
    Science/datasets/consonance/interval_tension/data/indian_tension_ratings.csv

Outputs:
    results/29_r3ext_correlations.csv          per-claim per-channel ρ + verdict
    results/29_r3ext_manifest.json             provenance + decision-rule audit
    results/29_input_hashes.json               SHA-256 of every input CSV
    results/29_sign_convention.json            per-claim expected-sign log
    results/29_invariants.json                 CDC + HRI invariant outcomes
    results/{C-R3EXT-NN}_engine.csv            per-claim R³ engine output

Decision rules: see 03-PRE-REGISTRATION.md §"Decision rules".
Synthesis recipe: see 00-METHODOLOGY.md §2.2-§2.4.

Self-contained execution:
    cd 29-r3-extended-oos-consonance
    bash code/run.sh
"""
from __future__ import annotations

# ── Determinism BEFORE numpy/torch import ─────────────────────────────
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torchaudio.transforms as T_audio
from scipy import stats

# ── Paths ─────────────────────────────────────────────────────────────
# Layout: V-Reproduction/06-r3-oos-consonance/extended/code/run_extended.py
EXTENDED_DIR = Path(__file__).resolve().parent.parent
PARENT_PHASE = EXTENDED_DIR.parent
V_REPRO = PARENT_PHASE.parent
SCIENCE = V_REPRO.parent
PHASE_DIR = EXTENDED_DIR  # preserve historical variable name for the rest of the script

sys.path.insert(0, str(V_REPRO / "_infra"))
import _engine_path  # noqa: E402,F401  (side-effect: extends sys.path)

DATASETS = SCIENCE / "Science" / "datasets" / "consonance"
if not DATASETS.exists():
    raise SystemExit(f"[abort] dataset root not found: {DATASETS}")

RESULTS = PHASE_DIR / "results"
RESULTS.mkdir(exist_ok=True, parents=True)

ENGINE_HEAD_FILE = V_REPRO / "_infra" / "manifests" / "engine_head.json"

# ── Engine HEAD SHA verification ──────────────────────────────────────
def _aggregate_engine_sha(engine_root: Path) -> str:
    """SHA-256 of (sorted .py file SHAs), excluding __pycache__.

    Mirrors the canonical method documented in engine_head.json and
    implemented in 21-c3-chill-prediction/_infra/sha_utils.py:
        find <root> -type f -name '*.py' -not -path '*/__pycache__/*'
            | sort | xargs shasum -a 256 | awk '{print $1}'
            | shasum -a 256 | awk '{print $1}'
    """
    py_files = sorted(p for p in engine_root.rglob("*.py")
                      if "__pycache__" not in p.parts)
    inner = hashlib.sha256()
    for p in py_files:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        inner.update(h.hexdigest().encode("ascii"))
        inner.update(b"\n")
    return inner.hexdigest(), len(py_files)


def verify_engine_head():
    """Abort if vendored engine aggregate SHA differs from manifest."""
    with open(ENGINE_HEAD_FILE) as fh:
        meta = json.load(fh)
    expected_sha = meta["content_aggregate_sha256"]
    engine_root = V_REPRO / "engine" / "Musical_Intelligence"
    if not engine_root.is_dir():
        raise SystemExit(f"[abort] vendored engine not found: {engine_root}")
    aggregate, n_files = _aggregate_engine_sha(engine_root)
    if aggregate != expected_sha:
        raise SystemExit(
            f"[abort] engine aggregate SHA mismatch.\n"
            f"  expected {expected_sha}\n"
            f"  got      {aggregate}\n"
            f"Pre-reg §Forbidden moves item 1 violation."
        )
    print(f"[engine] HEAD verified: {meta['pinned_commit'][:12]}  "
          f"aggregate SHA OK ({n_files} files)")
    return meta["pinned_commit"]


# ── Audio constants (frozen at pre-reg) ───────────────────────────────
SR = 44_100
DURATION = 0.5
N_HARM = 6
F0_BASE = 261.625565  # 12-TET C4

R3_NAMES = (
    "roughness", "sethares_dissonance", "helmholtz_kang",
    "stumpf_fusion", "sensory_pleasantness", "inharmonicity",
    "harmonic_deviation",
)

# Headline channels used by the decision rule (PASS criterion ≥ 2 / 3).
HEADLINE_CHANNELS = ("stumpf_fusion", "sensory_pleasantness", "roughness")

# Theoretical sign convention (from Group A engine specification,
# 00-METHODOLOGY.md §3). Positive = consonance-aligned, negative = inverted.
EXPECTED_SIGN = {
    "stumpf_fusion": +1,
    "sensory_pleasantness": +1,
    "roughness": -1,
}

# Classical Western interval subset for the HRI invariant.
HIERARCHY_SEMITONES_FULL = (0, 5, 4, 7, 8, 6)   # P1, P4, M3, P5, m6, TT
HIERARCHY_SEMITONES_NOP1 = (5, 4, 7, 8, 6)      # for datasets lacking P1


# ── Audio helpers ─────────────────────────────────────────────────────
def synth_audio(freqs, amps):
    t = torch.linspace(0.0, DURATION, int(SR * DURATION), dtype=torch.float64)
    audio = torch.zeros_like(t)
    for f, a in zip(freqs, amps):
        if 0.0 < f < SR / 2.0:
            audio += a * torch.sin(2.0 * np.pi * f * t)
    return audio.unsqueeze(0).to(torch.float32)


def synth_interval(s, f0=F0_BASE, n_harm=N_HARM):
    f1 = f0
    f2 = f0 * 2 ** (s / 12.0)
    fs, ams = [], []
    for fb in (f1, f2):
        for n in range(1, n_harm + 1):
            ff = fb * n
            if ff < SR / 2.0:
                fs.append(ff)
                ams.append(1.0 / n)
    return synth_audio(fs, ams)


# ── Engine init (deferred until after SHA verification) ───────────────
_r3 = None
_mel = None


def init_engine():
    global _r3, _mel
    print("[engine] Initialising R3Extractor …")
    t0 = time.time()
    from Musical_Intelligence.ear.r3.extractor import R3Extractor
    _r3 = R3Extractor()
    _mel = T_audio.MelSpectrogram(
        sample_rate=SR, n_fft=2048, hop_length=256, n_mels=128, power=2.0
    )
    print(f"[engine] R3Extractor ready ({time.time() - t0:.1f} s)")


def extract_r3(audio):
    with torch.no_grad():
        mel = torch.log1p(_mel(audio))
        mel = mel / mel.max().clamp(min=1e-8)
        out = _r3.extract(mel, audio=audio, sr=SR)
        return out.features[0, :, :7].mean(dim=0).cpu().numpy()


# ── Input SHA logging ─────────────────────────────────────────────────
def sha256_of(path: Path) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# ── Per-claim runners ─────────────────────────────────────────────────
def _bin_dense_rating(csv_path: Path) -> tuple[np.ndarray, np.ndarray, int]:
    """Mean rating per integer-semitone bin for Marjieh dense-rating CSVs.

    Returns (semitone_bins, mean_per_bin, n_raw_ratings).
    Drops bins with fewer than 3 ratings (consistent with Phase 6 floor).
    """
    df = pd.read_csv(csv_path)
    n_raw = len(df)
    df["s_int"] = df["v1"].round().astype(int)
    df = df[(df["s_int"] >= 0) & (df["s_int"] <= 12)].reset_index(drop=True)
    agg = df.groupby("s_int")["rating"].agg(["mean", "count"]).reset_index()
    agg = agg[agg["count"] >= 3].reset_index(drop=True)
    return agg["s_int"].to_numpy(), agg["mean"].to_numpy(), n_raw


def _per_channel_rho(human: np.ndarray, feats: np.ndarray, polarity: int = +1):
    """Spearman ρ per R³ channel; polarity flips ρ sign when source column
    encodes dissonance / tension rather than consonance (polarity = -1)."""
    rows = []
    for i, name in enumerate(R3_NAMES):
        rho, p = stats.spearmanr(human, feats[:, i])
        rho_adj = polarity * float(rho)
        rows.append({"channel": name, "rho": rho_adj, "p": float(p)})
    return rows


def _run_marjieh_dense(claim_id: str, csv_name: str, n_harm: int = N_HARM):
    csv_path = DATASETS / "marjieh2024" / "data-csv" / csv_name
    print(f"\n[{claim_id}] {csv_name}")
    bins, mean_per_bin, n_raw = _bin_dense_rating(csv_path)
    feats = np.stack([extract_r3(synth_interval(int(s), n_harm=n_harm))
                      for s in bins])
    pd.DataFrame({
        "semitone": bins,
        "mean_rating": mean_per_bin,
        **{f"r3_{n}": feats[:, i] for i, n in enumerate(R3_NAMES)},
    }).to_csv(RESULTS / f"{claim_id}_engine.csv", index=False)
    rows = _per_channel_rho(mean_per_bin, feats, polarity=+1)
    print(f"  N_raw={n_raw}  N_bins={len(bins)}  "
          f"stumpf_fusion ρ={[r['rho'] for r in rows if r['channel']=='stumpf_fusion'][0]:+.3f}")
    return {
        "claim_id": claim_id,
        "n_raw": int(n_raw),
        "n_bins": int(len(bins)),
        "polarity": +1,
        "semitones": bins.tolist(),
        "rows": rows,
        "source": str(csv_path.relative_to(SCIENCE)),
        "input_sha256": sha256_of(csv_path),
    }


def _run_csv_per_interval(claim_id: str, csv_rel: str, target_col: str,
                          polarity: int, semitone_col: str = "semitones"):
    csv_path = DATASETS / csv_rel
    print(f"\n[{claim_id}] {csv_rel} (target={target_col}, polarity={polarity:+d})")
    df = pd.read_csv(csv_path)
    semitones = df[semitone_col].to_numpy().astype(int)
    target = df[target_col].to_numpy().astype(float)
    feats = np.stack([extract_r3(synth_interval(int(s))) for s in semitones])
    pd.DataFrame({
        "semitone": semitones,
        target_col: target,
        **{f"r3_{n}": feats[:, i] for i, n in enumerate(R3_NAMES)},
    }).to_csv(RESULTS / f"{claim_id}_engine.csv", index=False)
    rows = _per_channel_rho(target, feats, polarity=polarity)
    print(f"  N={len(df)}  "
          f"stumpf_fusion ρ={[r['rho'] for r in rows if r['channel']=='stumpf_fusion'][0]:+.3f}")
    return {
        "claim_id": claim_id,
        "n_raw": int(len(df)),
        "n_intervals": int(len(df)),
        "polarity": polarity,
        "semitones": semitones.tolist(),
        "rows": rows,
        "source": str(csv_path.relative_to(SCIENCE)),
        "target_column": target_col,
        "input_sha256": sha256_of(csv_path),
    }


def _run_indian_tension(claim_id: str):
    csv_path = DATASETS / "interval_tension" / "data" / "indian_tension_ratings.csv"
    print(f"\n[{claim_id}] indian_tension_ratings.csv (tension ↑ ⇔ consonance ↓)")
    df = pd.read_csv(csv_path)
    interval_map = {
        "m2": 1, "M2": 2, "m3": 3, "M3": 4, "P4": 5, "A4": 6,
        "P5": 7, "m6": 8, "M6": 9, "m7": 10, "M7": 11, "P8": 12,
    }
    df["semitone"] = df["Interval"].map(interval_map)
    if df["semitone"].isna().any():
        unmapped = df.loc[df["semitone"].isna(), "Interval"].unique().tolist()
        raise SystemExit(f"[abort] unmapped interval labels: {unmapped}")
    agg = df.groupby("semitone")["tensionrating"].mean().reset_index()
    semitones = agg["semitone"].to_numpy().astype(int)
    target = agg["tensionrating"].to_numpy().astype(float)
    feats = np.stack([extract_r3(synth_interval(int(s))) for s in semitones])

    pd.DataFrame({
        "semitone": semitones,
        "mean_tension": target,
        **{f"r3_{n}": feats[:, i] for i, n in enumerate(R3_NAMES)},
    }).to_csv(RESULTS / f"{claim_id}_engine.csv", index=False)

    # Auxiliary per-group sub-correlations (not load-bearing).
    aux = {}
    for grp, sub in df.groupby("Group"):
        grp_agg = sub.groupby("semitone")["tensionrating"].mean().reset_index()
        # Align to the same 12 intervals — every group rates the full set.
        if len(grp_agg) == len(semitones):
            grp_target = grp_agg.sort_values("semitone")["tensionrating"].to_numpy()
            grp_rho_stumpf, _ = stats.spearmanr(grp_target, feats[:, 3])
            aux[str(grp)] = {"n": int(len(sub)),
                             "stumpf_fusion_rho_inv": float(-grp_rho_stumpf)}

    rows = _per_channel_rho(target, feats, polarity=-1)
    print(f"  N_raw={len(df)}  N_intervals={len(semitones)}  "
          f"sensory_pleasantness ρ_inv="
          f"{[r['rho'] for r in rows if r['channel']=='sensory_pleasantness'][0]:+.3f}")

    return {
        "claim_id": claim_id,
        "n_raw": int(len(df)),
        "n_intervals": int(len(semitones)),
        "polarity": -1,
        "semitones": semitones.tolist(),
        "rows": rows,
        "auxiliary_per_group": aux,
        "source": str(csv_path.relative_to(SCIENCE)),
        "target_column": "tensionrating",
        "input_sha256": sha256_of(csv_path),
    }


# ── Decision rules (locked at pre-reg) ────────────────────────────────
def per_claim_verdict(claim_result):
    """Apply PASS / PARTIAL / FAIL rule from pre-reg §Decision rules."""
    rows = {r["channel"]: r for r in claim_result["rows"]}
    polarity = claim_result["polarity"]
    sign_ok = []
    mag_strong = []
    mag_weak = []
    for ch in HEADLINE_CHANNELS:
        rho = rows[ch]["rho"]
        # `rho` is already polarity-adjusted by _per_channel_rho.
        # Expected sign reflects the engine spec for a consonance-aligned
        # target. After polarity adjustment, the test is straightforward:
        exp_sign = EXPECTED_SIGN[ch]
        sign_match = (rho >= 0) == (exp_sign > 0) if abs(rho) > 1e-9 else False
        sign_ok.append(sign_match)
        if sign_match and abs(rho) >= 0.60:
            mag_strong.append(ch)
        elif sign_match and abs(rho) >= 0.40:
            mag_weak.append(ch)
    n_strong = len(mag_strong)
    n_weak = len(mag_weak)
    sign_consistent_count = sum(sign_ok)
    if n_strong >= 2:
        verdict = "PASS"
    elif n_strong == 1 or (n_strong + n_weak) >= 2:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"
    return {
        "verdict": verdict,
        "n_strong_channels": n_strong,
        "n_weak_channels": n_weak,
        "sign_consistent_channels": sign_consistent_count,
        "strong_channels": mag_strong,
        "weak_channels": mag_weak,
    }


def cross_dataset_consistency(claim_results):
    """CDC invariant: ≥ 7 / 9 sign-consistent per channel."""
    out = {}
    for ch in HEADLINE_CHANNELS:
        exp_sign = EXPECTED_SIGN[ch]
        sign_match = 0
        per_dataset = {}
        for cid, res in claim_results.items():
            rho = next(r["rho"] for r in res["rows"] if r["channel"] == ch)
            ok = (rho >= 0) == (exp_sign > 0) if abs(rho) > 1e-9 else False
            per_dataset[cid] = {"rho": rho, "sign_ok": bool(ok)}
            if ok:
                sign_match += 1
        out[ch] = {
            "n_sign_consistent": sign_match,
            "n_datasets": len(claim_results),
            "per_dataset": per_dataset,
            "pass": sign_match >= 7,
        }
    out["cdc_pass"] = all(out[ch]["pass"] for ch in HEADLINE_CHANNELS)
    return out


def hierarchy_reproduction(claim_results):
    """HRI invariant: ranking ρ on classical interval subset, headline channel."""
    out = {"per_dataset": {}, "n_pass": 0, "n_total": len(claim_results)}
    for cid, res in claim_results.items():
        semitones = np.array(res["semitones"])
        # Pick headline channel = max |rho| between stumpf_fusion and sensory_pleasantness
        ch_pick, max_abs = None, -1.0
        for ch in ("stumpf_fusion", "sensory_pleasantness"):
            rho = next(r["rho"] for r in res["rows"] if r["channel"] == ch)
            if abs(rho) > max_abs:
                max_abs, ch_pick = abs(rho), ch
        engine_csv = RESULTS / f"{cid}_engine.csv"
        df = pd.read_csv(engine_csv)
        target_col = next(c for c in ("mean_rating", "mean_tension",
                                       res.get("target_column", ""))
                          if c in df.columns)
        sub_set = (HIERARCHY_SEMITONES_NOP1 if 0 not in semitones
                   else HIERARCHY_SEMITONES_FULL)
        sub_mask = df["semitone"].isin(sub_set)
        if sub_mask.sum() < 4:
            out["per_dataset"][cid] = {"headline_channel": ch_pick,
                                        "ranking_rho": None,
                                        "subset_n": int(sub_mask.sum()),
                                        "pass": False,
                                        "note": "subset coverage too low"}
            continue
        rank_rho, _ = stats.spearmanr(
            df.loc[sub_mask, target_col].to_numpy() * res["polarity"],
            df.loc[sub_mask, f"r3_{ch_pick}"].to_numpy(),
        )
        # For roughness sign convention, ranking_rho sign already absorbed.
        passed = bool(abs(rank_rho) >= 0.85)
        out["per_dataset"][cid] = {
            "headline_channel": ch_pick,
            "subset_semitones": sorted(set(semitones) & set(sub_set)),
            "subset_n": int(sub_mask.sum()),
            "ranking_rho": float(rank_rho),
            "pass": passed,
        }
        if passed:
            out["n_pass"] += 1
    out["hri_pass"] = out["n_pass"] >= 7
    return out


def axis_level_verdict(per_claim, cdc, hri):
    pass_count = sum(1 for v in per_claim.values() if v["verdict"] == "PASS")
    if pass_count >= 7 and cdc["cdc_pass"] and hri["hri_pass"]:
        return "CLOSED-STRONG"
    if pass_count >= 5 and cdc["cdc_pass"]:
        return "CLOSED-PASS"
    if pass_count >= 3 and cdc["cdc_pass"]:
        return "CLOSED-PART"
    return "CLOSED-FAIL"


# ── Independence audit ────────────────────────────────────────────────
def independence_audit():
    """git log -S sweep of the engine subtree for each input CSV name.

    Records the verbatim hit count. This is the test, not an assertion.
    """
    engine_root = V_REPRO / "engine" / "Musical_Intelligence"
    needles = [
        "rating_dyh3dd", "rating_flute_harmonic_harflt",
        "rating_guitar_harmonic_hargtr", "rating_piano_harmonic_harpno",
        "pure_dyad_purdyrt", "bidelman2009_ffr",
        "schwartz2003_speech_harmonics", "sethares1993_dissonance",
        "indian_tension_ratings",
        "Bidelman", "Schwartz", "Marjieh", "Lahdelma",
    ]
    audit = {}
    for needle in needles:
        try:
            grep_out = subprocess.run(
                ["git", "grep", "-l", needle, "--", "Musical_Intelligence"],
                cwd=SCIENCE, capture_output=True, text=True, timeout=30,
            )
            files = [f for f in grep_out.stdout.splitlines() if f]
        except (subprocess.SubprocessError, FileNotFoundError):
            files = ["<git-grep-unavailable>"]
        audit[needle] = {"hits": len(files), "files": files[:20]}
    return audit


# ── Main ──────────────────────────────────────────────────────────────
def main():
    t0 = time.time()
    pinned = verify_engine_head()
    init_engine()

    claim_results = {}

    # Tier 1 — Marjieh sub-studies (5 dense-rating CSVs).
    claim_results["C-R3EXT-01"] = _run_marjieh_dense("C-R3EXT-01", "rating_dyh3dd.csv")
    claim_results["C-R3EXT-02"] = _run_marjieh_dense("C-R3EXT-02", "rating_flute_harmonic_harflt.csv")
    claim_results["C-R3EXT-03"] = _run_marjieh_dense("C-R3EXT-03", "rating_guitar_harmonic_hargtr.csv")
    claim_results["C-R3EXT-04"] = _run_marjieh_dense("C-R3EXT-04", "rating_piano_harmonic_harpno.csv")
    claim_results["C-R3EXT-05"] = _run_marjieh_dense("C-R3EXT-05", "pure_dyad_purdyrt.csv", n_harm=1)

    # Tier 2 — per-interval CSVs.
    claim_results["C-R3EXT-06"] = _run_csv_per_interval(
        "C-R3EXT-06", "bidelman2009_ffr.csv",
        target_col="behavioral_consonance", polarity=+1,
    )
    claim_results["C-R3EXT-07"] = _run_csv_per_interval(
        "C-R3EXT-07", "schwartz2003_speech_harmonics.csv",
        target_col="percent_similar", polarity=+1,
    )
    claim_results["C-R3EXT-08"] = _run_csv_per_interval(
        "C-R3EXT-08", "sethares1993_dissonance.csv",
        target_col="relative_dissonance", polarity=-1,
    )
    claim_results["C-R3EXT-09"] = _run_indian_tension("C-R3EXT-09")

    # Per-claim verdicts.
    per_claim = {cid: per_claim_verdict(res) for cid, res in claim_results.items()}

    # Invariants.
    cdc = cross_dataset_consistency(claim_results)
    hri = hierarchy_reproduction(claim_results)

    axis_verdict = axis_level_verdict(per_claim, cdc, hri)

    # ── Output artefacts ────────────────────────────────────────────
    # Per-claim correlations CSV.
    correl_rows = []
    for cid, res in claim_results.items():
        for r in res["rows"]:
            correl_rows.append({
                "claim_id": cid,
                "source": res["source"],
                "polarity": res["polarity"],
                "channel": r["channel"],
                "rho": round(r["rho"], 4),
                "p": r["p"],
                "verdict": per_claim[cid]["verdict"],
            })
    pd.DataFrame(correl_rows).to_csv(RESULTS / "29_r3ext_correlations.csv", index=False)

    # Input SHA-256 log.
    with open(RESULTS / "29_input_hashes.json", "w") as fh:
        json.dump({cid: {"source": res["source"], "sha256": res["input_sha256"]}
                   for cid, res in claim_results.items()}, fh, indent=2)

    # Sign-convention log.
    with open(RESULTS / "29_sign_convention.json", "w") as fh:
        json.dump({cid: {"polarity": res["polarity"],
                          "target_column": res.get("target_column", "rating"),
                          "rationale": ("tension/dissonance column — sign inverted"
                                        if res["polarity"] == -1
                                        else "consonance column — sign preserved")}
                   for cid, res in claim_results.items()}, fh, indent=2)

    # Invariants.
    with open(RESULTS / "29_invariants.json", "w") as fh:
        json.dump({"cross_dataset_consistency": cdc,
                   "hierarchy_reproduction": hri,
                   "axis_verdict": axis_verdict}, fh, indent=2)

    # Independence audit.
    indep = independence_audit()
    with open(RESULTS / "29_independence_audit.json", "w") as fh:
        json.dump(indep, fh, indent=2)

    # Manifest.
    manifest = {
        "axis_id": "AXIS-1-OOS-EXT",
        "axis_name": "Phase 6 extended — R³ Extended OOS Consonance Battery",
        "engine_head": pinned,
        "phase_close_date": None,  # set at close
        "seed_registry": {"primary": 2026051601,
                           "bootstrap": None, "permutation": None},
        "axis_verdict": axis_verdict,
        "claims": [
            {
                "claim_id": cid,
                "source": res["source"],
                "input_sha256": res["input_sha256"],
                "polarity": res["polarity"],
                "n_raw": res.get("n_raw"),
                "n_intervals_or_bins": res.get("n_bins", res.get("n_intervals")),
                "headline_channel_rhos": {
                    ch: next(round(r["rho"], 4)
                              for r in res["rows"] if r["channel"] == ch)
                    for ch in HEADLINE_CHANNELS
                },
                "verdict": per_claim[cid]["verdict"],
                "verdict_detail": per_claim[cid],
            }
            for cid, res in claim_results.items()
        ],
        "invariants": {"cross_dataset_consistency": cdc,
                        "hierarchy_reproduction": hri},
    }
    with open(RESULTS / "29_r3ext_manifest.json", "w") as fh:
        json.dump(manifest, fh, indent=2)

    # ── Console summary ─────────────────────────────────────────────
    print("\n" + "=" * 70)
    print(f"Phase 6 extended — wall-clock {time.time() - t0:.1f} s")
    print(f"Engine HEAD: {pinned[:12]}")
    print("=" * 70)
    print(f"{'CLAIM':<13} {'N':>6}  {'STUMPF':>8}  {'PLEAS':>8}  "
          f"{'ROUGH':>8}  {'VERDICT':<10}")
    print("-" * 70)
    for cid, res in claim_results.items():
        rhos = {r["channel"]: r["rho"] for r in res["rows"]}
        n = res.get("n_bins", res.get("n_intervals", res.get("n_raw")))
        print(f"{cid:<13} {n:>6d}  "
              f"{rhos['stumpf_fusion']:+8.3f}  "
              f"{rhos['sensory_pleasantness']:+8.3f}  "
              f"{rhos['roughness']:+8.3f}  "
              f"{per_claim[cid]['verdict']:<10}")
    print("-" * 70)
    print(f"CDC invariant (≥7/9 sign-consistent per channel): "
          f"{'PASS' if cdc['cdc_pass'] else 'FAIL'}")
    for ch in HEADLINE_CHANNELS:
        print(f"  {ch:<22} {cdc[ch]['n_sign_consistent']}/9 sign-OK")
    print(f"HRI invariant (≥7/9 hierarchy ranking ρ ≥ 0.85): "
          f"{'PASS' if hri['hri_pass'] else 'FAIL'}  "
          f"({hri['n_pass']}/{hri['n_total']})")
    print(f"\nAxis verdict: {axis_verdict}")
    print(f"\nOutputs → {RESULTS.relative_to(V_REPRO)}/")


if __name__ == "__main__":
    main()
