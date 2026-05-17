"""Statistical primitives shared across V-Reproduction phases.

These primitives are reused by 16 reproduction phases. Wrong implementations
propagate to every reproduction claim, so each is covered by a TDD pytest
suite under `_infra/tests/`.

Modules:
    fdr           — Benjamini-Hochberg, Benjamini-Bogomolov, Bonferroni
    permutation   — RAM topology nulls + generic shuffle null
    bootstrap     — BCa CI + song-level block bootstrap
    ridge         — LOSO ridge + banded ridge wrapper (himalaya optional)
    cka           — Linear centered kernel alignment
"""
