import fitz  # PyMuPDF
import os
import time
from collections import Counter
from statistics import median
from google import genai
from google.genai import errors as genai_errors
from dotenv import load_dotenv
import json
from geopy.geocoders import Nominatim

try:
    from docx import Document
except ImportError:
    Document = None

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

CHUNK_SIZE_CHARS = 4500
CHUNK_OVERLAP_CHARS = 400
MODEL_NAME = "gemini-2.5-flash"
MAX_RETRIES = 3
BASE_RETRY_DELAY_SECONDS = 1.5
DEFAULT_CATEGORY_KEYS = [
    "Climate Risks / Natural Disasters",
    "Infrastructure Systems",
    "Financial Sources supporting adaptation planning",
    "Stakeholders involved"
]
UNKNOWN_VALUES = {"", "unknown", "n/a", "na", "not specified", "none"}
DATASET_COLUMNS = [
    "city", "country", "region", "population_millions", "gdp_per_capita",
    "climate_zone", "coastal", "flood_risk", "heat_risk", "drought_risk",
    "sea_level_rise_risk", "adaptation_plan_exists", "infrastructure_vulnerability",
    "financial_capacity", "stakeholder_engagement", "resilience_score"
]
RISK_LEVELS = {"Low", "Medium", "High"}
YES_NO_VALUES = {"Yes", "No"}

def parse_json_response(response_text):
    """Extract JSON from response, handling markdown code blocks."""
    if not response_text or response_text.strip() == '':
        return {}
    
    # Remove markdown code blocks if present
    text = response_text.strip()
    if text.startswith('```json'):
        text = text[7:]  # Remove ```json
    elif text.startswith('```'):
        text = text[3:]  # Remove ```
    
    if text.endswith('```'):
        text = text[:-3]  # Remove closing ```
    
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Response text: {text[:500]}")
        # Return a default structure
        return {}

def extract_text(file_path):
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == ".pdf":
        with fitz.open(file_path) as doc:
            return "\n".join([page.get_text() for page in doc])

    if ext == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()

    if ext == ".docx":
        if Document is None:
            raise ValueError("DOCX support requires python-docx. Please install the dependency.")
        doc = Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    if ext == ".doc":
        raise ValueError("Legacy .doc files are not supported. Please convert to .docx or PDF.")

    raise ValueError(f"Unsupported file type: {ext}")


def _default_analysis_result(climate_zone="N/A", category_error=None, gap_message=None):
    categories = {k: [] for k in DEFAULT_CATEGORY_KEYS}
    if category_error:
        categories = {"error": category_error}

    gaps = []
    if gap_message:
        gaps = [gap_message]

    return {
        "city_info": {
            "city": "Unknown",
            "country": "Unknown",
            "climate_zone": climate_zone,
            "population": "N/A"
        },
        "categories": categories,
        "insights": {
            "strengths": [],
            "gaps": gaps
        }
    }


def split_text_into_chunks(text, chunk_size=CHUNK_SIZE_CHARS, overlap=CHUNK_OVERLAP_CHARS):
    if not text:
        return []

    if chunk_size <= 0:
        return [text]

    if overlap >= chunk_size:
        overlap = 0

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks


def _is_valid_city_value(value):
    if value is None:
        return False
    normalized = str(value).strip().lower()
    return normalized not in UNKNOWN_VALUES


def _pick_consensus_value(values, fallback):
    valid_values = [str(v).strip() for v in values if _is_valid_city_value(v)]
    if not valid_values:
        return fallback

    counts = Counter(valid_values)
    max_count = max(counts.values())
    top_values = {v for v, c in counts.items() if c == max_count}
    for value in valid_values:
        if value in top_values:
            return value

    return fallback


def _normalize_list(values):
    if not isinstance(values, list):
        return []
    return [str(v).strip() for v in values if str(v).strip()]


def _merge_ranked_items(items, limit=3):
    counts = Counter()
    first_seen = {}
    original_text = {}

    for idx, item in enumerate(items):
        item_text = str(item).strip()
        if not item_text:
            continue
        key = item_text.lower()
        counts[key] += 1
        if key not in first_seen:
            first_seen[key] = idx
            original_text[key] = item_text

    ranked_keys = sorted(counts.keys(), key=lambda k: (-counts[k], first_seen[k]))
    return [original_text[k] for k in ranked_keys[:limit]]


def _is_rate_limit_error(error_text):
    text = error_text.lower()
    return "429" in text or "resource_exhausted" in text or "rate limit" in text


def _is_transient_service_error(error_text):
    text = error_text.lower()
    return (
        "503" in text
        or "unavailable" in text
        or "high demand" in text
        or "internal" in text
        or "deadline exceeded" in text
        or "timeout" in text
    )


