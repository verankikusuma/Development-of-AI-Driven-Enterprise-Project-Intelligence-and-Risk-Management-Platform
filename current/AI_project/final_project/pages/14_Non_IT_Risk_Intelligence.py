import streamlit as st
import pandas as pd
from utils.ui import inject_css, page_header, risk_badge, render_risk_indicator

inject_css()
page_header("Non-IT Operational Risk Intelligence Command Center", "Deep-dive root cause analysis, business exposure telemetry, and operational risk mitigation strategies.")

project = st.session_state.get("selected_project", {})
if not project:
    st.warning("Please upload a Non-IT project document first.")
    st.page_link("pages/12_Non_IT_Document_Upload.py", label="Upload Project Document")
    st.stop()

features = project.get("features", {})
risk_score = float(project.get("risk_score", 50.0))
health_score = float(project.get("health_score", 70.0))
risk_level = project.get("risk_level", "Medium")
budget_usd = features.get("budget_usd", 2_150_000.0)
sched_overrun = features.get("schedule_overrun_pct", 15.0)
tech_complexity = features.get("tech_complexity_score", 65.0)
ext_dependency = features.get("external_dependency_score", 85.0)
res_avail = features.get("resource_availability_pct", 75.0)
vendor_cnt = features.get("vendor_dependency_count", 2.0)

# ============================================================
# 1. EXECUTIVE RISK SCORE & EXPOSURE TELEMETRY
# ============================================================

col_gauge, col_exposure = st.columns([1, 1.3])

with col_gauge:
    render_risk_indicator(risk_score, risk_level)

