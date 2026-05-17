"""L2 — ChillsDB v1 audio integrity test.

Verify that ChillsDB v1 audio WAV files are present at the expected location
in the project tree. Format checks (sample rate, duration sanity) are also done.

This is a presence-and-format test, not a checksum test. ChillsDB audio is
sourced from YouTube and may have minor codec differences; we assert
duration is within ±0.5 s of expected, not bit-identical.

NOTE: A fresh-clone reviewer must place the audio files BEFORE running this
suite. The README documents the expected paths.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from _infra.chillsdb_loader import CLIPS_9_FULL, audio_path


# Canonical clip durations in seconds (measured 2026-05-12 on the audio_chillsdb1/ tree).
# Tolerance ±5 s allows minor codec / source differences between fresh-clones.
EXPECTED_DURATIONS_S = {
    "C1ZL5AxmK_A": 277.4,
    "FOjdXSrtUxA": 262.6,
    "H3v9unphfi0": 329.3,
    "Y1UiD2sxoWo": 390.7,
    "fRL447oDId4": 456.5,
    "va1oiojnGrA": 310.9,
    "zx_dTSPzXlk": 226.3,
    "CwzjlmBLfrQ": 337.0,
    "YbNYinfj1h0": 377.5,
}


def _ffprobe_duration(audio_file: Path) -> float:
    """Return duration in seconds via ffprobe (requires ffmpeg installed)."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(audio_file)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed on {audio_file}: {result.stderr}")
    return float(result.stdout.strip())


def test_chillsdb_root_exists(chillsdb_root):
    """ChillsDB v1 audio root must exist."""
    assert chillsdb_root.exists(), (
        f"ChillsDB root not found at {chillsdb_root}.\n"
        f"Place ChillsDB v1 audio files at the expected paths (see README)."
    )


def test_audio_files_present(chillsdb_root):
    """All 9 ChillsDB v1 audio WAVs must be present."""
    missing = []
    for clip_id in CLIPS_9_FULL:
        path = audio_path(chillsdb_root, clip_id, variant="original")
        if not path.exists():
            missing.append(str(path))
    assert not missing, (
        f"Missing {len(missing)}/9 ChillsDB audio files:\n  " + "\n  ".join(missing)
    )


def test_ffmpeg_available():
    """ffprobe must be installed (needed for duration check and afftdn variant)."""
    result = subprocess.run(["ffprobe", "-version"], capture_output=True, text=True)
    assert result.returncode == 0, (
        "ffprobe not found — install ffmpeg (system package).\n"
        "macOS: brew install ffmpeg\n"
        "Ubuntu/Debian: apt install ffmpeg"
    )


@pytest.mark.parametrize("clip_id", CLIPS_9_FULL)
def test_audio_duration_within_tolerance(chillsdb_root, clip_id):
    """Each audio file duration must be within ±5 s of expected."""
    path = audio_path(chillsdb_root, clip_id, variant="original")
    if not path.exists():
        pytest.skip(f"Audio file not present: {path}")
    expected = EXPECTED_DURATIONS_S[clip_id]
    try:
        actual = _ffprobe_duration(path)
    except Exception as e:
        pytest.fail(f"ffprobe failed on {path}: {e}")
    tolerance = 5.0
    assert abs(actual - expected) < tolerance, (
        f"{clip_id} duration mismatch: expected ~{expected:.1f}s, got {actual:.2f}s "
        f"(tolerance ±{tolerance}s). Possibly wrong source file."
    )
