# Agent 8 — Escalation Queue

16 escalations total. 11 are `REFERENCE_VALUES` dict entries flagged R9 (form-LIT, coefficients-author re-parameterization) — paper confirmed but stored normalized [0,1] value is NOT bit-exact, tentative E PARTIAL MEDIUM. 5 are `BASELINE`/`PHASIC_THRESHOLD` ann-assign constants (same pattern: literature-anchored channel concept, but numeric value is engine-convention midpoint, NEGATIVE verification on the stored numeric, tentative E HIGH).

---

## ESC-1
- Constant ID: A8_DA_002
- File: `brain/neurochemicals/dopamine.py:16`
- Name + Value: `BASELINE = 0.5`
- Tentative category: E (E5 operational scaling)
- Tentative confidence: HIGH (NEGATIVE verification is itself high-confidence — value is clearly midpoint of unit interval, not paper-published)
- Issue: Module docstring cites Schultz 1997, Salimpoor 2011, Ferreri 2019, Berridge 2003. None of these papers publishes a normalized DA baseline of 0.5 on a [0,1] scale.
- Web search performed: yes, 2 attempts
- Web search outcome: NEGATIVE-UNVERIFIABLE for the specific numeric value 0.5
- Verification source attempted: Salimpoor 2011 Nat Neurosci 14:257; framework papers
- Recommended resolution: KEEP E. Literature citations co-located but stored value is engine-convention midpoint, not literature-published. Disclose in §Limitations alongside doctrine that BASELINE choices are operational scaling, not calibration.

## ESC-2
- Constant ID: A8_DA_003
- File: `brain/neurochemicals/dopamine.py:19`
- Name + Value: `PHASIC_THRESHOLD = 0.6`
- Tentative category: E (E3 threshold)
- Tentative confidence: HIGH
- Issue: Schultz/Salimpoor describe phasic vs tonic dissociation qualitatively; no published numeric 0.6 threshold on [0,1] scale.
- Web search performed: yes
- Web search outcome: NEGATIVE on specific value
- Recommended resolution: KEEP E. Document as engineering threshold.

## ESC-3
- Constant ID: A8_DA_004
- File: `brain/neurochemicals/dopamine.py:23`
- Name + Value: `REFERENCE_VALUES["peak_anticipatory_caudate"] = (0.78, "Salimpoor 2011, BP_ND decrease 5.7%")`
- Tentative category: E (E5)
- Tentative confidence: MEDIUM
- Issue: R9 — Salimpoor 2011 paper confirmed and reports caudate-leads-NAcc dissociation; specific 5.7% BP_ND decrease quoted in comment not directly surfaced in 4 search attempts; 0.78 is not 0.057 nor 5.7 nor a published percentage. Author normalization onto [0,1].
- Web search performed: yes, 4 attempts including value-specific queries
- Web search outcome: PARTIAL (paper confirmed, specific value not surfaced)
- Verification source attempted: http://audition.ens.fr/P2web/eval2011/BT_Salimpoor2011.pdf (WebFetch permission denied)
- Recommended resolution: KEEP E PARTIAL. If author opens Salimpoor 2011 supplementary table, the 5.7% may be verifiable — then the stored 0.78 still requires explicit normalization justification. Reference dict is documentation, not runtime parameter; no calibration risk.

## ESC-4
- Constant ID: A8_DA_005
- File: `brain/neurochemicals/dopamine.py:24`
- Name + Value: `REFERENCE_VALUES["peak_consummatory_nacc"] = (0.88, "Salimpoor 2011, BP_ND decrease 8.4%")`
- Same as ESC-3. R9 PARTIAL.

## ESC-5
- Constant ID: A8_DA_006
- File: `brain/neurochemicals/dopamine.py:25`
- Name + Value: `REFERENCE_VALUES["neutral_music_nacc"] = (0.35, "Salimpoor 2011, baseline")`
- Same pattern. R9 PARTIAL.

## ESC-6
- Constant ID: A8_DA_007
- File: `brain/neurochemicals/dopamine.py:26`
- Name + Value: `REFERENCE_VALUES["levodopa_enhancement"] = (0.92, "Ferreri 2019, pleasure +14.7%")`
- Tentative category: E PARTIAL
- Issue: Ferreri 2019 PNAS paper confirmed; +14.7% pleasure change not directly surfaced; 0.92 is author normalization.
- Recommended resolution: KEEP E PARTIAL.

## ESC-7
- Constant ID: A8_DA_008
- File: `brain/neurochemicals/dopamine.py:27`
- Name + Value: `REFERENCE_VALUES["risperidone_blockade"] = (0.28, "Ferreri 2019, pleasure -10.2%")`
- Same as ESC-6. R9 PARTIAL.

