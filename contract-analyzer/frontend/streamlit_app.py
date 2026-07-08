import streamlit as st
import requests
import math

import os

# Determine API_URL based on environment
# Priority: env var > streamlit secrets > docker service name > localhost
API_URL = os.getenv("API_URL")
if not API_URL:
    try:
        API_URL = st.secrets.get("API_URL", None)
    except Exception:
        API_URL = None

if not API_URL:
    # Check if running in Docker by looking for docker environment
    if os.path.exists("/.dockerenv") or os.getenv("DOCKER_HOST"):
        API_URL = "http://backend:8000"
    else:
        API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Contract Risk Analyzer", layout="wide", initial_sidebar_state="expanded")

if "token" not in st.session_state:
    st.session_state.token = None
    st.session_state.user = None


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


# Enhanced CSS with circular patterns
LOGIN_CSS = """
<style>
    * {box-sizing: border-box;}
    html, body {margin: 0; padding: 0;}
    
    #MainMenu, header, footer {visibility: hidden;}
    .block-container {padding: 0 !important; max-width: 100% !important;}
    
    .stApp {
        background-color: #061109;
        background-image: 
            /* Large floating circles */
            radial-gradient(circle 300px at 10% 20%, rgba(52, 211, 153, 0.15) 0%, transparent 50%),
            radial-gradient(circle 250px at 90% 80%, rgba(34, 197, 94, 0.12) 0%, transparent 50%),
            radial-gradient(circle 200px at 50% 50%, rgba(52, 211, 153, 0.08) 0%, transparent 50%),
            /* Circular dot pattern */
            radial-gradient(circle 3px at 5% 10%, rgba(52, 211, 153, 0.3) 0%, transparent 3px),
            radial-gradient(circle 3px at 15% 25%, rgba(52, 211, 153, 0.2) 0%, transparent 3px),
            radial-gradient(circle 3px at 25% 15%, rgba(52, 211, 153, 0.25) 0%, transparent 3px),
            radial-gradient(circle 3px at 35% 40%, rgba(34, 197, 94, 0.2) 0%, transparent 3px),
            radial-gradient(circle 3px at 45% 30%, rgba(52, 211, 153, 0.2) 0%, transparent 3px),
            radial-gradient(circle 3px at 55% 45%, rgba(52, 211, 153, 0.25) 0%, transparent 3px),
            radial-gradient(circle 3px at 65% 20%, rgba(34, 197, 94, 0.2) 0%, transparent 3px),
            radial-gradient(circle 3px at 75% 35%, rgba(52, 211, 153, 0.2) 0%, transparent 3px),
            radial-gradient(circle 3px at 85% 50%, rgba(52, 211, 153, 0.25) 0%, transparent 3px),
            radial-gradient(circle 3px at 95% 15%, rgba(34, 197, 94, 0.2) 0%, transparent 3px),
            radial-gradient(circle 3px at 10% 60%, rgba(52, 211, 153, 0.2) 0%, transparent 3px),
            radial-gradient(circle 3px at 30% 70%, rgba(52, 211, 153, 0.25) 0%, transparent 3px),
            radial-gradient(circle 3px at 50% 85%, rgba(34, 197, 94, 0.2) 0%, transparent 3px),
            radial-gradient(circle 3px at 70% 75%, rgba(52, 211, 153, 0.2) 0%, transparent 3px),
            radial-gradient(circle 3px at 90% 90%, rgba(52, 211, 153, 0.25) 0%, transparent 3px);
        background-size: 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%;
        background-position: 0 0, 0 0, 0 0, 0 0, 0 0, 0 0, 0 0, 0 0, 0 0, 0 0, 0 0, 0 0, 0 0, 0 0, 0 0, 0 0;
        background-attachment: fixed;
        margin: 0; 
        padding: 0;
    }

    /* Animations */
    @keyframes cardEntranceLeft {
        0% {
            opacity: 0;
            transform: translateX(-100px) rotate(-5deg);
        }
        100% {
            opacity: 1;
            transform: translateX(0) rotate(0deg);
        }
    }
    
    @keyframes cardEntranceRight {
        0% {
            opacity: 0;
            transform: translateX(100px) rotate(5deg);
        }
        100% {
            opacity: 1;
            transform: translateX(0) rotate(0deg);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(52, 211, 153, 0.2); }
        50% { box-shadow: 0 0 40px rgba(52, 211, 153, 0.4); }
    }

    @keyframes floatCircles {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }

    /* Main container layout */
    [data-testid="stHorizontalBlock"] {
        gap: 3rem !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 100vh;
        margin: 0 !important;
        padding: 4rem 2rem !important;
        flex-wrap: wrap;
    }
    
    [data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        display: flex !important;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    /* Decorative floating circles */
    .floating-circle-1 {
        position: fixed;
        width: 400px;
        height: 400px;
        border: 2px solid rgba(52, 211, 153, 0.15);
        border-radius: 50%;
        top: -100px;
        left: -100px;
        animation: floatCircles 8s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }

    .floating-circle-2 {
        position: fixed;
        width: 300px;
        height: 300px;
        border: 2px solid rgba(34, 197, 94, 0.12);
        border-radius: 50%;
        bottom: -80px;
        right: -80px;
        animation: floatCircles 10s ease-in-out infinite reverse;
        pointer-events: none;
        z-index: 0;
    }

    .floating-circle-3 {
        position: fixed;
        width: 250px;
        height: 250px;
        border: 2px solid rgba(52, 211, 153, 0.1);
        border-radius: 50%;
        top: 50%;
        right: 5%;
        animation: floatCircles 12s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }

    /* Left card - Credentials (High Visibility) */
    div[data-testid="column"]:has(> div .login-marker) {
        flex: 0 1 450px !important;
        max-width: 450px !important;
        animation: cardEntranceLeft 1s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        z-index: 10;
    }
    
    div[data-testid="column"]:has(> div .login-marker) [data-testid="stVerticalBlock"] {
        width: 100% !important;
        background: #0d1a13 !important;
        border: 3px solid #34d399 !important;
        border-radius: 28px;
        padding: 3rem 2.5rem !important;
        box-shadow: 0 0 30px rgba(52, 211, 153, 0.25), inset 0 0 20px rgba(52, 211, 153, 0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    div[data-testid="column"]:has(> div .login-marker) [data-testid="stVerticalBlock"]::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(52, 211, 153, 0.1) 0%, transparent 70%);
        pointer-events: none;
    }
    
    div[data-testid="column"]:has(> div .login-marker) [data-testid="stVerticalBlock"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 0 40px rgba(52, 211, 153, 0.35), inset 0 0 20px rgba(52, 211, 153, 0.08);
    }

    /* Right card - Welcome (High Visibility) */
    div[data-testid="column"]:has(> div .hero-marker) {
        flex: 0 1 450px !important;
        max-width: 450px !important;
        animation: cardEntranceRight 1s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        z-index: 10;
    }
    
    div[data-testid="column"]:has(> div .hero-marker) [data-testid="stVerticalBlock"] {
        width: 100% !important;
        background: #071309 !important;
        border: 3px solid rgba(52, 211, 153, 0.5) !important;
        border-radius: 28px;
        padding: 3.5rem 3rem !important;
        box-shadow: 0 0 30px rgba(52, 211, 153, 0.2), inset 0 0 20px rgba(52, 211, 153, 0.04);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    div[data-testid="column"]:has(> div .hero-marker) [data-testid="stVerticalBlock"]::before {
        content: '';
        position: absolute;
        top: -30%;
        left: -30%;
        width: 160%;
        height: 160%;
        background: radial-gradient(circle, rgba(52, 211, 153, 0.08) 0%, transparent 70%);
        pointer-events: none;
    }
    
    div[data-testid="column"]:has(> div .hero-marker) [data-testid="stVerticalBlock"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 0 40px rgba(52, 211, 153, 0.3), inset 0 0 20px rgba(52, 211, 153, 0.06);
    }

    /* Inner Elements Animations */
    .logo-row, .section-label, .ai-badge, .hero-title, .hero-sub, .waves, .fine-print {
        animation: fadeInUp 0.8s ease-out both;
    }
    
    .logo-row { animation-delay: 0.4s; }
    .section-label { animation-delay: 0.5s; }
    .hero-title { animation-delay: 0.6s; }
    .hero-sub { animation-delay: 0.7s; }
    .waves { animation-delay: 0.8s; }
    .fine-print { animation-delay: 0.9s; }

    /* Logo row with circular badge */
    .logo-row {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 2rem;
    }
    
    .logo-row .flag {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, rgba(52, 211, 153, 0.35), rgba(52, 211, 153, 0.08));
        border: 3px solid #34d399;
        box-shadow: 0 0 20px rgba(52, 211, 153, 0.3), inset 0 0 15px rgba(52, 211, 153, 0.1);
    }
    
    .logo-row .brand {
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }

    .section-label {
        color: #6ee7b7;
        letter-spacing: 3px;
        font-size: 0.8rem;
        font-weight: 800;
        margin-bottom: 2rem;
        text-transform: uppercase;
        border-left: 4px solid #34d399;
        padding-left: 10px;
    }

    .hero-title {
        color: #ffffff;
        font-size: clamp(1.8rem, 5vw, 2.6rem);
        font-weight: 900;
        line-height: 1.2;
        margin-bottom: 1.5rem;
    }
    
    .hero-title .accent {
        color: #34d399;
        text-shadow: 0 0 20px rgba(52, 211, 153, 0.4);
    }

    .hero-sub {
        color: #a7b5ad;
        font-size: 1.1rem;
        line-height: 1.8;
        margin-bottom: 2.5rem;
    }

    /* Customizing Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #061109 !important;
        border-radius: 14px;
        padding: 6px;
        border: 2px solid rgba(52, 211, 153, 0.3) !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 10px !important;
        color: #9ca3af;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: #34d399 !important;
        color: #04140b !important;
        box-shadow: 0 4px 12px rgba(52, 211, 153, 0.3);
    }

    /* Input fields styling */
    .stTextInput input {
        background: #061109 !important;
        color: #ffffff !important;
        border: 2px solid rgba(52, 211, 153, 0.3) !important;
        border-radius: 12px !important;
        height: 54px !important;
        font-size: 1.05rem !important;
    }
    
    .stTextInput input:focus {
        border-color: #34d399 !important;
        box-shadow: 0 0 0 4px rgba(52, 211, 153, 0.15) !important;
    }

    /* Button styling */
    .stButton button {
        background: #34d399 !important;
        color: #04140b !important;
        border-radius: 12px !important;
        height: 56px !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 4px 15px rgba(52, 211, 153, 0.2) !important;
    }
    
    .stButton button:hover {
        transform: scale(1.02);
        background: #22c55e !important;
        box-shadow: 0 8px 25px rgba(52, 211, 153, 0.4) !important;
    }

    /* Fine print */
    .fine-print {
        color: #6b7280;
        font-size: 0.85rem;
        margin-top: 2rem;
        text-align: center;
    }
    
    .fine-print a { color: #34d399; text-decoration: none; font-weight: 600; }

    /* Mobile adjustments */
    @media (max-width: 1024px) {
        [data-testid="stHorizontalBlock"] { padding: 2rem 1rem !important; }
        div[data-testid="column"]:has(> div .login-marker),
        div[data-testid="column"]:has(> div .hero-marker) {
            flex: 0 1 100% !important;
            max-width: 500px !important;
        }
        .floating-circle-1, .floating-circle-2, .floating-circle-3 {
            display: none;
        }
    }
</style>
"""

