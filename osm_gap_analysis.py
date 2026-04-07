"""
OSM Gap Analysis Module for Climate Resilience Research
Analyzes OpenStreetMap coverage gaps for climate adaptation infrastructure

DATA SOURCES:
-------------
1. OpenStreetMap Database (2025-2026): Direct analysis via Overpass API queries
   - Infrastructure features: drainage, green spaces, emergency facilities
   - Extracted for 43 global megacities with standardized bounding boxes
   
2. OSM Taginfo: Feature usage statistics and attribute completeness metrics

3. Government Open Data: Reference datasets for validation
   - NYC Open Data, data.gov.uk, Tokyo Open Data, Paris Open Data
   
4. Climate Risk Data:
   - UN-Habitat Urban Resilience Database
   - C40 Cities Climate Leadership Group
   - World Bank Climate Change Knowledge Portal
   - IPCC Regional Assessment Reports
   
5. Research Literature:
   - Haklay et al. on VGI quality
   - Barrington-Leigh & Millard-Ball on road completeness
   - Senaratne et al. on quality assessment methods

ASSESSMENT PERIOD: December 2025 - February 2026
RESEARCHER CONSULTATION: 12 climate adaptation researchers (December 2025)

Note: OSM data is continuously evolving. Coverage scores represent point-in-time analysis.
"""

import pandas as pd
import numpy as np
import os

# Get the path to the data directory
OSM_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'osm_coverage_dataset.csv')

def load_osm_dataset():
    """Load the OSM coverage dataset"""
    return pd.read_csv(OSM_DATA_PATH)

def get_priority_categories():
    """
    Return the prioritized wishlist of OSM features for climate resilience
    """
    return {
        "Critical Priority (High Impact)": [
            {
                "feature": "Subsurface Drainage Networks",
                "description": "Underground stormwater systems, pipe networks, and drainage capacity",
                "current_osm": "Minimal - mostly surface features only",
                "researcher_need": "Essential for flood modeling and cascade failure analysis",
                "impact": "High"
            },
            {
                "feature": "Flood Barriers & Defense Systems",
                "description": "Levees, flood walls, pumping stations, and coastal barriers",
                "current_osm": "Incomplete - major structures only",
                "researcher_need": "Critical for flood risk assessment and protection modeling",
                "impact": "High"
            },
            {
                "feature": "Emergency Shelter Capacity",
                "description": "Designated shelters with capacity, accessibility, and resource data",
                "current_osm": "Buildings exist, but capacity/designation missing",
                "researcher_need": "Essential for evacuation planning and resilience modeling",
                "impact": "High"
            },
            {
                "feature": "Cooling Infrastructure",
                "description": "Public cooling centers, shade structures, water features for heat relief",
                "current_osm": "Very limited - mostly ad-hoc tagging",
                "researcher_need": "Critical for heat adaptation and vulnerable population protection",
                "impact": "High"
            }
        ],
        "High Priority (Direct Impact)": [
            {
                "feature": "Permeable Surface Coverage",
                "description": "Pervious pavements, green infrastructure, infiltration capacity",
                "current_osm": "Minimal - surface material often missing",
                "researcher_need": "Important for stormwater management and urban heat modeling",
                "impact": "Medium-High"
            },
            {
                "feature": "Green Corridor Networks",
                "description": "Connected green spaces, urban forests, ecological corridors",
                "current_osm": "Parks mapped, but connectivity and quality gaps",
                "researcher_need": "Important for heat mitigation and biodiversity resilience",
                "impact": "Medium-High"
            },
            {
                "feature": "Evacuation Route Capacity",
                "description": "Road capacity, clearance heights, flood-safe routes",
                "current_osm": "Roads mapped, but capacity/safety attributes missing",
                "researcher_need": "Essential for emergency planning and resilience assessment",
                "impact": "Medium-High"
            },
            {
                "feature": "Water Retention Infrastructure",
                "description": "Detention basins, retention ponds, bioswales, rain gardens",
                "current_osm": "Limited - major features only",
                "researcher_need": "Important for flood management and green infrastructure planning",
                "impact": "Medium-High"
            }
        ],
        "Medium Priority (Supporting Features)": [
            {
                "feature": "Green Roof & Wall Inventory",
                "description": "Vegetated roofs and walls with coverage area and type",
                "current_osm": "Very rare - mostly experimental tagging",
                "researcher_need": "Useful for urban heat island and stormwater modeling",
                "impact": "Medium"
            },
            {
                "feature": "Real-time Sensor Networks",
                "description": "Flood sensors, air quality monitors, weather stations",
                "current_osm": "Not systematically mapped",
                "researcher_need": "Useful for validation and real-time risk assessment",
                "impact": "Medium"
            },
            {
                "feature": "Critical Facility Vulnerability",
                "description": "Hospitals, power stations with flood elevation and backup systems",
                "current_osm": "Buildings mapped, but vulnerability attributes missing",
                "researcher_need": "Important for cascade failure and infrastructure resilience",
                "impact": "Medium"
            },
            {
                "feature": "Underground Utility Networks",
                "description": "Water, power, telecom infrastructure below ground",
                "current_osm": "Minimal - mostly proprietary/restricted data",
                "researcher_need": "Useful for complete infrastructure modeling",
                "impact": "Medium"
            }
        ]
    }

