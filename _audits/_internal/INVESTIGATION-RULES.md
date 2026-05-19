# `INVESTIGATION-RULES.md` — Constant-Level Provenance Audit with Literature Verification

**Tarih:** 2026-05-17
**Engine SHA:** `318eb2f529d7103e8b7d80b01228357fdc4e0217`
**Engine aggregate:** `482ade45c50f5d3bf5c90c122e495b2c3230e6e6edc6542f72f22e3b5da37f88`
**Audit kapsamı:** 16,222 named-position numeric constants
**Audit yöntemi:** Manual per-constant inspection + literature verification via web search
**Audit hedefi:** Constant-level provenance attribution with bibliographic verification
**Refinement version:** v1.1 (2026-05-17, R1-R7 integrated)

---

## §1 Mission statement

V3 classifier file-level citation inheritance kullanıyor — bu **over-attribution** üretiyor. "LIT-FROZEN %49" rakamı reviewer için yanıltıcı çünkü co-location'ı derivation ile karıştırıyor.

Bu audit'in görevi her sabiti **iki katmanlı doğrulama** ile incelemek:

**Katman 1 — Code locality:** Sabitin kod tabanındaki konumu, citation yakınlığı, fonksiyonel rolü.

**Katman 2 — Literature verification:** Sabitin değerinin veya formülünün gerçekten cited literatürde yayınlanmış olup olmadığını **web search ile doğrulama**.

İkinci katman kritik çünkü kod yorumu "Sethares 1993" diyor olabilir ama:
- Sethares 1993'te o değer yayınlanmamış olabilir
- Yazar yanlış citation vermiş olabilir
- Sabit Sethares'in formülünden değil, başka bir kaynaktan gelmiş olabilir
- Sabit author interpretation'ı olabilir, literatürde explicit değil

Agent'lar baseline knowledge'ından emin olamaz. Literatür **doğrulanmalı**, varsayılmamalı.

**Anti-hallucination commitment:** Agent web'de paper bulamazsa, "öyle olmalı" diye varsaymak yerine LOW confidence + escalation seçer. Honest negative > fabricated positive.

---

## §2 Seven attribution categories — precise definitions

Her sabit tek bir kategoriye atfedilir. Kategoriler hiyerarşik değil, ayrık.

### Category A — LIT-VERBATIM
**Tanım:** Sabit, primary literatür kaynağında **birebir aynı değerle** yayınlanmış. Web search ile bibliyografik olarak doğrulanmış.

**Üç koşul birden sağlanmalı:**
1. Kod tarafında: line/block-level citation present (3-line locality kuralı, §5)
2. Literatür tarafında: web search ile orijinal kaynak doğrulandı
3. Değer match: literatürdeki yayınlanan değer ile kod'daki değer aynı (±0.01 tolerance veya rounding-aware match)

**Pozitif örnekler:**
- `D_STAR = 0.24` # Sethares 1993 roughness peak threshold
  - Verification: Sethares (1993) JASA 94(3):1218-1228, equation 3, D*=0.24
- `KK_MAJOR_PROFILE = [6.35, 2.23, 3.48, ...]`
  - Verification: Krumhansl & Kessler (1982) Psychological Review, Table 2

**Reddetme kriterleri:**
- Web search literatürü bulamazsa → LOW confidence, escalate
- Literatür mevcut ama değer farklı → REJECT, kategori E'ye düş
- Citation modüldeki başka bir formül için ise → REJECT (co-location, not derivation)

### Category B — LIT-DERIVED
**Tanım:** Sabit, literatür kaynağındaki bir **formül veya spec'ten** analitik olarak hesaplanmış. Değer literatürde aynen yayınlanmamış ama formül deterministik olarak üretiyor. Web search ile formülün literatürde var olduğu doğrulanmış.

**Dört koşul:**
1. Kod yorumu veya docstring formülün literatür kaynağını gösteriyor
2. Sabitin nasıl hesaplandığı görünür (algoritmik veya analitik adım)
3. Web search ile formül literatürde doğrulandı
4. Hesaplama deterministik (fit, optimization, training değil)

**Pozitif örnekler:**
- `ATTENTION_KERNEL_DECAY = 3` from `exp(-3*k/h)` per Hasson 2008 timescale spec
- `BARK_CENTERS_24` computed from Zwicker-Fastl Bark scale definition

**Reddetme kriterleri:**
- Formül literatürde var ama bu sabit author choice ise → E'ye düş
- Web search formülü bulamazsa → LOW confidence

