"""T-R2-04 — Companion figure: bootstrap distribution of the interaction
coefficient, ΔR², quadrant contrasts, and the Cheung 2019 published β line."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path(__file__).parent
results = json.loads((OUT / "results.json").read_text())
int_draws = np.load(OUT / "bootstrap_interaction.npy")
dr2_draws = np.load(OUT / "bootstrap_delta_r2.npy")
q_df = pd.DataFrame(results["quadrant_analysis"])

fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))

# Panel A: interaction coefficient bootstrap
ax = axes[0]
ax.hist(int_draws, bins=60, color="#6C7CE0", alpha=0.85, edgecolor="white")
ci = results["bootstrap"]["interaction_ci95"]
ax.axvline(0, color="black", lw=1, linestyle="--")
ax.axvline(ci[0], color="#0B2E6B", lw=1.5, linestyle=":")
ax.axvline(ci[1], color="#0B2E6B", lw=1.5, linestyle=":")
ax.axvline(-0.124, color="#C0392B", lw=2, linestyle="-",
           label=r"Cheung 2019 published $\beta_{ixn} = -0.124$")
ax.axvline(results["bootstrap"]["interaction_mean"], color="#0B2E6B", lw=2,
           label=rf"MI-proxy $\beta$ (mean={results['bootstrap']['interaction_mean']:+.3f})")
ax.set_xlabel(r"$\beta$(IC × ENTROPY)")
ax.set_ylabel("bootstrap density (B=5000)")
ax.set_title("A. Interaction coefficient — sign matches Cheung")
ax.legend(fontsize=8, loc="upper left")

# Panel B: ΔR² (M2-M1) bootstrap
ax = axes[1]
ax.hist(dr2_draws, bins=60, color="#63B99B", alpha=0.85, edgecolor="white")
dci = results["bootstrap"]["delta_r2_ci95"]
ax.axvline(0, color="black", lw=1, linestyle="--")
ax.axvline(dci[0], color="#0B5E3E", lw=1.5, linestyle=":")
ax.axvline(dci[1], color="#0B5E3E", lw=1.5, linestyle=":")
ax.set_xlabel(r"$\Delta R^2$ (M2 interaction − M1 additive)")
ax.set_ylabel("bootstrap density")
dmean = results["bootstrap"]["delta_r2_mean"]
ax.set_title(rf"B. $\Delta R^2$ mean={dmean:+.4f}, CI excludes 0")

# Panel C: 4-quadrant saddle pattern
ax = axes[2]
x = np.arange(4)
ax.bar(x - 0.18, q_df["rating_z_mean_obs"], width=0.35,
       color="#444", label="observed", alpha=0.85)
ax.bar(x + 0.18, q_df["rating_z_mean_pred"], width=0.35,
       color="#6C7CE0", label="M2 predicted", alpha=0.85)
ax.set_xticks(x)
ax.set_xticklabels([q.replace("_", "\n") for q in q_df["quadrant"]], fontsize=8)
ax.axhline(0, color="black", lw=1)
ax.set_ylabel("mean z-scored rating")
ax.set_title("C. Saddle pattern in 4 quadrants (Cheung 2019 Fig 1D)")
ax.legend(fontsize=8)

fig.suptitle(
    "T-R2-04 — Cheung 2019 uncertainty × surprise interaction; "
    f"ΔAIC(M2−M1) = {results['delta_aic']['M2_minus_M1']:+.1f}",
    fontsize=11,
)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(OUT / "figure.png", dpi=140, bbox_inches="tight")
fig.savefig(OUT / "figure.svg", bbox_inches="tight")
print(f"Saved: {OUT/'figure.png'}")
