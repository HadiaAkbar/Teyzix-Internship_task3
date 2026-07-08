import streamlit as st
import requests

# Set correct local API URL
API_URL = st.secrets.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Contract Risk Analyzer", layout="wide", initial_sidebar_state="expanded")

if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.user = None

def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}

# CSS (Keeping original UI)
LOGIN_CSS = """
<style>
    * {box-sizing: border-box;}
    html, body {margin: 0; padding: 0;}
    #MainMenu, header, footer {visibility: hidden;}
    .block-container {padding: 0 !important; max-width: 100% !important;}
    .stApp {
        background-color: #061109;
        background-image: 
            radial-gradient(circle 300px at 10% 20%, rgba(52, 211, 153, 0.15) 0%, transparent 50%),
            radial-gradient(circle 250px at 90% 80%, rgba(34, 197, 94, 0.12) 0%, transparent 50%),
            radial-gradient(circle 200px at 50% 50%, rgba(52, 211, 153, 0.08) 0%, transparent 50%);
        background-attachment: fixed;
    }
    [data-testid="stHorizontalBlock"] {
        min-height: 100vh;
        align-items: center;
        justify-content: center;
    }
    .login-card {
        background: #0d1a13;
        border: 3px solid #34d399;
        border-radius: 28px;
        padding: 3rem;
        box-shadow: 0 0 30px rgba(52, 211, 153, 0.25);
    }
    .brand { color: #ffffff; font-size: 1.5rem; font-weight: 800; }
    .accent { color: #34d399; }
</style>
"""

def login_view():
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)
    left, right = st.columns([1, 1])

    with left:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown('<div class="brand">Contract Analyzer</div>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            email = st.text_input("Email", key="l_email")
            password = st.text_input("Password", type="password", key="l_pw")
            if st.button("Login Now"):
                try:
                    r = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
                    if r.status_code == 200:
                        st.session_state.token = r.json()["access_token"]
                        me_r = requests.get(f"{API_URL}/auth/me", headers=auth_headers())
                        if me_r.status_code == 200:
                            st.session_state.user = me_r.json()
                            st.rerun()
                        else:
                            st.error("Profile fetch failed")
                    else:
                        st.error(r.json().get("detail", "Login failed"))
                except Exception:
                    st.error("Server Error (Status: 502) - Check backend")

        with tab2:
            name = st.text_input("Full Name")
            reg_email = st.text_input("Email", key="r_email")
            reg_pw = st.text_input("Password", type="password", key="r_pw")
            if st.button("Create Account"):
                try:
                    r = requests.post(f"{API_URL}/auth/register", 
                                    json={"full_name": name, "email": reg_email, "password": reg_pw})
                    if r.status_code == 201:
                        st.success("Registered! Please log in.")
                    else:
                        st.error(r.json().get("detail", "Registration failed"))
                except Exception:
                    st.error("Server Error (Status: 502)")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown(f'# Analyze Contracts with <span class="accent">AI Precision</span>', unsafe_allow_html=True)
        st.write("Upload any agreement and we'll automatically flag risks in seconds.")

def main_app():
    st.sidebar.title(f"👋 {st.session_state.user['full_name']}")
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()
    
    page = st.sidebar.radio("Navigate", ["Dashboard", "Upload", "Documents"])
    if page == "Dashboard":
        show_dashboard()
    elif page == "Upload":
        show_upload()
    elif page == "Documents":
        show_documents()

def show_dashboard():
    st.header("📊 Dashboard")
    try:
        r = requests.get(f"{API_URL}/dashboard", headers=auth_headers())
        if r.status_code == 200:
            st.json(r.json())
    except Exception:
        st.error("Dashboard failed")

def show_upload():
    st.header("📤 Upload")
    file = st.file_uploader("Choose file", type=["pdf", "docx", "txt"])
    if file and st.button("Analyze"):
        try:
            r = requests.post(f"{API_URL}/documents/upload", headers=auth_headers(), files={"file": file})
            if r.status_code == 201:
                doc_id = r.json()["id"]
                res = requests.post(f"{API_URL}/documents/{doc_id}/analyze", headers=auth_headers())
                if res.status_code == 200:
                    st.success("Analysis Complete!")
                    st.json(res.json())
        except Exception:
            st.error("Processing failed")

def show_documents():
    st.header("📚 Documents")
    try:
        r = requests.get(f"{API_URL}/documents", headers=auth_headers())
        if r.status_code == 200:
            st.json(r.json())
    except Exception:
        st.error("Load failed")

if __name__ == "__main__":
    if st.session_state.token:
        main_app()
    else:
        login_view()