### Category C — STRUCTURAL
**Tanım:** Sabit sistemin **topoloji veya tip imzasını** tanımlıyor. Empirik değer değil. Web search gerekmiyor çünkü structural choice.

**Pozitif örnekler:**
- `N_REGIONS = 26` (RAM cardinality)
- `N_MECHANISMS = 89` (C³ count)
- `R3_DIM = 97` (R³ output dimensionality)
- `NEUROCHEM_CHANNELS = 4` (DA, NE, OPI, 5-HT)
- `H3_HORIZONS = 32` (T³ horizon count)
- Region/channel index values
- Citation metadata (`citation_year = 1993` — reference metadata, not empirical value)

**Mathematical identities (web search gerekmez):**
- `OCTAVE_RATIO = 2.0`, `SEMITONE_RATIO = 2**(1/12)`, `PI`, `E`

### Category D — IDENTITY-PLACEHOLDER
**Tanım:** Trivial 0, 1, -1, veya sentinel. Operasyonel anlamı yok.

**Pozitif örnekler:**
- `init_value = 0.0`, `default_multiplier = 1.0`, `sentinel_index = -1`

**Reddetme kriterleri:**
- 0/1 anlamlı parametre ise (örn. probability threshold = 0, gain_max = 1.0 as upper clamp) → REDDET, E'ye düş

### Category E — ENGINEERING-CHOICE
**Tanım:** Author choice. Literatür-anchored değil. Sistemin çalışması için seçilmiş.

**Beş alt-kategori:**
- **E1 — Numerical stability:** `EPS = 1e-8`, `LOG_FLOOR = 1e-10`
- **E2 — Clamp/bound:** `gain_clamp = (0.05, 0.95)`, `output_clip = (0.0, 1.0)`
- **E3 — Threshold:** `SILENCE_DB = -60`, `MIN_PEAK_PROMINENCE = 0.1`
- **E4 — Mixer weight:** `0.5 * a + 0.5 * b`, `WEIGHT_TREND = 0.3`
- **E5 — Operational scaling:** `SCALE_FACTOR = 12.0`, `NORMALIZE_BY = 100.0`

### Category F — HAND-SPECIFIED-DISCLOSED
**Tanım:** Author choice, paper'da **explicit olarak disclosed**.

**Kesin liste (7 sabit, sadece bunlar):**
- `w_S = 1.5`, `w_R = 0.8`, `w_E = 0.5`, `w_M = 0.6` (reward formula weights)
- `phi_fam_star = 0.5` (familiarity peak)
- `g_DA_wanting = 0.6`, `g_DA_liking = 0.4` (dopamine split)

Başka hiçbir hand-tuned sabit F'ye atfedilemez.

### Category G — DEAD-CODE-UNREACHABLE *(R5)*
**Tanım:** Sabit kodda mevcut ama call-graph'tan unreachable veya superseded — engine runtime path'inde tüketilmiyor.

**Pozitif örnekler:**
- Legacy mech `__init__` artifacts henüz silinmemiş
- Commented-out blocks içinde (ama yorumda değil, gerçek expression olarak)
- Symbol exported ama `__all__`'da yok

**Tespit yöntemi:** AST walker `kind` alanında gözükenler engine call-graph'ta tüketilmiyorsa G. Şüphe varsa E5 + `unreachable` tag.

---

## §3 Web search verification protocol

Her LIT-VERBATIM ve LIT-DERIVED kategorizasyonu **mutlaka** web search verification gerektirir. ENGINEERING için opsiyonel ama recommended.

### §3.1 Search tool priority order

Anthropic agent tool set'inde kullanılacak araçlar **bu sırayla**:

1. **`WebSearch`** (built-in) — query patterns from §3.2; Google search surface covers Google Scholar/Semantic Scholar abstract excerpts
2. **`WebFetch`** for specific URLs surfaced in step 1 (DOI links, arXiv URLs, journal abstract pages)
3. **`WebSearch`** with broader fallback queries (textbook/review article)
4. **`WebSearch`** with author homepage / institutional repository queries
5. **Bütün 1-4 NEGATIVE → LOW confidence + escalation**

API-spesifik (Scholar/OpenAlex/Semantic Scholar) tool **gerekmiyor**; WebSearch zaten Scholar excerpt'lerini surface ediyor. Tool tercihini `verification_method` CSV kolonunda kayıt et (`websearch-google` / `webfetch-doi` / `websearch-scholar-snippet`).

### §3.2 Search query construction

**LIT-VERBATIM için 3 query pattern:**
- Query 1 — Author + concept + value: `"Sethares 1993" roughness "0.24"`
- Query 2 — Concept + parameter name: `"Bark scale" critical band centers 24`
- Query 3 — Direct DOI/paper search

