"""Common helpers for stream scripts: archive prior CSV, update segment manifest,
embed engine SHA + seed in outputs.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def archive_existing(path: Path) -> None:
    if not path.exists():
        return
    it_dir = path.parent / "iterations"
    it_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive = it_dir / f"{stamp}__{path.name}"
    path.rename(archive)
    print(f"   archived prior {path.name} → iterations/{archive.name}")


def write_csv(df: pd.DataFrame, path: Path, engine_sha: str, seed: int | None = None) -> None:
    df = df.copy()
    df["engine_sha"] = engine_sha
    if seed is not None:
        df["seed"] = seed
    path.parent.mkdir(parents=True, exist_ok=True)
    archive_existing(path)
    df.to_csv(path, index=False)


def update_manifest(manifest_path: Path, dataset_id: str, segment: str,
                   engine_sha: str, claim: dict[str, Any]) -> None:
    """Add/replace a single claim by claim_id."""
    existing = {}
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text())
    claims = [c for c in existing.get("claims", []) if c.get("claim_id") != claim["claim_id"]]
    claim = dict(claim)
    claim["engine_sha"] = engine_sha
    claim.setdefault("ran_at", now_iso())
    claims.append(claim)
    manifest = {
        "dataset_id": dataset_id,
        "segment": segment,
        "engine_sha": engine_sha,
        "last_updated": now_iso(),
        "claims": sorted(claims, key=lambda c: c.get("claim_id", "")),
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2))


def fig_footer(seed: int, engine_sha: str, segment: str, dataset: str, stream: str) -> str:
    return f"engine_sha={engine_sha[:16]}...  seed={seed}  {segment}/{dataset}/{stream}"


def write_report(report_path: Path, stream_id: str, name: str,
                 engine_sha: str, seed: int, verdict: str,
                 key_stats: dict[str, Any], headlines: list[str],
                 caveats: list[str] | None = None,
                 files: list[str] | None = None) -> None:
    """Auto-generate a markdown report for a single S<N> stream."""
    lines: list[str] = []
    lines.append(f"# {stream_id} — {name}")
    lines.append("")
    lines.append(f"- **Engine SHA:** `{engine_sha[:16]}...`")
    lines.append(f"- **Seed:** {seed}")
    lines.append(f"- **Ran at:** {now_iso()}")
    lines.append(f"- **Verdict:** **{verdict}**")
    lines.append("")
    if key_stats:
        lines.append("## Key statistics")
        lines.append("")
        for k, v in key_stats.items():
            if isinstance(v, float):
                lines.append(f"- `{k}` = {v:.4f}")
            else:
                lines.append(f"- `{k}` = {v}")
        lines.append("")
    if headlines:
        lines.append("## Headline findings")
        lines.append("")
        for h in headlines:
            lines.append(f"- {h}")
        lines.append("")
    if caveats:
        lines.append("## Caveats")
        lines.append("")
        for c in caveats:
            lines.append(f"- {c}")
        lines.append("")
    if files:
        lines.append("## Files")
        lines.append("")
        for f in files:
            lines.append(f"- `{f}`")
        lines.append("")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines))


def is_done(report_path: Path, engine_sha: str) -> bool:
    """Check if a stream's report exists for the current engine SHA."""
    if not report_path.exists():
        return False
    txt = report_path.read_text()
    return engine_sha[:16] in txt