# Dashboard CSS with circular patterns and sidebar styling
DASHBOARD_CSS = """
<style>
    .stApp {
        background-color: #061109;
        background-image: 
            /* Large floating circles */
            radial-gradient(circle 300px at 10% 20%, rgba(52, 211, 153, 0.12) 0%, transparent 50%),
            radial-gradient(circle 250px at 90% 80%, rgba(34, 197, 94, 0.1) 0%, transparent 50%),
            radial-gradient(circle 200px at 50% 50%, rgba(52, 211, 153, 0.06) 0%, transparent 50%),
            /* Circular dot pattern */
            radial-gradient(circle 2px at 5% 10%, rgba(52, 211, 153, 0.25) 0%, transparent 2px),
            radial-gradient(circle 2px at 15% 25%, rgba(52, 211, 153, 0.15) 0%, transparent 2px),
            radial-gradient(circle 2px at 25% 15%, rgba(52, 211, 153, 0.2) 0%, transparent 2px),
            radial-gradient(circle 2px at 35% 40%, rgba(34, 197, 94, 0.15) 0%, transparent 2px),
            radial-gradient(circle 2px at 45% 30%, rgba(52, 211, 153, 0.15) 0%, transparent 2px),
            radial-gradient(circle 2px at 55% 45%, rgba(52, 211, 153, 0.2) 0%, transparent 2px),
            radial-gradient(circle 2px at 65% 20%, rgba(34, 197, 94, 0.15) 0%, transparent 2px),
            radial-gradient(circle 2px at 75% 35%, rgba(52, 211, 153, 0.15) 0%, transparent 2px),
            radial-gradient(circle 2px at 85% 50%, rgba(52, 211, 153, 0.2) 0%, transparent 2px),
            radial-gradient(circle 2px at 95% 15%, rgba(34, 197, 94, 0.15) 0%, transparent 2px),
            radial-gradient(circle 2px at 10% 60%, rgba(52, 211, 153, 0.15) 0%, transparent 2px),
            radial-gradient(circle 2px at 30% 70%, rgba(52, 211, 153, 0.2) 0%, transparent 2px),
            radial-gradient(circle 2px at 50% 85%, rgba(34, 197, 94, 0.15) 0%, transparent 2px),
            radial-gradient(circle 2px at 70% 75%, rgba(52, 211, 153, 0.15) 0%, transparent 2px),
            radial-gradient(circle 2px at 90% 90%, rgba(52, 211, 153, 0.2) 0%, transparent 2px);
        background-size: 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%, 100% 100%;
        background-attachment: fixed;
    }

    /* Circular stat cards */
    .stat-card-circular {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        background: linear-gradient(135deg, #0d1a13 0%, #061109 100%);
        border: 2px solid rgba(52, 211, 153, 0.25);
        border-radius: 20px;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .stat-card-circular::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(52, 211, 153, 0.08) 0%, transparent 70%);
        pointer-events: none;
    }

    .stat-card-circular:hover {
        border-color: rgba(52, 211, 153, 0.4);
        box-shadow: 0 8px 24px rgba(52, 211, 153, 0.15);
        transform: translateY(-4px);
    }

    .stat-circle {
        width: 90px;
        height: 90px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, rgba(52, 211, 153, 0.25), rgba(52, 211, 153, 0.03));
        border: 3px solid rgba(52, 211, 153, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
        font-size: 2.5rem;
        font-weight: 900;
        color: #34d399;
        box-shadow: 0 0 20px rgba(52, 211, 153, 0.15), inset 0 0 15px rgba(52, 211, 153, 0.05);
    }

    .stat-label {
        color: #a7b5ad;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Risk badge circular */
    .risk-badge-circle {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.2rem;
        border: 3px solid;
        box-shadow: 0 0 20px;
        margin: 0 auto;
    }

    .risk-badge-circle.high {
        background: radial-gradient(circle at 30% 30%, rgba(239, 68, 68, 0.25), rgba(239, 68, 68, 0.03));
        border-color: #ef4444;
        color: #fca5a5;
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.3);
    }

    .risk-badge-circle.medium {
        background: radial-gradient(circle at 30% 30%, rgba(245, 158, 11, 0.25), rgba(245, 158, 11, 0.03));
        border-color: #f59e0b;
        color: #fcd34d;
        box-shadow: 0 0 20px rgba(245, 158, 11, 0.3);
    }

    .risk-badge-circle.low {
        background: radial-gradient(circle at 30% 30%, rgba(34, 197, 94, 0.25), rgba(34, 197, 94, 0.03));
        border-color: #22c55e;
        color: #86efac;
        box-shadow: 0 0 20px rgba(34, 197, 94, 0.3);
    }

    /* Floating circles for dashboard */
    .floating-circle-dash-1 {
        position: fixed;
        width: 350px;
        height: 350px;
        border: 2px solid rgba(52, 211, 153, 0.12);
        border-radius: 50%;
        top: 10%;
        left: -100px;
        pointer-events: none;
        z-index: 0;
    }

    .floating-circle-dash-2 {
        position: fixed;
        width: 280px;
        height: 280px;
        border: 2px solid rgba(34, 197, 94, 0.1);
        border-radius: 50%;
        bottom: 5%;
        right: -80px;
        pointer-events: none;
        z-index: 0;
    }

    /* ===== SIDEBAR STYLING ===== */
    /* Animations for sidebar */
    @keyframes sidebarGlow {
        0%, 100% { box-shadow: 0 0 20px rgba(52, 211, 153, 0.15), inset 0 0 15px rgba(52, 211, 153, 0.05); }
        50% { box-shadow: 0 0 40px rgba(52, 211, 153, 0.25), inset 0 0 20px rgba(52, 211, 153, 0.08); }
    }

    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes navItemPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }

    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #0a1410 0%, #051008 100%) !important;
        background-image: 
            /* Gradient overlays */
            linear-gradient(180deg, rgba(52, 211, 153, 0.08) 0%, transparent 50%),
            /* Animated glow circles */
            radial-gradient(circle 250px at 20% 30%, rgba(52, 211, 153, 0.12) 0%, transparent 50%),
            radial-gradient(circle 180px at 80% 70%, rgba(34, 197, 94, 0.1) 0%, transparent 50%),
            /* Dot pattern */
            radial-gradient(circle 2px at 15% 15%, rgba(52, 211, 153, 0.2) 0%, transparent 2px),
            radial-gradient(circle 2px at 85% 25%, rgba(34, 197, 94, 0.15) 0%, transparent 2px),
            radial-gradient(circle 2px at 25% 75%, rgba(52, 211, 153, 0.15) 0%, transparent 2px),
            radial-gradient(circle 2px at 75% 85%, rgba(34, 197, 94, 0.12) 0%, transparent 2px),
            linear-gradient(135deg, #0a1410 0%, #051008 100%) !important;
        border-right: 3px solid rgba(52, 211, 153, 0.3) !important;
        box-shadow: inset -20px 0 40px rgba(52, 211, 153, 0.05);
        animation: slideInLeft 0.6s ease-out;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        background: transparent !important;
        padding-top: 0.5rem !important;
    }

    /* Sidebar title - User name with enhanced styling */
    [data-testid="stSidebar"] h1 {
        background: linear-gradient(135deg, rgba(52, 211, 153, 0.2) 0%, rgba(52, 211, 153, 0.08) 100%) !important;
        padding: 1.75rem !important;
        border-radius: 18px !important;
        border: 2px solid rgba(52, 211, 153, 0.4) !important;
        margin-bottom: 1.25rem !important;
        margin-top: 0.5rem !important;
        font-size: 1.6rem !important;
        font-weight: 900 !important;
        color: #ffffff !important;
        box-shadow: 0 8px 24px rgba(52, 211, 153, 0.15), inset 0 0 20px rgba(52, 211, 153, 0.08) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        position: relative;
        overflow: hidden;
        animation: slideInLeft 0.7s ease-out;
    }

    [data-testid="stSidebar"] h1::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(52, 211, 153, 0.1) 0%, transparent 70%);
        pointer-events: none;
    }

    [data-testid="stSidebar"] h1:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 32px rgba(52, 211, 153, 0.25), inset 0 0 20px rgba(52, 211, 153, 0.12) !important;
        border-color: rgba(52, 211, 153, 0.6) !important;
    }

    /* Sidebar caption - Role badge with enhanced styling */
    [data-testid="stSidebar"] .stCaption {
        background: linear-gradient(135deg, rgba(52, 211, 153, 0.15) 0%, rgba(52, 211, 153, 0.05) 100%) !important;
        padding: 0.85rem 1.25rem !important;
        border-radius: 14px !important;
        border: 2px solid rgba(52, 211, 153, 0.35) !important;
        color: #6ee7b7 !important;
        font-weight: 800 !important;
        margin-bottom: 1.75rem !important;
        display: inline-block !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        font-size: 0.8rem !important;
        box-shadow: 0 4px 12px rgba(52, 211, 153, 0.12), inset 0 0 10px rgba(52, 211, 153, 0.05) !important;
        transition: all 0.3s ease !important;
        animation: slideInLeft 0.8s ease-out;
    }

    [data-testid="stSidebar"] .stCaption:hover {
        background: linear-gradient(135deg, rgba(52, 211, 153, 0.2) 0%, rgba(52, 211, 153, 0.08) 100%) !important;
        box-shadow: 0 6px 16px rgba(52, 211, 153, 0.18), inset 0 0 12px rgba(52, 211, 153, 0.08) !important;
        border-color: rgba(52, 211, 153, 0.5) !important;
    }

    /* Logout button styling - Enhanced with gradient and animations */
    [data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #34d399 0%, #22c55e 100%) !important;
        color: #04140b !important;
        border: 2px solid #34d399 !important;
        border-radius: 14px !important;
        height: 52px !important;
        font-weight: 800 !important;
        font-size: 1.05rem !important;
        width: 100% !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 0 6px 20px rgba(52, 211, 153, 0.25), inset 0 0 10px rgba(255, 255, 255, 0.1) !important;
        margin-bottom: 2.5rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.2px !important;
        position: relative;
        overflow: hidden;
        animation: slideInLeft 0.9s ease-out;
    }

    [data-testid="stSidebar"] .stButton button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s ease;
    }

    [data-testid="stSidebar"] .stButton button:hover::before {
        left: 100%;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        transform: translateY(-4px) scale(1.02) !important;
        box-shadow: 0 12px 32px rgba(52, 211, 153, 0.4), inset 0 0 15px rgba(255, 255, 255, 0.15) !important;
        background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
        border-color: #16a34a !important;
    }

    [data-testid="stSidebar"] .stButton button:active {
        transform: translateY(-2px) scale(0.98) !important;
    }

    /* Navigation label - Enhanced styling */
    [data-testid="stSidebar"] label {
        color: #a7b5ad !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
        margin-bottom: 1.25rem !important;
        margin-top: 0.5rem !important;
        display: block !important;
        border-left: 4px solid rgba(52, 211, 153, 0.4) !important;
        padding-left: 12px !important;
        animation: slideInLeft 1s ease-out;
    }

    /* Radio button container */
    [data-testid="stSidebar"] [role="radiogroup"] {
        background: transparent !important;
        gap: 0.5rem !important;
    }

    /* Individual radio option styling - Enhanced with animations */
    [data-testid="stSidebar"] .stRadio > label {
        background: linear-gradient(135deg, rgba(52, 211, 153, 0.08) 0%, rgba(52, 211, 153, 0.03) 100%) !important;
        padding: 0.9rem 1.2rem !important;
        border-radius: 14px !important;
        border: 2px solid rgba(52, 211, 153, 0.2) !important;
        margin-bottom: 0.85rem !important;
        transition: all 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        color: #a7b5ad !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        position: relative;
        overflow: hidden;
        animation: slideInLeft calc(1s + 0.1s) ease-out;
    }

    [data-testid="stSidebar"] .stRadio > label::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(52, 211, 153, 0.1) 0%, transparent 70%);
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    [data-testid="stSidebar"] .stRadio > label:hover {
        background: linear-gradient(135deg, rgba(52, 211, 153, 0.15) 0%, rgba(52, 211, 153, 0.08) 100%) !important;
        border-color: rgba(52, 211, 153, 0.45) !important;
        box-shadow: 0 6px 16px rgba(52, 211, 153, 0.12) !important;
        transform: translateX(4px) !important;
        color: #34d399 !important;
    }

    [data-testid="stSidebar"] .stRadio > label:hover::before {
        opacity: 1;
    }

    /* Selected radio option - Active page with enhanced styling */
    [data-testid="stSidebar"] .stRadio > label[data-selected="true"] {
        background: linear-gradient(135deg, rgba(52, 211, 153, 0.3) 0%, rgba(52, 211, 153, 0.12) 100%) !important;
        border: 2px solid #34d399 !important;
        color: #34d399 !important;
        box-shadow: 0 8px 24px rgba(52, 211, 153, 0.25), inset 0 0 15px rgba(52, 211, 153, 0.1) !important;
        font-weight: 900 !important;
        transform: translateX(6px) !important;
        animation: navItemPulse 2s ease-in-out infinite;
    }

    [data-testid="stSidebar"] .stRadio > label[data-selected="true"]::before {
        opacity: 1;
    }

    /* Divider styling - Enhanced */
    [data-testid="stSidebar"] hr {
        border: none !important;
        height: 2px !important;
        background: linear-gradient(90deg, transparent, rgba(52, 211, 153, 0.3), transparent) !important;
        margin: 1.75rem 0 !important;
        box-shadow: 0 2px 8px rgba(52, 211, 153, 0.1) !important;
    }
</style>
"""


