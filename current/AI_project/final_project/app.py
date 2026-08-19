import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Development of AI-Driven Enterprise Project Intelligence and Risk Management Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "user_type" not in st.session_state:
    st.session_state.user_type = ""

if "documents" not in st.session_state:
    st.session_state.documents = {}

if "selected_project_id" not in st.session_state:
    st.session_state.selected_project_id = None

if "selected_project" not in st.session_state:
    st.session_state.selected_project = None

if "project_analyzed" not in st.session_state:
    st.session_state.project_analyzed = False

if "prediction" not in st.session_state:
    st.session_state.prediction = None

if "it_project_uploaded" not in st.session_state:
    st.session_state.it_project_uploaded = False

if "non_it_project_uploaded" not in st.session_state:
    st.session_state.non_it_project_uploaded = False

if "api_base" not in st.session_state:
    st.session_state.api_base = "http://127.0.0.1:8000"


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>
    /* Global App Header */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {
        background: #090d16 !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.05) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(99, 102, 241, 0.05) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(15, 23, 42, 0.8) 0px, transparent 50%) !important;
        background-attachment: fixed !important;
        color: #f8fafc !important;
    }
    
    /* Default spacing */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.logged_in:

    # --------------------------------------------------------
    # HIDE SIDEBAR ON LOGIN PAGE
    # --------------------------------------------------------

    st.markdown(
        """
        <style>
        /* Hide sidebar completely on login page */
        section[data-testid="stSidebar"], [data-testid="stSidebarNav"] {
            display: none !important;
        }

        /* Prevent all vertical scrollbars on login screen */
        html, body, [data-testid="stAppViewContainer"], .main {
            overflow: hidden !important;
        }

        /* Center container with comfortable spacing */
        .block-container {
            padding-top: 2.2rem !important;
            padding-bottom: 1rem !important;
            max-width: 820px !important;
        }
        
        /* Hide standard streamlit UI elements for a cleaner look */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # LOGIN FORM & ENTERPRISE LANDING UI
    # --------------------------------------------------------

    col1, col2, col3 = st.columns([0.4, 5.2, 0.4])
    
    with col2:
        st.markdown(
            """
            <div style="margin-bottom: 1.8rem; text-align: center;">
                <div style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.4rem 1.2rem; background: linear-gradient(135deg, rgba(0, 242, 254, 0.12) 0%, rgba(112, 0, 255, 0.12) 100%); border: 1px solid rgba(0, 242, 254, 0.4); border-radius: 999px; color: #00f2fe; font-weight: 800; font-size: 0.8rem; letter-spacing: 0.5px; margin-bottom: 1rem;">
                    <span></span>ENTERPRISE RISK ANALYTICS PLATFORM
                </div>
                <h1 style="color: #ffffff; font-size: 2.1rem; line-height: 1.3; font-weight: 800; letter-spacing: -0.5px; font-family: 'Outfit', sans-serif; margin-top: 0;">
                    Development of AI-Driven Enterprise Project Intelligence and Risk Management Platform
                </h1>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.container():
            st.markdown(
                """
                <div class="glass-card" style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.85) 100%); border: 1px solid rgba(0, 242, 254, 0.35); border-radius: 18px; padding: 1.8rem 2.2rem; box-shadow: 0 18px 45px rgba(0, 0, 0, 0.55), 0 0 25px rgba(0, 242, 254, 0.12);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.3rem;">
                        <h3 style="color: #ffffff; margin: 0; font-weight: 800; font-size: 1.25rem;">Sign In / Access Control</h3>
                        <span style="background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); font-size: 0.75rem; font-weight: 700; padding: 0.22rem 0.65rem; border-radius: 999px;">Secure Session</span>                    </div>
                """,
                unsafe_allow_html=True
            )
            
            username = st.text_input("Username / Enterprise Email", placeholder="name@company.com")
            password = st.text_input("Security Access Token / Password", type="password", placeholder="••••••••")
            
            st.write("")
            
            # Buttons side by side
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                login_clicked = st.button("Authenticate Login", type="primary", use_container_width=True)
            with btn_col2:
                signup_clicked = st.button("Create Account", use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)


    # ========================================================
    # LOGIN / SIGNUP VALIDATION
    # ========================================================

    import json
    import os

    USER_FILE = "users.json"

    def load_users():
        if not os.path.exists(USER_FILE):
            default_users = {
                "it_user": {"password": "it123", "role": "IT"}, 
                "nonit_user": {"password": "nonit123", "role": "Non-IT"}
            }
            with open(USER_FILE, "w") as f:
                json.dump(default_users, f, indent=4)
            return default_users
        with open(USER_FILE, "r") as f:
            return json.load(f)

    def save_users(users):
        with open(USER_FILE, "w") as f:
            json.dump(users, f, indent=4)

    if signup_clicked:
        username = username.strip()
        if not username or not password:
            st.error("Please enter a username and password.")
        else:
            users = load_users()
            if username in users:
                st.error("Username already exists. Please log in.")
            else:
                users[username] = {"password": password, "role": "IT"}
                save_users(users)
                st.success("Account created successfully! You can now log in.")

    if login_clicked:
        username = username.strip()
        users = load_users()
        
        if username in users and users[username]["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            
            # Every user chooses the appropriate workspace after sign-in.
            st.session_state.user_type = ""

            # Reset project data
            st.session_state.documents = {}
            st.session_state.selected_project_id = None
            st.session_state.selected_project = None
            st.session_state.project_analyzed = False
            st.session_state.prediction = None
            st.session_state.it_project_uploaded = False
            st.session_state.non_it_project_uploaded = False

            st.rerun()
        else:
            st.error("Invalid username, password, or role.")


    # --------------------------------------------------------
    # STOP LOGIN PAGE
    # --------------------------------------------------------

    st.stop()


# ============================================================
# USER IS LOGGED IN
# ============================================================

if not st.session_state.user_type:
    st.markdown("""
        <style>
        section[data-testid="stSidebar"], [data-testid="stSidebarNav"] { display: none !important; }
        .block-container { max-width: 1000px; padding-top: 3rem; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2.5rem;">
        <h1 style="color: #ffffff; font-size: 2.2rem; font-weight: 800; margin-bottom: 0.6rem;">Select Project Workspace</h1>
        <p style="color: #cbd5e1; font-size: 1.05rem;">Choose the domain engine tailored to your project architecture, risk drivers, and terminology.</p>
    </div>
    """, unsafe_allow_html=True)
    
    it_col, business_col = st.columns(2)
    with it_col:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(14, 165, 233, 0.15) 0%, rgba(15, 23, 42, 0.8) 100%); border: 1px solid rgba(56, 189, 248, 0.35); border-radius: 18px; padding: 1.5rem; min-height: 295px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 10px 25px rgba(0,0,0,0.4); margin-bottom: 1rem;">
            <div>
                <div style="font-size: 2rem; margin-bottom: 0.5rem;"></div>                <h2 style="color: #38bdf8; font-size: 1.3rem; font-weight: 800; margin-top: 0; margin-bottom: 0.4rem;">IT & Technical Engineering</h2>
                <p style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.45; min-height: 68px; margin-bottom: 0.8rem;">
                    XGBoost & CatBoost ML models trained on software delivery, cloud migrations, DevOps pipelines, tech stack complexity, and IT vendor dependencies.
                </p>
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 0.35rem; min-height: 55px; align-content: flex-start; box-sizing: border-box;">
                <span style="background: rgba(56, 189, 248, 0.2); color: #7dd3fc; border: 1px solid rgba(56, 189, 248, 0.3); font-size: 0.74rem; padding: 0.2rem 0.45rem; border-radius: 6px;">Software Engineering</span>
                <span style="background: rgba(56, 189, 248, 0.2); color: #7dd3fc; border: 1px solid rgba(56, 189, 248, 0.3); font-size: 0.74rem; padding: 0.2rem 0.45rem; border-radius: 6px;">Cloud & Infrastructure</span>
                <span style="background: rgba(56, 189, 248, 0.2); color: #7dd3fc; border: 1px solid rgba(56, 189, 248, 0.3); font-size: 0.74rem; padding: 0.2rem 0.45rem; border-radius: 6px;">Cybersecurity</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter IT Workspace", type="primary", use_container_width=True):
            st.session_state.user_type = "IT"
            st.rerun()
        
    with business_col:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(15, 23, 42, 0.8) 100%); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 18px; padding: 1.5rem; min-height: 295px; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 10px 25px rgba(0,0,0,0.4); margin-bottom: 1rem;">
            <div>
                <div style="font-size: 2rem; margin-bottom: 0.5rem;"></div>                <h2 style="color: #fbbf24; font-size: 1.3rem; font-weight: 800; margin-top: 0; margin-bottom: 0.4rem;">Non-IT & Business Operations</h2>
                <p style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.45; min-height: 68px; margin-bottom: 0.8rem;">
                    Random Forest & Gradient Boosting models tuned for operational risk, business transformation, construction, supply chain, and financial rollout.
                </p>
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 0.35rem; min-height: 55px; align-content: flex-start; box-sizing: border-box;">
                <span style="background: rgba(245, 158, 11, 0.2); color: #fde68a; border: 1px solid rgba(245, 158, 11, 0.3); font-size: 0.74rem; padding: 0.2rem 0.45rem; border-radius: 6px;">Business Operations</span>
                <span style="background: rgba(245, 158, 11, 0.2); color: #fde68a; border: 1px solid rgba(245, 158, 11, 0.3); font-size: 0.74rem; padding: 0.2rem 0.45rem; border-radius: 6px;">Supply Chain & Logistics</span>
                <span style="background: rgba(245, 158, 11, 0.2); color: #fde68a; border: 1px solid rgba(245, 158, 11, 0.3); font-size: 0.74rem; padding: 0.2rem 0.45rem; border-radius: 6px;">Strategic Finance</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Enter Non-IT Workspace", use_container_width=True):
            st.session_state.user_type = "NON_IT"
            st.rerun()
        
    st.stop()