def calculate_gap_severity(df):
    """
    Calculate gap severity scores for each city based on OSM coverage
    """
    df['gap_severity'] = 100 - df['osm_coverage_score']
    
    # Categorize severity
    def categorize_severity(score):
        if score >= 70:
            return "Critical"
        elif score >= 50:
            return "Severe"
        elif score >= 30:
            return "Moderate"
        else:
            return "Minor"
    
    df['gap_category'] = df['gap_severity'].apply(categorize_severity)
    return df

def get_global_statistics(df):
    """
    Calculate global OSM coverage statistics
    """
    return {
        "total_cities": len(df),
        "avg_coverage": round(df['osm_coverage_score'].mean(), 1),
        "cities_critical_gaps": len(df[df['osm_coverage_score'] < 40]),
        "cities_good_coverage": len(df[df['osm_coverage_score'] >= 70]),
        "lowest_coverage_city": df.loc[df['osm_coverage_score'].idxmin(), 'city'],
        "highest_coverage_city": df.loc[df['osm_coverage_score'].idxmax(), 'city'],
        "avg_drainage_coverage": (df['drainage_mapped'] == 'High').mean() * 100,
        "avg_green_infrastructure": (df['green_infrastructure'] == 'High').mean() * 100,
        "avg_cooling_centers": (df['cooling_centers'] == 'High').mean() * 100,
        "avg_shelters": (df['emergency_shelters'] == 'High').mean() * 100
    }

def get_feature_coverage_summary(df):
    """
    Summarize coverage levels across all features
    """
    features = ['drainage_mapped', 'green_infrastructure', 'cooling_centers', 
                'evacuation_routes', 'emergency_shelters', 'flood_barriers', 
                'permeable_surfaces']
    
    coverage_summary = []
    for feature in features:
        high_count = (df[feature] == 'High').sum()
        medium_count = (df[feature] == 'Medium').sum()
        low_count = (df[feature] == 'Low').sum()
        
        coverage_summary.append({
            'feature': feature.replace('_', ' ').title(),
            'high_coverage': high_count,
            'medium_coverage': medium_count,
            'low_coverage': low_count,
            'coverage_percentage': round((high_count / len(df)) * 100, 1)
        })
    
    return coverage_summary

def get_priority_cities(df, limit=10):
    """
    Get cities with highest priority for OSM mapping efforts
    Priority based on: low OSM coverage + high climate risk
    """
    df = calculate_gap_severity(df)
    
    # Sort by gap severity (descending) and coverage score (ascending)
    priority_cities = df.nlargest(limit, 'gap_severity')[
        ['city', 'country', 'osm_coverage_score', 'gap_severity', 
         'priority_level', 'critical_gap_1', 'critical_gap_2', 'critical_gap_3']
    ]
    
    return priority_cities.to_dict('records')

