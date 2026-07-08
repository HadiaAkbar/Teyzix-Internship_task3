import streamlit as st
import requests

API_URL = st.secrets.get("API_URL", "http://localhost:8000") if hasattr(st, "secrets") else "http://localhost:8000"
try:
    API_URL = st.secrets["API_URL"]
except Exception:
    API_URL = "http://localhost:8000"

st.set_page_config(page_title="Contract Risk Analyzer", layout="wide", initial_sidebar_state="collapsed")

if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.user = None


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


LOGIN_CSS = """
<style>
    * {box-sizing: border-box;}
    html, body {margin: 0; padding: 0;}
    
    #MainMenu, header, footer {visibility: hidden;}
    .block-container {padding: 0 !important; max-width: 100% !important;}
    .stApp {background: #061109; margin: 0; padding: 0;}

    /* Main horizontal container */
    [data-testid="stHorizontalBlock"] {
        gap: 0 !important;
        align-items: stretch !important;
        height: 100vh;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        min-height: 100vh;
        display: flex !important;
        flex-direction: column;
        justify-content: center;
    }

    /* Left panel (form) */
    div[data-testid="column"]:has(> div .login-marker) {
        background: #071309;
        padding: 2rem 2rem !important;
        border-right: 1px solid rgba(52, 211, 153, 0.08);
        flex: 0 0 45% !important;
        max-width: 45% !important;
        overflow-y: auto;
    }
    
    div[data-testid="column"]:has(> div .login-marker) [data-testid="stVerticalBlock"] {
        max-width: 100%;
        width: 100%;
    }

    /* Right panel (hero) */
    div[data-testid="column"]:has(> div .hero-marker) {
        background:
            radial-gradient(circle at 78% 15%, rgba(52,211,153,0.28) 0%, rgba(52,211,153,0.0) 42%),
            radial-gradient(circle at 60% 55%, rgba(34,197,94,0.20) 0%, rgba(34,197,94,0.0) 45%),
            radial-gradient(circle at 18% 78%, rgba(16,120,80,0.35) 0%, rgba(16,120,80,0.0) 30%),
            linear-gradient(160deg, #04140b 0%, #0a2416 55%, #0f2f1c 100%);
        padding: 2rem 3rem !important;
        display: flex !important;
        flex-direction: column;
        justify-content: center;
        position: relative;
        overflow: hidden;
        flex: 1 1 55% !important;
    }
    
    div[data-testid="column"]:has(> div .hero-marker) [data-testid="stVerticalBlock"] {
        justify-content: center;
        width: 100%;
    }

    /* Logo row */
    .logo-row {
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin-bottom: 2rem;
        flex-wrap: nowrap;
    }
    
    .logo-row .flag {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 40px;
        height: 40px;
        border-radius: 8px;
        background: rgba(52, 211, 153, 0.12);
        flex-shrink: 0;
    }
    
    .logo-row .brand {
        color: #f5f7f6;
        font-size: 1.3rem;
        font-weight: 700;
        white-space: nowrap;
    }

    .section-label {
        color: #6ee7b7;
        letter-spacing: 2px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-transform: uppercase;
    }

    .ai-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(52, 211, 153, 0.10);
        border: 1px solid rgba(52, 211, 153, 0.35);
        color: #4ade80;
        font-weight: 700;
        font-size: 0.8rem;
        padding: 0.4rem 0.9rem;
        border-radius: 999px;
        margin-bottom: 1.5rem;
        letter-spacing: 1px;
        width: fit-content;
    }
    
    .ai-badge .dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #4ade80;
        flex-shrink: 0;
    }

    .hero-title {
        color: #f5f7f6;
        font-size: clamp(1.5rem, 4vw, 2.8rem);
        font-weight: 800;
        line-height: 1.2;
        margin-bottom: 1.2rem;
        max-width: 100%;
        word-wrap: break-word;
    }
    
    .hero-title .accent {
        color: #4ade80;
    }

    .hero-sub {
        color: #b9c4bd;
        font-size: clamp(0.95rem, 2vw, 1.1rem);
        line-height: 1.6;
        max-width: 100%;
        margin-bottom: 2rem;
    }

    .waves {
        margin-top: 1.5rem;
        opacity: 0.5;
        max-width: 100%;
        height: auto;
    }

    /* Tabs - Responsive */
    .stTabs {
        margin-bottom: 1rem;
        width: 100%;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background: #0d1a13 !important;
        border-radius: 10px;
        padding: 5px;
        gap: 8px !important;
        width: 100% !important;
        display: flex !important;
        border-bottom: none !important;
        flex-wrap: wrap !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px !important;
        color: #9ca3af;
        font-weight: 600;
        padding: 12px 16px !important;
        flex: 1 1 0 !important;
        justify-content: center;
        display: flex !important;
        align-items: center;
        margin: 0 !important;
        min-height: 44px;
        font-size: 1rem;
        white-space: nowrap;
        border: 1px solid transparent !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: #34d399 !important;
        color: #04140b !important;
    }
    
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }
    
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }
    
    .stTabs [data-testid="stMarkdownContainer"] p {
        font-weight: inherit;
        margin: 0;
    }

    /* Input fields - Responsive */
    .stTextInput {
        width: 100%;
        margin-bottom: 1rem;
    }
    
    .stTextInput > label {
        color: #d1d5db !important;
        font-weight: 600;
        font-size: 0.9rem;
        display: block;
        margin-bottom: 0.5rem;
    }
    
    .stTextInput input {
        background: #0d1a13 !important;
        color: #f5f7f6 !important;
        border: 1px solid rgba(52, 211, 153, 0.15) !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        width: 100% !important;
        font-size: 1rem;
        min-height: 44px;
        box-sizing: border-box;
    }
    
    .stTextInput input:focus {
        border: 1px solid #34d399 !important;
        box-shadow: none !important;
    }
    
    .stTextInput input::placeholder {
        color: #5b6660;
    }

    /* Buttons - Responsive */
    div[data-testid="stButton"] {
        width: 100%;
        margin-bottom: 0.75rem;
    }
    
    .stButton button {
        background: #34d399;
        color: #04140b;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        padding: 1rem !important;
        width: 100% !important;
        min-height: 48px;
        transition: background 0.15s ease;
        font-size: 1.1rem;
        cursor: pointer;
        box-sizing: border-box;
        display: block !important;
    }
    
    .stButton button:hover {
        background: #22c55e;
        color: #04140b;
    }
    
    .stButton button p {
        color: #04140b !important;
        font-weight: 700;
        margin: 0;
    }

    /* Fine print */
    .fine-print {
        color: #7c8a83;
        font-size: 0.8rem;
        margin-top: 1.5rem;
        line-height: 1.5;
        word-wrap: break-word;
    }
    
    .fine-print a {
        color: #4ade80;
        text-decoration: none;
    }

    /* Mobile responsiveness */
    @media (max-width: 1024px) {
        [data-testid="stHorizontalBlock"] {
            flex-direction: column;
            height: auto;
        }
        
        div[data-testid="column"]:has(> div .login-marker) {
            flex: 0 0 auto !important;
            max-width: 100% !important;
            border-right: none;
            border-bottom: 1px solid rgba(52, 211, 153, 0.08);
            padding: 2rem 1.5rem !important;
        }
        
        div[data-testid="column"]:has(> div .hero-marker) {
            flex: 1 1 auto !important;
            min-height: 50vh;
            padding: 2rem 1.5rem !important;
        }
    }

    @media (max-width: 768px) {
        div[data-testid="column"]:has(> div .login-marker) {
            padding: 1.5rem 1rem !important;
        }
        
        div[data-testid="column"]:has(> div .hero-marker) {
            padding: 1.5rem 1rem !important;
        }
        
        .logo-row .brand {
            font-size: 1.1rem;
        }
        
        .hero-title {
            font-size: clamp(1.3rem, 3vw, 2.2rem);
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 8px 6px !important;
            font-size: 0.8rem;
        }
    }

    @media (max-width: 480px) {
        div[data-testid="column"]:has(> div .login-marker) {
            padding: 1rem 0.75rem !important;
        }
        
        div[data-testid="column"]:has(> div .hero-marker) {
            padding: 1rem 0.75rem !important;
            min-height: 40vh;
        }
        
        .logo-row {
            margin-bottom: 1.5rem;
        }
        
        .logo-row .brand {
            font-size: 1rem;
        }
        
        .hero-title {
            font-size: clamp(1.1rem, 2.5vw, 1.8rem);
            margin-bottom: 1rem;
        }
        
        .hero-sub {
            font-size: 0.9rem;
        }
        
        .stTextInput input {
            padding: 0.7rem 0.8rem !important;
        }
        
        .stButton button {
            padding: 0.75rem 0.8rem !important;
        }
    }
</style>
"""


