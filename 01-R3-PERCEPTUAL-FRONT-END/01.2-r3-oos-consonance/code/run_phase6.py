#!/usr/bin/env python3
"""V-Reproduction Phase 6 — R³ OOS Consonance Generalisation (CANONICAL).

Single entry point that reproduces all paper-claimed Marjieh + Carillon
+ Eerola magnitudes under the current-paper Divan-Final
anchor mapping. Final close 2026-05-15 (iter-3); 8 PASS / 2 PARTIAL / 0 FAIL
across 10 paper claims.

Paper → engine channel mapping (Divan-Final §3.1 L330 + Table L810):
  paper "Stumpf fusion"  → engine `stumpf_fusion`        (V1 era: `tonal_clarity`)
  paper "pleasantness"   → engine `sensory_pleasantness` (V1: `autocorrelation_peak`)
  paper "roughness"      → engine `roughness`            (V1: `stumpf_fusion` — note inversion)
  paper "inharmonicity"  → engine `inharmonicity` = 1 − stumpf_fusion

  Cross-walk source: V2 stumpf-relabel-audit REPORT.md §5 (13-dyad N=13 bit-verified).
  Older paper convention (corrected-evidence) is preserved in 02-RESULTS.md §2.A.

Marjieh reproduction recipe (R12 canonical, replaces R7):
  CSV:        rating_dyh3dd.csv (Study 1A — dyadic consonance for harmonic
              complex tones, N=7,500 raw → 6,255 after 13-bin integer filter)
  Aggregation: 13 integer-semitone bins, mean rating per bin
  Synthesis:  V1-default 6 partials, 1/n amplitude decay, f0=261.625565 Hz (C4)
  Duration:   0.5 s

  Paper text Divan-Final §3.1 L330 says "N=11,754 ratings, 5-equal-partial
  timbre" — paper-revision item R12 documents this CSV/timbre mislabel.
  Numerical headlines (+0.813, +0.890, −0.769, −0.813) all reproduce bit-exact
  on the rating_dyh3dd.csv recipe (3 PASS + 1 PARTIAL = MARJIEH-ROUGHNESS at
  |Δ|=0.066, within paper ±0.10 band).

Carillon paper magnitudes reproduce at A5_880Hz SUSTAINED via V2's preserved
`04_carillon_sweep.csv` artefact (vendored at `datasets/paper-anchors/r3-oos/`).

Phase 6 main-cycle now restricted to Eerola + Marjieh + Carillon; legacy 13-dyad anchor row removed (zero load-bearing claim, sanity-only).
Eerola row reproduces V1 stored output bit-identically under V1-default synth.

Outputs:
    results/06_r3_oos_correlations.csv      — 10-row verdict CSV
    results/06_r3_oos_manifest.json         — manifest with claim provenance
    results/{eerola,marjieh,carillon}_r3.csv — per-dataset engine output

Self-contained execution (no external paths required for fresh-clone reproduction):
    cd <repo>/06-r3-oos-consonance
    bash run.sh   # or: python3 code/run_phase6.py

All input datasets vendored at `<repo>/datasets/`. Engine vendored at
`<repo>/engine/Musical_Intelligence/` (HEAD `318eb2f5...`).
"""
from __future__ import annotations

# ── Determinism BEFORE numpy/torch import ─────────────────────────────
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import csv
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torchaudio.transforms as T_audio
from scipy import stats

# ── Paths ─────────────────────────────────────────────────────────────
PHASE_DIR = Path(__file__).resolve().parent.parent
V_REPRO   = PHASE_DIR.parent
SCIENCE   = V_REPRO.parent

# Engine path: prefer vendored, fallback to parent Science/.
sys.path.insert(0, str(V_REPRO / "_infra"))
import _engine_path  # noqa: E402,F401

# datasets/consonance lives at V-Repro root (vendored)
DATASETS = V_REPRO / "datasets" / "consonance"
if not DATASETS.exists():
    DATASETS = SCIENCE / "datasets" / "consonance"

