#!/usr/bin/env python3
"""V-Reproduction Phase 10 — Cheung 2019 emergent reward interaction (6 claims).

Verifies 6 paper claims against the preserved V2 T-R2-04 results.json artefact
(no engine call required; Cheung audio was never released — analysis is post-hoc
OLS/LMM/bootstrap over Cheung 2024 OSF CSV).

Outputs:
    results/10_cheung_correlations.csv
    results/10_cheung_manifest.json
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

PHASE_DIR = Path(__file__).resolve().parent.parent
V_REPRO   = PHASE_DIR.parent.parent
SCIENCE   = V_REPRO.parent

# Paper anchor: cheung-reward (V2 T-R2-04)
ANCHORS = V_REPRO / "datasets" / "paper-anchors"
T_R2_04   = (ANCHORS / "cheung-reward") if (ANCHORS / "cheung-reward" / "results.json").exists() \
    else SCIENCE / "V2" / "reviewer-sims" / "divan-major-revision-2026-04-22" / "computing-phase" / "T-R2-04"
RESULTS_J = T_R2_04 / "results.json"
COEFS     = T_R2_04 / "coefficients.csv"
# Prefer vendored engine F6 mechanisms; fallback to parent Science checkout.
_VENDORED_F6 = V_REPRO / "engine" / "Musical_Intelligence" / "brain" / "functions" / "f6" / "mechanisms"
_PARENT_F6   = SCIENCE / "Musical_Intelligence" / "brain" / "functions" / "f6" / "mechanisms"
MI_F6     = _VENDORED_F6 if _VENDORED_F6.is_dir() else _PARENT_F6

RESULTS = PHASE_DIR / "results"
RESULTS.mkdir(parents=True, exist_ok=True)


def load_t_r2_04():
    return json.loads(RESULTS_J.read_text())


def m2_ols_beta_interaction():
    """β(IC_z:ENTROPY_z) from M2 OLS in coefficients.csv."""
    with COEFS.open() as f:
        for r in csv.DictReader(f):
            if (r["model"] == "M2_interaction_IC_x_ENTROPY"
                    and r["term"] == "IC_z:ENTROPY_z"):
                return float(r["beta"]), float(r["ci_lo"]), float(r["ci_hi"])
    raise KeyError("M2 IC_z:ENTROPY_z not found in coefficients.csv")


def reward_formula_additive():
    """Engine architectural control: Eq. 5 reward formula contains NO IC*ENTROPY product."""
    if not MI_F6.exists():
        return None, "F6 mechanisms path not found"
    candidates = list(MI_F6.rglob("*.py"))
    # Look for a static reward function that mentions surprise+resolution+exploration−monotony
    import re as _re
    relevant = []
    for p in candidates:
        try:
            t = p.read_text()
        except Exception:
            continue
        if any(k in t for k in ("surprise", "exploration", "monotony", "resolution")):
            # Confirm no `* ENTROPY` or `IC * ENT` style product term in same file
            has_interaction = bool(_re.search(r"IC\s*\*\s*ENTROPY|ENTROPY\s*\*\s*IC", t))
            relevant.append((p.name, has_interaction))
    if not relevant:
        return None, "no F6 reward formula files matched"
    additive = all(not has_int for _, has_int in relevant)
    return additive, f"{len(relevant)} F6 mech files inspected, additive={additive}"


def main():
    d = load_t_r2_04()
    full = d["full_data_fit"]
    boot = d["bootstrap"]
    delta_aic = d["delta_aic"]
    cv = d["held_out_cv_summary"]

    ols_beta, ols_lo, ols_hi = m2_ols_beta_interaction()
    print(f"[ols] β(IC×ENTROPY) = {ols_beta:.4f}  CI95=[{ols_lo:.4f},{ols_hi:.4f}]")
    print(f"[boot] mean = {boot['interaction_mean']:.4f}  CI95={boot['interaction_ci95']}")
    print(f"[cv ] M3 Eq.5 Pearson r = {cv['M3_MI_Eq5_composite']['pearson_r_mean']:.4f}")

    # Architectural control
    additive, note = reward_formula_additive()
    print(f"[arch] Eq.5 additivity check: additive={additive}  ({note})")

    cheung_published_beta = -0.124
    cheung_in_ci = (
        boot["interaction_ci95"][0] <= cheung_published_beta <= boot["interaction_ci95"][1]
    )

    # Per-claim verdict
    rows = []
    n_pass = n_caveat = n_fail = 0

    def add(cid, label, paper_val, repro_val, ok, tol):
        nonlocal n_pass, n_fail
        v = "PASS" if ok else "FAIL"
        if ok:
            n_pass += 1
        else:
            n_fail += 1
        rows.append({
            "claim_id": cid,
            "claim_label": label,
            "paper_value": paper_val,
            "reproduced_value": repro_val,
            "tolerance": tol,
            "verdict": v,
            "iteration_count": 1,
        })

    add("C-CHEUNG-01", "β(IC × ENTROPY) M2 OLS = −0.158",
        "-0.158", f"{ols_beta:.4f}",
        abs(ols_beta - (-0.158)) <= 0.01, "abs <= 0.01")

    ci_match = (
        abs(boot["interaction_ci95"][0] - (-0.228)) <= 0.01
        and abs(boot["interaction_ci95"][1] - (-0.084)) <= 0.01
    )
    add("C-CHEUNG-02", "Bootstrap 95% CI = [−0.228, −0.084]",
        "[-0.228, -0.084]",
        f"[{boot['interaction_ci95'][0]:.4f}, {boot['interaction_ci95'][1]:.4f}]",
        ci_match, "abs(endpoints) <= 0.01")

    add("C-CHEUNG-03", "Cheung published β=−0.124 inside bootstrap CI",
        "-0.124 ∈ [-0.228, -0.084]",
        f"-0.124 ∈ [{boot['interaction_ci95'][0]:.4f}, {boot['interaction_ci95'][1]:.4f}]",
        cheung_in_ci, "exact_match")

    add("C-CHEUNG-04", "ΔAIC (M2 − M1) = −33.5",
        "-33.5", f"{delta_aic['M2_minus_M1']:.2f}",
        abs(delta_aic["M2_minus_M1"] - (-33.5)) <= 1.0, "abs <= 1.0")

    m3_r = cv["M3_MI_Eq5_composite"]["pearson_r_mean"]
    add("C-CHEUNG-05", "Held-out Pearson r (M3 Eq.5) = +0.615",
        "+0.615", f"{m3_r:+.4f}",
        abs(m3_r - 0.615) <= 0.01, "abs <= 0.01")

    add("C-CHEUNG-06", "Eq.5 reward formula additive (no IC×ENTROPY term)",
        "additive=True",
        f"additive={additive}",
        bool(additive), "additive=True (engine source inspection)")

    # Sample-size sanity
    meta = d["meta"]
    add("C-CHEUNG-07-meta", "N=39,351 trials, 1,009 chord-level rows, 39 subjects, 30 songs",
        "39351 / 1009 / 39 / 30",
        f"{meta['n_trials_used']} / {meta['n_chord_level_rows']} / {meta['n_subjects']} / {meta['n_songs']}",
        (meta["n_trials_used"] == 39351 and meta["n_chord_level_rows"] == 1009
         and meta["n_subjects"] == 39 and meta["n_songs"] == 30),
        "exact_match")

    with (RESULTS / "10_cheung_correlations.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)

    engine_head = json.loads((V_REPRO / "_infra" / "manifests" / "engine_head.json").read_text())
    manifest = {
        "axis_id": "AXIS-10",
        "axis_name": "Cheung 2019 Emergent Reward Interaction",
        "engine_head": engine_head.get("pinned_commit"),
        "seed_registry": {"primary": 2026050705, "bootstrap": 42, "B": 5000},
        "phase_close_date": "2026-05-07",
        "git_commit_hash": "PENDING_AT_CLOSE",
        "claims": rows,
        "source_artefact": str(RESULTS_J.relative_to(SCIENCE)),
    }
    with (RESULTS / "10_cheung_manifest.json").open("w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n[verdict] PASS={n_pass}  CAVEAT={n_caveat}  FAIL={n_fail}  total={len(rows)}")


if __name__ == "__main__":
    main()
