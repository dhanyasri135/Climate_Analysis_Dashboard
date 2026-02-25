"""
Statistical Analysis Module for Climate Adaptation Research
Performs Chi-square tests, Cramer's V, correlation analysis, and regression modeling
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import chi2_contingency
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import os

# Get the path to the data directory
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'megacities_dataset.csv')

def load_dataset():
    """Load the megacities dataset"""
    return pd.read_csv(DATA_PATH)

def cramers_v(confusion_matrix):
    """
    Calculate Cramer's V statistic for categorical association
    """
    chi2 = stats.chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum()
    min_dim = min(confusion_matrix.shape) - 1
    return np.sqrt(chi2 / (n * min_dim))

def chi_square_test(df, var1, var2):
    """
    Perform Chi-square test between two categorical variables
    Returns test statistic, p-value, and Cramer's V
    """
    contingency_table = pd.crosstab(df[var1], df[var2])
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)
    cramers = cramers_v(contingency_table.values)
    
    return {
        'chi2_statistic': round(chi2, 4),
        'p_value': round(p_value, 4),
        'degrees_of_freedom': dof,
        'cramers_v': round(cramers, 4),
        'significant': p_value < 0.05,
        'contingency_table': contingency_table.to_dict()
    }

def correlation_analysis(df, variables=None):
    """
    Perform correlation analysis on numerical variables
    """
    if variables is None:
        # Select numeric columns
        numeric_df = df.select_dtypes(include=[np.number])
    else:
        numeric_df = df[variables]
    
    correlation_matrix = numeric_df.corr()
    
    # Find significant correlations (|r| > 0.5)
    significant_corr = []
    for i in range(len(correlation_matrix.columns)):
        for j in range(i+1, len(correlation_matrix.columns)):
            corr_value = correlation_matrix.iloc[i, j]
            if abs(corr_value) > 0.5:
                significant_corr.append({
                    'var1': correlation_matrix.columns[i],
                    'var2': correlation_matrix.columns[j],
                    'correlation': round(corr_value, 4),
                    'strength': 'Strong' if abs(corr_value) > 0.7 else 'Moderate'
                })
    
    return {
        'correlation_matrix': correlation_matrix.round(3).to_dict(),
        'significant_correlations': significant_corr
    }

def regression_analysis(df, target_var='resilience_score', predictor_vars=None):
    """
    Perform multiple linear regression analysis
    """
    if predictor_vars is None:
        # Use key numeric predictors only
        predictor_vars = [
            'population_millions', 'gdp_per_capita'
        ]
    
    # Prepare data - select only numeric columns
    X = df[predictor_vars].copy()
    y = df[target_var].copy()
    
    # Encode categorical variables if needed
    categorical_mapping = {
        'Low': 1,
        'Medium': 2,
        'High': 3
    }
    
    # Add encoded categorical features
    if 'infrastructure_vulnerability' in df.columns:
        X['infra_vuln_encoded'] = df['infrastructure_vulnerability'].map(categorical_mapping)
    if 'financial_capacity' in df.columns:
        X['financial_cap_encoded'] = df['financial_capacity'].map(categorical_mapping)
    if 'stakeholder_engagement' in df.columns:
        X['stakeholder_eng_encoded'] = df['stakeholder_engagement'].map(categorical_mapping)
    
    # Handle any missing values
    X = X.fillna(X.mean())
    y = y.fillna(y.mean())
    
    # Fit model
    model = LinearRegression()
    model.fit(X, y)
    
    # Calculate R-squared
    r_squared = model.score(X, y)
    
    # Get coefficients
    coefficients = []
    for var, coef in zip(X.columns, model.coef_):
        coefficients.append({
            'variable': var,
            'coefficient': round(coef, 4),
            'impact': 'Positive' if coef > 0 else 'Negative'
        })
    
    # Sort by absolute coefficient value
    coefficients.sort(key=lambda x: abs(x['coefficient']), reverse=True)
    
    return {
        'target_variable': target_var,
        'r_squared': round(r_squared, 4),
        'intercept': round(model.intercept_, 4),
        'coefficients': coefficients,
        'model_quality': 'Good' if r_squared > 0.7 else 'Moderate' if r_squared > 0.5 else 'Weak'
    }

def categorical_analysis(df):
    """
    Analyze relationships between categorical variables
    """
    # Test relationship between climate zone and adaptation plan existence
    test1 = chi_square_test(df, 'climate_zone', 'adaptation_plan_exists')
    
    # Test relationship between coastal location and flood risk
    test2 = chi_square_test(df, 'coastal', 'flood_risk')
    
    # Test relationship between region and heat risk
    test3 = chi_square_test(df, 'region', 'heat_risk')
    
    return {
        'climate_zone_vs_adaptation_plan': test1,
        'coastal_vs_flood_risk': test2,
        'region_vs_heat_risk': test3
    }

def resilience_factors_analysis(df):
    """
    Analyze factors affecting resilience scores
    """
    # Group by adaptation plan existence
    with_plan = df[df['adaptation_plan_exists'] == 'Yes']['resilience_score'].mean()
    without_plan = df[df['adaptation_plan_exists'] == 'No']['resilience_score'].mean()
    
    # Group by region
    regional_resilience = df.groupby('region')['resilience_score'].agg(['mean', 'std', 'count'])
    
    # Group by climate zone
    climate_resilience = df.groupby('climate_zone')['resilience_score'].agg(['mean', 'std', 'count'])
    
    return {
        'adaptation_plan_impact': {
            'with_plan': round(with_plan, 2),
            'without_plan': round(without_plan, 2),
            'difference': round(with_plan - without_plan, 2)
        },
        'regional_resilience': regional_resilience.round(2).to_dict('index'),
        'climate_resilience': climate_resilience.round(2).to_dict('index')
    }

def get_summary_statistics(df):
    """
    Get summary statistics for the dataset
    """
    return {
        'total_cities': len(df),
        'cities_with_plans': int(df[df['adaptation_plan_exists'] == 'Yes'].shape[0]),
        'cities_without_plans': int(df[df['adaptation_plan_exists'] == 'No'].shape[0]),
        'avg_resilience_score': round(df['resilience_score'].mean(), 2),
        'avg_population': round(df['population_millions'].mean(), 2),
        'coastal_cities': int(df[df['coastal'] == 'Yes'].shape[0]),
        'high_flood_risk': int(df[df['flood_risk'] == 'High'].shape[0]),
        'high_heat_risk': int(df[df['heat_risk'] == 'High'].shape[0])
    }

def run_full_analysis():
    """
    Run complete statistical analysis pipeline
    """
    df = load_dataset()
    
    return {
        'summary_stats': get_summary_statistics(df),
        'correlation_analysis': correlation_analysis(df),
        'regression_analysis': regression_analysis(df),
        'categorical_analysis': categorical_analysis(df),
        'resilience_factors': resilience_factors_analysis(df)
    }

if __name__ == "__main__":
    # Test the module
    results = run_full_analysis()
    print("Statistical Analysis Complete!")
    print(f"Total Cities: {results['summary_stats']['total_cities']}")
    print(f"Average Resilience Score: {results['summary_stats']['avg_resilience_score']}")
    print(f"Regression R²: {results['regression_analysis']['r_squared']}")
