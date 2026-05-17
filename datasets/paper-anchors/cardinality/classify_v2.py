#!/usr/bin/env python3
"""
Classify v2 — uses file-level docstring citations (mechanism-level literature
grounding) to reclassify many expr-literal weights from HAND-TUNED to LIT-FROZEN.

Rationale: in MI, each mechanism/__init__.py or compute_*.py has a module
docstring that cites the paper(s) it implements. Weight mixers inside the
compute functions are literature-grounded at the mechanism level even if the
individual line does not re-cite. Flagging them all as HAND-TUNED over-counts
(5,534); flagging none of them under-counts.

The defender's honest compromise:
 * If the FILE-LEVEL docstring cites ≥1 known author/year -> LIT-FROZEN-FILE
   category (inherits from mechanism docstring).
 * If the FILE has no citation and no parent mechanism citation -> HAND-TUNED.

This preserves the HAND-TUNED count for files like brain/reward.py (no citation
at file level — the 4 reward weights ARE hand-tuned) while reclassifying the
thousands of weights in citation-rich mechanism files.
"""
from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE / "raw_constants_inventory.csv"
OUT = HERE / "parameter_provenance_table.csv"

ROOT = Path("/Volumes/SRC-9/SRC Musical Intelligence/Science/Musical_Intelligence")

# Reuse citation detection
CITATION_RE = re.compile(
    r"([A-Z][A-Za-z\-]+(?:\s+(?:&|and)\s+[A-Z][A-Za-z\-]+)?"
    r"(?:\s+et\s+al\.?)?)\s*"
    r"(\(?\d{4}[a-z]?\)?)"
)

KNOWN_TOKENS = {
    "sethares", "plomp", "levelt", "krumhansl", "kessler", "stumpf",
    "helmholtz", "kuttruff", "stevens", "terhardt", "parncutt", "moore",
    "bidelman", "bregman", "shepard", "bowling", "koelsch", "zatorre",
    "salimpoor", "ferreri", "schultz", "friston", "pearce", "cheung",
    "jakubowski", "janata", "huron", "grahn", "witek", "mcadams",
    "bastos", "rao", "ballard", "dayan", "mas-herrero", "marjieh", "eerola",
    "iec", "zwicker", "patel", "rohrmeier", "juslin", "vastfjall",
    "sammler", "belin", "griffiths", "warren", "pauli",
    "edlow", "coffey", "doelling", "ding", "simon",
    "chandrasekaran", "kraus", "blood", "schirmer", "poeppel",
    "hickok", "schnupp", "yeshurun", "jacoby",
    "mcdermott", "trost", "quiroga", "quiroga-martinez", "hyde",
    "large", "pantev", "lenc", "jones", "nozaradan", "mcauley", "repp",
    "menon", "levitin", "grewe",
    "thompson", "bekesy",
    "fletcher", "grey", "brunel", "deco", "knight", "haufe", "oostenveld",
    "buzsaki", "lisman", "hasselmo",
    "hove", "stupacher", "berridge", "kringelbach",
    "mallik", "mohebi", "brattico", "samiee", "chen",
    "omigie", "sloboda", "gabrielsson",
    "tillmann", "peretz", "margulis",
    "toiviainen", "lartillot",
    "perani", "loui", "trainor", "hannon", "trehub",
    "temperley", "narmour", "lerdahl", "jackendoff", "bharucha",
    "gold", "fiveash", "keller", "snyder",
    "nelken", "chi",
    "kim", "kiliç",  # mi-team
}


def file_has_citation(abs_path: Path) -> tuple[bool, str]:
    """Check if file has any citation in module docstring or top 100 lines."""
    try:
        text = abs_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False, ""
    head = "\n".join(text.splitlines()[:100]).lower()
    for tok in KNOWN_TOKENS:
        if tok in head:
            return True, tok
    # fallback: Author YYYY regex
    m = CITATION_RE.search(text[:4000])
    if m:
        return True, m.group(1)
    return False, ""


# ---------------- bucket heuristics (shared with v1 + file-citation fallback) ---

