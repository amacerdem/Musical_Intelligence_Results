# Agent 9 Escalation Queue

**Scope:** Brain scaffolding remainder (`brain/__init__.py`, `brain/beliefs.py`, `brain/executor.py`) + non-brain paths (`scripts/`, `contracts/`, `data/`, `utils/`).
**Total constants audited:** 213
**Escalations:** 3 (1.4%)
**Audit date:** 2026-05-17

All three escalations are R9 (form-LIT / coefficients-author boundary) cases from `scripts/runpod_train.py` — a standalone RunPod training CLI that reimplements R³/H³ features inline rather than consuming the canonical engine modules. None affect the frozen engine runtime path (`brain/orchestrator.py` → `brain/executor.py` → `brain/functions/*`).

---

## ESC-A9-001
- **Constant ID:** A9_0136
- **File:** `scripts/runpod_train.py:207`
- **Name + Value:** `<expr-L>` = `0.85`
- **Tentative category:** E (ENGINEERING-CHOICE)
- **Tentative confidence:** MEDIUM
- **Issue:** Spectral rolloff threshold 0.85 — used in `roll = (cum >= 0.85 * total).int().argmax(...)`. This is the canonical MIR spectral-rolloff fraction (librosa default = 0.85, also Tzanetakis & Cook 2002 / Peeters 2004 CUIDADO). The form is literature-canonical (MIR community convention) and the value happens to match the widespread default. Is this LIT-VERBATIM (matches established convention) or ENGINEERING (author-chose to use the convention)?
- **Web search performed:** Yes — 1 attempt (websearch-google)
- **Web search outcome:** PARTIAL
- **Verification source attempted:** Spectral rolloff 0.85 → confirmed librosa default + Tzanetakis-Cook 2002 / Peeters 2004 MIR canon
- **Recommended resolution:** Keep E with PARTIAL per R9 (no per-author-paper bit-exact publication of "0.85"; it is community-default convention). Could be upgraded to A if reviewer requests citation to librosa or Peeters 2004 MIR-toolbox documentation as the authoritative source. Engine runtime impact: NONE (this constant lives in CLI training script, not engine path).

---

## ESC-A9-002
- **Constant ID:** A9_0158
- **File:** `scripts/runpod_train.py:298`
- **Name + Value:** `mod_rates` = `[0.5, 1, 2, 4, 8, 16]`
- **Tentative category:** E (ENGINEERING-CHOICE)
- **Tentative confidence:** MEDIUM
- **Issue:** Modulation rate ladder (six octave-spaced rates 0.5–16 Hz) for modulation-spectrum feature in CLI training script. Form (octave-spaced rate ladder) is literature-canonical for modulation-spectrum analysis (Houtgast 1985, Sukittanon & Atlas 2004, Schimmel 2007). Specific endpoint set [0.5, 16] is author re-parameterization (could plausibly extend to 0.25 or to 32 Hz). R9 boundary case.
- **Web search performed:** Yes — 1 attempt
- **Web search outcome:** PARTIAL
- **Verification source attempted:** Modulation-spectrum analysis literature uses octave-spaced rate ladders; no single canonical 6-rate set bit-equal to [0.5, 1, 2, 4, 8, 16]
- **Recommended resolution:** E with PARTIAL per R9. Engine runtime impact: NONE (CLI training script).

---

## ESC-A9-003
- **Constant ID:** A9_0164
- **File:** `scripts/runpod_train.py:338`
- **Name + Value:** `horizons` = `[4, 8, 16, 32, 64, 128, 256]`
- **Tentative category:** E (ENGINEERING-CHOICE)
- **Tentative confidence:** MEDIUM
- **Issue:** Power-of-2 horizon ladder (7 frames, ~23 ms–1.5 s) for CLI H³ feature extraction. **Differs** from canonical 32-horizon engine ladder (`ear/h3/bands/*` Micro/Meso/Macro/Ultra spanning 5.8 ms–981 s). The form (octave-spaced) is consistent with Hasson 2008 TRW inspiration, but this script's reduced 7-horizon ladder is a CLI training-script approximation, not the engine canonical ladder.
- **Web search performed:** Yes — 1 attempt
- **Web search outcome:** PARTIAL
- **Verification source attempted:** Hasson 2008 / Lerner 2011 / Murray 2014 TRW literature; no specific 7-horizon power-of-2 list bit-equal in cited primaries
- **Recommended resolution:** E with PARTIAL per R9. Engine runtime impact: NONE (CLI training script does not affect frozen engine SHA `318eb2f5...`).

---

## Summary of escalation pattern

All three escalations sit in `scripts/runpod_train.py` — a CLI training driver that **reimplements** R³/H³/C³ feature extraction inline rather than calling the canonical `Musical_Intelligence.ear.r3` / `ear.h3` modules. The constants in this file therefore are NOT part of the frozen engine runtime path (`brain/orchestrator.py` → `brain/executor.execute()`) that pins paper claims and Zenodo bundle SHA `318eb2f5...`. They are CLI utility constants used for an offline RunPod training dataset generator.

**Reviewer disclosure recommendation:** Note in audit summary that scripts/ training utilities contain three R9 boundary cases, all in CLI driver code outside frozen engine call-graph; they do not affect MI engine claims.
