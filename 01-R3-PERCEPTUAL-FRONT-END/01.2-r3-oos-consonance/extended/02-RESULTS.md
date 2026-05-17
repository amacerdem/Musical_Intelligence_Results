# Phase 01.2 extended — Results (CLOSED 2026-05-16)

**Status:** CLOSED 2026-05-16 (iter 01 PASS, single run).
**Wall-clock:** 2.0 s (Apple M2, 8 GB unified memory, single-threaded).
**Engine HEAD verified:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
**Axis verdict:** **CLOSED-PASS**

## 1. Verdict table

| Claim ID | Dataset | N (bins / rows) | stumpf_fusion ρ | sensory_pleasantness ρ | roughness ρ | Verdict |
|---|---|---|---|---|---|---|
| C-R3EXT-01 | Marjieh Study 1A harmonic | 13 bins / 7,500 raw | **+0.813** | **+0.890** | **−0.835** | **PASS** |
| C-R3EXT-02 | Marjieh Study 1B flute | 13 bins / 15,000 raw | +0.533 | **+0.769** | **−0.775** | **PASS** |
| C-R3EXT-03 | Marjieh Study 1B guitar | 13 bins / 15,000 raw | +0.440 | +0.599 | −0.533 | PARTIAL |
| C-R3EXT-04 | Marjieh Study 1B piano | 13 bins / 15,000 raw | **+0.615** | **+0.692** | **−0.736** | **PASS** |
| C-R3EXT-05 | Marjieh Study 4A pure tone (n_harm=1) | 13 bins / 7,500 raw | +0.451 | +0.357 | **−0.725** | PARTIAL |
| C-R3EXT-06 | Bidelman & Krishnan 2009 FFR | 6 intervals (canonical hierarchy) | **+1.000** | **+1.000** | **−0.886** | **PASS** |
| C-R3EXT-07 | Schwartz et al. 2003 speech-derived | 13 intervals | **+0.923** | **+0.879** | **−0.813** | **PASS** |
| C-R3EXT-08 | Sethares 1993 analytical reference | 13 intervals | **+0.923** | **+0.879** | **−0.813** | **PASS** |
| C-R3EXT-09 | Lahdelma et al. Indian Tension (polarity −1) | 12 intervals / 852 raw | **+0.804** | +0.580 | −0.524 | PARTIAL |

Bold = channel meets PASS threshold (|ρ| ≥ 0.60 with theoretical-convention sign).

**Counts:** 6 PASS / 3 PARTIAL / 0 FAIL.

## 2. Invariant outcomes

### 2.1 CDC — Cross-Dataset Consistency: **PASS**

Sign-consistency per headline channel across all nine datasets
(`results/29_invariants.json` §cross_dataset_consistency):

| Channel | Sign-consistent / 9 | Rule (≥ 7 / 9) |
|---|---|---|
| `stumpf_fusion` | **9 / 9** | PASS |
| `sensory_pleasantness` | **9 / 9** | PASS |
| `roughness` | **9 / 9** | PASS |

All three R³ Group A channels show theoretically-correct sign across
every dataset in the battery. This is the central cross-corroboration
evidence for Phase 6 extended.

### 2.2 HRI — Hierarchy Reproduction Invariant: **FAIL (4 / 9)**

Spearman ρ between the dataset-derived ranking and the
headline-channel-derived ranking on the classical Western interval
subset {P1, P4, M3, P5, m6, TT} (subset {P4, M3, P5, m6, TT} for
C-R3EXT-09):

| Claim ID | Headline channel | Ranking ρ | HRI verdict |
|---|---|---|---|
| C-R3EXT-01 | sensory_pleasantness | **+0.943** | PASS |
| C-R3EXT-02 | sensory_pleasantness | +0.200 | FAIL |
| C-R3EXT-03 | sensory_pleasantness | −0.086 | FAIL |
| C-R3EXT-04 | sensory_pleasantness | +0.371 | FAIL |
| C-R3EXT-05 | stumpf_fusion | −0.200 | FAIL |
| C-R3EXT-06 | stumpf_fusion | **+1.000** | PASS |
| C-R3EXT-07 | stumpf_fusion | **+1.000** | PASS |
| C-R3EXT-08 | stumpf_fusion | **+1.000** | PASS |
| C-R3EXT-09 | stumpf_fusion | +0.700 | FAIL |

The HRI threshold of ρ ≥ 0.85 on a 6-element ranking is strict. The
four passing datasets are precisely those that either (a) sample the
classical Western hierarchy cleanly across all 6 intervals (Bidelman:
all 6 intervals are exactly the hierarchy set, ρ = +1.000) or (b) carry
well-conditioned target values across the hierarchy subset (Schwartz,
Sethares, Marjieh harmonic baseline). The five FAIL cases fall into
two patterns:

- **C-R3EXT-02..04 instrument timbres** — flute / guitar / piano:
  hierarchy ranking degrades under the 6-partial 1/n harmonic proxy.
  The methodology-locked synthesis recipe does not reproduce
  instrument-specific spectral structure (formant peaks, decay
  envelopes); the headline magnitude correlation still meets the
  per-claim PASS rule for flute and piano. This is the methodological
  approximation flagged in `00-METHODOLOGY.md` §5.1.
- **C-R3EXT-05 pure tone** — n_harm=1: removes the harmonic content
  that the Plomp-Levelt / Sethares roughness model uses to construct
  the consonance hierarchy. Hierarchy ranking is not expected to hold.
  The headline `roughness` channel still passes (−0.725).
- **C-R3EXT-09 Indian Tension** — ranking ρ = +0.700 on the 5-element
  subset is close to but does not reach the 0.85 threshold. Cross-cultural
  listener pool tested on 12-TET Western stimuli.

HRI FAIL is recorded faithfully per pre-reg §Forbidden moves item 4
(no threshold adjustment).

### 2.3 Axis verdict

```
Decision rule:
  CLOSED-STRONG  ≥ 7 / 9 PASS  AND  CDC PASS  AND  HRI PASS
  CLOSED-PASS    ≥ 5 / 9 PASS  AND  CDC PASS              ← THIS
  CLOSED-PART    3–4 / 9 PASS  AND  CDC PASS
  CLOSED-FAIL    CDC FAIL  OR  ≤ 2 PASS

Observed: 6 / 9 PASS, CDC PASS, HRI FAIL
Verdict:  CLOSED-PASS
```

## 3. Independence audit

`git grep -l` sweep of `Musical_Intelligence/` at the pinned HEAD for
each input CSV filename and author name
(`results/29_independence_audit.json`):

| Needle | Hits in engine subtree | Interpretation |
|---|---|---|
| `rating_dyh3dd` | 0 | filename absent |
| `rating_flute_harmonic_harflt` | 0 | filename absent |
| `rating_guitar_harmonic_hargtr` | 0 | filename absent |
| `rating_piano_harmonic_harpno` | 0 | filename absent |
| `pure_dyad_purdyrt` | 0 | filename absent |
| `bidelman2009_ffr` | 0 | filename absent |
| `schwartz2003_speech_harmonics` | 0 | filename absent |
| `sethares1993_dissonance` | 0 | filename absent |
| `indian_tension_ratings` | 0 | filename absent |
| `Bidelman` | 16 | literature citation in F1 mechanism docstrings (BCH theory, MPG, PCCR, PNH, etc.) — not a fit target |
| `Schwartz` | 0 | author absent |
| `Marjieh` | 0 | author absent |
| `Lahdelma` | 0 | author absent |

Zero filename hits across all nine inputs confirms the engine never
reads from or fits to these CSVs. The 16 `Bidelman` hits in F1
mechanism docstrings cite Bidelman-Chandrasekaran-Helmholtz consonance
theory as a literature reference (the BCH mechanism takes its name from
this; PNH and related mechanisms cite Bidelman's brainstem-FFR
empirical work). This is the standard literature-citation pattern, not
a numerical fit target.

## 4. Per-channel observations

### 4.1 Schwartz ≡ Sethares identical ρ values

Both C-R3EXT-07 (Schwartz 2003 speech-derived) and C-R3EXT-08
(Sethares 1993 analytical reference, polarity −1) yield identical
correlations across all three R³ headline channels:

```
stumpf_fusion        +0.923
sensory_pleasantness +0.879
roughness            −0.813
```

This is not a duplication artefact. Spearman ρ depends only on rank
order; the two theoretical frameworks produce the same rank ordering on
the classical Western interval set (after polarity correction). That
the engine returns the same ρ against both is corroborating evidence
that the engine consistently tracks the cross-source-stable consonance
hierarchy, not a particular theoretical model's quantitative output.

### 4.2 Bidelman N = 6 (canonical hierarchy)

The Bidelman & Krishnan 2009 source CSV provides six intervals: P1, P4,
M3, P5, m6, TT — exactly the classical Western consonance hierarchy
subset used in the HRI invariant. The engine achieves ρ = +1.000 on
both `stumpf_fusion` and `sensory_pleasantness` against the
`behavioral_consonance` column, with the negative-pole roughness
channel at −0.886. This is the strongest single-dataset evidence in
the battery — the engine perfectly tracks the Bidelman behavioural
ranking of the canonical hierarchy.

## 5. Raw artefacts

- `results/29_r3ext_correlations.csv` — per-claim per-channel ρ + verdict
- `results/29_r3ext_manifest.json` — full manifest with decision-rule detail
- `results/29_invariants.json` — CDC + HRI outcomes per dataset / channel
- `results/29_input_hashes.json` — SHA-256 of every input CSV
- `results/29_sign_convention.json` — polarity log per claim
- `results/29_independence_audit.json` — `git grep` sweep verbatim
- `results/{C-R3EXT-NN}_engine.csv` (×9) — per-claim R³ engine output:
  semitone, target column, all 7 R³ Group A channels