def _generate_content_with_retry(prompt, max_retries=MAX_RETRIES):
    for attempt in range(max_retries + 1):
        try:
            return client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
        except genai_errors.ClientError as e:
            error_text = str(e)
            retryable = _is_transient_service_error(error_text)
            if (not retryable) or attempt == max_retries:
                raise

            delay = BASE_RETRY_DELAY_SECONDS * (2 ** attempt)
            time.sleep(delay)


def _analyze_single_chunk(chunk_text, chunk_index, total_chunks):
    prompt = f"""
You are an expert in climate adaptation planning. Analyze this section of a city adaptation document.

This is chunk {chunk_index} of {total_chunks}. Focus strictly on evidence present in this chunk.

Respond ONLY in JSON format with ALL of the following sections:

{{
  "city_info": {{
    "city": "city name",
    "country": "country name",
    "climate_zone": "climate zone if mentioned",
    "population": "population if mentioned"
  }},
  "categories": {{
    "Climate Risks / Natural Disasters": ["list of identified risks and disasters"],
    "Infrastructure Systems": ["list of infrastructure systems mentioned"],
    "Financial Sources supporting adaptation planning": ["list of financial sources"],
    "Stakeholders involved": ["list of stakeholders"]
  }},
  "insights": {{
    "strengths": ["top strengths from this chunk only"],
    "gaps": ["top weaknesses or missing elements from this chunk only"]
  }}
}}

Document chunk:
{chunk_text}
"""

    response = _generate_content_with_retry(prompt)
    return parse_json_response(response.text)


def _reduce_chunk_results(chunk_results):
    if not chunk_results:
        return _default_analysis_result(gap_message="No analyzable content found.")

    city_values = {
        "city": [],
        "country": [],
        "climate_zone": [],
        "population": []
    }
    merged_categories = {k: [] for k in DEFAULT_CATEGORY_KEYS}
    all_strengths = []
    all_gaps = []

    for chunk_result in chunk_results:
        if not isinstance(chunk_result, dict):
            continue

        city_info = chunk_result.get("city_info", {}) or {}
        for key in city_values:
            city_values[key].append(city_info.get(key, ""))

        categories = chunk_result.get("categories", {}) or {}
        for key in DEFAULT_CATEGORY_KEYS:
            merged_categories[key].extend(_normalize_list(categories.get(key, [])))

        insights = chunk_result.get("insights", {}) or {}
        all_strengths.extend(_normalize_list(insights.get("strengths", [])))
        all_gaps.extend(_normalize_list(insights.get("gaps", [])))

    deduped_categories = {}
    for key, items in merged_categories.items():
        deduped_categories[key] = _merge_ranked_items(items, limit=20)

    return {
        "city_info": {
            "city": _pick_consensus_value(city_values["city"], "Unknown"),
            "country": _pick_consensus_value(city_values["country"], "Unknown"),
            "climate_zone": _pick_consensus_value(city_values["climate_zone"], "N/A"),
            "population": _pick_consensus_value(city_values["population"], "N/A")
        },
        "categories": deduped_categories,
        "insights": {
            "strengths": _merge_ranked_items(all_strengths, limit=3),
            "gaps": _merge_ranked_items(all_gaps, limit=3)
        }
    }

def analyze_document_complete(filepath):
    """
    Multi-pass extraction over the full document.
    For long documents, this runs chunk-level extraction and merges all chunk outputs.
    """
    text = extract_text(filepath)

    if not text or not text.strip():
        return _default_analysis_result(gap_message="No text could be extracted from the uploaded document.")

    chunks = split_text_into_chunks(text)
    if not chunks:
        return _default_analysis_result(gap_message="No analyzable content found in the uploaded document.")

    chunk_results = []
    chunk_errors = []

    for idx, chunk in enumerate(chunks, start=1):
        try:
            chunk_result = _analyze_single_chunk(chunk, idx, len(chunks))
            if isinstance(chunk_result, dict) and chunk_result:
                chunk_results.append(chunk_result)
            else:
                chunk_errors.append(f"Chunk {idx}: Empty or invalid response")
        except genai_errors.ClientError as e:
            chunk_errors.append(f"Chunk {idx}: {str(e)[:200]}")
        except Exception as e:
            chunk_errors.append(f"Chunk {idx}: {str(e)[:200]}")

    if not chunk_results:
        joined_errors = " | ".join(chunk_errors).lower()
        if _is_rate_limit_error(joined_errors):
            return _default_analysis_result(
                climate_zone="API rate limit exceeded",
                category_error="API rate limit exceeded. You've reached the free tier limit of 20 requests per day.",
                gap_message="Please wait or upgrade your Gemini API plan"
            )
        if _is_transient_service_error(joined_errors):
            return _default_analysis_result(
                climate_zone="API temporarily unavailable",
                category_error="AI service is temporarily unavailable due to high demand. Please retry in a moment.",
                gap_message="Temporary model outage during document processing"
            )
        first_error = chunk_errors[0] if chunk_errors else "Unknown error"
        return _default_analysis_result(
            climate_zone="API error",
            category_error=f"API error: {first_error[:100]}",
            gap_message=first_error[:100]
        )

    merged_result = _reduce_chunk_results(chunk_results)
    if not merged_result or 'city_info' not in merged_result:
        return _default_analysis_result(gap_message="Unable to parse model output.")

    if chunk_errors:
        partial_note = "Some document sections could not be processed due to temporary AI service issues."
        current_gaps = merged_result.get("insights", {}).get("gaps", [])
        if partial_note not in current_gaps:
            current_gaps.append(partial_note)
        merged_result["insights"]["gaps"] = current_gaps[:3]

    return merged_result