def login_view():
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)

    left, right = st.columns([1.2, 1.5], gap="medium")

    with left:
        st.markdown(
            """
            <div class="login-marker"></div>
            <div class="logo-row">
                <span class="flag">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M6 3h12a1 1 0 0 1 1 1v17l-7-4-7 4V4a1 1 0 0 1 1-1z" fill="#34d399"/>
                    </svg>
                </span>
                <span class="brand">Contract Analyzer</span>
            </div>
            <div class="section-label">Login / Register</div>
            """,
            unsafe_allow_html=True,
        )

        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            email = st.text_input("Email", key="login_email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", key="login_pw",
                                      placeholder="Enter your password")
            if st.button("Login", key="login_btn"):
                r = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
                if r.status_code == 200:
                    st.session_state.token = r.json()["access_token"]
                    me = requests.get(f"{API_URL}/auth/me", headers=auth_headers()).json()
                    st.session_state.user = me
                    st.rerun()
                else:
                    st.error(r.json().get("detail", "Login failed"))

        with tab2:
            name = st.text_input("Full Name", placeholder="Enter your full name")
            email_r = st.text_input("Email", key="reg_email", placeholder="Enter your email")
            pw_r = st.text_input("Password", type="password", key="reg_pw",
                                  placeholder="Choose a password")
            if st.button("Register", key="register_btn"):
                r = requests.post(f"{API_URL}/auth/register",
                                   json={"full_name": name, "email": email_r, "password": pw_r})
                if r.status_code == 201:
                    st.success("Registered! Please log in.")
                else:
                    st.error(r.json().get("detail", "Registration failed"))

        st.markdown(
            """
            <div class="fine-print">
                By continuing you agree to our <a href="#">Terms</a> and <a href="#">Privacy Policy</a>.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="hero-marker"></div>
            <div class="ai-badge"><span class="dot"></span> AI-POWERED</div>
            <div class="hero-title">
                Welcome to the <span class="accent">Contract &amp; Legal Document Risk Analyzer</span>
            </div>
            <div class="hero-sub">
                Please login or register to continue. Once you're in, upload any agreement
                and we'll flag termination windows, auto-renewals, and liability exposure in seconds.
            </div>
            <svg class="waves" width="100%" height="90" viewBox="0 0 420 90" preserveAspectRatio="xMidYMid meet" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M0 70 Q60 30 140 70 T280 70 T420 70" stroke="#2f5c40" stroke-width="1.5" opacity="0.6"/>
                <path d="M0 82 Q60 42 140 82 T280 82 T420 82" stroke="#2f5c40" stroke-width="1.5" opacity="0.4"/>
            </svg>
            """,
            unsafe_allow_html=True,
        )


