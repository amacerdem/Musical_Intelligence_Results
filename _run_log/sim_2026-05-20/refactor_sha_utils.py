#!/usr/bin/env python3
"""Refactor: aggregate_engine_sha → cache-only manifest read.

Replaces source-tree SHA aggregation in each phase's _infra/sha_utils.py with
a function that reads the recorded canonical SHA from engine_outputs/_aggregate_sha.txt
(or falls back to _infra/manifests/engine_head.json). Engine source dir is
no longer required at test time.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

NEW_AGGREGATE_BODY = '''def aggregate_engine_sha(engine_root: Path | None = None) -> str:
    """Return the canonical engine aggregate SHA-256.

    Cache-only mode: reads the recorded SHA from engine_outputs/_aggregate_sha.txt
    (preferred) or _infra/manifests/engine_head.json. Engine source tree is
    NOT scanned — the cache + manifest are the load-bearing artefacts.

    The ``engine_root`` argument is accepted for backward compatibility but
    ignored; we read from the recorded value.
    """
    # Walk up to MI_Results root (contains engine_outputs/ and _infra/)
    here = Path(__file__).resolve()
    repo_root = None
    for parent in [here.parent, *here.parents]:
        if (parent / "engine_outputs").is_dir() and (parent / "_infra").is_dir():
            repo_root = parent
            break
    if repo_root is None:
        raise RuntimeError(f"Could not locate MI_Results from {here}")

    rec = repo_root / "engine_outputs" / "_aggregate_sha.txt"
    if rec.exists():
        return rec.read_text().strip()

    import json
    manifest = repo_root / "_infra" / "manifests" / "engine_head.json"
    return json.loads(manifest.read_text())["content_aggregate_sha256"]
'''


def patch(path: Path) -> bool:
    text = path.read_text()
    # Find existing function and replace
    pattern = re.compile(
        r'def aggregate_engine_sha\([^)]*\)[^:]*:\s*\n(?:.*\n)*?(?=\n\n|\Z|^def |^class )',
        re.MULTILINE
    )
    if not pattern.search(text):
        return False
    new_text = pattern.sub(NEW_AGGREGATE_BODY + "\n", text, count=1)
    if new_text == text:
        return False
    path.write_text(new_text)
    return True


def main():
    SHA_UTILS_FILES = sorted(ROOT.rglob("_infra/sha_utils.py"))
    SHA_UTILS_FILES = [p for p in SHA_UTILS_FILES
                      if ".venv" not in p.parts
                      and "Musical_Intelligence" not in p.parts]
    patched = []
    for p in SHA_UTILS_FILES:
        if patch(p):
            patched.append(str(p.relative_to(ROOT)))
    print(f"Patched {len(patched)}/{len(SHA_UTILS_FILES)} sha_utils.py files:")
    for f in patched:
        print(f"  {f}")


if __name__ == "__main__":
    main()
