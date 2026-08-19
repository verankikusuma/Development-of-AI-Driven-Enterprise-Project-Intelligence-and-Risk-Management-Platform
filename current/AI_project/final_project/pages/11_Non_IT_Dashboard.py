import streamlit as st
import pandas as pd
from utils.ui import (
    inject_css, page_header, risk_badge, render_risk_gauge,
    render_radar_chart, render_budget_contingency_chart,
    render_risk_drivers_chart, render_gantt_chart, render_risk_donut
)

# ============================================================
# PAGE SETUP
# ============================================================

inject_css()

page_header(
    "Non-IT Business Executive Dashboard",
    "Business-focused operational overview, financial contingency analytics, and enterprise risk management."
)

project_id = st.session_state.get("selected_project_id")
project = st.session_state.get("selected_project", {})
is_batch = st.session_state.get("is_batch", False)
batch_projects = st.session_state.get("batch_projects", [])

if not project_id or not project:
    st.warning("No active Non-IT project found. Please upload a business document or dataset first.")
    st.page_link("pages/12_Non_IT_Document_Upload.py", label="Go to Non-IT Document Upload")
    st.stop()

# ============================================================
# BATCH OVERVIEW (IF BATCH UPLOAD)
# ============================================================

if is_batch and batch_projects:
    st.subheader("Enterprise Portfolio Risk Overview")
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.plotly_chart(render_risk_donut(batch_projects), use_container_width=True)
    with col2:
        df = pd.DataFrame([{
            "Project Name": p.get("name", "Unknown"),
            "Business Health": f"{p.get('health_score', 0):.0f}%",
            "Risk Score": f"{p.get('risk_score', 0):.0f}/100",
            "Risk Level": p.get("risk_level", "Unknown")
        } for p in batch_projects])
        st.dataframe(df, use_container_width=True, hide_index=True)
    st.divider()

# ============================================================
# TOP EXECUTIVE KPI CARDS
# ============================================================

features = project.get("features", {})
health_score = float(project.get("health_score", 0.0))
risk_score = float(project.get("risk_score", 50.0))
risk_level = project.get("risk_level", "Medium")
budget_val = float(project.get("budget", features.get("budget_usd", 0.0)))

planned_days = features.get("planned_duration_days", 0)
deadline_val = project.get("deadline", "TBD")
if deadline_val == "TBD" and planned_days > 0:
    deadline_val = f"{int(planned_days)} Days"

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Operational Risk Index</div>        <div class="metric-card-value">{risk_score:.1f}<span style="font-size:1.1rem; color:#94a3b8;">/100</span></div>
        <div class="metric-card-sub">{risk_badge(risk_level)}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    health_color = "#34d399" if health_score >= 70 else "#fbbf24" if health_score >= 45 else "#f87171"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Business Health Score</div>        <div class="metric-card-value" style="color:{health_color};">{health_score:.1f}%</div>
        <div class="metric-card-sub" style="color:#cbd5e1;">Random Forest Evaluated</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Total Approved Budget</div>        <div class="metric-card-value">${budget_val:,.0f}</div>
        <div class="metric-card-sub" style="color:#cbd5e1;">Capital Allocation</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    overrun_pct = features.get("schedule_overrun_pct", 0)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Target Completion</div>        <div class="metric-card-value">{deadline_val}</div>
        <div class="metric-card-sub" style="color:{'#f87171' if overrun_pct > 15 else '#fbbf24'};">Operational Delay: +{overrun_pct:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ============================================================
# CHART SECTION 1: BUSINESS GAUGE & OPERATIONAL RADAR
# ============================================================

c1, c2 = st.columns([1, 1.2])

with c1:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color:#fbbf24; margin-top:0; font-size:1.1rem;">Business Risk Gauge Meter</h3>    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(render_risk_gauge(risk_score, risk_level), use_container_width=True)

with c2:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color:#fbbf24; margin-top:0; font-size:1.1rem;">Operational Risk Factors Radar</h3>    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(render_radar_chart(features), use_container_width=True)

# ============================================================
# CHART SECTION 2: BUDGET CONTINGENCY & STRATEGIC MILESTONES
# ============================================================

c3, c4 = st.columns([1, 1.2])

with c3:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color:#fbbf24; margin-top:0; font-size:1.1rem;">Financial Budget & Contingency Reserve</h3>    </div>
    """, unsafe_allow_html=True)
    cost_overrun = features.get("cost_overrun_pct", 0)
    st.plotly_chart(render_budget_contingency_chart(budget_val, risk_score, cost_overrun), use_container_width=True)

with c4:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color:#fbbf24; margin-top:0; font-size:1.1rem;">Strategic Deliverables Gantt View</h3>    </div>
    """, unsafe_allow_html=True)
    milestones = project.get("milestones", [])
    if milestones:
        fig_gantt = render_gantt_chart(milestones)
        if fig_gantt:
            st.plotly_chart(fig_gantt, use_container_width=True)
        else:
            st.dataframe(pd.DataFrame(milestones), use_container_width=True, hide_index=True)
    else:
        st.info("No explicit milestones extracted from the uploaded document.")

