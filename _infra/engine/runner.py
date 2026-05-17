"""V-Reproduction engine runner — single canonical entry point.

All V-Reproduction phases import `run_engine` from here. The runner is a
THIN wrapper around the frozen engine API used by the V6 A2 ECE pipeline
(`Science/V-Reproduction/05-ece-belief-calibration/code/extract_belief_traces.py`); it performs
no statistics or scientific transformation of its own.

Discovered API (from V6 A2 + Science/Musical_Intelligence/brain/executor.py):
    R3Extractor.extract(mel, audio, sr) -> r3_out.features   # (B, T, 97)
    H3Extractor.extract(r3_features, demands) -> h3_out.features  # dict
    execute(nuclei, h3_features, r3_features) -> (outputs, ram, neuro)

Engine HEAD pinned at `318eb2f529d7103e8b7d80b01228357fdc4e0217`
(see `_infra/manifests/engine_head.json`).

Determinism: torch + numpy ops in this engine are deterministic-by-construction
(no RNG draws). The `seed` argument is accepted for forward compatibility
but the frozen engine does not currently consume it. Bit-identical 3-run
determinism is asserted in `test_engine_runner.py`.
"""
from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set, Tuple

import numpy as np


# ── Path setup ───────────────────────────────────────────────────────
# This file: Science/V-Reproduction/_infra/engine/runner.py
# Engine resolution order (audit-grade, self-contained-first):
#   1) V-Reproduction/engine/Musical_Intelligence  (vendored flat snapshot at HEAD 318eb2f5)
#   2) Science/Musical_Intelligence  (parent-checkout fallback for dev / external use)
#
# parents[0] = engine/, parents[1] = _infra/,
# parents[2] = V-Reproduction/, parents[3] = Science/
_VREPRO_ROOT = Path(__file__).resolve().parents[2]
_VENDORED_ENGINE_PARENT = _VREPRO_ROOT / "engine"  # contains Musical_Intelligence/
_SCIENCE_ROOT = Path(__file__).resolve().parents[3]

if (_VENDORED_ENGINE_PARENT / "Musical_Intelligence").is_dir():
    _ENGINE_PARENT = _VENDORED_ENGINE_PARENT
else:
    _ENGINE_PARENT = _SCIENCE_ROOT

if str(_ENGINE_PARENT) not in sys.path:
    sys.path.insert(0, str(_ENGINE_PARENT))


# ── Public layer contract ────────────────────────────────────────────
REQUIRED_LAYERS: Tuple[str, ...] = ("r3", "h3", "c3", "ram", "neuro", "beliefs")

# ── Paper / engine conventions (mirror V6 A2) ────────────────────────
SAMPLE_RATE = 44_100
HOP_LENGTH = 256
N_MELS = 128
N_FFT = 2048
FRAME_RATE = SAMPLE_RATE / HOP_LENGTH  # 172.27 Hz
MAX_DURATION_S = 30.0  # paper convention V2/T-R3-08

# Paper's 8 Core beliefs (one per F1-F8) as the canonical "beliefs" layer
# subset. Mirrors `PAPER_BELIEFS + EXTENSION_BELIEFS` from V6 A2; we use
# the 8 PAPER_BELIEFS only here (each layer is a thin sample, not the
# full 121-belief registry — full extraction lives in V6/A2).
_BELIEF_REGISTRY: Tuple[Tuple[str, str, str, str], ...] = (
    ("F1", "BCH",  "Musical_Intelligence.brain.functions.f1.beliefs.bch.harmonic_stability",   "HarmonicStability"),
    ("F1", "PSCL", "Musical_Intelligence.brain.functions.f1.beliefs.pscl.pitch_prominence",    "PitchProminence"),
    ("F1", "PCCR", "Musical_Intelligence.brain.functions.f1.beliefs.pccr.pitch_identity",      "PitchIdentity"),
    ("F1", "MIAA", "Musical_Intelligence.brain.functions.f1.beliefs.miaa.timbral_character",   "TimbralCharacter"),
    ("F2", "HTP",  "Musical_Intelligence.brain.functions.f2.beliefs.htp.prediction_hierarchy", "PredictionHierarchy"),
    ("F2", "HTP",  "Musical_Intelligence.brain.functions.f2.beliefs.htp.prediction_accuracy",  "PredictionAccuracy"),
    ("F2", "SPH",  "Musical_Intelligence.brain.functions.f2.beliefs.sph.sequence_match",       "SequenceMatch"),
    ("F2", "ICEM", "Musical_Intelligence.brain.functions.f2.beliefs.icem.information_content", "InformationContent"),
)


def _set_deterministic_threading() -> None:
    """Pin BLAS thread counts pre-emptively. See module docstring on determinism.

    These envvars must be set BEFORE numpy/torch are imported by downstream
    code in the same process. They are idempotent across calls.
    """
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ.setdefault(var, "1")


