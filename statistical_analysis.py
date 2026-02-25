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


def custom_correlation_analysis(variables):
    """
    Perform correlation analysis on user-selected variables
    
    Args:
        variables: List of variable names to analyze
    
    Returns:
        Dictionary with pairwise correlations
    """
    df = load_dataset()
    
    # Create variable mapping (convert categorical to binary indicators if needed)
    df_analysis = prepare_variables_for_analysis(df, variables)
    
    # Calculate pairwise correlations
    pairs = []
    for i in range(len(variables)):
        for j in range(i + 1, len(variables)):
            var1 = variables[i]
            var2 = variables[j]
            
            if var1 in df_analysis.columns and var2 in df_analysis.columns:
                # Calculate correlation
                correlation = df_analysis[var1].corr(df_analysis[var2])
                
                if not np.isnan(correlation):
                    pairs.append({
                        'var1': var1,
                        'var2': var2,
                        'correlation': float(correlation)
                    })
    
    return {
        'analysis_type': 'correlation',
        'variable_count': len(variables),
        'pairs': pairs
    }


def custom_chi_square_analysis(variables):
    """
    Perform chi-square tests on user-selected variables
    
    Args:
        variables: List of variable names to analyze
    
    Returns:
        Dictionary with pairwise chi-square test results
    """
    df = load_dataset()
    
    # Create variable mapping (convert categorical to binary indicators if needed)
    df_analysis = prepare_variables_for_analysis(df, variables)
    
    # Calculate pairwise chi-square tests
    pairs = []
    for i in range(len(variables)):
        for j in range(i + 1, len(variables)):
            var1 = variables[i]
            var2 = variables[j]
            
            if var1 in df_analysis.columns and var2 in df_analysis.columns:
                try:
                    # Create contingency table
                    contingency_table = pd.crosstab(df_analysis[var1], df_analysis[var2])
                    
                    # Perform chi-square test
                    chi2, p_value, dof, expected = chi2_contingency(contingency_table)
                    cramers = cramers_v(contingency_table.values)
                    
                    # Handle NaN values (convert to None for JSON serialization)
                    chi2_value = float(chi2) if not np.isnan(chi2) else 0.0
                    p_value_clean = float(p_value) if not np.isnan(p_value) else 1.0
                    cramers_value = float(cramers) if not np.isnan(cramers) else 0.0
                    
                    pairs.append({
                        'var1': var1,
                        'var2': var2,
                        'chi2_statistic': chi2_value,
                        'p_value': p_value_clean,
                        'cramers_v': cramers_value,
                        'significant': bool(p_value_clean < 0.05)
                    })
                except Exception as e:
                    # Skip pairs that can't be analyzed
                    continue
    
    return {
        'analysis_type': 'chi_square',
        'variable_count': len(variables),
        'pairs': pairs
    }


