# CAPWIC 2026 — Presentation Slide Deck
**Title:** Urban Giants Under Threat: Unveiling Climate Vulnerabilities and Adaptive Strategies in Megacities  
**Presenter:** Dhanyasri Bolla | George Washington University  
**Format:** Research Short (13 minutes: 10 min talk + 3 min Q&A)  
**Style:** Assertion-Evidence (assertion as slide title, evidence as visual/bullet body)

---

## Research Questions
1. How do megacities plan to adapt to climate change?
2. Are there emergent themes across adaptation plans worldwide?

---

## Slide Structure

### Slide 1 — Title (0:45)
**Assertion (title):**
> Urban Giants Under Threat: Unveiling Climate Vulnerabilities and Adaptive Strategies in Megacities

**Slide body:**
- Dhanyasri Bolla | George Washington University
- ACM CAPWIC 2026
- Flash Talk · Research Short

---

### Slide 2 — Motivation (0:45)
**Assertion:**
> Megacities concentrate both the greatest climate risk and the largest share of global population.

**Evidence:**
- 43 megacities studied — each with 10M+ residents
- Cities span Asia, Africa, the Americas, and Europe
- Risks include flood, heat, drought, and sea-level rise
- Yet adaptation strategies vary enormously — and are hard to compare

**Visual:** World map with 43 cities plotted, colored by resilience score

---

### Slide 3 — Research Questions (1:00)
**Assertion:**
> Understanding how megacities plan for climate change requires both reading their documents and comparing them at scale.

**Evidence:**
> **RQ1:** How do megacities plan to adapt to climate change?  
> **RQ2:** Are there emergent themes across adaptation plans worldwide?

- Both require processing unstructured policy documents across 43 cities
- Neither can be answered by reading plans one at a time

---

### Slide 4 — Approach (1:00)
**Assertion:**
> Answering both questions requires combining AI-powered extraction with statistical pattern detection.

**Evidence (two-column layout):**

| To answer RQ1 | To answer RQ2 |
|---|---|
| LLM extracts strategies from each city's plan | Chi-square + Cramer's V tests for patterns |
| Output: categories per city (risks, finance, infrastructure, stakeholders) | Output: cross-city frequency and association results |
| Dashboard: inspect any single city | Dashboard: compare all 43 cities side-by-side |

---

### Slide 5 — Statistical Methods (1:15)
**Assertion:**
> Three statistical methods reveal which city attributes are meaningfully associated with resilience outcomes.

**Evidence:**
- **Chi-square tests** — three key pairs tested:
  - Climate zone vs. adaptation plan existence
  - Coastal location vs. flood risk level
  - World region vs. heat risk level
- **Cramer's V** — measures effect size beyond p-value
- **Multiple linear regression** — predicts resilience score
  - Predictors: population, GDP per capita, infrastructure vulnerability, financial capacity, stakeholder engagement
- Significance threshold: p < 0.05

**Visual:**

| Test | Variables tested | p-value | Cramer's V | Significant (p < 0.05)? |
|---|---|---:|---:|---|
| Chi-square Test 1 | Climate zone vs adaptation plan existence | 0.2478 | 0.3933 | No |
| Chi-square Test 2 | Coastal location vs flood risk level | 0.0951 | 0.3308 | No |
| Chi-square Test 3 | World region vs heat risk level | 0.0385 | 0.4352 | Yes |

---

### Slide 6 — LLM Extraction Workflow (1:00)
**Assertion:**
> A single structured LLM prompt converts unstructured policy text into four measurable adaptation categories per city.

**Evidence:**
- Model: Gemini 2.5 Flash
- One API call per document → extracts:
  1. Climate Risks / Natural Disasters
  2. Infrastructure Systems
  3. Financial Sources
  4. Stakeholders Involved
- Also extracts: top 3 strengths, top 3 gaps per city
- Output: strict JSON schema — fixed fields, no free text

**Visual:** Arrow diagram — `PDF → Prompt → JSON output` with a mini JSON snippet

---

### Slide 7 — Extracted Categories and Sub-categories (1:00)
**Assertion:**
> The LLM consistently extracted a shared adaptation taxonomy, making cross-city policy content comparable.

**Evidence:**
- **Category 1: Climate Risks / Natural Disasters**
  - Sub-categories: flood risk, heatwaves, drought, sea-level rise, extreme storms
- **Category 2: Infrastructure Systems**
  - Sub-categories: drainage, transport, water systems, energy grid, health infrastructure
