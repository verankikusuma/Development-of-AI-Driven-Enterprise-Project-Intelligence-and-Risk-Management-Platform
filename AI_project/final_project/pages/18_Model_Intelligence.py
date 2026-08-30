import streamlit as st
import pandas as pd
from utils.ui import inject_css, page_header, render_model_quality
from utils.dataset_analyzer import (
    load_dataset, get_dataset_metadata,
    render_it_vs_non_it_chart, render_risk_distribution_chart,
    render_budget_vs_risk_chart, render_key_feature_stats_chart
)

# ============================================================
# PAGE SETUP
# ============================================================

inject_css()

page_header(
    "About the Underlying ML Model",
    "Training dataset statistics, feature importance, and model accuracy metrics. This data describes how the risk prediction models were built — it is not related to your uploaded documents."
)

st.markdown("""
> **Important:** The statistics below describe the **model's training corpus** (200,000 synthetic project records used to train the XGBoost and Random Forest risk classifiers).
> They do **not** reflect your uploaded project documents. To see your document-specific analytics, visit the **Project Analysis** page.
""")

# ============================================================
# 1. TRAINING DATASET TELEMETRY KPIs
# ============================================================

meta = get_dataset_metadata()

st.subheader("Training Dataset Telemetry")

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
        <div class="metric-card-sub" style="color:#cbd5e1;">Training Rows</div>
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
        <div class="metric-card-title">IT Records</div>        <div class="metric-card-value" style="color:#38bdf8;">{meta['it_count']:,}</div>
        <div class="metric-card-sub" style="color:#cbd5e1;">{(meta['it_count']/max(1, meta['total_records'])*100):.1f}% of Dataset</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-card-title">Non-IT Records</div>        <div class="metric-card-value" style="color:#fbbf24;">{meta['non_it_count']:,}</div>
        <div class="metric-card-sub" style="color:#cbd5e1;">{(meta['non_it_count']/max(1, meta['total_records'])*100):.1f}% of Dataset</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ============================================================
# 2. TRAINING DATASET CHARTS
# ============================================================

st.subheader("Training Dataset Analysis & Distribution Visualizations")

tab1, tab2 = st.tabs(["Domain & Risk Distributions", "Correlation & Feature Analytics"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        fig_domain = render_it_vs_non_it_chart()
        if fig_domain:
            st.plotly_chart(fig_domain, use_container_width=True)
    with c2:
        fig_risk = render_risk_distribution_chart()
        if fig_risk:
            st.plotly_chart(fig_risk, use_container_width=True)

with tab2:
    c3, c4 = st.columns(2)
    with c3:
        fig_budget = render_budget_vs_risk_chart()
        if fig_budget:
            st.plotly_chart(fig_budget, use_container_width=True)
    with c4:
        fig_stats = render_key_feature_stats_chart()
        if fig_stats:
            st.plotly_chart(fig_stats, use_container_width=True)

st.divider()

# ============================================================
# 3. MODEL ACCURACY & QUALITY METRICS
# ============================================================

st.subheader("Model Accuracy & Quality")

col_it, col_nonit = st.columns(2)

with col_it:
    st.markdown("""
    <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.35);">
        <h4 style="color:#38bdf8; margin-top:0; font-weight:800;">IT Risk Model (XGBoost)</h4>
    </div>
    """, unsafe_allow_html=True)
    render_model_quality("IT")

with col_nonit:
    st.markdown("""
    <div class="glass-card" style="border-color: rgba(245, 158, 11, 0.35);">
        <h4 style="color:#fbbf24; margin-top:0; font-weight:800;">Non-IT Risk Model (Random Forest)</h4>
    </div>
    """, unsafe_allow_html=True)
    render_model_quality("Non-IT")

st.divider()

# ============================================================
# 4. DATASET COLUMN REFERENCE
# ============================================================

st.subheader("Training Dataset Column Reference")

columns = meta.get("columns", [])
if columns:
    col_df = pd.DataFrame({"Column Name": columns, "Index": range(len(columns))})
    st.dataframe(col_df, use_container_width=True, hide_index=True)
else:
    st.info("Dataset columns not available — ensure project_risk_dataset.csv is present in ml_models/.")
