import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from utils.ui import inject_css, page_header, risk_badge
from utils.local_ai import generate_local_document

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ============================================================
# PAGE SETUP
# ============================================================

inject_css()

page_header(
    "Non-IT Business Executive Document Studio",
    "Dynamically generate C-Suite Executive Briefings, Operational Risk Matrices, and Quarterly Project Memos."
)

project = st.session_state.get("selected_project")
if not project:
    st.warning("No active Non-IT project found. Please upload a business document first.")
    st.page_link("pages/12_Non_IT_Document_Upload.py", label="Go to Document Upload")
    st.stop()

documents = st.session_state.get("documents", {})
doc_texts = "\n\n".join(documents.values())

# ============================================================
# LLM & LOCAL GENERATION ENGINE
# ============================================================

def generate_business_doc(doc_type):
    if os.environ.get("USE_CLOUD_AI", "false").lower() != "true" or not GEMINI_API_KEY:
        return generate_local_document(project, doc_type, "Business Leadership")
        
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    if doc_type == "executive":
        prompt = f"""
        Act as a Chief Operating Officer (COO). Write a 1-page Executive Briefing Report for C-suite business leadership based on the following project context.
        
        FORMATTING REQUIREMENTS:
        - Executive Header with Title, Audience, and Risk Score Badge.
        - Strategic Purpose & Operational Scope.
        - Core Performance Metrics Table (| Metric | Status | Baseline Target | Variance |).
        - Key Strategic Deliverables list with bullet icons.
        - Critical Operational Risk Exposure & Triggers.
        - Recommended Executive Decisions Requested.
        
        Project Context:
        {doc_texts[:20000]}
        """
    elif doc_type == "risk":
        prompt = f"""
        Act as an Enterprise Operational Risk Director. Create a formal Operational Risk Matrix Table based on the following context.
        
        FORMATTING REQUIREMENTS:
        - Executive Risk Assessment Overview.
        - Markdown Risk Matrix Table with columns: | ID | Identified Risk Event | Financial/Operational Impact (Critical / High / Medium / Low) | Exposure Likelihood | Mitigation Strategy & Controls | Accountable Risk Owner |
        - Governance & Escalation Protocols.
        
        Project Context:
        {doc_texts[:20000]}
        """
    else:
        prompt = f"""
        Act as a Senior Transformation Director. Generate a quarterly project status memo highlighting key accomplishments, upcoming milestones, financial utilization, and resource requirements.
        
        FORMATTING REQUIREMENTS:
        - Quarterly Status Memo Header.
        - Key Accomplishments & Deliverables Completed.
        - Milestone Progress Table (| Milestone | Completion Target | Status | Progress % |).
        - Financial Allocation & Contingency Buffer Status.
        - Resource & Vendor Dependencies.
        
        Project Context:
        {doc_texts[:20000]}
        """
        
    try:
        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return generate_local_document(project, doc_type, "Business Leadership")

# ============================================================
# DOCUMENT STUDIO CONTROLS
# ============================================================

st.subheader("Business Document Generator Studio")
st.write("Select a document template below to generate formatted, executive-ready documentation grounded in your project data.")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 1.2rem;">
        <div style="font-size: 1.8rem; margin-bottom: 0.4rem;"></div>        <h4 style="color: #fbbf24; margin: 0 0 0.4rem 0;">C-Suite Executive Briefing</h4>
        <p style="font-size: 0.82rem; color: #94a3b8;">Board briefing, operational KPIs, and decision requests.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Generate Executive Briefing", type="primary", use_container_width=True):
        with st.spinner("Synthesizing C-Suite Executive Briefing..."):
            st.session_state.non_it_gen_doc = generate_business_doc("executive")
            st.session_state.non_it_gen_doc_type = "c_suite_executive_briefing"

with c2:
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 1.2rem;">
        <div style="font-size: 1.8rem; margin-bottom: 0.4rem;"></div>        <h4 style="color: #f87171; margin: 0 0 0.4rem 0;">Operational Risk Register</h4>
        <p style="font-size: 0.82rem; color: #94a3b8;">Operational risk matrix, financial impacts, and mitigations.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Generate Risk Register", use_container_width=True):
        with st.spinner("Building Operational Risk Matrix..."):
            st.session_state.non_it_gen_doc = generate_business_doc("risk")
            st.session_state.non_it_gen_doc_type = "operational_risk_matrix"

with c3:
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 1.2rem;">
        <div style="font-size: 1.8rem; margin-bottom: 0.4rem;"></div>        <h4 style="color: #38bdf8; margin: 0 0 0.4rem 0;">Quarterly Status Memo</h4>
        <p style="font-size: 0.82rem; color: #94a3b8;">Milestone tracking, financial utilization, and resource needs.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Generate Status Memo", use_container_width=True):
        with st.spinner("Drafting Quarterly Status Memo..."):
            st.session_state.non_it_gen_doc = generate_business_doc("memo")
            st.session_state.non_it_gen_doc_type = "quarterly_status_memo"

# ============================================================
# RENDERED DOCUMENT STUDIO & EXPORTER
# ============================================================

if "non_it_gen_doc" in st.session_state:
    doc_content = st.session_state.non_it_gen_doc
    doc_type_key = st.session_state.get("non_it_gen_doc_type", "business_document")
    
    st.divider()
    st.subheader("Rendered Document Studio")

    st.markdown(
        f"""
        <div class="glass-card" style="padding: 2rem; border-color: rgba(245, 158, 11, 0.35);">
        """,
        unsafe_allow_html=True
    )
    st.markdown(doc_content, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Export Bar
    st.divider()
    ex1, ex2 = st.columns(2)
    
    with ex1:
        st.download_button(
            label="Download Markdown Document (.md)",
            data=doc_content,
            file_name=f"{doc_type_key}.md",
            mime="text/markdown",
            use_container_width=True
        )
        
    with ex2:
        # Create standalone HTML report
        html_report = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{project.get('name', 'Business Project')} - Executive Briefing</title>
<style>
body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #0f172a; max-width: 900px; margin: 40px auto; padding: 20px; }}
h1, h2, h3 {{ color: #d97706; }}
table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
th, td {{ border: 1px solid #cbd5e1; padding: 10px 14px; text-align: left; }}
th {{ background-color: #fef3c7; }}
blockquote {{ background: #fffbeb; border-left: 4px solid #d97706; margin: 20px 0; padding: 12px 20px; }}
</style>
</head>
<body>
{doc_content}
</body>
</html>"""
        st.download_button(
            label="Download Standalone Executive Report (.html)",
            data=html_report,
            file_name=f"{doc_type_key}.html",
            mime="text/html",
            use_container_width=True
        )
