# Code — ECE Reproduction

Self-contained reproduction pipeline. Engine is **not** copied here; assumed at standard `Science/Musical_Intelligence/`.

## Files

| File | Role |
|---|---|
| `extract_belief_traces.py` | Loads engine, runs R³→H³→mechanisms on 5 DEAM held-out songs (30s each), invokes `CoreBelief.run_cycle()` for 14 beliefs (paper's 8 + V6's 6 extension), saves per-frame (π_pred, PE, posterior, obs, y) traces to `../results/traces/song_{ID}.npz`. ~5 min wall on M2. |
| `compute_metrics.py` | Loads traces, computes per-cell ECE, Brier decomposition, 1K bootstrap reliability CIs per belief, 10K-permutation circular-shift null per cell + pooled. Writes CSV/JSON to `../results/`. ~30 s wall on M2. |
| `plot_reliability.py` | Loads `../results/A2_reliability_data.npz`, generates 3 figures: per-belief reliability diagrams (14-panel grid), 5×14 ECE heatmap, paper-vs-extension bar chart. Writes PNG to `../figures/`. ~5 s wall. |
| `test_belief_extraction.py` | Smoke test on 1 song (1034, 30s). Verifies engine path + venv before full run. Use during cold-start setup. |
| `run.sh` | Single-command pipeline: activates venv, verifies engine + data, runs all three Python scripts in order. |
| `requirements.txt` | Pinned Python deps (mirror Science/.venv). |

## Quick start

```bash
cd "<REPO_ROOT>/05-ece-belief-calibration/code"
./run.sh
```

Expected output:
```
PRIMARY (paper's 8 beliefs, F1×4 + F2×4):
  pooled ECE:          0.0841   (paper published: 0.084, deviation: +0.0001)
  median per-cell ECE: 0.0831   (IQR: 0.0591-0.1028, max: 0.1865)
  cells with ECE<0.10: 28 / 40
  ...
```

## Smoke test (1 song only)

```bash
python3 test_belief_extraction.py
```

Verifies in ~30s that:
- Engine imports correctly
- Audio loads (DEAM 1034)
- R³, H³, mechanism execution work
- `HarmonicStability.run_cycle()` returns non-empty traces with sane ranges

## Manual run (Phase by phase)

```bash
python3 extract_belief_traces.py    # Phase 1: ~5 min
python3 compute_metrics.py          # Phase 2: ~30 s
python3 plot_reliability.py         # Phase 3: ~5 s
```

## Path resolution

All paths use `Path(__file__).resolve().parents[N]`:
- `parents[3]` = Science/ (engine root)
- `parents[1]` = 03-C3-BEHAVIORAL-VALIDATION/03.2-ece-belief-calibration/ (this reproduction's root)

If you move this reproduction directory, the path resolution will break — update `_PROJECT_ROOT` and `_REPRO_ROOT` in `extract_belief_traces.py` and `compute_metrics.py`.

## Engine assumption

The reproduction expects the engine at `Science/Musical_Intelligence/` with HEAD at `5b9aba41` (or successor with `|Δρ| ≤ 1e-4` documented).

To verify engine HEAD:
```bash
cd <PAPER_TIME_SCIENCE_ROOT>
git rev-parse HEAD
```

If the engine has moved beyond `5b9aba41`, the reproduction may produce slightly different numbers due to engine changes. Document any discrepancy in `01-PROVENANCE.md`.

## Notes on determinism

- `extract_belief_traces.py` uses no random state — engine output is fully deterministic.
- `compute_metrics.py` uses `seed = 2026050502` for both 1K bootstrap and 10K circular-shift permutation null.
- All result CSVs include `seed` and engine-path metadata.
