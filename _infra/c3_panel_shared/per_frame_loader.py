"""Per-frame npz loaders for Musical_Intelligence_Outputs/<category>/<dataset>/per_frame/.

Each per_frame/<clip_id>.npz contains:
  - r3 (T, 97)
  - ram (T, 26)
  - neuro (T, 4)        # order: DA, NE, OPI, 5HT
  - beliefs (T, 131)
  - mech_<CLASS> (T, dim)  # 84 unique mech classes

The pooled.csv MECH columns appear in the same order as the per-frame mech_<CLASS>
dim axis, so for a pooled column name `MECH_<CLASS>__<DIM>`, the per-frame index
is the position of that name within the list of pooled columns starting with
`MECH_<CLASS>__`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .load_outputs import emotify_paths, load_emotify_pooled


def parse_mech_pooled_col(col: str) -> tuple[str, str]:
    """`MECH_HTP__E2:low_level_lead` → ('HTP', 'E2:low_level_lead')."""
    if not col.startswith("MECH_"):
        raise ValueError(f"not a MECH column: {col}")
    rest = col[len("MECH_"):]
    cls, dim = rest.split("__", 1)
    return cls, dim


def build_mech_dim_index(pooled_columns: Iterable[str]) -> dict[str, tuple[str, int]]:
    """Return {pooled_col_name: (mech_class, dim_idx_within_class)}.

    Used to fetch a single mech-channel trajectory from per_frame/<clip>.npz.
    """
    mapping: dict[str, tuple[str, int]] = {}
    per_class: dict[str, list[str]] = {}
    for c in pooled_columns:
        if not c.startswith("MECH_"):
            continue
        cls, _ = parse_mech_pooled_col(c)
        per_class.setdefault(cls, []).append(c)
    for cls, cols in per_class.items():
        for idx, c in enumerate(cols):
            mapping[c] = (cls, idx)
    return mapping


def emotify_per_frame_path(clip_id: str) -> Path:
    return emotify_paths()["per_frame_dir"] / f"{clip_id}.npz"


def load_emotify_clip_npz(clip_id: str) -> dict[str, np.ndarray]:
    p = emotify_per_frame_path(clip_id)
    if not p.exists():
        raise FileNotFoundError(p)
    with np.load(p) as z:
        return {k: z[k] for k in z.files}


def perframe_clip_stats(clip_id: str,
                       mech_cols: list[str],
                       ram_indices: list[int] | None = None,
                       neuro_indices: list[int] | None = None,
                       mech_dim_index: dict[str, tuple[str, int]] | None = None) -> dict[str, float]:
    """Compute per-clip {std, range, max-mean, peak-count}-style summaries.

    Used by S13 / S5d / S6c. Returns a flat dict suitable for adding to a row.
    Memory: loads ONE npz at a time and immediately reduces to scalars; safe on
    M2-8GB across all 400 clips.
    """
    bundle = load_emotify_clip_npz(clip_id)
    out: dict[str, float] = {}
    T = bundle["r3"].shape[0]
    out["_n_frames"] = float(T)

    if mech_cols:
        if mech_dim_index is None:
            raise ValueError("mech_dim_index required when mech_cols passed")
        for col in mech_cols:
            cls, idx = mech_dim_index[col]
            key = f"mech_{cls}"
            arr = bundle[key][:, idx].astype(np.float64)
            out[f"std__{col}"] = float(arr.std(ddof=0))
            out[f"range__{col}"] = float(arr.max() - arr.min())
            out[f"peakdev__{col}"] = float(arr.max() - arr.mean())
            # event count: frames > mean + 2σ
            thr = arr.mean() + 2 * arr.std(ddof=0)
            out[f"peakn__{col}"] = float((arr > thr).sum())

    if ram_indices:
        ram = bundle["ram"].astype(np.float64)
        for idx in ram_indices:
            arr = ram[:, idx]
            out[f"std__RAM_{idx}"] = float(arr.std(ddof=0))
            out[f"range__RAM_{idx}"] = float(arr.max() - arr.min())
            out[f"peakdev__RAM_{idx}"] = float(arr.max() - arr.mean())

    if neuro_indices:
        neuro = bundle["neuro"].astype(np.float64)
        labels = ["DA", "NE", "OPI", "5HT"]
        for idx in neuro_indices:
            arr = neuro[:, idx]
            out[f"std__NEURO_{labels[idx]}"] = float(arr.std(ddof=0))
            out[f"range__NEURO_{labels[idx]}"] = float(arr.max() - arr.min())
            out[f"peakdev__NEURO_{labels[idx]}"] = float(arr.max() - arr.mean())

    return out


def perframe_batch_stats(clip_ids: Iterable[str], **kwargs) -> pd.DataFrame:
    rows = []
    for cid in clip_ids:
        stats = perframe_clip_stats(cid, **kwargs)
        stats["clip_id"] = cid
        rows.append(stats)
    df = pd.DataFrame(rows)
    cols = ["clip_id"] + [c for c in df.columns if c != "clip_id"]
    return df[cols]


if __name__ == "__main__":
    pooled = load_emotify_pooled()
    midx = build_mech_dim_index(pooled.columns)
    print(f"mech dim index built: {len(midx)} entries")
    test_col = "MECH_HTP__E2:low_level_lead"
    print(f"{test_col} → {midx[test_col]}")
    sample = perframe_clip_stats("classical_1",
                                 mech_cols=[test_col],
                                 ram_indices=[1, 13, 15],
                                 neuro_indices=[0, 1, 2, 3],
                                 mech_dim_index=midx)
    for k, v in sample.items():
        print(f"   {k:>40s} = {v}")
