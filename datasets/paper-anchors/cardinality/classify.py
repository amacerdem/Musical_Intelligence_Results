#!/usr/bin/env python3
"""
Classify raw_constants_inventory.csv rows into provenance buckets.

Buckets per ticket:
  LIT-FROZEN     — value from a cited paper (Sethares 1993 coefficients,
                   Bastos 2012 delays, Krumhansl-Kessler profiles, Bowling
                   intervals 12-TET frequencies, etc.).
  CALIB-BOWLING  — tuned once on Bowling N=13 (F1-BCH relay gains + R³ Group-A
                   consonance gains).
  HAND-TUNED     — set by authors without a cited source and not calibrated
                   on a dataset (reward formula weights τ / w_trend / w_period /
                   w_ctx, generic mixture weights in non-citation context).
  STRUCTURAL     — dimension counts, topology, r3 indices, horizon/morph/law
                   codes, channel indices, Brodmann areas, MNI coordinates,
                   citation years, LayerSpec ranges — declared architectural
                   choices that are not free parameters.
  NULL-FALLBACK  — defaults like 0.0 / 1 / None placeholders for zero-state
                   initializers, clamp bounds with TODO context, or
                   unambiguously-zero literals inside padding.

Classification heuristics (applied in order; first match wins):

  1. If name matches {Citation.arg1, Citation.arg2}             -> STRUCTURAL
     (Citation(author, year, ...) — year is structural literature metadata)
  2. If name matches {_h3.*, LayerSpec.*, H3DemandSpec.*}       -> STRUCTURAL
     (H3 demand codes + LayerSpec range codes — topology, not parameters)
  3. If name in regions/ and arg index 0/1/2 of mni_coords      -> STRUCTURAL
     (MNI coordinates are anatomical reference, not fit parameters)
  4. If name == ".index"  (region index) or Brodmann-area-like  -> STRUCTURAL
  5. If context mentions Bowling 2018 OR file is f1/mechanisms/bch/**
     AND is a numeric weight (not structural code)              -> CALIB-BOWLING
  6. If file in ear/r3/groups/a_consonance/ AND name is Group-A
     gain / weight                                               -> CALIB-BOWLING
  7. If row is a link-weight-posarg2 (RegionLink weight) and
     has literature citation in context                          -> LIT-FROZEN
     (link weights are literature-seeded, not Bowling-fit)
  8. If row is NeuroLink weight (link-weight-posarg2 or 3) and
     has literature citation                                     -> LIT-FROZEN
  9. If has_citation_in_context=1 AND value is non-trivial
     (not in {0, 1, -1, 2, 0.0, 1.0})                           -> LIT-FROZEN
 10. If context contains TODO/FIXME/STUB                         -> NULL-FALLBACK
 11. If value in {0, 0.0, 1, 1.0, -1, None-equivalent} AND
     expr-literal kind and no citation                           -> NULL-FALLBACK
 12. If file in brain/reward.py OR name contains 'reward' AND
     value is float weight AND no citation                       -> HAND-TUNED
 13. If expr-literal and value is fractional weight (0.xx) AND
     no citation AND scope is compute_*                          -> HAND-TUNED
 14. If ann-assign/class-attr/module-assign with value looking
     structural (int ≤ 100 representing dim/index/channel) AND
     name in {CHANNEL, OUTPUT_DIM, N, NUM_, INDEX, SIZE, LEN,
             LAYER, DEPTH, HORIZON, MORPH, LAW}                  -> STRUCTURAL
 15. Fallback                                                    -> HAND-TUNED

Output: parameter_provenance_table.csv with columns
  file_path, line, scope, name, value, dtype, kind, bucket, bucket_reason,
  citation_author, citation_year, context_line
"""
from __future__ import annotations

import csv
import re
from pathlib import Path
from collections import Counter

HERE = Path(__file__).parent
RAW = HERE / "raw_constants_inventory.csv"
OUT = HERE / "parameter_provenance_table.csv"


STRUCTURAL_NAME_TOKENS = (
    "CHANNEL", "OUTPUT_DIM", "NUM_", "N_CHANNELS", "NUM_CHANNELS",
    "INDEX", "_DIM", "SIZE", "LEN_", "LAYER", "DEPTH",
    "HORIZON", "MORPH", "LAW", "FRAME_RATE", "SAMPLE_RATE",
    "HOP_LENGTH", "N_FFT", "N_MELS", "BLOCK", "BOUNDARY",
)

BOWLING_CALIB_PATHS = (
    "brain/functions/f1/mechanisms/bch/",
    "ear/r3/groups/a_consonance/",
)

REWARD_PATHS = (
    "brain/reward.py",
    "brain/functions/f6/mechanisms/",  # Reward function
)


