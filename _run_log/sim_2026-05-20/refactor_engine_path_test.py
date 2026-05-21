#!/usr/bin/env python3
"""Refactor test_engine_path_resolves → cache-aware (engine_outputs/ presence).

Cache-only mode: engine source is not vendored. Replace the source-tree
existence check with a check that the cache root is present.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

OLD = re.compile(
    r"def test_engine_path_resolves\(project_root\):\s*\n"
    r"\s*\"\"\"[^\"]*?\"\"\"\s*\n"
    r"\s*engine_root\s*=\s*project_root\s*/\s*\"Musical_Intelligence\"\s*\n"
    r"\s*assert engine_root\.exists\(\)[^\n]*\n"
    r"\s*assert \(engine_root\s*/\s*\"ear\".*?[^\n]*\n"
    r"(?:\s*f\"Engine[^\n]*\n)?",
    re.DOTALL,
)

NEW = '''def test_engine_path_resolves(project_root):
    """Cache-only mode: engine_outputs/ root must be present.

    The reviewer reproduction path is the deposited cache, not the live
    engine; this test verifies the cache root exists rather than the
    Musical_Intelligence/ source tree.
    """
    cache_root = project_root / "engine_outputs"
    assert cache_root.exists(), f"Cache root not found at {cache_root}"
    assert (cache_root / "_aggregate_sha.txt").exists(), \\
        f"Engine SHA marker missing at {cache_root}/_aggregate_sha.txt"
'''


def patch(path: Path) -> bool:
    text = path.read_text()
    new = OLD.sub(NEW, text)
    if new == text:
        return False
    path.write_text(new)
    return True


def main():
    targets = list(ROOT.glob("*/*/L1_engine_pin/test_engine_pin.py")) + \
              list(ROOT.glob("*/*/L1_spec_compliance/test_spec_*.py"))
    patched = []
    for p in targets:
        if patch(p):
            patched.append(str(p.relative_to(ROOT)))
    print(f"Patched {len(patched)}/{len(targets)}:")
    for f in patched:
        print(f"  {f}")


if __name__ == "__main__":
    main()
