"""
Visualization Module for Statistical Analysis
Generates interactive charts using Plotly
"""

import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json

def create_correlation_heatmap(correlation_matrix):
    """
    Create an interactive correlation heatmap
    """
    df_corr = pd.DataFrame(correlation_matrix)
    
    fig = go.Figure(data=go.Heatmap(
        z=df_corr.values,
        x=df_corr.columns,
        y=df_corr.columns,
        colorscale='RdBu',
        zmid=0,
        text=df_corr.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title='Correlation Matrix: Climate Resilience Factors',
        xaxis_title='Variables',
        yaxis_title='Variables',
        height=600,
        width=800
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_regression_coefficients_chart(coefficients):
    """
    Create a bar chart showing regression coefficients
    """
    df = pd.DataFrame(coefficients)
    
    # Color code by impact
    colors = ['green' if x == 'Positive' else 'red' for x in df['impact']]
    
    fig = go.Figure(data=[
        go.Bar(
            x=df['coefficient'],
            y=df['variable'],
            orientation='h',
            marker_color=colors,
            text=df['coefficient'].round(3),
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title='Regression Coefficients: Impact on Resilience Score',
        xaxis_title='Coefficient Value',
        yaxis_title='Predictor Variables',
        height=400,
        showlegend=False
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_resilience_distribution(df):
    """
    Create a histogram of resilience scores
    """
    fig = px.histogram(
        df,
        x='resilience_score',
        nbins=15,
        title='Distribution of Resilience Scores Across 43 Megacities',
        labels={'resilience_score': 'Resilience Score'},
        color_discrete_sequence=['#3498db']
    )
    
    fig.update_layout(
        xaxis_title='Resilience Score',
        yaxis_title='Number of Cities',
        showlegend=False
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_regional_comparison(regional_data):
    """
    Create a bar chart comparing resilience by region
    """
    regions = list(regional_data.keys())
    means = [regional_data[r]['mean'] for r in regions]
    
    df = pd.DataFrame({
        'region': regions,
        'avg_resilience': means
    })
    
    fig = px.bar(
        df,
        x='region',
        y='avg_resilience',
        title='Average Resilience Score by Region',
        labels={'avg_resilience': 'Average Resilience Score', 'region': 'Region'},
        color='avg_resilience',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis_title='Region',
        yaxis_title='Average Resilience Score',
        showlegend=False
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_risk_comparison(df):
    """
    Create a stacked bar chart comparing different risk types
    """
    # Count high risks by type
    risk_counts = {
        'Flood Risk': len(df[df['flood_risk'] == 'High']),
        'Heat Risk': len(df[df['heat_risk'] == 'High']),
        'Drought Risk': len(df[df['drought_risk'] == 'High']),
        'Sea Level Rise': len(df[df['sea_level_rise_risk'] == 'High'])
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=list(risk_counts.keys()),
            y=list(risk_counts.values()),
            marker_color=['#3498db', '#e74c3c', '#f39c12', '#9b59b6'],
            text=list(risk_counts.values()),
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title='Number of Cities Facing High Climate Risks',
        xaxis_title='Risk Type',
        yaxis_title='Number of Cities',
        showlegend=False,
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_adaptation_plan_comparison(with_plan, without_plan):
    """
    Create a comparison chart for cities with/without adaptation plans
    """
    fig = go.Figure(data=[
        go.Bar(
            x=['With Adaptation Plan', 'Without Adaptation Plan'],
            y=[with_plan, without_plan],
            marker_color=['#27ae60', '#e74c3c'],
            text=[round(with_plan, 2), round(without_plan, 2)],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title='Average Resilience Score: Impact of Adaptation Plans',
        xaxis_title='',
        yaxis_title='Average Resilience Score',
        showlegend=False,
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_scatter_gdp_resilience(df):
    """
    Create a scatter plot showing GDP vs Resilience
    """
    fig = px.scatter(
        df,
        x='gdp_per_capita',
        y='resilience_score',
        size='population_millions',
        color='region',
        hover_name='city',
        title='GDP per Capita vs Resilience Score',
        labels={
            'gdp_per_capita': 'GDP per Capita (USD)',
            'resilience_score': 'Resilience Score'
        }
    )
    
    fig.update_layout(height=500)
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def generate_all_visualizations(df, analysis_results):
    """
    Generate all visualizations and return as JSON strings
    """
    return {
        'correlation_heatmap': create_correlation_heatmap(
            analysis_results['correlation_analysis']['correlation_matrix']
        ),
        'regression_coefficients': create_regression_coefficients_chart(
            analysis_results['regression_analysis']['coefficients']
        ),
        'resilience_distribution': create_resilience_distribution(df),
        'regional_comparison': create_regional_comparison(
            analysis_results['resilience_factors']['regional_resilience']
        ),
        'risk_comparison': create_risk_comparison(df),
        'adaptation_plan_impact': create_adaptation_plan_comparison(
            analysis_results['resilience_factors']['adaptation_plan_impact']['with_plan'],
            analysis_results['resilience_factors']['adaptation_plan_impact']['without_plan']
        ),
        'gdp_resilience_scatter': create_scatter_gdp_resilience(df)
    }
