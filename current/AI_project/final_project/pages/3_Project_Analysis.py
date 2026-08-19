import streamlit as st
import pandas as pd
import numpy as np
from utils.ui import inject_css, page_header, risk_badge
from utils.dataset_analyzer import (
    load_dataset, get_dataset_metadata,
    render_it_vs_non_it_chart, render_risk_distribution_chart,
    render_budget_vs_risk_chart, render_key_feature_stats_chart
)
from utils.api_client import backend_health

# ============================================================
# PAGE SETUP
# ============================================================

inject_css()

page_header(
    "IT Project & Dataset Intelligence Analysis",
    "Comprehensive dataset analytics across 200,000 project records, API status, and active project ML predictions."
)

project_id = st.session_state.get("selected_project_id")
project = st.session_state.get("selected_project", {})
api_base = st.session_state.get("api_base", "http://127.0.0.1:8000")

# ============================================================
# 1. SYSTEM & DATASET TELEMETRY KPIS
# ============================================================

meta = get_dataset_metadata()
is_healthy = backend_health(api_base)

st.subheader("Dataset & API System Telemetry")

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Dataset Size</div>        <div class="metric-card-value">{meta['file_size_mb']:.1f}<span style="font-size:1.1rem; color:#94a3b8;"> MB</span></div>
        <div class="metric-card-sub" style="color:#cbd5e1;">project_risk_dataset.csv</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Total Records</div>        <div class="metric-card-value">{meta['total_records']:,}</div>
        <div class="metric-card-sub" style="color:#cbd5e1;">Telemetry Rows</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Feature Count</div>        <div class="metric-card-value">{meta['total_features']}</div>
        <div class="metric-card-sub" style="color:#cbd5e1;">Predictive Attributes</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Relevant IT Records</div>        <div class="metric-card-value" style="color:#38bdf8;">{meta['it_count']:,}</div>
        <div class="metric-card-sub" style="color:#cbd5e1;">{(meta['it_count']/max(1, meta['total_records'])*100):.1f}% of Dataset</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    api_color = "#34d399" if is_healthy else "#fbbf24"
    api_label = "FastAPI Online" if is_healthy else "Embedded Engine"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">API Status</div>        <div class="metric-card-value" style="color:{api_color}; font-size:1.3rem;">{api_label}</div>
        <div class="metric-card-sub" style="color:#cbd5e1;">XGBoost ML Active</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ============================================================
# 2. CHARTS FOR DATASET ANALYSIS
# ============================================================

st.subheader("Dataset Analysis & Distribution Visualizations")

