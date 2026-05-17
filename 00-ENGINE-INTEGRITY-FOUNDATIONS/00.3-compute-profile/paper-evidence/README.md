# Phase 4 — Paper Evidence Pointers

## Where these claims live in the paper

Source: `The Paper/Divan-Final-corrected-evidence/Musical-Intelligence-corrected-evidence.{tex,pdf}`.

Compute claims appear in the §Compute profile / §Performance / §Implementation subsection. The five hardware-throughput claims (3.31× real-time, 570 fps median, 465 MB peak, p50/p95/p99 latency, 2.94× p95 margin) plus determinism (|Δρ| ≤ 8.8×10⁻⁵) form a single architectural-signature block.

## Hardware claim

> Apple MacBook Air M2 (2023, 8 GB unified memory) consumer laptop, single-threaded.

Verified at Phase 4 close: `Mac14,2`, `Apple M2`, `8 GB` — exact match.

## Determinism claim

The paper's |Δρ| ≤ 8.8×10⁻⁵ is a Spearman correlation bound across runs. Phase 0 already verified the **stronger** claim of bit-identical determinism (MD5 hashes match across 3 runs on R³ + C³ + RAM + neuro + beliefs layers). Phase 4 re-asserts via 2-run MD5 on r3 layer.

## Bridge to other phases

- Phase 0 — engine determinism floor (bit-identical, 3-run check, full layers).
- Phase 1 — paper claims compute profile in `compute_profile.json` summary; not separately enumerated, but Phase 1 C-CARD-10 gates that runtime profiling lives in Phase 4.
- Phase 4 (this) — first standalone reproduction of the throughput / memory / latency block.
