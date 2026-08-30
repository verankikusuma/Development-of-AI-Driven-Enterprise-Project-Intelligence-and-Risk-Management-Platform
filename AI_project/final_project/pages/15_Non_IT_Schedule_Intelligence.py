import streamlit as st
import pandas as pd
from utils.ui import (
    inject_css, page_header, render_gantt_chart,
    render_timeline_burnup_chart, render_phase_duration_chart, render_schedule_buffer_chart
)

inject_css()
page_header("Non-IT Business Schedule & Milestone Intelligence Suite", "Comprehensive multi-chart operational timeline analytics, velocity burnup trends, and critical path bottleneck identification.")

project = st.session_state.get("selected_project", {})
if not project:
    st.warning("Please upload a Non-IT project document first.")
    st.page_link("pages/12_Non_IT_Document_Upload.py", label="Upload Document")
    st.stop()

features = project.get("features", {})
def safe_num(val, default=0.0):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default

planned_days = safe_num(features.get("planned_duration_days", 90.0))
sched_overrun_pct = safe_num(features.get("schedule_overrun_pct", 15.0))
delay_days = round((planned_days * (sched_overrun_pct / 100.0)), 1)
elapsed_days = round(planned_days * 0.55, 1)

# ============================================================
# 1. EXECUTIVE TIMELINE METRICS
# ============================================================

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Target Planned Timeline", f"{int(planned_days)} Days")
with c2:
    st.metric("Elapsed Schedule Time", f"{int(elapsed_days)} Days")
with c3:
    st.metric("Timeline Delay Exposure", f"+{delay_days:.0f} Days", delta=f"{sched_overrun_pct:.1f}% Variance", delta_color="inverse")
with c4:
    schedule_health ="On Track"if sched_overrun_pct <= 5 else ("Watchlist"if sched_overrun_pct <= 15 else"At Risk")
    st.metric("Operational Schedule State", schedule_health)

st.divider()

# ============================================================
# 2. INTERACTIVE TIMELINE ANALYTICS SUITE (4 CHARTS)
# ============================================================

st.subheader("Interactive Milestone & Operational Velocity Suite")

tab1, tab2 = st.tabs(["Phased Gantt Progress & Burnup","Phase Duration & Schedule Allocation"])

with tab1:
    col_gantt, col_burnup = st.columns(2)
    with col_gantt:
        st.markdown("<h4 style='color: #fbbf24; font-size: 1rem;'>1. Phased Business Milestone Gantt Progress</h4>", unsafe_allow_html=True)
        milestones = project.get("milestones", [])
        fig_gantt = render_gantt_chart(milestones)
        if fig_gantt:
            st.plotly_chart(fig_gantt, use_container_width=True)
        else:
            st.info("No milestone data extracted.")

    with col_burnup:
        st.markdown("<h4 style='color: #fbbf24; font-size: 1rem;'>2. Velocity Burnup (Target vs Actual Trajectory)</h4>", unsafe_allow_html=True)
        fig_burnup = render_timeline_burnup_chart(planned_days, sched_overrun_pct)
        st.plotly_chart(fig_burnup, use_container_width=True)

with tab2:
    col_duration, col_buffer = st.columns(2)
    with col_duration:
        st.markdown("<h4 style='color: #fbbf24; font-size: 1rem;'>3. Phase-by-Phase Planned vs Actual Duration</h4>", unsafe_allow_html=True)
        fig_duration = render_phase_duration_chart(milestones, planned_days, sched_overrun_pct)
        st.plotly_chart(fig_duration, use_container_width=True)

    with col_buffer:
        st.markdown("<h4 style='color: #fbbf24; font-size: 1rem;'>4. Time Allocation & Delay Exposure Breakdown</h4>", unsafe_allow_html=True)
        fig_buffer = render_schedule_buffer_chart(sched_overrun_pct)
        st.plotly_chart(fig_buffer, use_container_width=True)

st.divider()

# ============================================================
# 3. CRITICAL PATH BOTTLENECK MATRIX
# ============================================================