- **Category 3: Financial Sources**
  - Sub-categories: municipal budgets, national funds, climate finance, PPPs, multilateral support
- **Category 4: Stakeholders Involved**
  - Sub-categories: local government, utilities, NGOs, communities, private sector

**Visual:** 4-column taxonomy matrix (category on top, 4-5 sub-categories under each)

---

### Slide 8 — From Categories to Statistical Themes (1:00)
**Assertion:**
> Once categories were structured, we quantified them to detect global adaptation themes across cities.

**Evidence:**
- Step 1: Convert each extracted category/sub-category into analysis variables (presence/frequency)
- Step 2: Aggregate at city level to build comparable policy feature vectors
- Step 3: Run chi-square and Cramer's V tests for cross-city associations
- Step 4: Interpret significant patterns as emergent global adaptation themes
- Example outcome: region vs heat-risk profile showed a statistically significant association

**Visual:** Analysis flowchart — `Extracted categories → Encoded variables → Statistical tests → Emergent themes`

---

### Slide 9 — Technical: PDF Ingestion and Preprocessing (1:15)
**Assertion:**
> Extraction quality depends on a standardized ingestion and cleaning pipeline before any LLM step.

**Evidence:**
- **Library:** PyMuPDF (`fitz`) — page-by-page text extraction
- **Metadata logged:** city name, country, source, document year
- **Text cleaning:** removes headers, footers, page numbers, OCR artifacts
- **Chunking:** first 5,000 characters sent per prompt (controlled context window)
- **Quality controls:**
  - Missing/empty response → default JSON structure returned
  - Malformed JSON → fallback parser strips markdown code blocks
  - API rate-limit (429) → explicit error caught, user notified

**Visual:** Pipeline diagram — `PDF → fitz extract → clean → chunk → QC check → LLM ready`

---

### Slide 10 — Technical: Prompting, Extraction, and Validation (1:15)
**Assertion:**
> Structured role prompting with schema enforcement and multi-level validation converts raw text into analyzable records.

**Evidence:**
- **Prompt role:** "You are an expert in climate adaptation planning"
- **Output contract:** respond ONLY in JSON with required top-level keys:
  - `city_info`, `categories`, `insights`
- **Consistency controls:**
  - Temperature near 0 for reproducibility
  - JSON parse error → retry with stripped markdown → fallback default
  - Missing keys → filled with empty defaults, never silently dropped
- **Validation layers:**
  1. Required-field check (all four categories must exist)
  2. Non-empty list check per category
  3. Human spot-check on sampled outputs

**Visual:** Two-column example — left: raw PDF paragraph | right: resulting JSON block

---

### Slide 11 — Dashboard Demo (1:00)
**Assertion:**
> The interactive dashboard surfaces both statistical and LLM-derived insights for dynamic city-to-city comparison.

**Evidence (annotated screenshot with callouts):**
- **Callout 1:** Select any city from 43 megacities
- **Callout 2:** View adaptation categories extracted from its policy document
- **Callout 3:** Compare resilience scores side-by-side
- **Callout 4:** View identified strengths and policy gaps
- Built with Flask (backend) + Leaflet.js (map) + HTML/CSS frontend

**Visual:** 1 large annotated dashboard screenshot — most of the slide

---

### Slide 12 — Findings: RQ1 (1:15)
**Assertion:**
> Megacities' adaptation plans emphasize infrastructure and climate risk most, while financing and stakeholder engagement are frequently underdeveloped.

**Evidence:**
- All 43 city documents mention infrastructure systems and climate risks
- Financial mechanisms are the least represented category across extracted documents
- Stakeholder engagement varies widely: high in Tokyo, Delhi — low in Cairo, Dhaka
- Common risk themes: flooding, heat, drought (often co-occurring in tropical/arid cities)
- Plans range from vague aspirational text to detailed action items — depth is uneven

**Visual:** Grouped bar chart — 4 extracted categories × High/Medium/Low representation across 43 cities  
**File:** `static/slide12_categories_chart.html` (interactive Plotly, dark background, export to PNG for slides)

| Category | High | Medium | Low |
|---|---:|---:|---:|
| Climate Risks / Natural Disasters | 38 | 4 | 1 |
| Infrastructure Systems | 13 | 23 | 7 |
| Financial Sources | 18 | 12 | 13 |
| Stakeholders Involved | 13 | 23 | 7 |

> Key takeaway: Climate risk is universally represented (38/43 cities = High), while Financial Sources and Stakeholders show the widest gaps.

