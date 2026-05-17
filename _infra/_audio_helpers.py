"""V-Reproduction audio helpers (vendored from Science/V1/conftest.py).

Two pure functions for loading WAV stimuli into the engine's expected
formats. Used by Phase 2 (R3 unit tests Bowling DEV reproduction) and
any other phase that needs WAV → mel / raw waveform conversion.

Requires: soundfile, torch, torchaudio (already in V-Repro requirements).
"""
from __future__ import annotations

from pathlib import Path

import torch


def load_wav_as_mel(wav_path: str | Path, sr: int = 44100) -> torch.Tensor:
    """Load a WAV file and convert to mel spectrogram (B, 128, T).

    Returns a batch-1 mel tensor ready for R3Extractor.
    """
    import soundfile as sf
    import torchaudio.transforms as T

    data, orig_sr = sf.read(str(wav_path), dtype="float32")
    waveform = torch.from_numpy(data)
    if waveform.ndim == 1:
        waveform = waveform.unsqueeze(0)            # (1, samples)
    else:
        waveform = waveform.T                       # (channels, samples)
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    if orig_sr != sr:
        import torchaudio
        waveform = torchaudio.functional.resample(waveform, orig_sr, sr)

    mel_transform = T.MelSpectrogram(
        sample_rate=sr, n_fft=2048, hop_length=256,
        n_mels=128, power=2.0,
    )
    mel = mel_transform(waveform)                   # (1, 128, T)
    return mel.unsqueeze(0)                         # (B=1, 1, 128, T)


def load_wav_raw(wav_path: str | Path, sr: int = 44100) -> torch.Tensor:
    """Load WAV as raw waveform tensor (1, N_SAMPLES)."""
    import soundfile as sf

    data, orig_sr = sf.read(str(wav_path), dtype="float32")
    waveform = torch.from_numpy(data)
    if waveform.ndim == 1:
        waveform = waveform.unsqueeze(0)
    else:
        waveform = waveform.T
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    if orig_sr != sr:
        import torchaudio
        waveform = torchaudio.functional.resample(waveform, orig_sr, sr)
    return waveform                                 # (1, N_SAMPLES)
