# Agent 4 — verification log

**Engine SHA:** `318eb2f5...`
**Scope:** `ear/r3/*` + `ear/h3/*` (592 constants)
**Date:** 2026-05-17

Each row records: query → search tool → outcome → verification source → resolution applied.

---

## Web-search queries performed

### Q1 — Sethares 1993 dyad constants
- Query: `Sethares 1993 dissonance JASA D* 0.24 s1 0.0207 s2 18.96 a1 -3.51 a2 -5.75 c1 5`
- Tool: WebSearch (Google + Scholar snippets)
- Result: Sethares 1993 JASA 94(3):1218-1228 paper found via multiple sources; parameter values referenced but precise values delivered by next query.
- Follow-up: WebFetch on `sethares.engr.wisc.edu/comprog.html`
- Outcome: **POSITIVE** — all 7 constants extracted bit-exact from MATLAB dissmeasure.m + BASIC reference code:
  - Dstar=0.24, S1=0.0207, S2=18.96, C1=5, C2=-5, A1=-3.51, A2=-5.75
- Applied to: `_DSTAR`, `_S1`, `_S2`, `_C1`, `_C2`, `_A1`, `_A2` → A LIT-VERBATIM (7 constants)

### Q2 — Plomp-Levelt critical bandwidth
- Query: `"Plomp" "Levelt" 1965 critical bandwidth formula "25 + 75" "1.4" "0.69"`
- Tool: WebSearch
- Result: Plomp & Levelt 1965 *JASA* 38:548-560 paper found (multiple mirrors) but query-specific formula constants not visible in snippets.
- Follow-up: `Zwicker Fastl critical bandwidth formula "25 + 75" "0.69"`
- Outcome: **POSITIVE** via Voelk 2015 DAGA "Updated analytical expressions for critical bandwidth and critical-band rate" (windacoustics.com PDF): formula `Δf_GZ(f) = 25 + 75·[1 + 1.4·(f/kHz)²]^0.69` confirmed as **Zwicker & Terhardt 1980** parametrization (NOT direct Plomp-Levelt 1965).
- Applied to: 25.0, 75.0, 1.4, 1000.0, 0.69, 2 (the `^2`) in `_roughness` line 349 → A LIT-VERBATIM (5 constants + structural 2)

### Q3 — Krumhansl-Kessler 1982 profiles
- Queries (parallel):
  - `Krumhansl Kessler 1982 key profile major "6.35 2.23 3.48 2.33 4.38 4.09" minor "6.33"`
  - `Krumhansl Kessler major key profile "6.35, 2.23, 3.48" tonal hierarchy`
  - `Krumhansl Kessler minor key profile "6.33, 2.68, 3.52, 5.38"`
- Tool: WebSearch
- Result: Multiple Krumhansl-Schmuckler key-finder implementations (partitura, MediaMatrix, bmcfee gist, rnhart.net) cite the EXACT 12+12 numeric matrix from KK 1982 Table 2.
- Outcome: **POSITIVE** — both `_MAJOR` and `_MINOR` profiles bit-exact match.
- Applied to: `_MAJOR`, `_MINOR` (h_harmony lines 9, 10) → A LIT-VERBATIM (2 constants)

### Q4 — Mel-scale formula
- Query: `mel scale formula "2595 log10" 700 Hz O'Shaughnessy Stevens`
- Tool: WebSearch
- Result: Wikipedia Mel scale + Hertz-to-mel literature confirm m = 2595·log10(1+f/700) as O'Shaughnessy 1987 / Makhoul-Cosell 1976 standard parametrization.
- Outcome: **POSITIVE** — both 2595 and 700 are universal-standard mel formula constants.
- Applied to: 2595.0 (×9), 700.0 (×9 when in mel context) → A LIT-VERBATIM (18 constants)

### Q5 — IEC 61672-1 A-weighting
- Query: `A-weighting formula IEC 61672-1 "12194" "20.6" "107.7" "737.9"`
- Tool: WebSearch
- Result: Third-Octave A-weighting docs, python-acoustics IEC 61672_1_2013, Wikipedia A-weighting all confirm:
  - `R_A(f) = 12194² · f^4 / [(f²+20.6²)(f²+12194²)·√((f²+107.7²)(f²+737.9²))]`
  - `A(f) = 20·log10(R_A) + 2.00 dB`
- Outcome: **POSITIVE** — all 5 IEC pole frequencies + 2 dB reference + 20 dB factor verified bit-exact.
- Applied to: 12194.0, 20.6, 107.7, 737.9, 2.0 (+ 2 dB), 20.0 (20·log10), 4 (f^4), 2 (squared denominators) → A LIT-VERBATIM (×6 distinct values, ~8 cells)

### Q6 — Traunmüller Bark formula
- Query: `Traunmuller Bark scale formula "13 atan" "0.00076" "3.5 atan" "7500"`
- Tool: WebSearch
- Result: Bark scale Wikipedia confirms `B(f) = 13·atan(0.00076·f) + 3.5·atan((f/7500)²)` is **Traunmüller 1990 JASA 88:97** ("agrees with bark scale tables to within ±0.20 to ±0.25 Bark").
- Outcome: **POSITIVE** — all 4 Bark formula constants verified bit-exact (13, 0.00076, 3.5, 7500) + the embedded ^2 exponent.
- Applied to: 13.0, 0.00076, 3.5, 7500.0, 2 (the `^2`) → A LIT-VERBATIM (4 distinct values)

### Q7 — Stevens loudness exponent
- Query: `Stevens 1957 loudness power law exponent 0.3 sone`
- Tool: WebSearch
- Result: Wikipedia Stevens's power law confirms "Stevens' 1957 analysis confirmed the sone scale's exponent of approximately 0.3 for loudness growth." Standard reference.
- Outcome: **POSITIVE** — 0.3 exponent universally cited as Stevens 1957.
- Applied to: `b_energy/group.py:44` `amp_raw.pow(0.3)` → A LIT-VERBATIM (1 constant)