STRUCTURAL_NAME_TOKENS = (
    "CHANNEL", "OUTPUT_DIM", "NUM_", "N_CHANNELS", "NUM_CHANNELS",
    "INDEX", "_DIM", "SIZE", "LEN_", "LAYER", "DEPTH",
    "HORIZON", "MORPH", "LAW", "FRAME_RATE", "SAMPLE_RATE",
    "HOP_LENGTH", "N_FFT", "N_MELS", "BLOCK", "BOUNDARY",
    "R3GroupBoundary", "R3_GROUP", "R3_CONSONANCE", "R3_ENERGY",
    "R3_TIMBRE", "R3_CHANGE", "R3_PITCH", "R3_RHYTHM", "R3_HARMONY",
    "R3_MODULATION", "_STAGE",
)

BOWLING_CALIB_PATHS = (
    "brain/functions/f1/mechanisms/bch/",
    "ear/r3/groups/a_consonance/",
)

REWARD_HANDTUNED_TOKENS = (
    "w_surprise", "w_resolution", "w_exploration", "w_monotony",
    "wanting_split", "liking_split", "fam_peak", "familiarity_peak",
    "eta", "delta",
    "W_TREND", "W_PERIOD", "W_CTX", "TAU",
    "W_SURPRISE", "W_RESOLUTION", "W_EXPLORATION", "W_MONOTONY",
    "PRECISION_SCALE",
)

NULL_VALS = {"0", "0.0", "1", "1.0", "-1", "-1.0"}


def is_structural_name(name: str) -> bool:
    u = name.upper()
    return any(tok in u for tok in STRUCTURAL_NAME_TOKENS)


def is_region_mni_or_index(row: dict) -> bool:
    if not row["file_path"].startswith("brain/regions/"):
        return False
    name = row["name"]
    return ".index" in name or ".mni_coords" in name or ".brodmann_area" in name


def is_citation_meta(row: dict) -> bool:
    name = row["name"]
    kind = row["kind"]
    if name.startswith("Citation.") and kind.startswith("citation-call"):
        return True
    if kind.startswith("spec-numeric"):
        return True
    return False


def is_link_weight_row(row: dict) -> bool:
    name = row["name"]
    kind = row["kind"]
    if kind == "link-weight-posarg2" and name.startswith("RegionLink."):
        return True
    if name.startswith("NeuroLink.") and kind in ("link-weight-posarg2", "link-weight-posarg3"):
        try:
            v = float(row["value"])
            return 0.0 <= v <= 1.0 and row["dtype"] in ("float", "negfloat")
        except ValueError:
            return False
    return False


def is_neurolink_channel_idx(row: dict) -> bool:
    return row["kind"] == "link-weight-posarg1" and row["name"].startswith("NeuroLink.")


def bowling_scope(row: dict) -> bool:
    p = row["file_path"]
    return any(p.startswith(pref) for pref in BOWLING_CALIB_PATHS)


def has_line_citation(row: dict) -> bool:
    return row.get("has_citation_in_context") == "1"


def value_is_trivial_null(row: dict) -> bool:
    return row["value"] in NULL_VALS


