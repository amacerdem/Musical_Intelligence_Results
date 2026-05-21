#!/usr/bin/env python3
"""Round 2: patch remaining old hardcoded paths to MI_Results layout."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PATTERNS = [
    # 05.3 + 05.5: BOLD checkpoints
    (re.compile(r'"datasets/paper-anchors/mech-region/bold-26region/checkpoints"'),
     '"datasets/paper-anchors/mech-region/bold-26region/checkpoints"'),
    (re.compile(r'"Science"\s*/\s*"Bold-fMRI"\s*/\s*"exp-02-cross-subject-17"\s*/\s*"checkpoints"'),
     '"datasets" / "paper-anchors" / "mech-region" / "bold-26region" / "checkpoints"'),

    # 05.5 + 05.6: per_subject_per_region_r.csv
    (re.compile(r'"Science/Bold-fMRI/ds003720/06_encoding/per_subject_per_region_r\.csv"'),
     '"datasets/paper-anchors/voxelwise-encoding/per_subject_per_region_r.csv"'),
    (re.compile(r'"Bold-fMRI"\s*/\s*"ds003720"\s*/\s*"06_encoding"\s*/\s*"per_subject_per_region_r\.csv"'),
     '"datasets" / "paper-anchors" / "voxelwise-encoding" / "per_subject_per_region_r.csv"'),
    (re.compile(r'"Science"\s*/\s*"Bold-fMRI"\s*/\s*"ds003720"\s*/\s*"06_encoding"\s*/\s*"per_subject_per_region_r\.csv"'),
     '"datasets" / "paper-anchors" / "voxelwise-encoding" / "per_subject_per_region_r.csv"'),

    # 05.5: ckpt_bold under Science/V2 reviewer-sims
    (re.compile(
        r'"Science/V2/reviewer-sims/[^"]+/ckpt_bold"'),
     '"datasets/paper-anchors/voxelwise-encoding/ckpt_bold"'),
    (re.compile(
        r'"Science"\s*/\s*"V2"\s*/\s*"reviewer-sims"\s*/[^,)]+?"ckpt_bold"'),
     '"datasets" / "paper-anchors" / "voxelwise-encoding" / "ckpt_bold"'),
]

def patch_file(p: Path) -> int:
    try:
        text = p.read_text()
    except Exception:
        return 0
    orig = text
    for rx, repl in PATTERNS:
        text = rx.sub(repl, text)
    if text != orig:
        p.write_text(text)
        return 1
    return 0

def main():
    SKIP = {".venv", "__pycache__", "Musical_Intelligence"}
    changed = []
    for p in ROOT.rglob("*.py"):
        if any(s in p.parts for s in SKIP):
            continue
        if patch_file(p):
            changed.append(str(p.relative_to(ROOT)))
    print(f"Patched {len(changed)} files:")
    for f in changed:
        print(f"  {f}")

if __name__ == "__main__":
    main()
