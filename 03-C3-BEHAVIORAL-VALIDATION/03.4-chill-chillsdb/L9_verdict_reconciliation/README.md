# L9 — Verdict Reconciliation

**Purpose:** Final cross-check that local results match paper-time baseline within declared tolerance, and emit a clean verdict block in REPORT.md.

## What this layer asserts

1. `test_l4_result_csv_present` — L4 produced its CSV (sanity: did L4 actually run?)
2. `test_headline_finding_within_tolerance` — MMP P2 rb and bonf_p both within paper-time tolerance:
   - `|rb_local - rb_paper| ≤ 0.01`
   - `|p_bonf_local - p_bonf_paper| ≤ 0.005`
3. `test_engine_sha_consistent` — pin manifest still declares the canonical paper-time engine SHA

## Tolerance philosophy

The 500-permutation null introduces ~0.002 absolute variance in `bonf_p` across runs at fixed engine SHA + fixed RNG seed. Tolerance is set to **0.005 on bonf_p**, large enough to absorb permutation noise but small enough that the qualitative Bonferroni-pass verdict (p<0.05) is invariant.

If a runner's machine produces a result outside tolerance, this layer FAILS with a clear diagnostic dump showing:
- Expected vs actual rb
- Expected vs actual bonf_p
- Drift magnitude
- Tolerance threshold

A FAIL here means investigate (RNG seed drift, scipy version drift, fp-noise accumulation). It does NOT mean the qualitative finding doesn't reproduce — that's L4's job.

## Output

Final REPORT.md block (written by `run_all.py`):

```markdown
## Headline TC005 verdict (afftdn 7-clean)

| Channel | mean_rb | bonf_p | n_clips_pos | status |
|---|---|---|---|---|
| MECH_MMP__P2:familiarity | +0.2306 | 0.0072 | 7/7 | ★ Bonferroni |
| MECH_AAC__E0:emotional_arousal | +0.1697 | 0.04 | 5/7 | ★ Bonferroni |
| ... |
```

This block IS the reviewer-facing verdict. Everything else is plumbing.