**LIT-DERIVED için 2 query pattern:**
- Query 1 — Formula + author: `Hasson 2008 temporal receptive window decay`
- Query 2 — Operational definition: `"intrinsic timescales" Murray 2014`

### §3.3 Verification criteria

**Outcome 1 — POSITIVE CONFIRMATION:**
- Paper found (DOI/direct link)
- Value/formula matches code (within tolerance)
- Functional role match
→ A or B, confidence HIGH

**Outcome 2 — PARTIAL CONFIRMATION:**
- Paper found but exact value not published
- Formula published but specific instantiation author-derived
→ B (MEDIUM) or E (MEDIUM), escalate

**Outcome 3 — NEGATIVE / NO MATCH:**
- Paper not found in 3 search attempts
- Citation found but value mismatched
- Citation accurate but different context
→ E (MEDIUM) or REJECT, mandatory escalation

### §3.4 Hallucination guard *(R3 — CRITICAL)*

**Eğer 3 search attempt sonrasında cited paper bulunamazsa:**
- DOI yok / full text yok / abstract snippet yok / secondary source yok
- Agent **ASLA** "paper'da öyle olmalı" diye varsaymaz
- Otomatik **LOW confidence + escalation queue**
- `verification_outcome = "NEGATIVE-UNVERIFIABLE"`, `verification_source = "3 search attempts failed"`

**Yapay POSITIVE üretmek = audit failure.** Honest negative > fabricated positive.

### §3.5 Search documentation requirement

Her web search **kayda alınmalı**. CSV `verification_notes`:

```
search_query_1: "Sethares 1993 roughness D* 0.24"
search_outcome: POSITIVE
verification_source: Sethares 1993 JASA 94(3):1218-1228, Equation 3
value_match: exact (0.24 = 0.24)
notes: Confirmed via Google Scholar abstract + first-page snippet
```

### §3.6 Common verification pitfalls

1. **Generic citation, specific value mismatch:** "Sethares 1993" cite edilmiş ama kod'daki sabit Sethares'in coefficient'inden türetilmiş başka değer → LIT-DERIVED, not LIT-VERBATIM
2. **Multi-paper citation:** Hangisinden geliyor? Üçünü kontrol et, en yakın eşleşeni al
3. **Author cited but value author-derived:** de Vries & Wurm 2023 interaction model **tanımlıyor**, multiplicative çoklama önermiyor → LIT-DERIVED, COMPOSED tag
4. **Common knowledge vs cited:** Octave 2.0 / semitone 2^(1/12) → STRUCTURAL (citation gereksiz)
5. **Atlas centroid match:** MNI region centroid (örn. A1/HG (-50, -18, 8)) → cited atlas (Eickhoff 2005) verify
6. **Self-citation:** Erdem'in kendi önceki paper'ı → LIT kategorisi DEĞİL (E veya C)

---

## §4 Iş bölümü — 6 agent görevi (refined per R2 + R7)

### Agent 1 — F1 + F2 mechanisms (perceptual + prediction core)
**Kapsam:** `brain/functions/f1/*`, `brain/functions/f2/*`
**Tahmin sabit sayısı:** ~3,200

**Critical mechanisms:** F1 BCH, PNH, TPIO, HTP-E0/E1/E2, MIAA, PSCL; F2 HTP-E3, SPH-E3, UDP, ICEM

**Critical literature verifications:** Sethares 1993 D*/C1/C2, Plomp-Levelt 1965 critical bandwidth, Stumpf 1890, de Vries & Wurm 2023, Bonetti 2024, Cheung 2019, Pearce IDyOM

**Özel dikkat:** F1 modülleri Sethares-Plomp-Levelt yoğun cite eder. Mixer weights, clamp bounds, threshold values genelde ENGINEERING. Sadece spectral integration coefficients, critical band parameters LIT-VERBATIM.

### Agent 2 — F3 + F4 + F5 mechanisms (attention + memory + emotion)
**Kapsam:** `brain/functions/f3/*`, `brain/functions/f4/*`, `brain/functions/f5/*`
**Tahmin sabit sayısı:** ~3,000

**Critical mechanisms:** F3 IACM, ACM, SDL, STANM; F4 MMP, memory mechanisms; F5 VMM, IUCP, NEMAC, DAP

**Critical literature verifications:** Hasson 2008 temporal receptive windows, Murray 2014 intrinsic timescales, Berlyne 1971 inverted-U (4x(1-x) kernel), Aston-Jones locus coeruleus, Schoeller 2023 chill construct