def login_view():
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)
    
    # Add floating circles
    st.markdown(
        """
        <div class="floating-circle-1"></div>
        <div class="floating-circle-2"></div>
        <div class="floating-circle-3"></div>
        """,
        unsafe_allow_html=True,
    )

    # Use columns to center the cards and give them a layout
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown(
            """
            <div class="login-marker"></div>
            <div class="logo-row">
                <span class="flag">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M6 3h12a1 1 0 0 1 1 1v17l-7-4-7 4V4a1 1 0 0 1 1-1z" fill="#34d399"/>
                    </svg>
                </span>
                <span class="brand">Contract Analyzer</span>
            </div>
            <div class="section-label">Account Access</div>
            """,
            unsafe_allow_html=True,
        )

        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            email = st.text_input("Email", key="login_email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", key="login_pw",
                                      placeholder="••••••••")
            if st.button("Login Now", key="login_btn"):
                r = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
                if r.status_code == 200:
                    try:
                        st.session_state.token = r.json()["access_token"]
                        me_r = requests.get(f"{API_URL}/auth/me", headers=auth_headers())
                        if me_r.status_code == 200:
                            st.session_state.user = me_r.json()
                            st.rerun()
                        else:
                            st.error("Failed to retrieve user profile after login.")
                    except Exception:
                        st.error("Login succeeded but returned invalid data format.")
                else:
                    try:
                        err_detail = r.json().get("detail", "Login failed")
                    except Exception:
                        err_detail = f"Server Error (Status: {r.status_code})"
                    st.error(err_detail)

        with tab2:
            name = st.text_input("Full Name", placeholder="John Doe")
            email_r = st.text_input("Email", key="reg_email", placeholder="your@email.com")
            pw_r = st.text_input("Password", type="password", key="reg_pw",
                                  placeholder="Create a password")
            if st.button("Create Account", key="register_btn"):
                r = requests.post(f"{API_URL}/auth/register",
                                   json={"full_name": name, "email": email_r, "password": pw_r})
                if r.status_code == 201:
                    st.success("Registered! Please log in.")
                else:
                    try:
                        err_detail = r.json().get("detail", "Registration failed")
                    except Exception:
                        err_detail = f"Server Error (Status: {r.status_code})"
                    st.error(err_detail)

        st.markdown(
            """
            <div class="fine-print">
                Secure access to your legal insights. <br>
                By continuing you agree to our <a href="#">Terms</a>.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="hero-marker"></div>
            <div class="hero-title">
                Analyze Contracts with <span class="accent">AI Precision</span>
            </div>
            <div class="hero-sub">
                Upload any agreement and we'll automatically flag termination windows, 
                auto-renewals, and liability exposure in seconds.
            </div>
            <svg class="waves" width="100%" height="80" viewBox="0 0 420 80" preserveAspectRatio="xMidYMid meet" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M0 60 Q60 20 140 60 T280 60 T420 60" stroke="#34d399" stroke-width="2" opacity="0.8"/>
                <path d="M0 72 Q60 32 140 72 T280 72 T420 72" stroke="#34d399" stroke-width="1.5" opacity="0.4"/>
            </svg>
            """,
            unsafe_allow_html=True,
        )