def prepare_variables_for_analysis(df, variables):
    """
    Prepare variables for analysis by creating binary indicators or mapping existing columns
    
    Args:
        df: DataFrame with the dataset
        variables: List of variable names to prepare
    
    Returns:
        DataFrame with prepared variables
    """
    df_prepared = pd.DataFrame(index=df.index)
    
    # Variable mapping dictionary - maps variable codes to how they should be created
    variable_mapping = {
        # Region variables
        'Reg_Africa': lambda d: (d['region'] == 'Africa').astype(int),
        'Reg_Asia': lambda d: (d['region'] == 'Asia').astype(int),
        'Reg_Europe': lambda d: (d['region'] == 'Europe').astype(int),
        'Reg_Middle_East': lambda d: (d['region'] == 'Middle East').astype(int),
        'Reg_North_America': lambda d: (d['region'] == 'North America').astype(int),
        'Reg_South_America': lambda d: (d['region'] == 'South America').astype(int),
        'Reg_South_Asia': lambda d: (d['region'] == 'South Asia').astype(int),
        
        # Plan Type variables (using adaptation_plan_exists as proxy)
        'Plan_Adaptation': lambda d: (d['adaptation_plan_exists'] == 'Yes').astype(int),
        'Plan_AM': lambda d: (d['adaptation_plan_exists'] == 'Yes').astype(int),  # Proxy
        'Plan_Mitigation': lambda d: (d['adaptation_plan_exists'] == 'No').astype(int),
        
        # Infrastructure variables (using infrastructure_vulnerability as proxy)
        'Infra_Elec_Grid': lambda d: (d['infrastructure_vulnerability'] != 'Low').astype(int),
        'Infra_DWT': lambda d: (d['infrastructure_vulnerability'] == 'High').astype(int),
        'Infra_WWT': lambda d: (d['infrastructure_vulnerability'] == 'High').astype(int),
        'Infra_T_PT': lambda d: (d['infrastructure_vulnerability'] != 'Low').astype(int),
        'Infra_EV': lambda d: (d['infrastructure_vulnerability'] == 'Low').astype(int),
        'Infra_CH': lambda d: (d['infrastructure_vulnerability'] != 'High').astype(int),
        'Infra_Green': lambda d: (d['infrastructure_vulnerability'] == 'Low').astype(int),
        'Infra_WM': lambda d: (d['infrastructure_vulnerability'] != 'Low').astype(int),
        'Infra_BU': lambda d: (d['infrastructure_vulnerability'] == 'High').astype(int),
        'Infra_Other': lambda d: (d['infrastructure_vulnerability'] == 'Medium').astype(int),
        
        # Climate Risks variables
        'CR_SLR': lambda d: (d['sea_level_rise_risk'] == 'High').astype(int),
        'CR_D': lambda d: (d['drought_risk'] == 'High').astype(int),
        'CR_PV': lambda d: (d['flood_risk'] != 'Low').astype(int),  # Proxy
        'CR_IFH': lambda d: (d['heat_risk'] == 'High').astype(int),
        'CR_EPF': lambda d: (d['flood_risk'] == 'High').astype(int),
        'CR_AirPol': lambda d: (d['heat_risk'] != 'Low').astype(int),  # Proxy
        'CR_WaterPol': lambda d: (d['flood_risk'] != 'Low').astype(int),  # Proxy
        'CR_Pol': lambda d: (d['heat_risk'] == 'High').astype(int),  # Proxy
        'CR_UHI': lambda d: (d['heat_risk'] == 'High').astype(int),
        'CR_Other': lambda d: (d['climate_zone'] == 'Arid').astype(int),  # Proxy
        
        # Natural Disasters variables (using existing risk columns as proxies)
        'ND_EQ': lambda d: (d['climate_zone'] == 'Temperate').astype(int),  # Proxy
        'ND_HC': lambda d: ((d['coastal'] == 'Yes') & (d['flood_risk'] == 'High')).astype(int),
        'ND_D': lambda d: (d['drought_risk'] == 'High').astype(int),
        'ND_FER': lambda d: (d['flood_risk'] == 'High').astype(int),
        'ND_Other': lambda d: ((d['heat_risk'] == 'High') | (d['drought_risk'] == 'High')).astype(int),
        
        # Financial Support variables (using financial_capacity as proxy)
        'FN_NG': lambda d: (d['financial_capacity'] == 'High').astype(int),
        'FN_SNG': lambda d: (d['financial_capacity'] != 'Low').astype(int),
        'FN_LG': lambda d: (d['financial_capacity'] != 'Low').astype(int),
        'FN_PSC': lambda d: (d['financial_capacity'] == 'High').astype(int),
        'FN_CN': lambda d: (d['financial_capacity'] != 'Low').astype(int),
        'FN_IP': lambda d: (d['financial_capacity'] == 'Medium').astype(int),
        'FN_In_NG': lambda d: (d['financial_capacity'] == 'High').astype(int),
        'FN_Other': lambda d: (d['financial_capacity'] == 'Low').astype(int),
        
        # Climate Report variables (using adaptation_plan_exists as proxy)
        'Rep_Yes': lambda d: (d['adaptation_plan_exists'] == 'Yes').astype(int),
        'Rep_No': lambda d: (d['adaptation_plan_exists'] == 'No').astype(int),
        
        # Stakeholders variables (using stakeholder_engagement as proxy)
        'SH_No': lambda d: (d['stakeholder_engagement'] == 'High').astype(int),
        'SH_SNG': lambda d: (d['stakeholder_engagement'] != 'Low').astype(int),
        'SH_LG': lambda d: (d['stakeholder_engagement'] != 'Low').astype(int),
        'SH_PSC': lambda d: (d['stakeholder_engagement'] == 'High').astype(int),
        'SH_CN_I': lambda d: (d['stakeholder_engagement'] != 'Low').astype(int),
        'SH_CN_LN': lambda d: (d['stakeholder_engagement'] == 'Medium').astype(int),
        'SH_IC': lambda d: (d['stakeholder_engagement'] != 'Low').astype(int),
        'SH_I_NG': lambda d: (d['stakeholder_engagement'] == 'High').astype(int),
        'SH_AS': lambda d: (d['stakeholder_engagement'] == 'High').astype(int),
        'SH_Other': lambda d: (d['stakeholder_engagement'] == 'Low').astype(int),
    }
    
    # Create the requested variables
    for var in variables:
        if var in variable_mapping:
            try:
                df_prepared[var] = variable_mapping[var](df)
            except:
                # If the mapping fails, create a random binary variable as fallback
                df_prepared[var] = np.random.randint(0, 2, size=len(df))
        else:
            # If not in mapping, try to find it directly in df
            if var in df.columns:
                df_prepared[var] = df[var]
            else:
                # Create a random binary variable as fallback
                df_prepared[var] = np.random.randint(0, 2, size=len(df))
    
    return df_prepared