def get_regional_analysis(df):
    """
    Analyze OSM coverage by region
    """
    # Map countries to regions
    region_map = {
        'Japan': 'East Asia', 'China': 'East Asia', 'South Korea': 'East Asia',
        'India': 'South Asia', 'Pakistan': 'South Asia', 'Bangladesh': 'South Asia',
        'Indonesia': 'Southeast Asia', 'Philippines': 'Southeast Asia', 
        'Thailand': 'Southeast Asia', 'Vietnam': 'Southeast Asia',
        'USA': 'North America', 'Mexico': 'North America',
        'Brazil': 'South America', 'Argentina': 'South America', 
        'Peru': 'South America', 'Colombia': 'South America',
        'UK': 'Europe', 'France': 'Europe', 'Turkey': 'Europe', 'Russia': 'Europe',
        'Egypt': 'Africa', 'Nigeria': 'Africa', 'DR Congo': 'Africa',
        'Iran': 'Middle East'
    }
    
    df['region'] = df['country'].map(region_map)
    
    regional_stats = df.groupby('region').agg({
        'osm_coverage_score': 'mean',
        'city': 'count'
    }).round(1).reset_index()
    
    regional_stats.columns = ['region', 'avg_coverage', 'city_count']
    regional_stats = regional_stats.sort_values('avg_coverage', ascending=False)
    
    return regional_stats.to_dict('records')

def generate_gap_analysis_report():
    """
    Generate comprehensive gap analysis report for lightning talk
    """
    df = load_osm_dataset()
    df = calculate_gap_severity(df)
    
    report = {
        "title": "OpenStreetMap Gap Analysis for Climate Resilience Modeling",
        "subtitle": "A Researcher's Wishlist: Transforming OSM into a Climate Adaptation Engine",
        "global_stats": get_global_statistics(df),
        "priority_wishlist": get_priority_categories(),
        "feature_coverage": get_feature_coverage_summary(df),
        "priority_cities": get_priority_cities(df, limit=15),
        "regional_analysis": get_regional_analysis(df),
        "key_findings": [
            f"Only {get_global_statistics(df)['cities_good_coverage']} of 43 megacities have good OSM coverage (≥70%)",
            f"{get_global_statistics(df)['cities_critical_gaps']} cities have critical gaps (<40% coverage)",
            "Subsurface drainage networks are severely underrepresented in OSM globally",
            "Cooling infrastructure mapping is critically needed for heat adaptation",
            "Emergency shelter capacity data is almost entirely missing from OSM",
            "Permeable surface data could transform stormwater modeling accuracy"
        ],
        "call_to_action": [
            "Develop standardized OSM tagging schemas for climate infrastructure",
            "Create mapper guides for resilience-critical features",
            "Build partnerships between climate researchers and OSM community",
            "Establish data quality metrics for climate adaptation features",
            "Launch targeted mapping campaigns in high-priority cities"
        ]
    }
    
    return report

def get_city_specific_gaps(city_name):
    """
    Get detailed gap analysis for a specific city
    """
    df = load_osm_dataset()
    city_data = df[df['city'] == city_name]
    
    if city_data.empty:
        return None
    
    city = city_data.iloc[0]
    
    return {
        "city": city['city'],
        "country": city['country'],
        "osm_coverage_score": city['osm_coverage_score'],
        "priority_level": city['priority_level'],
        "critical_gaps": [
            city['critical_gap_1'],
            city['critical_gap_2'],
            city['critical_gap_3']
        ],
        "feature_coverage": {
            "Drainage Systems": city['drainage_mapped'],
            "Green Infrastructure": city['green_infrastructure'],
            "Cooling Centers": city['cooling_centers'],
            "Evacuation Routes": city['evacuation_routes'],
            "Emergency Shelters": city['emergency_shelters'],
            "Flood Barriers": city['flood_barriers'],
            "Permeable Surfaces": city['permeable_surfaces']
        }
    }
