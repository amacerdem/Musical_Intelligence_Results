"""L3.2 — Cross-process determinism.

A fresh Python interpreter, fresh torch import, fresh extractor instance —
running on the same audio bytes — produces bit-identical output to the
in-process baseline. Pins R³ as truly stateless across interpreter
boundaries.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf
import torch

from _infra import stimuli as stim


WORKER_SCRIPT = """\
import sys, json, hashlib
sys.path.insert(0, {project_root!r})
sys.path.insert(0, {suite_root!r})
import torch
import soundfile as sf
import numpy as np
from Musical_Intelligence.ear.r3.extractor import R3Extractor
from _infra.stimuli import to_mel

audio_np, sr = sf.read({audio_path!r}, dtype='float32', always_2d=False)
audio = torch.from_numpy(audio_np).unsqueeze(0)
mel = to_mel(audio)
ex = R3Extractor()
with torch.no_grad():
    out = ex.extract(mel, audio=audio, sr=sr)
features = out.features.cpu().numpy().tobytes()
print(hashlib.sha256(features).hexdigest())
"""


def _project_root() -> Path:
    """Project root = parent of Musical_Intelligence/ tree."""
    p = Path(__file__).resolve()
    for _ in range(8):
        if (p / "Musical_Intelligence" / "ear" / "r3").exists():
            return p
        p = p.parent
    raise RuntimeError("could not locate project root")


def _suite_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _audio_sha(audio_path: Path) -> str:
    audio_np, sr = sf.read(str(audio_path), dtype='float32', always_2d=False)
    audio = torch.from_numpy(audio_np).unsqueeze(0)
    mel = stim.to_mel(audio)
    from Musical_Intelligence.ear.r3.extractor import R3Extractor
    ex = R3Extractor()
    with torch.no_grad():
        out = ex.extract(mel, audio=audio, sr=sr)
    import hashlib
    return hashlib.sha256(out.features.cpu().numpy().tobytes()).hexdigest()


def test_cross_process_run_bit_identical(tmp_path):
    """In-process SHA-256 of features = subprocess SHA-256 of features."""
    audio = stim.stim_mix(duration_s=2.0)
    wav_path = tmp_path / "probe.wav"
    sf.write(str(wav_path), audio[0].numpy(), 44100)

    in_proc_sha = _audio_sha(wav_path)

    script = WORKER_SCRIPT.format(
        project_root=str(_project_root()),
        suite_root=str(_suite_root()),
        audio_path=str(wav_path),
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, (
        f"subprocess failed: stdout={result.stdout!r}\nstderr={result.stderr!r}"
    )
    sub_proc_sha = result.stdout.strip()
    assert in_proc_sha == sub_proc_sha, (
        f"cross-process drift: in-proc {in_proc_sha} vs sub-proc {sub_proc_sha}"
    )


def test_two_subprocesses_bit_identical(tmp_path):
    """Two independent subprocesses also agree, ruling out any in-process
    fixture contamination effect."""
    audio = stim.stim_mix(duration_s=2.0)
    wav_path = tmp_path / "probe2.wav"
    sf.write(str(wav_path), audio[0].numpy(), 44100)
    script = WORKER_SCRIPT.format(
        project_root=str(_project_root()),
        suite_root=str(_suite_root()),
        audio_path=str(wav_path),
    )
    shas = []
    for _ in range(2):
        r = subprocess.run([sys.executable, "-c", script],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr
        shas.append(r.stdout.strip())
    assert shas[0] == shas[1], f"two subprocesses disagreed: {shas}"
