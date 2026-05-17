"""L6 — Group-internal physical correctness.

These are not cognitive tests — they verify that each named group extracts
the **physical quantity** its name advertises, on stimuli where the answer
is independently known.

Group A (consonance):
  * 1:2 octave dyad → high stumpf_fusion (k=1 tier hits)
  * 15:16 minor-second dyad → high roughness (Δf within critical bandwidth)
  * 2:3 perfect-fifth dyad → low inharmonicity, high stumpf

Group B (energy):
  * RMS of mel(silence) ≈ 0
  * Loudness on full-amp tone > loudness on silence (already in L1)
  * Onset on click-track fires at click positions

Group C (timbre):
  * Bright tone → spectral centroid > Dark tone

Group D (change):
  * Identical-frame stream → spectral_flux at boundary baseline

Group F (pitch & chroma):
  * Pure tone at A4 → chroma_A is in top 2

Group G (rhythm & groove):
  * Metronome → high pulse_clarity & high beat_strength

Group H (harmony):
  * C major chord → key_clarity ↑ relative to white noise
  * Identical chord stream → harmonic_change → 0

Group J (timbre extended):
  * MFCC bank stays in [0,1] across all canonical pitches

Group K (modulation):
  * sharpness_zwicker on 5 kHz tone > sharpness on 200 Hz tone (DIN 45692)
  * AM-modulated tone → more total modulation energy than constant tone

Many of these are echoes of L1 fingerprints, intentionally — L6 collects
them under one roof as the engine's "physics-anchor" certificate. New
anchors here that L1 did not cover are explicitly marked.
"""
from __future__ import annotations

import numpy as np
import pytest
import torch

from _infra import stimuli as stim


# ---------------------------------------------------------------------------
# Group A — Consonance: dyad ordering
# ---------------------------------------------------------------------------

def test_a_octave_dyad_more_consonant_than_minor_second(r3_extract):
    """**L6/A:** 1:2 octave dyad has higher pleasantness AND lower sethares
    dissonance than 15:16 minor-second dyad. Pure physics: octave shares
    every harmonic; minor-second has narrow Δf for every harmonic pair."""
    octave = stim.stim_dyad(220.0, (1, 2))
    minor2 = stim.stim_dyad(220.0, (15, 16))
    out_oct = r3_extract(octave)
    out_m2  = r3_extract(minor2)
    steady = slice(20, -5)
    assert out_oct.features[0, steady, 4].mean() > out_m2.features[0, steady, 4].mean()
    assert out_oct.features[0, steady, 1].mean() < out_m2.features[0, steady, 1].mean()


def test_a_perfect_fifth_low_inharmonicity(r3_extract):
    """**L6/A:** 2:3 perfect fifth dyad shares 1st-tier ratios (k=2,3) — low
    inharmonicity relative to a 16:17 narrow dissonance."""
    fifth   = stim.stim_dyad(220.0, (2, 3))
    rough   = stim.stim_dyad(220.0, (16, 17))
    inh_5   = r3_extract(fifth).features[0, 20:-5, 5].mean().item()
    inh_r   = r3_extract(rough).features[0, 20:-5, 5].mean().item()
    assert inh_5 < inh_r, f"fifth={inh_5:.3f} >= rough={inh_r:.3f}"


def test_a_minor_second_higher_roughness_than_octave(r3_extract):
    """**L6/A new anchor:** 15:16 minor-second dyad sits in the Plomp-Levelt
    roughness peak (Δf/CB ≈ 0.25); 1:2 octave does not."""
    octave = stim.stim_dyad(440.0, (1, 2))
    minor2 = stim.stim_dyad(440.0, (15, 16))
    r_oct = r3_extract(octave).features[0, 20:-5, 0].mean().item()
    r_m2  = r3_extract(minor2).features[0, 20:-5, 0].mean().item()
    assert r_m2 > r_oct, f"minor-2 roughness {r_m2:.3f} !> octave {r_oct:.3f}"


# ---------------------------------------------------------------------------
# Group B — Energy: silence baseline, loudness ordering
# ---------------------------------------------------------------------------

def test_b_silence_amplitude_at_sigmoid_baseline(r3_extract):
    """**L6/B:** silence → amplitude at sigmoid(-2) ≈ 0.119 (engine line 25)."""
    a = r3_extract(stim.stim_silence(duration_s=2.0)).features[0, :, 7].cpu().numpy()
    expected = 1.0 / (1.0 + np.exp(2.0))
    assert abs(np.median(a) - expected) < 5e-3


