from flask import Flask, render_template, request, jsonify
from extract_and_prompt import analyze_document_complete
from statistical_analysis import run_full_analysis, load_dataset
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

if __name__ == "__main__":
    app.run(debug=True)
