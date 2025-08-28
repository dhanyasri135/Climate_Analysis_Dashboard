import fitz  # PyMuPDF
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from geopy.geocoders import Nominatim

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
def extract_text(file_path):
    doc = fitz.open(file_path)
    return "\n".join([page.get_text() for page in doc])

def process_document(filepath):
    text = extract_text(filepath)
    prompt = f"""
You are an expert in climate adaptation planning. Categorize the following city adaptation document into the following:

1. Climate Risks / Natural Disasters
2. Infrastructure Systems
3. Financial Sources supporting adaptation planning
4. Stakeholders involved

Within each category, identify specific sub-themes.

Respond ONLY in JSON format:
{{
  "Climate Risks / Natural Disasters": [...],
  "Infrastructure Systems": [...],
  "Financial Sources supporting adaptation planning": [...],
  "Stakeholders involved": [...]
}}

Document:
{text[:4000]}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return json.loads(response.choices[0].message.content)

def extract_city_info(filepath):
    text = extract_text(filepath)
    prompt = """
Extract city name, country, and if possible, climate zone and population from the document below. Respond in JSON format:
{
  "city": "...",
  "country": "...",
  "climate_zone": "...",
  "population": "..."
}
Document:
""" + text[:3000]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return json.loads(response.choices[0].message.content)

def get_llm_insights(filepath):
    text = extract_text(filepath)
    prompt = """
You are an expert climate adaptation policy analyst. Given the document below, summarize:
1. Top 3 strengths of the adaptation strategy
2. Top 3 weaknesses or missing elements
Respond in this format:
{
  "strengths": ["...", "..."],
  "gaps": ["...", "..."]
}
Document:
""" + text[:4000]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return json.loads(response.choices[0].message.content)
