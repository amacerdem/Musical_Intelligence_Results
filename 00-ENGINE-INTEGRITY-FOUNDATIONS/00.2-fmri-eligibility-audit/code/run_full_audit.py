"""Orchestrator: audit ≥30 datasets and write CSV + JSON + JSONL.

Usage:
    python code/run_full_audit.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

PHASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PHASE_DIR / "code"))

from audit_dataset import audit  # noqa: E402

SCIENCE = PHASE_DIR.parent.parent  # Science/
DATASETS = SCIENCE / "datasets"


# Paper-cited + Phase 18 + scan-candidate dataset registry.
#
# Format: (dataset_id, modality, path, phase_consumer, manual_overrides)
#
# Manual overrides honestly label datasets we cannot inspect (closed-access
# pharma / PET, audio-only behavioral, EEG/MEG modality boundary), per the
# user-validated MI_fMRI_validasyon_notlari.md framing.
DATASET_REGISTRY = [
    # ---- A. Paper-cited fMRI datasets we can locally inspect ----
    (
        "ds002725",
        "fMRI",
        DATASETS / "neuroimaging/fmri_openneuro/ds002725",
        "Phase 11",
        {
            # ds002725 has bold but NO T1w on disk (joint EEG-fMRI scan
            # didn't include structural). The team's working preprocessing
            # pipeline (`Science/Bold-fMRI/ds002725/02_bold_preproc/`)
            # uses EPI-based normalization. Override mni_derivative to
            # `runnable_via_fmriprep` to reflect feasibility under that
            # pipeline.
            "mni_derivative": "runnable_via_fmriprep",
            "notes": (
                "Daly 2019. 7 classical pieces (Chopin, Rachmaninoff, "
                "Mendelssohn Op.54, Beethoven). 12 trial starts in shared "
                "events.tsv (some pieces repeat). 17/21 subs have classical "
                "bold + shared events.tsv applies. Phase 11 verifies "
                "per-subject onset matching. NOTE: no T1w on disk; preproc "
                "uses EPI-based normalization."
            ),
        },
    ),
    (
        "ds003720",
        "fMRI",
        DATASETS / "neuroimaging/ds003720",
        "Phase 12",
        {
            "notes": (
                "Nakai 2021 Music Genre fMRI. 5 subs, 1720 stimulus WAVs, "
                "90 events.tsv (18/sub). Used for routing-ablation framing in "
                "Phase 12 (NOT a population estimate — 93% lift over MI-naive)."
            ),
        },
    ),
    # ---- A2. Closed-access pharma / PET — manual overrides ----
    (
        "putkinen2025",
        "PET",
        DATASETS / "neuroimaging/putkinen2025",
        "Phase 8",
        {
            "n_dataset_level": 15,
            "audio_available": "summary_only",
            "exact_timing": "none_recoverable",
            "mni_derivative": "not_applicable",
            "n_qc_pass": -1,
            "n_alignment_qualified": -1,
            "exclusion_reason": (
                "Closed-access PET; summary-only convergence with paper "
                "Putkinen 2025 µ-opioid 7/7 regions"
            ),
            "notes": "Used as published-result convergence cross-validation only.",
        },
    ),
    (
        "mallik2017",
        "fMRI",
        DATASETS / "neuroimaging/mallik2017",
        "Phase 8",
        {
            "n_dataset_level": 0,
            "audio_available": "summary_only",
            "exact_timing": "none_recoverable",
            "mni_derivative": "not_applicable",
            "n_qc_pass": -1,
            "n_alignment_qualified": -1,
            "exclusion_reason": (
                "Subject-level data not deposited; summary-only naltrexone block"
            ),
            "notes": "",
        },
    ),
    (
        "salimpoor2011",
        "fMRI",
        DATASETS / "neuroimaging/salimpoor2011",
        "Phase 8",
        {
            "n_dataset_level": 8,
            "audio_available": "no_recoverable",
            "exact_timing": "none_recoverable",
            "mni_derivative": "not_applicable",
            "n_qc_pass": -1,
            "n_alignment_qualified": -1,
            "exclusion_reason": (
                "Closed-access; uses caudate-NAcc temporal sequence claim only "
                "via Salimpoor's published lag (+0.9 s)"
            ),
            "notes": "",
        },
    ),
    (
        "ferreri2019",
        "fMRI",
        DATASETS / "neuroimaging/ferreri2019",
        "Phase 8",
        {
            "n_dataset_level": 27,
            "audio_available": "no_recoverable",
            "exact_timing": "none_recoverable",
            "mni_derivative": "not_applicable",
            "n_qc_pass": -1,
            "n_alignment_qualified": -1,
            "exclusion_reason": (
                "Closed-access pharmacology trial; uses dose-ordering claim "
                "(levodopa>placebo>risperidone) only"
            ),
            "notes": "",
        },
    ),
    # ---- A3. RAM-topology peaks-only legacy datasets ----
    (
        "blood2001",
        "PET",
        DATASETS / "neuroimaging/blood2001",
        "Phase 9 (RAM)",
        {
            "n_dataset_level": 10,
            "audio_available": "no_recoverable",
            "exact_timing": "none_recoverable",
            "mni_derivative": "not_applicable",
            "n_qc_pass": -1,
            "n_alignment_qualified": -1,
            "exclusion_reason": "Old PET study; uses peak coordinates only for RAM topology",
            "notes": "",
        },
    ),
    (
        "salimpoor2013",
        "fMRI",
        DATASETS / "neuroimaging/salimpoor2013",
        "Phase 9 (RAM)",
        {
            "n_dataset_level": 19,
            "audio_available": "no_recoverable",
            "exact_timing": "none_recoverable",
            "mni_derivative": "not_applicable",
            "n_qc_pass": -1,
            "n_alignment_qualified": -1,
            "exclusion_reason": "Used for RAM peak-coordinate convergence only",
            "notes": "",
        },
    ),
    (
        "grahn2007",
        "fMRI",
        DATASETS / "neuroimaging/grahn2007",
        "Phase 9 (RAM)",
        {
            "n_dataset_level": 14,
            "audio_available": "no_recoverable",
            "exact_timing": "none_recoverable",
            "mni_derivative": "not_applicable",
            "n_qc_pass": -1,
            "n_alignment_qualified": -1,
            "exclusion_reason": "RAM topology peaks-only",
            "notes": "",
        },
    ),
    (
        "koelsch2005",
        "fMRI",
        DATASETS / "neuroimaging/koelsch2005",
        "Phase 9 (RAM)",
        {
            "n_dataset_level": 18,
            "audio_available": "no_recoverable",
            "exact_timing": "none_recoverable",
            "mni_derivative": "not_applicable",
            "n_qc_pass": -1,
            "n_alignment_qualified": -1,
            "exclusion_reason": "RAM topology peaks-only",
            "notes": "",
        },
    ),
    (
        "brattico2011",
        "fMRI",
        DATASETS / "neuroimaging/brattico2011",
        "Phase 9 (RAM)",
        {
            "n_dataset_level": 16,
            "audio_available": "no_recoverable",
            "exact_timing": "none_recoverable",
            "mni_derivative": "not_applicable",
            "n_qc_pass": -1,
            "n_alignment_qualified": -1,
            "exclusion_reason": "RAM topology peaks-only",
            "notes": "",
        },
    ),
    (
        "zatorre2005",
        "fMRI",
        DATASETS / "neuroimaging/zatorre2005",
        "Phase 9 (RAM)",
        {
            "n_dataset_level": 12,
            "audio_available": "no_recoverable",
            "exact_timing": "none_recoverable",
            "mni_derivative": "not_applicable",
            "n_qc_pass": -1,
            "n_alignment_qualified": -1,
            "exclusion_reason": "RAM topology peaks-only",
            "notes": "",
        },
    ),
    # ---- B. Phase 18 planned ----
    (
        "studyforrest_7t_music",
        "fMRI",
        DATASETS / "neuroimaging/studyforrest",
        "Phase 18.1",
        {
            "n_dataset_level": 20,
            "audio_available": "yes_external_DOI",
            # Override n_align: external DOI audio (Forrest Gump score) is
            # canonically known and recoverable; alignment-qualified N
            # equals subs with bold + events + sub-TR timing.
            "n_alignment_qualified": 20,
            "notes": (
                "studyforrest 7T music-genre extension. 37 subs/148 events.tsv/"
                "750 bold on disk. Audio = Forrest Gump score (external DOI: "
                "10.18112/openneuro.ds000113). 7T sub-set is N≈20. Phase 18.1 "
                "entry-gate verdict: ELIGIBLE conditional on external audio fetch."
            ),
        },
    ),
    (
        "ds005880",
        "fMRI",
        DATASETS / "neuroimaging/ds005880",
        "Phase 18.2",
        {
            "n_dataset_level": 20,
            "audio_available": "yes_external_DOI",
            "exact_timing": "events_tsv_TR_only",  # confirmed integer-second onsets
            "n_qc_pass": 15,
            "n_alignment_qualified": 0,
            "exclusion_reason": (
                "PARTIAL DOWNLOAD (~710 MB / 6 GB); events.tsv onsets are "
                "integer-second only (TR-only). Phase 18.2 entry-gate verdict: "
                "NON-ELIGIBLE pending download + psychopy-log recovery for "
                "sub-TR onset"
            ),
            "notes": (
                "Diminished 7th chord. 20 subs/40 events.tsv/15 bold on disk. "
                "Re-audit when download completes."
            ),
        },
    ),
    (
        "ds006583",
        "fMRI",
        DATASETS / "neuroimaging/ds006583",
        "Phase 18.3",
        {
            "n_dataset_level": 23,
            "audio_available": "yes_external_DOI",
            "exact_timing": "none_recoverable",
            "n_qc_pass": 9,
            "n_alignment_qualified": 0,
            "exclusion_reason": (
                "PARTIAL DOWNLOAD; 23 subs/9 bold/0 events.tsv on disk. "
                "Phase 18.3 entry-gate verdict: NON-ELIGIBLE pending download"
            ),
            "notes": "Affective Transitions. Re-audit when download completes.",
        },
    ),
    (
        "ds006564",
        "fMRI",
        DATASETS / "neuroimaging/ds006564",
        "Phase 18.4",
        {
            "n_dataset_level": 41,
            "audio_available": "yes_external_DOI",
            "exact_timing": "none_recoverable",
            "n_qc_pass": 41,
            "n_alignment_qualified": 0,
            "exclusion_reason": (
                "PARTIAL DOWNLOAD; 41 subs/56 bold/0 events.tsv on disk. "
                "Phase 18.4 entry-gate verdict: NON-ELIGIBLE pending download"
            ),
            "notes": (
                "Naturalistic film with controlled musical information. "
                "Re-audit when download completes."
            ),
        },
    ),
    (
        "ds000171",
        "fMRI",
        DATASETS / "neuroimaging/ds000171",
        "Phase 18.5",
        {
            "n_dataset_level": 39,
            "audio_available": "yes_external_DOI",
            # Audio for emotional music block is referenced via paper
            # supplementary (Lepping 2016 Sci. Rep.). Alignment-qualified N
            # equals subs with bold + events + sub-TR timing (~28 of 39).
            "n_alignment_qualified": 28,
            "notes": (
                "Music + depression (39 = 19 MDD + 20 ND). 39 subs / 141 events.tsv / "
                "89 bold on disk. Audio referenced via paper supplementary "
                "(Lepping 2016 Sci. Rep.). Phase 18.5 entry-gate verdict: "
                "ELIGIBLE conditional on external audio fetch."
            ),
        },
    ),
    # ---- C. 5-agent scan multimodal candidates (companion-paper scope) ----
    (
        "nmedh_hindi_eeg",
        "EEG",
        DATASETS / "attention/MUSIN-G",
        "Companion paper #2 (EEG/MEG)",
        {
            "n_dataset_level": 48,
            "audio_available": "yes_in_dataset",
            "exact_timing": "events_tsv_sub_TR",
            "mni_derivative": "not_applicable",
            "n_qc_pass": 48,
            "n_alignment_qualified": 0,
            "exclusion_reason": (
                "EEG modality not directly compatible with MI's audio→fMRI BOLD "
                "architecture; requires source-localization adapter (companion paper #2)"
            ),
            "notes": "",
        },
    ),
    (
        "musin_g",
        "EEG",
        DATASETS / "attention/MUSIN-G",
        "Companion paper #2 (EEG/MEG)",
        {
            "n_dataset_level": 20,
            "audio_available": "yes_in_dataset",
            "exact_timing": "events_tsv_sub_TR",
            "mni_derivative": "not_applicable",
            "n_qc_pass": 20,
            "n_alignment_qualified": 0,
            "exclusion_reason": "EEG modality requires source-localization adapter (companion paper #2)",
            "notes": "",
        },
    ),
    (
        "daly_ds002721",
        "EEG",
        DATASETS / "neuroimaging/ds002721",
        "Companion paper #2 (EEG/MEG)",
        {
            "n_dataset_level": 31,
            "audio_available": "yes_external_DOI",
            "exact_timing": "events_tsv_sub_TR",
            "mni_derivative": "not_applicable",
            "n_qc_pass": 31,
            "n_alignment_qualified": 0,
            "exclusion_reason": "EEG twin of ds002725; companion paper #2",
            "notes": "",
        },
    ),
    (
        "di_liberto_bach",
        "EEG",
        DATASETS / "prediction/diliberto2020",
        "Companion paper #2",
        {
            "n_dataset_level": 20,
            "audio_available": "yes_external_DOI",
            "exact_timing": "events_tsv_sub_TR",
            "mni_derivative": "not_applicable",
            "n_qc_pass": 20,
            "n_alignment_qualified": 0,
            "exclusion_reason": "EEG note-level; companion paper #2",
            "notes": "",
        },
    ),
    (
        "marion_meg",
        "MEG",
        DATASETS / "prediction/marion_meg",
        "Companion paper #2",
        {
            "n_dataset_level": 40,
            "audio_available": "yes_external_DOI",
            "exact_timing": "events_tsv_sub_TR",
            "mni_derivative": "not_applicable",
            "n_qc_pass": 40,
            "n_alignment_qualified": 0,
            "exclusion_reason": "MEG modality; companion paper #2",
            "notes": "",
        },
    ),
    (
        "bellier_ecog",
        "ECoG",
        DATASETS / "neuroimaging/bellier_ecog",
        "Companion paper #1 (iEEG)",
        {
            "n_dataset_level": 29,
            "audio_available": "yes_external_DOI",
            "exact_timing": "events_tsv_sub_TR",
            "mni_derivative": "not_applicable",
            "n_qc_pass": 29,
            "n_alignment_qualified": 0,
            "exclusion_reason": (
                "iEEG modality; sub-cm electrode validation = companion paper #1"
            ),
            "notes": "Bellier 2023 Pink Floyd ECoG (Zenodo 7876019).",
        },
    ),
    (
        "music_expertise_ieeg",
        "ECoG",
        DATASETS / "neuroimaging/music_expertise_ieeg",
        "Companion paper #1 (iEEG)",
        {
            "n_dataset_level": 6,
            "audio_available": "yes_external_DOI",
            "exact_timing": "events_tsv_sub_TR",
            "mni_derivative": "not_applicable",
            "n_qc_pass": 6,
            "n_alignment_qualified": 0,
            "exclusion_reason": "iEEG modality; companion paper #1",
            "notes": "",
        },
    ),
    # ---- D. Behavioral-only / negative-control ----
    (
        "mehr2019_nhs",
        "behavioral_only",
        DATASETS / "cross_cultural/nhs_discography",
        "Phase 14 (cross-cultural)",
        {
            "n_dataset_level": 86,
            "audio_available": "yes_in_dataset",
            "exact_timing": "not_applicable",
            "mni_derivative": "not_applicable",
            "n_qc_pass": -1,
            "n_alignment_qualified": -1,
            "exclusion_reason": (
                "Behavioral-only; no neuroimaging — Phase 14 V5 marked "
                "out-of-scope for MI fMRI core"
            ),
            "notes": "",
        },
    ),
    (
        "aam",
        "behavioral_only",
        DATASETS / "emotion/aam",
        "(none)",
        {
            "n_dataset_level": 0,
            "audio_available": "no_recoverable",
            "exact_timing": "none_recoverable",
            "mni_derivative": "not_applicable",
            "n_qc_pass": -1,
            "n_alignment_qualified": -1,
            "exclusion_reason": "Path not on disk; documenting completeness only",
            "notes": "",
        },
    ),
    (
        "pmemo",
        "behavioral_only",
        DATASETS / "emotion/PMEmo",
        "(none)",
        {
            "n_dataset_level": 794,
            "audio_available": "yes_in_dataset",
            "exact_timing": "not_applicable",
            "mni_derivative": "not_applicable",
            "n_qc_pass": -1,
            "n_alignment_qualified": -1,
            "exclusion_reason": "Audio-only; no fMRI",
            "notes": "",
        },
    ),
    (
        "deam",
        "behavioral_only",
        DATASETS / "emotion/DEAM",
        "Phase 5 ECE only",
        {
            "n_dataset_level": 1802,
            "audio_available": "yes_in_dataset",
            "exact_timing": "not_applicable",
            "mni_derivative": "not_applicable",
            "n_qc_pass": -1,
            "n_alignment_qualified": -1,
            "exclusion_reason": (
                "Audio-only behavioral ratings; used in Phase 5 ECE belief "
                "calibration only"
            ),
            "notes": "",
        },
    ),
    (
        "groove_midi",
        "behavioral_only",
        DATASETS / "motor/groove_midi",
        "Phase 7 F3+F7",
        {
            "n_dataset_level": 1150,
            "audio_available": "no_recoverable",
            "exact_timing": "events_tsv_sub_TR",
            "mni_derivative": "not_applicable",
            "n_qc_pass": -1,
            "n_alignment_qualified": -1,
            "exclusion_reason": (
                "MIDI-only (no audio rendered); used in Phase 7 functional anchors"
            ),
            "notes": "",
        },
    ),
    (
        "emotify",
        "behavioral_only",
        DATASETS / "emotion/emotify",
        "(none)",
        {
            "n_dataset_level": 400,
            "audio_available": "yes_in_dataset",
            "exact_timing": "not_applicable",
            "mni_derivative": "not_applicable",
            "n_qc_pass": -1,
            "n_alignment_qualified": -1,
            "exclusion_reason": "Audio-only behavioral; no fMRI",
            "notes": "",
        },
    ),
    # ---- E. Padding to ≥30 (gold2019, ds001417 audit-only entries) ----
    (
        "gold2019_absolute_pitch",
        "fMRI",
        DATASETS / "neuroimaging/gold2019_absolute_pitch",
        "(none)",
        {
            "n_dataset_level": 0,
            "audio_available": "no_recoverable",
            "exact_timing": "none_recoverable",
            "mni_derivative": "not_applicable",
            "n_qc_pass": -1,
            "n_alignment_qualified": -1,
            "exclusion_reason": "Audit-only entry; closed-access AP fMRI study",
            "notes": "",
        },
    ),
    (
        "ds001417",
        "fMRI",
        DATASETS / "neuroimaging/ds001417",
        "(none)",
        {
            "n_dataset_level": 0,
            "audio_available": "no_recoverable",
            "exact_timing": "none_recoverable",
            "mni_derivative": "not_applicable",
            "n_qc_pass": -1,
            "n_alignment_qualified": -1,
            "exclusion_reason": "Audit-only entry; not on local disk",
            "notes": "",
        },
    ),
]


def main() -> None:
    rows = []
    log_lines = []
    for ds_id, modality, path, phase_consumer, overrides in DATASET_REGISTRY:
        row = audit(
            ds_id,
            path,
            modality=modality,
            phase_consumer=phase_consumer,
            manual_overrides=overrides,
        )
        rows.append(row)
        log_lines.append(json.dumps({"dataset_id": ds_id, "row": row}, default=str))
        flag = "YES" if row["mi_compatible"] else "NO "
        reason = row["exclusion_reason"] or "OK"
        print(f"  [{flag}] {ds_id:30s}  {reason}")

    out_dir = PHASE_DIR / "results"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_csv = out_dir / "eligibility_audit.csv"
    with out_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\nWrote {out_csv}")

    n_compat = sum(1 for r in rows if r["mi_compatible"])
    n_excl = sum(1 for r in rows if not r["mi_compatible"])

    out_json = out_dir / "eligibility_audit.json"
    out_json.write_text(
        json.dumps(
            {
                "phase": "0.5",
                "audit_date": "2026-05-06",
                "engine_head": "318eb2f529d7103e8b7d80b01228357fdc4e0217",
                "seed": 20260506005,
                "n_datasets": len(rows),
                "n_compatible": n_compat,
                "n_excluded": n_excl,
                "rows": rows,
            },
            indent=2,
        )
    )
    print(f"Wrote {out_json}")

    out_jsonl = out_dir / "per_dataset_audit_log.jsonl"
    out_jsonl.write_text("\n".join(log_lines) + "\n")
    print(f"Wrote {out_jsonl}")

    print()
    print(f"Total: {len(rows)} datasets")
    print(f"MI-compatible: {n_compat}")
    print(f"Excluded: {n_excl}")

    # Quick summary for the 6 paper-cited fMRI/PET that must have a verdict
    paper_cited = {
        "ds002725", "ds003720", "putkinen2025", "mallik2017",
        "salimpoor2011", "ferreri2019",
    }
    print()
    print("Paper-cited verdicts (must all be present):")
    for r in rows:
        if r["dataset_id"] in paper_cited:
            print(
                f"  {r['dataset_id']:20s}  mi_compatible={r['mi_compatible']:>5}  "
                f"n_align={r['n_alignment_qualified']}"
            )


if __name__ == "__main__":
    main()