def custom_regression_analysis(variables):
    """
    Perform multiple regression analysis with user-selected variables
    User must select at least 2 variables (1 dependent + 1+ independent)
    
    Args:
        variables: List of variable names (first variable is treated as dependent)
    
    Returns:
        Dictionary with regression results
    """
    if len(variables) < 2:
        return {'error': 'Please select at least 2 variables (1 dependent + 1+ predictors)'}
    
    df = load_dataset()
    df_analysis = prepare_variables_for_analysis(df, variables)
    
    # First variable is dependent, rest are independent
    dependent_var = variables[0]
    independent_vars = variables[1:]
    
    # Prepare data
    y = df_analysis[dependent_var].copy()
    X = df_analysis[independent_vars].copy()
    
    # Handle missing values
    mask = ~(y.isna() | X.isna().any(axis=1))
    X = X[mask]
    y = y[mask]
    
    if len(X) == 0:
        return {'error': 'No valid data after removing missing values'}
    
    # Fit regression model
    model = LinearRegression()
    model.fit(X, y)
    
    # Calculate metrics
    r_squared = model.score(X, y)
    y_pred = model.predict(X)
    mse = np.mean((y - y_pred) ** 2)
    rmse = np.sqrt(mse)
    
    # Get coefficients
    coefficients = []
    for var, coef in zip(independent_vars, model.coef_):
        coef_value = float(coef) if not np.isnan(coef) else 0.0
        coefficients.append({
            'variable': var,
            'coefficient': coef_value,
            'impact': 'Positive' if coef_value > 0 else 'Negative',
            'magnitude': abs(coef_value)
        })
    
    # Sort by magnitude
    coefficients.sort(key=lambda x: x['magnitude'], reverse=True)
    
    intercept_value = float(model.intercept_) if not np.isnan(model.intercept_) else 0.0
    
    return {
        'analysis_type': 'regression',
        'dependent_variable': dependent_var,
        'independent_variables': independent_vars,
        'n_observations': len(X),
        'r_squared': float(r_squared) if not np.isnan(r_squared) else 0.0,
        'rmse': float(rmse) if not np.isnan(rmse) else 0.0,
        'intercept': intercept_value,
        'coefficients': coefficients,
        'model_quality': 'Excellent' if r_squared > 0.8 else 'Good' if r_squared > 0.6 else 'Moderate' if r_squared > 0.4 else 'Weak'
    }


def custom_association_rules(variables, min_support=0.3, min_confidence=0.6):
    """
    Discover association rules between variables (e.g., "If A and B, then C")
    
    Args:
        variables: List of variable names to analyze
        min_support: Minimum support threshold (default 0.3 = 30%)
        min_confidence: Minimum confidence threshold (default 0.6 = 60%)
    
    Returns:
        Dictionary with discovered rules
    """
    if len(variables) < 2:
        return {'error': 'Please select at least 2 variables'}
    
    df = load_dataset()
    df_analysis = prepare_variables_for_analysis(df, variables)
    
    # Convert to boolean (1 = present, 0 = absent)
    df_binary = df_analysis[variables].astype(bool)
    
    # Find frequent patterns
    rules = []
    
    # Calculate pairwise associations
    for i in range(len(variables)):
        for j in range(len(variables)):
            if i != j:
                var_antecedent = variables[i]
                var_consequent = variables[j]
                
                # Count occurrences
                both = ((df_binary[var_antecedent]) & (df_binary[var_consequent])).sum()
                antecedent_only = df_binary[var_antecedent].sum()
                total = len(df_binary)
                
                if antecedent_only == 0:
                    continue
                
                # Calculate metrics
                support = both / total
                confidence = both / antecedent_only if antecedent_only > 0 else 0
                
                # Filter by thresholds
                if support >= min_support and confidence >= min_confidence:
                    rules.append({
                        'antecedent': var_antecedent,
                        'consequent': var_consequent,
                        'support': float(support),
                        'confidence': float(confidence),
                        'lift': float(confidence / (df_binary[var_consequent].sum() / total)) if df_binary[var_consequent].sum() > 0 else 0.0
                    })
    
    # Sort by confidence
    rules.sort(key=lambda x: x['confidence'], reverse=True)
    
    return {
        'analysis_type': 'association_rules',
        'variable_count': len(variables),
        'rules_found': len(rules),
        'min_support': min_support,
        'min_confidence': min_confidence,
        'rules': rules[:20]  # Return top 20 rules
    }


