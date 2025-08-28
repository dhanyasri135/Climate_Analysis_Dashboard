# utils/city_info.py
import fitz  # PyMuPDF
import re
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="climate_dashboard")

def extract_city_metadata(text):
    # Naive pattern: Look for common city-country structure
    lines = text.split("\n")
    for line in lines:
        if "," in line and any(c.isalpha() for c in line):
            parts = line.strip().split(",")
            if len(parts) >= 2:
                city = parts[0].strip()
                country = parts[1].strip()
                return city, country
    return "Unknown", "Unknown"

def get_city_coordinates(city, country):
    try:
        location = geolocator.geocode(f"{city}, {country}")
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print("Geolocation error:", e)
    return None, None

def extract_city_info(filepath):
    doc = fitz.open(filepath)
    text = "\n".join([page.get_text() for page in doc])
    city, country = extract_city_metadata(text)
    lat, lon = get_city_coordinates(city, country)
    return {
        "city": city,
        "country": country,
        "climate_zone": "(to be predicted via LLM)",
        "population": "(to be extracted via LLM)",
        "latitude": lat,
        "longitude": lon
    }
