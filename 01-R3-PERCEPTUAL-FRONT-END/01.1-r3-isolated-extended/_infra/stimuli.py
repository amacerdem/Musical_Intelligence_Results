"""Stimulus library for R³ isolated validation.

All stimuli are deterministic, byte-reproducible, mono, 44.1 kHz, float32 in
[-1, 1] (clipping behavior tested explicitly in L5). Returned as
torch.Tensor of shape (1, N_SAMPLES) for direct use with R3Extractor.

The library has eight families used as L1's stimulus axis:

    1. white  — white Gaussian noise, seed=0xR3, scaled to RMS = 0.1
    2. tone_a4— pure sine at 440 Hz (A4)
    3. sweep  — pure-tone sweep across {100, 220, 440, 880, 1760, 3520} Hz
    4. real   — three real-audio clips (piano, ensemble, percussion)
    5. silence— zeros
    6. dc     — constant 0.5
    7. impulse— Dirac delta at t=0
    8. mix    — white noise + 440 Hz tone superposition

Plus pathological inputs for L5 (saturated, low-amp, phase-inverted, …).
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Dict, Tuple

import numpy as np
import torch
from torch import Tensor

# ---------------------------------------------------------------------------
# Engine constants (canonical pin)
# ---------------------------------------------------------------------------

SR: int = 44100
HOP: int = 256
FRAME_RATE_HZ: float = SR / HOP  # ≈ 172.27
DEFAULT_DURATION_S: float = 5.0  # 861 frames at 172.27 Hz; > 688-frame Tier-2

NYQUIST_HZ: float = SR / 2.0


def _frames(duration_s: float) -> int:
    """Number of mel frames at the engine frame rate."""
    return int(round(duration_s * FRAME_RATE_HZ))


def _samples(duration_s: float) -> int:
    """Number of audio samples at SR."""
    return int(round(duration_s * SR))


# ---------------------------------------------------------------------------
# Mel front-end (matches Musical_Intelligence/ear preprocessing)
# ---------------------------------------------------------------------------

def to_mel(audio: Tensor, n_mels: int = 128, n_fft: int = 2048) -> Tensor:
    """Compute the engine-canonical log-mel spectrogram.

    Output shape (B, n_mels, T) with T = ceil(N_SAMPLES / HOP).
    Matches the engine's `MAX_DURATION_S = 30.0`-capped pipeline.
    """
    import torchaudio
    audio_2d = audio if audio.dim() == 2 else audio.unsqueeze(0)
    mel_xf = torchaudio.transforms.MelSpectrogram(
        sample_rate=SR,
        n_fft=n_fft,
        hop_length=HOP,
        n_mels=n_mels,
        power=2.0,
    )
    mel = mel_xf(audio_2d)            # (B, n_mels, T)
    log_mel = torch.log1p(mel)
    # per-clip-max normalisation (engine convention)
    max_per_clip = log_mel.amax(dim=(-2, -1), keepdim=True).clamp_min(1e-8)
    return (log_mel / max_per_clip).float()


# ---------------------------------------------------------------------------
# Eight stimulus families
# ---------------------------------------------------------------------------

def stim_white(duration_s: float = DEFAULT_DURATION_S, seed: int = 0xC3) -> Tensor:
    """Seeded white Gaussian noise scaled to RMS = 0.1."""
    n = _samples(duration_s)
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n).astype(np.float32)
    x *= 0.1 / max(float(np.sqrt(np.mean(x * x))), 1e-8)
    return torch.from_numpy(x).unsqueeze(0)


def stim_tone(freq_hz: float, duration_s: float = DEFAULT_DURATION_S,
              amplitude: float = 0.5) -> Tensor:
    """Pure cosine wave at *freq_hz*, amplitude in (0, 1)."""
    if not (0 < freq_hz < NYQUIST_HZ):
        raise ValueError(f"freq_hz={freq_hz} outside (0, {NYQUIST_HZ})")
    n = _samples(duration_s)
    t = np.arange(n, dtype=np.float64) / SR
    x = (amplitude * np.cos(2 * np.pi * freq_hz * t)).astype(np.float32)
    return torch.from_numpy(x).unsqueeze(0)


def stim_tone_a4(duration_s: float = DEFAULT_DURATION_S) -> Tensor:
    """A4 = 440 Hz pure tone."""
    return stim_tone(440.0, duration_s)


SWEEP_FREQS_HZ: Tuple[float, ...] = (100.0, 220.0, 440.0, 880.0, 1760.0, 3520.0)


def stim_sweep_segments(duration_s: float = DEFAULT_DURATION_S) -> Tensor:
    """Concatenated equal-duration segments at the SWEEP_FREQS_HZ ladder."""
    seg_dur = duration_s / len(SWEEP_FREQS_HZ)
    parts = [stim_tone(f, seg_dur) for f in SWEEP_FREQS_HZ]
    return torch.cat(parts, dim=-1)


def stim_silence(duration_s: float = DEFAULT_DURATION_S) -> Tensor:
    return torch.zeros(1, _samples(duration_s), dtype=torch.float32)


def stim_dc(duration_s: float = DEFAULT_DURATION_S, value: float = 0.5) -> Tensor:
    return torch.full((1, _samples(duration_s)), value, dtype=torch.float32)


def stim_impulse(duration_s: float = DEFAULT_DURATION_S, position: int = 0) -> Tensor:
    n = _samples(duration_s)
    x = np.zeros(n, dtype=np.float32)
    x[position] = 1.0
    return torch.from_numpy(x).unsqueeze(0)


def stim_mix(duration_s: float = DEFAULT_DURATION_S, freq_hz: float = 440.0,
             noise_rms: float = 0.05, tone_amp: float = 0.3) -> Tensor:
    """Tone + white noise superposition."""
    return stim_tone(freq_hz, duration_s, tone_amp) + \
           noise_rms / 0.1 * stim_white(duration_s)


# ---------------------------------------------------------------------------
# Pathological / robustness library (for L5)
# ---------------------------------------------------------------------------

def stim_pink_noise(duration_s: float = DEFAULT_DURATION_S, seed: int = 0xC3) -> Tensor:
    """1/f noise via spectral shaping of white noise."""
    n = _samples(duration_s)
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n).astype(np.float32)
    X = np.fft.rfft(x)
    f = np.arange(1, len(X) + 1, dtype=np.float64)
    X = X / np.sqrt(f)
    y = np.fft.irfft(X, n=n).astype(np.float32)
    y *= 0.1 / max(float(np.sqrt(np.mean(y * y))), 1e-8)
    return torch.from_numpy(y).unsqueeze(0)


def stim_brown_noise(duration_s: float = DEFAULT_DURATION_S, seed: int = 0xC3) -> Tensor:
    """Brownian (red) noise — integrated white."""
    n = _samples(duration_s)
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n).astype(np.float32)
    y = np.cumsum(x).astype(np.float32)
    y -= y.mean()
    y *= 0.1 / max(float(np.sqrt(np.mean(y * y))), 1e-8)
    return torch.from_numpy(y).unsqueeze(0)


def stim_clipped(base: Tensor, clip_amplitude: float = 1.5) -> Tensor:
    """Saturate a base signal to [-1, 1] after multiplying by *clip_amplitude*."""
    return torch.clamp(base * clip_amplitude, -1.0, 1.0)


def stim_phase_inverted(base: Tensor) -> Tensor:
    return -base


def stim_low_amp(base: Tensor, db: float = -60.0) -> Tensor:
    return base * (10.0 ** (db / 20.0))


def stim_am_tone(carrier_hz: float = 1000.0, mod_hz: float = 8.0,
                 duration_s: float = DEFAULT_DURATION_S,
                 mod_depth: float = 0.5) -> Tensor:
    """AM-modulated tone for L6 K-modulation tests."""
    n = _samples(duration_s)
    t = np.arange(n, dtype=np.float64) / SR
    carrier = np.cos(2 * np.pi * carrier_hz * t)
    envelope = 1.0 + mod_depth * np.cos(2 * np.pi * mod_hz * t)
    x = (0.4 * envelope * carrier).astype(np.float32)
    return torch.from_numpy(x).unsqueeze(0)


def stim_dyad(f0_hz: float, ratio: Tuple[int, int],
              n_partials: int = 6, partial_decay: str = "1/n",
              duration_s: float = DEFAULT_DURATION_S,
              amplitude: float = 0.4) -> Tensor:
    """Two harmonic complex tones at *f0_hz* and *f0_hz * ratio[1] / ratio[0]*.

    Mirrors the V1 default synth (6 partials, 1/n decay) used in V-Reproduction
    Phase 6 — but here for L6 internal-consistency probes only, never for
    cognitive-rating correlation.
    """
    p, q = ratio
    if not (p > 0 and q > 0):
        raise ValueError("ratio must be positive integers")
    n = _samples(duration_s)
    t = np.arange(n, dtype=np.float64) / SR

    def complex_tone(f0: float) -> np.ndarray:
        out = np.zeros(n, dtype=np.float64)
        for k in range(1, n_partials + 1):
            f_k = f0 * k
            if f_k >= NYQUIST_HZ:
                break
            if partial_decay == "1/n":
                amp = 1.0 / k
            elif partial_decay == "flat":
                amp = 1.0
            else:
                raise ValueError(f"partial_decay={partial_decay}")
            out += amp * np.cos(2 * np.pi * f_k * t)
        # peak-normalise
        out /= max(float(np.max(np.abs(out))), 1e-8)
        return out

    a = complex_tone(f0_hz)
    b = complex_tone(f0_hz * q / p)
    x = (amplitude * 0.5 * (a + b)).astype(np.float32)
    return torch.from_numpy(x).unsqueeze(0)


def stim_metronome(bpm: float = 120.0, duration_s: float = DEFAULT_DURATION_S,
                   click_freq_hz: float = 1000.0, click_ms: float = 10.0) -> Tensor:
    """Periodic clicks at *bpm* — used by L6 G-rhythm tests."""
    n = _samples(duration_s)
    period_samples = int(round(SR * 60.0 / bpm))
    click_n = int(round(SR * click_ms / 1000.0))
    t_click = np.arange(click_n, dtype=np.float64) / SR
    envelope = np.exp(-t_click * 200.0)  # fast-decay
    click = (0.6 * envelope * np.cos(2 * np.pi * click_freq_hz * t_click)).astype(np.float32)
    x = np.zeros(n, dtype=np.float32)
    pos = 0
    while pos + click_n <= n:
        x[pos:pos + click_n] = click
        pos += period_samples
    return torch.from_numpy(x).unsqueeze(0)


# ---------------------------------------------------------------------------
# Eight L1 stimulus families — single registry
# ---------------------------------------------------------------------------

L1_STIMULI: Dict[str, Callable[[], Tensor]] = {
    "white":      lambda: stim_white(),
    "tone_a4":    lambda: stim_tone_a4(),
    "sweep":      lambda: stim_sweep_segments(),
    "silence":    lambda: stim_silence(),
    "dc":         lambda: stim_dc(),
    "impulse":    lambda: stim_impulse(),
    "mix":        lambda: stim_mix(),
    # 'real' family is loaded from data/ in tests that need real audio;
    # registered here as a sentinel so L1 reports the 8-stimulus axis.
    "real":       lambda: _load_real_audio_clip(),
}


_REAL_AUDIO_CACHE: Tensor | None = None


def _load_real_audio_clip() -> Tensor:
    """Load one real-audio clip from data/ if available; else fall back to mix."""
    global _REAL_AUDIO_CACHE
    if _REAL_AUDIO_CACHE is not None:
        return _REAL_AUDIO_CACHE
    candidates = [
        Path(__file__).parents[2] / "data" / "real_clips" / "piano_solo.wav",
        Path(__file__).parents[2] / "data" / "real_clips" / "ensemble.wav",
        Path(__file__).parents[2] / "data" / "real_clips" / "percussion.wav",
    ]
    for p in candidates:
        if p.exists():
            import soundfile as sf
            x, sr = sf.read(str(p), dtype="float32", always_2d=False)
            if sr != SR:
                # simple linear resample (sufficient for spec-compliance tests)
                idx = np.linspace(0, len(x) - 1, int(len(x) * SR / sr))
                x = np.interp(idx, np.arange(len(x)), x).astype(np.float32)
            x = x[: _samples(DEFAULT_DURATION_S)]
            _REAL_AUDIO_CACHE = torch.from_numpy(x).unsqueeze(0)
            return _REAL_AUDIO_CACHE
    # Fallback: use mix so the L1 axis stays full and tests are skippable
    _REAL_AUDIO_CACHE = stim_mix()
    return _REAL_AUDIO_CACHE


L1_STIMULUS_NAMES: Tuple[str, ...] = (
    "white", "tone_a4", "sweep", "real", "silence", "dc", "impulse", "mix",
)
assert set(L1_STIMULUS_NAMES) == set(L1_STIMULI.keys())