**Özel dikkat:** Berlyne 4x(1-x) kernel — paper'da **explicit** mi yayınlanmış yoksa author analytic interpretation mı? Web search kritik.

### Agent 3 — F6 + F7 + F8 mechanisms (reward + motor + learning)
**Kapsam:** `brain/functions/f6/*`, `brain/functions/f7/*`, `brain/functions/f8/*`
**Tahmin sabit sayısı:** ~2,800

**Critical mechanisms:** F6 DAED, CDMR, AAC; F7 NSCP, DDSMI; F8 EDNR, learning

**Critical literature verifications:** Salimpoor 2011/2013 (caudate-NAcc, +0.9s lag), Schultz 1998, Berridge & Kringelbach 2009, Doya 2002, Mallik 2017, Putkinen 2025, Ferreri 2019

**Özel dikkat — kritik isolation:** `brain/reward.py:33-94` — sadece **7 sabit** HAND-SPECIFIED-DISCLOSED (F). Diğer mixer weights, intermediate constants ENGINEERING (E). Bu ayrımı çok dikkatli yap.

### Agent 4 — R³ + T³ infrastructure (perceptual front-end + temporal grammar)
**Kapsam:** `ear/*` (R³ groups A-K), `brain/h3/*` (T³)
**Tahmin sabit sayısı:** ~3,500

**Critical components:** R³ Groups A-K, T³ 32 horizons / 24 morphological operators / 3 causal laws / exponential attention kernel

**Critical literature verifications:** Sethares 1993, Plomp-Levelt 1965, Krumhansl-Kessler 1982, Davis-Mermelstein 1980 MFCC, Zwicker-Fastl 1990 Bark scale, Stumpf 1890, Hasson 2008, Murray 2014

**Özel dikkat:**
- R³ companion preprint atom-level provenance (102 atoms, 46% direct) **atom-level**, bu audit **constant-level**. R³ companion'ın %46 direct rate constant-level'da %5-15 arası olabilir
- T³ horizons: 32 horizon count = STRUCTURAL; 32 horizon **değerleri** (5.8 ms, ... 16 dakika) = LIT-DERIVED (Hasson spec)

### Agent 5 — Brain infrastructure (RAM + NeuroLink + reward + scaffolding + remainder paths) *(R2)*
**Kapsam:** `brain/ram/*`, `brain/neurolink/*`, `brain/reward.py`, `brain/beliefs/*`, `brain/cycle/*`, **plus** `scripts/*`, `contracts/*`, `data/*`, `utils/*`
**Tahmin sabit sayısı:** ~3,700 (3,500 RAM/neurolink + 201 scripts/contracts/data — coverage gap closed)

**Critical components:** RAM 26 region MNI centroids, RAM 529 RegionLink weights, NeuroLink 54 channel routing, 4 neuromodulator channels, Bayesian belief cycle, reward formula (7 disclosed), belief precision

**Critical literature verifications:** MNI152 atlas (Eickhoff 2005, Talairach-Tournoux 1988), region-specific peaks (Patterson, Norman-Haignere, Salimpoor, Blood-Zatorre, Koelsch, Brattico), Friston 2005, Doya 2002, Schultz 1998, Berridge-Kringelbach 2009

**Özel dikkat:**
- RAM 529 edge weights: per-edge citation present → LIT-VERBATIM; normalized 0-1 author scaling → ENGINEERING
- NeuroLink 54: 45 canonical (citation present) + 9 fall-through (ENGINEERING)
- `scripts/` (~130 sabit) ağırlıklı E (training utilities, not engine runtime)
- `contracts/dataclasses/` Citation/RegionLink/NeuroLink/LayerSpec/H3DemandSpec spec parameters genellikle C (STRUCTURAL)

### Agent 6 — Reconciliation + final synthesis *(R7)*
**Kapsam:** post-parallel coordination
**Görev:** §9 reconciliation phase + final audit deliverable
**Tahmin wall-clock:** 30-45 dk
**Çalışma şekli:** Agent 1-5 bitince başlar; merge + duplicate detection + consistency check + summary

---

## §5 Investigation rules — strict procedure

### Rule 1 — Citation locality test (Layer 1: Code)
Sabitin line'ına bak. 3-line window içinde citation var mı?
- Same line / previous 2 lines / following 1 line

**Eğer 3-line locality başarısız → LIT-VERBATIM veya LIT-DERIVED ATFEDİLEMEZ. Module docstring inheritance kullanma.**

### Rule 2 — Block-level test
3-line failure'dan sonra enclosing function/method/class scope'una bak:
- Citation **bu sabit için mi** yoksa fonksiyonun başka bir parçası için mi?
- Specific → continue verification; Other formula → REJECT