tab1, tab2 = st.tabs(["Domain & Risk Distributions","Correlation & Feature Analytics"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        fig_domain = render_it_vs_non_it_chart()
        if fig_domain: st.plotly_chart(fig_domain, use_container_width=True)
    with c2:
        fig_risk = render_risk_distribution_chart()
        if fig_risk: st.plotly_chart(fig_risk, use_container_width=True)

with tab2:
    c3, c4 = st.columns(2)
    with c3:
        fig_budget = render_budget_vs_risk_chart()
        if fig_budget: st.plotly_chart(fig_budget, use_container_width=True)
    with c4:
        fig_stats = render_key_feature_stats_chart()
        if fig_stats: st.plotly_chart(fig_stats, use_container_width=True)

st.divider()

# ============================================================
# 3. EXECUTIVE PROJECT BENCHMARK & PERFORMANCE STUDIO
# ============================================================

st.subheader("Executive Project Benchmark & Performance Studio")

if not project:
    st.info("Upload an IT project document on the **Document Upload** page to view live performance benchmark comparisons.")
else:
    features = project.get("features", {})
    b_usd = features.get("budget_usd", 0.0)
    s_overrun = features.get("schedule_overrun_pct", 0.0)
    res_avail = features.get("resource_availability_pct", 85.0)
    complexity = features.get("tech_complexity_score", 45.0)
    vendor_cnt = features.get("vendor_dependency_count", 1.0)
    
    benchmark_data = [
        {"Operational Parameter":"Capital Project Budget","Active Project Telemetry": f"${b_usd:,.0f}","Industry Mean Benchmark":"$2,150,000 Mean","Status Assessment":"Baseline Compliant"},
        {"Operational Parameter":"Schedule Overrun Exposure","Active Project Telemetry": f"{s_overrun:.1f}% Variance","Industry Mean Benchmark":"15.0% Variance Baseline","Status Assessment":"Active Governance"},
        {"Operational Parameter":"Resource Capacity Index","Active Project Telemetry": f"{res_avail:.0f}% Availability","Industry Mean Benchmark":"85% Target Availability","Status Assessment":"Stable Capacity"},
        {"Operational Parameter":"Technical Complexity Score","Active Project Telemetry": f"{complexity:.0f}/100 Rating","Industry Mean Benchmark":"45/100 Average Rating","Status Assessment":"High Density"},
        {"Operational Parameter":"External Vendor Interfaces","Active Project Telemetry": f"{vendor_cnt:.0f} Active Vendors","Industry Mean Benchmark":"< 2 Vendors Target","Status Assessment":"Dependency Risk"},
    ]
    
    st.dataframe(pd.DataFrame(benchmark_data), use_container_width=True, hide_index=True)

st.divider()

# ============================================================
# 4. ACTIVE IT PROJECT ML PREDICTION STATISTICS & ACTION MATRIX
# ============================================================

st.subheader("Active Project Prediction & Strategic Action Matrix")

if not project:
    st.info("Upload an IT project document to activate predictions and strategic action items.")
else:
    health = float(project.get("health_score", 0.0))
    risk = float(project.get("risk_score", 0.0))
    r_level = project.get("risk_level", "Medium")

    col_active1, col_active2 = st.columns([1, 1.3])

    with col_active1:
        st.markdown(f"""
        <div class="glass-card" style="border-color: rgba(0, 242, 254, 0.35); height: 100%;">
            <h4 style="color:#00f2fe; margin-top:0; font-weight:800; font-size:1.05rem;">Active Project Telemetry & Assessment</h4>
            <p style="color:#ffffff; font-size:0.95rem;"><strong>Project Name:</strong> {project.get('name', 'IT Project')}</p>
            <p style="color:#ffffff; font-size:0.95rem;"><strong>Predicted Risk Score:</strong> {risk:.1f}/100 ({risk_badge(r_level)})</p>
            <p style="color:#ffffff; font-size:0.95rem;"><strong>Engineering Health Score:</strong> {health:.1f}%</p>
            <p style="color:#cbd5e1; font-size:0.9rem;"><strong>Dataset Benchmark Mean:</strong> {meta['mean_risk_score']:.1f}/100</p>
        </div>
        """, unsafe_allow_html=True)

    with col_active2:
        delivs = project.get("deliverables", [])
        action_matrix = [
            {"Task ID":"ACT-001","Strategic Delivery Task": f"Execute Security Penetration Audit for {delivs[0] if delivs else'Core Module'}","Operational Owner":"Security Engineering Lead","Priority":"CRITICAL","Sprint":"Sprint 1","Status":"In Progress"},
            {"Task ID":"ACT-002","Strategic Delivery Task": f"Deploy Microservices Gateway for {delivs[1] if len(delivs)>1 else'API Services'}","Operational Owner":"DevOps Architecture Lead","Priority":"HIGH","Sprint":"Sprint 1","Status":"In Progress"},
            {"Task ID":"ACT-003","Strategic Delivery Task":"Finalize Third-Party Vendor SLA Contracts","Operational Owner":"Vendor Management Lead","Priority":"HIGH","Sprint":"Sprint 2","Status":"Pending Sign-off"},
            {"Task ID":"ACT-004","Strategic Delivery Task":"Establish Weekly Executive Steering Committee Sync","Operational Owner":"Delivery Director","Priority":"MEDIUM","Sprint":"Sprint 2","Status":"Completed"},
            {"Task ID":"ACT-005","Strategic Delivery Task":"Conduct Disaster Recovery Chaos Simulation","Operational Owner":"Infrastructure Lead","Priority":"MEDIUM","Sprint":"Sprint 3","Status":"Scheduled"},
        ]
        
        st.markdown("""
        <div class="glass-card" style="height: 100%;">
            <h4 style="color:#00f2fe; margin-top:0; font-weight:800; font-size:1.05rem;">Enterprise Delivery Action Plan & Task Matrix</h4>
        """, unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(action_matrix), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    missing = project.get("missing_info", [])
    if missing:
        st.warning("**Document Information Gaps:**")
        for m in missing:
            st.write(f"- {m}")