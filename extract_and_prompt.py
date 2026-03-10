import fitz  # PyMuPDF
import os
from google import genai
from google.genai import errors as genai_errors
from dotenv import load_dotenv
import json
from geopy.geocoders import Nominatim

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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
    doc = fitz.open(file_path)
    return "\n".join([page.get_text() for page in doc])

def analyze_document_complete(filepath):
    """
    Single API call that extracts everything: categories, city info, and insights.
    This reduces API usage from 3 calls to 1 call per document.
    """
    text = extract_text(filepath)
    prompt = f"""
You are an expert in climate adaptation planning. Analyze the following city adaptation document and provide a comprehensive analysis.

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
    "strengths": ["top 3 strengths of the adaptation strategy"],
    "gaps": ["top 3 weaknesses or missing elements"]
  }}
}}

Document:
{text[:5000]}
"""

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        result = parse_json_response(response.text)
        
        # Ensure all keys exist with defaults
        if not result or 'city_info' not in result:
            result = {
                "city_info": {"city": "Unknown", "country": "Unknown", "climate_zone": "N/A", "population": "N/A"},
                "categories": {},
                "insights": {"strengths": [], "gaps": []}
            }
        
        return result
        
    except genai_errors.ClientError as e:
        if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e):
            return {
                "city_info": {"city": "Unknown", "country": "Unknown", "climate_zone": "API rate limit exceeded", "population": "N/A"},
                "categories": {"error": "API rate limit exceeded. You've reached the free tier limit of 20 requests per day."},
                "insights": {
                    "strengths": ["API rate limit exceeded"],
                    "gaps": ["Please wait or upgrade your Gemini API plan"]
                }
            }
        return {
            "city_info": {"city": "Unknown", "country": "Unknown", "climate_zone": "API error", "population": "N/A"},
            "categories": {"error": f"API error: {str(e)[:100]}"},
            "insights": {"strengths": ["API error"], "gaps": [str(e)[:100]]}
        }
    except Exception as e:
        return {
            "city_info": {"city": "Unknown", "country": "Unknown", "climate_zone": "Error", "population": "N/A"},
            "categories": {"error": f"Unexpected error: {str(e)[:100]}"},
            "insights": {"strengths": ["Error occurred"], "gaps": [str(e)[:100]]}
        }

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