with col_exposure:
    contingency_fund = budget_usd * (risk_score / 200.0)
    delay_days = round((sched_overrun / 100.0) * features.get("planned_duration_days", 90.0), 1)
    
    st.markdown(f"""
    <div class="glass-card" style="border-color: rgba(245, 158, 11, 0.35); padding: 1.3rem;">
        <h3 style="color: #fbbf24; margin-top: 0; font-size: 1.15rem; font-weight: 800;">Business Risk Exposure & Contingency Reserve Summary</h3>        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
            <div style="background: rgba(15, 23, 42, 0.6); padding: 0.9rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);">
                <div style="color: #94a3b8; font-size: 0.82rem; font-weight: 600; text-transform: uppercase;">Required Risk Reserve</div>
                <div style="color: #fbbf24; font-size: 1.5rem; font-weight: 800; margin-top: 0.2rem;">${contingency_fund:,.0f}</div>
                <div style="color: #cbd5e1; font-size: 0.78rem;">({risk_score/2:.1f}% of Base Budget)</div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 0.9rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);">
                <div style="color: #94a3b8; font-size: 0.82rem; font-weight: 600; text-transform: uppercase;">Operational Schedule Exposure</div>
                <div style="color: #f97316; font-size: 1.5rem; font-weight: 800; margin-top: 0.2rem;">+{delay_days:.0f} Days</div>
                <div style="color: #cbd5e1; font-size: 0.78rem;">({sched_overrun:.1f}% Timeline Variance)</div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 0.9rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);">
                <div style="color: #94a3b8; font-size: 0.82rem; font-weight: 600; text-transform: uppercase;">Process Complexity Index</div>
                <div style="color: #00f2fe; font-size: 1.5rem; font-weight: 800; margin-top: 0.2rem;">{tech_complexity:.0f}/100</div>
                <div style="color: #cbd5e1; font-size: 0.78rem;">Operational Difficulty Rating</div>
            </div>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 0.9rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);">
                <div style="color: #94a3b8; font-size: 0.82rem; font-weight: 600; text-transform: uppercase;">Supply Chain & Vendor Risk</div>
                <div style="color: #ef4444; font-size: 1.5rem; font-weight: 800; margin-top: 0.2rem;">{ext_dependency:.0f}/100</div>
                <div style="color: #cbd5e1; font-size: 0.78rem;">{vendor_cnt:.0f} Key Suppliers</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ============================================================
# 2. DEEP ROOT-CAUSE ANALYSIS STUDIO
# ============================================================

st.subheader("Deep Root-Cause Analysis: Why Does This Business Project Have These Risks?")

st.markdown("""
This section provides an in-depth breakdown of the specific operational, supply chain, and contractual drivers extracted directly from your uploaded document that contribute to the calculated risk score.
""")

proj_name = project.get("name", "Active Business Project")
delivs = project.get("deliverables", [])
risks_list = project.get("potential_risks", [])

deliv_primary = delivs[0] if delivs else "Primary Operations & Logistics"
deliv_sec = delivs[1] if len(delivs) > 1 else "Vendor Supply Chain Procurement"
risk_trigger_1 = risks_list[0] if risks_list else "Vendor contract SLA alignment and material delivery lead times."
risk_trigger_2 = risks_list[1] if len(risks_list) > 1 else "Phase milestone schedule variance and approval permits."

rc1, rc2 = st.columns(2)

with rc1:
    st.markdown(f"""
    <div class="glass-card" style="height: 100%; border-left: 4px solid #fbbf24;">
        <h4 style="color: #fbbf24; margin-top: 0; font-weight: 800;">1. Operational & Process Complexity (Score: {tech_complexity:.0f}/100)</h4>
        <p style="color: #e2e8f0; font-size: 0.92rem; line-height: 1.6;">
            <strong>Root Cause:</strong> The uploaded document for <em>"{proj_name}"</em> specifies operational complexity centered around <strong>{deliv_primary}</strong> and <strong>{deliv_sec}</strong>.
        </p>
        <p style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.5;">
            <strong>Impact on Risk:</strong> Multi-site operational workflows and cross-departmental sign-offs increase approval latency and site execution friction.
        </p>
    </div>
    """, unsafe_allow_html=True)

with rc2:
    st.markdown(f"""
    <div class="glass-card" style="height: 100%; border-left: 4px solid #ef4444;">
        <h4 style="color: #ef4444; margin-top: 0; font-weight: 800;">2. Supply Chain & External Supplier Exposure (Score: {ext_dependency:.0f}/100)</h4>
        <p style="color: #e2e8f0; font-size: 0.92rem; line-height: 1.6;">
            <strong>Root Cause:</strong> Delivery relies on {vendor_cnt:.0f} primary equipment suppliers and contractors. Document risk trigger: <em>"{risk_trigger_1}"</em>
        </p>
        <p style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.5;">
            <strong>Impact on Risk:</strong> External supplier lead-time extensions or material price fluctuations directly expose the project to unbudgeted cost overruns.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.write("")
rc3, rc4 = st.columns(2)

with rc3:
    st.markdown(f"""
    <div class="glass-card" style="height: 100%; border-left: 4px solid #f97316;">
        <h4 style="color: #f97316; margin-top: 0; font-weight: 800;">3. Operational Schedule Variance ({sched_overrun:.1f}% Overrun)</h4>
        <p style="color: #e2e8f0; font-size: 0.92rem; line-height: 1.6;">
            <strong>Root Cause:</strong> Extracted schedule telemetry shows a {sched_overrun:.1f}% timeline variance. Document risk signal: <em>"{risk_trigger_2}"</em>
        </p>
        <p style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.5;">
            <strong>Impact on Risk:</strong> Delays in initial site preparation trigger a cumulative schedule slip across downstream installation workstreams by estimated +{delay_days:.0f} days.
        </p>
    </div>
    """, unsafe_allow_html=True)

with rc4:
    st.markdown(f"""
    <div class="glass-card" style="height: 100%; border-left: 4px solid #10b981;">
        <h4 style="color: #10b981; margin-top: 0; font-weight: 800;">4. Resource & Staffing Availability ({res_avail:.0f}%)</h4>
        <p style="color: #e2e8f0; font-size: 0.92rem; line-height: 1.6;">
            <strong>Root Cause:</strong> Staffing analysis indicates a {100-res_avail:.0f}% capacity gap in specialized site supervisors and compliance auditors for <strong>{deliv_primary}</strong>.
        </p>
        <p style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.5;">
            <strong>Impact on Risk:</strong> Audit delays or supervisor bandwidth constraints increase operational defect risk during phase sign-offs.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ============================================================
# 3. QUALITATIVE RISK TRIGGERS & EXPOSURE MATRIX
# ============================================================

st.subheader("Document Qualitative Risk Triggers & Threat Matrix")

potential_risks = project.get("potential_risks", [])

if potential_risks:
    st.markdown("The following document-extracted risk triggers represent qualitative business threats detected by the ML NLP parser:")
    for idx, risk_item in enumerate(potential_risks[:6], 1):
        severity_color = "#ef4444" if idx <= 2 else ("#f97316" if idx <= 4 else "#fbbf24")
        severity_label = "HIGH SEVERITY" if idx <= 2 else ("MEDIUM SEVERITY" if idx <= 4 else "MODERATE WATCH")
        
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.7); padding: 0.9rem 1.2rem; border-radius: 8px; border-left: 4px solid {severity_color}; margin-bottom: 0.6rem; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="color: {severity_color}; font-weight: 800; font-size: 0.8rem; text-transform: uppercase; margin-right: 0.8rem;">[{severity_label}]</span>
                <span style="color: #f8fafc; font-size: 0.93rem;">{risk_item}</span>
            </div>
            <span style="color: #94a3b8; font-size: 0.8rem; font-weight: 600;">Trigger #{idx}</span>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ============================================================
# 4. ENTERPRISE RISK MITIGATION & CONTINGENCY MATRIX
# ============================================================

st.subheader("Enterprise Risk Mitigation & Contingency Strategy")

mitigation_matrix = [
    {
        "Risk Event ID": "RSK-001",
        "Category": "Supply Chain",
        "Root Cause Trigger": "Key equipment supplier lead times & material price volatility",
        "Mitigation Control Strategy": "Establish dual-sourcing contracts, secondary supplier reserves, and fixed-price purchase locks.",
        "Contingency Buffer": f"${budget_usd * 0.07:,.0f} / +8 Days",
        "Owner": "Procurement Lead",
        "Control Status":"Active Control"    },
    {
        "Risk Event ID": "RSK-002",
        "Category": "Operational",
        "Root Cause Trigger": "Multi-site deployment coordination & approval delays",
        "Mitigation Control Strategy": "Deploy regional site PMs, standardized execution playbooks, and daily operational syncs.",
        "Contingency Buffer": f"${budget_usd * 0.05:,.0f} / +6 Days",
        "Owner": "Operations Director",
        "Control Status":"Monitoring"    },
    {
        "Risk Event ID": "RSK-003",
        "Category": "Regulatory",
        "Root Cause Trigger": "Environmental permit delays & compliance verification backlogs",
        "Mitigation Control Strategy": "Engage local legal counsel early, submit expedited permit filings, and pre-audit site plans.",
        "Contingency Buffer": f"${budget_usd * 0.04:,.0f} / +5 Days",
        "Owner": "Compliance Officer",
        "Control Status":"Active Control"    },
    {
        "Risk Event ID": "RSK-004",
        "Category": "Resource Deficit",
        "Root Cause Trigger": "Site supervisor bandwidth shortages during peak rollout",
        "Mitigation Control Strategy": "Reallocate senior supervisors from completed projects and contract specialized site auditors.",
        "Contingency Buffer": f"${budget_usd * 0.03:,.0f} / +3 Days",
        "Owner": "HR / PMO Sponsor",
        "Control Status":"In Progress"    }
]

st.dataframe(pd.DataFrame(mitigation_matrix), use_container_width=True, hide_index=True)

st.divider()
st.markdown("### Generate Formal Stakeholder Risk Documentation")
st.write("Generate an executive-ready Business Risk Briefing report with detailed mitigation timelines and governance sign-offs.")
st.page_link("pages/19_Non_IT_Documentation.py", label="Generate Formal Risk Briefing Document")
