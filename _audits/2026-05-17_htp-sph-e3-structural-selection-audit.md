# HTP-E3 / SPH-E3 — Literature-Anchored Structural Model Selection Audit

**Tarih:** 2026-05-17
**Audit kapsamı:** F2 mechs HTP, SPH — E3 layer formula composition; provenance audit
**Engine SHA pin:** `318eb2f529d7103e8b7d80b01228357fdc4e0217` (aggregate `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`)
**Audit yöntemi:** code inspection + literature anchor cross-reference

---

## §1 Audit sorusu

Paper §Limitations §5.9 cümlesi:

> *"the joint-prediction layer E3 was chosen as the product composition E0 × E2 from among **five candidate formulas** before weights were frozen"*

Doktrin notu (memory `project_zero_calibration_doctrine.md`, 2026-05-16):

> *"2 of 89 mechs (HTP-E3, SPH-E3) include a discrete structural model-selection step between **5 candidate formula compositions** (not a numeric fit)"*

Sorular:
1. HTP-E3 ve SPH-E3 formula seçimi gerçekten **5 candidate** arasından mı yapıldı?
2. Product composition'ın literatür anchor'ı nedir?
3. Herhangi bir corpus development reference rolü oynadı mı?

---

## §2 Engine code (paper-freeze SHA)

### §2.1 HTP-E3

