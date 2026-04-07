from flask import Flask, render_template, request, jsonify
from extract_and_prompt import (analyze_document_complete, 
                                answer_research_question)
from statistical_analysis import (run_full_analysis, load_dataset, 
                                   custom_correlation_analysis, custom_chi_square_analysis,
                                   custom_regression_analysis, custom_association_rules,
                                   custom_odds_ratio_analysis, get_codebook_summary,
                                   codebook_correlation_analysis, codebook_indicator_prevalence)
from visualizations import generate_all_visualizations
from osm_gap_analysis import (load_osm_dataset, generate_gap_analysis_report,
                               get_city_specific_gaps, calculate_gap_severity)
from osm_visualizations import generate_all_osm_visualizations
import os
import uuid
import pandas as pd

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def is_allowed_file(filename):
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS


def get_cities_list():
    """Load sorted city names for UI dropdown from multipass dataset (primary) or codebook (fallback)."""
    cities = []

    # Primary source: multipass chunked dataset
    try:
        from utils.codebook_loader import get_cities_from_multipass
        cities = get_cities_from_multipass()
    except Exception:
        cities = []

    # Fallback source: manually coded workbook
    if not cities:
        try:
            from utils.codebook_loader import load_codebook
            df = load_codebook()
            cities = [
                str(city).strip()
                for city in df["city"].tolist()
                if pd.notna(city) and str(city).strip()
            ]
        except Exception:
            cities = []

    # Fallback source: CSV dataset if codebook unavailable
    if not cities:
        csv_path = os.path.join("data", "megacities_dataset.csv")
        if os.path.exists(csv_path):
            df_csv = pd.read_csv(csv_path)
            if "city" in df_csv.columns:
                cities = [
                    str(city).strip()
                    for city in df_csv["city"].tolist()
                    if pd.notna(city) and str(city).strip()
                ]

    # De-duplicate while preserving sorted output
    return sorted(set(cities))

@app.route("/", methods=["GET", "POST"])
def index():
    cities = []
    try:
        cities = get_cities_list()
    except Exception:
        # Keep landing page usable even if codebook load fails.
        cities = []

    if request.method == "POST":
        uploaded_files = [
            f for f in request.files.getlist("files")
            if f and f.filename and f.filename.strip()
        ]

        if not uploaded_files:
            return render_template(
                "index.html",
                result=None,
                error_message="Please select at least one file to analyze.",
                cities=cities
            )

        results = []

        for file in uploaded_files:
            if not is_allowed_file(file.filename):
                results.append({
                    "filename": file.filename,
                    "categories": {
                        "error": "Unsupported file type. Please upload PDF, DOCX, or TXT files."
                    },
                    "city_info": {
                        "city": "Unknown",
                        "country": "Unknown",
                        "climate_zone": "N/A",
                        "population": "N/A"
                    },
                    "insights": {
                        "strengths": [],
                        "gaps": ["Unsupported file format"]
                    }
                })
                continue

            filename = f"{uuid.uuid4()}_{file.filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Single optimized API call instead of 3 separate calls
            result = analyze_document_complete(filepath)

            results.append({
                "filename": file.filename,
                "categories": result.get("categories", {}),
                "city_info": result.get("city_info", {}),
                "insights": result.get("insights", {})
            })

        if len(results) > 1:
            return render_template("compare.html", results=results)
        else:
            return render_template("index.html", result=results[0], cities=cities)

    return render_template("index.html", result=None, error_message=None, cities=cities)

@app.route("/statistics")
def statistics():
    """Statistical analysis dashboard route"""
    try:
        # Run full statistical analysis
        analysis_results = run_full_analysis()
        
        # Load dataset for visualizations
        df = load_dataset()
        
        # Generate all visualizations
        visualizations = generate_all_visualizations(df, analysis_results)
        
        return render_template(
            "statistics.html",
            stats=analysis_results,
            charts=visualizations
        )
    except Exception as e:
        return render_template(
            "statistics.html",
            error=str(e)
        )