def main_app():
    st.sidebar.title(f"👋 {st.session_state.user['full_name']}")
    st.sidebar.caption(f"Role: {st.session_state.user['role']}")
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()

    page = st.sidebar.radio("Navigate", ["Dashboard", "Upload & Analyze", "My Documents", "Search"])

    if page == "Dashboard":
        show_dashboard()
    elif page == "Upload & Analyze":
        show_upload()
    elif page == "My Documents":
        show_documents()
    elif page == "Search":
        show_search()


def show_dashboard():
    st.header("📊 AI Insights Dashboard")
    r = requests.get(f"{API_URL}/dashboard", headers=auth_headers())
    if r.status_code != 200:
        st.error("Failed to load dashboard")
        return
    stats = r.json()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Documents", stats["total_documents"])
    c2.metric("Average Risk Score", stats["average_risk_score"])
    c3.metric("High-Risk Documents", stats["high_risk_documents"])

    st.subheader("Frequently Detected Risks")
    if stats["frequently_detected_risks"]:
        st.table(stats["frequently_detected_risks"])
    else:
        st.info("No risk data yet — analyze a document first.")


def show_upload():
    st.header("📤 Upload & Analyze a Document")
    file = st.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])
    if file and st.button("Upload"):
        files = {"file": (file.name, file.getvalue())}
        r = requests.post(f"{API_URL}/documents/upload", headers=auth_headers(), files=files)
        if r.status_code == 201:
            doc = r.json()
            st.success(f"Uploaded: {doc['filename']} (ID: {doc['id']})")
            with st.spinner("Running AI analysis..."):
                ar = requests.post(f"{API_URL}/documents/{doc['id']}/analyze", headers=auth_headers())
            if ar.status_code == 200:
                render_analysis(ar.json())
            else:
                st.error(ar.json().get("detail", "Analysis failed"))
        else:
            st.error(r.json().get("detail", "Upload failed"))