# Known Bowling-calibrated variable names (from R3.md §A5 + BCH code inspection).
BOWLING_CALIB_VAR_TOKENS = (
    "_GAIN",
    "_COEFF",
    "_SCALE",
    "gain_",
)


# Reward formula weights (from paper Eq(1)): 1.5 surprise, 0.8 resolution,
# 0.5 exploration, -0.6 monotony, 0.5 familiarity peak, 0.6/0.4 wanting/liking.
REWARD_HANDTUNED_TOKENS = (
    "w_surprise", "w_resolution", "w_exploration", "w_monotony",
    "wanting_split", "liking_split", "fam_peak", "familiarity_peak",
    "eta", "delta",
    "W_TREND", "W_PERIOD", "W_CTX", "TAU",
)


# Values that look like pure null/zero-fallback placeholders when expr-literal.
NULL_VALS = {"0", "0.0", "1", "1.0", "-1", "-1.0"}


def is_structural_name(name: str) -> bool:
    u = name.upper()
    for tok in STRUCTURAL_NAME_TOKENS:
        if tok in u:
            return True
    # MNI / arg position-based (e.g., RegionLink.arg2 is a weight, so NOT structural)
    return False


def is_region_mni_or_index(row: dict) -> bool:
    p = row["file_path"]
    if not p.startswith("brain/regions/"):
        return False
    name = row["name"]
    # Region(index=..., mni_coords=(...), brodmann_area=...) — all structural.
    if ".index" in name or ".mni_coords" in name or ".brodmann_area" in name:
        return True
    return False


def is_citation_meta(row: dict) -> bool:
    """Citation(author, year, ...) — year arg. LayerSpec / _h3 — structural codes."""
    name = row["name"]
    kind = row["kind"]
    if name.startswith("Citation.") and kind.startswith("citation-call"):
        return True
    if kind.startswith("spec-numeric"):
        # r3_idx, horizon, morph, law — all structural
        return True
    return False


def is_link_weight(row: dict) -> bool:
    name = row["name"]
    kind = row["kind"]
    if kind == "link-weight-posarg2" and name.startswith("RegionLink."):
        return True  # weight is 3rd arg (index 2)
    if name.startswith("NeuroLink.") and kind in ("link-weight-posarg2", "link-weight-posarg3"):
        # NeuroLink has two shapes:
        #   NeuroLink("dim", channel_int, "effect", weight_float, "cit")  -> posarg3 is weight
        #   NeuroLink("dim", "channel_str", weight_float, "cit")          -> posarg2 is weight
        # Non-weight positional args (channel ints) we classify below separately.
        try:
            v = float(row["value"])
            if 0.0 <= v <= 1.0 and row["dtype"] in ("float", "negfloat"):
                return True
        except ValueError:
            pass
    return False


def is_neurolink_channel_idx(row: dict) -> bool:
    """NeuroLink.arg1 (channel int) is structural, not a weight."""
    name = row["name"]
    kind = row["kind"]
    if kind == "link-weight-posarg1" and name.startswith("NeuroLink."):
        return True
    return False


def bowling_scope(row: dict) -> bool:
    p = row["file_path"]
    for pref in BOWLING_CALIB_PATHS:
        if p.startswith(pref):
            return True
    return False


def has_lit_citation(row: dict) -> bool:
    return row.get("has_citation_in_context") == "1"


def value_is_trivial_null(row: dict) -> bool:
    v = row["value"]
    if v in NULL_VALS:
        return True
    return False


