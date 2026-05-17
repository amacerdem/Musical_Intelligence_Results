"""L11 — Anti-feature / hidden-state probes.

Engine claim: R³ has no hidden state, cache, global, time-, filename-, or
environment-dependence beyond declared inputs. This module pins the
**negative** claims by AST audit + behavioural probes.
"""
from __future__ import annotations

import os
import re
import socket
import time
from pathlib import Path

import numpy as np
import pytest
import torch

from _infra import stimuli as stim


def _engine_root() -> Path:
    p = Path(__file__).resolve()
    for _ in range(8):
        if (p / "Musical_Intelligence" / "ear" / "r3").exists():
            return p / "Musical_Intelligence" / "ear" / "r3"
        p = p.parent
    raise RuntimeError("engine root not found")


# ---------------------------------------------------------------------------
# L11.1 — No filename / file-path dependence
# ---------------------------------------------------------------------------

def test_no_filename_dependence(tmp_path, r3_extract):
    """Same audio bytes via two different filenames → bit-identical output."""
    import soundfile as sf
    audio = stim.stim_mix(duration_s=2.0)
    p1 = tmp_path / "alpha.wav"
    p2 = tmp_path / "beta_completely_different_name.wav"
    sf.write(str(p1), audio[0].numpy(), 44100)
    sf.write(str(p2), audio[0].numpy(), 44100)

    a1, _ = sf.read(str(p1), dtype='float32', always_2d=False)
    a2, _ = sf.read(str(p2), dtype='float32', always_2d=False)
    a1 = torch.from_numpy(a1).unsqueeze(0)
    a2 = torch.from_numpy(a2).unsqueeze(0)

    o1 = r3_extract(a1).features.cpu().numpy()
    o2 = r3_extract(a2).features.cpu().numpy()
    assert np.array_equal(o1, o2)


# ---------------------------------------------------------------------------
# L11.2 — No time-of-day dependence (3 spaced runs in same second)
# ---------------------------------------------------------------------------

def test_no_time_of_day_dependence(r3_extract):
    audio = stim.stim_mix(duration_s=2.0)
    a = r3_extract(audio).features.cpu().numpy()
    time.sleep(0.05)
    b = r3_extract(audio).features.cpu().numpy()
    time.sleep(0.05)
    c = r3_extract(audio).features.cpu().numpy()
    assert np.array_equal(a, b)
    assert np.array_equal(b, c)


# ---------------------------------------------------------------------------
# L11.3 — No PRNG drift (already in L3.3, repeated as anti-feature claim)
# ---------------------------------------------------------------------------

def test_no_random_module_imports():
    """Engine source contains no `import random` or `from random import`."""
    root = _engine_root()
    for p in root.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        text = p.read_text()
        assert "import random" not in text and "from random import" not in text, (
            f"{p.relative_to(root)} imports `random` — anti-feature drift"
        )


# ---------------------------------------------------------------------------
# L11.4 — No global state mutation across instances
# ---------------------------------------------------------------------------

def test_no_global_state_mutation_across_instances(stim, mel_of):
    """Two independent `R3Extractor` instances on the same audio give
    bit-identical output. Order-independence: A then B vs B then A."""
    from Musical_Intelligence.ear.r3.extractor import R3Extractor
    audio = stim.stim_mix(duration_s=2.0)
    mel = mel_of(audio)

    ex_a = R3Extractor()
    ex_b = R3Extractor()
    out_a1 = ex_a.extract(mel, audio=audio, sr=44100).features.cpu().numpy()
    out_b1 = ex_b.extract(mel, audio=audio, sr=44100).features.cpu().numpy()

    # Order-flipped
    ex_c = R3Extractor()
    ex_d = R3Extractor()
    out_d2 = ex_d.extract(mel, audio=audio, sr=44100).features.cpu().numpy()
    out_c2 = ex_c.extract(mel, audio=audio, sr=44100).features.cpu().numpy()

    assert np.array_equal(out_a1, out_b1)
    assert np.array_equal(out_a1, out_c2)
    assert np.array_equal(out_a1, out_d2)


# ---------------------------------------------------------------------------
# L11.5 — No file-system side effects during extract
# ---------------------------------------------------------------------------

def test_no_filesystem_side_effects(tmp_path, r3_extract):
    """Extract must not write any file. We monitor `tmp_path` and the engine
    source dir for new files during a probe."""
    audio = stim.stim_mix(duration_s=1.0)
    engine_root = _engine_root()
    before_engine = {p for p in engine_root.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    before_tmp    = set(tmp_path.iterdir())

    _ = r3_extract(audio)

    after_engine = {p for p in engine_root.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
    after_tmp    = set(tmp_path.iterdir())

    new_engine_files = after_engine - before_engine
    new_tmp_files = after_tmp - before_tmp

    assert not new_engine_files, (
        f"R³ extract wrote files into engine source: {new_engine_files}"
    )
    assert not new_tmp_files, (
        f"R³ extract wrote files into tmp_path: {new_tmp_files}"
    )


# ---------------------------------------------------------------------------
# L11.6 — No network calls
# ---------------------------------------------------------------------------

def test_no_network_socket_in_engine_source():
    """Engine source contains no `socket.`, `urllib`, `requests.`, `http.`,
    or `httpx.` references."""
    root = _engine_root()
    forbidden = re.compile(
        r"\b(socket\.|urllib|requests\.|httpx\.|http\.client|aiohttp|websocket)",
    )
    found = []
    for p in root.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        for lineno, line in enumerate(p.read_text().splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith('"""'):
                continue
            if forbidden.search(line):
                found.append((str(p.relative_to(root)), lineno, line.strip()))
    assert not found, f"Network reference in engine source: {found[:5]}"


# ---------------------------------------------------------------------------
# L11.7 — No dynamic code execution / subprocess / exec
# ---------------------------------------------------------------------------

def test_no_exec_eval_subprocess_in_engine_source():
    """Engine source contains no `exec(`, `eval(`, `subprocess.`, `os.system(`."""
    root = _engine_root()
    forbidden_exact = (
        "exec(", "eval(", "subprocess.", "os.system(", "os.popen(",
    )
    found = []
    for p in root.rglob("*.py"):
        if "__pycache__" in p.parts:
            continue
        for lineno, line in enumerate(p.read_text().splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith('"""'):
                continue
            for pat in forbidden_exact:
                if pat in line:
                    found.append((str(p.relative_to(root)), lineno, pat, line.strip()))
    assert not found, f"Forbidden dynamic-code call in engine source: {found[:5]}"


# ---------------------------------------------------------------------------
# L11.8 — No env-var sweep changes output (R3 doesn't consume env vars)
# ---------------------------------------------------------------------------

def test_omp_mkl_numexpr_envvars_no_effect(r3_extract):
    """Sweeping OMP_NUM_THREADS, MKL_NUM_THREADS, NUMEXPR_NUM_THREADS
    leaves R³ output bit-identical (already covered by L3.4 thread-count;
    redundant pin here so the anti-feature claim has its own owner)."""
    audio = stim.stim_mix(duration_s=2.0)
    saved = {k: os.environ.get(k) for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS",
                                              "NUMEXPR_NUM_THREADS")}
    try:
        for k in saved:
            os.environ[k] = "1"
        a = r3_extract(audio).features.cpu().numpy()
        for k in saved:
            os.environ[k] = "8"
        b = r3_extract(audio).features.cpu().numpy()
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    assert np.array_equal(a, b)
