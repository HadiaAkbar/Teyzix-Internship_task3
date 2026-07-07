import streamlit as st
import os
import datetime
import textwrap
from summarizer import read_file, generate_txt_bytes, generate_pdf_bytes, generate_combined_txt_bytes, generate_pdf_bytes_multi
from ai_analyzer import AIAnalyzer
from database import SessionLocal, User, Document, get_db
from sqlalchemy.orm import Session

# BUILD VERSION: 2026-07-07_v8.0 - ROBUST RENDER

st.set_page_config(
    page_title="Contract Analyzer AI",
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Global State ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# --- CSS OVERRIDES ---
# We use st.components.v1.html for complex layouts if needed, but here we'll stick to st.markdown
# with extremely careful string handling.
def get_css():
    return textwrap.dedent("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
            header, [data-testid="stSidebar"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
                display: none !important;
            }
            .main .block-container {
                padding: 0 !important;
                margin: 0 !important;
                max-width: 100% !important;
                width: 100% !important;
            }
            .stApp {
                background-color: #05170f !important;
                color: #eafff3 !important;
                font-family: 'Inter', sans-serif !important;
            }
            .nuclear-auth-container {
                display: flex;
                width: 100vw;
                height: 100vh;
                overflow: hidden;
                background: #05170f;
            }
            .nuclear-left {
                width: 450px;
                background: #061a11;
                border-right: 1px solid rgba(255,255,255,0.05);
                padding: 60px 50px;
                display: flex;
                flex-direction: column;
                z-index: 100;
                position: relative;
            }
            .nuclear-right {
                flex: 1;
                background: #020c08;
                display: flex;
                align-items: center;
                justify-content: center;
                position: relative;
                overflow: hidden;
            }
            .orb {
                position: absolute;
                border-radius: 50%;
                pointer-events: none;
            }
            .orb-1 {
                width: 800px; height: 800px;
                right: -200px; top: -200px;
                background: radial-gradient(circle, rgba(52,217,128,0.15) 0%, transparent 70%);
            }
            .orb-2 {
                width: 600px; height: 600px;
                right: 10%; top: 10%;
                background: radial-gradient(circle, rgba(23,167,95,0.1) 0%, transparent 70%);
            }
            .circle-line {
                position: absolute;
                border: 1px solid rgba(52,217,128,0.1);
                border-radius: 50%;
                pointer-events: none;
            }
            .logo-v2 {
                display: flex;
                align-items: center;
                gap: 12px;
                font-size: 22px;
                font-weight: 700;
                color: #fff;
                margin-bottom: 60px;
            }
            .section-label {
                font-size: 14px;
                font-weight: 700;
                color: #b6d9c6;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                margin-bottom: 25px;
            }
            .hero-v2 {
                text-align: center;
                max-width: 800px;
                z-index: 10;
                padding: 40px;
            }
            .pill-v2 {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                font-size: 12px;
                font-weight: 700;
                color: #34d980;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                background: rgba(52,217,128,0.1);
                border: 1px solid rgba(52,217,128,0.2);
                padding: 6px 16px;
                border-radius: 20px;
                margin-bottom: 30px;
            }
            .pill-v2::before {
                content: '';
                width: 6px; height: 6px;
                border-radius: 50%;
                background: #34d980;
                box-shadow: 0 0 10px #34d980;
            }
            h1.v2-title {
                font-size: 48px;
                font-weight: 800;
                line-height: 1.1;
                margin-bottom: 30px;
                color: #fff;
            }
            h1.v2-title span {
                color: #34d980;
            }
            .hero-v2 p {
                font-size: 18px;
                line-height: 1.6;
                color: #b6d9c6;
                max-width: 600px;
                margin: 0 auto;
            }
            .stButton button {
                width: 100% !important;
                background: linear-gradient(90deg, #34d980, #17a75f) !important;
                color: #05170f !important;
                font-weight: 700 !important;
                font-size: 16px !important;
                padding: 12px 0 !important;
                border: none !important;
                border-radius: 8px !important;
                margin-top: 20px !important;
            }
            div[data-baseweb="input"] {
                background-color: #0d251a !important;
                border: 1px solid #1a3a2a !important;
                border-radius: 8px !important;
            }
            input {
                color: #fff !important;
            }
            label {
                color: #b6d9c6 !important;
                font-size: 14px !important;
                font-weight: 500 !important;
            }
            div[data-testid="stRadio"] > div {
                display: flex !important;
                background: #0d251a !important;
                border: 1px solid #1a3a2a !important;
                border-radius: 8px !important;
                padding: 4px !important;
                margin-bottom: 30px !important;
            }
            div[data-testid="stRadio"] label {
                flex: 1 !important;
                text-align: center !important;
                padding: 8px 0 !important;
                border-radius: 6px !important;
                color: #b6d9c6 !important;
                font-weight: 600 !important;
                background: transparent !important;
            }
            div[data-testid="stRadio"] label[data-selected="true"] {
                background: linear-gradient(90deg, #34d980, #17a75f) !important;
                color: #05170f !important;
            }
            div[data-testid="stRadio"] input {
                display: none !important;
            }
            .auth-footer {
                margin-top: auto;
                font-size: 13px;
                color: #b6d9c6;
                opacity: 0.8;
            }
            .auth-footer a {
                color: #34d980;
                text-decoration: none;
            }
            .waves-container {
                position: absolute;
                bottom: 0;
                left: 0;
                width: 100%;
                height: 150px;
                opacity: 0.3;
                pointer-events: none;
            }
        </style>
    """).strip()

def get_auth_html():
    return textwrap.dedent("""
        <div class="nuclear-auth-container">
            <div class="nuclear-left">
                <div class="logo-v2">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M19 21L12 16L5 21V5C5 4.46957 5.21071 3.96086 5.58579 3.58579C5.96086 3.21071 6.46957 3 7 3H17C17.5304 3 18.0391 3.21071 18.4142 3.58579C18.7893 3.96086 19 4.46957 19 5V21Z" fill="#34d980"/>
                    </svg>
                    Contract Analyzer
                </div>
                <div class="section-label">LOGIN / REGISTER</div>
                <div id="form-container" style="min-height: 400px;"></div>
                <div class="auth-footer">
                    By continuing you agree to our <a href="#">Terms</a> and <a href="#">Privacy Policy</a>.
                </div>
            </div>
            <div class="nuclear-right">
                <div class="orb orb-1"></div>
                <div class="orb orb-2"></div>
                <div class="circle-line" style="width: 500px; height: 500px; right: 5%; top: 5%;"></div>
                <div class="circle-line" style="width: 700px; height: 700px; right: -5%; top: -5%;"></div>
                <div class="hero-v2">
                    <div class="pill-v2">AI-POWERED</div>
                    <h1 class="v2-title">Welcome to the <span>Contract & Legal<br>Document Risk Analyzer</span></h1>
                    <p>Please login or register to continue. Once you're in, upload any agreement and we'll flag termination windows, auto-renewals, and liability exposure in seconds.</p>
                </div>
                <div class="waves-container">
                    <svg viewBox="0 0 1440 320" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M0 160L48 176C96 192 192 224 288 224C384 224 480 192 576 165.3C672 139 768 117 864 128C960 139 1056 181 1152 192C1248 203 1344 181 1392 170.7L1440 160V320H1392C1344 320 1248 320 1152 320C1056 320 960 320 864 320C768 320 672 320 576 320C480 320 384 320 288 320C192 320 96 320 48 320H0V160Z" fill="#34d980" fill-opacity="0.05"/>
                    </svg>
                </div>
            </div>
        </div>
    """).strip()

# --- Auth Functions ---
def authenticate_user(username, password):
    db: Session = next(get_db())
    user = db.query(User).filter(User.username == username).first()
    if user and user.password_hash == password:
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["user_id"] = user.id
        st.session_state["user_role"] = user.role
        return True
    return False

def register_user(username, password):
    db: Session = next(get_db())
    if db.query(User).filter(User.username == username).first():
        return False
    new_user = User(username=username, password_hash=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return True

# --- Main Logic ---
if not st.session_state["logged_in"]:
    # Using st.markdown with unsafe_allow_html=True
    # To avoid markdown parsing issues, we ensure no leading spaces or special markdown chars.
    st.markdown(get_css(), unsafe_allow_html=True)
    st.markdown(get_auth_html(), unsafe_allow_html=True)

    # Inject Streamlit widgets into the left panel
    # We use a container and then absolute positioning.
    with st.container():
        st.markdown(textwrap.dedent("""
            <div style="position: absolute; top: 185px; left: 50px; width: 350px; z-index: 1000;">
        """).strip(), unsafe_allow_html=True)
        
        mode = st.radio("AuthMode", ["Login", "Register"], label_visibility="collapsed")
        
        if mode == "Login":
            username = st.text_input("Username", placeholder="Enter your username", key="login_user")
            password = st.text_input("Password", placeholder="Enter your password", type="password", key="login_pass")
            if st.button("Login", key="btn_login"):
                if authenticate_user(username, password):
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        else:
            username = st.text_input("Username", placeholder="Enter your username", key="reg_user")
            password = st.text_input("Password", placeholder="Enter your password", type="password", key="reg_pass")
            if st.button("Register", key="btn_reg"):
                if register_user(username, password):
                    st.success("Account created! Please login.")
                else:
                    st.error("Username already exists")
        
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("<style>header {display: flex !important;} [data-testid='stSidebar'] {display: flex !important;}</style>", unsafe_allow_html=True)
    with st.sidebar:
        st.title("Contract AI")
        st.write(f"Logged in as: **{st.session_state['username']}**")
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()
    
    st.title("Document Analysis")
    st.write("Welcome to your AI-powered contract analysis workspace.")