from utils.api_client import backend_health

is_healthy = backend_health(st.session_state.get("api_base", "http://127.0.0.1:8000"))
status_text = "Backend API Connected" if is_healthy else "Embedded ML Engine Active"
status_color = "#34d399" if is_healthy else "#fbbf24"

active_proj = st.session_state.get("selected_project")
active_proj_name = active_proj.get("name", "No Project Selected") if active_proj else "No Active Project"

is_it = st.session_state.get("user_type") == "IT"
role_tag = "IT Technical Engineering Workspace" if is_it else "Non-IT Business & Operations Workspace"
role_badge_style = "background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.35);" if is_it else "background: rgba(245, 158, 11, 0.15); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.35);"

st.markdown(
    f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                padding: 0.85rem 1.5rem; border-radius: 16px; margin-bottom: 1.4rem;
                border: 1px solid rgba(255,255,255,0.12); box-shadow: 0 6px 20px rgba(0,0,0,0.3);
                display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.6rem;">
        <div style="display: flex; align-items: center; gap: 0.9rem;">
            <span style="color: #ffffff; font-weight: 800; font-size: 1.15rem; letter-spacing: -0.3px;">AI Project Intelligence</span>
            <span style="{role_badge_style} font-size: 0.78rem; font-weight: 700; padding: 0.25rem 0.7rem; border-radius: 999px; text-transform: uppercase;">{role_tag}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 1.4rem; font-size: 0.88rem;">
            <span style="color: #cbd5e1; font-weight: 600;">Active: <strong style="color: #ffffff;">{active_proj_name}</strong></span>            <span style="display: flex; align-items: center; gap: 0.45rem; color: {status_color}; font-weight: 600;">
                <span style="width: 8px; height: 8px; background-color: {status_color}; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px {status_color};"></span>
                {status_text}
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR USER INFORMATION
# ============================================================

with st.sidebar:

    st.markdown(
        "## AI Enterprise Project Intelligence"
    )

    st.divider()


    st.write(
        f"User: {st.session_state.username}"
    )


    if st.session_state.get("is_batch", False) and "batch_projects" in st.session_state:
        st.divider()
        st.markdown("**Batch Project Selection**")
        
        batch_projects = st.session_state.batch_projects
        project_names = [p.get("name", f"Project {p['id']}") for p in batch_projects]
        
        selected_proj = st.session_state.get("selected_project")
        current_name = selected_proj.get("name") if selected_proj else None
        try:
            default_index = project_names.index(current_name) if current_name in project_names else 0
        except ValueError:
            default_index = 0
            
        selected_name = st.selectbox(
            "Active Project",
            options=project_names,
            index=default_index,
            help="Select a project from your batch upload to analyze across all pages."
        )
        
        if selected_name != current_name:
            for p in batch_projects:
                if p.get("name", f"Project {p['id']}") == selected_name:
                    st.session_state.selected_project = p
                    st.session_state.selected_project_id = p["id"]
                    st.rerun()

    st.divider()


    # --------------------------------------------------------
    # LOGOUT
    # --------------------------------------------------------

    if st.button(
        "Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False

        st.session_state.username = ""

        st.session_state.user_type = ""

        st.session_state.documents = {}

        st.session_state.selected_project_id = None

        st.session_state.selected_project = None

        st.session_state.project_analyzed = False

        st.session_state.prediction = None

        st.session_state.it_project_uploaded = False

        st.session_state.non_it_project_uploaded = False

        st.rerun()


# ============================================================
# IT USER NAVIGATION
# ============================================================

if st.session_state.user_type == "IT":

    it_pages = [

        # FIRST PAGE AFTER IT LOGIN
        st.Page(
            "pages/2_Document_Upload.py",
            title="Document Upload"
        ),

        st.Page(
            "pages/1_Dashboard.py",
            title="Project Dashboard"
        ),

        st.Page(
            "pages/3_Project_Analysis.py",
            title="Project Analysis"
        ),

        st.Page(
            "pages/4_Risk_Intelligence.py",
            title="Risk Intelligence"
        ),

        st.Page(
            "pages/5_Schedule_Intelligence.py",
            title="Schedule Intelligence"
        ),

        st.Page(
            "pages/6_Dependencies.py",
            title="Dependencies"
        ),

        st.Page(
            "pages/7_What_If_Simulation.py",
            title="What-If Simulation"
        ),

        st.Page(
            "pages/9_Documentation.py",
            title="Documentation"
        ),

        st.Page(
            "pages/10_AI_Assistant.py",
            title="RAGBot"
        )
    ]


    # --------------------------------------------------------
    # IT NAVIGATION
    # --------------------------------------------------------

    navigation = st.navigation(
        it_pages,
        position="sidebar"
    )

    navigation.run()


# ============================================================
# NON-IT USER NAVIGATION
# ============================================================

elif st.session_state.user_type == "NON_IT":

    non_it_pages = [

        # FIRST PAGE AFTER NON-IT LOGIN
        st.Page(
            "pages/12_Non_IT_Document_Upload.py",
            title="Document Upload"
        ),

        st.Page(
            "pages/11_Non_IT_Dashboard.py",
            title="Project Dashboard"
        ),

        st.Page(
            "pages/13_Non_IT_Project_Analysis.py",
            title="Project Analysis"
        ),

        st.Page(
            "pages/14_Non_IT_Risk_Intelligence.py",
            title="Risk Intelligence"
        ),

        st.Page(
            "pages/15_Non_IT_Schedule_Intelligence.py",
            title="Schedule Intelligence"
        ),

        st.Page(
            "pages/16_Non_IT_Dependencies.py",
            title="Dependencies"
        ),

        st.Page(
            "pages/17_Non_IT_What_If_Simulation.py",
            title="What-If Simulation"
        ),

        st.Page(
            "pages/19_Non_IT_Documentation.py",
            title="Documentation"
        ),

        st.Page(
            "pages/20_Non_IT_AI_Assistant.py",
            title="RAGBot"
        )
    ]


    # --------------------------------------------------------
    # NON-IT NAVIGATION
    # --------------------------------------------------------

    navigation = st.navigation(
        non_it_pages,
        position="sidebar"
    )

    navigation.run()
