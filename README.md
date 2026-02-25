# 🌍 Climate Adaptation Mapping Dashboard (LLM-powered + Statistical Analysis)

**A Comprehensive AI-Powered Platform for Climate Resilience Assessment**

This project presents a **quantitative framework and AI-powered analytics dashboard** designed to assess climate resilience across **43 global megacities**. It combines **Large Language Models (LLMs)** for policy document analysis with **statistical methods** (Chi-square tests, Cramer's V, regression modeling) to provide data-driven insights for urban sustainability.

Built for researchers, policy analysts, and urban planners, the dashboard enables automated, structured extraction of insights from adaptation documents alongside rigorous statistical analysis of resilience patterns across the world's largest cities.

---

## 🧠 What It Does

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

---

## 🚀 Live Features

| Feature                          | Description                            |
| -------------------------------- | -------------------------------------- |
| ✅ LLM Categorization             | Extracts key themes using Gemini API  |
| ✅ Multi-City Upload              | Analyze and compare multiple documents |
| ✅ 43 Megacities Dataset          | Pre-loaded resilience data             |
| ✅ Statistical Testing            | Chi-square, Cramer's V, correlations   |
| ✅ Regression Modeling            | Predict resilience from key factors    |
| ✅ Interactive Visualizations     | Plotly charts, heatmaps, scatter plots |
| ✅ Map Visualization              | Uses Leaflet + OpenStreetMap           |
| ✅ City Profile Sidebar           | Extracts location, population, zone    |
| ✅ Insights Panel                 | Highlights strengths and gaps per plan |

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
├── data/
│   └── megacities_dataset.csv  # 43 cities data
├── utils/
│   └── city_info.py            # City utilities
├── static/
│   ├── style.css
│   └── map.js
├── templates/
│   ├── index.html              # Document analysis page
│   ├── compare.html            # Multi-city comparison
│   └── statistics.html         # Statistical dashboard
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


## 🧠 Why This Matters

Climate adaptation plans are rich but unstructured. This tool helps:

* Policymakers benchmark strategies
* Researchers extract and compare themes
* Cities identify blind spots and next steps

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

