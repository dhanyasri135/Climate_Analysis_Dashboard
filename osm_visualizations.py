"""
OSM Gap Visualization Module
Creates interactive charts for OSM coverage gap analysis
"""

import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json

def create_coverage_score_map(df):
    """
    Create world map showing OSM coverage scores by city
    """
    fig = go.Figure(data=go.Scattergeo(
        lon=[0] * len(df),  # Placeholder - would need actual coordinates
        lat=[0] * len(df),
        text=df['city'] + ', ' + df['country'],
        mode='markers',
        marker=dict(
            size=df['osm_coverage_score'] / 5,
            color=df['osm_coverage_score'],
            colorscale='RdYlGn',
            cmin=0,
            cmax=100,
            colorbar=dict(title="OSM Coverage Score"),
            line=dict(width=0.5, color='white')
        ),
        hovertemplate='<b>%{text}</b><br>Coverage: %{marker.color:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title='Global OSM Coverage for Climate Resilience Infrastructure',
        geo=dict(
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            coastlinecolor='rgb(204, 204, 204)',
        ),
        height=500
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_gap_severity_chart(df):
    """
    Create bar chart showing cities by gap severity
    """
    df['gap_severity'] = 100 - df['osm_coverage_score']
    df_sorted = df.nlargest(20, 'gap_severity')
    
    # Color by priority level
    color_map = {'High': '#dc3545', 'Medium': '#ffc107', 'Low': '#28a745'}
    colors = df_sorted['priority_level'].map(color_map)
    
    fig = go.Figure(data=[
        go.Bar(
            y=df_sorted['city'] + ', ' + df_sorted['country'],
            x=df_sorted['gap_severity'],
            orientation='h',
            marker_color=colors,
            text=df_sorted['gap_severity'].round(1),
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Gap Severity: %{x:.1f}%<br>Coverage: ' + 
                          (100 - df_sorted['gap_severity']).round(1).astype(str) + '%<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title='Top 20 Cities with Largest OSM Coverage Gaps',
        xaxis_title='Gap Severity Score (100 - Coverage)',
        yaxis_title='',
        height=600,
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_feature_coverage_heatmap(df):
    """
    Create heatmap showing feature coverage across cities
    """
    features = ['drainage_mapped', 'green_infrastructure', 'cooling_centers', 
                'evacuation_routes', 'emergency_shelters', 'flood_barriers', 
                'permeable_surfaces']
    
    # Convert to numeric (High=3, Medium=2, Low=1)
    coverage_map = {'High': 3, 'Medium': 2, 'Low': 1}
    
    # Take top 25 cities by gap severity for readability
    df['gap_severity'] = 100 - df['osm_coverage_score']
    df_subset = df.nlargest(25, 'gap_severity')
    
    z_data = []
    for feature in features:
        z_data.append(df_subset[feature].map(coverage_map).values)
    
    feature_labels = [f.replace('_', ' ').title() for f in features]
    
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=df_subset['city'].values,
        y=feature_labels,
        colorscale=[[0, '#dc3545'], [0.5, '#ffc107'], [1, '#28a745']],
        colorbar=dict(
            title="Coverage",
            tickvals=[1, 2, 3],
            ticktext=['Low', 'Medium', 'High']
        ),
        hovertemplate='<b>%{y}</b><br>City: %{x}<br>Coverage: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Feature Coverage Heatmap: Priority Cities',
        xaxis_title='City',
        yaxis_title='Infrastructure Feature',
        height=500,
        xaxis={'tickangle': -45}
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_priority_distribution_pie(df):
    """
    Create pie chart showing distribution of cities by priority level
    """
    priority_counts = df['priority_level'].value_counts()
    
    colors = {'High': '#dc3545', 'Medium': '#ffc107', 'Low': '#28a745'}
    
    fig = go.Figure(data=[go.Pie(
        labels=priority_counts.index,
        values=priority_counts.values,
        marker=dict(colors=[colors[p] for p in priority_counts.index]),
        hole=0.3,
        textinfo='label+percent+value',
        hovertemplate='<b>%{label}</b><br>Cities: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title='Distribution of Cities by Mapping Priority Level',
        height=400
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_regional_coverage_chart(regional_stats):
    """
    Create bar chart comparing regional OSM coverage
    """
    df_regional = pd.DataFrame(regional_stats)
    
    fig = go.Figure(data=[
        go.Bar(
            x=df_regional['region'],
            y=df_regional['avg_coverage'],
            marker_color=df_regional['avg_coverage'],
            marker=dict(
                colorscale='RdYlGn',
                cmin=0,
                cmax=100,
                colorbar=dict(title="Coverage %")
            ),
            text=df_regional['avg_coverage'].round(1),
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Avg Coverage: %{y:.1f}%<br>Cities: ' + 
                          df_regional['city_count'].astype(str) + '<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title='Average OSM Coverage by World Region',
        xaxis_title='Region',
        yaxis_title='Average Coverage Score (%)',
        height=400,
        showlegend=False
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_feature_summary_bars(feature_coverage):
    """
    Create horizontal bar chart summarizing feature coverage globally
    """
    df_features = pd.DataFrame(feature_coverage)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='High Coverage',
        y=df_features['feature'],
        x=df_features['high_coverage'],
        orientation='h',
        marker_color='#28a745',
        text=df_features['high_coverage'],
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name='Medium Coverage',
        y=df_features['feature'],
        x=df_features['medium_coverage'],
        orientation='h',
        marker_color='#ffc107',
        text=df_features['medium_coverage'],
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name='Low Coverage',
        y=df_features['feature'],
        x=df_features['low_coverage'],
        orientation='h',
        marker_color='#dc3545',
        text=df_features['low_coverage'],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='Global Feature Coverage Summary (43 Megacities)',
        xaxis_title='Number of Cities',
        yaxis_title='',
        barmode='stack',
        height=500,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_coverage_vs_gap_scatter(df):
    """
    Create scatter plot showing OSM coverage vs gap severity
    """
    df['gap_severity'] = 100 - df['osm_coverage_score']
    
    color_map = {'High': '#dc3545', 'Medium': '#ffc107', 'Low': '#28a745'}
    
    fig = go.Figure()
    
    for priority in ['High', 'Medium', 'Low']:
        df_priority = df[df['priority_level'] == priority]
        fig.add_trace(go.Scatter(
            x=df_priority['osm_coverage_score'],
            y=df_priority['gap_severity'],
            mode='markers+text',
            name=f'{priority} Priority',
            marker=dict(
                size=12,
                color=color_map[priority],
                line=dict(width=1, color='white')
            ),
            text=df_priority['city'],
            textposition='top center',
            textfont=dict(size=8),
            hovertemplate='<b>%{text}</b><br>Coverage: %{x:.1f}%<br>Gap: %{y:.1f}%<extra></extra>'
        ))
    
    fig.update_layout(
        title='OSM Coverage vs Gap Severity by Priority Level',
        xaxis_title='OSM Coverage Score (%)',
        yaxis_title='Gap Severity (100 - Coverage)',
        height=600,
        hovermode='closest',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def generate_all_osm_visualizations(df, report):
    """
    Generate all visualizations for the OSM gap analysis dashboard
    """
    return {
        'gap_severity_chart': create_gap_severity_chart(df),
        'feature_heatmap': create_feature_coverage_heatmap(df),
        'priority_pie': create_priority_distribution_pie(df),
        'regional_chart': create_regional_coverage_chart(report['regional_analysis']),
        'feature_summary': create_feature_summary_bars(report['feature_coverage']),
        'scatter_plot': create_coverage_vs_gap_scatter(df)
    }