def _normalize_yes_no(value, fallback="No"):
    if value is None:
        return fallback
    text = str(value).strip().lower()
    if text in {"yes", "y", "true", "1"}:
        return "Yes"
    if text in {"no", "n", "false", "0"}:
        return "No"
    return fallback


def _normalize_risk_level(value, fallback="Medium"):
    if value is None:
        return fallback
    text = str(value).strip().lower()
    if text == "low":
        return "Low"
    if text == "medium":
        return "Medium"
    if text == "high":
        return "High"
    return fallback


def _safe_float(value):
    if value is None:
        return None
    text = str(value).strip().replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _pick_numeric_value(values):
    numeric_values = []
    for value in values:
        parsed = _safe_float(value)
        if parsed is not None:
            numeric_values.append(parsed)

    if not numeric_values:
        return None
    return round(median(numeric_values), 3)


def _reduce_dataset_chunk_rows(chunk_rows):
    if not chunk_rows:
        return {}

    fields = {col: [] for col in DATASET_COLUMNS}
    for row in chunk_rows:
        if not isinstance(row, dict):
            continue
        for col in DATASET_COLUMNS:
            fields[col].append(row.get(col))

    reduced_row = {
        "city": _pick_consensus_value(fields["city"], "Unknown"),
        "country": _pick_consensus_value(fields["country"], "Unknown"),
        "region": _pick_consensus_value(fields["region"], "Unknown"),
        "population_millions": _pick_numeric_value(fields["population_millions"]),
        "gdp_per_capita": _pick_numeric_value(fields["gdp_per_capita"]),
        "climate_zone": _pick_consensus_value(fields["climate_zone"], "Unknown"),
        "coastal": _normalize_yes_no(_pick_consensus_value(fields["coastal"], "No"), "No"),
        "flood_risk": _normalize_risk_level(_pick_consensus_value(fields["flood_risk"], "Medium"), "Medium"),
        "heat_risk": _normalize_risk_level(_pick_consensus_value(fields["heat_risk"], "Medium"), "Medium"),
        "drought_risk": _normalize_risk_level(_pick_consensus_value(fields["drought_risk"], "Medium"), "Medium"),
        "sea_level_rise_risk": _normalize_risk_level(_pick_consensus_value(fields["sea_level_rise_risk"], "Medium"), "Medium"),
        "adaptation_plan_exists": _normalize_yes_no(_pick_consensus_value(fields["adaptation_plan_exists"], "No"), "No"),
        "infrastructure_vulnerability": _normalize_risk_level(_pick_consensus_value(fields["infrastructure_vulnerability"], "Medium"), "Medium"),
        "financial_capacity": _normalize_risk_level(_pick_consensus_value(fields["financial_capacity"], "Medium"), "Medium"),
        "stakeholder_engagement": _normalize_risk_level(_pick_consensus_value(fields["stakeholder_engagement"], "Medium"), "Medium"),
        "resilience_score": _pick_numeric_value(fields["resilience_score"])
    }

    return reduced_row