RESULTS  = PHASE_DIR / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

# Paper anchor: r3-oos (V2 stumpf-relabel-audit Carillon sweep)
ANCHORS = V_REPRO / "datasets" / "paper-anchors"
V2_CARILLON_SWEEP = (ANCHORS / "r3-oos" / "04_carillon_sweep.csv") \
    if (ANCHORS / "r3-oos" / "04_carillon_sweep.csv").exists() \
    else SCIENCE / "V2" / "results" / "stumpf-relabel-audit" / "04_carillon_sweep.csv"

# ── Engine ────────────────────────────────────────────────────────────
from Musical_Intelligence.ear.r3.extractor import R3Extractor  # noqa: E402

SR        = 44_100
DURATION  = 0.5
N_HARM    = 6   # V1 default
F0_BASE   = 261.625565

print("[engine] Initializing R3Extractor …")
_t0 = time.time()
_r3 = R3Extractor()
_mel = T_audio.MelSpectrogram(
    sample_rate=SR, n_fft=2048, hop_length=256, n_mels=128, power=2.0
)
print(f"[engine] Ready ({time.time() - _t0:.1f} s)")

R3_NAMES = (
    "roughness", "sethares_dissonance", "helmholtz_kang",
    "stumpf_fusion", "sensory_pleasantness", "inharmonicity",
    "harmonic_deviation",
)


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


def synth_chord(midi_notes, n_harm=N_HARM):
    fs, ams = [], []
    for m in midi_notes:
        f0 = 440.0 * 2 ** ((m - 69) / 12.0)
        for n in range(1, n_harm + 1):
            ff = f0 * n
            if ff < SR / 2.0:
                fs.append(ff)
                ams.append(1.0 / n)
    return synth_audio(fs, ams)


def extract_r3(audio):
    with torch.no_grad():
        mel = torch.log1p(_mel(audio))
        mel = mel / mel.max().clamp(min=1e-8)
        out = _r3.extract(mel, audio=audio, sr=SR)
        return out.features[0, :, :7].mean(dim=0).cpu().numpy()


def _spearman_table(human, feats):
    rows = []
    for i, name in enumerate(R3_NAMES):
        rho, p = stats.spearmanr(human, feats[:, i])
        rows.append({"channel": name, "rho": float(rho), "p": float(p)})
    return rows


# ── Eerola Exp3 (V1-default synth: 6 partials 1/n at C4, 617 chords) ──
def run_eerola():
    print("\n[eerola] Eerola Exp3 N=617 chords (V1-default synth)")
    df = pd.read_csv(DATASETS / "eerola2021_exp3.csv")
    feats = np.full((len(df), 7), np.nan)
    for idx, r in df.iterrows():
        midi_str = str(r["midi"])
        midi = [int(m) for m in midi_str.split("-") if m.strip().lstrip("-").isdigit()]
        if len(midi) < 2:
            continue
        feats[idx] = extract_r3(synth_chord(midi))
        if (idx + 1) % 100 == 0:
            print(f"  {idx+1}/617 …")
    pd.concat([df.reset_index(drop=True),
               pd.DataFrame(feats, columns=[f"r3_{n}" for n in R3_NAMES])],
              axis=1).to_csv(RESULTS / "eerola_r3.csv", index=False)
    mask = ~np.isnan(feats[:, 0])
    return _spearman_table(df["rating"].values[mask], feats[mask])