### Rule 3 — Web search verification (Layer 2: Literature)
§3'te detaylı protokol. **Mandatory for A and B.**

### Rule 4 — Value semantics test
- Topology/dimension/index → C
- Trivial init/sentinel → D
- Reward formula (7 disclosed) → F
- Engineering operation (clamp, eps, mixer, threshold) → E
- Dead-code / unreachable → G
- Literature-verified value → A or B

### Rule 5 — Conservative attribution
**Şüphe durumunda E (ENGINEERING-CHOICE) seç.** Asla yukarı kategorize etme. **Anti-overclaim** kuralı.

- A iddiası için **HIGH confidence** lazım (3-line + web search POSITIVE)
- B iddiası için **MEDIUM+ confidence** lazım (block-level + web search POSITIVE/PARTIAL)
- Düşük confidence → E + escalation

### Rule 6 — Per-constant independence *(R4 — CRITICAL)*
Aynı dosyada birden fazla sabit varsa, her birine **bağımsız** kategori ver. Modül Sethares cite ediyor diye her sabit LIT-VERBATIM olmaz.

**Pattern-batching prohibition:**
> *"Aynı dosyadaki 50 sabit aynı kategoriye düşse bile, her birine ayrı `reason` cümlesi yazılmalı. Pattern-batching = audit failure."*

Örnek:
```python
# brain/functions/f1/mechanisms/bch/extraction.py
# Implements Sethares 1993 roughness model

D_STAR = 0.24      # Sethares 1993 D* coefficient    → A (LIT-VERBATIM)
EPS = 1e-8         # numerical stability              → E (ENGINEERING)
MIN_PEAK = 0.001   # spectral peak detection threshold → E (ENGINEERING)
OUTPUT_CLAMP = (0.0, 1.0)  # operational bound       → E (ENGINEERING)
N_BANDS = 24       # Bark scale band count            → C or B (Bark-canonical mı?)
```

### Rule 7 — Documentation completeness
CSV'de zorunlu kolonlar (§7).

### Rule 8 — Checkpoint discipline *(R1)*
Her **500 sabit** kategorize edildikten sonra:
- Mini summary üret (sayım, dağılım, escalation count)
- Önceki 500 sabit içinde pattern-batching yapmadığını verify et
- Confidence dağılımı sağlıklı mı (çok fazla HIGH ya da çok fazla LOW yok)

---

## §6 Edge cases — special handling

1. **Composed constants:** Birden fazla literatür kaynağı → B (LIT-DERIVED), `COMPOSED-MULTI-SOURCE` tag
2. **Mathematical identities:** π, e, octave 2.0, semitone 2^(1/12) → C
3. **Region MNI centroids:** 78 koordinat → atlas-verified → A; citation yok → C
4. **Hand-tuned mechanism mixers:** 7 disclosed → F; diğer hepsi → E4
5. **Spec parameters:** LayerSpec/H3DemandSpec positional args — index → C; weight → E; year metadata → C
6. **Default kwarg literals:** neutral (0/1/-1) → D; operational → E; citation-anchored → A/B
7. **Implicit expression literals:** `(x - 0.5) * 2.0` → E (no 3-line locality)
8. **Historical citations:** Stumpf 1890, Helmholtz 1863 — secondary source verification; doğrulanamazsa MEDIUM + escalation
9. **Self-citation:** Erdem'in kendi paper'ı → E veya C, LIT değil
10. **Algorithm implementation constants:** FFT 1024/2048, hop size, cosine window → C (signal processing standard)

---

## §7 Output format — agent CSV deliverable

Her agent kendi kapsamı için CSV üretir. **Zorunlu kolonlar:**

```csv
constant_id,file_path,line_number,name,value,kind,category,reason,citation,verification_method,verification_outcome,verification_source,confidence,escalation_flag,notes
```

**Örnek satırlar:**