### Q8 — Zwicker sharpness scaling 0.11
- Query: `Zwicker sharpness acum formula 0.11 weighting function high Bark exponential`
- Tool: WebSearch
- Result: Salford SIRC + ANSYS sharpness docs confirm "von Bismark method sets the scaling factor k to 0.11" with weighting function `g(z) = 1 for z≤15 Bark, exponential above`. 0.11 is universal sharpness scaling (acum units).
- Outcome: **POSITIVE** for 0.11; **PARTIAL** for the engine's specific re-parameterization 0.066/0.171 (standard Bismarck is 0.2/0.308 — engine uses different parametrization).
- Applied to: 0.11 → A LIT-VERBATIM; 15 (z=15 Bark threshold) → A LIT-VERBATIM; 0.066, 0.171 → E (re-parameterization, escalated)

### Q9 — Jiang 2002 spectral contrast
- Query: `Jiang 2002 ICME octave spectral contrast 7 bands sub-bands music`
- Tool: WebSearch
- Result: Semantic Scholar / IEEE Xplore confirm paper "Music type classification by spectral contrast feature" (Jiang, Lu, Zhang, Tao, Cai; IEEE ICME 2002). 7-band partition cardinality confirmed; specific mel-bin endpoints (0,4,8,16,32,64,96,128) are author mapping onto 128-mel grid — not in Jiang publication.
- Outcome: **PARTIAL** — cardinality LIT, specific bin endpoints author-mapped.
- Applied to: `_CONTRAST_BANDS` → B LIT-DERIVED (escalated)

### Q10 — Hasson 2008 / Lerner 2011 attention decay
- Query: `"Hasson 2008" temporal receptive window decay constant exp Lerner 2011 timescales`
- Tool: WebSearch
- Result: Hasson 2008 J Neurosci 28:2539 PMC2556707 + Lerner 2011 J Neurosci 31:2906 PMC3089381 papers found; both describe TRW hierarchy qualitatively (ms→minutes) with empirical durations ~0.7±0.5s words, 7.7±3.5s sentences, 38.1±17.6s paragraphs. **No specific 32-horizon ladder or ATTENTION_DECAY=3.0 published in either paper.**
- Outcome: **NEGATIVE** for bit-exact values, **POSITIVE** for inspirational anchor.
- Applied to: `HORIZON_MS`, `HORIZON_FRAMES` → B/MEDIUM (escalated); `ATTENTION_DECAY=3.0` → E5 (engineering scaling, NOT LIT)

### Q11 — Bidelman & Krishnan 2009 65-cent
- Query: `Bidelman Krishnan 2009 critical bandwidth pitch tolerance 65 cents frequency-following response`
- Tool: WebSearch
- Result: Bidelman & Krishnan 2009 J Neurosci 29:13165 (PubMed 19925180) paper found; FFR consonance/dissonance study confirmed but specific 65-cent pitch encoding precision threshold not visible in abstract/snippet.
- Outcome: **PARTIAL** — paper found, σ=0.0383 ≈ 65 cents derivation not bit-exact in primary source.
- Applied to: `_RATIO_SIGMA = 0.0383` → B/MEDIUM (escalated)

---

## Internal-inspection (no web search needed)

The following constants were attributed via internal inspection only — these are either:
- **D (IDENTITY-PLACEHOLDER):** 0/1/-1/0.5 sentinels, clamp endpoints, additive identities in textbook formulas
- **C (STRUCTURAL):** tensor dims, FFT/hop sizes, index ranges, group cardinalities, mathematical identities (12-TET, octave 2.0, π/6 spacing)
- **E (ENGINEERING-CHOICE):** sigmoid wrapper midpoints/scales, tanh wrapper scales, clamp values inside cited kernels, peak thresholds, BPM bounds, mixer weights — per context_brief §7.8 explicit risk area

No literature verification needed per §3.4 / §6.10 (mathematical identities, structural choices, engineering operational scaling).

---

## Checkpoint mini-summaries (every 500 constants)

### Checkpoint 1 — after constant 500
- A: 64, B: 16, C: 116, D: 53, E: 251, F: 0, G: 0
- Confidence: HIGH=355, MEDIUM=145
- Escalation count: 13
- Pattern-batching self-audit: each row carries individualized reason cell including the constant value and its functional role. Where identical engineering patterns occur (e.g. ε=1e-8 numerical-stability epsilons across 36 sites), the reason cell is identical (correctly — same pattern, same justification) but each row carries unique constant_id, file_path, line_number, name, value, and kind. Per Rule 6 §6 this is correct treatment, not pattern-batching.

### Checkpoint 2 — after constant 592 (full scope completed)
- A: 67 (11.3%), B: 18 (3.0%), C: 153 (25.8%), D: 70 (11.8%), E: 284 (48.0%), F: 0, G: 0
- Confidence: HIGH=430, MEDIUM=162, LOW=0
- Escalation count: 16
- Unique reasons: 421/592 (71.1%)
- Pattern-batching self-audit final: PASS

---

## Tool-usage record

| Search source | Queries | POSITIVE | PARTIAL | NEGATIVE |
|---|---|---|---|---|
| WebSearch (Google + Scholar snippets) | 11 | 7 | 3 | 1 |
| WebFetch (DOI / authoritative URL) | 1 | 1 | 0 | 0 |

Total: 12 web operations.

3-attempt hallucination guard triggered 0 times — all literature anchors either resolved POSITIVE or PARTIAL (with paper found). No constant was fabricated as POSITIVE without web verification.
