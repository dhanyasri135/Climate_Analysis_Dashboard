# Climate Adaptation Project: Technical Work (A to Z)

## 1) What this system is

This project is a full-stack research application that combines:

- LLM-based extraction from adaptation policy documents
- Quantitative statistical analysis over a 43-city dataset
- OSM (OpenStreetMap) gap analysis for climate-resilience infrastructure
- Interactive dashboards and API endpoints for exploration

Core objective: convert unstructured climate adaptation documents and structured city-level indicators into analyzable, comparable insights.

---

## 2) End-to-end architecture

### Backend

- Framework: Flask (`app.py`)
- LLM integration: Google Gemini via `google-genai` (`extract_and_prompt.py`)
- Document ingestion: PyMuPDF (`fitz`) for PDF text extraction
- Statistical engine: pandas, numpy, scipy, scikit-learn (`statistical_analysis.py`)
- Visualization generation: Plotly JSON specs (`visualizations.py`, `osm_visualizations.py`)
- OSM scoring/report logic: (`osm_gap_analysis.py`)

### Frontend

- Templating: Jinja2 HTML templates in `templates/`
- UI framework: Bootstrap 5
- Charts: Plotly.js rendered client-side from server-generated JSON
- Mapping: Leaflet + OSM tiles + Nominatim geocoding (`static/map.js`)

### Data

- `data/megacities_dataset.csv`: city resilience/climate variables
- `data/osm_coverage_dataset.csv`: per-city OSM coverage indicators and priority metadata

---

## 3) High-level workflow

### A. Document upload and analysis workflow

1. User uploads 1+ files through `/`.
2. Flask stores each file in `uploads/` with UUID-prefixed filename.
3. For each file, `analyze_document_complete(filepath)` is executed.
4. Function extracts text using PyMuPDF.
5. One Gemini request asks for a strict JSON response with:
   - `city_info`
   - `categories`
   - `insights`
6. Response text is JSON-parsed (including markdown code-block cleanup fallback).
7. Results are rendered:
   - 1 file -> `index.html`
   - multiple files -> `compare.html`
8. City profile and extracted categories/insights are displayed.
9. City map is geocoded in browser and plotted in Leaflet.

### B. Statistical dashboard workflow

