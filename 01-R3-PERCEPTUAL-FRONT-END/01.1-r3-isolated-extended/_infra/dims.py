"""Canonical 97-D R³ dim registry — frozen for the isolated-validation suite.

Sourced from `Musical_Intelligence/ear/r3/extractor.py` at engine pin
`318eb2f5…` (see `_infra/manifests/engine_pin.json`).

This module is the **single source of truth** for dim names and group
boundaries inside R3_Isolated_Validation. Every test imports from here
rather than re-querying the engine, so a registry drift in the engine
will cause `test_dims_match_engine` (in `_infra/test_pin_integrity.py`)
to fail loudly.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

# ---------------------------------------------------------------------------
# 97 dim names — frozen ordered tuple
# ---------------------------------------------------------------------------

DIM_NAMES: Tuple[str, ...] = (
    # Group A — Consonance [0:7]
    "roughness",
    "sethares_dissonance",
    "helmholtz_kang",
    "stumpf_fusion",
    "sensory_pleasantness",
    "inharmonicity",
    "harmonic_deviation",
    # Group B — Energy [7:12]
    "amplitude",
    "velocity_A",
    "acceleration_A",
    "loudness",
    "onset_strength",
    # Group C — Timbre [12:21]
    "warmth",
    "sharpness",
    "tonalness",
    "clarity",
    "spectral_smoothness",
    "spectral_autocorrelation",
    "tristimulus1",
    "tristimulus2",
    "tristimulus3",
    # Group D — Change [21:25]
    "spectral_flux",
    "distribution_entropy",
    "distribution_flatness",
    "distribution_concentration",
    # Group F — Pitch & Chroma [25:41]
    "chroma_C",
    "chroma_Db",
    "chroma_D",
    "chroma_Eb",
    "chroma_E",
    "chroma_F",
    "chroma_Gb",
    "chroma_G",
    "chroma_Ab",
    "chroma_A",
    "chroma_Bb",
    "chroma_B",
    "pitch_height",
    "pitch_class_entropy",
    "pitch_salience",
    "inharmonicity_index",
    # Group G — Rhythm & Groove [41:51]
    "tempo_estimate",
    "beat_strength",
    "pulse_clarity",
    "syncopation_index",
    "metricality_index",
    "isochrony_nPVI",
    "groove_index",
    "event_density",
    "tempo_stability",
    "rhythmic_regularity",
    # Group H — Harmony & Tonality [51:63]
    "key_clarity",
    "tonnetz_fifth_x",
    "tonnetz_fifth_y",
    "tonnetz_minor_x",
    "tonnetz_minor_y",
    "tonnetz_major_x",
    "tonnetz_major_y",
    "voice_leading_distance",
    "harmonic_change",
    "tonal_stability",
    "diatonicity",
    "syntactic_irregularity",
    # Group J — Timbre Extended [63:83]
    "mfcc_1", "mfcc_2", "mfcc_3", "mfcc_4", "mfcc_5",
    "mfcc_6", "mfcc_7", "mfcc_8", "mfcc_9", "mfcc_10",
    "mfcc_11", "mfcc_12", "mfcc_13",
    "spectral_contrast_1", "spectral_contrast_2", "spectral_contrast_3",
    "spectral_contrast_4", "spectral_contrast_5", "spectral_contrast_6",
    "spectral_contrast_7",
    # Group K — Modulation [83:97]
    "modulation_0_5Hz",
    "modulation_1Hz",
    "modulation_2Hz",
    "modulation_4Hz",
    "modulation_8Hz",
    "modulation_16Hz",
    "modulation_centroid",
    "modulation_bandwidth",
    "sharpness_zwicker",
    "fluctuation_strength",
    "loudness_a_weighted",
    "alpha_ratio",
    "hammarberg_index",
    "spectral_slope_0_500",
)

assert len(DIM_NAMES) == 97, f"DIM_NAMES has {len(DIM_NAMES)} entries, expected 97"

# ---------------------------------------------------------------------------
# Group boundaries
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GroupSpec:
    name: str
    letter: str
    slice_start: int
    slice_end: int
    stage: int
    domain: str
    depends_on: Tuple[str, ...] = ()

    @property
    def dim(self) -> int:
        return self.slice_end - self.slice_start

    @property
    def indices(self) -> Tuple[int, ...]:
        return tuple(range(self.slice_start, self.slice_end))


GROUPS: Tuple[GroupSpec, ...] = (
    GroupSpec("consonance",       "A", 0,  7,  stage=1, domain="psychoacoustic"),
    GroupSpec("energy",           "B", 7,  12, stage=1, domain="spectral"),
    GroupSpec("timbre",           "C", 12, 21, stage=1, domain="spectral"),
    GroupSpec("change",           "D", 21, 25, stage=1, domain="temporal"),
    GroupSpec("pitch_chroma",     "F", 25, 41, stage=1, domain="tonal"),
    GroupSpec("rhythm_groove",    "G", 41, 51, stage=2, domain="temporal",
              depends_on=("energy[11]:onset_strength",)),
    GroupSpec("harmony_tonality", "H", 51, 63, stage=2, domain="tonal",
              depends_on=("pitch_chroma[25:36]:chroma_12",)),
    GroupSpec("timbre_extended",  "J", 63, 83, stage=1, domain="spectral"),
    GroupSpec("modulation",       "K", 83, 97, stage=1, domain="psychoacoustic"),
)

# Total = 7+5+9+4+16+10+12+20+14 = 97
assert sum(g.dim for g in GROUPS) == 97

# ---------------------------------------------------------------------------
# Warm-up tiers — per `Musical_Intelligence/ear/r3/pipeline/warmup.py`
# ---------------------------------------------------------------------------

# Tier 0: frame-local, confidence = 1 from frame 0
# Tier 1 ramp: 344-frame ramp 0 → 1
# Tier 1 zero: output = 0 until frame 344
# Tier 2 zero: output = 0 until frame 688
#
# Counts (per paper §97-D / §Boundary doctrine): 79 / 9 / 8 / 1 = 97.
# Exact dim assignment is verified against the engine's WarmupManager
# in `_infra/test_pin_integrity.py` (so this file does not duplicate it).

WARMUP_TIER_COUNTS = {
    "tier_0_frame_local": 79,
    "tier_1_ramp_344f":   9,
    "tier_1_zero_344f":   8,
    "tier_2_zero_688f":   1,
}
assert sum(WARMUP_TIER_COUNTS.values()) == 97

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def group_for_index(idx: int) -> GroupSpec:
    """Return the GroupSpec whose slice contains *idx*."""
    for g in GROUPS:
        if g.slice_start <= idx < g.slice_end:
            return g
    raise IndexError(f"index {idx} out of range [0, 97)")


def index_for_name(name: str) -> int:
    """Return the dim index for *name*. Raises if absent."""
    return DIM_NAMES.index(name)