def main_app():
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
    
    st.sidebar.title(f"👋 {st.session_state.user['full_name']}")
    st.sidebar.caption(f"🎯 Role: {st.session_state.user['role'].upper()}")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.token = None
        st.session_state.user = None
        st.rerun()

    st.sidebar.divider()
    
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
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="floating-circle-dash-1"></div>
        <div class="floating-circle-dash-2"></div>
        """,
        unsafe_allow_html=True,
    )
    
    st.header("📊 AI Insights Dashboard")
    
    r = requests.get(f"{API_URL}/dashboard", headers=auth_headers())
    if r.status_code != 200:
        st.error("Failed to load dashboard")
        return
    
    stats = r.json()
    
    # Create circular stat displays
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stat-card-circular">', unsafe_allow_html=True)
        st.markdown('<div class="stat-circle">📄</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #34d399; font-size: 2rem; font-weight: 900; margin: 0.5rem 0;">{stats.get("total_documents", 0)}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Total Documents</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        high_risk = stats.get("high_risk_documents", 0)
        st.markdown('<div class="stat-card-circular">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-circle" style="color: #ef4444;">{high_risk}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #ef4444; font-size: 1.8rem; font-weight: 900; margin: 0.5rem 0;">{high_risk}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">High Risk</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        avg_risk = stats.get("average_risk_score", 0)
        st.markdown('<div class="stat-card-circular">', unsafe_allow_html=True)
        st.markdown(f'<div class="stat-circle" style="color: #f59e0b;">⚡</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #f59e0b; font-size: 1.8rem; font-weight: 900; margin: 0.5rem 0;">{avg_risk:.1f}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Avg Risk Score</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="stat-card-circular">', unsafe_allow_html=True)
        st.markdown('<div class="stat-circle">🎯</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="color: #34d399; font-size: 2rem; font-weight: 900; margin: 0.5rem 0;">{len(stats.get("frequently_detected_risks", []))}</div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">Risk Types</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    
    # Risk distribution with circular badges
    st.subheader("🎯 Frequently Detected Risks")
    frequent = stats.get("frequently_detected_risks", [])
    
    if frequent:
        risk_cols = st.columns(min(5, len(frequent)))
        for idx, risk in enumerate(frequent[:5]):
            with risk_cols[idx]:
                st.markdown(
                    f"""
                    <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #0d1a13 0%, #061109 100%); 
                    border: 2px solid rgba(52, 211, 153, 0.25); border-radius: 16px;">
                        <div class="risk-badge-circle low">
                            {risk['count']}
                        </div>
                        <div style="color: #a7b5ad; font-size: 0.85rem; font-weight: 600; word-wrap: break-word; margin-top: 0.75rem;">{risk['title'][:20]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("No risks detected yet.")

    st.divider()
    st.subheader("📋 Recent Analyses")
    recent = stats.get("recent_documents", [])
    if recent:
        for doc in recent:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 **{doc['filename']}**")
                st.caption(doc.get("summary", "No summary available")[:100] + "...")
            with col2:
                risk_level = doc['risk_level'].lower()
                if risk_level == "high":
                    st.markdown('<div class="risk-badge-circle high">H</div>', unsafe_allow_html=True)
                elif risk_level == "medium":
                    st.markdown('<div class="risk-badge-circle medium">M</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="risk-badge-circle low">L</div>', unsafe_allow_html=True)
    else:
        st.info("No documents analyzed yet.")


def show_upload():
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
    st.header("📤 Upload & Analyze Document")
    uploaded_file = st.file_uploader("Choose a document", type=["pdf", "docx", "txt"])
    if uploaded_file:
        with st.spinner("Uploading and analyzing document..."):
            # Step 1: Upload
            files = {"file": uploaded_file}
            r = requests.post(f"{API_URL}/documents/upload", headers=auth_headers(), files=files)
            if r.status_code == 201:
                doc = r.json()
                doc_id = doc["id"]
                
                # Step 2: Analyze
                r_analyze = requests.post(f"{API_URL}/documents/{doc_id}/analyze", headers=auth_headers())
                if r_analyze.status_code == 200:
                    try:
                        result = r_analyze.json()
                        st.success("Document analyzed successfully!")
                        st.json(result)
                    except Exception:
                        st.error("Analysis succeeded but returned invalid data format.")
                else:
                    try:
                        err_detail = r_analyze.json().get('detail', 'Unknown error')
                    except Exception:
                        err_detail = f"Server Error (Status: {r_analyze.status_code})"
                    st.error(f"Analysis failed: {err_detail}")
            else:
                try:
                    err_detail = r.json().get('detail', 'Unknown error')
                except Exception:
                    err_detail = f"Server Error (Status: {r.status_code})"
                st.error(f"Upload failed: {err_detail}")


def show_documents():
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
    st.header("📚 My Documents")
    r = requests.get(f"{API_URL}/documents", headers=auth_headers())
    if r.status_code == 200:
        docs = r.json()
        if docs:
            for doc in docs:
                with st.expander(f"📄 {doc['filename']} - {doc['risk_level']}"):
                    st.write(f"Uploaded: {doc.get('uploaded_at', 'N/A')}")
                    st.write(f"Summary: {doc.get('summary', 'N/A')}")
        else:
            st.info("No documents found.")
    else:
        st.error("Failed to load documents")


def show_search():
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)
    st.header("🔍 Search Documents")
    query = st.text_input("Enter search query")
    if query:
        with st.spinner("Searching..."):
            r = requests.get(f"{API_URL}/search", headers=auth_headers(), params={"query": query})
            if r.status_code == 200:
                results = r.json()
                st.write(f"Found {len(results)} results")
                for result in results:
                    st.write(result)
            else:
                st.error("Search failed")


if __name__ == "__main__":
    if st.session_state.token:
        main_app()
    else:
        login_view()