## ESC-8
- Constant ID: A8_NE_002
- File: `brain/neurochemicals/norepinephrine.py:17`
- Name + Value: `BASELINE = 0.5`
- Tentative category: E (E5)
- Issue: Doya 2002 / Aston-Jones 2005 describe NE qualitatively; no published 0.5 baseline.
- Web search outcome: NEGATIVE on stored value
- Recommended resolution: KEEP E.

## ESC-9
- Constant ID: A8_NE_003
- File: `brain/neurochemicals/norepinephrine.py:21`
- Name + Value: `REFERENCE_VALUES["resting_baseline"] = (0.50, "tonic baseline level")`
- Tentative category: E PARTIAL
- Issue: Aston-Jones 2005 confirmed for phasic/tonic LC-NE framework; specific 0.50 not published.
- Recommended resolution: KEEP E PARTIAL.

## ESC-10
- Constant ID: A8_NE_004
- File: `brain/neurochemicals/norepinephrine.py:22`
- Name + Value: `REFERENCE_VALUES["unexpected_event"] = (0.75, "phasic burst to surprising musical event")`
- Same as ESC-9. R9 PARTIAL.

## ESC-11
- Constant ID: A8_NE_005
- File: `brain/neurochemicals/norepinephrine.py:23`
- Name + Value: `REFERENCE_VALUES["familiar_predictable"] = (0.35, "low tonic during predictable sequences")`
- Same as ESC-9. R9 PARTIAL.

## ESC-12
- Constant ID: A8_OPI_002
- File: `brain/neurochemicals/opioid.py:16`
- Name + Value: `BASELINE = 0.5`
- Tentative category: E (E5)
- Issue: No literature anchor for normalized OPI baseline 0.5.
- Recommended resolution: KEEP E.

## ESC-13
- Constant ID: A8_OPI_003
- File: `brain/neurochemicals/opioid.py:20`
- Name + Value: `REFERENCE_VALUES["peak_pleasure_chills"] = (0.85, "Blood & Zatorre 2001, peak during musical chills")`
- Tentative category: E PARTIAL
- Issue: Blood & Zatorre 2001 paper confirmed for chills-PET rCBF; paper measures regional CBF, no published normalized 0.85 OPI value.
- Recommended resolution: KEEP E PARTIAL.

## ESC-14
- Constant ID: A8_OPI_004
- File: `brain/neurochemicals/opioid.py:21`
- Name + Value: `REFERENCE_VALUES["naltrexone_blockade"] = (0.30, "Mallik 2017, opioid antagonist reduces pleasure")`
- Tentative category: E PARTIAL
- Issue: Mallik 2017 paper confirmed (N=15 final; p<0.05 reduction on 0-100 MIDI slider); specific 0.30 not bit-exact, author normalization.
- Recommended resolution: KEEP E PARTIAL.

## ESC-15
- Constant ID: A8_5HT_002
- File: `brain/neurochemicals/serotonin.py:16`
- Name + Value: `BASELINE = 0.5`
- Tentative category: E (E5)
- Issue: Doya 2002 framework qualitative; no published baseline.
- Recommended resolution: KEEP E.

## ESC-16
- Constant ID: A8_5HT_005
- File: `brain/neurochemicals/serotonin.py:22`
- Name + Value: `REFERENCE_VALUES["depleted_anxious_impulsive"] = (0.30, "tryptophan depletion, short-horizon bias")`
- Tentative category: E PARTIAL
- Issue: Crockett 2009 tryptophan-depletion literature confirmed qualitatively; no published normalized 0.30 on [0,1].
- Recommended resolution: KEEP E PARTIAL.

---

## Cross-cutting recommendation for Agent 6 / final synthesis

The 15 `REFERENCE_VALUES` dict entries across 4 neurochemical files form a coherent **documentation/sensitivity-panel reference table**, not runtime cycle parameters. They are loaded as module-level dicts but NEVER read by `init_neuro`, `accumulate_neuro`, `compute_beliefs`, or the orchestrator. Verified via grep: no import-site outside the module reads `dopamine.REFERENCE_VALUES`, etc.

Implication: these E-PARTIAL flags do NOT puncture MI's zero-calibration doctrine. They are author-disclosed reference anchors for ±30% sensitivity panel design (Phase 16) and documentation of literature targets — exactly the kind of "anchored interpretation" that the paper claims for §Limitations. Recommend the audit summary explicitly notes that the 15 R9 cases are documentation, not calibration.

Recommend Agent 6 reconcile these against Agent 3's `brain/reward.py` audit (where the 7 F constants live) and Agents 1-3's per-mech NeuroLink declarations (where the actual 54-channel routing weights live) — those are the load-bearing neurochemical constants, not these reference dicts.
