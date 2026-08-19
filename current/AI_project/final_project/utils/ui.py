import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
from pathlib import Path


def inject_css():
    """Injects state-of-the-art corporate dark-mode glassmorphism design system styling across the Streamlit UI."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #f8fafc;
    }

    h1, h2, h3, h4 {
        font-family: 'Outfit', 'Plus Jakarta Sans', sans-serif;
        letter-spacing: -0.4px;
    }

    /* Overall App Ambient Mesh Canvas */
    [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
        background: #070a12 !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(0, 242, 254, 0.07) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(112, 0, 255, 0.07) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(15, 23, 42, 0.9) 0px, transparent 50%) !important;
        background-attachment: fixed !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* Container Padding & Max Width */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3.5rem;
        max-width: 1440px;
    }
    
    /* Sleek Midnight Glass Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0b111e !important;
        background-image: linear-gradient(180deg, rgba(15, 23, 42, 0.8) 0%, rgba(7, 10, 18, 0.95) 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: 5px 0 25px rgba(0, 0, 0, 0.5);
    }

    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"] span,
    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"] p,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stMarkdown p {
        color: #cbd5e1 !important;
        font-weight: 500;
        font-size: 0.92rem;
    }

    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
        background: rgba(0, 242, 254, 0.12) !important;
        border-radius: 10px;
        transition: all 0.2s ease;
    }

    [data-testid="stSidebar"] [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.2) 0%, rgba(112, 0, 255, 0.2) 100%) !important;
        border: 1px solid rgba(0, 242, 254, 0.4) !important;
        border-radius: 10px;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.25);
    }
    
    /* Hero Banner Header */
    .hero-banner {
        padding: 1.8rem 2.2rem;
        border-radius: 20px;
        margin-bottom: 1.8rem;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.85) 60%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.15);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(16px);
    }
    
    .hero-banner::before {
        content: "";
        position: absolute;
        top: 0; right: 0; width: 350px; height: 100%;
        background: radial-gradient(circle, rgba(0, 242, 254, 0.18) 0%, transparent 70%);
        pointer-events: none;
    }
    
    .hero-banner h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-banner p {
        margin: 0.45rem 0 0 0;
        font-size: 1.05rem;
        color: #94a3b8;
        font-weight: 500;
    }

    .workspace-tag-it {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(0, 242, 254, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(0, 242, 254, 0.4);
        font-size: 0.78rem;
        font-weight: 800;
        padding: 0.28rem 0.85rem;
        border-radius: 999px;
        letter-spacing: 0.4px;
        margin-bottom: 0.6rem;
        text-transform: uppercase;
        box-shadow: 0 0 14px rgba(0, 242, 254, 0.25);
    }

    .workspace-tag-nonit {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.4);
        font-size: 0.78rem;
        font-weight: 800;
        padding: 0.28rem 0.85rem;
        border-radius: 999px;
        letter-spacing: 0.4px;
        margin-bottom: 0.6rem;
        text-transform: uppercase;
        box-shadow: 0 0 14px rgba(245, 158, 11, 0.25);
    }

    /* Glowing Risk Badges */
    .risk-badge-low {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
        font-weight: 800;
        font-size: 0.85rem;
        color: #34d399;
        background: rgba(16, 185, 129, 0.18);
        border: 1px solid rgba(16, 185, 129, 0.4);
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.25);
    }
    
    .risk-badge-medium {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
        font-weight: 800;
        font-size: 0.85rem;
        color: #fbbf24;
        background: rgba(245, 158, 11, 0.18);
        border: 1px solid rgba(245, 158, 11, 0.4);
        box-shadow: 0 0 12px rgba(245, 158, 11, 0.25);
    }
    
    .risk-badge-high {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
        font-weight: 800;
        font-size: 0.85rem;
        color: #fb923c;
        background: rgba(249, 115, 22, 0.18);
        border: 1px solid rgba(249, 115, 22, 0.4);
        box-shadow: 0 0 12px rgba(249, 115, 22, 0.25);
    }
    
    .risk-badge-critical {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
        font-weight: 800;
        font-size: 0.85rem;
        color: #f87171;
        background: rgba(239, 68, 68, 0.22);
        border: 1px solid rgba(239, 68, 68, 0.5);
        box-shadow: 0 0 16px rgba(239, 68, 68, 0.35);
    }
    
    /* Modern Frost Glass Cards */
    .glass-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(26, 34, 53, 0.7) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 18px;
        padding: 1.5rem;
        margin-bottom: 1.3rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(14px);
        transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.25s ease, box-shadow 0.25s ease;
    }

    .glass-card:hover {
        transform: translateY(-3px);
        border-color: rgba(0, 242, 254, 0.35);
        box-shadow: 0 14px 35px rgba(0, 0, 0, 0.45), 0 0 20px rgba(0, 242, 254, 0.12);
    }

    .metric-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.75) 100%);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 1.35rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .metric-card:hover {
        border-color: rgba(0, 242, 254, 0.3);
        transform: translateY(-2px);
    }

    .metric-card-title {
        color: #94a3b8;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.7px;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .metric-card-value {
        color: #ffffff;
        font-size: 1.95rem;
        font-weight: 800;
        margin-top: 0.45rem;
        letter-spacing: -0.6px;
    }
    
    .metric-card-sub {
        color: #38bdf8;
        font-size: 0.84rem;
        font-weight: 600;
        margin-top: 0.25rem;
    }

    /* Dark Streamlit Inputs, Selectboxes & Tables */
    div[data-baseweb="select"] > div {
        background-color: #111827 !important;
        border-color: rgba(255, 255, 255, 0.18) !important;
        color: #f8fafc !important;
        border-radius: 10px !important;
    }

    .stDataFrame, div[data-testid="stTable"] {
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
    }

    /* Custom Streamlit Button Styling */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%) !important;
        border: 1px solid rgba(0, 198, 255, 0.5) !important;
        box-shadow: 0 4px 16px rgba(0, 198, 255, 0.4);
        font-weight: 700 !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        transition: all 0.2s ease !important;
    }

    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 22px rgba(0, 198, 255, 0.6) !important;
    }

    div.stButton > button[kind="secondary"] {
        background: rgba(30, 41, 59, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.18) !important;
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
    }

    div.stButton > button[kind="secondary"]:hover {
        background: rgba(51, 65, 85, 0.85) !important;
        border-color: rgba(0, 242, 254, 0.4) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }

    /* Tab Headers Custom Styling */
    button[data-baseweb="tab"] {
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 0.6rem 1.2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = None):
    """Renders a styled page title banner with workspace context."""
    user_type = st.session_state.get("user_type", "IT")
    if user_type == "IT":
        workspace_html = '<div class="workspace-tag-it">IT Technical Engineering Workspace</div>'
    else:
        workspace_html = '<div class="workspace-tag-nonit">Business & Operations Workspace</div>'
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f"""
    <div class="hero-banner">
        {workspace_html}
        <h1>{title}</h1>
        {subtitle_html}
    </div>
    """, unsafe_allow_html=True)


def risk_badge(level: str) -> str:
    """Returns HTML for color-coded glowing risk badge."""
    lvl = str(level).strip().capitalize()
    if lvl in ["Low", "Healthy"]:
        return f'<span class="risk-badge-low">{lvl} Risk</span>'
    elif lvl in ["Medium", "Moderate"]:
        return f'<span class="risk-badge-medium">{lvl} Risk</span>'
    elif lvl in ["High", "Severe"]:
        return f'<span class="risk-badge-high">{lvl} Risk</span>'
    else:
        return f'<span class="risk-badge-critical">{lvl} Risk</span>'

def render_risk_indicator(score: float, level: str | None = None):
    """Fast native alternative metric indicator."""
    score = max(0.0, min(100.0, float(score or 0.0)))
    resolved_level = level or ("Low" if score < 30 else "Medium" if score < 55 else "High" if score < 75 else "Critical")
    st.metric("Project Risk Index", f"{score:.1f}/100", help="0 is lowest risk and 100 is highest risk.")
    st.progress(int(score))
    st.caption(f"Current classification: {resolved_level} Risk")


def render_risk_gauge(score: float, level: str = None):
    """Generates an interactive Plotly Radial Gauge Chart for Risk Score."""
    score = max(0.0, min(100.0, float(score or 0.0)))
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "<b>Risk Index Score</b>", 'font': {'size': 18, 'color': '#f8fafc', 'family': 'Plus Jakarta Sans'}},
        number={'suffix': "/100", 'font': {'size': 38, 'color': '#ffffff', 'family': 'Plus Jakarta Sans'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
            'bar': {'color': "#00f2fe", 'thickness': 0.28},
            'bgcolor': "rgba(15, 23, 42, 0.6)",
            'borderwidth': 1,
            'bordercolor': "rgba(255, 255, 255, 0.12)",
            'steps': [
                {'range': [0, 30], 'color': 'rgba(16, 185, 129, 0.25)'},
                {'range': [30, 55], 'color': 'rgba(245, 158, 11, 0.25)'},
                {'range': [55, 75], 'color': 'rgba(249, 115, 22, 0.25)'},
                {'range': [75, 100], 'color': 'rgba(239, 68, 68, 0.35)'}
            ],
            'threshold': {
                'line': {'color': "#ef4444", 'width': 3},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': "#f8fafc", 'family': "Plus Jakarta Sans"},
        margin=dict(l=20, r=20, t=50, b=20),
        height=280
    )
    return fig


def render_radar_chart(features: dict):
    """Generates an interactive Plotly Radar / Spider Chart showing key risk factors."""
    categories = ['Schedule Overrun', 'Cost Overrun', 'Turnover Rate', 'Tech Complexity', 'Dependency Risk']
    
    def safe_number(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default
    s_overrun = min(100, safe_number(features.get('schedule_overrun_pct', 0)))
    c_overrun = min(100, safe_number(features.get('cost_overrun_pct', 0)))
    turnover = min(100, safe_number(features.get('team_turnover_pct', 0)) * 2)
    complexity = min(100, safe_number(features.get('tech_complexity_score', 0)))
    dep_risk = min(100, safe_number(features.get('external_dependency_score', 0)))
    
    values = [s_overrun, c_overrun, turnover, complexity, dep_risk]
    values.append(values[0])
    cats = categories + [categories[0]]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=cats,
        fill='toself',
        fillcolor='rgba(0, 242, 254, 0.28)',
        line=dict(color='#00f2fe', width=3),
        marker=dict(size=6, color='#ffffff'),
        name="Project Risk Profile"
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.15)", tickfont=dict(color="#94a3b8", size=10)),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.15)", tickfont=dict(color="#ffffff", size=12, family="Outfit")),
            bgcolor="rgba(15, 23, 42, 0.6)"
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "#f8fafc", 'family': "Plus Jakarta Sans"},
        margin=dict(l=50, r=50, t=30, b=30),
        height=320,
        showlegend=False
    )
    return fig


def render_budget_contingency_chart(budget: float, risk_score: float, cost_overrun_pct: float = 0.0):
    """Renders a financial breakdown chart comparing Base Budget, Risk Reserve, and Exposure."""
    base_budget = float(budget or 0.0)
    risk_contingency = base_budget * (min(100.0, float(risk_score or 0.0)) / 200.0)
    overrun_exposure = base_budget * (min(100.0, float(cost_overrun_pct or 0.0)) / 100.0)
    
    categories = ['Base Budget', 'Risk Reserve', 'Overrun Exposure']
    amounts = [base_budget, risk_contingency, overrun_exposure]
    colors = ['#00f2fe', '#fbbf24', '#ef4444']
    
    def fmt_usd(val):
        if val >= 1_000_000:
            return f"${val/1_000_000:.2f}M"
        elif val >= 1_000:
            return f"${val/1_000:.1f}K"
        return f"${val:,.0f}"

    labels = [fmt_usd(v) for v in amounts]

    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=amounts,
            marker_color=colors,
            text=labels,
            textposition='auto',
            textfont=dict(size=13, color='#ffffff', family="Plus Jakarta Sans", weight='bold'),
        )
    ])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 23, 42, 0.5)',
        font={'color': "#f8fafc", 'family': "Plus Jakarta Sans"},
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickfont=dict(size=12, color='#e2e8f0')),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="USD ($)", tickfont=dict(color='#94a3b8')),
        margin=dict(l=20, r=20, t=30, b=30),
        height=290
    )
    return fig


def render_risk_drivers_chart(features: dict):
    """Horizontal bar chart displaying key numerical risk drivers and their severity."""
    driver_map = {
        'Schedule Delay (%)': float(features.get('schedule_overrun_pct', 0)),
        'Cost Overrun (%)': float(features.get('cost_overrun_pct', 0)),
        'Tech Complexity': float(features.get('tech_complexity_score', 0)),
        'Ext. Dependencies': float(features.get('external_dependency_score', 0)),
        'Team Turnover (%)': float(features.get('team_turnover_pct', 0)),
    }
    
    df = pd.DataFrame({
        'Driver': list(driver_map.keys()),
        'Score': list(driver_map.values())
    }).sort_values(by='Score', ascending=True)
    
    colors = ['#10b981' if s < 25 else '#fbbf24' if s < 55 else '#ef4444' for s in df['Score']]
    
    fig = go.Figure(go.Bar(
        x=df['Score'],
        y=df['Driver'],
        orientation='h',
        marker_color=colors,
        text=[f"{s:.1f}" for s in df['Score']],
        textposition='outside',
        textfont=dict(size=12, color='#ffffff', weight='bold')
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 23, 42, 0.5)',
        font={'color': "#f8fafc", 'family': "Plus Jakarta Sans"},
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", range=[0, 108]),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickfont=dict(size=12, color='#e2e8f0')),
        margin=dict(l=10, r=35, t=20, b=20),
        height=270
    )
    return fig


def render_gantt_chart(milestones: list):
    """Renders a clean, spacious Plotly horizontal Gantt/Milestone progress chart."""
    if not milestones:
        return None
        
    names = []
    progresses = []
    
    for m in milestones:
        if isinstance(m, dict):
            name = m.get("name", "Milestone")
            # Truncate overly long names for clean display
            if len(name) > 35:
                name = name[:32] + "..."
            names.append(name)
            p = float(m.get("progress_pct", 0.0))
            progresses.append(p)
            
    if not names:
        return None
        
    colors = ['#10b981' if p >= 100 else ('#00f2fe' if p >= 50 else '#fbbf24') for p in progresses]

    fig = go.Figure(go.Bar(
        x=progresses,
        y=names,
        orientation='h',
        marker_color=colors,
        text=[f"{p:.0f}%" for p in progresses],
        textposition='outside',
        textfont=dict(size=12, color='#ffffff', weight='bold')
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 23, 42, 0.5)',
        font={'color': "#f8fafc", 'family': "Plus Jakarta Sans"},
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Completion Progress (%)", range=[0, 115]),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickfont=dict(size=11, color='#e2e8f0'), automargin=True),
        margin=dict(l=10, r=35, t=20, b=20),
        height=max(220, len(names) * 55),
        showlegend=False
    )
    return fig


def render_timeline_burnup_chart(planned_days: float = 90.0, schedule_overrun_pct: float = 18.5):
    """Renders a multi-line velocity burnup chart comparing Baseline Target vs Actual Progress vs Overrun Projection."""
    total_days = float(planned_days or 90.0)
    delay_days = round((total_days * (schedule_overrun_pct / 100.0)), 1)
    weeks = [f"Week {i}" for i in range(1, 13)]
    
    # Generate S-curve planned trajectory
    planned_trajectory = [round(min(100.0, (i / 12.0) ** 1.2 * 100.0), 1) for i in range(1, 13)]
    # Actual velocity lagging behind due to overrun
    actual_trajectory = [round(min(100.0, (i / 12.0) ** 1.5 * (100.0 - schedule_overrun_pct * 0.4)), 1) for i in range(1, 8)]
    # Projected trajectory for remaining weeks
    projected_trajectory = [None] * 6 + [actual_trajectory[-1]] + [round(min(100.0, actual_trajectory[-1] + (i * 11.0)), 1) for i in range(1, 5)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=weeks, y=planned_trajectory, mode='lines+markers', name='Baseline Target Pace', line=dict(color='#00f2fe', width=3, dash='dash')))
    fig.add_trace(go.Scatter(x=weeks[:7], y=actual_trajectory, mode='lines+markers', name='Actual Velocity', line=dict(color='#10b981', width=3.5)))
    fig.add_trace(go.Scatter(x=weeks[6:], y=projected_trajectory[6:], mode='lines+markers', name=f'Projected Trajectory (+{delay_days:.0f}d)', line=dict(color='#ef4444', width=3, dash='dot')))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 23, 42, 0.5)',
        font={'color': "#f8fafc", 'family': "Plus Jakarta Sans"},
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Project Timeline (Weeks)", tickangle=0),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Cumulative Progress (%)", range=[0, 105]),
        margin=dict(l=20, r=20, t=20, b=50),
        height=320,
        legend=dict(orientation="h", yanchor="top", y=0.98, xanchor="left", x=0.02, bgcolor="rgba(15, 23, 42, 0.75)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1)
    )
    return fig


def render_phase_duration_chart(milestones: list, planned_days: float = 90.0, schedule_overrun_pct: float = 18.5):
    """Grouped bar chart comparing Target Planned Days vs Actual/Projected Duration per Phase."""
    phase_names = ["Phase 1", "Phase 2", "Phase 3", "Phase 4"]
    if milestones:
        for idx, m in enumerate(milestones[:4]):
            if isinstance(m, dict) and m.get("name"):
                n = m["name"].split(":")[0] if ":" in m["name"] else f"Phase {idx+1}"
                phase_names[idx] = n[:15]

    base_per_phase = round(planned_days / 4.0, 1)
    planned_durations = [base_per_phase * 0.9, base_per_phase * 1.1, base_per_phase * 1.0, base_per_phase * 1.0]
    actual_durations = [
        planned_durations[0],
        planned_durations[1] * (1.0 + (schedule_overrun_pct * 0.015)),
        planned_durations[2] * (1.0 + (schedule_overrun_pct * 0.025)),
        planned_durations[3]
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=phase_names, y=planned_durations, name='Planned Target Days', marker_color='#00f2fe'))
    fig.add_trace(go.Bar(x=phase_names, y=actual_durations, name='Actual / Projected Days', marker_color='#fbbf24'))

    fig.update_layout(
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 23, 42, 0.5)',
        font={'color': "#f8fafc", 'family': "Plus Jakarta Sans"},
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickangle=0),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Duration (Days)"),
        margin=dict(l=20, r=20, t=20, b=50),
        height=320,
        legend=dict(orientation="h", yanchor="top", y=0.98, xanchor="right", x=0.98, bgcolor="rgba(15, 23, 42, 0.75)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1)
    )
    return fig


def render_schedule_buffer_chart(schedule_overrun_pct: float = 18.5):
    """Donut chart showing time allocation breakdown: Completed, In-Progress, Risk Buffer, Delay Lag."""
    labels = ['Completed Work', 'Active In-Progress', 'Buffer Contingency', 'Delay Overrun Exposure']
    
    completed_pct = 40.0
    active_pct = 35.0
    buffer_pct = max(5.0, 25.0 - schedule_overrun_pct)
    delay_pct = float(schedule_overrun_pct)
    
    values = [completed_pct, active_pct, buffer_pct, delay_pct]
    colors = ['#10b981', '#00f2fe', '#fbbf24', '#ef4444']

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.52,
        marker=dict(colors=colors),
        textinfo='label+percent',
        insidetextorientation='radial',
        textfont=dict(color="#ffffff", size=11)
    )])

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "#f8fafc", 'family': "Plus Jakarta Sans"},
        margin=dict(l=20, r=20, t=20, b=60),
        height=320,
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5)
    )
    return fig


def render_what_if_chart(baseline_score, sim_score, baseline_delay, sim_delay):
    """Renders a comparative bar chart for What-If scenario impact."""
    df = pd.DataFrame({
        'Metric': ['Risk Score (0-100)', 'Delay (Days)'],
        'Baseline': [baseline_score, baseline_delay],
        'Simulated Scenario': [sim_score, sim_delay]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df['Metric'], y=df['Baseline'],
        name='Baseline Current State',
        marker_color='#00f2fe'
    ))
    fig.add_trace(go.Bar(
        x=df['Metric'], y=df['Simulated Scenario'],
        name='Simulated Scenario',
        marker_color='#ef4444'
    ))
    
    fig.update_layout(
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 23, 42, 0.5)',
        font={'color': "#f8fafc", 'family': "Plus Jakarta Sans"},
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        margin=dict(l=20, r=20, t=30, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=300
    )
    return fig


def render_risk_donut(batch_projects: list):
    """Renders a Plotly donut chart showing batch risk levels breakdown."""
    levels = [p.get("risk_level", "Unknown").capitalize() for p in batch_projects]
    counts = pd.Series(levels).value_counts()
    
    color_map = {
        'Low': '#10b981',
        'Medium': '#fbbf24',
        'High': '#fb923c',
        'Critical': '#ef4444'
    }
    
    colors = [color_map.get(lbl, '#94a3b8') for lbl in counts.index]
    
    fig = go.Figure(data=[go.Pie(
        labels=counts.index,
        values=counts.values,
        hole=.5,
        marker=dict(colors=colors),
        textinfo='label+percent',
        insidetextorientation='radial'
    )])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "#f8fafc", 'family': "Plus Jakarta Sans"},
        margin=dict(l=20, r=20, t=20, b=20),
        height=260,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )
    return fig


def render_risk_management_processes():
    """Show the four project-risk processes from the project methodology."""
    st.subheader("Project Risk Management Workflow")
    columns = st.columns(4)
    stages = [
        ("1. Identify", "Capture sources, potential risks, and a risk checklist."),
        ("2. Assess", "Evaluate probability, impact, ranking, and time-overrun exposure."),
        ("3. Respond", "Set mitigation actions, owners, response plan, and baseline."),
        ("4. Control", "Monitor risks and record corrective actions through delivery."),
    ]
    for column, (title, description) in zip(columns, stages):
        with column:
            st.markdown(f"""
            <div class="glass-card" style="padding: 1.2rem; text-align: center;">
                <h4 style="color: #00f2fe; margin-top: 0; font-weight: 800;">{title}</h4>
                <p style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 0; line-height: 1.5;">{description}</p>
            </div>
            """, unsafe_allow_html=True)


def render_model_quality(project_type: str):
    """Render validation evidence for both IT and Non-IT models."""
    st.subheader("Risk Model Validation Evidence")
    
    if project_type == "Non-IT":
        metadata_path = Path(__file__).parents[1] / "ml_models" / "non_it_models" / "model_metadata.json"
    else:
        metadata_path = Path(__file__).parents[1] / "ml_models" / "it_models" / "model_metadata.json"
        
    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metrics = metadata["metrics"]
        st.caption(f"{metadata['model_type']} • Validated on {metadata['test_samples']:,} held-out telemetry records")
        cols = st.columns(5)
        for col, label, key in zip(cols, ["Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"], ["accuracy", "precision", "recall", "f1_score", "roc_auc"]):
            with col:
                st.metric(label, f"{metrics[key] * 100:.1f}%")
        st.caption(metadata["data_disclaimer"])
    else:
        st.info(f"Model validation metadata file not found at {metadata_path}.")