def _extract_dataset_row_from_chunk(chunk_text, chunk_index, total_chunks):
    prompt = f"""
You are a climate adaptation data extraction assistant.

Extract one candidate row for a megacity climate dataset from this document chunk.
This is chunk {chunk_index} of {total_chunks}.

Return ONLY JSON with exactly these keys:
{{
  "city": "string or null",
  "country": "string or null",
  "region": "Africa|Asia|Europe|North America|South America|Oceania|Unknown|null",
  "population_millions": "number or null",
  "gdp_per_capita": "number or null",
  "climate_zone": "string or null",
  "coastal": "Yes|No|null",
  "flood_risk": "Low|Medium|High|null",
  "heat_risk": "Low|Medium|High|null",
  "drought_risk": "Low|Medium|High|null",
  "sea_level_rise_risk": "Low|Medium|High|null",
  "adaptation_plan_exists": "Yes|No|null",
  "infrastructure_vulnerability": "Low|Medium|High|null",
  "financial_capacity": "Low|Medium|High|null",
  "stakeholder_engagement": "Low|Medium|High|null",
  "resilience_score": "number between 0 and 10, or null"
}}

Rules:
- Use null when information is not present in this chunk.
- Do not invent city names.
- Keep risk/capacity labels in Low/Medium/High.

Document chunk:
{chunk_text}
"""

    response = _generate_content_with_retry(prompt)
    return parse_json_response(response.text)


def analyze_document_for_dataset_row(filepath):
    """
    Multi-pass chunked ingestion for generating one dataset row from one document.
    Returns a dictionary containing DATASET_COLUMNS.
    """
    text = extract_text(filepath)
    if not text or not text.strip():
        raise ValueError("No text could be extracted from document")

    chunks = split_text_into_chunks(text)
    if not chunks:
        raise ValueError("No analyzable chunks generated from document")

    chunk_rows = []
    chunk_errors = []

    for idx, chunk in enumerate(chunks, start=1):
        try:
            row = _extract_dataset_row_from_chunk(chunk, idx, len(chunks))
            if isinstance(row, dict) and row:
                chunk_rows.append(row)
            else:
                chunk_errors.append(f"Chunk {idx}: Empty extraction")
        except Exception as e:
            chunk_errors.append(f"Chunk {idx}: {str(e)[:200]}")

    if not chunk_rows:
        first_error = chunk_errors[0] if chunk_errors else "Unknown extraction error"
        raise RuntimeError(first_error)

    reduced_row = _reduce_dataset_chunk_rows(chunk_rows)

    if not reduced_row.get("city") or reduced_row.get("city") == "Unknown":
        filename = os.path.basename(filepath)
        reduced_row["city"] = os.path.splitext(filename)[0]

    return reduced_row

# Keep the old functions for backward compatibility, but they now call the optimized version


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

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return parse_json_response(response.text)
    except genai_errors.ClientError as e:
        if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):
            return {"error": "API rate limit exceeded. Please try again later or upgrade your API plan."}
        return {"error": f"API error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

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

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return parse_json_response(response.text)
    except genai_errors.ClientError as e:
        if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):
            return {"city": "Unknown", "country": "Unknown", "climate_zone": "API rate limit exceeded", "population": "N/A"}
        return {"city": "Unknown", "country": "Unknown", "climate_zone": "API error", "population": "N/A"}
    except Exception as e:
        return {"city": "Unknown", "country": "Unknown", "climate_zone": "Error", "population": "N/A"}

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

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return parse_json_response(response.text)
    except genai_errors.ClientError as e:
        if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):
            return {
                "strengths": ["API rate limit exceeded. You've reached the free tier limit of 20 requests per day."],
                "gaps": ["Please wait ~17 seconds or upgrade your Gemini API plan for higher limits."]
            }
        return {
            "strengths": ["API error occurred"],
            "gaps": [f"Error: {str(e)[:100]}"]
        }
    except Exception as e:
        return {
            "strengths": ["Unexpected error"],
            "gaps": [f"Error: {str(e)[:100]}"]
        }

def answer_research_question(question, dataset_context=None):
    """
    Answer research questions about climate adaptation using the LLM.
    Optionally includes dataset context for data-specific questions.
    """
    # Build context-aware prompt
    context_info = ""
    if dataset_context:
        context_info = f"""
Context: You have access to a dataset of 43 global megacities with the following information:
- Cities from various climate zones (Tropical, Temperate, Arid, Continental)
- Climate resilience scores and adaptation plan status
- Population, GDP, and infrastructure quality metrics
- Stakeholder engagement levels
- Climate risks and mitigation strategies

Dataset sample:
{dataset_context[:1000]}
"""
    
    prompt = f"""
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
"""

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text.strip()
        
    except genai_errors.ClientError as e:
        if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):
            return "⚠️ API rate limit exceeded. You've reached the free tier limit of 20 requests per day. Please wait or upgrade your Gemini API plan."
        return f"⚠️ API error: {str(e)[:200]}"
    except Exception as e:
        return f"⚠️ An error occurred: {str(e)[:200]}"