1. User opens `/statistics`.
2. Backend runs `run_full_analysis()` on `megacities_dataset.csv`.
3. Statistical outputs are assembled:
   - summary stats
   - correlation analysis
   - regression analysis
   - categorical tests (chi-square + Cramer's V)
   - resilience factors aggregation
4. Plotly charts are generated server-side as JSON strings.
5. `statistics.html` renders cards, charts, and test summaries.

### C. Interactive custom analytics workflow

1. User opens `/dashboard` and selects variables + analysis type.
2. Frontend posts to `/api/dashboard/analyze` with:
   - `variables`
   - `analysis_type`
3. Backend dispatches to one of:
   - `custom_correlation_analysis`
   - `custom_chi_square_analysis`
   - `custom_regression_analysis`
   - `custom_association_rules`
   - `custom_odds_ratio_analysis`
4. JSON response is rendered in dynamic tables with interpretation text.

### D. Research terminal workflow

1. User submits question to `/api/research/ask`.
2. Backend loads dataframe and includes a head(5) string as dataset context.
3. Gemini prompt is composed with climate adaptation expert role.
4. LLM returns a concise answer (2-4 paragraphs target in prompt).
5. Chat UI appends assistant response.

### E. OSM gap analysis workflow

1. User opens `/osm-gaps`.
2. Dataset loaded from `osm_coverage_dataset.csv`.
3. Gap severity computed: `100 - osm_coverage_score`.
4. Global report generated:
   - global stats
   - priority wishlist categories
   - feature coverage summary
   - priority cities
   - regional analysis
   - key findings and call-to-action
5. Plotly visualizations generated and rendered in tabs.
6. Methodology details available at `/osm-methodology`.

---

## 4) Flask route-by-route technical behavior (`app.py`)

- `GET/POST /`
  - GET: render empty upload page.
  - POST: iterate uploaded files, save, run LLM analysis, aggregate results.
  - If >1 result, render compare view.

- `GET /statistics`
  - Runs complete statistics pipeline + chart generation.
  - Renders dashboard or error message.

- `GET /api/statistics`
  - Returns raw analysis JSON.

- `GET /dashboard`
  - Serves custom analytics UI.

- `POST /api/dashboard/analyze`
  - Validates at least 2 variables.
  - Switches on analysis type and returns JSON output.

- `GET /research`
  - Serves research chat UI.

- `POST /api/research/ask`
  - Validates non-empty question.
  - Calls LLM with optional dataset context.

- `GET /osm-gaps`
  - Loads OSM dataset, computes severity, builds report, builds charts.

- `GET /api/osm-gaps/city/<city_name>`
  - Returns city-specific gap details or 404.

- `GET /osm-methodology`
  - Serves methodology page.

---

## 5) LLM implementation details (`extract_and_prompt.py`)

## 5.1 API client and environment

- Loads `.env` via `load_dotenv()`.
- Creates Gemini client:
  - `client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))`
- Uses model: `gemini-2.5-flash`.

## 5.2 PDF extraction

`extract_text(file_path)`:

- Opens doc via `fitz.open(file_path)`.
- Extracts each page text via `page.get_text()`.
- Joins pages with newline.

## 5.3 Unified extraction function

`analyze_document_complete(filepath)` is the optimized main path.

Prompt contract requests exactly this JSON structure:

```json
{
  "city_info": {
    "city": "...",
    "country": "...",
    "climate_zone": "...",
    "population": "..."
  },
  "categories": {
    "Climate Risks / Natural Disasters": [],
    "Infrastructure Systems": [],
    "Financial Sources supporting adaptation planning": [],
    "Stakeholders involved": []
  },
  "insights": {
    "strengths": [],
    "gaps": []
  }
}
```

Context sent to model is truncated to first ~5000 chars for this call.

## 5.4 JSON parser robustness

`parse_json_response(response_text)` handles common LLM formatting issues:

- empty/blank response -> `{}`
- strips leading ```json and trailing ``` markers
- attempts `json.loads`
- on parse error, logs debug and returns `{}`

## 5.5 Error handling strategy

- Explicit handling for Gemini client errors
- Rate limit detection by checking `429` / `RESOURCE_EXHAUSTED` in exception text
- Returns user-friendly fallback payloads that preserve response schema
- Any unexpected exception returns safe default error structure

This prevents frontend breakage from malformed or missing response fields.

## 5.6 Additional LLM functions

- `process_document(filepath)` (legacy segmented categorization)
- `extract_city_info(filepath)` (legacy city metadata extraction)
- `get_llm_insights(filepath)` (legacy strengths/gaps)
- `answer_research_question(question, dataset_context)` for chat mode

Main app path currently uses the unified `analyze_document_complete` for upload processing.

## 5.7 Exact prompt used for document analysis (`analyze_document_complete`)

The application sends this exact prompt template (verbatim from code):

```text
You are an expert in climate adaptation planning. Analyze the following city adaptation document and provide a comprehensive analysis.

Respond ONLY in JSON format with ALL of the following sections:

{
  "city_info": {
    "city": "city name",
    "country": "country name",
    "climate_zone": "climate zone if mentioned",
    "population": "population if mentioned"
  },
  "categories": {
    "Climate Risks / Natural Disasters": ["list of identified risks and disasters"],
    "Infrastructure Systems": ["list of infrastructure systems mentioned"],
    "Financial Sources supporting adaptation planning": ["list of financial sources"],
    "Stakeholders involved": ["list of stakeholders"]
  },
  "insights": {
    "strengths": ["top 3 strengths of the adaptation strategy"],
    "gaps": ["top 3 weaknesses or missing elements"]
  }
}

Document:
{text[:5000]}
```

Notes:

- Model used: `gemini-2.5-flash`
- Input truncation: first 5000 characters of extracted document text
- Parser strips markdown fences (```json ... ```) before JSON decode

## 5.8 Exact outputs for document analysis

### 5.8.1 Normal successful output shape

```json
{
  "city_info": {
    "city": "...",
    "country": "...",
    "climate_zone": "...",
    "population": "..."
  },
  "categories": {
    "Climate Risks / Natural Disasters": ["..."],
    "Infrastructure Systems": ["..."],
    "Financial Sources supporting adaptation planning": ["..."],
    "Stakeholders involved": ["..."]
  },
  "insights": {
    "strengths": ["..."],
    "gaps": ["..."]
  }
}
```

### 5.8.2 Fallback output when parse/structure is invalid

If parsed result is empty or missing `city_info`, code returns:

```json
{
  "city_info": {
    "city": "Unknown",
    "country": "Unknown",
    "climate_zone": "N/A",
    "population": "N/A"
  },
  "categories": {},
  "insights": {
    "strengths": [],
    "gaps": []
  }
}
```

### 5.8.3 Exact output on API rate limit (429 / RESOURCE_EXHAUSTED)

```json
{
  "city_info": {
    "city": "Unknown",
    "country": "Unknown",
    "climate_zone": "API rate limit exceeded",
    "population": "N/A"
  },
  "categories": {
    "error": "API rate limit exceeded. You've reached the free tier limit of 20 requests per day."
  },
  "insights": {
    "strengths": ["API rate limit exceeded"],
    "gaps": ["Please wait or upgrade your Gemini API plan"]
  }
}
```

### 5.8.4 Exact output on non-rate API error

```json
{
  "city_info": {
    "city": "Unknown",
    "country": "Unknown",
    "climate_zone": "API error",
    "population": "N/A"
  },
  "categories": {
    "error": "API error: <first 100 chars of exception>"
  },
  "insights": {
    "strengths": ["API error"],
    "gaps": ["<first 100 chars of exception>"]
  }
}
```

### 5.8.5 Exact output on unexpected exception

```json
{
  "city_info": {
    "city": "Unknown",
    "country": "Unknown",
    "climate_zone": "Error",
    "population": "N/A"
  },
  "categories": {
    "error": "Unexpected error: <first 100 chars of exception>"
  },
  "insights": {
    "strengths": ["Error occurred"],
    "gaps": ["<first 100 chars of exception>"]
  }
}
```

## 5.9 Exact prompt and outputs for Research Terminal (`answer_research_question`)

Prompt template used:

```text
You are an expert AI assistant specializing in climate adaptation, urban resilience, and sustainability.
Your role is to provide accurate, well-informed answers about:
- Climate risks and natural disasters
- Urban adaptation strategies
- Resilience frameworks and methodologies
- Climate finance and funding mechanisms
- Infrastructure systems and green infrastructure
- Stakeholder engagement
- Climate science and policy

{context_info}

User Question: {question}

Provide a clear, informative answer. If the question relates to the dataset, include specific examples or statistics when relevant.
Keep your response concise but comprehensive (2-4 paragraphs).
```

Where `context_info` is conditionally injected as:

```text
Context: You have access to a dataset of 43 global megacities with the following information:
- Cities from various climate zones (Tropical, Temperate, Arid, Continental)
- Climate resilience scores and adaptation plan status
- Population, GDP, and infrastructure quality metrics
- Stakeholder engagement levels
- Climate risks and mitigation strategies

Dataset sample:
{dataset_context[:1000]}
```

Research terminal outputs:

- Success: plain text answer (`response.text.strip()`)
- Rate limit: `⚠️ API rate limit exceeded. You've reached the free tier limit of 20 requests per day. Please wait or upgrade your Gemini API plan.`
- API error: `⚠️ API error: <first 200 chars>`
- Unexpected error: `⚠️ An error occurred: <first 200 chars>`

---

## 6) Statistical engine details (`statistical_analysis.py`)

## 6.1 Dataset loading

- File: `data/megacities_dataset.csv`
- `load_dataset()` returns dataframe.

Primary columns include:

- `population_millions`, `gdp_per_capita`, `resilience_score`
- `climate_zone`, `region`, `coastal`
- risk levels: `flood_risk`, `heat_risk`, `drought_risk`, `sea_level_rise_risk`
- governance/capacity labels: `adaptation_plan_exists`, `infrastructure_vulnerability`, `financial_capacity`, `stakeholder_engagement`

## 6.2 Summary statistics

`get_summary_statistics(df)` computes counts and means:

- total cities
- cities with/without adaptation plans
- average resilience score
- average population
- count coastal cities
- count high flood risk / high heat risk

## 6.3 Chi-square and Cramer's V

### Chi-square

`chi_square_test(df, var1, var2)`:

1. Contingency table via `pd.crosstab`.
2. `chi2_contingency(contingency_table)` -> chi2, p-value, dof, expected.
3. Significance threshold: `p < 0.05`.

### Cramer's V

`cramers_v(confusion_matrix)`:

\[
V = \sqrt{\frac{\chi^2}{n \cdot (\min(r,c)-1)}}
\]

where:

- \(\chi^2\): chi-square statistic
- \(n\): sample size
- \(r,c\): contingency matrix dimensions

`categorical_analysis(df)` runs three predefined tests:

- climate zone vs adaptation plan existence
- coastal vs flood risk
- region vs heat risk

## 6.4 Correlation analysis

`correlation_analysis(df, variables=None)`:

- Uses numeric columns (unless explicit variable list provided)
- Computes Pearson correlation matrix via `df.corr()`
- Flags "significant correlations" as absolute r > 0.5
- Labels strength:
  - Strong if |r| > 0.7
  - Moderate otherwise (for thresholded set)

## 6.5 Regression analysis (global)

`regression_analysis(df, target_var='resilience_score', predictor_vars=None)`:

Default predictors:

- `population_millions`
- `gdp_per_capita`

Additional categorical proxies are ordinally encoded if columns exist:

- `infrastructure_vulnerability`: Low/Medium/High -> 1/2/3
- `financial_capacity`: Low/Medium/High -> 1/2/3
- `stakeholder_engagement`: Low/Medium/High -> 1/2/3

Pipeline:

1. Assemble X and y
2. Fill missing values by column mean
3. Fit sklearn `LinearRegression`
4. Compute R^2 from `model.score(X,y)`
5. Extract coefficients and sign-based impact label
6. Sort coefficients by absolute magnitude

Model quality labels:

- Good if R^2 > 0.7
- Moderate if R^2 > 0.5
- Weak otherwise

## 6.6 Full pipeline orchestrator

`run_full_analysis()` returns a dict with:

- `summary_stats`
- `correlation_analysis`
- `regression_analysis`
- `categorical_analysis`
- `resilience_factors`

## 6.7 Resilience factors aggregation

`resilience_factors_analysis(df)` computes:

- mean resilience for cities with adaptation plan vs without
- regional mean/std/count of resilience
- climate-zone mean/std/count of resilience

## 6.8 Custom dashboard analyses

### 6.8.1 Variable preparation layer

`prepare_variables_for_analysis(df, variables)` creates analysis-ready columns.

Important implementation detail:

- Many dashboard variable IDs are mapped as **proxy/binary transformations** from existing columns.
- Example: `CR_SLR` maps to `sea_level_rise_risk == 'High'`.
- Example: many infrastructure/finance/stakeholder variables map from vulnerability/capacity engagement categories.

Fallback behavior:

- If mapping function errors, code creates random binary variable via `np.random.randint(0, 2, size=len(df))`.
- If variable unknown and not a dataframe column, same random fallback is used.

This is practical for avoiding crashes but introduces stochastic synthetic variables; results for fallback variables are not scientifically interpretable.

### 6.8.2 Custom correlation

`custom_correlation_analysis(variables)`:

- pairwise Pearson r for selected variables
- skips NaN correlations
- returns list of pair objects

### 6.8.3 Custom chi-square

`custom_chi_square_analysis(variables)`:

- builds pairwise crosstabs
- runs chi-square + Cramer's V
- sanitizes NaN values for JSON serialization
- marks significance by p < 0.05

### 6.8.4 Custom regression

`custom_regression_analysis(variables)`:

- first selected variable = dependent variable
- remaining variables = predictors
- removes rows with missing in any selected variable
- computes:
  - R^2
  - RMSE
  - intercept
  - coefficient list with magnitude and sign
- quality labels:
  - Excellent > 0.8
  - Good > 0.6
  - Moderate > 0.4
  - Weak otherwise

### 6.8.5 Association rules

`custom_association_rules(variables, min_support=0.3, min_confidence=0.6)`:

- converts selected variables to boolean
- evaluates pairwise implication-style rules A -> B
- metrics:
  - support = P(A and B)
  - confidence = P(B | A)
  - lift = confidence / P(B)
- returns top 20 by confidence

### 6.8.6 Odds ratio analysis

`custom_odds_ratio_analysis(variables)`:

- evaluates all variable pairs with 2x2 contingency tables
- cell notation:
  - a = both present
  - b = var1 present, var2 absent
  - c = var1 absent, var2 present
  - d = both absent
- odds ratio:

\[
OR = \frac{a\cdot d}{b\cdot c}
\]

- if zero cells in b or c, applies continuity correction (+0.5 to all cells)
- computes log-scale 95% CI:

\[
\log(OR) \pm 1.96\cdot SE,\quad SE = \sqrt{1/a+1/b+1/c+1/d}
\]

- runs chi-square p-value for significance
- maps OR magnitude to interpretation buckets

---

## 7) Statistical visualization system (`visualizations.py`)

Generated charts (Plotly JSON):

1. Correlation heatmap (RdBu diverging scale, centered at 0)
2. Regression coefficient horizontal bars (green/red by sign)
3. Resilience distribution histogram (manual bins)
4. Regional average resilience bar chart
5. High-risk counts across risk types bar chart
6. Adaptation plan impact bar comparison
7. GDP vs resilience scatter (bubble size by population, color by region)

All chart builders return serialized JSON using PlotlyJSONEncoder.

---

## 8) OSM gap analysis computation (`osm_gap_analysis.py`)

## 8.1 Dataset and features

Source file: `data/osm_coverage_dataset.csv`

Primary columns:

- `osm_coverage_score` (0-100)
- 7 feature-level coverage columns (High/Medium/Low):
  - `drainage_mapped`
  - `green_infrastructure`
  - `cooling_centers`
  - `evacuation_routes`
  - `emergency_shelters`
  - `flood_barriers`
  - `permeable_surfaces`
- critical gap strings (`critical_gap_1..3`)
- `priority_level` (High/Medium/Low)

## 8.2 Gap severity formula

`calculate_gap_severity(df)`:

\[
\text{gap_severity} = 100 - \text{osm_coverage_score}
\]

Category thresholds:

- Critical: >= 70
- Severe: >= 50
- Moderate: >= 30
- Minor: < 30

## 8.3 Global summary metrics

`get_global_statistics(df)` computes:

- number of cities
- average coverage
- count with critical gaps (<40 coverage)
- count with good coverage (>=70)
- min/max coverage city names
- percentage of cities with High level in selected features

## 8.4 Feature coverage summary

`get_feature_coverage_summary(df)` counts High/Medium/Low for each of 7 features and computes:

\[
\text{coverage_percentage} = \frac{\#\text{High}}{\#\text{Cities}} \times 100
\]

## 8.5 Priority city selection

`get_priority_cities(df, limit=10)`:

- computes severity
- selects `nlargest(limit, 'gap_severity')`
- returns city/country/score/severity/priority/gap text fields

## 8.6 Regional analysis

`get_regional_analysis(df)`:

- maps country names to regions using hard-coded dictionary
- groups by region to compute mean coverage and city count
- sorts descending by avg coverage

## 8.7 Comprehensive report object

`generate_gap_analysis_report()` combines:

- titles/subtitle
- global stats
- prioritized wishlist categories (12 features total)
- feature coverage summary
- top 15 priority cities
- regional analysis
- key findings statements
- call-to-action statements

## 8.8 City-specific API payload

`get_city_specific_gaps(city_name)` returns per-city JSON with:

- score + priority
- top 3 critical gaps
- feature coverage dictionary

---

## 9) OSM visualization system (`osm_visualizations.py`)

Charts generated:

1. Gap severity ranking bar chart (top 20)
2. Feature coverage heatmap (top 25 severity cities)
3. Priority distribution donut pie chart
4. Regional coverage bar chart
5. Global feature summary stacked horizontal bars
6. Coverage vs gap scatter by priority level

Encoding details:

- Feature heatmap maps High/Medium/Low -> 3/2/1
- Priority colors:
  - High = red
  - Medium = yellow
  - Low = green

Note: `create_coverage_score_map()` exists but is not used in final chart bundle; it currently uses placeholder lat/lon arrays of zeros.

---

## 10) Frontend behavior and integration

## 10.1 Document analysis UI (`templates/index.html`)

- Multi-file upload form with file type restrictions
- API usage notice for Gemini free-tier limits
- On result:
  - city profile section
  - category cards
  - strengths and gaps panel
  - Leaflet map seeded via `setMap("city, country")`

## 10.2 Compare UI (`templates/compare.html`)

- Two-column card layout for multiple uploads
- City metadata + extracted categories + strengths/gaps
- Shared Leaflet map with multiple markers via `setMultipleMarkers(cities)`

## 10.3 Statistical UI (`templates/statistics.html`)

- Summary cards
- Tabbed views:
  - Overview
  - Regression
  - Correlations
  - Chi-square
  - Definitions
- Charts instantiated from server-provided Plotly JSON

## 10.4 Interactive analytics UI (`templates/dashboard.html`)

- Checkbox catalog of domain variables
- selected variable badge UX
- analysis-type radio selector
- API call to `/api/dashboard/analyze`
- dynamic result table rendering per method with interpretation blocks

## 10.5 Research terminal (`templates/research.html`)

- Chat-like UI with async submit
- loading indicator
- predefined example question buttons
- calls `/api/research/ask`

## 10.6 OSM dashboards (`templates/osm_gaps.html`, `templates/osm_methodology.html`)

- OSM insights tabs and chart zones
- methodology page documents scoring framework, thresholds, and rationale

## 10.7 Mapping JS (`static/map.js`)

- Initializes Leaflet map + OSM tile layer
- geocoding uses Nominatim search endpoint in browser
- `setMap()` sets single city marker and zoom
- `setMultipleMarkers()` geocodes each location and places markers

---

## 11) Data model details

## 11.1 Megacities dataset schema (`data/megacities_dataset.csv`)

Each row is a megacity with:

- location/admin: `city`, `country`, `region`
- scale/economy: `population_millions`, `gdp_per_capita`
- climate context: `climate_zone`, `coastal`
- hazards: flood/heat/drought/sea-level risk (Low/Medium/High)
- policy capacity indicators:
  - `adaptation_plan_exists` (Yes/No)
  - `infrastructure_vulnerability` (Low/Medium/High)
  - `financial_capacity` (Low/Medium/High)
  - `stakeholder_engagement` (Low/Medium/High)
- target output: `resilience_score`

## 11.2 OSM coverage dataset schema (`data/osm_coverage_dataset.csv`)

Each row includes:

- city/country
- aggregate `osm_coverage_score`
- seven feature coverage labels (High/Medium/Low)
- textual top-3 critical gaps
- priority level

## 11.3 How `megacities_dataset.csv` was created

This section is the dataset-construction narrative used for technical reporting.

Implementation status in this repository:

- The app loads `data/megacities_dataset.csv` directly as a canonical input table.
- There is no raw-to-final build script checked into the repo right now.
- The creation process is therefore documented as a curation workflow.

### Creation workflow (curation pipeline)

1. Define city scope
  - Include global megacities (10M+ scale) across regions.
  - Final table contains 43 city records.

2. Build the base city table
  - Core identifiers: `city`, `country`, `region`.
  - Standardize names to one canonical spelling per city.

3. Add quantitative baseline variables
  - `population_millions`
  - `gdp_per_capita`
  - `resilience_score`

4. Add climate/geographic context
  - `climate_zone`
  - `coastal` (Yes/No)

5. Add climate risk indicators
  - `flood_risk`
  - `heat_risk`
  - `drought_risk`
  - `sea_level_rise_risk`
  - Risk labels encoded as ordinal categories: `Low`, `Medium`, `High`.

6. Add policy/capacity indicators
  - `adaptation_plan_exists` (Yes/No)
  - `infrastructure_vulnerability` (Low/Medium/High)
  - `financial_capacity` (Low/Medium/High)
  - `stakeholder_engagement` (Low/Medium/High)

7. Final QA and release
  - Validate row count and column completeness.
  - Validate category domains (only allowed values).
  - Save as `data/megacities_dataset.csv` for downstream analysis.

### Encodings used in the file

- Binary categories:
  - `coastal`: `Yes` or `No`
  - `adaptation_plan_exists`: `Yes` or `No`
- Ordinal categories:
  - Risk and capacity dimensions use `Low`, `Medium`, `High`.
- Numeric fields:
  - `population_millions`, `gdp_per_capita`, `resilience_score`

### QA profile of the released dataset (current file)

- Total rows: 43
- Regions: Africa 3, Asia 27, Europe 4, North America 4, South America 5
- Climate zones: Tropical 15, Temperate 9, Subtropical 8, Arid 6, Continental 4, Mediterranean 1
- Adaptation plan coverage: Yes 39, No 4
- Coastal split: Yes 18, No 25

Numeric ranges:

- `population_millions`: min 8.2, max 37.4, mean 14.66
- `gdp_per_capita`: min 580, max 75419, mean 19525.3
- `resilience_score`: min 3.5, max 8.2, mean 6.23

Category distributions (examples):

- `flood_risk`: High 14, Medium 20, Low 9
- `heat_risk`: High 33, Medium 9, Low 1
- `drought_risk`: High 11, Medium 9, Low 23
- `sea_level_rise_risk`: High 10, Medium 7, Low 26
- `infrastructure_vulnerability`: High 13, Medium 23, Low 7
- `financial_capacity`: High 18, Medium 12, Low 13
- `stakeholder_engagement`: High 13, Medium 23, Low 7

### Reproducibility note

Current reproducibility is strong for **analysis** (same CSV -> same results),
but partial for **construction** (raw-source ingest code not yet committed).

To fully operationalize dataset rebuilds, add a `scripts/build_megacities_dataset.py`
pipeline plus a provenance file with source URLs, access dates, and transformation rules.

---

## 12) Error handling and reliability design

### LLM layer

- Catches rate-limit errors explicitly
- Catches generic API errors and unexpected exceptions
- Always returns JSON-compatible fallback structures

### Dashboard APIs

- Validate minimum variable count for custom analyses
- return 400 for bad input, 500 for unexpected failures

### Statistical functions

- NaN sanitation in chi-square/correlation custom paths
- try/except around pairwise calculations to skip invalid pairs

### Mapping

- geocode failures logged to console; app remains functional

---

## 13) Scientific/computational assumptions and caveats

1. Correlation threshold for "significant_correlations" is heuristic (|r| > 0.5), not inferential significance testing.
2. Regression is fit and scored on same data split (no train/test split), so R^2 is in-sample.
3. Several custom dashboard variables are proxies mapped from broader indicators.
4. Fallback random binary generation for unmapped variables can produce non-reproducible/non-interpretable associations.
5. LLM extraction uses truncated text windows (up to ~5000 chars) and may omit content beyond truncation.
6. LLM outputs rely on prompt compliance and parser robustness; defaults prevent crashes but can hide extraction quality variation.
7. OSM analysis uses precomputed coverage scores from dataset; code does not live-query OSM in runtime.

---

## 14) Dependencies and why they were incorporated (`requirements.txt`)

- Flask: web server and routing
- google-genai: Gemini model access
- python-dotenv: environment variable management for API key
- PyMuPDF: robust PDF text extraction
- geopy: imported for geospatial utility support (not core in current runtime path)
- pandas/numpy: core data processing
- scipy: chi-square statistics
- scikit-learn: linear regression model
- matplotlib/seaborn: included but current dashboard uses Plotly
- plotly: interactive chart generation/serialization

---

## 15) Practical API contracts

### Upload processing return structure used by templates

```json
{
  "filename": "uploaded_file_name",
  "categories": {"...": []},
  "city_info": {"city": "...", "country": "...", "climate_zone": "...", "population": "..."},
  "insights": {"strengths": [], "gaps": []}
}
```

### Custom dashboard analyze request

```json
{
  "variables": ["Reg_Asia", "CR_SLR", "Plan_Adaptation"],
  "analysis_type": "chi_square"
}
```

### Research terminal request

```json
{
  "question": "Which cities appear most resilient and why?"
}
```

### City-specific OSM request

`GET /api/osm-gaps/city/<city_name>`

Returns city score, priority, critical gaps, and feature levels.

---

## 16) How each major calculation works (quick reference)

1. Gap Severity: `100 - osm_coverage_score`
2. Cramer's V: `sqrt(chi2 / (n*(min_dim)))` where `min_dim = min(r,c)-1`
3. Pearson correlation: pairwise linear association from dataframe correlation matrix
4. Regression prediction: linear weighted sum + intercept fit by ordinary least squares
5. RMSE: `sqrt(mean((y - y_pred)^2))`
6. Odds Ratio: `(a*d)/(b*c)` with continuity correction if needed
7. Association confidence: `P(B|A) = support(A and B)/support(A)`
8. Lift: `confidence / P(B)`

---

## 17) A-to-Z module index

- `app.py`: route orchestration and API surface
- `extract_and_prompt.py`: PDF extraction, LLM prompting, response parsing, research Q&A
- `statistical_analysis.py`: statistical core + custom analytics
- `visualizations.py`: statistical chart generation
- `osm_gap_analysis.py`: OSM scoring/report engine
- `osm_visualizations.py`: OSM chart generation
- `templates/index.html`: document analysis UI
- `templates/compare.html`: multi-document comparison UI
- `templates/statistics.html`: statistical dashboard UI
- `templates/dashboard.html`: interactive custom analysis UI
- `templates/research.html`: research chat UI
- `templates/osm_gaps.html`: OSM analysis UI
- `templates/osm_methodology.html`: OSM methodology narrative
- `static/map.js`: client geocoding/map plotting
- `data/megacities_dataset.csv`: resilience/climate data
- `data/osm_coverage_dataset.csv`: OSM coverage and priorities
- `test_models.py`: Gemini connectivity/model listing smoke test

---

## 18) Technical summary

This codebase integrates unstructured-policy extraction (LLM), quantitative analytics (classical statistics + regression), and geospatial data-gap diagnostics (OSM coverage framework) into one coherent research application. The engineering design emphasizes:

- route-level modularity
- strict JSON schema handling for LLM outputs
- resilient error handling for API limits/failures
- reusable analysis functions behind API endpoints
- interactive, explainable visual reporting for both statistical and OSM findings

That is the complete technical picture from ingestion, extraction, and modeling to visualization and deployment-ready web interaction.