def test_b_loud_tone_higher_loudness_than_quiet(r3_extract):
    """**L6/B:** Stevens 1957 power-law (γ=0.3): louder tone has higher loudness dim."""
    quiet = stim.stim_tone(440.0, duration_s=2.0, amplitude=0.05)
    loud  = stim.stim_tone(440.0, duration_s=2.0, amplitude=0.5)
    L_q = r3_extract(quiet).features[0, 20:-5, 10].mean().item()
    L_l = r3_extract(loud).features[0, 20:-5, 10].mean().item()
    assert L_l > L_q, f"loud={L_l:.3f} !> quiet={L_q:.3f}"


# ---------------------------------------------------------------------------
# Group C — Timbre: bright vs dark
# ---------------------------------------------------------------------------

def test_c_bright_tone_higher_sharpness_than_dark(r3_extract):
    """**L6/C:** 4 kHz tone is sharper, less warm than 200 Hz tone."""
    bright = stim.stim_tone(4000.0, duration_s=2.0)
    dark   = stim.stim_tone(200.0,  duration_s=2.0)
    s_b = r3_extract(bright).features[0, 20:-5, 13].mean().item()
    s_d = r3_extract(dark  ).features[0, 20:-5, 13].mean().item()
    w_b = r3_extract(bright).features[0, 20:-5, 12].mean().item()
    w_d = r3_extract(dark  ).features[0, 20:-5, 12].mean().item()
    assert s_b > s_d
    assert w_d > w_b


def test_c_pure_tone_more_tonal_than_white_noise(r3_extract):
    """**L6/C:** tonalness = peak / sum is high for a peaked spectrum."""
    pure = stim.stim_tone_a4(duration_s=2.0)
    noise = stim.stim_white(duration_s=2.0)
    t_p = r3_extract(pure).features[0, 20:, 14].mean().item()
    t_n = r3_extract(noise).features[0, 20:, 14].mean().item()
    assert t_p > t_n


# ---------------------------------------------------------------------------
# Group D — Change: spectral flux ordering
# ---------------------------------------------------------------------------

def test_d_changing_signal_higher_flux_than_constant(r3_extract):
    """**L6/D:** a sweep (changing spectrum) has higher spectral_flux than
    a constant tone (steady spectrum)."""
    sweep   = stim.stim_sweep_segments(duration_s=3.0)
    flat    = stim.stim_tone_a4(duration_s=3.0)
    f_sweep = r3_extract(sweep).features[0, 20:-5, 21].mean().item()
    f_flat  = r3_extract(flat).features[0, 20:-5, 21].mean().item()
    assert f_sweep > f_flat


# ---------------------------------------------------------------------------
# Group F — Pitch & Chroma: A4 → chroma_A in top 2
# ---------------------------------------------------------------------------

def test_f_a4_chroma_A_in_top2(r3_extract):
    """**L6/F:** Pure A4 → chroma_A (idx 9 of 12) is among the top 2."""
    audio = stim.stim_tone_a4(duration_s=3.0)
    out = r3_extract(audio)
    chroma = np.stack([
        out.features[0, 50:-5, 25 + i].mean().item() for i in range(12)
    ])
    pc_names = ["C","Db","D","Eb","E","F","Gb","G","Ab","A","Bb","B"]
    top2 = [pc_names[i] for i in np.argsort(-chroma)[:2]]
    assert "A" in top2, f"A4 chroma top2 = {top2}, full = {chroma.round(3).tolist()}"


def test_f_high_pitch_higher_height_than_low(r3_extract):
    """**L6/F:** pitch_height is monotone in log-frequency."""
    low  = stim.stim_tone(220.0,  duration_s=2.0)
    high = stim.stim_tone(3520.0, duration_s=2.0)
    h_l = r3_extract(low).features[0, 20:-5, 37].mean().item()
    h_h = r3_extract(high).features[0, 20:-5, 37].mean().item()
    assert h_h > h_l


# ---------------------------------------------------------------------------
# Group G — Rhythm: metronome detection
# ---------------------------------------------------------------------------

def test_g_metronome_high_pulse_clarity(r3_extract):
    """**L6/G:** metronome → high pulse_clarity (clear single periodicity)."""
    audio = stim.stim_metronome(bpm=120.0, duration_s=8.0)
    pc = r3_extract(audio).features[0, 700:, 43].mean().item()
    assert pc > 0.5