_set_deterministic_threading()


def _collect_mechanisms(strict: bool = False) -> Tuple[List[Any], Set[Tuple[int, int, int, int]]]:
    """Auto-discover all mechanism instances across F1-F9. Mirrors V6 A2.

    Args:
        strict: If True, re-raise mechanism-import or instantiation errors
            instead of warning + continuing. Use this in CI / phase-zero
            sanity checks where partial mech registries are unacceptable.
    """
    from Musical_Intelligence.contracts.bases.nucleus import _NucleusBase  # noqa: WPS433

    role_to_depth = {"relay": 0, "encoder": 1, "associator": 2, "integrator": 3, "hub": 4}
    seen: Set[str] = set()
    nuclei: List[Any] = []

    for fn in ("f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9"):
        try:
            mod = importlib.import_module(f"Musical_Intelligence.brain.functions.{fn}.mechanisms")
        except Exception as e:
            if strict:
                raise
            print(
                f"[runner] WARN failed to import mechanisms module for {fn}: {e!r}",
                file=sys.stderr,
            )
            continue
        for attr_name in getattr(mod, "__all__", []):
            cls = getattr(mod, attr_name, None)
            if cls is None:
                continue
            try:
                inst = cls()
            except Exception as e:
                if strict:
                    raise
                print(
                    f"[runner] WARN failed to instantiate mech {fn}.{attr_name}: {e!r}",
                    file=sys.stderr,
                )
                continue
            if not isinstance(inst, _NucleusBase):
                continue
            if inst.NAME in seen:
                continue
            seen.add(inst.NAME)
            role = getattr(inst, "ROLE", "relay")
            min_depth = role_to_depth.get(role, 0)
            if inst.PROCESSING_DEPTH < min_depth:
                inst.PROCESSING_DEPTH = min_depth
            nuclei.append(inst)

    h3_demands: Set[Tuple[int, int, int, int]] = set()
    for m in nuclei:
        for spec in m.h3_demand:
            h3_demands.add(spec.as_tuple())

    return nuclei, h3_demands


def _load_audio_to_mel(audio_path: Path) -> Tuple[Any, Any]:
    """Load audio → (mel_log_normalized, audio_tensor). Returns torch tensors.

    Replicates V6 A2 preprocessing exactly: librosa load (mono, 44.1k, 30s cap)
    → torchaudio MelSpectrogram → log1p → max-normalize.
    """
    import librosa  # noqa: WPS433
    import torch  # noqa: WPS433
    import torchaudio  # noqa: WPS433

    y, _ = librosa.load(str(audio_path), sr=SAMPLE_RATE, mono=True, duration=MAX_DURATION_S)
    audio_t = torch.from_numpy(y).unsqueeze(0).float()

    mel_transform = torchaudio.transforms.MelSpectrogram(
        sample_rate=SAMPLE_RATE,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        n_mels=N_MELS,
        power=2.0,
    )
    mel = torch.log1p(mel_transform(audio_t))
    mel_max = mel.amax(dim=(-2, -1), keepdim=True).clamp(min=1e-8)
    mel = mel / mel_max
    return mel, audio_t


def _to_numpy(x: Any) -> np.ndarray:
    """Detach torch tensor to NumPy without copy when possible."""
    import torch  # noqa: WPS433

    if isinstance(x, torch.Tensor):
        return x.detach().cpu().numpy()
    return np.asarray(x)


