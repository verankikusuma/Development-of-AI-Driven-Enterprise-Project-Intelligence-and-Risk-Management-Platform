import streamlit as st
import pandas as pd
from utils.ui import inject_css, page_header
from utils.predictor import predict_non_it_risk, predict_it_risk
from utils.llm_parser import parse_document_with_gemini, parse_batch_with_gemini
from rag_chatbot.session_store import clear_index
from utils.ui import render_model_quality, render_risk_management_processes

inject_css()

page_header(
    "Non-IT Document & Data Upload",
    "Upload business proposals, project charters, budgets, or milestone CSVs. The system extracts business metrics and calculates operational risk."
)

if "documents" not in st.session_state:
    st.session_state.documents = {}
if "selected_project_id" not in st.session_state:
    st.session_state.selected_project_id = None
if "selected_project" not in st.session_state:
    st.session_state.selected_project = None

def extract_text(file):
    filename = file.name.lower()
    if filename.endswith(".txt") or filename.endswith(".csv"):
        try:
            return file.getvalue().decode("utf-8", errors="ignore")
        except: return ""
    if filename.endswith(".docx"):
        try:
            import docx2txt
            return docx2txt.process(file)
        except Exception as e:
            st.error(f"Error reading DOCX: {e}")
            return ""
    if filename.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(file)
            return "\n".join([p.extract_text() or "" for p in reader.pages])
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            return ""

def save_non_it_prediction(insights_dict, prediction):
    project_id = 3000 + len(st.session_state.documents)
    features = insights_dict.get("features", {})
    
    project_data = {
        "id": project_id,
        "project_id": str(project_id),
        "name": insights_dict.get("project_name", "Business Operation Project"),
        "status": "IN_PROGRESS",
        "budget": features.get("budget_usd", 0),
        "deadline": "TBD",
        "progress": 0,
        "health_score": max(0, 100 - prediction["risk_score"]),
        "risk_level": prediction["risk_level"],
        "risk_score": prediction["risk_score"],
        "features": features,
        "project_scope": insights_dict.get("project_scope", ""),
        "deliverables": insights_dict.get("deliverables", []),
        "action_items": insights_dict.get("action_items", []),
        "milestones": insights_dict.get("milestones", []),
        "dependencies": insights_dict.get("dependencies", []),
        "missing_info": insights_dict.get("missing_info", []),
        "potential_risks": insights_dict.get("potential_risks", []),
    }
    
    st.session_state.selected_project_id = project_id
    st.session_state.selected_project = project_data
    st.session_state.project_analyzed = True
    st.session_state.non_it_project_uploaded = True
    st.session_state.prediction = prediction["risk_level"]

st.write("### Autonomous Document Processing")
st.write("Upload a PDF, DOCX, CSV, or TXT file. The first-pass analysis runs locally for a dependable response.")
render_risk_management_processes()

uploaded_file = st.file_uploader(
    "Choose business project file",
    type=["pdf", "docx", "txt", "csv"],
    help="Supported formats: PDF, DOCX, TXT, CSV"
)

if uploaded_file is not None:
    if st.button("Process & Analyze Document", type="primary", use_container_width=True):
        st.success(f"Uploaded: {uploaded_file.name}")
        st.divider()

        is_csv = uploaded_file.name.lower().endswith(".csv")

        with st.spinner("Extracting insights with AI..."):
            extracted_text = extract_text(uploaded_file)
            if not extracted_text.strip():
                st.error("No readable text was found. Upload a text-based PDF, DOCX, CSV, or TXT file.")
                st.stop()
            st.session_state.documents[uploaded_file.name] = extracted_text

            try:
                if is_csv:
                    insights_dict = parse_batch_with_gemini(extracted_text, "Non-IT")
                else:
                    insights_dict = parse_document_with_gemini(extracted_text, "Non-IT")
            except Exception as e:
                st.error(f"Document analysis failed: {e}")
                st.stop()

        with st.spinner("Evaluating Non-IT Risk Models..."):
            if is_csv:
                batch_projects = []
                for i, proj in enumerate(insights_dict.get("projects", [])):
                    feats = proj.get("features", {})
                    pred = predict_non_it_risk(feats)
                    
                    project_id = 4000 + i
                    project_data = {
                        "id": project_id,
                        "project_id": str(project_id),
                        "name": proj.get("project_name", f"Business Project {i+1}"),
                        "status": "IN_PROGRESS",
                        "budget": feats.get("budget_usd", 0),
                        "deadline": "TBD",
                        "progress": 0,
                        "health_score": max(0, 100 - pred["risk_score"]),
                        "risk_level": pred["risk_level"],
                        "risk_score": pred["risk_score"],
                        "features": feats,
                        "project_scope": proj.get("project_scope", ""),
                        "deliverables": proj.get("deliverables", []),
                        "action_items": proj.get("action_items", []),
                        "milestones": proj.get("milestones", []),
                        "dependencies": proj.get("dependencies", []),
                        "missing_info": proj.get("missing_info", []),
                        "potential_risks": proj.get("potential_risks", []),
                    }
                    batch_projects.append(project_data)

                st.session_state.batch_projects = batch_projects
                if batch_projects:
                    st.session_state.selected_project = batch_projects[0]
                    st.session_state.selected_project_id = batch_projects[0]["id"]
                st.session_state.is_batch = True
                st.session_state.project_analyzed = True
            else:
                feats = insights_dict.get("features", {})
                pred = predict_non_it_risk(feats)
                save_non_it_prediction(insights_dict, pred)
                st.session_state.is_batch = False

        clear_index()
        st.session_state["rag_ready"] = False
        st.session_state["rag_chunk_count"] = 0

        st.success("Project document analyzed successfully! Navigate to Dashboard to view results.")