```csv
BCH_DSTAR_001,brain/functions/f1/mechanisms/bch/extraction.py,45,D_STAR,0.24,module-assign,A,"Sethares 1993 roughness peak threshold D* coefficient",Sethares 1993,websearch-google,POSITIVE,"Sethares 1993 JASA 94(3):1218-1228 Eq. 3",HIGH,FALSE,"3-line locality + value exact match"

BCH_EPS_002,brain/functions/f1/mechanisms/bch/extraction.py,67,EPS,1e-8,module-assign,E,"Numerical stability epsilon",NONE,websearch-google,NEGATIVE,"Not in Sethares 1993; standard engineering choice",HIGH,FALSE,"Module cites Sethares but EPS is engineering decision"

HTP_E3_FORMULA_003,brain/functions/f2/mechanisms/htp/extraction.py,98,e3,e0*e2,expr-literal,B,"Multiplicative composition operationalizing de Vries-Wurm 2023 interaction model",de Vries & Wurm 2023,websearch-scholar-snippet,PARTIAL,"de Vries & Wurm 2023 J Cogn Neurosci; specifies interaction (ηp²=0.49) not explicit multiplicative formula",MEDIUM,TRUE,"Composition derivation MEDIUM; literature anchor present, specific multiplicative form is author operationalization"

REWARD_WS_005,brain/reward.py,45,w_S,1.5,module-assign,F,"Surprise weight in reward formula, paper-disclosed",Paper §Reward formula,paper-anchor,POSITIVE,"Paper Methods §Reward (this paper)",HIGH,FALSE,"One of 7 hand-specified disclosed reward weights"
```

### Confidence levels — strict definition

- **HIGH:** A with 3-line locality + web search POSITIVE + exact match; B with block-level citation + POSITIVE + deterministic mapping; C/D/F definitional certainty
- **MEDIUM:** A attempted with PARTIAL verification; B with ambiguous literature anchor; E recommended verification but skipped
- **LOW:** Citation present but web search NEGATIVE; ambiguous functional role; multiple competing categories → mandatory escalation

---

## §8 Escalation queue protocol

```markdown
## ESC-[N]
- Constant ID: [unique ID]
- File: [path:line]
- Name + Value: [name = value]
- Tentative category: [A-G]
- Tentative confidence: LOW
- Issue: [why uncertain]
- Web search performed: [yes/no, attempts count]
- Web search outcome: [POSITIVE/PARTIAL/NEGATIVE-UNVERIFIABLE/N/A]
- Verification source attempted: [paper title or N/A]
- Recommended resolution: [manual review action]
- Audit agent: [Agent 1-5]
```

Audit sonu manual review → `escalation_resolutions.md` → final CSV update.

---

## §9 Cross-agent reconciliation *(Agent 6 görevi)*

### Step 1: Merge all agent CSVs
```python
audit_combined = pd.concat([
    pd.read_csv(f'agent_{i}_audit.csv') 
    for i in range(1, 6)
])
```

### Step 2: Duplicate detection
- Aynı `(file_path, line_number, name)` iki agent tarafından kategorize edildi mi?
- Kategori uyuşuyor mu? Uyuşmuyorsa **tutarsızlık**.

### Step 3: Pattern consistency check
- Aynı pattern (`EPS = 1e-8`) farklı modüllerde aynı kategoriye atfedilmiş mi?
- Aynı literature anchor farklı agent'lar tarafından tutarlı şekilde verified mi?

### Step 4: Citation consistency check
- Aynı citation farklı agent'lar tarafından farklı kategoriler için kullanıldıysa **neden**?
- Açıklanabilir tutarsızlık (mod-1 LIT-VERBATIM, mod-2 LIT-DERIVED) → OK
- Açıklanamayan → escalation

### Step 5: Confidence distribution check
- Her agent'ın HIGH/MEDIUM/LOW dağılımı benzer mi?
- Over-confident agent (çok HIGH) / under-confident agent (çok LOW) flag

### Step 6: Final reconciliation log + summary

---

## §10 Final audit deliverable

**Engine state preserved:** SHA `318eb2f5...`

**Output files:**
1. `audit_combined.csv` — 16,222 sabit, full per-constant attribution
2. `agent_1_audit.csv` through `agent_5_audit.csv` — per-agent raw outputs
3. `escalation_queue.md` — LOW confidence + ambiguous cases
4. `escalation_resolutions.md` — manual review decisions
5. `reconciliation_log.md` — cross-agent consistency (Agent 6)
6. `bucket_distribution_real.csv` — final 7-category distribution
7. `literature_verification_log.md` — all web searches + outcomes
8. `audit_summary.md` — high-level findings + paper revision implications

**Expected final distribution (sayım tahmini, gerçek dağılım audit sonucu):**
- A (LIT-VERBATIM): ~5-10% (800-1,600)
- B (LIT-DERIVED): ~5-10% (800-1,600)
- C (STRUCTURAL): ~35-40% (5,500-6,500)
- D (IDENTITY-PLACEHOLDER): ~8-10% (1,300-1,600)
- E (ENGINEERING-CHOICE): ~30-45% (5,000-7,000)
- F (HAND-SPECIFIED-DISCLOSED): 7 (exact)
- G (DEAD-CODE-UNREACHABLE): <1% (estimated 50-150)