def run_engine(
    audio_path: str | Path,
    *,
    return_layers: Iterable[str] = REQUIRED_LAYERS,
    seed: int = 0,
    strict: bool = False,
) -> Dict[str, Any]:
    """Run the frozen MI engine on a single audio file.

    Args:
        audio_path: Path to a WAV (or any librosa-readable) file.
        return_layers: Iterable of layer names to include in output. Must
            be a subset of REQUIRED_LAYERS. Unknown layers raise KeyError.
        seed: int = 0
            Forward-compatibility parameter. The frozen MI engine has no RNG
            draws, so this value is not consumed. Phase consumers should still
            pass their phase seed for traceability — future engine versions
            may consume it.
        strict: If True, re-raise any exception encountered during mechanism
            discovery / instantiation or belief-cycle execution instead of
            warning to stderr and continuing. Default (False) preserves the
            V6 A2 behaviour of tolerating partial mech registries during
            engine refactors, but emits a stderr WARN line per failure so the
            drift is visible.

    The `beliefs` layer returns ONLY the 8 PAPER_BELIEFS subset (mirroring
    V6 A2). The full 121-belief F1-F8 registry is NOT run by this canonical
    wrapper. Phases needing all 121 beliefs must extend or write a
    phase-specific extractor.

    Returns:
        dict keyed by layer name:
          - "r3":      np.ndarray (T, 97) — squeezed batch dim
          - "h3":      dict[(r3_idx, horizon, morph, law) -> np.ndarray (T,)]
          - "c3":      dict[mechanism_NAME -> np.ndarray (T, D_mech)]
          - "ram":     np.ndarray (T, 26)
          - "neuro":   np.ndarray (T, 4)
          - "beliefs": dict["{Function}_{BeliefClass}" -> dict[trace_name -> np.ndarray (T,)]]
                       Trace names: pi_pred, pe, posterior, obs.

    Raises:
        FileNotFoundError: if `audio_path` does not exist.
        KeyError: if a requested layer is not in REQUIRED_LAYERS.
    """
    import torch  # noqa: WPS433

    requested = tuple(return_layers)
    unknown = [l for l in requested if l not in REQUIRED_LAYERS]
    if unknown:
        raise KeyError(
            f"Unknown layers {unknown}; valid layers: {REQUIRED_LAYERS}"
        )

    audio_path = Path(audio_path)
    if not audio_path.exists():
        raise FileNotFoundError(audio_path)

    # Lazy imports — keep module import cheap so test discovery doesn't
    # pull torch+librosa for every collection.
    from Musical_Intelligence.brain.executor import execute  # noqa: WPS433
    from Musical_Intelligence.ear import H3Extractor, R3Extractor  # noqa: WPS433

    nuclei, h3_demands = _collect_mechanisms(strict=strict)

    mel, audio_t = _load_audio_to_mel(audio_path)

    r3_extractor = R3Extractor()
    h3_extractor = H3Extractor()

    with torch.no_grad():
        r3_out = r3_extractor.extract(mel, audio=audio_t, sr=SAMPLE_RATE)
        r3_features = r3_out.features  # (B=1, T, 97)
        h3_out = h3_extractor.extract(r3_features, h3_demands)
        h3_features = h3_out.features  # dict[tuple -> (B, T)] tensors
        outputs, ram, neuro = execute(nuclei, h3_features, r3_features)

    out: Dict[str, Any] = {}

    if "r3" in requested:
        # Squeeze batch dim → (T, 97). Bit-identical determinism is asserted on
        # this layer specifically (it is the cheapest of the 6 to validate).
        out["r3"] = _to_numpy(r3_features.squeeze(0))

    if "h3" in requested:
        # H³ tuples are sparse — return as dict, NOT stacked, so that
        # downstream code can address a specific (r3_idx, horizon, morph, law).
        out["h3"] = {key: _to_numpy(val.squeeze(0) if val.ndim == 2 else val)
                     for key, val in h3_features.items()}

    if "c3" in requested:
        # Per-mechanism (T, D_mech). Using mech NAME as key (matches V6 A2).
        out["c3"] = {name: _to_numpy(t.squeeze(0)) for name, t in outputs.items()}

    if "ram" in requested:
        out["ram"] = _to_numpy(ram.squeeze(0))  # (T, 26)

    if "neuro" in requested:
        out["neuro"] = _to_numpy(neuro.squeeze(0))  # (T, 4)

    if "beliefs" in requested:
        out["beliefs"] = _run_beliefs(outputs, h3_features, strict=strict)

    return out


def _run_beliefs(
    outputs: Dict[str, Any],
    h3_features: Dict[Tuple[int, int, int, int], Any],
    strict: bool = False,
) -> Dict[str, Dict[str, np.ndarray]]:
    """Run the paper's 8 Core beliefs. Empty context (V6 A2 convention).

    Skips beliefs whose mechanism is not in `outputs` (early-failed mechs);
    callers can detect skipped beliefs by absence of the key in the returned
    dict.

    Args:
        strict: If True, re-raise any belief-import or run_cycle exception
            instead of warning + continuing.
    """
    import torch  # noqa: WPS433

    traces: Dict[str, Dict[str, np.ndarray]] = {}
    for fn, mech_key, mod_path, cls_name in _BELIEF_REGISTRY:
        if mech_key not in outputs:
            continue
        try:
            mod = importlib.import_module(mod_path)
            cls = getattr(mod, cls_name)
            inst = cls()
        except Exception as e:
            if strict:
                raise
            print(
                f"[runner] WARN belief {cls_name} import/instantiate failed "
                f"for mech {mech_key}: {e!r}",
                file=sys.stderr,
            )
            continue

        with torch.no_grad():
            try:
                result = inst.run_cycle(
                    mechanism_output=outputs[mech_key],
                    context={},
                    h3_features=h3_features,
                )
            except Exception as e:
                if strict:
                    raise
                print(
                    f"[runner] WARN belief {cls_name} run_cycle failed for "
                    f"mech {mech_key}: {e!r}",
                    file=sys.stderr,
                )
                continue

        traces[f"{fn}_{cls_name}"] = {
            "pi_pred": _to_numpy(result["pi_pred"][0]),
            "pe": _to_numpy(result["pe"][0]),
            "posterior": _to_numpy(result["posterior"][0]),
            "obs": _to_numpy(result["obs"][0]),
        }
    return traces
