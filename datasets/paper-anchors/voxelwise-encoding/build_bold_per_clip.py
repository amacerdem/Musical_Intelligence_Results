#!/usr/bin/env python3
"""
build_bold_per_clip.py — align Zenodo BOLD to per-clip feature index.

KEY FINDING (2026-04-24): Zenodo Training[r*400:(r+1)*400] covers WAV
Run{r+1}_01..40 in DIRECT filename-position order. Events.tsv row 0 is a
warm-up attention trial (NOT part of the 40 WAVs) which was dropped from
the Zenodo preproc, leaving 400 TRs/run = 40 clips × 10 TRs/clip at TR=1.5s.

Therefore we do NOT parse events.tsv — we use the canonical WAV sequence
from MI meta.json directly.

Training: 12 runs × 40 WAVs = 480 clips @ 4800 TRs
Test_Mean: 6 runs × 40 WAVs = 240 clips — BUT Test_Mean is (n_vox, 600 TRs)
           = 60 clips (not 240). Per Nakai convention, each Test run's 40
           clips are 10 UNIQUE × 4 repeats; Test_Mean averages across the 4
           repeats. So Test_Mean covers 60 unique clips × 10 TRs = 600 TRs.

For first-pass we use Test_Mean (higher SNR) — 60 clips, matched to WAV
positions 1..10 within each Test run (the "unique set" of that run).

Outputs: {subj}_bold_per_clip.npy (N_clips_used, n_voxels)
         {subj}_clip_indices.npy  (N_clips_used,) into canonical 720 order
         {subj}_bold_meta.json
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np

SEED = 20260424
BASE = Path("<PAPER_TIME_SCIENCE_ROOT>/Science/Bold-fMRI")
DS = BASE / "ds003720"
OUT = DS / "04_roi_extraction"
OUT.mkdir(parents=True, exist_ok=True)

ZEN = BASE / "cycle-17-ds003720" / "preproc_zenodo"
FEAT = DS / "05_features"

TR = 1.5
CLIP_S = 15.0
TRS_PER_CLIP = 10
HRF_LAG_TR = 4
POOL_WIN_TR = 4

SUBJECTS = ["sub-005"]  # sub-001/003/004 already built; adding sub-005 now


def pool_run(run_bold: np.ndarray) -> np.ndarray:
    """(n_vox, 400 or 600 TRs) → (n_clips, n_vox) with HRF-lagged mean window."""
    nvox, ntr = run_bold.shape
    assert ntr % TRS_PER_CLIP == 0, ntr
    n_clips = ntr // TRS_PER_CLIP
    out = np.zeros((n_clips, nvox), dtype=np.float32)
    for c in range(n_clips):
        s = c * TRS_PER_CLIP + HRF_LAG_TR
        e = min(s + POOL_WIN_TR, ntr)
        if s < ntr:
            out[c] = run_bold[:, s:e].mean(axis=1)
        else:
            out[c] = run_bold[:, -POOL_WIN_TR:].mean(axis=1)
    return out


def main():
    clip_order = json.loads((FEAT / "clip_order.json").read_text())
    id_to_idx = {cid: i for i, cid in enumerate(clip_order)}
    assert len(id_to_idx) == 720

    # Build Training WAV sequence (filename order): Run01_01..Run01_40, Run02_01..Run02_40, ..., Run12_40
    training_ids: list[str] = []
    for run in range(1, 13):
        # All 40 WAV positions in this run — find them in clip_order
        for pos in range(1, 41):
            # Match by prefix
            prefix = f"Stim_Training_Run{run:02d}_{pos:02d}_"
            matches = [c for c in clip_order if c.startswith(prefix)]
            assert len(matches) == 1, f"{prefix}: {matches}"
            training_ids.append(matches[0])
    assert len(training_ids) == 480

    # Test_Mean: 60 unique clips per subject, ordered as WAV positions 01..10 of Test Run 01..06
    # (Nakai: each Test run has 40 clips = 10 unique × 4 repeats; Test_Mean averages the 4)
    test_mean_ids: list[str] = []
    for run in range(1, 7):
        for pos in range(1, 11):
            prefix = f"Stim_Test_Run{run:02d}_{pos:02d}_"
            matches = [c for c in clip_order if c.startswith(prefix)]
            assert len(matches) == 1, f"{prefix}: {matches}"
            test_mean_ids.append(matches[0])
    assert len(test_mean_ids) == 60

    for subj in SUBJECTS:
        print(f"\n[bold] {subj}", flush=True)
        # Training
        tr_bold = np.load(ZEN / f"{subj}_Resp_Training.npy", mmap_mode="r")
        tr_bold = np.asarray(tr_bold, dtype=np.float32)
        print(f"  training BOLD: {tr_bold.shape}")
        assert tr_bold.shape[1] == 4800
        tr_pooled = pool_run(tr_bold)
        print(f"  training pooled: {tr_pooled.shape} → matching {len(training_ids)} clip ids")
        assert tr_pooled.shape[0] == len(training_ids)

        # Test_Mean
        tm = np.load(ZEN / f"{subj}_Resp_Test_Mean.npy", mmap_mode="r")
        tm = np.asarray(tm, dtype=np.float32)
        print(f"  test_mean BOLD: {tm.shape}")
        assert tm.shape[1] == 600
        tm_pooled = pool_run(tm)
        print(f"  test_mean pooled: {tm_pooled.shape} → matching {len(test_mean_ids)} clip ids")
        assert tm_pooled.shape[0] == len(test_mean_ids)

        # Combine into a dict keyed by canonical clip index
        seen: dict[int, np.ndarray] = {}
        for cid, row in zip(test_mean_ids, tm_pooled):
            seen[id_to_idx[cid]] = row  # Test_Mean preferred (higher SNR)
        for cid, row in zip(training_ids, tr_pooled):
            if id_to_idx[cid] not in seen:
                seen[id_to_idx[cid]] = row

        idxs = sorted(seen.keys())
        bold = np.stack([seen[i] for i in idxs], axis=0).astype(np.float32)
        idxs_arr = np.asarray(idxs, dtype=np.int32)
        print(f"  final: bold={bold.shape} clip_indices={idxs_arr.shape}")

        np.save(OUT / f"{subj}_bold_per_clip.npy", bold)
        np.save(OUT / f"{subj}_clip_indices.npy", idxs_arr)
        meta = {
            "subject": subj,
            "n_voxels": int(bold.shape[1]),
            "n_clips_used": int(bold.shape[0]),
            "n_from_test_mean": int(len(test_mean_ids)),
            "n_from_training": int(bold.shape[0] - len(test_mean_ids)),
            "hrf_lag_tr": HRF_LAG_TR,
            "pool_win_tr": POOL_WIN_TR,
            "tr_s": TR,
            "clip_s": CLIP_S,
            "seed": SEED,
            "methodology_note": "Zenodo Training/Test_Mean assumed to be in WAV-filename order (Run-pos). Event_row 0 = warm-up dropped.",
        }
        (OUT / f"{subj}_bold_meta.json").write_text(json.dumps(meta, indent=2))
        print(f"  saved {subj}_bold_per_clip.npy")


if __name__ == "__main__":
    main()
