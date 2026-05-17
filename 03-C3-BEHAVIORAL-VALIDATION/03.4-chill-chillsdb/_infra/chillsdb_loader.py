"""ChillsDB v1 loader — clips, events, audio path discovery.

The 9 clips of ChillsDB v1 + their participant button-press event timestamps.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd


CLIPS_9_FULL = [
    "C1ZL5AxmK_A",  # Lakme Flower Duet
    "FOjdXSrtUxA",  # Inception Time
    "H3v9unphfi0",  # Miserere
    "Y1UiD2sxoWo",  # Ed Sheeran
    "fRL447oDId4",  # Lana Del Rey
    "va1oiojnGrA",  # Gladiator Now We Are Free
    "zx_dTSPzXlk",  # Agnus Dei
    "CwzjlmBLfrQ",  # Mr. Bean (excluded from 7-clean)
    "YbNYinfj1h0",  # Vocal Intros compilation (excluded from 7-clean)
]

CLIPS_EXCLUDED_FROM_7CLEAN = {"CwzjlmBLfrQ", "YbNYinfj1h0"}
CLIPS_7_CLEAN = [c for c in CLIPS_9_FULL if c not in CLIPS_EXCLUDED_FROM_7CLEAN]


def audio_path(chillsdb_root: Path, clip_id: str, variant: str = "original") -> Path:
    """Resolve audio file path for a clip × audio variant.

    Layout (canonical ChillsDB v1 in this repo):
      original     → audio_chillsdb1/<clip>.wav
      afftdn       → audio_chillsdb1_denoised/<clip>.wav  (ffmpeg afftdn nr=12)
      noisereduce  → audio_chillsdb1_noisereduce/<clip>.wav
    """
    if variant == "original":
        return chillsdb_root / "audio_chillsdb1" / f"{clip_id}.wav"
    elif variant == "afftdn":
        return chillsdb_root / "audio_chillsdb1_denoised" / f"{clip_id}.wav"
    elif variant == "noisereduce":
        return chillsdb_root / "audio_chillsdb1_noisereduce" / f"{clip_id}.wav"
    else:
        raise ValueError(f"Unknown audio variant: {variant}")


def load_events(chillsdb_root: Path, clip_id: str) -> List[float]:
    """Return list of chill-event timestamps (seconds) for a clip.

    Reads from music_stimuli.csv. Columns:
      - "Video ID"       — YouTube video ID matching audio file stem
      - "chills Binary"  — 1 if participant reported chill events for this stimulus
      - "Timings"        — comma-separated timestamps (seconds)
    """
    music_csv = chillsdb_root / "music_stimuli.csv"
    if not music_csv.exists():
        raise FileNotFoundError(
            f"ChillsDB music_stimuli.csv not found at {music_csv}\n"
            f"Required columns: 'Video ID', 'chills Binary', 'Timings'"
        )
    df = pd.read_csv(music_csv)
    if "Video ID" not in df.columns:
        raise ValueError(f"music_stimuli.csv missing 'Video ID' column; got: {df.columns.tolist()}")

    subset = df[df["Video ID"] == clip_id]
    events: List[float] = []
    for _, row in subset.iterrows():
        # Only include rows marked as chill-reporting
        if "chills Binary" in row and int(row["chills Binary"]) != 1:
            continue
        raw = row.get("Timings", "")
        if pd.isna(raw):
            continue
        s = str(raw).strip()
        if not s or s == "nan":
            continue
        for tok in s.split(","):
            tok = tok.strip()
            if not tok or tok == "nan":
                continue
            try:
                events.append(float(tok))
            except ValueError:
                pass
    return sorted(events)


def load_events_per_clip(chillsdb_root: Path, clips: List[str]) -> Dict[str, List[float]]:
    """Return {clip_id: [event_timestamps]} for the requested clips."""
    return {c: load_events(chillsdb_root, c) for c in clips}


def list_audio_files(chillsdb_root: Path, variant: str = "original") -> Dict[str, Path]:
    """Return {clip_id: audio_path} for all 9 ChillsDB v1 clips."""
    return {c: audio_path(chillsdb_root, c, variant) for c in CLIPS_9_FULL}
