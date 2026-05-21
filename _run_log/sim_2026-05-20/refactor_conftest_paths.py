#!/usr/bin/env python3
"""Refactor conftest path bootstrap: cache-only mode.

Replaces the Musical_Intelligence/ear/r3/extractor.py source-tree scan with
a cache-aware MI_Results root detection (engine_outputs/ + _infra/ presence).
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

OLD = re.compile(
    r"_PROJECT_ROOT\s*=\s*_THIS\.parent\s*\n"
    r"for\s+_\s+in\s+range\(\d+\):\s*\n"
    r"\s*if\s+\(_PROJECT_ROOT\s*/\s*\"Musical_Intelligence\"\s*/\s*\"ear\".*?\n"
    r"\s*break\s*\n"
    r"(?:\s*#[^\n]*\n)*"
    r"\s*if\s+\(_PROJECT_ROOT\s*/\s*\"engine\".*?\n"
    r"\s*_PROJECT_ROOT\s*=\s*_PROJECT_ROOT\s*/\s*\"engine\"\s*\n"
    r"\s*break\s*\n"
    r"\s*_PROJECT_ROOT\s*=\s*_PROJECT_ROOT\.parent\s*\n"
    r"else:\s*\n"
    r"\s*raise\s+RuntimeError\(f\"Could not locate Musical_Intelligence[^\"]*\"\)",
    re.DOTALL,
)

NEW = (
    "_PROJECT_ROOT = _THIS.parent\n"
    "for _ in range(8):\n"
    "    # Cache-only mode: MI_Results root has engine_outputs/ + _infra/\n"
    "    if (_PROJECT_ROOT / \"engine_outputs\").is_dir() and (_PROJECT_ROOT / \"_infra\").is_dir():\n"
    "        break\n"
    "    _PROJECT_ROOT = _PROJECT_ROOT.parent\n"
    "else:\n"
    "    raise RuntimeError(f\"Could not locate MI_Results from {_THIS}\")"
)


def patch(path: Path) -> bool:
    text = path.read_text()
    new = OLD.sub(NEW, text)
    if new == text:
        return False
    path.write_text(new)
    return True


def main():
    files = []
    for cf in sorted(ROOT.rglob("conftest.py")):
        if ".venv" in cf.parts or "Musical_Intelligence" in cf.parts:
            continue
        if patch(cf):
            files.append(str(cf.relative_to(ROOT)))
    print(f"Patched {len(files)} conftest.py files:")
    for f in files:
        print(f"  {f}")


if __name__ == "__main__":
    main()
