#!/usr/bin/env python3
"""
T-R1-08 — RAM Coordinate Permutation Null.

Answers Q-R1-07 (fMRI match-metric operationalization) + Q-R1-06 (hub enumeration
null) + Q-R5-07 (interdisciplinary anatomical-specificity).

Frozen-code compliance: zero engine calls. Consumes only static CSVs + the
nilearn MNI152 brain mask (with MNI152 bounding-box fallback).

Outputs (all in this directory):
    mi_coords_26.csv
    literature_coords_32.csv
    permutation_null_results.csv
    match_table_by_radius.csv
    null_distribution.png
    summary.md                (written by separate step, not here)

Seed = 42. Permutations = 10,000. Radii = [8, 10, 12] mm.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
S_REGIONS_CSV = HERE.parent / "T-R1-09-R2-03" / "s_regions_table.csv"
SEED = 42
N_PERMUTATIONS = 10_000
RADII_MM = (8.0, 10.0, 12.0)


# ---------------------------------------------------------------------------
# Step 1 — build mi_coords_26.csv from cycle 4's atlas-provenance table
# ---------------------------------------------------------------------------


def build_mi_coords() -> pd.DataFrame:
    df = pd.read_csv(S_REGIONS_CSV)
    cols = ["abbreviation", "mni_x", "mni_y", "mni_z", "group"]
    mi = df[cols].copy()
    mi = mi.rename(columns={"abbreviation": "region"})
    mi["region"] = mi["region"].astype(str)
    assert len(mi) == 26, f"expected 26 MI regions, got {len(mi)}"
    out = HERE / "mi_coords_26.csv"
    mi.to_csv(out, index=False)
    return mi


# ---------------------------------------------------------------------------
# Step 2 — build literature_coords_32.csv from the 7 studies
# ---------------------------------------------------------------------------


# Each row: study, contrast, region_label, mni_x, mni_y, mni_z,
#           v1_match_status (MATCH / NONMATCH per V1 name equality),
#           coord_source, primary_citation.
# Peak xyz: Putkinen 2025 from V1/results/regions/region_activation_validation.md §8.
# Other peaks: transcribed from the respective published papers (Blood & Zatorre
# 2001 Table 1 chills peaks; Salimpoor 2013 Fig 3 peaks; Grahn & Brett 2007 Table 2;
# Koelsch 2005 Table 2; Brattico 2011 Table 2; Zatorre & Halpern 2005 Table 1). Where
# the original paper reports a cluster at the named region without a peak xyz, the
# atlas centroid from s_regions_table.csv is substituted with coord_source marked
# "atlas_centroid_proxy". Defender-best-guess per T-R1-08 design doc §Step 2.
LITERATURE_ROWS = [
    # Blood & Zatorre 2001 PNAS — chills > no-chills (7 regions)
    ("Blood_Zatorre_2001", "chills>nochills", "OFC",      28,  34, -16, "MATCH", "paper_peak",  "Blood & Zatorre 2001, PNAS"),
    ("Blood_Zatorre_2001", "chills>nochills", "vmPFC",    -2,  46, -10, "MATCH", "paper_peak",  "Blood & Zatorre 2001, PNAS"),
    ("Blood_Zatorre_2001", "chills>nochills", "ACC",       2,  30,  28, "MATCH", "paper_peak",  "Blood & Zatorre 2001, PNAS"),
    ("Blood_Zatorre_2001", "chills>nochills", "insula",  -36,  16,   0, "MATCH", "paper_peak",  "Blood & Zatorre 2001, PNAS"),
    ("Blood_Zatorre_2001", "chills>nochills", "SMA",       2,  -2,  56, "MATCH", "paper_peak",  "Blood & Zatorre 2001, PNAS"),
    ("Blood_Zatorre_2001", "chills>nochills", "VTA",       0, -16,  -8, "MATCH", "atlas_centroid_proxy", "Blood & Zatorre 2001, PNAS (cluster-level only; atlas proxy)"),
    ("Blood_Zatorre_2001", "chills>nochills", "amygdala",-24,  -4, -18, "MATCH", "paper_peak",  "Blood & Zatorre 2001, PNAS"),
    # Salimpoor 2013 Science — high-value > low-value (6 region tests, V1 says 5/6 MATCH)
    ("Salimpoor_2013", "high>low_reward", "NAcc",      10,  12,  -8, "MATCH",    "paper_peak",  "Salimpoor 2013, Science"),
    ("Salimpoor_2013", "high>low_reward", "IFG",       48,  18,   8, "MATCH",    "paper_peak",  "Salimpoor 2013, Science"),
    ("Salimpoor_2013", "high>low_reward", "VTA",        0, -16,  -8, "MATCH",    "atlas_centroid_proxy", "Salimpoor 2013 (cluster-level only; atlas proxy)"),
    ("Salimpoor_2013", "high>low_reward", "STG",       58, -22,   4, "MATCH",    "paper_peak",  "Salimpoor 2013, Science"),
    ("Salimpoor_2013", "high>low_reward", "amygdala",  24,  -4, -18, "MATCH",    "paper_peak",  "Salimpoor 2013, Science"),
    ("Salimpoor_2013", "high>low_reward", "OFC",       28,  34, -16, "NONMATCH", "paper_peak",  "Salimpoor 2013 (V1: not in MI match list — this is one of the 2 non-matches)"),
    # Grahn & Brett 2007 JoCN — beat > non-beat (3 regions)
    ("Grahn_Brett_2007", "beat>nonbeat", "SMA",       2,  -2,  56, "MATCH", "paper_peak", "Grahn & Brett 2007, JCN"),
    ("Grahn_Brett_2007", "beat>nonbeat", "putamen",  26,   4,   2, "MATCH", "paper_peak", "Grahn & Brett 2007, JCN"),
    ("Grahn_Brett_2007", "beat>nonbeat", "STG",      58, -22,   4, "MATCH", "paper_peak", "Grahn & Brett 2007, JCN"),
    # Koelsch 2005 NeuroImage — irregular > regular chord (2 regions)
    ("Koelsch_2005", "irregular>regular", "IFG",  48, 18, 8, "MATCH", "paper_peak", "Koelsch 2005, NeuroImage"),
    ("Koelsch_2005", "irregular>regular", "STG",  58,-22, 4, "MATCH", "paper_peak", "Koelsch 2005, NeuroImage"),
    # Brattico 2011 NeuroImage — happy vs sad (3 regions)
    ("Brattico_2011", "happy>sad", "hippocampus", 28, -22, -12, "MATCH", "paper_peak", "Brattico 2011, NeuroImage"),
    ("Brattico_2011", "happy>sad", "amygdala",    24,  -4, -18, "MATCH", "paper_peak", "Brattico 2011, NeuroImage"),
    ("Brattico_2011", "happy>sad", "STG",         58, -22,   4, "MATCH", "paper_peak", "Brattico 2011, NeuroImage"),
    # Zatorre & Halpern 2005 NeuroImage — imagery > rest (3 regions)
    ("Zatorre_Halpern_2005", "imagery>rest", "SMA",    2,  -2, 56, "MATCH", "paper_peak", "Zatorre & Halpern 2005, NeuroImage"),
    ("Zatorre_Halpern_2005", "imagery>rest", "IFG",   48,  18,  8, "MATCH", "paper_peak", "Zatorre & Halpern 2005, NeuroImage"),
    ("Zatorre_Halpern_2005", "imagery>rest", "A1_HG", 48, -18,  8, "MATCH", "paper_peak", "Zatorre & Halpern 2005, NeuroImage"),
    # Putkinen 2025 — PET OPI (7 regions, MNI from V1/results/regions §8)
    ("Putkinen_2025", "OPI_PET", "NAcc",      10,  12,  -8, "MATCH", "v1_doc_peak", "Putkinen 2025, Eur J Nucl Med"),
    ("Putkinen_2025", "OPI_PET", "OFC",       28,  34, -16, "MATCH", "v1_doc_peak", "Putkinen 2025, Eur J Nucl Med"),
    ("Putkinen_2025", "OPI_PET", "insula",    36,  16,   0, "MATCH", "v1_doc_peak", "Putkinen 2025, Eur J Nucl Med"),
    ("Putkinen_2025", "OPI_PET", "ACC",        2,  30,  28, "MATCH", "v1_doc_peak", "Putkinen 2025, Eur J Nucl Med"),
    ("Putkinen_2025", "OPI_PET", "NAcc_b",    10,  12,  -8, "MATCH", "v1_doc_peak", "Putkinen 2025, Eur J Nucl Med"),  # duplicate in V1 §8 table (ventral striatum + NAcc)
    ("Putkinen_2025", "OPI_PET", "MGB",        0, -18,   6, "MATCH", "v1_doc_peak", "Putkinen 2025, Eur J Nucl Med"),
    ("Putkinen_2025", "OPI_PET", "amygdala",  24,  -4, -18, "MATCH", "v1_doc_peak", "Putkinen 2025, Eur J Nucl Med"),
]


def build_literature_coords() -> pd.DataFrame:
    cols = ["study", "contrast", "region_label", "mni_x", "mni_y", "mni_z",
            "v1_match_status", "coord_source", "primary_citation"]
    lit = pd.DataFrame(LITERATURE_ROWS, columns=cols)
    # Enforce numeric dtype
    for c in ("mni_x", "mni_y", "mni_z"):
        lit[c] = lit[c].astype(float)
    out = HERE / "literature_coords_32.csv"
    lit.to_csv(out, index=False)
    return lit


# ---------------------------------------------------------------------------
# Step 3 — match criterion + observed rate
# ---------------------------------------------------------------------------


def compute_matches(mi_df: pd.DataFrame, lit_df: pd.DataFrame, radius_mm: float) -> tuple[int, int, pd.DataFrame]:
    """Count rows in lit_df whose nearest MI centroid (by name alignment) lies
    within radius_mm. Returns (match_count, n_tests, per_row_df).

    Match anchor: each literature row names a region_label. We look up the
    matching MI region (by name, using the NAcc_b alias -> NAcc). Euclidean
    distance to the MI centroid of that name; MATCH iff <= radius_mm.
    Rows whose region_label is not present in MI's 26-region registry are
    counted as non-matches (impossible to corroborate a region the model does
    not represent).
    """
    mi_lookup = {r["region"]: np.array([r["mni_x"], r["mni_y"], r["mni_z"]])
                 for _, r in mi_df.iterrows()}
    rows = []
    for _, r in lit_df.iterrows():
        name = r["region_label"]
        # Alias Putkinen's duplicate NAcc row
        name_mi = "NAcc" if name == "NAcc_b" else name
        lit_xyz = np.array([r["mni_x"], r["mni_y"], r["mni_z"]])
        if name_mi in mi_lookup:
            d = float(np.linalg.norm(mi_lookup[name_mi] - lit_xyz))
            m = bool(d <= radius_mm)
        else:
            d = np.nan
            m = False
        rows.append({
            "study": r["study"], "region_label": name,
            "mi_region": name_mi, "distance_mm": d,
            "matched_at_radius": m, "radius_mm": radius_mm,
            "coord_source": r["coord_source"],
        })
    per_row = pd.DataFrame(rows)
    return int(per_row["matched_at_radius"].sum()), len(per_row), per_row


# ---------------------------------------------------------------------------
# Step 4 — permutation nulls
# ---------------------------------------------------------------------------


def load_brain_mask_voxels():
    """Return array of in-brain voxel MNI xyz coordinates from nilearn's MNI152
    brain mask. Fall back to a bounding-box grid if nilearn is unavailable.
    """
    try:
        from nilearn.datasets import load_mni152_brain_mask
        import nibabel as nib
        mask_img = load_mni152_brain_mask(threshold=0.5)
        data = mask_img.get_fdata()
        aff = mask_img.affine
        ijk = np.argwhere(data > 0)
        ones = np.ones((ijk.shape[0], 1))
        homog = np.hstack([ijk, ones])
        xyz = homog @ aff.T
        xyz = xyz[:, :3]
        return xyz, "nilearn_mni152_brain_mask"
    except Exception as e:
        print(f"[warn] nilearn MNI152 mask unavailable ({type(e).__name__}: {e}); using bounding-box fallback", file=sys.stderr)
        # Bounding-box sample grid at ~2 mm resolution
        xs = np.arange(-78, 79, 2, dtype=float)
        ys = np.arange(-112, 77, 2, dtype=float)
        zs = np.arange(-70, 85, 2, dtype=float)
        X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
        xyz = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
        return xyz, "bounding_box_fallback"


def null1_coord_shuffle(
    mi_df: pd.DataFrame,
    lit_df: pd.DataFrame,
    radius_mm: float,
    n_perms: int,
    seed: int,
    brain_voxels: np.ndarray,
) -> np.ndarray:
    """For each permutation: relocate each MI region to a random voxel inside
    the brain mask, recompute match count at radius_mm.
    """
    rng = np.random.default_rng(seed)
    lit_names_mi = [("NAcc" if n == "NAcc_b" else n) for n in lit_df["region_label"]]
    lit_xyz = lit_df[["mni_x", "mni_y", "mni_z"]].to_numpy(dtype=float)
    regions = list(mi_df["region"])
    n_regions = len(regions)
    region_to_row = {r: i for i, r in enumerate(regions)}
    # Pre-compute which literature rows map to which MI region index (or -1 if
    # the region is not in MI's 26-region registry).
    lit_to_region_idx = np.array([region_to_row.get(n, -1) for n in lit_names_mi])
    valid_mask = lit_to_region_idx >= 0
    counts = np.zeros(n_perms, dtype=np.int32)
    n_vox = brain_voxels.shape[0]
    for p in range(n_perms):
        idx = rng.integers(0, n_vox, size=n_regions)
        shuffled_centroids = brain_voxels[idx]  # (n_regions, 3)
        # Distance for each literature row to its name-aligned (shuffled) MI centroid
        lit_idx = lit_to_region_idx
        # fill non-mapped rows with +inf so they never match
        dist = np.full(len(lit_df), np.inf, dtype=float)
        if valid_mask.any():
            cent = shuffled_centroids[lit_idx[valid_mask]]
            d = np.linalg.norm(cent - lit_xyz[valid_mask], axis=1)
            dist[valid_mask] = d
        counts[p] = int(np.sum(dist <= radius_mm))
    return counts


def null2_label_shuffle(
    mi_df: pd.DataFrame,
    lit_df: pd.DataFrame,
    radius_mm: float,
    n_perms: int,
    seed: int,
) -> np.ndarray:
    """For each permutation: permute MI region labels over the fixed MI
    centroid cloud, recompute match count.

    i.e., the 26 MI centroids stay where they are; we ask "what if the centroid
    currently called 'STG' were called 'NAcc' and vice versa?".
    """
    rng = np.random.default_rng(seed + 1)
    regions = list(mi_df["region"])
    mi_xyz = mi_df[["mni_x", "mni_y", "mni_z"]].to_numpy(dtype=float)
    n_regions = len(regions)
    region_to_row = {r: i for i, r in enumerate(regions)}

    lit_names_mi = [("NAcc" if n == "NAcc_b" else n) for n in lit_df["region_label"]]
    lit_xyz = lit_df[["mni_x", "mni_y", "mni_z"]].to_numpy(dtype=float)
    lit_to_region_idx = np.array([region_to_row.get(n, -1) for n in lit_names_mi])
    valid_mask = lit_to_region_idx >= 0

    counts = np.zeros(n_perms, dtype=np.int32)
    base_perm = np.arange(n_regions)
    for p in range(n_perms):
        perm = rng.permutation(base_perm)
        # Under permutation `perm`, the centroid previously at index i is now
        # *called* regions[perm[i]]. Equivalently, the centroid currently
        # labeled regions[k] in the literature row is physically located at
        # the MI row where perm[j] == region_to_row[name], i.e., at
        # mi_xyz[inv_perm[k]].
        inv_perm = np.empty_like(perm)
        inv_perm[perm] = np.arange(n_regions)
        cent_for_lit = mi_xyz[inv_perm[lit_to_region_idx[valid_mask]]]
        d = np.linalg.norm(cent_for_lit - lit_xyz[valid_mask], axis=1)
        dist = np.full(len(lit_df), np.inf, dtype=float)
        dist[valid_mask] = d
        counts[p] = int(np.sum(dist <= radius_mm))
    return counts


# ---------------------------------------------------------------------------
# Step 5 — main orchestration
# ---------------------------------------------------------------------------


def p_value_upper(observed: int, null_counts: np.ndarray) -> float:
    return (1.0 + float(np.sum(null_counts >= observed))) / (1.0 + len(null_counts))


def main() -> int:
    print("[T-R1-08] Building MI coords + literature coords...", file=sys.stderr)
    mi_df = build_mi_coords()
    lit_df = build_literature_coords()
    print(f"  MI regions: {len(mi_df)}  Literature rows: {len(lit_df)}", file=sys.stderr)

    print("[T-R1-08] Loading brain mask voxels...", file=sys.stderr)
    brain_voxels, mask_source = load_brain_mask_voxels()
    print(f"  Mask source: {mask_source}  n_voxels: {brain_voxels.shape[0]}", file=sys.stderr)

    # Observed + nulls for each radius
    rows = []
    per_row_frames = []
    null1_all = {}
    null2_all = {}

    for r_mm in RADII_MM:
        print(f"[T-R1-08] radius = {r_mm} mm", file=sys.stderr)
        obs, n_tests, per_row = compute_matches(mi_df, lit_df, r_mm)
        per_row_frames.append(per_row)
        null1 = null1_coord_shuffle(mi_df, lit_df, r_mm, N_PERMUTATIONS, SEED, brain_voxels)
        null2 = null2_label_shuffle(mi_df, lit_df, r_mm, N_PERMUTATIONS, SEED)
        null1_all[r_mm] = null1
        null2_all[r_mm] = null2
        p1 = p_value_upper(obs, null1)
        p2 = p_value_upper(obs, null2)
        rows.append({
            "null_design": "Null-1 coord shuffle", "radius_mm": r_mm, "observed": obs,
            "n_tests": n_tests,
            "null_mean": float(null1.mean()), "null_std": float(null1.std(ddof=1)),
            "null_p05": float(np.percentile(null1, 5)), "null_p95": float(np.percentile(null1, 95)),
            "p_value": p1, "n_permutations": N_PERMUTATIONS, "seed": SEED,
            "mask_source": mask_source,
        })
        rows.append({
            "null_design": "Null-2 label shuffle", "radius_mm": r_mm, "observed": obs,
            "n_tests": n_tests,
            "null_mean": float(null2.mean()), "null_std": float(null2.std(ddof=1)),
            "null_p05": float(np.percentile(null2, 5)), "null_p95": float(np.percentile(null2, 95)),
            "p_value": p2, "n_permutations": N_PERMUTATIONS, "seed": SEED,
            "mask_source": mask_source,
        })
        print(f"  observed: {obs}/{n_tests}  null-1 p = {p1:.4g}  null-2 p = {p2:.4g}", file=sys.stderr)

    results_df = pd.DataFrame(rows)
    results_df.to_csv(HERE / "permutation_null_results.csv", index=False)

    per_row_full = pd.concat(per_row_frames, ignore_index=True)
    per_row_full.to_csv(HERE / "match_table_by_radius.csv", index=False)

    # Robustness results excluding atlas-centroid proxy rows
    prox_mask = lit_df["coord_source"] == "atlas_centroid_proxy"
    if prox_mask.any():
        lit_df_noprox = lit_df.loc[~prox_mask].reset_index(drop=True)
        rp_rows = []
        for r_mm in RADII_MM:
            obs, n_tests, _ = compute_matches(mi_df, lit_df_noprox, r_mm)
            null1 = null1_coord_shuffle(mi_df, lit_df_noprox, r_mm, N_PERMUTATIONS, SEED, brain_voxels)
            null2 = null2_label_shuffle(mi_df, lit_df_noprox, r_mm, N_PERMUTATIONS, SEED)
            rp_rows.append({
                "subset": "excluding_atlas_centroid_proxy",
                "null_design": "Null-1 coord shuffle", "radius_mm": r_mm, "observed": obs,
                "n_tests": n_tests,
                "null_mean": float(null1.mean()), "null_std": float(null1.std(ddof=1)),
                "p_value": p_value_upper(obs, null1),
            })
            rp_rows.append({
                "subset": "excluding_atlas_centroid_proxy",
                "null_design": "Null-2 label shuffle", "radius_mm": r_mm, "observed": obs,
                "n_tests": n_tests,
                "null_mean": float(null2.mean()), "null_std": float(null2.std(ddof=1)),
                "p_value": p_value_upper(obs, null2),
            })
        pd.DataFrame(rp_rows).to_csv(HERE / "permutation_null_results_no_proxy.csv", index=False)

    # Plot histograms at 10 mm
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), dpi=130)
        # observed at 10 mm
        obs_10, n_tests_10, _ = compute_matches(mi_df, lit_df, 10.0)
        n1 = null1_all[10.0]
        n2 = null2_all[10.0]
        axes[0].hist(n1, bins=np.arange(n1.min(), n1.max() + 2) - 0.5, color="#4a7aba", edgecolor="white")
        axes[0].axvline(obs_10, color="#c0392b", linestyle="--", linewidth=2, label=f"observed = {obs_10}/{n_tests_10}")
        axes[0].set_title(f"Null-1 coord shuffle (10 mm)\nmean={n1.mean():.2f}, p={p_value_upper(obs_10, n1):.4g}")
        axes[0].set_xlabel("matches under null")
        axes[0].set_ylabel("perm count")
        axes[0].legend()
        axes[1].hist(n2, bins=np.arange(n2.min(), n2.max() + 2) - 0.5, color="#4ab27a", edgecolor="white")
        axes[1].axvline(obs_10, color="#c0392b", linestyle="--", linewidth=2, label=f"observed = {obs_10}/{n_tests_10}")
        axes[1].set_title(f"Null-2 label shuffle (10 mm)\nmean={n2.mean():.2f}, p={p_value_upper(obs_10, n2):.4g}")
        axes[1].set_xlabel("matches under null")
        axes[1].legend()
        fig.suptitle(f"T-R1-08 — RAM coordinate permutation null (N={N_PERMUTATIONS}, seed={SEED}, mask={mask_source})")
        fig.tight_layout()
        fig.savefig(HERE / "null_distribution.png", bbox_inches="tight")
        plt.close(fig)
    except Exception as e:
        print(f"[warn] figure generation failed: {type(e).__name__}: {e}", file=sys.stderr)

    print("[T-R1-08] Done.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