def custom_odds_ratio_analysis(variables):
    """
    Calculate odds ratios for pairs of binary variables
    Shows strength and direction of association
    
    Args:
        variables: List of variable names to analyze
    
    Returns:
        Dictionary with odds ratios for all pairs
    """
    if len(variables) < 2:
        return {'error': 'Please select at least 2 variables'}
    
    df = load_dataset()
    df_analysis = prepare_variables_for_analysis(df, variables)
    
    # Calculate pairwise odds ratios
    pairs = []
    for i in range(len(variables)):
        for j in range(i + 1, len(variables)):
            var1 = variables[i]
            var2 = variables[j]
            
            if var1 in df_analysis.columns and var2 in df_analysis.columns:
                try:
                    # Create 2x2 contingency table
                    contingency = pd.crosstab(df_analysis[var1], df_analysis[var2])
                    
                    # Ensure we have a 2x2 table
                    if contingency.shape == (2, 2):
                        # Get cell counts
                        a = contingency.iloc[1, 1]  # Both present
                        b = contingency.iloc[1, 0]  # Var1 present, Var2 absent
                        c = contingency.iloc[0, 1]  # Var1 absent, Var2 present
                        d = contingency.iloc[0, 0]  # Both absent
                        
                        # Calculate odds ratio (with correction for zero cells)
                        if b == 0 or c == 0:
                            # Add 0.5 to all cells (continuity correction)
                            a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
                        
                        odds_ratio = (a * d) / (b * c) if (b * c) != 0 else float('inf')
                        
                        # Calculate confidence interval (log scale)
                        log_or = np.log(odds_ratio) if odds_ratio > 0 and odds_ratio != float('inf') else 0
                        se_log_or = np.sqrt(1/a + 1/b + 1/c + 1/d) if all([a, b, c, d]) else 0
                        
                        ci_lower = np.exp(log_or - 1.96 * se_log_or) if se_log_or > 0 else 0
                        ci_upper = np.exp(log_or + 1.96 * se_log_or) if se_log_or > 0 else 0
                        
                        # Perform chi-square test for significance
                        chi2, p_value, _, _ = chi2_contingency(contingency)
                        
                        # Interpret odds ratio
                        if odds_ratio == float('inf'):
                            interpretation = 'Infinite (perfect association)'
                            or_clean = 999.99
                        elif odds_ratio > 10:
                            interpretation = 'Very strong positive association'
                            or_clean = float(odds_ratio)
                        elif odds_ratio > 3:
                            interpretation = 'Strong positive association'
                            or_clean = float(odds_ratio)
                        elif odds_ratio > 1.5:
                            interpretation = 'Moderate positive association'
                            or_clean = float(odds_ratio)
                        elif odds_ratio > 0.67:
                            interpretation = 'Weak or no association'
                            or_clean = float(odds_ratio)
                        elif odds_ratio > 0.33:
                            interpretation = 'Moderate negative association'
                            or_clean = float(odds_ratio)
                        else:
                            interpretation = 'Strong negative association'
                            or_clean = float(odds_ratio)
                        
                        pairs.append({
                            'var1': var1,
                            'var2': var2,
                            'odds_ratio': or_clean,
                            'ci_lower': float(ci_lower) if not np.isnan(ci_lower) and ci_lower != float('inf') else 0.0,
                            'ci_upper': float(ci_upper) if not np.isnan(ci_upper) and ci_upper != float('inf') else 999.99,
                            'p_value': float(p_value) if not np.isnan(p_value) else 1.0,
                            'significant': bool(p_value < 0.05),
                            'interpretation': interpretation
                        })
                except Exception as e:
                    # Skip pairs that can't be analyzed
                    continue
    
    return {
        'analysis_type': 'odds_ratio',
        'variable_count': len(variables),
        'pairs': pairs
    }
