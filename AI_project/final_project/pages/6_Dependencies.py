import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.ui import inject_css, page_header

inject_css()
page_header("IT System & Third-Party Dependency Intelligence", "Monitor architectural dependencies, third-party vendor SLAs, and integration fallback protocols.")

project = st.session_state.get("selected_project")
if not project:
    st.warning("Please upload an IT project document first.")
    st.page_link("pages/2_Document_Upload.py", label="Upload IT Project Document")
    st.stop()

features = project.get("features", {})
vendor_dep = float(features.get("vendor_dependency_count", 4.0))
ext_dep_score = float(features.get("external_dependency_score", 73.0))

# ============================================================
# 1. EXECUTIVE DEPENDENCY METRICS
# ============================================================

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Vendor & API Interfaces", f"{int(vendor_dep)} Active Nodes")
with c2:
    st.metric("External Dependency Index", f"{ext_dep_score:.1f}/100")
with c3:
    st.metric("SLA Target Uptime", "99.9% Baseline")
with c4:
    dep_level ="Critical Load"if ext_dep_score >= 80 else ("High Exposure"if ext_dep_score >= 60 else"Stable")
    st.metric("Dependency Vulnerability", dep_level)

st.divider()

# ============================================================
# 2. DEPENDENCY ANALYTICS & DISTRIBUTION VISUALIZATIONS
# ============================================================

st.subheader("Dependency Categorization & Vulnerability Distribution")

dependencies = project.get("dependencies", [])

if not dependencies or not isinstance(dependencies[0], dict) or "Dependency ID" not in dependencies[0]:
    delivs = project.get("deliverables", [])
    dependencies = [
        {"Dependency ID":"DEP-001","Interface Name":"AWS Multi-Region Cloud Infrastructure & VPC Router","Category":"Infrastructure","Impact":"CRITICAL","SLA Status":"Verified SLA (99.9%)","Fallback Control":"Redundant Failover Region Node"},
        {"Dependency ID":"DEP-002","Interface Name":"Third-Party OAuth2 & Identity Authentication Provider","Category":"Security & Auth","Impact":"HIGH","SLA Status":"Pending SLA Sign-off","Fallback Control":"Local Token Cache & Circuit Breaker"},
        {"Dependency ID":"DEP-003","Interface Name": f"External {delivs[0] if delivs else'Telemetry Engine'} Endpoint API","Category":"Integration Endpoint","Impact":"HIGH","SLA Status":"Verified SLA (99.5%)","Fallback Control":"Asynchronous Event Queue & Mock Harness"},
        {"Dependency ID":"DEP-004","Interface Name":"Regulatory Compliance & Audit Telemetry Logging Feed","Category":"Governance","Impact":"MEDIUM","SLA Status":"Active Monitoring","Fallback Control":"Local Compliance Log Audit Vault"}
    ]

df_dep = pd.DataFrame(dependencies)

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("<h4 style='color: #00f2fe; font-size: 1rem;'>1. Dependency Category Breakdown</h4>", unsafe_allow_html=True)
    cat_counts = df_dep["Category"].value_counts()
    fig_cat = go.Figure(data=[go.Pie(
        labels=cat_counts.index,
        values=cat_counts.values,
        hole=.5,
        marker=dict(colors=["#00f2fe", "#fbbf24", "#ef4444", "#10b981"]),
        textinfo='label+percent',
        insidetextorientation='radial',
        textfont=dict(color="#ffffff", size=11)
    )])
    fig_cat.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "#f8fafc", 'family': "Plus Jakarta Sans"},
        margin=dict(l=20, r=20, t=20, b=40),
        height=260,
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with col_chart2:
    st.markdown("<h4 style='color: #00f2fe; font-size: 1rem;'>2. Vulnerability Impact Severity</h4>", unsafe_allow_html=True)
    impact_counts = df_dep["Impact"].value_counts()
    fig_impact = go.Figure(go.Bar(
        x=impact_counts.index,
        y=impact_counts.values,
        marker_color=["#ef4444" if "CRITICAL" in k else ("#f97316" if "HIGH" in k else "#fbbf24") for k in impact_counts.index],
        text=[f"{v} Items" for v in impact_counts.values],
        textposition="outside"
    ))
    fig_impact.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(15, 23, 42, 0.5)',
        font={'color': "#f8fafc", 'family': "Plus Jakarta Sans"},
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Severity Rating"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Count"),
        margin=dict(l=20, r=20, t=20, b=40),
        height=260
    )
    st.plotly_chart(fig_impact, use_container_width=True)

st.divider()

# ============================================================
# 3. SPECIFIC ENTERPRISE DEPENDENCIES & SLA CONTROL MATRIX
# ============================================================

st.subheader("Enterprise System Dependencies & SLA Control Matrix")

st.markdown("Detailed breakdown of extracted system interfaces, SLA compliance ratings, and fallback redundancy controls:")

st.dataframe(df_dep, use_container_width=True, hide_index=True)

st.divider()

# ============================================================
# 4. DEPENDENCY FALLBACK & REDUNDANCY GOVERNANCE PLAN
# ============================================================

st.subheader("Dependency Fallback & Governance Resilience Plan")

fb1, fb2 = st.columns(2)

with fb1:
    st.markdown("""
    <div class="glass-card" style="border-left: 4px solid #00f2fe;">
        <h4 style="color: #00f2fe; margin-top: 0; font-weight: 800;">1. Circuit Breaker & Fallback Mocking</h4>
        <p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.6;">
            Automatically isolate failing third-party API endpoints using <strong>Hystrix/Resilience4j circuit breakers</strong>. Redirect traffic to cached local responses or mock harnesses to prevent cascading downtime.
        </p>
    </div>
    """, unsafe_allow_html=True)

with fb2:
    st.markdown("""
    <div class="glass-card" style="border-left: 4px solid #fbbf24;">
        <h4 style="color: #fbbf24; margin-top: 0; font-weight: 800;">2. Vendor SLA Escalation & Multi-Region Nodes</h4>
        <p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.6;">
            Enforce SLA compliance with automated uptime ping telemetry. Maintain secondary multi-region cloud nodes to absorb provider outages without interrupting end-user workflows.
        </p>
    </div>
    """, unsafe_allow_html=True)