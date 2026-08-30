import streamlit as st
import os
from dotenv import load_dotenv
from google import genai
from utils.ui import inject_css, page_header, risk_badge
from utils.local_ai import generate_local_document
from utils.api_client import backend_health, api_generate_document

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ============================================================
# PAGE SETUP
# ============================================================

inject_css()

page_header(
    "IT Executive Document Studio",
    "Dynamically generate C-level Executive Summaries, Agile Backlogs with Gherkin Acceptance Criteria, and Enterprise Risk Registers via API."
)

project = st.session_state.get("selected_project")
if not project:
    st.warning("No active IT project found. Please upload an IT project document first.")
    st.page_link("pages/2_Document_Upload.py", label="Go to Document Upload")
    st.stop()

documents = st.session_state.get("documents", {})
doc_texts = "\n\n".join(documents.values())
api_base = st.session_state.get("api_base", "http://127.0.0.1:8000")

# ============================================================
# LLM & API DOCUMENTATION ENGINE
# ============================================================

def generate_docs(doc_type):
    # 1. Try FastAPI Backend API Endpoint
    try:
        if backend_health(api_base):
            api_doc = api_generate_document(project, doc_type, audience="IT Delivery Leadership", base_url=api_base)
            if api_doc and len(api_doc) > 50:
                return api_doc
    except Exception:
        pass

    # 2. Try Gemini Cloud AI
    if os.environ.get("USE_CLOUD_AI", "false").lower() == "true" and GEMINI_API_KEY:
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            if doc_type == "user_stories":
                prompt = f"Generate 5-8 Agile User Stories with Gherkin Acceptance Criteria and Sprint DoD for: {doc_texts[:15000]}"
            elif doc_type == "risk_register":
                prompt = f"Generate an Enterprise Risk Register Table with Severity badges and Mitigations for: {doc_texts[:15000]}"
            else:
                prompt = f"Write a 1-page C-level Executive Summary Briefing for: {doc_texts[:15000]}"
            
            response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
            return response.text
        except Exception:
            pass

    # 3. Local Document Engine Fallback
    return generate_local_document(project, doc_type, "IT Delivery Leadership")

# ============================================================
# DOCUMENT STUDIO CONTROLS
# ============================================================

st.subheader("AI Document Generator Studio")
st.write("Select a document template below to generate formatted, executive-ready documentation grounded in your project data.")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 1.2rem;">
        <div style="font-size: 1.8rem; margin-bottom: 0.4rem;"></div>        <h4 style="color: #38bdf8; margin: 0 0 0.4rem 0;">Agile User Stories</h4>
        <p style="font-size: 0.82rem; color: #94a3b8;">Gherkin acceptance criteria, story points, and DoD checklists.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Generate Backlog Suite", type="primary", use_container_width=True):
        with st.spinner("Drafting Agile User Stories & Backlog via API..."):
            st.session_state.generated_doc = generate_docs("user_stories")
            st.session_state.generated_doc_type = "agile_user_stories"

with col2:
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 1.2rem;">
        <div style="font-size: 1.8rem; margin-bottom: 0.4rem;"></div>        <h4 style="color: #fbbf24; margin: 0 0 0.4rem 0;">Enterprise Risk Register</h4>
        <p style="font-size: 0.82rem; color: #94a3b8;">Risk matrix, impact ratings, mitigation owners, and SLAs.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Generate Risk Register", use_container_width=True):
        with st.spinner("Building Enterprise Risk Register via API..."):
            st.session_state.generated_doc = generate_docs("risk_register")
            st.session_state.generated_doc_type = "enterprise_risk_register"

with col3:
    st.markdown("""
    <div class="glass-card" style="text-align: center; padding: 1.2rem;">
        <div style="font-size: 1.8rem; margin-bottom: 0.4rem;"></div>        <h4 style="color: #34d399; margin: 0 0 0.4rem 0;">C-Level Executive Briefing</h4>
        <p style="font-size: 0.82rem; color: #94a3b8;">Board-ready 1-page summary, KPI targets, and decisions.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Generate Executive Briefing", use_container_width=True):
        with st.spinner("Synthesizing Executive Summary Briefing via API..."):
            st.session_state.generated_doc = generate_docs("executive_summary")
            st.session_state.generated_doc_type = "executive_briefing"

# ============================================================
# RENDERED DOCUMENT STUDIO & EXPORTER
# ============================================================

if "generated_doc" in st.session_state:
    doc_content = st.session_state.generated_doc
    doc_type_key = st.session_state.get("generated_doc_type", "project_document")
    
    st.divider()
    st.subheader("Rendered Document Studio")

    st.markdown(
        f"""
        <div class="glass-card" style="padding: 2rem; border-color: rgba(56, 189, 248, 0.35);">
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
        html_report = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{project.get('name', 'IT Project')} - Executive Report</title>
<style>
body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #0f172a; max-width: 900px; margin: 40px auto; padding: 20px; }}
h1, h2, h3 {{ color: #0284c7; }}
table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
th, td {{ border: 1px solid #cbd5e1; padding: 10px 14px; text-align: left; }}
th {{ background-color: #f1f5f9; }}
blockquote {{ background: #e0f2fe; border-left: 4px solid #0284c7; margin: 20px 0; padding: 12px 20px; }}
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
