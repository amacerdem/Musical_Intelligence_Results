#!/usr/bin/env python3
"""Patch hardcoded old V-Reproduction paths → MI_Results engine_outputs/.

Patterns (in order):
  1) `"engine_outputs"`  → `"engine_outputs"`
  2) `"engine_outputs"`               → `"engine_outputs"`
  3) `engine_outputs` (any remaining)                    → `engine_outputs`

Targets: every .py under MI_Results, excluding .venv, __pycache__, Musical_Intelligence/.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PATTERNS = [
    (re.compile(r'"Science"\s*/\s*"V-Reproduction"\s*/\s*"engine_outputs"'),
     '"engine_outputs"'),
    (re.compile(r'"V-Reproduction"\s*/\s*"engine_outputs"'),
     '"engine_outputs"'),
    (re.compile(r'engine_outputs'),
     'engine_outputs'),
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