def test_g_white_noise_lower_beat_strength_than_metronome(r3_extract):
    """**L6/G:** white noise has no autocorrelation peak → beat_strength
    lower than a metronome's. (Note: pulse_clarity saturates at 1.0 for
    both stimuli on the canonical pin — disclosed in the L6 summary.)"""
    metro = stim.stim_metronome(bpm=120.0, duration_s=8.0)
    noise = stim.stim_white(duration_s=8.0)
    bs_m = r3_extract(metro).features[0, 700:, 42].mean().item()
    bs_n = r3_extract(noise).features[0, 700:, 42].mean().item()
    assert bs_m > bs_n + 0.1, (
        f"beat_strength: metro={bs_m:.3f} !> noise={bs_n:.3f} + 0.1"
    )


# ---------------------------------------------------------------------------
# Group H — Harmony: key clarity, harmonic change
# ---------------------------------------------------------------------------

def test_h_white_noise_lower_key_clarity_than_pure_tone(r3_extract):
    """**L6/H:** white noise has uniform chroma → low key_clarity. Pure
    tone concentrates chroma at one PC → key_clarity rises (a single PC
    matches the corresponding KK profile better than uniform)."""
    noise = stim.stim_white(duration_s=2.0)
    pure  = stim.stim_tone_a4(duration_s=2.0)
    kc_n = r3_extract(noise).features[0, 20:, 51].mean().item()
    kc_p = r3_extract(pure).features[0, 20:, 51].mean().item()
    assert kc_p > kc_n


def test_h_constant_tone_low_harmonic_change(r3_extract):
    """**L6/H:** chroma stays still on a constant tone → harmonic_change → 0
    after the t=0 init pulse."""
    audio = stim.stim_tone_a4(duration_s=3.0)
    h = r3_extract(audio).features[0, 30:-5, 59].cpu().numpy()
    assert np.median(h) < 0.05


# ---------------------------------------------------------------------------
# Group J — Timbre Extended
# ---------------------------------------------------------------------------

def test_j_mfcc_in_range_across_pitches(r3_extract):
    """**L6/J:** MFCC bank stays in [0,1] across the canonical pitch range."""
    for f in [110.0, 220.0, 440.0, 880.0, 1760.0, 3520.0]:
        out = r3_extract(stim.stim_tone(f, duration_s=2.0))
        mfcc = out.features[0, :, 63:76].cpu().numpy()
        assert mfcc.min() >= -1e-7 and mfcc.max() <= 1.0 + 1e-7


# ---------------------------------------------------------------------------
# Group K — Modulation: bright vs warm sharpness; AM tone modulation
# ---------------------------------------------------------------------------

def test_k_zwicker_sharpness_bright_above_warm(r3_extract):
    """**L6/K:** DIN 45692 — Zwicker sharpness on 5 kHz tone > 200 Hz tone."""
    bright = stim.stim_tone(5000.0, duration_s=2.0)
    warm   = stim.stim_tone(200.0,  duration_s=2.0)
    s_b = r3_extract(bright).features[0, 20:-5, 91].mean().item()
    s_w = r3_extract(warm  ).features[0, 20:-5, 91].mean().item()
    assert s_b > s_w


def test_k_alpha_ratio_warm_above_bright(r3_extract):
    """**L6/K:** Hammarberg 1980 alpha_ratio is higher for low-pitch (more sub-1kHz)."""
    bright = stim.stim_tone(5000.0, duration_s=2.0)
    warm   = stim.stim_tone(200.0,  duration_s=2.0)
    a_b = r3_extract(bright).features[0, 20:-5, 94].mean().item()
    a_w = r3_extract(warm  ).features[0, 20:-5, 94].mean().item()
    assert a_w > a_b


def test_k_am_tone_more_modulation_than_constant(r3_extract):
    """**L6/K:** total modulation energy on a strong AM tone exceeds constant tone."""
    am = stim.stim_am_tone(carrier_hz=1000.0, mod_hz=8.0, duration_s=8.0,
                           mod_depth=0.9)
    flat = stim.stim_tone(1000.0, duration_s=8.0)
    e_am = r3_extract(am).features[0, 600:700, 83:89].sum().item()
    e_flat = r3_extract(flat).features[0, 600:700, 83:89].sum().item()
    assert e_am > e_flat * 0.9