st.subheader("Critical Path Bottleneck & Operational Delay Matrix")

delivs = project.get("deliverables", [])
deliv_1 = delivs[0] if delivs else "Primary Operations"
deliv_2 = delivs[1] if len(delivs) > 1 else "Procurement & Logistics"

bottleneck_data = [
    {
        "Phase Name": "Phase 1: Project Initiation & Permits",
        "Critical Path Status":"Completed",
        "Planned Days": f"{planned_days*0.22:.0f} Days",
        "Actual Days": f"{planned_days*0.22:.0f} Days",
        "Delay Variance": "0 Days",
        "Primary Bottleneck Cause": "None (Regulatory permits & charter approved)",
        "Owner": "Project Director"
    },
    {
        "Phase Name": f"Phase 2: {deliv_1}",
        "Critical Path Status":"Critical Bottleneck",
        "Planned Days": f"{planned_days*0.28:.0f} Days",
        "Actual Days": f"{(planned_days*0.28) + (delay_days*0.6):.0f} Days",
        "Delay Variance": f"+{delay_days*0.6:.0f} Days",
        "Primary Bottleneck Cause": f"Vendor material lead-time delays for {deliv_1}",
        "Owner": "Procurement Lead"
    },
    {
        "Phase Name": f"Phase 3: {deliv_2}",
        "Critical Path Status":"In Progress / Watch",
        "Planned Days": f"{planned_days*0.25:.0f} Days",
        "Actual Days": f"{(planned_days*0.25) + (delay_days*0.4):.0f} Days",
        "Delay Variance": f"+{delay_days*0.4:.0f} Days",
        "Primary Bottleneck Cause": "Site inspection clearance and supervisor audit sign-offs",
        "Owner": "Operations Lead"
    },
    {
        "Phase Name": "Phase 4: Operational Handover & Sign-Off",
        "Critical Path Status":"Scheduled",
        "Planned Days": f"{planned_days*0.25:.0f} Days",
        "Actual Days": f"{planned_days*0.25:.0f} Days Target",
        "Delay Variance": "0 Days Slack",
        "Primary Bottleneck Cause": "Dependent on Phase 3 operational site clearance",
        "Owner": "Executive Sponsor"
    }
]

st.dataframe(pd.DataFrame(bottleneck_data), use_container_width=True, hide_index=True)

st.divider()

# ============================================================
# 4. WHAT-IF SCHEDULE RECOVERY SIMULATOR
# ============================================================

st.subheader("What-If Schedule Recovery & Fast-Tracking Simulator")

st.markdown("Test how applying operational crash-scheduling reduces site delivery delay exposure:")

sim_col1, sim_col2 = st.columns([1.2, 1])

with sim_col1:
    additional_supervisors = st.slider("Deploy Additional Site Supervisors & Contractors", 0, 5, 2)
    fast_track_procurement = st.checkbox("Fast-Track Supplier Shipping & Expedited Customs Clearance", value=True)
    
    recovered_days = (additional_supervisors * 3.0) + (7.0 if fast_track_procurement else 0.0)
    net_delay = max(0.0, delay_days - recovered_days)

with sim_col2:
    st.markdown(f"""
    <div class="glass-card" style="border-color: rgba(16, 185, 129, 0.35); padding: 1.2rem;">
        <h4 style="color: #10b981; margin-top: 0; font-weight: 800;">Simulated Timeline Recovery</h4>
        <p><strong>Baseline Delay Exposure:</strong> <span style="color:#ef4444;">+{delay_days:.0f} Days</span></p>
        <p><strong>Recovered Timeline Days:</strong> <span style="color:#10b981;">-{recovered_days:.0f} Days</span></p>
        <p><strong>Net Projected Delay:</strong> <span style="color:#fbbf24;">+{net_delay:.0f} Days</span></p>
        <p><strong>Revised Schedule State:</strong>{"On Track"if net_delay <= 3 else"Acceptable Variance"}</p>    </div>
    """, unsafe_allow_html=True)
