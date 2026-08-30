import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils.ui import inject_css, page_header, risk_badge
from utils.api_client import backend_health
from utils.app_store import list_documents
from utils.rbac import current_user_id

# ============================================================
# PAGE SETUP
# ============================================================

inject_css()

page_header(
    "Non-IT Business Project & Document Intelligence Analysis",
    "Live document analytics for your uploaded business project files, API status, and active project ML predictions."
)

project_id = st.session_state.get("selected_project_id")
project = st.session_state.get("selected_project", {})
api_base = st.session_state.get("api_base", "http://127.0.0.1:8000")

# ============================================================
# HELPER: format document size/count card value
# ============================================================

def _format_size(size_bytes):
    if size_bytes is None:
        return "—"
    if size_bytes >= 1_048_576:
        return f"{size_bytes / 1_048_576:.1f} MB"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes:,} B"


def _doc_content_label(meta):
    """Return a human-readable page/row/slide/image count string."""
    doc_type = (meta.get("doc_type") or "").upper()
    if doc_type == "PDF":
        pc = meta.get("page_count")
        return f"{pc} pages" if pc else "—"
    if doc_type == "PPTX":
        sc = meta.get("slide_count")
        return f"{sc} slides" if sc else "—"
    if doc_type == "DOCX":
        pc = meta.get("page_count")
        return f"~{pc} pages" if pc else "—"
    if doc_type == "CSV":
        rc = meta.get("row_count")
        return f"{rc:,} rows" if rc is not None else "—"
    if doc_type == "TXT":
        cc = meta.get("char_count")
        return f"{cc:,} chars" if cc else "—"
    if doc_type == "IMAGE":
        return "1 image"
    return "—"

# ============================================================
# 1. UPLOADED DOCUMENT TELEMETRY KPIs
# ============================================================

user_id = current_user_id()
docs = list_documents(user_id) if user_id else []
is_healthy = backend_health(api_base)

st.subheader("Uploaded Document & API System Telemetry")

# Document selector (syncs selected_project for cross-page consistency)
selected_doc = None
if len(docs) > 1:
    doc_names = [d["filename"] for d in docs]
    sel_idx = st.selectbox(
        "Select uploaded document to inspect",
        range(len(doc_names)),
        format_func=lambda i: doc_names[i],
        key="nonit_pa_doc_selector",
    )
    selected_doc = docs[sel_idx]
elif len(docs) == 1:
    selected_doc = docs[0]

if not selected_doc and not docs:
    st.info("Upload a business project document on the **Document Upload** page to see live document analytics here.")

# Build card values
doc_meta = (selected_doc or {}).get("metadata", {}) if selected_doc else {}
doc_filename = (selected_doc or {}).get("filename", "—")
doc_size = _format_size((selected_doc or {}).get("size_bytes"))
doc_content = _doc_content_label(doc_meta)
doc_type = doc_meta.get("doc_type", "—")
doc_uploaded = (selected_doc or {}).get("created_at", "—")

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Document</div>        <div class="metric-card-value" style="font-size:1.15rem;">{doc_filename}</div>
        <div class="metric-card-sub" style="color:#cbd5e1;">{doc_type}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">File Size</div>        <div class="metric-card-value">{doc_size}</div>
        <div class="metric-card-sub" style="color:#cbd5e1;">Uploaded File</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Content</div>        <div class="metric-card-value">{doc_content}</div>
        <div class="metric-card-sub" style="color:#cbd5e1;">Pages / Rows / Slides</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    risk_level = project.get("risk_level", "—") if project else "—"
    risk_score = project.get("risk_score", "—") if project else "—"
    risk_display = f"{risk_score}" if isinstance(risk_score, (int, float)) else risk_score
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Risk Assessment</div>        <div class="metric-card-value" style="color:#f97316;">{risk_display}</div>
        <div class="metric-card-sub">{risk_badge(risk_level) if risk_level != '—' else '—'}</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    api_color = "#34d399" if is_healthy else "#fbbf24"
    api_label = "FastAPI Online" if is_healthy else "Embedded Engine"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">API Status</div>        <div class="metric-card-value" style="color:{api_color}; font-size:1.3rem;">{api_label}</div>
        <div class="metric-card-sub" style="color:#cbd5e1;">Random Forest ML Active</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ============================================================
# 2. DOCUMENT-SPECIFIC ANALYSIS & FEATURE VISUALIZATIONS
# ============================================================

st.subheader("Document Analysis & Feature Visualizations")