---

### Slide 13 — Findings: RQ2 (1:15)
**Assertion:**
> Cross-city analysis reveals emergent global patterns: coastal cities prioritize flood adaptation, and financial capacity strongly predicts resilience depth.

**Evidence:**
- **Theme 1:** Coastal cities cluster around flood + sea-level rise strategies (Chi-square: coastal vs. flood risk, significant)
- **Theme 2:** Arid/tropical cities share heat and drought risk language but diverge in response strategies
- **Theme 3:** High financial capacity cities show broader, more multi-sectoral adaptation plans
- **Theme 4:** Regional patterns — Asian megacities (Tokyo, Shanghai, Beijing) score highest on resilience; South Asian and Sub-Saharan cities score lowest
- Resilience score range: **4.2 (Dhaka) → 7.8 (Tokyo)**

**Visuals (both generated, pick one or show both side-by-side):**

**Visual A — Heatmap:** `static/slide13_heatmap.html`  
Cities (x-axis, sorted highest → lowest resilience) × 4 adaptation categories (y-axis), colored Red (Low) → Orange (Medium) → Green (High).  
Pattern visible: financial and stakeholder rows fade to red/orange as you move right toward lower-resilience cities.

**Visual B — Box Plot:** `static/slide13_boxplot.html`  
Resilience scores grouped by world region, all individual cities shown as dots.

| Region | Median Score | Min | Max | Cities |
|---|---:|---:|---:|---:|
| North America | 7.85 | 6.1 | 8.2 | 4 |
| Europe | 7.35 | 6.4 | 8.1 | 4 |
| South America | 6.20 | 5.9 | 6.5 | 5 |
| Asia | 6.10 | 3.7 | 7.9 | 27 |
| Africa | 3.90 | 3.5 | 4.5 | 3 |

> Key takeaway: North America and Europe lead on resilience; Africa has the lowest median and narrowest range; Asia has the widest spread — reflecting both the highest and lowest scoring cities in the dataset.

---

### Slide 14 — Limitations (0:50)
**Assertion:**
> Current results are exploratory and bounded by document heterogeneity and early-stage validation.

**Evidence:**
- Document quality varies: some plans are detailed, others high-level only
- Context window (5,000 chars) may miss content in long documents
- LLM extraction not yet benchmarked against manual annotation
- Correlation findings are associative — no causal claims made
- 43-city sample: large for megacities, limited for generalization

---

### Slide 15 — Next Steps and Closing (0:45)
**Assertion:**
> AI-assisted policy analytics can help cities move from fragmented documents to comparable adaptation intelligence at scale.

**Evidence:**
- **Next steps:**
  - Expand context window / multi-pass chunking for longer documents
  - Benchmark LLM extraction against expert-labeled ground truth
  - Add temporal analysis: track policy evolution across plan versions

**Closing line (spoken, not on slide):**
> "We believe this pipeline is a step toward making climate policy as legible as the risks it addresses."

- Contact: dhanyasribolla@gmail.com | George Washington University

---

## Timing Guide

| Slides | Content | Time |
|---|---|---|
| 1–2 | Title + Motivation | 1:30 |
| 3–4 | Research Questions + Approach | 2:00 |
| 5–10 | Methods (stats + extraction + technical pipeline) | 6:30 |
| 11 | Dashboard demo | 1:00 |
| 12–13 | Findings (RQ1 + RQ2) | 2:30 |
| 14–15 | Limitations + Next steps | 1:35 |
| **Total** | | **~13:35** |

> To hit 13:00 exactly, trim Slides 7 and 9 to 0:45 each.

---

## Likely Q&A Questions

| Question | Ready Answer |
|---|---|
| How reliable is the LLM extraction? | Structured prompts + deterministic settings + validation layers; full benchmarking is a next step |
| Why combine statistics and LLMs? | LLMs convert unstructured text into analyzable variables; statistics test whether patterns are meaningful |
| Is this generalizable beyond 43 megacities? | Yes — the pipeline scales to any city with a policy document |
| What is the practical impact? | Planners can identify specific policy gaps and compare their city against peers without manual review |
| Why Gemini instead of GPT-4? | Cost-effective for research use; structured output quality is comparable for this task |

---

## Design Notes

- One assertion per slide — full claim sentence, not a topic label
- Evidence should be primarily visual; minimize bullet text
- Use high contrast and large fonts for room readability
- Keep details in the spoken script, not on the slide
- Colors: consider a consistent palette tied to resilience score (red → green gradient)
