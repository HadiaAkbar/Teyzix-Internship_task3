# VERSION: 1.0.1 - CACHE BUST
import streamlit as st
import os
import datetime
from summarizer import read_file, generate_txt_bytes, generate_pdf_bytes, generate_combined_txt_bytes, generate_pdf_bytes_multi
from ai_analyzer import AIAnalyzer
from database import SessionLocal, User, Document, get_db
from sqlalchemy.orm import Session

# BUILD VERSION: 2026-07-08_v12.0 - STABLE CLOUD BUILD

st.set_page_config(
    page_title="Contract Analyzer AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Global State ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# --- Auth Functions ---
def authenticate_user(username, password):
    try:
        db: Session = next(get_db())
        user = db.query(User).filter(User.username == username).first()
        if user and user.password_hash == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["user_id"] = user.id
            st.session_state["user_role"] = user.role
            return True
    except Exception as e:
        st.error(f"Database error: {e}")
    return False

def register_user(username, password):
    try:
        db: Session = next(get_db())
        if db.query(User).filter(User.username == username).first():
            return False
        new_user = User(username=username, password_hash=password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
    return False


# --- CSS: turns the two st.columns into the fixed-width auth panel + hero layout ---
AUTH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root{
  --bg: #05170f;
  --bg-2: #061a11;
  --bg-3: #020c08;
  --green-1: #0f6b45;
  --green-2: #17a75f;
  --green-3: #34d980;
  --green-glow: #22c76e;
  --text: #eafff3;
  --text-soft: #b6d9c6;
  --line: rgba(255,255,255,0.08);
}

header, [data-testid="stSidebar"], [data-testid="stToolbar"], [data-testid="stDecoration"],
footer, #MainMenu {display: none !important;}

html, body, .stApp {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}
.main .block-container {padding: 0 !important; margin: 0 !important; max-width: 100% !important;}

/* Turn the two-column row into the split-panel layout */
[data-testid="stHorizontalBlock"]{
  gap: 0 !important;
  align-items: stretch !important;
}
[data-testid="stHorizontalBlock"] > div:nth-of-type(1){
  flex: 0 0 440px !important;
  max-width: 440px !important;
  min-width: 440px !important;
  background: var(--bg-2);
  border-right: 1px solid var(--line);
  padding: 56px 44px 40px !important;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
[data-testid="stHorizontalBlock"] > div:nth-of-type(2){
  flex: 1 1 auto !important;
  background: linear-gradient(180deg, #04140d 0%, var(--bg-3) 100%);
  position: relative;
  overflow: hidden;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px !important;
}

/* Logo + section label */
.logo-v2{
  display:flex; align-items:center; gap:10px;
  font-size: 20px; font-weight:800; color:#fff;
  margin-bottom: 46px;
}
.section-label{
  font-size: 13px; font-weight:700; color: var(--text-soft);
  text-transform: uppercase; letter-spacing: 0.08em;
  margin-bottom: 20px;
}

/* Radio-as-tabs */
div[data-testid="stRadio"] > div{
  display:flex !important;
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid var(--line) !important;
  border-radius: 12px !important;
  padding: 4px !important;
  gap: 4px;
  margin-bottom: 8px !important;
}
div[data-testid="stRadio"] label{
  flex:1 !important;
  text-align:center !important;
  justify-content:center !important;
  padding: 9px 0 !important;
  border-radius: 9px !important;
  color: var(--text-soft) !important;
  font-weight:600 !important;
  background: transparent !important;
  margin: 0 !important;
  transition: all .15s ease;
}
div[data-testid="stRadio"] label[data-checked="true"],
div[data-testid="stRadio"] label:has(input:checked){
  background: linear-gradient(180deg, var(--green-3), var(--green-2)) !important;
  color: #04170e !important;
}
div[data-testid="stRadio"] input{ display:none !important; }
div[data-testid="stRadio"] label > div:first-child{ display:none !important; }

/* Text inputs */
div[data-baseweb="input"]{
  background-color: rgba(255,255,255,0.04) !important;
  border: 1px solid var(--line) !important;
  border-radius: 10px !important;
}
div[data-baseweb="input"]:focus-within{
  border-color: var(--green-3) !important;
  background-color: rgba(52,217,128,0.06) !important;
}
input{
  color: #fff !important;
  font-family: 'Inter', sans-serif !important;
}
label{
  color: var(--text-soft) !important;
  font-size: 13px !important;
  font-weight: 600 !important;
}
[data-testid="stTextInput"]{ margin-bottom: 4px; }

/* Primary button */
.stButton button{
  width:100% !important;
  background: linear-gradient(180deg, var(--green-3), var(--green-2)) !important;
  color: #04170e !important;
  font-weight:700 !important;
  font-size:15px !important;
  padding: 12px 0 !important;
  border:none !important;
  border-radius:10px !important;
  margin-top: 10px !important;
  box-shadow: 0 10px 24px -8px rgba(34,199,110,0.55);
}
.stButton button:hover{ filter: brightness(1.05); color: #04170e !important; }

.auth-footer{
  margin-top: auto;
  padding-top: 30px;
  font-size: 12.5px;
  color: var(--text-soft);
  opacity: 0.65;
  line-height: 1.6;
}
.auth-footer a{ color: var(--green-3); text-decoration:none; }

/* Hero (right panel) */
.orb{ position:absolute; border-radius:50%; pointer-events:none; }
.orb-1{ width:620px; height:620px; right:-180px; top:-220px;
  background: radial-gradient(circle at 35% 30%, rgba(52,217,128,0.55), rgba(15,107,69,0.15) 60%, transparent 75%); }
.orb-2{ width:420px; height:420px; right:-40px; top:40px;
  border:1px solid rgba(52,217,128,0.35);
  background: radial-gradient(circle at 30% 25%, rgba(23,167,95,0.55), transparent 70%); }
.orb-3{ width:260px; height:260px; right:210px; top:210px; border:1px solid rgba(52,217,128,0.28); }
.orb-4{ width:130px; height:130px; left:60px; bottom:90px;
  border:1px solid rgba(52,217,128,0.22);
  background: radial-gradient(circle at 35% 30%, rgba(23,167,95,0.25), transparent 70%); }
.waves-container{ position:absolute; left:20px; bottom:30px; width:320px; height:100px; pointer-events:none; }

.hero-copy{ position:relative; z-index:2; max-width:640px; text-align:center; }
.pill-v2{
  display:inline-flex; align-items:center; gap:8px;
  font-size:13px; font-weight:600; color: var(--green-3);
  text-transform:uppercase; letter-spacing:0.08em;
  background: rgba(52,217,128,0.08);
  border: 1px solid rgba(52,217,128,0.25);
  padding: 7px 14px; border-radius: 999px;
  margin-bottom: 26px;
}
.pill-v2::before{
  content:''; width:6px; height:6px; border-radius:50%;
  background: var(--green-3); box-shadow: 0 0 8px var(--green-glow);
}
.v2-title{
  font-size: clamp(28px, 3vw, 42px);
  font-weight:800; line-height:1.18; letter-spacing:-0.01em;
  margin: 0 0 22px; color:#fff;
}
.v2-title span{
  background: linear-gradient(180deg, var(--green-3), var(--green-2));
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero-copy p{
  font-size: 16px; line-height:1.7; color: var(--text-soft);
  max-width: 540px; margin: 0 auto;
}

@media (max-width: 900px){
  [data-testid="stHorizontalBlock"] > div:nth-of-type(1){ flex: 1 1 100% !important; max-width:100% !important; min-width:0 !important; }
  [data-testid="stHorizontalBlock"] > div:nth-of-type(2){ display:none !important; }
}
</style>
"""

HERO_HTML = """
<div class="orb orb-1"></div>
<div class="orb orb-2"></div>
<div class="orb orb-3"></div>
<div class="orb orb-4"></div>
<svg class="waves-container" viewBox="0 0 320 100" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M0 80 C 60 40, 120 100, 180 60 S 300 20, 320 50" stroke="rgba(52,217,128,0.35)" stroke-width="1.5"/>
<path d="M0 92 C 60 55, 120 110, 180 72 S 300 32, 320 62" stroke="rgba(52,217,128,0.22)" stroke-width="1.5"/>
<path d="M0 100 C 60 68, 120 118, 180 84 S 300 44, 320 74" stroke="rgba(52,217,128,0.14)" stroke-width="1.5"/>
</svg>
<div class="hero-copy">
<div class="pill-v2">AI-Powered</div>
<h1 class="v2-title">Welcome to the <span>Contract &amp; Legal Document Risk Analyzer</span></h1>
<p>Please login or register to continue. Once you're in, upload any agreement and we'll flag termination windows, auto-renewals, and liability exposure in seconds.</p>
</div>
""".strip()

LOGO_HTML = """
<div class="logo-v2">
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M19 21L12 16L5 21V5C5 4.46957 5.21071 3.96086 5.58579 3.58579C5.96086 3.21071 6.46957 3 7 3H17C17.5304 3 18.0391 3.21071 18.4142 3.58579C18.7893 3.96086 19 4.46957 19 5V21Z" fill="#34d980"/>
</svg>
Contract Analyzer
</div>
<div class="section-label">LOGIN / REGISTER</div>
"""

# --- Main Logic ---
if not st.session_state["logged_in"]:
    st.markdown(AUTH_CSS, unsafe_allow_html=True)

    left, right = st.columns([1, 1.6], gap="small")

    with left:
        st.markdown(LOGO_HTML, unsafe_allow_html=True)

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

        st.markdown(
            '<div class="auth-footer">By continuing you agree to our '
            '<a href="#">Terms</a> and <a href="#">Privacy Policy</a>.</div>',
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(HERO_HTML, unsafe_allow_html=True)

else:
    st.markdown(
        "<style>header {display: flex !important;} [data-testid='stSidebar'] {display: flex !important;}</style>",
        unsafe_allow_html=True,
    )
    with st.sidebar:
        st.title("Contract AI")
        # Fixed syntax error in f-string
        user_name = st.session_state.get('username', 'User')
        user_role = st.session_state.get('user_role', 'user')
        st.write(f"Logged in as: **{user_name}** ({user_role})")
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()

    st.title("Document Analysis")
    st.write("Welcome to your AI-powered contract analysis workspace.")