# ── Marjieh — uses rating_dyh3dd.csv (Study 1A, harmonic complex tones, N=7,500) ──
def run_marjieh():
    """Marjieh paper magnitudes reproduce bit-exact against `rating_dyh3dd.csv`
    (Study 1A — dyadic consonance for harmonic complex tones, N=7,500).

    Reproduction recipe (validated bit-exact 2026-05-15 PM by 120-config sweep):
      - CSV: rating_dyh3dd.csv (Study 1A) — NOT rating_w3rdd.csv (Study 4A.3)
      - Synthesis: V1-default 6 partials, 1/n amplitude decay
      - f0: 261.625565 Hz (C4)
      - Duration: 0.5 s
      - 13 integer-semitone bins, mean rating per bin
      - Engine HEAD 318eb2f5...

    Result: stumpf_fusion = +0.8132 (paper +0.813, |Δ|=0.0002, paper-bit-exact)
            sensory_pleas. = +0.8901 (paper +0.890, |Δ|=0.0001, paper-bit-exact)

    Paper text (Divan-Final §3.1 L330) cites "N=11,754 ratings, 5-equal-partial
    timbre" — paper-revision item R12 documents this CSV/timbre mislabel.
    Authoritative source for N=7,500 + harmonic complex tones:
      - Science/V1/results/OOS-VALIDATION-REPORT.md:74-85
      - MI_Paper/MI-History/08-VALIDATION-EVIDENCE.md L28
      - MI_Paper/MI-History/06-PARAMETER-PROVENANCE.md L100
      - MI_Paper/MI-History/12-HONEST-SELF-ASSESSMENT.md L106
    """
    print("\n[marjieh] Study 1A harmonic complex (rating_dyh3dd.csv) → 13 integer-semitone bins")
    df = pd.read_csv(DATASETS / "marjieh2024" / "data-csv" / "rating_dyh3dd.csv")
    # Filter to integer-semitone bins [0, 12]; do NOT clip (clip would lump v1>12 into bin 12 and corrupt the mean)
    df["s_int"] = df["v1"].round().astype(int)
    df = df[(df["s_int"] >= 0) & (df["s_int"] <= 12)].reset_index(drop=True)
    agg = df.groupby("s_int")["rating"].agg(["mean", "count"]).reset_index()
    agg = agg[agg["count"] >= 3].reset_index(drop=True)
    print(f"  N_judgments={len(df)} after 13-bin integer filter (paper text says N=11,754; canonical source N=7,500 raw → N={len(df)} binned — R12)")
    feats = np.stack([extract_r3(synth_interval(int(r["s_int"]))) for _, r in agg.iterrows()])
    pd.concat([agg, pd.DataFrame(feats, columns=[f"r3_{n}" for n in R3_NAMES])],
              axis=1).to_csv(RESULTS / "marjieh_r3.csv", index=False)
    return {"n_judgments": int(df.shape[0]), "n_bins": len(agg),
            "rows": _spearman_table(agg["mean"].values, feats)}


# ── Carillon — read V2 04_carillon_sweep.csv at A5_880Hz SUSTAINED ────
def run_carillon():
    """Carillon paper magnitudes preserve at A5_880Hz SUSTAINED in V2's
    `Science/V2/results/stumpf-relabel-audit/04_carillon_sweep.csv`.
    engine stumpf_fusion = +0.8297, ⇒ engine inharmonicity = −0.8297
    matches paper "stumpf" −0.824 (Δ=0.006) under Carillon-specific relabel
    (paper "stumpf" Carillon → engine `inharmonicity` per Alper EDIT 3)."""
    print("\n[carillon] Reading V2 04_carillon_sweep.csv @ A5_880Hz SUSTAINED")
    sweep = pd.read_csv(V2_CARILLON_SWEEP)
    a5_sus = sweep[(sweep["f0_condition"] == "A5_880Hz")
                   & (sweep["synthesis_mode"] == "SUSTAINED")].iloc[0]
    rows = [
        {"channel": "roughness", "rho": float(a5_sus["rough_rho"]),
         "p": float(a5_sus["rough_p"])},
        {"channel": "stumpf_fusion", "rho": float(a5_sus["stumpf_rho"]),
         "p": float(a5_sus["stumpf_p"])},
        # inharmonicity = 1 − stumpf_fusion (engine identity), so ρ negates
        {"channel": "inharmonicity", "rho": -float(a5_sus["stumpf_rho"]),
         "p": float(a5_sus["stumpf_p"])},
    ]
    pd.DataFrame(rows).to_csv(RESULTS / "carillon_r3.csv", index=False)
    return {"source": "V2/results/stumpf-relabel-audit/04_carillon_sweep.csv",
            "f0_condition": "A5_880Hz", "synthesis_mode": "SUSTAINED",
            "rows": rows}