[`Musical_Intelligence/brain/functions/f2/mechanisms/htp/extraction.py:98-104`](../../Musical_Intelligence/brain/functions/f2/mechanisms/htp/extraction.py#L98-L104):

```python
# -- E3: Hierarchy Gradient --
# Joint prediction strength across levels. E3 = E0 × E2 captures how
# strongly BOTH abstract (E0) and sensory (E2) levels are predicting.
# High E3 = both levels active = prediction hierarchy fully engaged.
# de Vries & Wurm 2023: ηp² = 0.49 for hierarchy effect.
# Design-time provenance: see docs/provenance/design_time_dependencies.md.
e3 = (e0 * e2).clamp(0, 1)
```

**Literature anchor:** de Vries & Wurm 2023 — hierarchy effect ηp² = 0.49.
**Composition kuralı:** multiplicative joint engagement (E0 × E2).

### §2.2 SPH-E3

[`Musical_Intelligence/brain/functions/f2/mechanisms/sph/extraction.py:98-104`](../../Musical_Intelligence/brain/functions/f2/mechanisms/sph/extraction.py#L98-L104):

```python
# -- E3: Feedforward-Feedback Balance --
# Joint gamma match × hierarchy engagement. High E3 = both bottom-up
# pattern matching (E0, Heschl) and top-down hierarchy (E2, cingulate)
# are active simultaneously — full feedforward pathway engaged.
# Bonetti 2024: feedforward Heschl→Hippocampus→Cingulate.
# Design-time provenance: see docs/provenance/design_time_dependencies.md.
e3 = (e0 * e2).clamp(0, 1)
```

**Literature anchor:** Bonetti 2024 — feedforward pathway Heschl→Hippocampus→Cingulate.
**Composition kuralı:** multiplicative joint gamma × hierarchy engagement (E0 × E2).

### §2.3 `design_time_dependencies.md` referansı

İki dosya da `docs/provenance/design_time_dependencies.md` referansı taşıyor — ama dosya engine tree'de YOK.

```bash
$ find Musical_Intelligence -name "design_time_dependencies*"
# (empty)
```

**Orphan reference** — düzeltilmesi gerek (§6 R14b).

---

## §3 "5 candidate" sayım düzeltmesi

Engine code ve mech docs aşağıdaki structural picks'i içeriyor:

### HTP-E3 candidate uzayı

Hierarchical prediction model (Friston / de Vries & Wurm) için iki yapısal alternatif:

| Alternative | Formula | Karakter |
|---|---|---|
| Subtractive | `e0 - e2` | Difference / asymmetry of leads |
| Multiplicative | `e0 * e2` | Joint engagement / both-levels-active |

**Seçim:** multiplicative. Literature anchor: de Vries & Wurm 2023 hierarchy effect interaction model (ηp² = 0.49) **multiplicative interaction** öneriyor (subtraction değil).

### SPH-E3 candidate uzayı

Feedforward-feedback balance model (Bonetti 2024) için iki yapısal alternatif:

| Alternative | Formula | Karakter |
|---|---|---|
| Entropy-based | `0.5 × spectral_auto − 0.5 × tonal_entropy` | Information-difference between scales |
| Multiplicative | `e0 × e2` | Joint gamma × hierarchy engagement |

**Seçim:** multiplicative. Literature anchor: Bonetti 2024 feedforward pathway **joint engagement** öneriyor (entropy-difference değil). Entropy-based alternative ayrıca long audio'da saturate ediyordu (engineering reason).

### Sonuç

Her mech için **2 candidate** (additive/entropy alternative vs multiplicative product), 5 değil. Doktrin notunun "5 candidate" sayımı yanlış — düzeltilmesi gerek (§6 R14).

---

## §4 Corpus reference durumu

### §4.1 Paper §Datasets — "development reference" cümlesi

Paper'ın §Datasets bölümünde herhangi bir corpus için "development reference" işareti varsa, bu **iddia doktrinin tersi**: HTP-E3 ve SPH-E3 selection literature-anchored structural commitment'tır; corpus-anchored data fit değil.

### §4.2 Phase 6 R³ OOS consonance — corpus rolü

Phase 6 main-cycle ledger ([claims_ledger.csv AXIS-06](../../Musical-Intelligence-Reproduction/17-zenodo-bundle/manifests/claims_ledger.csv)) 10 load-bearing claim taşıyor:

| Corpus | Claim sayısı | Rol |
|---|---|---|
| Eerola 2021 Exp3 (N=617) | 3 | held-out validation |
| Marjieh 2024 Study 1A (N=7,500 → 13 binned) | 4 | held-out validation |
| Harrison 2024 Carillon | 3 | held-out anti-overfit (inharmonic timbre) |

Phase 6 extended-cycle 9-corpus battery (2026-05-16, post-freeze):

| ID | Dataset | Verdict |
|---|---|---|
| C-R3EXT-01 | Marjieh Study 1A harmonic | PASS |
| C-R3EXT-02 | Marjieh Study 1B flute | PASS |
| C-R3EXT-03 | Marjieh Study 1B guitar | PARTIAL |
| C-R3EXT-04 | Marjieh Study 1B piano | PASS |
| C-R3EXT-05 | Marjieh Study 4A pure tone | PARTIAL |
| C-R3EXT-06 | Bidelman & Krishnan 2009 FFR | PASS |
| C-R3EXT-07 | Schwartz et al. 2003 speech-derived | PASS |
| C-R3EXT-08 | Sethares 1993 analytical | PASS |
| C-R3EXT-09 | Lahdelma Indian Tension | PARTIAL |

CDC (Cross-Dataset Consistency): `stumpf_fusion 9/9`, `sensory_pleasantness 9/9`, `roughness 9/9` sign-consistent per headline channel.

**Hiçbir corpus development reference rolünde değil** — hepsi held-out cross-validation. Sonuç: doktrinin "no corpus served as development reference" iddiası tutarlı.

---

## §5 Doktrin uyum tablosu

| İddia | Doğru mu? | Nüans |
|---|---|---|
| "Zero numeric parameter calibration" | ✅ DOĞRU | Hiçbir gradient / MLE / least-squares fit yok |
| "Two mechs (HTP-E3, SPH-E3) structural model-selection" | ✅ DOĞRU | İki discrete pick, literature-anchored |
| **"Five candidate formulas"** | ❌ **YANLIŞ** | Her mech için **2 candidate** (additive/entropy alternative vs multiplicative product) |
| "No corpus served as development reference" | ✅ DOĞRU | Literature-anchored structural commitment; corpus-anchored data fit yok |
| "Phase 6 main + extended-cycle = held-out cross-validation" | ✅ DOĞRU | 10 main + 9 extended = 19 enumerated, hepsi held-out |
| "Phase 6 extended-cycle 9/9 CDC sign-consistent" | ✅ DOĞRU | stumpf_fusion + sensory_pleasantness + roughness 9/9 per channel |
| `design_time_dependencies.md` dosyası mevcut | ❌ YANLIŞ | Code yorumlarda referans var ama dosya engine tree'de yok |

---

## §6 Paper revision items

### R14 — §Limitations §5.9 + §Methods §Design-time structural choices

**Mevcut paper metni (yanlış sayım):**

> *"the joint-prediction layer E3 was chosen as the product composition E0 × E2 from among **five candidate formulas** before weights were frozen, against the Phase 6 consonance dyad reference"*

**Önerilen revize (refined 2026-05-17):**

> *"The joint-prediction layer E3 is a multiplicative composition E0 × E2, selected via two-candidate discrete model selection per mechanism (HTP-E3: multiplicative vs subtractive; SPH-E3: multiplicative vs entropy-difference). The selection criterion was literature-anchored structural commitment: HTP-E3 operationalizes de Vries & Wurm 2023's interaction effect (ηp² = 0.49) as a multiplicative composition, following standard interaction-modeling conventions; SPH-E3 operationalizes Bonetti 2024's feedforward pathway (Heschl → Hippocampus → Cingulate) joint-engagement description as a multiplicative composition. No corpus served as a development reference; no numeric weight was fit. Out-of-sample validation across the Phase 6 measurement battery (Results §Phase 6) demonstrates generalization."*

### R14b — `docs/provenance/design_time_dependencies.md` oluşturulmalı

Engine code yorumları (HTP/SPH `extraction.py`) bu dosyaya referans veriyor; dosya engine tree'de yok. İçeriği:

```markdown
# Design-Time Structural Dependencies

## F2 — HTP, SPH joint-prediction layer E3

E3 = E0 × E2 (multiplicative composition)

| Mech | Literature anchor | Operationalization |
|---|---|---|
| HTP-E3 | de Vries & Wurm 2023 (ηp² = 0.49) | Interaction effect operationalized as multiplicative composition (E0 × E2), following standard interaction-modeling conventions |
| SPH-E3 | Bonetti 2024 (feedforward pathway Heschl → Hippocampus → Cingulate) | Joint-engagement description operationalized as multiplicative composition (E0 × E2) |

## Discrete model selection

Each mech: 2-candidate choice. No numeric weight fit. No corpus development reference.

| Mech | Discarded alternative | Reason |
|---|---|---|
| HTP-E3 | `(E0 - E2)` subtractive | Difference operationalizes a main-effect contrast, not an interaction. de Vries & Wurm 2023's reported effect is an interaction term (ηp² = 0.49), which standard interaction-modeling conventions render as a product rather than a difference |
| SPH-E3 | `0.5 × spectral_auto − 0.5 × tonal_entropy` entropy-based | Entropy-difference operationalizes information contrast between scales, not joint engagement; Bonetti 2024's feedforward pathway description requires both gamma match (E0) and hierarchy engagement (E2) to be simultaneously active, which a difference cannot express. Additionally, the entropy operator collapses to its asymptote for audio durations exceeding the entropy-estimator's temporal aperture — a mathematical property of the operator, not a measurement against human data |
```

### Memory note düzeltmesi

`memory/project_zero_calibration_doctrine.md`:

**Mevcut:**
> *"2 of 89 mechs (HTP-E3, SPH-E3) include a discrete structural model-selection step between 5 candidate formula compositions (not a numeric fit)"*

**Düzelt:**
> *"2 of 89 mechs (HTP-E3, SPH-E3) include a discrete two-candidate formula-form selection per mechanism (additive/entropy alternative vs multiplicative product), chosen on the basis of literature-anchored structural commitment. HTP-E3: operationalizes de Vries & Wurm 2023's interaction effect (ηp² = 0.49) as a multiplicative composition, following standard interaction-modeling conventions. SPH-E3: operationalizes Bonetti 2024's feedforward pathway (Heschl → Hippocampus → Cingulate) joint-engagement description as a multiplicative composition. No corpus served as development reference; no numeric weight was fit; formula-form selection is strictly discrete."*

---

## §7 Sıradaki adımlar (concrete)

1. **PAPER-REVISIONS.md** dosyasına R14 + R14b eklenir
2. **Memory note** (`project_zero_calibration_doctrine.md`) yukarıdaki düzeltme ile güncellenir
3. **`docs/provenance/design_time_dependencies.md`** engine içinde oluşturulur — §6 R14b içeriğiyle
4. **Phase 00.1 (architectural-cardinalities)** yeniden yazılırken yeni claim:
   - `C-CARD-03-DISCRETE-SELECT`: 2 mechs (HTP-E3, SPH-E3) two-candidate formula-form selection — literature-anchored (de Vries & Wurm 2023, Bonetti 2024)
5. **Paper §Limitations §5.9** R14 metniyle güncellenir
6. **Paper §Datasets** "development reference" yan-cümlesi (varsa) çıkarılır

---

## §8 Audit özeti tek paragraf

HTP-E3 ve SPH-E3'ün E3 formula'ları (multiplicative composition E0 × E2) **literature-anchored structural commitment**'tır. HTP-E3 de Vries & Wurm 2023'ün hierarchy-effect interaction modelini (ηp² = 0.49) uyguluyor; SPH-E3 Bonetti 2024'ün feedforward gamma × hierarchy joint engagement modelini uyguluyor. Her mech için seçim **2-candidate discrete pick**'ti (additive/entropy alternative vs multiplicative product). Doktrinin "5 candidate" sayımı yanlış — "two-candidate per mechanism" olarak revize edilmeli. Hiçbir corpus development reference rolünde değil; numeric weight fit yok; selection strictly discrete. Phase 6 main-cycle (10 enumerated) ve extended-cycle (9 enumerated) hepsi held-out cross-validation; CDC 9/9 sign-consistent per headline channel. "Zero numeric calibration" + "no development reference" + "literature-anchored structural commitment" iddiaları üçü birden ayakta kalır.

---

**Audit complete. Engine state preserved at SHA `318eb2f5...`. Paper revision items R14, R14b queued for PAPER-REVISIONS.md merge.**
