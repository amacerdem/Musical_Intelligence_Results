#!/usr/bin/env python3
"""Add pytest_collection_modifyitems hook to skip engine-source-dependent
tests when engine is not vendored (cache-only reviewer mode).

Targets: pytest phase conftest.py files (01.1, 02.1).
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SNIPPET = '''

# ---------------------------------------------------------------------------
# Cache-only mode: skip engine-source-dependent tests if engine not vendored
# ---------------------------------------------------------------------------

def pytest_collection_modifyitems(config, items):
    """In cache-only mode (no Musical_Intelligence/ source vendored),
    skip all collected tests — the engine cannot be live-loaded.

    The reviewer reproduction path is engine_outputs cache + verify_full_ledger.py;
    this phase's pytest panel verifies the engine spec, which requires the
    engine source. Skipping (not failing) preserves the cache-only contract.
    """
    if (_PROJECT_ROOT / "Musical_Intelligence" / "ear" / "r3" / "extractor.py").exists():
        return  # engine present, run normally
    import pytest
    marker = pytest.mark.skip(reason="cache-only mode: engine source not vendored")
    for item in items:
        item.add_marker(marker)
'''


def patch(path: Path) -> bool:
    text = path.read_text()
    if "pytest_collection_modifyitems" in text:
        return False
    path.write_text(text + SNIPPET)
    return True


def main():
    targets = [
        ROOT / "01-R3-PERCEPTUAL-FRONT-END/01.1-r3-isolated-extended/conftest.py",
        ROOT / "02-T3-TEMPORAL-LAYER/02.1-t3-isolated-extended/conftest.py",
    ]
    for p in targets:
        if patch(p):
            print(f"patched: {p.relative_to(ROOT)}")
        else:
            print(f"skip (already has hook): {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