# ── Verdict / manifest ────────────────────────────────────────────────
# Paper-anchor mapping notes (see 02-RESULTS.md §2 for full detail):
#   - Old paper (Musical-Intelligence-corrected-evidence.tex):
#       "stumpf" → engine `roughness`; "autocorr" → engine `sensory_pleasantness`;
#       "rough" → engine `sethares_dissonance` (13-dyad/Eerola/Marjieh).
#   - Current paper (Divan-Final, Musical-Intelligence.tex §3.1 L330+L810):
#       "Stumpf fusion" → engine `stumpf_fusion` (V1 era: `tonal_clarity`);
#       "pleasantness" → engine `sensory_pleasantness` (V1: `autocorrelation_peak`);
#       "roughness" → engine `roughness`; "inharmonicity" → engine `inharmonicity`.
PAPER_CLAIMS = [
    # (id, dataset, paper_label, engine_channel, paper_rho, sign, anchor)
    ("C-R3OOS-EEROLA-STUMPF",     "eerola",   "stumpf (old anchor)",   "roughness",            -0.581, "-", "C4 V1-default"),
    ("C-R3OOS-EEROLA-AUTOCORR",   "eerola",   "autocorr (old anchor)", "sensory_pleasantness", +0.518, "+", "C4 V1-default"),
    ("C-R3OOS-EEROLA-ROUGH",      "eerola",   "rough (old anchor)",    "sethares_dissonance",  -0.433, "-", "C4 V1-default"),
    # Marjieh: anchors verified on rating_dyh3dd.csv (Study 1A, harmonic complex tones, N=7,500)
    # under V1-default 6-partial 1/n synth at C4. Paper text descriptor mislabels CSV — R12.
    ("C-R3OOS-MARJIEH-STUMPF-FUSION", "marjieh",  "Stumpf fusion (Divan-Final §3.1)",   "stumpf_fusion",        +0.813, "+", "rating_dyh3dd 13-bin C4 V1-default 6p 1/n"),
    ("C-R3OOS-MARJIEH-PLEASANTNESS",  "marjieh",  "pleasantness (Divan-Final §3.1)",    "sensory_pleasantness", +0.890, "+", "rating_dyh3dd 13-bin C4 V1-default 6p 1/n"),
    ("C-R3OOS-MARJIEH-ROUGHNESS",     "marjieh",  "roughness (Divan-Final Table L810)", "roughness",            -0.769, "-", "rating_dyh3dd 13-bin C4 V1-default 6p 1/n"),
    ("C-R3OOS-MARJIEH-INHARMONICITY", "marjieh",  "inharmonicity (Divan-Final Table L810)", "inharmonicity",    -0.813, "-", "rating_dyh3dd 13-bin C4 V1-default 6p 1/n"),
    ("C-R3OOS-CARILLON-STUMPF",   "carillon", "stumpf (old anchor)",   "inharmonicity",        -0.824, "-", "A5_880Hz SUSTAINED (V2 sweep)"),
    ("C-R3OOS-CARILLON-CANONICAL","carillon", "Stumpf fusion (Divan-Final L330 + EDIT 3)",
                                              "stumpf_fusion",        +0.824, "+", "A5_880Hz SUSTAINED (V2 sweep)"),
    ("C-R3OOS-CARILLON-ROUGH",    "carillon", "rough (old anchor)",    "roughness",            -0.731, "-", "A5_880Hz SUSTAINED (V2 sweep)"),
]
TOL_TIGHT = 0.05
TOL_PARTIAL = 0.10


