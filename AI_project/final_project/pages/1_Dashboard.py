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
    "IT Engineering Executive Dashboard",
    "AI-powered predictive risk analytics, architectural health, and ML-driven forecasting for software initiatives."
)

is_batch = st.session_state.get("is_batch", False)
batch_projects = st.session_state.get("batch_projects", [])

project_id = st.session_state.get("selected_project_id")
project = st.session_state.get("selected_project", {})

if not project_id or not project:
    st.warning("No active IT project found. Please upload an IT project document or dataset first.")
    st.page_link("pages/2_Document_Upload.py", label="Go to IT Document Upload")
    st.stop()

# ============================================================
# BATCH OVERVIEW (IF BATCH UPLOAD)
# ============================================================

if is_batch and batch_projects:
    st.subheader("Portfolio Batch Risk Overview")
    
    col_donut, col_tbl = st.columns([1, 1.2])
    with col_donut:
        st.plotly_chart(render_risk_donut(batch_projects), use_container_width=True)
    with col_tbl:
        results_list = [{
            "Project Name": p.get("name", "Unknown"),
            "Health Score": f"{p.get('health_score', 0):.1f}%",
            "Risk Score": f"{p.get('risk_score', 0):.1f}/100",
            "Risk Level": p.get("risk_level", "Unknown")
        } for p in batch_projects]
        df = pd.DataFrame(results_list)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        csv_export = df.to_csv(index=False)
        st.download_button(
            label="Download Portfolio Risk Report (CSV)",
            data=csv_export,
            file_name="batch_project_risk_scores.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    st.info("**Tip**: Use the **Batch Project Selection** dropdown in the sidebar to switch between projects.")
    st.divider()

# ============================================================
# TOP KPI METRICS CARDS
# ============================================================

features = project.get("features", {})
health_score = float(project.get("health_score", 0.0))
risk_score = float(project.get("risk_score", 0.0))
risk_level = project.get("risk_level", "Low")
budget_val = float(project.get("budget", features.get("budget_usd", 0.0)))

planned_days = features.get("planned_duration_days", 0)
deadline_val = project.get("deadline", "TBD")
if deadline_val == "TBD" and planned_days > 0:
    deadline_val = f"{int(planned_days)} Days"

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">System Risk Index</div>        <div class="metric-card-value">{risk_score:.1f}<span style="font-size:1.1rem; color:#94a3b8;">/100</span></div>
        <div class="metric-card-sub">{risk_badge(risk_level)}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    health_color = "#34d399" if health_score >= 70 else "#fbbf24" if health_score >= 45 else "#f87171"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Engineering Health</div>        <div class="metric-card-value" style="color:{health_color};">{health_score:.1f}%</div>
        <div class="metric-card-sub" style="color:#cbd5e1;">XGBoost Evaluated</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Capital Budget</div>        <div class="metric-card-value">${budget_val:,.0f}</div>
        <div class="metric-card-sub" style="color:#cbd5e1;">Allocated Funding</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    overrun_pct = features.get("schedule_overrun_pct", 0)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Planned Timeline</div>        <div class="metric-card-value">{deadline_val}</div>
        <div class="metric-card-sub" style="color:{'#f87171' if overrun_pct > 15 else '#38bdf8'};">Overrun Risk: +{overrun_pct:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ============================================================
# CHART SECTION 1: RISK GAUGE & TECH RISK RADAR
# ============================================================

c1, c2 = st.columns([1, 1.2])

with c1:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color:#38bdf8; margin-top:0; font-size:1.1rem;">XGBoost Risk Index Speedometer</h3>    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(render_risk_gauge(risk_score, risk_level), use_container_width=True)

with c2:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color:#38bdf8; margin-top:0; font-size:1.1rem;">Multidimensional IT Risk Factor Radar</h3>    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(render_radar_chart(features), use_container_width=True)

# ============================================================
# CHART SECTION 2: FINANCIAL ALLOCATION & MILESTONES
# ============================================================

c3, c4 = st.columns([1, 1.2])

with c3:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color:#38bdf8; margin-top:0; font-size:1.1rem;">Financial Allocation & Risk Contingency</h3>    </div>
    """, unsafe_allow_html=True)
    cost_overrun = features.get("cost_overrun_pct", 0)
    st.plotly_chart(render_budget_contingency_chart(budget_val, risk_score, cost_overrun), use_container_width=True)

with c4:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color:#38bdf8; margin-top:0; font-size:1.1rem;">Milestone Completion Progress (Gantt)</h3>    </div>
    """, unsafe_allow_html=True)
    milestones = project.get("milestones", [])
    if milestones:
        fig_gantt = render_gantt_chart(milestones)
        if fig_gantt:
            st.plotly_chart(fig_gantt, use_container_width=True)
        else:
            st.dataframe(pd.DataFrame(milestones), use_container_width=True, hide_index=True)
    else:
        st.info("No milestone milestones schedule extracted. Upload document with milestones.")

# ============================================================
# CHART SECTION 3: NUMERIC RISK DRIVERS
# ============================================================

st.markdown("""
<div class="glass-card">
    <h3 style="color:#38bdf8; margin-top:0; font-size:1.1rem;">Key Numerical Risk Factors & Impact Outliers</h3></div>
""", unsafe_allow_html=True)
st.plotly_chart(render_risk_drivers_chart(features), use_container_width=True)

st.divider()

# ============================================================
# SCOPE, DELIVERABLES & DOCUMENT GAPS
# ============================================================

info_col1, info_col2 = st.columns(2)

with info_col1:
    st.markdown("""
    <div class="glass-card">
        <h3 style="color:#ffffff; margin-top:0; font-size:1.1rem;">Technical Project Scope</h3>    """, unsafe_allow_html=True)
    st.write(project.get("project_scope", "No scope defined."))
    
    deliverables = project.get("deliverables", [])
    if deliverables:
        st.markdown("**Key Engineering Deliverables:**")
        for d in deliverables[:6]:
            st.markdown(f"- {d}")
    st.markdown("</div>", unsafe_allow_html=True)

with info_col2:
    missing_info = project.get("missing_info", [])
    st.markdown("""
    <div class="glass-card">
        <h3 style="color:#ffffff; margin-top:0; font-size:1.1rem;">Document Gaps & Risk Drivers</h3>    """, unsafe_allow_html=True)
    if missing_info:
        for m in missing_info:
            st.warning(f"Missing parameter: {m}")
    else:
        st.success("All critical technical parameters were identified in document.")
        
    potential_risks = project.get("potential_risks", [])
    if potential_risks:
        st.markdown("**Qualitative Risk Triggers:**")
        for r in potential_risks[:4]:
            st.markdown(f"• {r}")
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# DEEP DIVE MODULE QUICK LINKS
# ============================================================

st.divider()
st.subheader("Deep Dive Intelligence Modules")

c1, c2, c3 = st.columns(3)
with c1:
    st.page_link("pages/3_Project_Analysis.py", label="Action Items & Tasks")
with c2:
    st.page_link("pages/4_Risk_Intelligence.py", label="Risk Intelligence & Radar")
with c3:
    st.page_link("pages/5_Schedule_Intelligence.py", label="Schedule & Milestones")

c4, c5, c6 = st.columns(3)
with c4:
    st.page_link("pages/6_Dependencies.py", label="Technical Dependencies")
with c5:
    st.page_link("pages/9_Documentation.py", label="Auto-Generate Agile Docs")
with c6:
    st.page_link("pages/10_AI_Assistant.py", label="RAGBot AI Assistant")
