import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.ui import inject_css, page_header

inject_css()
page_header("Non-IT Operational & Supplier Dependencies", "Monitor vendor contracts, material supply chains, regulatory approvals, and operational handoffs.")

project = st.session_state.get("selected_project", {})
if not project:
    st.warning("Please upload a Non-IT project document first.")
    st.page_link("pages/12_Non_IT_Document_Upload.py", label="Upload Project Document")
    st.stop()

features = project.get("features", {})
vendor_dep = float(features.get("vendor_dependency_count", 3.0))
ext_dep_score = float(features.get("external_dependency_score", 65.0))

# ============================================================
# 1. EXECUTIVE DEPENDENCY METRICS
# ============================================================

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Suppliers & Contractors", f"{int(vendor_dep)} Primary Vendors")
with c2:
    st.metric("External Dependency Index", f"{ext_dep_score:.1f}/100")
with c3:
    st.metric("Contract SLA Target", "98.5% Baseline")
with c4:
    dep_level ="Critical Load"if ext_dep_score >= 80 else ("High Exposure"if ext_dep_score >= 60 else"Stable")
    st.metric("Supply Chain Exposure", dep_level)

st.divider()

# ============================================================
# 2. DEPENDENCY ANALYTICS & DISTRIBUTION VISUALIZATIONS
# ============================================================

st.subheader("Dependency Categorization & Vulnerability Distribution")

dependencies = project.get("dependencies", [])

if not dependencies or not isinstance(dependencies[0], dict) or "Dependency ID" not in dependencies[0]:
    delivs = project.get("deliverables", [])
    dependencies = [
        {"Dependency ID":"DEP-001","Interface Name":"Primary Material & Equipment Supplier Contract","Category":"Supply Chain","Impact":"CRITICAL","SLA Status":"Fixed-Price SLA Locked","Fallback Control":"Secondary Supplier Reserve Reserve"},
        {"Dependency ID":"DEP-002","Interface Name":"Local Government Regulatory Permit & Environmental License","Category":"Regulatory","Impact":"HIGH","SLA Status":"Permit Approval Pending","Fallback Control":"Expedited Legal & Permit Liaison"},
        {"Dependency ID":"DEP-003","Interface Name": f"Third-Party Logistics & Freight Transport for {delivs[0] if delivs else'Primary Operations'}","Category":"Logistics","Impact":"HIGH","SLA Status":"Active Dispatch SLA","Fallback Control":"Backup Regional Freight Carriers"},
        {"Dependency ID":"DEP-004","Interface Name":"Site Quality Inspection & Safety Audit Board","Category":"Governance","Impact":"MEDIUM","SLA Status":"Active Monitoring","Fallback Control":"Pre-Audit Internal Site Certification"}
    ]

df_dep = pd.DataFrame(dependencies)

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("<h4 style='color: #fbbf24; font-size: 1rem;'>1. Dependency Category Breakdown</h4>", unsafe_allow_html=True)
    cat_counts = df_dep["Category"].value_counts()
    fig_cat = go.Figure(data=[go.Pie(
        labels=cat_counts.index,
        values=cat_counts.values,
        hole=.5,
        marker=dict(colors=["#fbbf24", "#00f2fe", "#ef4444", "#10b981"]),
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
    st.markdown("<h4 style='color: #fbbf24; font-size: 1rem;'>2. Vulnerability Impact Severity</h4>", unsafe_allow_html=True)
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

st.subheader("Operational Dependencies & Supplier SLA Matrix")

st.markdown("Detailed breakdown of extracted supplier interfaces, regulatory permits, and SLA contingency controls:")

st.dataframe(df_dep, use_container_width=True, hide_index=True)

st.divider()

# ============================================================
# 4. DEPENDENCY FALLBACK & REDUNDANCY GOVERNANCE PLAN
# ============================================================

st.subheader("Supply Chain & Contingency Governance Plan")

fb1, fb2 = st.columns(2)

with fb1:
    st.markdown("""
    <div class="glass-card" style="border-left: 4px solid #fbbf24;">
        <h4 style="color: #fbbf24; margin-top: 0; font-weight: 800;">1. Dual-Sourcing & Material Reserves</h4>
        <p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.6;">
            Contract secondary equipment suppliers and establish buffer material reserves at regional warehouses to insulate site execution from single-vendor lead time delays.
        </p>
    </div>
    """, unsafe_allow_html=True)

with fb2:
    st.markdown("""
    <div class="glass-card" style="border-left: 4px solid #10b981;">
        <h4 style="color: #10b981; margin-top: 0; font-weight: 800;">2. Regulatory Permit & Expedited Sign-Offs</h4>
        <p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.6;">
            Pre-audit site blueprints with local compliance officers and submit expedited environmental filings early in Phase 1 to eliminate phase handover delays.
        </p>
    </div>
    """, unsafe_allow_html=True)
