"""
Load and parse the megacity analysis codebook.

This module provides utilities to load city climate adaptation data from:
1. Multipass chunked dataset (megacity_multipass_dataset.csv) - PRIMARY
   Contains chunks from 43 documents with 61 binary indicator columns
2. Legacy Excel file (Megacity_CodeForAnalysis_v4.xlsx) - FALLBACK
   Contains manually coded 43 megacities with aggregated indicators

The multipass dataset breaks each document into chunks for more granular analysis.
"""

import pandas as pd
import os

CODEBOOK_PATH = os.path.join(os.path.dirname(__file__), '..', 'Megacity_CodeForAnalysis_v4.xlsx')
MULTIPASS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data_exports', 'megacity_multipass_dataset.csv')


def load_codebook():
    """
    Load the manually-coded megacity analysis dataset from Excel.
    
    Returns:
        DataFrame with 43 cities and 52 binary indicator columns.
    """
    if not os.path.exists(CODEBOOK_PATH):
        raise FileNotFoundError(f"Codebook not found: {CODEBOOK_PATH}")
    
    df = pd.read_excel(CODEBOOK_PATH, sheet_name='Main sheet')
    
    # Set city as index if needed
    if 'City' in df.columns:
        df = df.rename(columns={'City': 'city'})
    
    return df


def get_codebook_metadata():
    """
    Get the legend/metadata explaining column definitions.
    
    Returns:
        DataFrame with codebook legend.
    """
    if not os.path.exists(CODEBOOK_PATH):
        raise FileNotFoundError(f"Codebook not found: {CODEBOOK_PATH}")
    
    legend = pd.read_excel(CODEBOOK_PATH, sheet_name='Legend')
    return legend


def get_column_groups():
    """
    Return organized column groups by category.
    
    Returns:
        Dictionary mapping category names to lists of column names.
    """
    df = load_codebook()
    columns = list(df.columns)
    
    groups = {
        'region': [col for col in columns if col.startswith('Reg_')],
        'planning': [col for col in columns if col.startswith('Plan_')],
        'infrastructure': [col for col in columns if col.startswith('Infra_')],
        'climate_risks': [col for col in columns if col.startswith('CR_')],
        'finance': [col for col in columns if col.startswith('Fin_')],
        'stakeholders': [col for col in columns if col.startswith('SH')],
    }
    
    return groups


def get_city_profile(city_name):
    """
    Get all coded indicators for a specific city.
    
    Args:
        city_name: Name of the city
    
    Returns:
        Dictionary with city's coded indicators.
    """
    df = load_codebook()
    
    city_rows = df[df['city'].str.lower() == city_name.lower()]
    if city_rows.empty:
        raise ValueError(f"City not found: {city_name}")
    
    row = city_rows.iloc[0]
    
    groups = get_column_groups()
    profile = {
        'city': row['city'],
        'categories': {}
    }
    
    for group_name, cols in groups.items():
        profile['categories'][group_name] = {
            col: bool(row[col]) for col in cols if col in row.index
        }
    
    return profile


# ============================================================================
# MULTIPASS DATASET FUNCTIONS (Primary data source)
# ============================================================================

def load_multipass_dataset():
    """
    Load the multipass chunked dataset from CSV.
    
    Returns:
        DataFrame with 13,836+ rows (chunks) from 42 cities, 61 indicator columns.
    """
    if not os.path.exists(MULTIPASS_PATH):
        raise FileNotFoundError(f"Multipass dataset not found: {MULTIPASS_PATH}")
    
    df = pd.read_csv(MULTIPASS_PATH)
    return df


def get_cities_from_multipass():
    """
    Get list of unique cities from multipass dataset.
    
    Returns:
        Sorted list of city names.
    """
    df = load_multipass_dataset()
    cities = sorted(df['city'].unique().tolist())
    return cities