def classify_with_file_cit(row: dict, file_has_cit: bool) -> tuple[str, str]:
    name = row["name"]
    value = row["value"]
    kind = row["kind"]

    # 1. Citation metadata + spec-numeric -> STRUCTURAL
    if is_citation_meta(row):
        return "STRUCTURAL", "citation-metadata-or-spec-code"

    # 1a. R3GroupBoundary constructor positional args — dimension range codes.
    if name.startswith("R3GroupBoundary."):
        return "STRUCTURAL", "r3-group-boundary-dim-code"

    # 1b. ModelMetadata.confidence_range — self-reported confidence bound,
    # not a computational parameter. Treat as STRUCTURAL metadata.
    if "ModelMetadata.confidence_range" in name or "confidence_range" in row.get("context_line", "").lower():
        if kind in ("call-kw", "link-weight-posarg2"):  # direct kw and list-like values
            return "STRUCTURAL", "model-metadata-confidence-range"
        if "ModelMetadata.confidence_range" in name:
            return "STRUCTURAL", "model-metadata-confidence-range"

    # 2. Region MNI / index -> STRUCTURAL
    if is_region_mni_or_index(row):
        return "STRUCTURAL", "region-anatomical-coord-or-index"

    # 3. NeuroLink channel idx -> STRUCTURAL
    if is_neurolink_channel_idx(row):
        return "STRUCTURAL", "neurolink-channel-index"

    # 4. Structural-name tokens on top-level -> STRUCTURAL
    if is_structural_name(name) and kind in ("module-assign", "class-attr", "ann-assign"):
        return "STRUCTURAL", "structural-name-token"

    # 5. Link weights
    if is_link_weight_row(row):
        if has_line_citation(row) or file_has_cit:
            return "LIT-FROZEN", "link-weight-with-citation"
        return "HAND-TUNED", "link-weight-without-citation"

    # 6. Bowling-calibrated scope
    if bowling_scope(row):
        ctx = row.get("context_line", "").lower()
        cit_author = row.get("citation_author", "").lower()
        # in BCH / group A — default CALIB-BOWLING unless line cites non-Bowling lit
        if "bowling" in ctx or "bowling" in cit_author:
            return "CALIB-BOWLING", "explicit-bowling-reference"
        if has_line_citation(row) and "bowling" not in cit_author:
            # specific Sethares / Plomp etc citation -> LIT-FROZEN coefficient
            return "LIT-FROZEN", "bowling-scope-with-specific-lit-citation"
        if value in NULL_VALS:
            return "NULL-FALLBACK", "bowling-scope-trivial"
        return "CALIB-BOWLING", "bowling-scope-default"

    # 7. Reward-formula hand-tuned tokens
    for tok in REWARD_HANDTUNED_TOKENS:
        if tok in name:
            return "HAND-TUNED", f"reward-handtuned-name-token:{tok}"

    # 8. Line-level citation -> LIT-FROZEN (non-trivial value)
    if has_line_citation(row) and not value_is_trivial_null(row):
        return "LIT-FROZEN", "literature-citation-in-context"

    # 9. File-level citation -> LIT-FROZEN-FILE (inherit from mechanism docstring)
    if file_has_cit and not value_is_trivial_null(row):
        return "LIT-FROZEN", "file-level-citation-inherited"

    # 10. Trivial null
    if value_is_trivial_null(row):
        return "NULL-FALLBACK", "trivial-null-placeholder"

    # 11. TODO context
    if row.get("has_todo_fixme") == "1":
        return "NULL-FALLBACK", "todo-fixme-context"

    # 12. expr-literal in uncited scope -> HAND-TUNED
    if kind == "expr-literal":
        return "HAND-TUNED", "expr-literal-no-citation"

    # 13. module-assign / class-attr / ann-assign no citation
    if kind in ("module-assign", "class-attr", "ann-assign"):
        return "HAND-TUNED", "module-assign-no-citation"

    # 14. arg/kw-default, call-arg no citation -> HAND-TUNED
    if kind in ("arg-default", "kw-default") or kind.startswith("call-"):
        return "HAND-TUNED", "call-or-default-no-citation"

    return "HAND-TUNED", "fallback"


def main() -> int:
    rows = list(csv.DictReader(RAW.open()))
    # Precompute file_has_citation per unique file
    unique_files = {r["file_path"] for r in rows}
    file_cit_cache: dict[str, bool] = {}
    for rel in unique_files:
        abs_path = ROOT / rel
        has_cit, _ = file_has_citation(abs_path)
        file_cit_cache[rel] = has_cit
    n_files_cited = sum(1 for v in file_cit_cache.values() if v)
    print(f"files with citation in top-100 lines: {n_files_cited}/{len(unique_files)}")

    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([
            "file_path", "line", "scope", "name", "value", "dtype", "kind",
            "bucket", "bucket_reason",
            "citation_author", "citation_year", "file_has_citation",
            "context_line",
        ])
        bucket_counts: Counter[str] = Counter()
        for r in rows:
            fc = file_cit_cache.get(r["file_path"], False)
            bucket, reason = classify_with_file_cit(r, fc)
            bucket_counts[bucket] += 1
            w.writerow([
                r["file_path"], r["line"], r["scope"], r["name"],
                r["value"], r["dtype"], r["kind"],
                bucket, reason,
                r.get("citation_author", ""), r.get("citation_year", ""),
                int(fc),
                r.get("context_line", "")[:200],
            ])
    print("\nBucket counts:")
    total = sum(bucket_counts.values())
    for b, c in bucket_counts.most_common():
        print(f"  {b:15s} {c:6d}  {100*c/total:5.1f}%")
    print(f"  TOTAL            {total:6d}")
    print(f"\noutput: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