@app.route("/api/statistics")
def api_statistics():
    """API endpoint for statistical data"""
    try:
        analysis_results = run_full_analysis()
        return jsonify(analysis_results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/dashboard")
def dashboard():
    """Interactive dashboard for custom variable analysis"""
    return render_template("dashboard.html")

@app.route("/api/dashboard/analyze", methods=["POST"])
def api_dashboard_analyze():
    """API endpoint for custom variable analysis"""
    try:
        data = request.get_json()
        variables = data.get("variables", [])
        analysis_type = data.get("analysis_type", "correlation")
        
        if len(variables) < 2:
            return jsonify({"error": "Please select at least 2 variables"}), 400
        
        # Perform the requested analysis
        if analysis_type == "correlation":
            results = custom_correlation_analysis(variables)
        elif analysis_type == "chi_square":
            results = custom_chi_square_analysis(variables)
        elif analysis_type == "regression":
            results = custom_regression_analysis(variables)
        elif analysis_type == "association_rules":
            results = custom_association_rules(variables)
        elif analysis_type == "odds_ratio":
            results = custom_odds_ratio_analysis(variables)
        else:
            return jsonify({"error": "Invalid analysis type"}), 400
        
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/research")
def research():
    """Research terminal for asking questions about climate adaptation"""
    return render_template("research.html")

@app.route("/api/research/ask", methods=["POST"])
def api_research_ask():
    """API endpoint for research questions"""
    try:
        data = request.get_json()
        question = data.get("question", "").strip()
        
        if not question:
            return jsonify({"error": "Please provide a question"}), 400
        
        # Load dataset context for data-specific questions
        df = load_dataset()
        dataset_summary = df.head(5).to_string() if df is not None else None
        
        # Get answer from LLM
        answer = answer_research_question(question, dataset_summary)
        
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/osm-gaps")
def osm_gaps():
    """OSM Gap Analysis dashboard for climate resilience research"""
    try:
        # Load OSM coverage dataset
        df = load_osm_dataset()
        df = calculate_gap_severity(df)
        
        # Generate comprehensive gap analysis report
        report = generate_gap_analysis_report()
        
        # Generate all visualizations
        visualizations = generate_all_osm_visualizations(df, report)
        
        return render_template(
            "osm_gaps.html",
            report=report,
            charts=visualizations
        )
    except Exception as e:
        return render_template(
            "osm_gaps.html",
            error=str(e)
        )

@app.route("/api/osm-gaps/city/<city_name>")
def api_osm_city_gaps(city_name):
    """API endpoint for city-specific gap analysis"""
    try:
        city_data = get_city_specific_gaps(city_name)
        if city_data is None:
            return jsonify({"error": "City not found"}), 404
        return jsonify(city_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/osm-methodology")
def osm_methodology():
    """OSM Gap Analysis Methodology and Calculations"""
    return render_template("osm_methodology.html")

@app.route("/api/codebook/summary")
def api_codebook_summary():
    """API endpoint for codebook summary statistics"""
    try:
        summary = get_codebook_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/codebook/prevalence")
def api_codebook_prevalence():
    """API endpoint for indicator prevalence analysis"""
    try:
        prevalence = codebook_indicator_prevalence()
        return jsonify(prevalence)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/codebook/correlations")
def api_codebook_correlations():
    """API endpoint for indicator correlation analysis"""
    try:
        correlations = codebook_correlation_analysis()
        return jsonify(correlations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/cities")
def api_cities():
    """API endpoint to get list of all cities in codebook"""
    try:
        cities = get_cities_list()
        return jsonify({"cities": cities})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/city/<city_name>/codebook")
def api_city_codebook(city_name):
    """API endpoint to get city-specific analysis from multipass dataset"""
    try:
        from utils.codebook_loader import analyze_city_features
        
        # Use the new multipass analysis function
        city_analysis = analyze_city_features(city_name)
        
        return jsonify(city_analysis)
    except ValueError as e:
        # City not found
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Analysis error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
