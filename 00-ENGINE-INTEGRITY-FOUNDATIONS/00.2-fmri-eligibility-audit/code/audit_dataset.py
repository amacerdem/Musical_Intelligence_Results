"""Per-dataset eligibility audit. Single function returns one row dict.

The returned dict matches `code/schema_eligibility.json`. The function is
deterministic and side-effect free — it only inspects the file system.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

PHASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PHASE_DIR / "code"))

from audit_helpers import (  # noqa: E402
    find_bids_root,
    has_audio,
    parse_events_resolution,
    has_mni_derivative,
    count_qc_pass_subjects,
    estimate_alignment_qualified_n,
)


def audit(
    dataset_id: str,
    dataset_path: Path,
    *,
    modality: str = "fMRI",
    phase_consumer: str = "",
    manual_overrides: Optional[dict] = None,
) -> dict:
    """Audit one dataset; return a row matching schema_eligibility.json.

    ``manual_overrides`` may set fields where automation cannot decide
    (closed-access PET, supplementary-only summaries, behavioral-only).
    """
    manual_overrides = dict(manual_overrides or {})

    if not dataset_path.exists():
        return {
            "dataset_id": dataset_id,
            "modality": modality,
            "n_dataset_level": int(manual_overrides.get("n_dataset_level", 0)),
            "audio_available": manual_overrides.get(
                "audio_available", "no_recoverable"
            ),
            "exact_timing": manual_overrides.get(
                "exact_timing", "none_recoverable"
            ),
            "mni_derivative": manual_overrides.get(
                "mni_derivative", "not_applicable"
            ),
            "n_qc_pass": int(manual_overrides.get("n_qc_pass", -1)),
            "n_alignment_qualified": int(
                manual_overrides.get("n_alignment_qualified", -1)
            ),
            "mi_compatible": False,
            "exclusion_reason": manual_overrides.get(
                "exclusion_reason", "Local path not present"
            ),
            "phase_consumer": phase_consumer,
            "notes": manual_overrides.get("notes", ""),
        }

    bids_root = find_bids_root(dataset_path) or dataset_path

    audio_verdict, audio_files = has_audio(bids_root)
    timing_verdict, timing_resolution_ms = parse_events_resolution(bids_root)
    mni_verdict = has_mni_derivative(bids_root)
    n_qc_pass = count_qc_pass_subjects(bids_root)
    n_align = estimate_alignment_qualified_n(
        bids_root,
        audio_files,
        timing_resolution_ms,
        timing_verdict=timing_verdict,
    )

    # Manual overrides take precedence (e.g., closed-access PET / supplementary-only).
    audio_verdict = manual_overrides.get("audio_available", audio_verdict)
    timing_verdict = manual_overrides.get("exact_timing", timing_verdict)
    mni_verdict = manual_overrides.get("mni_derivative", mni_verdict)
    n_qc_pass = int(manual_overrides.get("n_qc_pass", n_qc_pass))
    n_align = int(manual_overrides.get("n_alignment_qualified", n_align))

    mi_compatible = (
        audio_verdict in ("yes_in_dataset", "yes_external_DOI")
        and timing_verdict in ("events_tsv_sub_TR", "recoverable_from_logs")
        and mni_verdict in ("present", "runnable_via_fmriprep")
        and n_align >= 1
    )

    parts = []
    if audio_verdict not in ("yes_in_dataset", "yes_external_DOI"):
        parts.append(f"audio={audio_verdict}")
    if timing_verdict not in ("events_tsv_sub_TR", "recoverable_from_logs"):
        parts.append(f"timing={timing_verdict}")
    if mni_verdict not in ("present", "runnable_via_fmriprep"):
        parts.append(f"mni={mni_verdict}")
    if n_align < 1:
        parts.append(f"n_align={n_align}")

    if mi_compatible:
        exclusion_reason = ""
    elif "exclusion_reason" in manual_overrides:
        exclusion_reason = manual_overrides["exclusion_reason"]
    else:
        exclusion_reason = "; ".join(parts) if parts else ""

    return {
        "dataset_id": dataset_id,
        "modality": modality,
        "n_dataset_level": int(
            manual_overrides.get("n_dataset_level", n_qc_pass if n_qc_pass >= 0 else 0)
        ),
        "audio_available": audio_verdict,
        "exact_timing": timing_verdict,
        "mni_derivative": mni_verdict,
        "n_qc_pass": n_qc_pass,
        "n_alignment_qualified": n_align,
        "mi_compatible": mi_compatible,
        "exclusion_reason": exclusion_reason,
        "phase_consumer": phase_consumer,
        "notes": manual_overrides.get("notes", ""),
    }