def analyze_city_features(city_name):
    """
    Analyze which features are present for a specific city in multipass dataset.
    Aggregates across all chunks for that city.
    
    Args:
        city_name: Name of the city
    
    Returns:
        Dictionary with city analysis and feature presence/counts.
    """
    df = load_multipass_dataset()
    
    # Find city (case-insensitive)
    city_data = df[df['city'].str.lower() == city_name.lower()]
    if city_data.empty:
        raise ValueError(f"City not found: {city_name}")
    
    # Define feature categories with their columns
    feature_categories = {
        'region': {
            'label': '🌍 Regions',
            'columns': ['Reg_Africa', 'Reg_East asia', 'Reg_Europe', 'Reg_middle east', 
                       'Reg_North America', 'Reg_South America', 'Reg_South Asia']
        },
        'planning': {
            'label': '📋 Planning Types',
            'columns': ['Plan_Adaptation', 'Plan_A&M', 'Plan_Mitigation', 'Plan_Yes', 'Plan_No']
        },
        'infrastructure': {
            'label': '🏗️ Infrastructure',
            'columns': ['Infra_Elec_Grid', 'Infra_DWT', 'Infra_WWT', 'Infra_T_PT', 'Infra_EV',
                       'Infra_C/H', 'Infra_Green', 'Infra_WM', 'Infra_BU', 'Infra_other']
        },
        'climate_risks': {
            'label': '⚠️ Climate Risks',
            'columns': ['CR_SLR', 'CR_Dr', 'CR_PV', 'CR_IFIH', 'CR_EPIF', 'CR_AirPol',
                       'CR_WaterPol', 'CR_Pol', 'CR_UHI', 'CR_Other']
        },
        'natural_disasters': {
            'label': '🌊 Natural Disasters',
            'columns': ['ND_EQ', 'ND_HC', 'ND_Dr', 'ND_F/ER', 'ND_Other Hazards']
        },
        'finance': {
            'label': '💰 Finance Sources',
            'columns': ['Fin_NG', 'Fin_SNG', 'Fin_LG', 'Fin_PSC', 'Fin_C/N', 'Fin_I/P',
                       'Fin_In_N/G', 'Fin_Other']
        },
        'stakeholders': {
            'label': '👥 Stakeholders',
            'columns': ['SH_NG', 'SH_SNG', 'SH_LG', 'SH_PSC', 'SH_C/N-I', 'SH_C/N-L/S',
                       'SH_I/C', 'SH_I-N/G', 'SH-A/S', 'SH_Other']
        }
    }
    
    # Column to label mapping
    column_labels = {
        'Reg_Africa': 'Africa',
        'Reg_East asia': 'East Asia',
        'Reg_Europe': 'Europe',
        'Reg_middle east': 'Middle East',
        'Reg_North America': 'North America',
        'Reg_South America': 'South America',
        'Reg_South Asia': 'South Asia',
        
        'Plan_Adaptation': 'Adaptation Planning',
        'Plan_A&M': 'Adaptation & Mitigation',
        'Plan_Mitigation': 'Mitigation Planning',
        'Plan_Yes': 'Planning Present',
        'Plan_No': 'No Planning',
        
        'Infra_Elec_Grid': 'Electrical Grid',
        'Infra_DWT': 'Drinking Water Treatment',
        'Infra_WWT': 'Wastewater Treatment',
        'Infra_T_PT': 'Transport/Public Transit',
        'Infra_EV': 'Electric Vehicles',
        'Infra_C/H': 'Cooling/Heating',
        'Infra_Green': 'Green Infrastructure',
        'Infra_WM': 'Water Management',
        'Infra_BU': 'Building Upgrades',
        'Infra_other': 'Other Infrastructure',
        
        'CR_SLR': 'Sea Level Rise',
        'CR_Dr': 'Drought',
        'CR_PV': 'Precipitation Variability',
        'CR_IFIH': 'Inland Flooding/Inundation',
        'CR_EPIF': 'Extreme Precipitation/Flooding',
        'CR_AirPol': 'Air Pollution',
        'CR_WaterPol': 'Water Pollution',
        'CR_Pol': 'Pollution',
        'CR_UHI': 'Urban Heat Island',
        'CR_Other': 'Other Climate Risks',
        
        'ND_EQ': 'Earthquakes',
        'ND_HC': 'Heat Catastrophes',
        'ND_Dr': 'Drought',
        'ND_F/ER': 'Floods/Erosion',
        'ND_Other Hazards': 'Other Hazards',
        
        'Fin_NG': 'National Government',
        'Fin_SNG': 'Subnational Government',
        'Fin_LG': 'Local Government',
        'Fin_PSC': 'Public-Private Contracts',
        'Fin_C/N': 'Corporate/NGO',
        'Fin_I/P': 'International/Public',
        'Fin_In_N/G': 'Infrastructure/Nature-based',
        'Fin_Other': 'Other Funding',
        
        'SH_NG': 'National Government',
        'SH_SNG': 'Subnational Government',
        'SH_LG': 'Local Government',
        'SH_PSC': 'Public-Private Collaboration',
        'SH_C/N-I': 'Corporate/NGO-International',
        'SH_C/N-L/S': 'Corporate/NGO-Local/Sub',
        'SH_I/C': 'International/Community',
        'SH_I-N/G': 'International-NGO',
        'SH-A/S': 'Academia/Scientific',
        'SH_Other': 'Other Stakeholders'
    }
    
    # Build result
    result = {
        'city': city_name,
        'total_chunks': int(len(city_data)),
        'categories': {}
    }
    
    # Analyze each category
    for category_key, category_info in feature_categories.items():
        category_result = {
            'label': category_info['label'],
            'items': {}
        }
        
        for col in category_info['columns']:
            if col in city_data.columns:
                # Count how many chunks have this feature
                present_count = int((city_data[col] == 1).sum())
                total_count = int(len(city_data))
                presence_pct = (present_count / total_count * 100) if total_count > 0 else 0.0
                
                category_result['items'][col] = {
                    'label': column_labels.get(col, col),
                    'present': present_count > 0,
                    'count': present_count,
                    'percentage': round(presence_pct, 1),
                    'total': total_count
                }
        
        result['categories'][category_key] = category_result
    
    return result

