import streamlit as st
import os
import datetime
from summarizer import read_file, generate_txt_bytes, generate_pdf_bytes, generate_combined_txt_bytes, generate_pdf_bytes_multi
from ai_analyzer import AIAnalyzer
from database import SessionLocal, User, Document, get_db
from sqlalchemy.orm import Session

# BUILD VERSION: 2026-07-07_v3.0 - REFINED NUCLEAR UI

st.set_page_config(
    page_title="Contract Analyzer AI",
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Global State ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# --- NUCLEAR CSS OVERRIDES ---
nuclear_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* 1. HIDE ALL DEFAULT ELEMENTS */
    header, [data-testid="stSidebar"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important;
    }

    /* 2. FORCE FULL SCREEN */
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

    /* 3. AUTH LAYOUT ENGINE */
    .nuclear-auth-container {
        display: flex;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
        background: #05170f;
    }

    .nuclear-left {
        width: 420px;
        background: linear-gradient(180deg, #08201548 0%, #05170f 100%), #071f14;
        border-right: 1px solid rgba(255,255,255,0.08);
        padding: 40px;
        display: flex;
        flex-direction: column;
        z-index: 100;
        position: relative;
    }

    .nuclear-right {
        flex: 1;
        background: linear-gradient(180deg, #04140d 0%, #061a11 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        overflow: hidden;
    }

    /* 4. BACKGROUND ORBS */
    .orb {
        position: absolute;
        border-radius: 50%;
        pointer-events: none;
    }
    .orb-1 {
        width: 620px; height: 620px;
        right: -180px; top: -220px;
        background: radial-gradient(circle at 35% 30%, rgba(52,217,128,0.55), rgba(15,107,69,0.15) 60%, transparent 75%);
    }
    .orb-2 {
        width: 420px; height: 420px;
        right: -40px; top: 40px;
        border: 1px solid rgba(52,217,128,0.35);
        background: radial-gradient(circle at 30% 25%, rgba(23,167,95,0.55), transparent 70%);
    }
    .orb-3 {
        width: 260px; height: 260px;
        right: 210px; top: 210px;
        border: 1px solid rgba(52,217,128,0.28);
    }
    .orb-4 {
        width: 130px; height: 130px;
        left: 60px; bottom: 90px;
        border: 1px solid rgba(52,217,128,0.22);
        background: radial-gradient(circle at 35% 30%, rgba(23,167,95,0.25), transparent 70%);
    }

    /* 5. DESIGN TOKENS */
    .logo-v2 {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 20px;
        font-weight: 800;
        color: #fff;
        margin-bottom: 56px;
    }

    .hero-v2 {
        text-align: center;
        max-width: 720px;
        z-index: 10;
        padding: 60px;
    }

    .pill-v2 {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        font-weight: 600;
        color: #34d980;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        background: rgba(52,217,128,0.08);
        border: 1px solid rgba(52,217,128,0.25);
        padding: 7px 14px;
        border-radius: 999px;
        margin-bottom: 26px;
    }
    .pill-v2::before {
        content: '';
        width: 6px; height: 6px;
        border-radius: 50%;
        background: #34d980;
        box-shadow: 0 0 8px #22c76e;
    }

    h1.v2-title {
        font-size: clamp(30px, 3.4vw, 44px);
        font-weight: 800;
        line-height: 1.18;
        letter-spacing: -0.01em;
        margin: 0 0 22px;
        color: #fff;
    }

    h1.v2-title span {
        background: linear-gradient(180deg, #34d980, #17a75f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-v2 p {
        font-size: 16.5px;
        line-height: 1.7;
        color: #b6d9c6;
        max-width: 560px;
        margin: 0 auto;
    }

    /* 6. WIDGET OVERRIDES */
    .stButton button {
        width: 100% !important;
        background: linear-gradient(180deg, #34d980, #17a75f) !important;
        color: #04170e !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 14px 0 !important;
        border: none !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 24px -8px rgba(34,199,110,0.55) !important;
        transition: filter .15s ease !important;
    }
    .stButton button:hover {
        filter: brightness(1.05) !important;
    }

    div[data-baseweb="input"] {
        background-color: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 10px !important;
        transition: border-color .15s ease, background .15s ease !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #34d980 !important;
        background-color: rgba(52,217,128,0.06) !important;
    }

    input {
        color: white !important;
        font-size: 14.5px !important;
    }

    /* Radio tabs styling */
    div[data-testid="stRadio"] > div {
        display: flex !important;
        gap: 4px !important;
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 12px !important;
        padding: 4px !important;
        margin-bottom: 30px !important;
    }
    div[data-testid="stRadio"] label {
        flex: 1 !important;
        text-align: center !important;
        padding: 10px 0 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #b6d9c6 !important;
        border-radius: 9px !important;
        cursor: pointer !important;
        transition: all .15s ease !important;
        background: transparent !important;
        border: none !important;
        display: block !important;
    }
    div[data-testid="stRadio"] label[data-selected="true"] {
        background: linear-gradient(180deg, #34d980, #17a75f) !important;
        color: #04170e !important;
    }
    /* Hide radio dots */
    div[data-testid="stRadio"] input {
        display: none !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > div {
        padding: 0 !important;
        margin: 0 !important;
        flex: 1 !important;
    }

    .auth-foot {
        margin-top: auto;
        padding-top: 30px;
        font-size: 12.5px;
        color: #b6d9c6;
        opacity: 0.65;
        line-height: 1.6;
    }
    .auth-foot a { color: #34d980; text-decoration: none; }

    /* Waves SVG */
    .waves {
        position: absolute;
        left: 20px; bottom: 30px;
        width: 320px; height: 100px;
        pointer-events: none;
    }
</style>
"""

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
    st.markdown(nuclear_css, unsafe_allow_html=True)
    
    # Force the layout structure
    st.markdown("""
    <div class="nuclear-auth-container">
        <div class="nuclear-left">
            <div class="logo-v2">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                    <path d="M4 3v18l8-5 8 5V3a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1z" fill="url(#g)"/>
                    <defs>
                        <linearGradient id="g" x1="4" y1="2" x2="20" y2="21" gradientUnits="userSpaceOnUse">
                            <stop stop-color="#34d980"/>
                            <stop offset="1" stop-color="#0f6b45"/>
                        </linearGradient>
                    </defs>
                </svg>
                Contract Analyzer
            </div>
            <div style="font-size: 14px; font-weight: 600; color: #b6d9c6; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 18px;">Login / Register</div>
            
            <!-- Auth form placeholder -->
            <div id="auth-anchor" style="height: 400px;"></div>

            <div class="auth-foot">
                By continuing you agree to our <a href="#">Terms</a> and <a href="#">Privacy Policy</a>.
            </div>
        </div>
        <div class="nuclear-right">
            <div class="orb orb-1"></div>
            <div class="orb orb-2"></div>
            <div class="orb orb-3"></div>
            <div class="orb orb-4"></div>
            
            <svg class="waves" viewBox="0 0 320 100" fill="none">
                <path d="M0 80 C 60 40, 120 100, 180 60 S 300 20, 320 50" stroke="rgba(52,217,128,0.35)" stroke-width="1.5"/>
                <path d="M0 92 C 60 55, 120 110, 180 72 S 300 32, 320 62" stroke="rgba(52,217,128,0.22)" stroke-width="1.5"/>
                <path d="M0 100 C 60 68, 120 118, 180 84 S 300 44, 320 74" stroke="rgba(52,217,128,0.14)" stroke-width="1.5"/>
            </svg>

            <div class="hero-v2">
                <div class="pill-v2">AI-Powered</div>
                <h1 class="v2-title">Welcome to the <span>Contract & Legal<br>Document Risk Analyzer</span></h1>
                <p>Please login or register to continue. Once you're in, upload any agreement and we'll flag termination windows, auto-renewals, and liability exposure in seconds.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Place Streamlit widgets using absolute positioning logic
    with st.container():
        # Adjusting the position to match the anchor in the HTML
        st.markdown('<div style="position: absolute; top: 155px; left: 40px; width: 340px; z-index: 101;">', unsafe_allow_html=True)
        
        mode = st.radio("Mode", ["Login", "Register"], label_visibility="collapsed")
        
        if mode == "Login":
            u = st.text_input("Username", key="u_login", placeholder="Enter your username")
            p = st.text_input("Password", type="password", key="p_login", placeholder="Enter your password")
            st.markdown('<div style="margin-top: 10px;">', unsafe_allow_html=True)
            if st.button("Login"):
                if authenticate_user(u, p):
                    st.rerun()
                else:
                    st.error("Invalid login")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            u = st.text_input("Username", key="u_reg", placeholder="Choose a username")
            p = st.text_input("Password", type="password", key="p_reg", placeholder="Choose a password")
            st.markdown('<div style="margin-top: 10px;">', unsafe_allow_html=True)
            if st.button("Create Account"):
                if register_user(u, p):
                    st.success("Account created!")
                else:
                    st.error("User exists")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # Workspace UI
    st.markdown("<style>header {display: flex !important;} [data-testid='stSidebar'] {display: flex !important;}</style>", unsafe_allow_html=True)
    with st.sidebar:
        st.title("Contract AI")
        st.write(f"User: {st.session_state['username']}")
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()
    
    st.title("Document Analysis")
    st.write("Welcome to your workspace.")
