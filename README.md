# 🌍 Climate Adaptation Mapping Dashboard (LLM-powered)

This project is a web-based tool that uses **Large Language Models (LLMs)** like GPT-4 to analyze city-level climate adaptation plans and visualize key strategies, risks, and gaps.

Built for researchers, policy analysts, and urban planners, the dashboard enables automated, structured extraction of insights from adaptation documents — with features for comparison, mapping, and interpretation.

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
| ✅ LLM Categorization             | Extracts key themes using GPT-4        |
| ✅ Multi-City Upload              | Analyze and compare multiple documents |
| ✅ Map Visualization              | Uses Leaflet + OpenStreetMap           |
| ✅ City Profile Sidebar           | Extracts location, population, zone    |
| ✅ Insights Panel                 | Highlights strengths and gaps per plan |
| 📄 Export to PDF/HTML *(coming)* | Print-friendly reports (WIP)           |

---

## 🛠️ Tech Stack

* **Backend**: `Flask`, `PyMuPDF`, `OpenAI API`
* **Frontend**: `HTML`, `Bootstrap 5`, `JavaScript`, `Leaflet.js`
* **Utilities**: `Geopy` (for geocoding), `dotenv`, `uuid`
* **LLM Model**: `gpt-4` or `gpt-3.5-turbo`

---

## 📂 Folder Structure

```
.
├── app.py
├── extract_and_prompt.py
├── utils/
│   └── city_info.py
├── static/
│   ├── style.css
│   └── map.js
├── templates/
│   ├── index.html
│   └── compare.html
├── uploads/
├── requirements.txt
├── .env.example
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

4. **Set your OpenAI API key**
   Create a `.env` file:

   ```
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxx
   ```

5. **Run the app**

   ```bash
   python app.py
   ```

   Visit `http://localhost:5000`

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