# ============================================================
# CHART SECTION 3: OPERATIONAL RISK OUTLIERS CHART
# ============================================================

st.markdown("""
<div class="glass-card">
    <h3 style="color:#fbbf24; margin-top:0; font-size:1.1rem;">Operational Risk Outliers & Variance</h3></div>
""", unsafe_allow_html=True)
st.plotly_chart(render_risk_drivers_chart(features), use_container_width=True)

st.divider()

# ============================================================
# BUSINESS SCOPE & DELIVERABLES
# ============================================================

info_col1, info_col2 = st.columns(2)

with info_col1:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color:#ffffff; margin-top:0; font-size:1.1rem;">Business Project Scope</h3>    """, unsafe_allow_html=True)
    st.write(project.get("project_scope", "No scope defined."))
    
    delivs = project.get("deliverables", [])
    if delivs:
        st.markdown("**Key Strategic Deliverables:**")
        for d in delivs[:6]:
            st.markdown(f"- {d}")
    st.markdown("</div>", unsafe_allow_html=True)

with info_col2:
    missing_info = project.get("missing_info", [])
    st.markdown("""
    <div class="glass-card">
        <h3 style="color:#ffffff; margin-top:0; font-size:1.1rem;">Operational Gaps & Risk Drivers</h3>    """, unsafe_allow_html=True)
    if missing_info:
        for m in missing_info:
            st.warning(f"Operational gap: {m}")
    else:
        st.success("All core operational parameters documented.")
        
    potential_risks = project.get("potential_risks", [])
    if potential_risks:
        st.markdown("**Strategic Risk Triggers:**")
        for r in potential_risks[:4]:
            st.markdown(f"• {r}")
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# EXECUTIVE NAVIGATION QUICK LINKS
# ============================================================

st.divider()
st.subheader("Executive Navigation Quick Links")

c1, c2, c3 = st.columns(3)
with c1:
    st.page_link("pages/13_Non_IT_Project_Analysis.py", label="Detailed Business Analysis")
with c2:
    st.page_link("pages/14_Non_IT_Risk_Intelligence.py", label="Operational Risk Intelligence")
with c3:
    st.page_link("pages/15_Non_IT_Schedule_Intelligence.py", label="Timeline & Milestones")

c4, c5, c6 = st.columns(3)
with c4:
    st.page_link("pages/16_Non_IT_Dependencies.py", label="Resource & Vendor Dependencies")
with c5:
    st.page_link("pages/19_Non_IT_Documentation.py", label="Generate Briefing Docs")
with c6:
    st.page_link("pages/20_Non_IT_AI_Assistant.py", label="Ask AI Assistant")
