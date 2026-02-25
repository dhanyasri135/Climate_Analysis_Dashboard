from flask import Flask, render_template, request, jsonify
from extract_and_prompt import analyze_document_complete
from statistical_analysis import (run_full_analysis, load_dataset, 
                                   custom_correlation_analysis, custom_chi_square_analysis,
                                   custom_regression_analysis, custom_association_rules,
                                   custom_odds_ratio_analysis)
from visualizations import generate_all_visualizations
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_files = request.files.getlist("files")
        results = []

        for file in uploaded_files:
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
            return render_template("index.html", result=results[0])

    return render_template("index.html", result=None)

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

if __name__ == "__main__":
    app.run(debug=True)