def classify(row: dict) -> tuple[str, str]:
    name = row["name"]
    value = row["value"]
    kind = row["kind"]
    path = row["file_path"]
    scope = row["scope"]

    # 1. Citation + spec metadata -> STRUCTURAL
    if is_citation_meta(row):
        return "STRUCTURAL", "citation-metadata-or-spec-code"

    # 2. Region MNI / index / brodmann -> STRUCTURAL
    if is_region_mni_or_index(row):
        return "STRUCTURAL", "region-anatomical-coord-or-index"

    # 3. NeuroLink channel index (arg1) -> STRUCTURAL
    if is_neurolink_channel_idx(row):
        return "STRUCTURAL", "neurolink-channel-index"

    # 4. Structural-name tokens (CHANNEL, OUTPUT_DIM, NUM_X, etc.) -> STRUCTURAL
    if is_structural_name(name) and kind in ("module-assign", "class-attr", "ann-assign"):
        return "STRUCTURAL", "structural-name-token"

    # 5. Link weights (RegionLink weight, NeuroLink weight) -> LIT-FROZEN if cited
    if is_link_weight(row):
        if has_lit_citation(row):
            return "LIT-FROZEN", "link-weight-with-citation"
        return "HAND-TUNED", "link-weight-without-citation"

    # 6. Bowling-calibrated scope + reward-like weight
    if bowling_scope(row):
        # Separate structural codes (already caught above) — the rest are
        # calibrated gains or literature-derived dissonance coefficients.
        # Only the gains that are NOT already a literature coefficient count
        # as CALIB-BOWLING. Simple heuristic: if the context line cites Bowling
        # or Sethares/Plomp (dissonance) — the latter is LIT-FROZEN; the
        # former is CALIB-BOWLING. If citation author in known-Bowling-set
        # (Bowling, Body), tag CALIB-BOWLING. Else if other citation, LIT-FROZEN.
        ctx = row.get("context_line", "").lower()
        cit_author = row.get("citation_author", "").lower()
        if "bowling" in ctx or "bowling" in cit_author:
            return "CALIB-BOWLING", "explicit-bowling-reference"
        if has_lit_citation(row):
            return "LIT-FROZEN", "bowling-scope-with-non-bowling-citation"
        # No citation, in Bowling-calib scope, non-trivial numeric -> CALIB-BOWLING
        if value not in NULL_VALS:
            return "CALIB-BOWLING", "bowling-scope-no-citation-weight"

    # 7. Reward-formula hand-tuned tokens
    for tok in REWARD_HANDTUNED_TOKENS:
        if tok in name:
            return "HAND-TUNED", f"reward-handtuned-name-token:{tok}"

    # 8. Has literature citation -> LIT-FROZEN (if value is not trivial-null)
    if has_lit_citation(row) and not value_is_trivial_null(row):
        return "LIT-FROZEN", "literature-citation-in-context"

    # 9. Trivial null placeholders
    if value_is_trivial_null(row) and kind == "expr-literal":
        return "NULL-FALLBACK", "trivial-null-expr-literal"
    if value_is_trivial_null(row) and not has_lit_citation(row):
        return "NULL-FALLBACK", "trivial-null-no-citation"

    # 10. TODO/STUB in context
    if row.get("has_todo_fixme") == "1":
        return "NULL-FALLBACK", "todo-fixme-context"

    # 11. In-expression literals inside compute_* functions (weights / thresholds) — HAND-TUNED
    if kind == "expr-literal":
        # weights with no citation inside mechanism compute functions
        if "def compute" in scope or "def observe" in scope or "def predict" in scope:
            return "HAND-TUNED", "expr-literal-in-compute-no-citation"
        return "HAND-TUNED", "expr-literal-no-citation"

    # 12. Non-expr literals with no citation
    #  - Function default args: likely architectural knobs (epsilon, padding) - NULL-FALLBACK if 0/1
    #  - call-kw with numeric values - often framework params (torch.clamp min/max) - NULL-FALLBACK
    if kind in ("call-kw", "call-posarg0", "call-posarg1", "call-posarg2", "call-posarg3",
                "call-posarg4", "call-posarg5"):
        # clamp/min/max/eps-looking
        if value in ("0.0", "0", "1.0", "1", "-1", "-1.0"):
            return "NULL-FALLBACK", "framework-kw-arg-trivial"
        return "HAND-TUNED", "call-arg-no-citation"

    # 13. Module-assign / class-attr / ann-assign with no citation and non-trivial value
    if kind in ("module-assign", "class-attr", "ann-assign"):
        if value in ("0", "0.0", "1", "1.0"):
            return "NULL-FALLBACK", "module-assign-trivial"
        # Non-trivial module constant with no citation is likely architectural
        # knob or hand-tuned threshold. Default: HAND-TUNED.
        return "HAND-TUNED", "module-assign-no-citation"

    # 14. arg-default / kw-default — function knobs
    if kind in ("arg-default", "kw-default"):
        if value in NULL_VALS:
            return "NULL-FALLBACK", "arg-default-trivial"
        return "HAND-TUNED", "arg-default-no-citation"

    return "HAND-TUNED", "fallback"


def main() -> int:
    rows = list(csv.DictReader(RAW.open()))
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([
            "file_path", "line", "scope", "name", "value", "dtype", "kind",
            "bucket", "bucket_reason",
            "citation_author", "citation_year", "context_line",
        ])
        bucket_counts: Counter[str] = Counter()
        for r in rows:
            bucket, reason = classify(r)
            bucket_counts[bucket] += 1
            w.writerow([
                r["file_path"], r["line"], r["scope"], r["name"],
                r["value"], r["dtype"], r["kind"],
                bucket, reason,
                r.get("citation_author", ""), r.get("citation_year", ""),
                r.get("context_line", "")[:200],
            ])
    print("Bucket counts:")
    total = sum(bucket_counts.values())
    for b, c in bucket_counts.most_common():
        print(f"  {b:15s} {c:6d}  {100*c/total:5.1f}%")
    print(f"  TOTAL            {total:6d}")
    print(f"\noutput: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
