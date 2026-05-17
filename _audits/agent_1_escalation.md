# Agent 1 — F1 Escalation Queue

Total escalations: 3

## ESC-F1-001
- Constant ID: F1_00438
- File: brain/functions/f1/mechanisms/bch/extraction.py:64
- Name + Value: <expr-L> = 0.81
- Kind: expr-literal
- Tentative category: E
- Tentative confidence: MEDIUM
- Reason: BCH E3 ceiling cap 0.81 numerically matches Bidelman 2009 FFR-behavior r=0.81 (web-verified). However the role is a bounding clamp on the layer output, not a published parameter value (context_brief §7 risk-item 1 explicitly classifies BCH ceiling caps 0.90/0.85/0.80/0.81 as ENGINEERING-CHOICE bounding clamps, not free parameters). Tagged E (E2 clamp) with escalation for manual confirmation.
- Verification source: Bidelman & Krishnan 2009 J Neurosci 29(42):13165 r=0.81 (verified 2026-05-17); but code role is ceiling cap (E2 clamp) per context_brief §7 risk-item 1, not value reproduction

## ESC-F1-002
- Constant ID: F1_01090
- File: brain/functions/f1/mechanisms/mpg/temporal_integration.py:33
- Name + Value: _ALPHA = 0.7
- Kind: module-assign
- Tentative category: E
- Tentative confidence: MEDIUM
- Reason: Model coefficient '_ALPHA'=0.7 for posterior/anterior gradient blend; Rupp 2022 establishes the qualitative posterior-to-anterior gradient form but does NOT publish a specific 0.7 numeric coefficient (web search verified 2026-05-17). R9 form-LIT + author re-parameterization → ENGINEERING-CHOICE with PARTIAL.
- Verification source: Rupp 2022 (Taddeo et al.) Front Hum Neurosci 2022 establishes posterior-anterior pitch gradient qualitatively; no specific 0.70/0.30 weighting published (websearch 2026-05-17)

## ESC-F1-003
- Constant ID: F1_01091
- File: brain/functions/f1/mechanisms/mpg/temporal_integration.py:34
- Name + Value: _BETA = 0.3
- Kind: module-assign
- Tentative category: E
- Tentative confidence: MEDIUM
- Reason: Model coefficient '_BETA'=0.3 for posterior/anterior gradient blend; Rupp 2022 establishes the qualitative posterior-to-anterior gradient form but does NOT publish a specific 0.3 numeric coefficient (web search verified 2026-05-17). R9 form-LIT + author re-parameterization → ENGINEERING-CHOICE with PARTIAL.
- Verification source: Rupp 2022 (Taddeo et al.) Front Hum Neurosci 2022 establishes posterior-anterior pitch gradient qualitatively; no specific 0.70/0.30 weighting published (websearch 2026-05-17)