**Total: 16,222 (±0)**

---

## §11 Time budget — refined per R1

5 audit agent paralel + Agent 6 reconciliation. **Yeni budget:**

**Per-agent breakdown (4-6 saat wall-clock):**
- 30 dk: kapsam keşfi, dosya listesi, ön-tarama, key citations identification
- 3-5 saat: line-by-line inspection + web search verification
  - Most constants (C/D/E): ~2-5 saniye/sabit (fast triage)
  - A/B candidates (~500/agent): ~1-2 dk/sabit (web search verification)
- 30 dk: CSV finalization + escalation queue documentation
- Checkpoint discipline (Rule 8): her 500 sabit sonrası ~5 dk mini-summary

**Agent 6 reconciliation (30-45 dk):**
- Cross-agent merge + duplicate/inconsistency detection
- Confidence distribution review
- Final summary generation

**Total wall-clock:** ~5-7 saat (paralel agent 1-5) + ~45 dk (sequential Agent 6) = ~6-8 saat
**Total agent-hours:** ~30-40 agent-hour

---

## §12 Critical reminders — every agent reads before starting

1. **Co-location ≠ derivation.** Modül citation co-located ≠ constant literature-derived.

2. **Web search verification is mandatory for A and B.** Kodda citation görsen bile literatürde gerçekten o değer/formül var mı doğrula.

3. **Conservative attribution.** Şüphe varsa ENGINEERING (E). Yukarı kategorize etme.

4. **Per-constant independence.** Modüldeki her sabit ayrı değerlendirilir. **Pattern-batching = audit failure.**

5. **Document your search.** Her web search kayıt altına alınır.

6. **7 disclosed reward weights → F. Diğer hepsi → E.** Bu ayrımı çok dikkatli yap.

7. **Mathematical identities (π, e, octave 2.0, semitone 2^(1/12)) → STRUCTURAL.** Web search gereksiz.

8. **Confidence calibration.** HIGH = full verification chain. MEDIUM = partial. LOW = uncertain → escalation.

9. **Honest negative results.** Web search NEGATIVE bulursan, attribution revize. **Yapay POSITIVE üretme.**

10. **Reasoning trail.** Her decision için `reason` alanına gerekçe cümle yaz. Otomatik etiket değil, manuel açıklama.

11. **3-attempt hallucination guard.** 3 search attempt sonrası paper bulunamazsa → LOW + NEGATIVE-UNVERIFIABLE + escalation. Asla "olmalı" diye varsayma.

12. **Checkpoint every 500 constants.** Mini summary + pattern-batching audit.

---

## §13 Audit launch command (per agent)

```
You are Agent [N] of 5 in a parallel constant-level provenance audit.

CRITICAL: Read INVESTIGATION-RULES.md and context_brief.md fully before starting any analysis.

Your scope: [agent-specific scope from §4]
Expected constant count: [~3,000-3,700]
Time budget: 4-6 hours wall-clock.

Method:
1. Inventory all numeric constants in your scope (use AST walker output at 
   datasets/paper-anchors/cardinality/raw_constants_inventory.csv, filtered to your scope)
2. For each constant: apply Investigation Rules §5 in order
3. For Category A/B candidates: MANDATORY web search verification per §3
4. Document every decision in CSV per §7
5. Escalate LOW confidence cases per §8
6. Checkpoint every 500 constants per Rule 8

Tool priority for verification:
- WebSearch (built-in) primary
- WebFetch for specific paper URLs surfaced
- 3-attempt hallucination guard: paper bulunamazsa LOW + escalate, ASLA "olmalı" varsayma

Apply conservative attribution: when in doubt, ENGINEERING-CHOICE (E).
Co-location ≠ derivation. Each constant evaluated independently.
Document your literature verifications. Honest negative results required.

Pattern-batching prohibition: aynı dosyadaki 50 sabit aynı kategoriye 
düşse bile her birine ayrı `reason` yaz. Pattern-batching = audit failure.

Cross-agent reconciliation will happen after all 5 audit agents complete (Agent 6).

Output: per-agent CSV at agent_[N]_audit.csv with full attribution chain.
```

---

**Audit yöntemi:** bibliographic verification + code locality + per-constant independence.
**Audit philosophy:** anti-overclaim, conservative attribution, verifiable provenance, anti-hallucination.
**Expected outcome:** gerçek literature-anchored constant rate (5-10%) ile engine'in compositional contribution'ı (95%+) doğru oranlarda gösterilecek.

---