if st.session_state.get("project_analyzed", False):
    project = st.session_state.get("selected_project", {})
    st.divider()
    st.subheader("Project Analysis Snapshot")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Project Name", project.get("name"))
    with c2: st.metric("Health Index", f"{project.get('health_score', 0):.0f}%")
    with c3: st.metric("Risk Score", f"{project.get('risk_score', 0):.0f}/100")
    with c4: st.metric("Risk Level", project.get("risk_level"))
    
    st.markdown(f"""
    <div class="glass-card" style="margin-top: 1rem; margin-bottom: 1.5rem; border-color: rgba(245, 158, 11, 0.35);">
        <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.6rem;">
            <span style="font-size: 1.3rem;"></span>            <span style="color: #fbbf24; font-weight: 800; font-size: 1.05rem; text-transform: uppercase; letter-spacing: 0.5px;">Executive Business Document Scope & Highlights</span>
        </div>
        <p style="color: #e2e8f0; font-size: 0.96rem; line-height: 1.6; margin: 0;">{project.get('project_scope', 'Extracted scope details from uploaded project documentation.')}</p>
    </div>
    """, unsafe_allow_html=True)

    details_col, risk_col = st.columns(2)
    with details_col:
        with st.expander("Strategic Deliverables & Milestone Telemetry", expanded=True):
            st.markdown("<h4 style='color: #ffffff; font-size: 0.95rem; margin-bottom: 0.6rem;'>Key Business Workstreams</h4>", unsafe_allow_html=True)
            for item in project.get("deliverables", [])[:6]:
                st.markdown(f"<div style='color: #cbd5e1; font-size: 0.88rem; margin-bottom: 0.35rem;'><strong>{item}</strong></div>", unsafe_allow_html=True)
            
            st.divider()
            st.markdown("<h4 style='color: #ffffff; font-size: 0.95rem; margin-bottom: 0.6rem;'>Milestone Completion Telemetry</h4>", unsafe_allow_html=True)
            for milestone in project.get("milestones", [])[:4]:
                name = milestone.get('name', 'Unnamed Phase')
                pct = int(milestone.get('progress_pct', 0))
                st.caption(f"{name} — **{pct}% Complete**")
                st.progress(pct)

    with risk_col:
        with st.expander("Predictive Risk Telemetry & Evidence", expanded=True):
            features = project.get("features", {})
            evidence = {
                "Capital Budget Baseline": f"${features.get('budget_usd', 0):,.0f}",
                "Schedule Variance Exposure": f"{features.get('schedule_overrun_pct', 0):.1f}%",
                "Resource Availability Index": f"{features.get('resource_availability_pct', 0):.0f}%",
                "Technical Complexity Rating": f"{features.get('tech_complexity_score', 0):.0f}/100",
                "External Dependency Index": f"{features.get('external_dependency_score', 0):.0f}/100",
            }
            st.dataframe(pd.DataFrame(evidence.items(), columns=["Telemetry Signal", "Extracted Value"]), hide_index=True, use_container_width=True)
            st.markdown("<h4 style='color: #ffffff; font-size: 1.05rem; margin-top: 1rem; margin-bottom: 0.6rem; font-weight: 800;'>Key Risk Triggers</h4>", unsafe_allow_html=True)
            for risk in project.get("potential_risks", [])[:5]:
                r_clean = str(risk).strip(" -•\t")
                if r_clean:
                    r_cap = r_clean[0].upper() + r_clean[1:]
                    st.markdown(f"<div style='color: #f8fafc; font-size: 0.98rem; font-weight: 500; margin-bottom: 0.45rem; line-height: 1.5;'>{r_cap}</div>", unsafe_allow_html=True)
                
    render_model_quality("Non-IT")
