"""Engine cache helpers — load per-frame npz, extract channel trajectories.

Channel naming: "MECH_<CLASS>__<DIM_LABEL>" e.g. "MECH_MMP__P2:familiarity"

Dim ordering is determined dynamically from pooled.csv at each dataset's cache
root. The pooled column order matches the per-frame mech_<CLS> dim axis exactly
(engine guarantee).
"""
from __future__ import annotations

from pathlib import Path
from functools import lru_cache
from typing import Dict, List

import numpy as np
import pandas as pd


def parse_channel_name(channel: str) -> tuple[str, str]:
    """`MECH_MMP__P2:familiarity` → ('MMP', 'P2:familiarity')."""
    if not channel.startswith("MECH_"):
        raise ValueError(f"Not a MECH channel: {channel}")
    rest = channel[len("MECH_"):]
    cls, dim_label = rest.split("__", 1)
    return cls, dim_label


@lru_cache(maxsize=32)
def _load_pooled_cols(pooled_csv: Path) -> tuple:
    """Cache pooled.csv columns (immutable per dataset cache)."""
    return tuple(pd.read_csv(pooled_csv, nrows=1).columns.tolist())


def route(channel: str, pooled_csv: Path) -> tuple[str, int]:
    """Resolve channel → (mech_class_key, dim_idx) by inspecting pooled.csv.

    Matches the routing logic of TC003-TC007 (`route()` in those scripts).
    """
    pooled_cols = _load_pooled_cols(pooled_csv)
    cls, _ = parse_channel_name(channel)
    class_cols = [c for c in pooled_cols if c.startswith(f"MECH_{cls}__")]
    if not class_cols:
        raise KeyError(f"No pooled columns for class {cls}")
    if channel not in class_cols:
        raise KeyError(f"Channel {channel} not in pooled cols for {cls}; got {class_cols}")
    return f"mech_{cls}", class_cols.index(channel)


def zscore_clip(sig: np.ndarray) -> np.ndarray:
    """Z-score a signal within-clip (matches TC003-TC007 zscore_clip)."""
    s = sig.astype(np.float64)
    sd = s.std()
    if sd < 1e-8:
        return np.zeros_like(s)
    return (s - s.mean()) / sd


def load_channel(npz_path: Path, channel: str, pooled_csv: Path = None) -> np.ndarray:
    """Load a single channel's frame trajectory from per_frame .npz.

    If pooled_csv is provided, use dynamic routing (recommended).
    The signal is z-scored within-clip (matches TC003-TC007).
    """
    if pooled_csv is None:
        # Infer pooled.csv from npz_path: per_frame/<clip>.npz → ../pooled.csv
        pooled_csv = npz_path.parent.parent / "pooled.csv"
        if not pooled_csv.exists():
            raise FileNotFoundError(
                f"Cannot infer pooled.csv from {npz_path}; pass pooled_csv explicitly."
            )
    grp, idx = route(channel, pooled_csv)
    z = np.load(npz_path, allow_pickle=True)
    if grp not in z.files:
        raise KeyError(f".npz {npz_path.name} missing key: {grp}")
    sig = z[grp][:, idx].astype(np.float64)
    return zscore_clip(sig)


# Canonical 22-channel chill-relevant cluster (from TC003-TC007)
CHILL_CHANNELS_22 = (
    "MECH_AAC__P0:current_intensity",
    "MECH_AAC__I0:chills_intensity",
    "MECH_AAC__I1:ans_composite",
    "MECH_AAC__F0:scr_pred_1s",
    "MECH_AAC__F1:hr_pred_2s",
    "MECH_AAC__E0:emotional_arousal",
    "MECH_AAC__E1:ans_response",
    "MECH_AAC__P1:driving_signal",
    "MECH_AAC__P2:perceptual_arousal",
    "MECH_DAED__f01:anticipatory_da",
    "MECH_DAED__f02:consummatory_da",
    "MECH_DAED__f03:wanting_index",
    "MECH_DAED__f04:liking_index",
    "MECH_SSRI__P1:endorphin_proxy",
    "MECH_MMP__P2:familiarity",
    "MECH_SRP__M0:harmonic_tension",
    "MECH_SRP__M2:peak_detection",
    "MECH_SRP__P2:pleasure",
    "MECH_BCH__P0:consonance_signal",
    "MECH_PUPF__P0:surprise_pleasure",
    "MECH_UDP__M1:pleasure_index",
    "MECH_MORMR__f02:chills_count",
)
