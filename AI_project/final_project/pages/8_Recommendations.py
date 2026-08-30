import streamlit as st

from utils.ui import inject_css, page_header


inject_css()

page_header(
    "AI Recommendations",
    "Recommended actions based on project status and risks."
)


project_id = st.session_state.get(
    "selected_project_id"
)

if project_id is None:

    st.warning(
        "Please upload an IT project first."
    )

    st.page_link(
        "pages/2_Document_Upload.py",
        label=" Upload Project"
    )

    st.stop()


# ============================================================
# RECOMMENDATIONS
# ============================================================

recommendations = [

    (
        " High Priority",
        "Review schedule milestones and identify potential delays."
    ),

    (
        " Medium Priority",
        "Monitor budget consumption regularly."
    ),

    (
        " Medium Priority",
        "Track technical dependencies between development tasks."
    ),

    (
        " Low Priority",
        "Update project documentation continuously."
    )
]


st.subheader(
    " Recommended Actions"
)


for priority, recommendation in recommendations:

    with st.container():

        st.markdown(
            f"### {priority}"
        )

        st.write(
            recommendation
        )

        st.divider()


# ============================================================
# ACTION PLAN
# ============================================================

st.subheader(
    " Action Plan"
)

st.checkbox(
    "Review high-priority risks"
)

st.checkbox(
    "Check upcoming deadlines"
)

st.checkbox(
    "Review task dependencies"
)

st.checkbox(
    "Update project documentation"
)