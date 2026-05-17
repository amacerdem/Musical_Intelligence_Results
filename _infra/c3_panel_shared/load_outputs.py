"""Cache loaders for Musical_Intelligence_Outputs/<category>/<dataset>/.

Per-dataset functions encapsulate the join-key contract between pooled.csv and
targets.csv. No analysis script reimplements join logic.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from .engine_pin_check import V_REPRO_ROOT, EXPECTED_SHA, assert_dataset_cache_sha

CACHE_ROOT = V_REPRO_ROOT / "Musical_Intelligence_Outputs"

# emotify-specific: targets.csv uses global int 1..400 with per-genre offsets,
# while pooled.csv uses '<genre>_<stem>' strings (stem 1..100 within each genre).
EMOTIFY_GENRE_OFFSET: dict[str, int] = {
    "classical": 0,
    "rock": 100,
    "electronic": 200,
    "pop": 300,
}

GEMS_9: tuple[str, ...] = (
    "amazement", "solemnity", "tenderness", "nostalgia", "calmness",
    "power", "joyful_activation", "tension", "sadness",
)
# 7 of the 9 GEMS labels are C³-testable; `nostalgia` (autobiographical, not in
# engine ontology) and `power` (R³-readable, owned by axis-1 not C³) are
# excluded at intake. Authority: C3-Cognitive-Signals/data/emotify/labels.md.
EMOTIFY_INSCOPE_LABELS: tuple[str, ...] = (
    "amazement", "solemnity", "tenderness", "calmness",
    "joyful_activation", "tension", "sadness",
)


def emotify_paths() -> dict[str, Path]:
    base = CACHE_ROOT / "emotion" / "emotify"
    return {
        "base": base,
        "manifest": base / "manifest.json",
        "pooled": base / "pooled.csv",
        "pooled_pct": base / "pooled_pct.csv",
        "targets": base / "targets.csv",
        "per_frame_dir": base / "per_frame",
    }


def load_emotify_pooled() -> pd.DataFrame:
    return pd.read_csv(emotify_paths()["pooled"])


def load_emotify_targets_raw() -> pd.DataFrame:
    """Return the 8,408-row per-rater table, with header columns stripped of
    leading/trailing whitespace ('genre' had a leading space in the source CSV).
    """
    df = pd.read_csv(emotify_paths()["targets"])
    df.columns = [c.strip() for c in df.columns]
    df["genre"] = df["genre"].astype(str).str.strip()
    return df


def _emotify_build_join_key(genre: str, clip_id_int: int) -> str:
    if genre not in EMOTIFY_GENRE_OFFSET:
        raise KeyError(f"unknown emotify genre: {genre!r}")
    within = clip_id_int - EMOTIFY_GENRE_OFFSET[genre]
    return f"{genre}_{within}"


def load_emotify_per_rater_long() -> pd.DataFrame:
    """8,408-row long table joined to pooled clip_id via the genre-offset rule.

    Adds a 'clip_id' column matching pooled.csv (e.g. 'pop_82'), and keeps the
    original integer in 'clip_id_int' for traceability.
    """
    df = load_emotify_targets_raw()
    df = df.rename(columns={"clip_id": "clip_id_int"})
    df["clip_id"] = [
        _emotify_build_join_key(g, c) for g, c in zip(df["genre"], df["clip_id_int"])
    ]
    return df


def load_emotify_targets_aggregated(emotion_columns: Iterable[str] = GEMS_9,
                                    extra_binary: Iterable[str] = ("liked", "disliked")) -> pd.DataFrame:
    """Per-clip targets: 400 rows × (genre, clip_id, n_raters, mean(GEMS_9), mean(liked/disliked)).

    Means over per-rater binary 0/1 responses = proportion of raters endorsing
    that label for that clip.
    """
    long = load_emotify_per_rater_long()
    binary_cols = list(emotion_columns) + list(extra_binary)
    agg = long.groupby(["clip_id", "genre"], as_index=False).agg(
        n_raters=("clip_id_int", "count"),
        **{c: (c, "mean") for c in binary_cols},
    )
    return agg


def load_emotify_joined(emotion_columns: Iterable[str] = GEMS_9,
                        extra_binary: Iterable[str] = ("liked", "disliked"),
                        verify_sha: bool = True) -> pd.DataFrame:
    """One-stop loader for per-clip MI outputs ⨝ aggregated human ratings.

    Returns a 400-row DataFrame with:
        - clip_id (string '<genre>_<stem>')
        - genre, n_raters
        - aggregated proportions for each emotion column + liked/disliked
        - every engine column from pooled.csv (R3_*, MECH_*, RAM_*, NEURO_*, BELIEF_*)

    Halts on engine SHA mismatch and on row-count anomalies.
    """
    paths = emotify_paths()
    if verify_sha:
        assert_dataset_cache_sha(paths["manifest"], expected_sha=EXPECTED_SHA)

    pooled = load_emotify_pooled()
    tgt_agg = load_emotify_targets_aggregated(emotion_columns=emotion_columns, extra_binary=extra_binary)

    joined = pooled.merge(tgt_agg, on="clip_id", how="inner", validate="one_to_one")
    if len(joined) != 400:
        raise RuntimeError(
            f"Emotify join produced {len(joined)} rows, expected 400. "
            f"Pooled: {len(pooled)}, targets-agg: {len(tgt_agg)}."
        )
    return joined


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "smoke":
        joined = load_emotify_joined()
        print(f"OK loaded {len(joined)} rows × {joined.shape[1]} cols")
        print("genre dist:", joined["genre"].value_counts().to_dict())
        print("sample clip_ids:", joined["clip_id"].head(3).tolist(),
              "...", joined["clip_id"].tail(2).tolist())
        # quick header sanity
        for col in ("joyful_activation", "liked", "MECH_VMM__P0:perceived_happy",
                    "RAM_13", "NEURO_DA", "BELIEF_0"):
            assert col in joined.columns, f"missing column: {col}"
        print("schema sanity: PASS")
    else:
        print("usage: load_outputs.py smoke")
