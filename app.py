from flask import Flask, render_template, request
from extract_and_prompt import process_document, extract_city_info, get_llm_insights
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

            analysis = process_document(filepath)
            city_info = extract_city_info(filepath)
            insights = get_llm_insights(filepath)

            results.append({
                "filename": file.filename,
                "categories": analysis,
                "city_info": city_info,
                "insights": insights
            })

        if len(results) > 1:
            return render_template("compare.html", results=results)
        else:
            return render_template("index.html", result=results[0])

    return render_template("index.html", result=None)
if __name__ == "__main__":
    app.run(debug=True)