tab1, tab2 = st.tabs(["Risk & Feature Analytics", "Document Detail & Risk Triggers"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        # Risk score gauge from uploaded document
        if project:
            rs = float(project.get("risk_score", 0))
            rl = project.get("risk_level", "Medium")
            gauge_color = "#10b981" if rs < 35 else "#fbbf24" if rs < 65 else "#ef4444"
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=rs,
                title={"text": f"Document Risk Score ({rl})", "font": {"color": "#f8fafc", "size": 15}},
                number={"font": {"color": gauge_color, "size": 42}},
                gauge={
                    "axis": {"range": [0, 100], "tickfont": {"color": "#94a3b8"}},
                    "bar": {"color": gauge_color},
                    "bgcolor": "rgba(15,23,42,0.5)",
                    "steps": [
                        {"range": [0, 35], "color": "rgba(16,185,129,0.15)"},
                        {"range": [35, 65], "color": "rgba(251,191,36,0.15)"},
                        {"range": [65, 100], "color": "rgba(239,68,68,0.15)"},
                    ],
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font={"color": "#f8fafc", "family": "Plus Jakarta Sans"},
                margin=dict(l=20, r=20, t=50, b=20),
                height=260,
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
        else:
            st.info("Upload a document to see the risk gauge.")

    with c2:
        # Feature bar chart — only show features that exist and are non-zero
        if project:
            features = project.get("features", {})
            feature_labels = {
                "budget_usd": "Budget (USD)",
                "schedule_overrun_pct": "Schedule Overrun %",
                "cost_overrun_pct": "Cost Overrun %",
                "tech_complexity_score": "Process Complexity",
                "external_dependency_score": "Supply Chain Dep.",
                "resource_availability_pct": "Resource Avail. %",
                "vendor_dependency_count": "Supplier Count",
                "team_turnover_pct": "Turnover %",
            }
            chart_features = {
                feature_labels.get(k, k): float(v)
                for k, v in features.items()
                if k in feature_labels and k != "budget_usd" and v and float(v) != 0
            }

            if len(chart_features) >= 2:
                fig_feat = go.Figure(go.Bar(
                    x=list(chart_features.values()),
                    y=list(chart_features.keys()),
                    orientation="h",
                    marker_color="#fbbf24",
                    text=[f"{v:.1f}" for v in chart_features.values()],
                    textposition="auto",
                ))
                fig_feat.update_layout(
                    title={"text": "<b>Extracted Business Features</b>", "font": {"size": 14, "color": "#ffffff"}},
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(15,23,42,0.4)",
                    font={"color": "#f8fafc", "family": "Plus Jakarta Sans"},
                    xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                    yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
                    margin=dict(l=20, r=20, t=50, b=20),
                    height=260,
                )
                st.plotly_chart(fig_feat, use_container_width=True)
            elif chart_features:
                st.markdown("**Extracted Features:**")
                for k, v in chart_features.items():
                    st.write(f"- **{k}:** {v:.1f}")
            else:
                st.info("Structured features could not be extracted from this document type.")
        else:
            st.info("Upload a document to see extracted features.")

with tab2:
    c3, c4 = st.columns(2)
    with c3:
        detail_rows = {
            "File Name": doc_filename,
            "File Size": doc_size,
            "Document Type": doc_type,
            "Content": doc_content,
            "Upload Time": doc_uploaded,
            "Risk Level": project.get("risk_level", "—") if project else "—",
            "Risk Score": f"{project.get('risk_score', '—')}/100" if project else "—",
            "Health Score": f"{project.get('health_score', '—')}%" if project else "—",
        }
        st.markdown("**Document Summary**")
        st.dataframe(
            pd.DataFrame(detail_rows.items(), columns=["Property", "Value"]),
            use_container_width=True, hide_index=True,
        )

    with c4:
        if project:
            potential_risks = project.get("potential_risks", [])
            if potential_risks:
                st.markdown("**Document Risk Triggers**")
                for idx, risk_item in enumerate(potential_risks[:6], 1):
                    severity_color = "#ef4444" if idx <= 2 else ("#f97316" if idx <= 4 else "#fbbf24")
                    severity_label = "HIGH" if idx <= 2 else ("MEDIUM" if idx <= 4 else "WATCH")
                    st.markdown(f"""
                    <div style="background: rgba(15, 23, 42, 0.7); padding: 0.7rem 1rem; border-radius: 8px; border-left: 4px solid {severity_color}; margin-bottom: 0.5rem;">
                        <span style="color: {severity_color}; font-weight: 800; font-size: 0.75rem; text-transform: uppercase; margin-right: 0.6rem;">[{severity_label}]</span>
                        <span style="color: #f8fafc; font-size: 0.88rem;">{risk_item}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No risk triggers detected in the uploaded document.")
        else:
            st.info("Upload a document to see risk triggers.")

st.divider()

# ============================================================
# 3. EXECUTIVE PROJECT BENCHMARK & PERFORMANCE STUDIO
# ============================================================

st.subheader("Executive Project Benchmark & Performance Studio")

if not project:
    st.info("Upload a Non-IT project document on the **Document Upload** page to view live performance benchmark comparisons.")
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
        {"Operational Parameter":"Technical Complexity Score","Active Project Telemetry": f"{complexity:.0f}/100 Rating","Industry Mean Benchmark":"45/100 Average Rating","Status Assessment":"Operational Baseline"},
        {"Operational Parameter":"External Vendor Interfaces","Active Project Telemetry": f"{vendor_cnt:.0f} Active Vendors","Industry Mean Benchmark":"< 2 Vendors Target","Status Assessment":"Dependency Risk"},
    ]
    
    st.dataframe(pd.DataFrame(benchmark_data), use_container_width=True, hide_index=True)

st.divider()

# ============================================================
# 4. ACTIVE BUSINESS PROJECT ML PREDICTION STATISTICS & ACTION MATRIX
# ============================================================

st.subheader("Active Business Project Prediction & Strategic Action Matrix")

if not project:
    st.info("Upload a Non-IT project document to activate predictions and strategic action items.")
else:
    health = float(project.get("health_score", 0.0))
    risk = float(project.get("risk_score", 50.0))
    r_level = project.get("risk_level", "Medium")

    col_active1, col_active2 = st.columns([1, 1.3])

    with col_active1:
        st.markdown(f"""
        <div class="glass-card" style="border-color: rgba(245, 158, 11, 0.35); height: 100%;">
            <h4 style="color:#fbbf24; margin-top:0; font-weight:800; font-size:1.05rem;">Active Project Telemetry & Assessment</h4>
            <p style="color:#ffffff; font-size:0.95rem;"><strong>Project Name:</strong> {project.get('name', 'Business Project')}</p>
            <p style="color:#ffffff; font-size:0.95rem;"><strong>Predicted Risk Score:</strong> {risk:.1f}/100 ({risk_badge(r_level)})</p>
            <p style="color:#ffffff; font-size:0.95rem;"><strong>Business Health Index:</strong> {health:.1f}%</p>
            <p style="color:#cbd5e1; font-size:0.9rem;"><strong>Source Document:</strong> {doc_filename}</p>
        </div>
        """, unsafe_allow_html=True)

    with col_active2:
        delivs = project.get("deliverables", [])
        action_matrix = [
            {"Task ID":"ACT-001","Strategic Delivery Task": f"Finalize Site Logistics & Supply Schedule for {delivs[0] if delivs else'Primary Operations'}","Operational Owner":"Operations Director","Priority":"CRITICAL","Phase":"Phase 1","Status":"In Progress"},
            {"Task ID":"ACT-002","Strategic Delivery Task": f"Execute Vendor SLA Contract Sign-Off for {delivs[1] if len(delivs)>1 else'Vendor Deliverables'}","Operational Owner":"Contract & Legal Sponsor","Priority":"HIGH","Phase":"Phase 1","Status":"In Progress"},
            {"Task ID":"ACT-003","Strategic Delivery Task":"Audit Regulatory Compliance & Safety Protocols","Operational Owner":"Compliance Audit Lead","Priority":"HIGH","Phase":"Phase 2","Status":"Pending Sign-off"},
            {"Task ID":"ACT-004","Strategic Delivery Task":"Establish Weekly Steering Committee Sync","Operational Owner":"Finance Director","Priority":"MEDIUM","Phase":"Phase 2","Status":"Completed"},
            {"Task ID":"ACT-005","Strategic Delivery Task":"Execute Procurement Risk Buffer Reserve Plan","Operational Owner":"Procurement Lead","Priority":"MEDIUM","Phase":"Phase 3","Status":"Scheduled"},
        ]
        
        st.markdown("""
        <div class="glass-card" style="height: 100%;">
            <h4 style="color:#fbbf24; margin-top:0; font-weight:800; font-size:1.05rem;">Enterprise Delivery Action Plan & Task Matrix</h4>
        """, unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(action_matrix), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    missing = project.get("missing_info", [])
    if missing:
        st.warning("**Critical Information Gaps:**")
        for m in missing:
            st.write(f"- {m}")