**v1.1 refinements (2026-05-17) integrated:**
- R1: Time budget realistic (4-6 hr/agent vs original 1.5-2 hr); Rule 8 checkpoint discipline
- R2: Agent 5 scope coverage extended to scripts/, contracts/, data/, utils/ (~200 sabit gap closed)
- R3: §3.4 hallucination guard explicit; 3-attempt rule; NEGATIVE-UNVERIFIABLE outcome
- R4: Rule 6 pattern-batching prohibition reinforced; launch command'da repeat
- R5: Category G (DEAD-CODE-UNREACHABLE) added; 7 kategori
- R6: Context brief via prep agent (separate workflow step, not in this file)
- R7: Agent 6 reconciliation phase explicit; §4'te listed

---

## §14 Update v1.2 — Pilot-derived refinements (2026-05-17, post Agent 4)

Agent 4 (R³+T³ pilot) tamamlandı: 592/592 sabit attribution, A=%11.3 / B=%3.0 / E=%48 dağılım, %72.6 HIGH confidence, 0 F (doğru), 16 escalation. İki refinement validated:

### Rule R8 — AST walker `citation_author` column reliability

**Sorun:** AST walker output'taki `citation_author` kolonu false-positive citations üretiyor (token-level matches: "hannon", "ding" gibi isimler literature author olarak yanlış işaretleniyor).

**Kural:**

Agent'lar AST walker'ın `citation_author` kolonunu **bağımsız bir kanıt olarak kullanmaz**. Bu kolon yalnızca **yönlendirme amaçlı** (heuristic hint) — "bu modülde citation olabilir, manuel kontrol et" sinyali. Final attribution **Rule 1 (3-line locality) + Rule 3 (web search verification)** üzerinden bağımsız doğrulanır.

**Pratik uygulama:**
- AST walker `citation_author = "Sethares"` derse: agent 3-line locality kontrolü yapar, citation gerçekten var mı doğrular
- Web search ayrı yapılır
- Walker kolonu **delil değil, ipucu**

**Anti-pattern:**
```
WRONG: AST walker citation_author=Sethares → category = A (LIT-VERBATIM)
RIGHT: AST walker hint → manuel 3-line locality check → web search verification → final category
```

### Rule R9 — Form-LIT / coefficients-author boundary

**Sorun:** Bir formül literatürden geliyor ama yazar kendi coefficient'lerini seçmiş (re-parameterization). Bu durum A / B / E arasında belirsiz.

**Kural:**

Bir sabit, **formülü literatür-türevi ama coefficient'leri author re-parameterization** ise, **Category E (ENGINEERING-CHOICE) with PARTIAL verification** olarak işaretlenir. Escalation flag TRUE.

**Decision flow:**

```
Sabit bir formülün parçası mı?
  Evet → Formula literatürde mi yayınlanmış?
    Evet → Coefficient literatürde bit-exact yayınlanmış mı?
      Evet → A (LIT-VERBATIM), web search POSITIVE, HIGH
      Hayır → Coefficient author derivation deterministik mi (closed-form derive)?
        Evet → B (LIT-DERIVED), MEDIUM
        Hayır (author re-parameterization) → E (ENGINEERING-CHOICE) with PARTIAL, escalation
    Hayır → E veya C duruma göre
```

**Pozitif örnek (Agent 4 pilot'tan):**
```python
# Bismarck 1974 critical band saliency formula:
# g(z) = a*z + b
# (form LIT, coefficients author re-parameterized)
A_COEF = 0.066  # author choice, no bit-exact paper value
B_COEF = 0.171  # author choice, no bit-exact paper value
```
→ Her ikisi **E with PARTIAL, escalation TRUE**.

**Anti-pattern:**
```
WRONG: Form LIT → A (LIT-VERBATIM)          # coefficient bit-exact yok
WRONG: Form LIT + author coeff → B (LIT-DERIVED)  # deterministic derivation yok
RIGHT: Form LIT + author re-parameterization → E (ENGINEERING) with PARTIAL
```

**Escalation notu:** Manual review'de iki seçenek:
1. Coefficient'ler alternative source'larda yayınlanıyor mu? (deeper search)
2. Author derivation methodology dokümante edilmişse (örn. `docs/provenance/design_time_dependencies.md`) → B'ye yükseltilebilir; yoksa E kalır.

---

**v1.2 refinements (2026-05-17 post-pilot) integrated:**
- R8: AST walker citation_author column unreliable (hint only, not evidence); independent 3-line locality + web search verification required
- R9: Form-LIT / coefficients-author re-parameterization → E (ENGINEERING-CHOICE) with PARTIAL, NOT B
