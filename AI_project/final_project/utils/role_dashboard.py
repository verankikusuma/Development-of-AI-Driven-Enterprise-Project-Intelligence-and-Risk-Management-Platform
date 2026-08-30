"""Role-specific dashboard panels. Does not change the XGBoost forecast itself."""

from __future__ import annotations

import streamlit as st

from utils.roles import get_role_config, normalize_job_role


FOCUS_COPY = {
    "backend": (
        "Backend / API focus",
        "Server-side, API, database, and integration risks from your authorized project view.",
    ),
    "frontend": (
        "Frontend / UI focus",
        "Interface, client integration, and frontend delivery risks.",
    ),
    "fullstack": (
        "Full-stack delivery focus",
        "Combined backend, frontend, and integration risk view.",
    ),
    "ml": (
        "ML / AI focus",
        "Model forecast outputs, data-quality signals, and AI-related risks. The XGBoost model is unchanged.",
    ),
    "data": (
        "Data engineering focus",
        "Dataset, pipeline, and data-quality information.",
    ),
    "ux": (
        "UI/UX focus",
        "Experience, interface, and related project documents.",
    ),
    "qa": (
        "QA / testing focus",
        "Quality risks, defects, and testing-related documents.",
    ),
    "devops": (
        "DevOps / infrastructure focus",
        "Deployment, CI/CD, and infrastructure risks.",
    ),
    "security": (
        "Cybersecurity focus",
        "Security, compliance, and vulnerability-related project information.",
    ),
    "database": (
        "Database administration focus",
        "Schema, data store, and backend data risks.",
    ),
    "pm": (
        "Project manager view",
        "Overall risk forecast, mitigation context, and project documents.",
    ),
    "lead": (
        "Team lead view",
        "Delivery health, risks, and team-relevant project information.",
    ),
    "ba": (
        "Business analyst view",
        "Requirements, scope, and process-related project information.",
    ),
    "management": (
        "Management view",
        "High-level project health, critical risks, and forecast summary.",
    ),
}


def render_role_panel(project: dict | None = None):
    role = normalize_job_role(st.session_state.get("job_role"))
    cfg = get_role_config(role)
    focus = cfg.get("dashboard_focus", "pm")
    title, blurb = FOCUS_COPY.get(focus, FOCUS_COPY["pm"])
    st.markdown(
        f"""
        <div class="glass-card" style="margin: 0.6rem 0 1rem 0; border-color: rgba(56,189,248,0.35);">
            <div style="color:#38bdf8;font-weight:800;font-size:0.95rem;text-transform:uppercase;letter-spacing:0.4px;">{title}</div>
            <div style="color:#cbd5e1;margin-top:0.35rem;">{blurb}</div>
            <div style="color:#94a3b8;margin-top:0.45rem;font-size:0.82rem;">Signed in as <strong style="color:#fff;">{st.session_state.get("username")}</strong> · Role stored on account: <strong style="color:#fff;">{role}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not project:
        return
    if cfg.get("can_see_ml_full") or focus in {"ml", "pm", "management", "lead"}:
        pred = st.session_state.get("prediction_detail") or {}
        if pred or project.get("risk_level"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("ML predicted class", project.get("risk_level") or pred.get("predicted_class", "—"))
            with c2:
                conf = pred.get("confidence") or project.get("confidence")
                st.metric("Forecast confidence", f"{conf:.0%}" if isinstance(conf, (int, float)) else "—")
            with c3:
                st.metric("Risk score", project.get("risk_score", "—"))
            probs = pred.get("probabilities") or project.get("probabilities")
            if isinstance(probs, dict):
                st.caption("Probability distribution (derived from the existing forecast score; model weights were not retrained).")
                st.json(probs)
            factors = pred.get("contributing_factors") or project.get("contributing_factors") or []
            if factors:
                st.caption("Contributing factors")
                st.dataframe(factors, use_container_width=True, hide_index=True)
    if focus == "management":
        level = str(project.get("risk_level", "")).lower()
        if level == "critical":
            st.error("Critical risk class from the XGBoost forecast. Review contributing factors before acting.")
        elif level == "high":
            st.warning("High risk class from the XGBoost forecast.")
    if focus == "qa":
        st.info("QA view highlights defects and testing language from documents you are authorized to see.")
    if focus == "devops":
        st.info("DevOps view emphasizes deployment, infrastructure, and CI/CD language from authorized documents.")
