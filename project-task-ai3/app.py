import streamlit as st
import os
import datetime
from summarizer import read_file, generate_txt_bytes, generate_pdf_bytes, generate_combined_txt_bytes, generate_pdf_bytes_multi
from ai_analyzer import AIAnalyzer
from database import SessionLocal, User, Document, get_db
from sqlalchemy.orm import Session

# BUILD VERSION: 2026-07-07_v2.0 - NUCLEAR UI OVERHAUL

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
# Using !important on everything to fight Streamlit's internal CSS
nuclear_css = """
<style>
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
        background: #071f14;
        border-right: 1px solid rgba(255,255,255,0.08);
        padding: 60px 40px;
        display: flex;
        flex-direction: column;
        z-index: 100;
    }

    .nuclear-right {
        flex: 1;
        background: linear-gradient(180deg, #04140d 0%, #061a11 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }

    /* 4. DESIGN TOKENS */
    .logo-v2 {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 22px;
        font-weight: 800;
        color: #fff;
        margin-bottom: 50px;
    }

    .hero-v2 {
        text-align: center;
        max-width: 600px;
        z-index: 10;
    }

    .pill-v2 {
        display: inline-block;
        padding: 6px 14px;
        background: rgba(52,217,128,0.1);
        border: 1px solid rgba(52,217,128,0.2);
        border-radius: 100px;
        color: #34d980;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 24px;
    }

    h1.v2-title {
        font-size: 44px;
        font-weight: 800;
        line-height: 1.2;
        color: white;
        margin-bottom: 20px;
    }

    h1.v2-title span {
        background: linear-gradient(180deg, #34d980, #17a75f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* 5. WIDGET OVERRIDES */
    .stButton button {
        background: linear-gradient(180deg, #34d980, #17a75f) !important;
        color: #04170e !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        padding: 14px !important;
        border: none !important;
        box-shadow: 0 10px 20px rgba(52,217,128,0.3) !important;
    }

    div[data-baseweb="input"] {
        background-color: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 10px !important;
    }

    input {
        color: white !important;
    }

    /* Version Marker */
    .version-marker {
        position: fixed;
        bottom: 10px;
        right: 10px;
        font-size: 10px;
        color: rgba(255,255,255,0.2);
        z-index: 999;
    }
</style>
<div class="version-marker">Build: 2026-07-07_v2.0</div>
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
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
                    <path d="M4 3v18l8-5 8 5V3a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1z" fill="#34d980"/>
                </svg>
                Contract Analyzer
            </div>
            <div style="font-size: 13px; font-weight: 600; color: #b6d9c6; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 24px;">Login / Register</div>
        </div>
        <div class="nuclear-right">
            <div class="hero-v2">
                <div class="pill-v2">AI-Powered</div>
                <h1 class="v2-title">Welcome to the<br><span>Contract & Legal<br>Document Risk Analyzer</span></h1>
                <p style="color: #b6d9c6; line-height: 1.6;">Upload any agreement and we'll flag termination windows, auto-renewals, and liability exposure in seconds.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Place Streamlit widgets using absolute positioning logic
    # We use a container that overlaps the left panel
    with st.container():
        # This creates a vertical gap to align with the "Login / Register" text
        st.markdown('<div style="position: absolute; top: 200px; left: 40px; width: 340px; z-index: 101;">', unsafe_allow_html=True)
        
        mode = st.radio("Mode", ["Login", "Register"], label_visibility="collapsed")
        
        if mode == "Login":
            u = st.text_input("Username", key="u_login")
            p = st.text_input("Password", type="password", key="p_login")
            if st.button("Login"):
                if authenticate_user(u, p):
                    st.rerun()
                else:
                    st.error("Invalid login")
        else:
            u = st.text_input("New Username", key="u_reg")
            p = st.text_input("New Password", type="password", key="p_reg")
            if st.button("Create Account"):
                if register_user(u, p):
                    st.success("Account created!")
                else:
                    st.error("User exists")
        
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
