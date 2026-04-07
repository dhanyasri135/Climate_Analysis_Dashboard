# 🌍 Climate Adaptation Mapping Dashboard (LLM-powered + Statistical Analysis + OSM Gap Analysis)

**A Comprehensive AI-Powered Platform for Climate Resilience Assessment**

This project presents a **quantitative framework and AI-powered analytics dashboard** designed to assess climate resilience across **43 global megacities**. It combines **Large Language Models (LLMs)** for policy document analysis with **statistical methods** (Chi-square tests, Cramer's V, regression modeling) and **OpenStreetMap gap analysis** to provide data-driven insights for urban sustainability and resilience modeling.

Built for researchers, policy analysts, and urban planners, the dashboard enables automated, structured extraction of insights from adaptation documents alongside rigorous statistical analysis of resilience patterns and identification of critical data gaps in OpenStreetMap infrastructure mapping.

---

## 🧠 What It Does

### Document Analysis
Upload one or more city adaptation plans (PDF or text), and the system will:

* 🔍 **Automatically categorize** content into:
  * Climate Risks & Natural Disasters
  * Infrastructure Systems
  * Financial Sources
  * Stakeholders Involved
* 🧠 **Generate AI-powered insights** (strengths, gaps, missing elements)
* 🏙️ **Extract city metadata** (name, country, population, climate zone)
* 🗺️ **Display the city on an interactive map**
* 📊 **Compare multiple cities** side-by-side
* ⚡ Visualize results with dynamic UI (Bootstrap + Leaflet)

### OSM Gap Analysis (NEW)
Comprehensive analysis of OpenStreetMap data gaps for climate resilience:

* 🗺️ **OSM Coverage Scoring** across 43 megacities (0-100%)
* 📊 **Gap Severity Analysis** identifying critical data missing from OSM
* 🎯 **Priority Wishlist** of 12 infrastructure features researchers need
* 🌆 **City Priority Rankings** for targeted mapping campaigns
* 📈 **6 Interactive Visualizations** (heatmaps, charts, scatter plots)
* 🔍 **Regional Analysis** comparing OSM coverage by world region
* 📖 **Detailed Methodology** explaining all calculations and scoring

---

## 🚀 Live Features

| Feature                          | Description                                  |
| -------------------------------- | -------------------------------------------- |
| ✅ LLM Categorization             | Extracts key themes using Gemini API        |
| ✅ Multi-City Upload              | Analyze and compare multiple documents       |
| ✅ 43 Megacities Dataset          | Pre-loaded resilience data                   |
| ✅ Statistical Testing            | Chi-square, Cramer's V, correlations         |
| ✅ Regression Modeling            | Predict resilience from key factors          |
| ✅ Interactive Visualizations     | Plotly charts, heatmaps, scatter plots       |
| ✅ Map Visualization              | Uses Leaflet + OpenStreetMap                 |
| ✅ City Profile Sidebar           | Extracts location, population, zone          |
| ✅ Insights Panel                 | Highlights strengths and gaps per plan       |
| ✅ **OSM Gap Analysis Dashboard** | **Standalone page for OSM data gap analysis**|
| ✅ **Priority Wishlist**          | **12 critical features categorized by impact**|
| ✅ **Methodology Page**           | **Detailed explanation of all calculations** |

---

## 🛠️ Tech Stack

### Backend
* **Flask**: Web framework
* **Gemini API**: Large Language Model for NLP
* **PyMuPDF**: PDF text extraction
* **Pandas & NumPy**: Data manipulation
* **SciPy**: Statistical tests (Chi-square, correlations)
* **Scikit-learn**: Regression modeling

### Frontend
* **HTML5 & Bootstrap 5**: Responsive UI
* **JavaScript & Plotly.js**: Interactive visualizations
* **Leaflet.js**: Geographic mapping

### Data Science
* **Statistical Analysis**: Chi-square, Cramer's V, Pearson correlation
* **Machine Learning**: Linear regression for resilience modeling
* **Data Visualization**: Heatmaps, scatter plots, bar charts

---

## 📂 Folder Structure

```
.
├── app.py                      # Flask application with routes
├── extract_and_prompt.py       # LLM document processing
├── statistical_analysis.py     # Statistical tests & regression
├── visualizations.py           # Chart generation (Plotly)
├── osm_gap_analysis.py         # OSM coverage gap analysis (NEW)
├── osm_visualizations.py       # OSM gap visualizations (NEW)
├── data/
│   ├── megacities_dataset.csv  # 43 cities climate data
│   └── osm_coverage_dataset.csv # OSM coverage metrics (NEW)
├── utils/
│   └── city_info.py            # City utilities
├── static/
│   ├── style.css
│   └── map.js
├── templates/
│   ├── index.html              # Document analysis page
│   ├── compare.html            # Multi-city comparison
│   ├── statistics.html         # Statistical dashboard
│   ├── dashboard.html          # Interactive dashboard
│   ├── research.html           # Research terminal
│   ├── osm_gaps.html           # OSM gap analysis page (NEW)
│   └── osm_methodology.html    # Methodology page (NEW)
├── uploads/                     # Uploaded documents
├── requirements.txt
├── .env
└── README.md
```

---

## 🔧 Setup Instructions

1. **Clone the repo**

   ```bash
   git clone https://github.com/your-username/climate-adaptation-dashboard.git
   cd climate-adaptation-dashboard
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   venv\Scripts\activate      # On Windows
   source venv/bin/activate  # On Mac/Linux
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set your Gemini API key**
   Create a `.env` file:

   ```
   GEMINI_API_KEY=your_api_key_here
   ```

5. **Run the app**

   ```bash
   python app.py
   ```

   Visit `http://localhost:5000`

---

## 🏗️ Build `megacities_dataset.csv` From Documents (Multi-pass Chunking)

The repository now includes a reproducible ingestion script that builds a dataset row per source document using full-document chunked extraction.

### What it does

* Splits each long document into overlapping chunks
* Extracts a candidate dataset row from each chunk with the LLM
* Reduces chunk-level outputs into one consolidated row per document
* Writes a CSV with the same schema as `data/megacities_dataset.csv`

### Command

```bash
python scripts/build_megacities_dataset.py --input-dir uploads --output-csv data/megacities_dataset_generated.csv
```

Optional flags:

* `--fail-fast` stop on first failed document

Input support: `.pdf`, `.docx`, `.txt`

---

## 📊 Using the Statistical Analysis

Navigate to **Statistical Analysis** from the main menu to access:

1. **Summary Statistics**: Overview of all 43 megacities
2. **Overview Tab**: 
   - Resilience score distribution
   - Regional comparisons
   - Climate risk analysis
   - Impact of adaptation plans
   - GDP vs. Resilience scatter plot
3. **Regression Analysis Tab**:
   - Multiple linear regression results
   - R² score and model quality
   - Coefficient impacts on resilience
4. **Correlations Tab**:
   - Interactive correlation heatmap
   - Significant correlations list
5. **Chi-Square Tests Tab**:
   - Categorical variable associations
   - Cramer's V effect sizes
   - Statistical significance tests

### Statistical Methods Explained

**Chi-Square Tests**: Tests independence between categorical variables (e.g., climate zone vs. adaptation plan existence)

**Cramer's V**: Measures strength of association (0-1 scale) for categorical variables

**Correlation Analysis**: Pearson correlations between numeric variables (GDP, population, infrastructure, resilience)

**Multiple Linear Regression**: Models resilience score based on population, GDP, infrastructure vulnerability, financial capacity, and stakeholder engagement

---

## 🗺️ Using the OSM Gap Analysis (NEW)

Navigate to the **OSM Gap Analysis** page to explore critical OpenStreetMap data gaps for climate resilience:

### Features:

1. **Priority Wishlist Tab**:
   - 12 infrastructure features categorized by research impact (Critical/High/Medium)
   - Subsurface drainage networks, flood barriers, emergency shelters, cooling infrastructure
   - Detailed descriptions of why researchers need each feature
   - Current OSM status vs. research requirements

2. **Data Visualizations Tab**:
   - Gap severity rankings (top 20 cities)
   - Feature coverage heatmap across priority cities
   - Priority level distribution (pie chart)
   - Regional coverage comparison
   - Global feature summary (stacked bars)
   - Coverage vs gap scatter plot

3. **Priority Cities Tab**:
   - Top 15 cities ranked by gap severity
   - Coverage scores, priority levels, and critical gaps
   - Identifies where mapping efforts would have greatest impact
   - Cities like Lagos, Kinshasa, Karachi prioritized for mapping

4. **Key Findings Tab**:
   - Research insights and statistical findings
   - Regional analysis by continent
   - Call to action for OSM mapping community
   - Impact statement for climate adaptation research

### Methodology Page:

Access the **Methodology & Calculations** page to understand:
- How OSM coverage scores are calculated (weighted average of 7 features)
- Gap severity scoring system (Critical/Severe/Moderate/Minor)
- Priority level assignment criteria
- Critical gaps identification process
- Data sources and assessment methods
- Statistical analysis techniques
- Research applications and limitations

### Key Insights:
- Only 9 of 43 cities have good OSM coverage (≥70%)
- 12 cities have critical gaps (<40% coverage)
- Subsurface drainage networks severely underrepresented globally
- Cooling infrastructure mapping critically needed for heat adaptation
- Emergency shelter capacity data almost entirely missing

### Data Sources:
The OSM gap analysis integrates data from multiple authoritative sources:

**OpenStreetMap Analysis (2025-2026):**
- Direct OSM data extraction via Overpass API for 43 megacities
- Feature completeness assessment using OSM Taginfo statistics
- Attribute quality analysis for climate-relevant infrastructure tags

**Climate & Vulnerability Data:**
- UN-Habitat Urban Resilience Database
- C40 Cities Climate Leadership Group datasets
- World Bank Climate Change Knowledge Portal
- IPCC Regional Climate Impact Studies (AR6)

**Validation & Reference:**
- Government open data portals (NYC, London, Tokyo, Paris)
- Academic research on OSM data quality (Haklay, Barrington-Leigh, Senaratne)
- Researcher interviews (12 climate adaptation experts, December 2025)

**Assessment Period:** December 2025 - February 2026

---

## 🧠 Why This Matters

Climate adaptation plans are rich but unstructured. This tool helps:

* Policymakers benchmark strategies
* Researchers extract and compare themes
* Cities identify blind spots and next steps
* **OSM mappers prioritize climate-critical infrastructure mapping**
* **Climate scientists identify data gaps limiting resilience modeling**

---

## 🙋‍♀️ Contribute or Collaborate

Pull requests are welcome! If you’re working in:

* Climate tech
* Public policy
* Urban data science
* LLM-based document analysis

Let’s connect!

---

## 📄 License

MIT License

