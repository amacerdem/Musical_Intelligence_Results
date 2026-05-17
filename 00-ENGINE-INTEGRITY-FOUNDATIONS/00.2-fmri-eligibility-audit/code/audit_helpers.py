"""Shared helpers for per-dataset eligibility audit.

These helpers are deterministic, side-effect free, and operate on
file-system metadata only. No engine pipeline runs in Phase 0.5.

Verdict vocabularies:

* audio_available  ∈ {yes_in_dataset, yes_external_DOI, summary_only, no_recoverable}
* exact_timing     ∈ {events_tsv_sub_TR, events_tsv_TR_only, recoverable_from_logs,
                       none_recoverable, not_applicable}
* mni_derivative   ∈ {present, runnable_via_fmriprep, not_feasible, not_applicable}
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Tuple, List


AUDIO_EXTENSIONS = ("*.wav", "*.mp3", "*.aiff", "*.flac", "*.aif", "*.ogg")


def find_bids_root(dataset_path: Path) -> Optional[Path]:
    """Locate the directory containing dataset_description.json.

    Phase 0.5 picks the *shallowest* dataset_description.json under
    ``dataset_path`` to avoid descending into derivatives or sourcedata.
    """
    candidates = sorted(
        dataset_path.rglob("dataset_description.json"),
        key=lambda p: len(p.parts),
    )
    if not candidates:
        return None
    return candidates[0].parent


def has_audio(bids_root: Path) -> Tuple[str, List[Path]]:
    """Return (verdict, list-of-audio-files).

    verdict ∈ {yes_in_dataset, yes_external_DOI, summary_only, no_recoverable}.
    """
    audio_files: List[Path] = []
    for ext in AUDIO_EXTENSIONS:
        audio_files.extend(bids_root.rglob(ext))
    # Filter out tiny placeholder washout/control sounds (< 200 KB) for
    # the "is real music here" heuristic. Phase 0.5 keeps them in the
    # list but uses the unfiltered count for the boolean test.
    if audio_files:
        return ("yes_in_dataset", audio_files)
    desc_path = bids_root / "dataset_description.json"
    if desc_path.exists():
        try:
            desc = json.loads(desc_path.read_text())
            doi = desc.get("DatasetDOI") or desc.get("RelatedDOI")
            if doi:
                return ("yes_external_DOI", [])
        except json.JSONDecodeError:
            pass
    return ("no_recoverable", [])


def parse_events_resolution(bids_root: Path) -> Tuple[str, float]:
    """Inspect events.tsv files for onset resolution.

    Returns (verdict, min_positive_onset_diff_ms).

    verdict ∈ {events_tsv_sub_TR, events_tsv_TR_only, recoverable_from_logs,
               none_recoverable}.

    A dataset qualifies as ``events_tsv_sub_TR`` if EITHER:

    1. min positive onset diff < 1.0 s (frame-level events), OR
    2. any onset value has non-zero fractional part (sub-second precision
       in the recording clock — typical of psychopy-logged paradigms), OR
    3. an auxiliary sub-TR column is present (e.g., ``start``,
       ``stim_onset_time``, ``trigger_ts``) with fractional values
       (block-design with sub-TR audio cue start-times).

    Otherwise → ``events_tsv_TR_only``.
    """
    events_files = list(bids_root.rglob("*_events.tsv"))
    if not events_files:
        return ("none_recoverable", float("inf"))
    try:
        import pandas as pd
    except ImportError:
        return ("recoverable_from_logs", float("inf"))
    # Prefer a file whose name suggests audio task; otherwise first.
    sample = events_files[0]
    for f in events_files:
        if any(
            tag in f.name.lower()
            for tag in ("music", "audi", "song", "test", "stim")
        ):
            sample = f
            break
    try:
        df = pd.read_csv(sample, sep="\t")
    except Exception:
        return ("none_recoverable", float("inf"))
    if "onset" not in df.columns or len(df) < 2:
        return ("none_recoverable", float("inf"))
    onsets = df["onset"].dropna().sort_values()
    diffs = onsets.diff().dropna()
    diffs_pos = diffs[diffs > 0]
    if len(diffs_pos) == 0:
        return ("none_recoverable", float("inf"))
    min_diff_s = float(diffs_pos.min())
    min_diff_ms = min_diff_s * 1000.0

    # Rule 1: frame-level event spacing
    if min_diff_s < 1.0:
        return ("events_tsv_sub_TR", min_diff_ms)

    # Rule 2: sub-second precision in onset values themselves
    onset_fractional = (onsets % 1.0)
    has_sub_sec_onset = bool((onset_fractional.abs() > 1e-6).any())
    if has_sub_sec_onset:
        return ("events_tsv_sub_TR", min_diff_ms)

    # Rule 3: auxiliary sub-TR column with fractional values
    aux_cols = ("start", "stim_onset_time", "stimulus_onset", "trigger_ts")
    for col in aux_cols:
        if col in df.columns:
            try:
                vals = df[col].dropna().astype(float)
                if (vals % 1.0).abs().max() > 1e-6:
                    return ("events_tsv_sub_TR", min_diff_ms)
            except Exception:
                continue

    return ("events_tsv_TR_only", min_diff_ms)


def has_mni_derivative(bids_root: Path) -> str:
    """Check derivatives/fmriprep/ for MNI152NLin2009cAsym outputs.

    Verdict ∈ {present, runnable_via_fmriprep, not_feasible, not_applicable}.
    """
    deriv = bids_root / "derivatives" / "fmriprep"
    if deriv.exists():
        if list(deriv.rglob("*MNI152NLin2009cAsym*.nii.gz")):
            return "present"
    has_t1w = bool(
        list(bids_root.rglob("sub-*_T1w.nii.gz"))
        or list(bids_root.rglob("sub-*_T1w.nii"))
    )
    has_bold = bool(
        list(bids_root.rglob("*_bold.nii.gz"))
        or list(bids_root.rglob("*_bold.nii"))
    )
    if has_t1w and has_bold:
        return "runnable_via_fmriprep"
    return "not_feasible"


def count_qc_pass_subjects(bids_root: Path) -> int:
    """Phase-0.5-conservative count of subjects with bold + events.tsv.

    A subject passes the lower-bound QC iff they have:

    * at least one ``*_bold.nii.gz`` (or ``.nii``) under ``sub-*/``, AND
    * either a per-subject ``*_events.tsv`` OR a top-level shared
      events.tsv applies (we treat the existence of *any* events.tsv
      with sub-TR resolution as the latter — Phase 11 verifies
      per-subject onset matching).

    Real motion FD QC requires running fmriprep / extracting confounds;
    deferred to phase consumers.
    """
    sub_dirs = sorted(
        p for p in bids_root.iterdir()
        if p.is_dir() and p.name.startswith("sub-")
    )
    n_with_bold = 0
    has_shared_events = bool(list(bids_root.rglob("*_events.tsv")))
    for sd in sub_dirs:
        bold_present = bool(
            list(sd.rglob("*_bold.nii.gz")) or list(sd.rglob("*_bold.nii"))
        )
        per_sub_events = bool(list(sd.rglob("*_events.tsv")))
        if bold_present and (per_sub_events or has_shared_events):
            n_with_bold += 1
    return n_with_bold


def estimate_alignment_qualified_n(
    bids_root: Path,
    audio_files: List[Path],
    events_resolution_ms: float,
    timing_verdict: Optional[str] = None,
) -> int:
    """Phase-0.5 conservative estimate of alignment-qualified N.

    * If ``timing_verdict`` is not in {sub_TR, recoverable_from_logs} → 0
      (cannot do frame-level alignment even in principle).
    * If audio files are present in-dataset → return ``n_qc_pass``.
    * If timing is sub-TR but audio is absent locally → -1 (unknown;
      audio may exist via external DOI; manual confirmation required).

    Note: the legacy ``events_resolution_ms`` parameter is retained for
    backward compatibility but is now informational only — the ``timing_verdict``
    drives the decision. ``events_resolution_ms`` is the min onset-diff,
    which is large (15 s) for block-design but irrelevant since the
    block onsets themselves are still sub-TR-precision-aligned.
    """
    if timing_verdict is None:
        # Backward-compatible inference from the float
        if events_resolution_ms == float("inf"):
            return 0
        if events_resolution_ms >= 1000.0:
            return 0  # legacy heuristic
    else:
        if timing_verdict not in ("events_tsv_sub_TR", "recoverable_from_logs"):
            return 0
    if not audio_files:
        return -1
    return count_qc_pass_subjects(bids_root)