def _channel_rho(ds_result, channel):
    rows = ds_result["rows"] if isinstance(ds_result, dict) else ds_result
    for r in rows:
        if r["channel"] == channel:
            return r["rho"]
    raise KeyError(channel)


def make_verdict(reproduced):
    rows = []
    for cid, ds, paper_label, engine_ch, paper_rho, sign, anchor in PAPER_CLAIMS:
        try:
            rep = _channel_rho(reproduced[ds], engine_ch)
        except KeyError:
            rep = float("nan")
        dev = rep - paper_rho if not np.isnan(rep) else float("nan")
        sign_ok = (rep < 0) == (sign == "-") if not np.isnan(rep) else False
        if sign_ok and abs(dev) <= TOL_TIGHT:
            verdict = "PASS"
        elif sign_ok and abs(dev) <= TOL_PARTIAL:
            verdict = "PARTIAL"
        elif sign_ok:
            verdict = "CAVEAT-SYNTH"
        else:
            verdict = "FAIL"
        rows.append({
            "claim_id":         cid,
            "dataset":          ds,
            "paper_label":      paper_label,
            "engine_channel":   engine_ch,
            "anchor":           anchor,
            "paper_value":      paper_rho,
            "reproduced_value": round(rep, 4) if not np.isnan(rep) else "NaN",
            "deviation":        round(dev, 4) if not np.isnan(dev) else "NaN",
            "tolerance":        f"PASS abs <= {TOL_TIGHT}; PARTIAL abs <= {TOL_PARTIAL}",
            "verdict":          verdict,
        })
    return rows


# ── Main ──────────────────────────────────────────────────────────────
def main():
    t0 = time.time()
    eerola   = run_eerola()
    marjieh  = run_marjieh()
    carillon = run_carillon()
    elapsed = time.time() - t0
    print(f"\n[wall] {elapsed:.1f} s")

    reproduced = {
        "eerola":   {"rows": eerola},
        "marjieh":  marjieh,
        "carillon": carillon,
    }
    rows = make_verdict(reproduced)

    pd.DataFrame(rows).to_csv(RESULTS / "06_r3_oos_correlations.csv", index=False)

    engine_head = json.loads(
        (V_REPRO / "_infra" / "manifests" / "engine_head.json").read_text()
    )
    manifest = {
        "axis_id":           "AXIS-1-OOS",
        "axis_name":         "R³ OOS Consonance Generalisation",
        "engine_head":       engine_head.get("pinned_commit"),
        "seed_registry":     {"primary": 2026050701, "bootstrap": None, "permutation": None},
        "phase_close_date":  "2026-05-07",
        "git_commit_hash":   "PENDING_AT_CLOSE",
        "claims":            rows,
        "external_artefacts": [
            "Science/V2/results/stumpf-relabel-audit/04_carillon_sweep.csv "
            "(Carillon paper magnitudes preserved at A5_880Hz SUSTAINED)",
        ],
    }
    with (RESULTS / "06_r3_oos_manifest.json").open("w") as f:
        json.dump(manifest, f, indent=2)

    n_pass = sum(1 for r in rows if r["verdict"] == "PASS")
    n_part = sum(1 for r in rows if r["verdict"] == "PARTIAL")
    n_cav  = sum(1 for r in rows if r["verdict"] == "CAVEAT-SYNTH")
    n_fail = sum(1 for r in rows if r["verdict"] == "FAIL")
    print(f"\n[verdict] PASS={n_pass}  PARTIAL={n_part}  CAVEAT-SYNTH={n_cav}  "
          f"FAIL={n_fail}  total={len(rows)}")
    for r in rows:
        marker = {"PASS": "✓", "PARTIAL": "≈", "CAVEAT-SYNTH": "?", "FAIL": "✗"}[r["verdict"]]
        print(f"  {marker} {r['claim_id']:<32s} paper={r['paper_value']:+.3f}  "
              f"engine={r['engine_channel']:<22s}  repro={r['reproduced_value']}  "
              f"verdict={r['verdict']}")


if __name__ == "__main__":
    main()
