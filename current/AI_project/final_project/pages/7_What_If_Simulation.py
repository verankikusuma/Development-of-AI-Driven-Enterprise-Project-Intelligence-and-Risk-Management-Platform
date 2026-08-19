import streamlit as st
from utils.ui import inject_css, page_header, render_what_if_chart
from utils.api_client import backend_health, api_simulate_scenario

inject_css()

page_header(
    "What-If Risk Simulation Engine",
    "Simulate project scenario perturbations (delays, budget variance, resource reductions) via backend API endpoints."
)

project = st.session_state.get("selected_project")
if not project:
    st.warning("Please upload an IT project first.")
    st.page_link("pages/2_Document_Upload.py", label="Upload Project")
    st.stop()

# ============================================================
# SIMULATION INPUTS
# ============================================================

st.subheader("Simulation Parameters")

col_s1, col_s2, col_s3 = st.columns(3)

with col_s1:
    delay_days = st.slider("Additional Schedule Delay (Days)", 0, 90, 15)
with col_s2:
    budget_change = st.slider("Budget Overrun / Reduction (%)", -30, 50, 10)
with col_s3:
    team_reduction = st.slider("Team Turnover / Reduction (%)", 0, 50, 10)

# ============================================================
# SIMULATION EXECUTION VIA BACKEND API
# ============================================================

if st.button("Run What-If Simulation", type="primary", use_container_width=True):
    baseline_score = float(project.get("risk_score", 40.0))
    api_base = st.session_state.get("api_base", "http://127.0.0.1:8000")
    
    with st.spinner("Executing simulation via Backend API..."):
        api_res = None
        if backend_health(api_base):
            api_res = api_simulate_scenario(baseline_score, delay_days, budget_change, team_reduction, base_url=api_base)
            
        if api_res and "simulated_score" in api_res:
            simulated_risk_score = float(api_res["simulated_score"])
            engine_source = "FastAPI Backend API Endpoint"
        else:
            simulated_risk_score = min(100.0, max(0.0, baseline_score + (delay_days * 0.75) + (budget_change * 0.4) + (team_reduction * 0.6)))
            engine_source = "Embedded Simulation Engine"

    st.divider()
    st.subheader("Simulation Results & Visual Impact Comparison")
    st.caption(f"Execution Engine: `{engine_source}`")
    
    col_chart, col_metrics = st.columns([1.2, 1])
    
    with col_chart:
        st.plotly_chart(render_what_if_chart(baseline_score, simulated_risk_score, 0, delay_days), use_container_width=True)
        
    with col_metrics:
        st.metric("Baseline Risk Score", f"{baseline_score:.1f}/100")
        st.metric("Simulated Risk Score", f"{simulated_risk_score:.1f}/100", delta=f"+{simulated_risk_score - baseline_score:.1f}")
        
        if simulated_risk_score >= 70:
            st.error("High Risk Scenario: Simulated parameters push project into critical threshold!")
        elif simulated_risk_score >= 45:
            st.warning("Moderate Risk Scenario: Monitor milestones closely.")
        else:
            st.success("Manageable Scenario: Risk remains within target limits.")

    st.divider()
    st.subheader("Strategic AI Recommendation")
    
    if delay_days > 20:
        st.info("**Schedule Intervention:** Consider fast-tracking critical path deliverables or bringing in specialized external contractors.")
    elif team_reduction > 15:
        st.info("**Resource Intervention:** High team turnover increases knowledge leakage risk. Pair core developers with cross-trained junior engineers.")
    else:
        st.info("**Status Quo:** Current scenario requires routine weekly progress check-ins without major resource reallocation.")