def show_documents():
    st.header("📁 My Documents")
    r = requests.get(f"{API_URL}/documents", headers=auth_headers())
    docs = r.json() if r.status_code == 200 else []
    if not docs:
        st.info("No documents yet.")
        return

    for doc in docs:
        with st.expander(f"{doc['filename']} — {doc['status']}"):
            col1, col2, col3 = st.columns(3)
            if col1.button("View Analysis", key=f"view_{doc['id']}"):
                ar = requests.get(f"{API_URL}/documents/{doc['id']}/analysis", headers=auth_headers())
                if ar.status_code == 200:
                    render_analysis(ar.json())
                else:
                    st.warning("Not analyzed yet. Re-upload or trigger analysis.")
            if col2.button("Download PDF Report", key=f"pdf_{doc['id']}"):
                pr = requests.get(f"{API_URL}/reports/{doc['id']}/pdf", headers=auth_headers())
                if pr.status_code == 200:
                    st.download_button("Save PDF", pr.content, file_name=f"{doc['filename']}_report.pdf",
                                        key=f"dlpdf_{doc['id']}")
            if col3.button("Delete", key=f"del_{doc['id']}"):
                requests.delete(f"{API_URL}/documents/{doc['id']}", headers=auth_headers())
                st.rerun()


def show_search():
    st.header("🔍 Semantic Search")
    r = requests.get(f"{API_URL}/documents", headers=auth_headers())
    docs = r.json() if r.status_code == 200 else []
    analyzed = [d for d in docs if d["status"] == "analyzed"]
    if not analyzed:
        st.info("Analyze a document first to enable search.")
        return

    doc_map = {f"{d['filename']} (ID {d['id']})": d["id"] for d in analyzed}
    choice = st.selectbox("Select document", list(doc_map.keys()))
    query = st.text_input("Ask a question, e.g. 'Show payment terms'")
    if st.button("Search") and query:
        payload = {"document_id": doc_map[choice], "query": query, "top_k": 5}
        r = requests.post(f"{API_URL}/search", headers=auth_headers(), json=payload)
        if r.status_code == 200:
            results = r.json()
            for res in results:
                st.markdown(f"**Relevance: {round(res['score']*100)}%**")
                st.write(res["text"])
                st.divider()
        else:
            st.error(r.json().get("detail", "Search failed"))


def render_analysis(a: dict):
    st.subheader("📄 AI Analysis Results")
    st.metric("Risk Score", f"{a['risk_score']} / 100")
    st.caption(f"Engine used: {a['engine_used']}")

    st.write("**Contract Type:**", a.get("contract_type"))
    st.write("**Parties:**", ", ".join(a.get("parties") or []))
    st.write("**Effective Date:**", a.get("effective_date"))
    st.write("**Expiry Date:**", a.get("expiry_date"))

    st.markdown("### Executive Summary")
    st.write(a.get("executive_summary"))

    st.markdown("### Risk Findings")
    for risk in a.get("risks", []):
        color = {"high": "🔴", "medium": "🟠", "low": "🟡"}.get(risk["severity"], "⚪")
        st.markdown(f"{color} **[{risk['severity'].upper()}] {risk['title']}** "
                     f"— confidence {round(risk['confidence']*100)}%")
        st.write(risk["explanation"])

    st.markdown("### Recommended Actions")
    for action in a.get("recommended_actions") or []:
        st.write(f"- {action}")


if st.session_state.token is None:
    login_view()
else:
    main_app()
