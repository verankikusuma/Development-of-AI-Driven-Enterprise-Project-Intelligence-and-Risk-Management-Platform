import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

DATASET_PATH = Path(__file__).parents[1] / "ml_models" / "project_risk_dataset.csv"
IT_PROJECT_TYPES = ["Software Development", "IT Infrastructure", "ERP Implementation", "Telecom", "Healthcare IT", "Financial Systems"]

@st.cache_data(show_spinner=False)
def load_dataset():
    """Loads and caches the 200,000 project risk dataset."""
    if not os.path.exists(DATASET_PATH):
        return None
    df = pd.read_csv(DATASET_PATH)
    # Classify IT vs Non-IT
    df["domain"] = df["project_type"].apply(lambda x: "IT Technical" if x in IT_PROJECT_TYPES else "Non-IT Business")
    return df


def get_dataset_metadata():
    """Returns dataset telemetry metadata."""
    df = load_dataset()
    if df is None:
        return {
            "file_size_mb": 0.0,
            "total_records": 0,
            "total_features": 0,
            "it_count": 0,
            "non_it_count": 0,
            "risk_counts": {},
            "mean_risk_score": 0.0,
            "mean_budget": 0.0
        }
    
    file_size = os.path.getsize(DATASET_PATH) / (1024 * 1024)
    risk_counts = df["risk_category"].value_counts().to_dict()
    domain_counts = df["domain"].value_counts().to_dict()
    
    return {
        "file_size_mb": round(file_size, 1),
        "total_records": len(df),
        "total_features": len(df.columns) - 1, # Excluding added domain col
        "it_count": domain_counts.get("IT Technical", 0),
        "non_it_count": domain_counts.get("Non-IT Business", 0),
        "risk_counts": risk_counts,
        "mean_risk_score": float(df["risk_score"].mean()),
        "mean_budget": float(df["budget_usd"].mean()),
        "columns": [c for c in df.columns if c != "domain"]
    }


def render_it_vs_non_it_chart():
    """Generates a Plotly donut chart for IT vs Non-IT distribution."""
    df = load_dataset()
    if df is None: return None
    
    counts = df["domain"].value_counts()
    fig = go.Figure(data=[go.Pie(
        labels=counts.index,
        values=counts.values,
        hole=.5,
        marker=dict(colors=["#38bdf8", "#fbbf24"]),
        textinfo="label+percent",
        textfont=dict(color="#ffffff", size=13)
    )])
    fig.update_layout(
        title="<b>IT vs Non-IT Dataset Ratio</b>",
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#f8fafc", "family": "Plus Jakarta Sans"},
        margin=dict(l=20, r=20, t=40, b=20),
        height=260,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )
    return fig


def render_risk_distribution_chart():
    """Generates a bar chart showing risk category distribution across dataset."""
    df = load_dataset()
    if df is None: return None
    
    risk_order = ["Low", "Medium", "High", "Critical"]
    counts = df["risk_category"].value_counts().reindex(risk_order).fillna(0)
    color_map = {"Low": "#10b981", "Medium": "#f59e0b", "High": "#f97316", "Critical": "#ef4444"}
    colors = [color_map[k] for k in counts.index]
    
    fig = go.Figure(data=[go.Bar(
        x=counts.index,
        y=counts.values,
        marker_color=colors,
        text=[f"{v:,}" for v in counts.values],
        textposition="auto"
    )])
    fig.update_layout(
        title="<b>Risk Category Frequency (200,000 Telemetry Records)</b>",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        font={"color": "#f8fafc", "family": "Plus Jakarta Sans"},
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Risk Category"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Total Projects"),
        margin=dict(l=20, r=20, t=40, b=30),
        height=260
    )
    return fig


def render_budget_vs_risk_chart():
    """Generates a scatter/trend chart for Budget vs Risk Index correlation."""
    df = load_dataset()
    if df is None: return None
    
    # Subsample 1,200 points for fast browser rendering
    sample_df = df.sample(min(1200, len(df)), random_state=42)
    
    fig = px.scatter(
        sample_df,
        x="budget_usd",
        y="risk_score",
        color="risk_category",
        color_discrete_map={"Low": "#10b981", "Medium": "#fbbf24", "High": "#fb923c", "Critical": "#ef4444"},
        hover_data=["project_type", "schedule_overrun_pct"],
    )
    
    fig.update_layout(
        title=dict(text="<b>Capital Budget vs ML Risk Index Correlation</b>", y=0.96, x=0.01, font=dict(size=14, color="#ffffff")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.5)",
        font={"color": "#f8fafc", "family": "Plus Jakarta Sans"},
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Budget (USD)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Risk Index Score (0-100)"),
        margin=dict(l=40, r=30, t=50, b=60),
        height=310,
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5, title="")
    )
    return fig


def render_key_feature_stats_chart():
    """Generates horizontal comparison chart of average feature values by domain."""
    df = load_dataset()
    if df is None: return None
    
    grouped = df.groupby("domain")[["schedule_overrun_pct", "cost_overrun_pct", "tech_complexity_score", "external_dependency_score", "team_turnover_pct"]].mean().reset_index()
    
    melted = pd.melt(grouped, id_vars=["domain"], var_name="Feature", value_name="Average Score")
    
    feature_labels = {
        "schedule_overrun_pct": "Schedule Overrun %",
        "cost_overrun_pct": "Cost Overrun %",
        "tech_complexity_score": "Tech Complexity",
        "external_dependency_score": "Ext. Dependency",
        "team_turnover_pct": "Turnover %"
    }
    melted["Feature"] = melted["Feature"].map(feature_labels)
    
    fig = px.bar(
        melted,
        x="Average Score",
        y="Feature",
        color="domain",
        barmode="group",
        color_discrete_map={"IT Technical": "#00f2fe", "Non-IT Business": "#fbbf24"},
    )
    
    fig.update_layout(
        title=dict(text="<b>Average Feature Metrics: IT vs Non-IT Projects</b>", y=0.96, x=0.01, font=dict(size=14, color="#ffffff")),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.5)",
        font={"color": "#f8fafc", "family": "Plus Jakarta Sans"},
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        margin=dict(l=40, r=30, t=50, b=60),
        height=310,
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5, title="")
    )
    return fig
