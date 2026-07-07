import streamlit as st
import os
from summarizer import read_file, generate_txt_bytes, generate_pdf_bytes, generate_combined_txt_bytes, generate_pdf_bytes_multi
from ai_analyzer import AIAnalyzer
from database import SessionLocal, User, Document, get_db
from sqlalchemy.orm import Session
from typing import List, Dict, Any

# Set up environment variable for Google API Key
# In a real deployment, this would be managed securely (e.g., Streamlit Secrets, environment variables)
# For local testing, you can set it in your environment or directly here for development purposes.
# os.environ["GOOGLE_API_KEY"] = "YOUR_GOOGLE_API_KEY"

st.set_page_config(
    page_title="AI-Powered Contract & Legal Document Risk Analyzer",
    page_icon="⚖️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url(\'https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap\');
    
    :root {
        --bg-color: #E0E5EC;
        --text-color: #4A4A4A;
        --text-light: #718096;
        --shadow-light: #FFFFFF;
        --shadow-dark: #A3B1C6;
        --pastel-blue: #E3F2FD;
        --pastel-purple: #F3E5F5;
    }

    html, body, [class*="css"] {
        font-family: \'Poppins\', sans-serif;
        color: var(--text-color);
        background-color: var(--bg-color);
    }

    /* Neumorphic Container */
    .neu-container {
        background-color: var(--bg-color);
        border-radius: 50px;
        box-shadow: 20px 20px 60px var(--shadow-dark), 
                   -20px -20px 60px var(--shadow-light);
        padding: 3rem;
        margin-bottom: 3rem;
    }

    /* Neumorphic Inset */
    .neu-inset {
        background-color: var(--bg-color);
        border-radius: 30px;
        box-shadow: inset 8px 8px 16px var(--shadow-dark), 
                    inset -8px -8px 16px var(--shadow-light);
        padding: 2rem;
        margin-bottom: 1.5rem;
    }

    /* Neumorphic Button */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        padding: 1rem 2rem;
        background-color: var(--bg-color);
        color: var(--text-color);
        font-weight: 600;
        border: none;
        box-shadow: 6px 6px 12px var(--shadow-dark), 
                    -6px -6px 12px var(--shadow-light);
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        box-shadow: 2px 2px 5px var(--shadow-dark), 
                    -2px -2px 5px var(--shadow-light);
        transform: translateY(1px);
        color: #2D3748;
    }

    .stButton>button:active {
        box-shadow: inset 4px 4px 8px var(--shadow-dark), 
                    inset -4px -4px 8px var(--shadow-light);
    }

    /* Header Styling */
    .header-section {
        text-align: center;
        padding: 4rem 1rem;
    }

    .header-section h1 {
        font-weight: 800;
        font-size: 4.5rem;
        color: var(--text-color);
        letter-spacing: -2px;
        margin-bottom: 0.5rem;
    }

    .tagline {
        font-weight: 400;
        font-size: 1.1rem;
        color: var(--text-light);
        letter-spacing: 1px;
    }

    /* Sidebar Branding */
    [data-testid="stSidebar"] {
        background-color: var(--bg-color) !important;
        border-right: none;
    }

    .sidebar-logo {
        font-weight: 800;
        font-size: 1.8rem;
        color: var(--text-color);
        margin-bottom: 2rem;
    }

    /* Neumorphic Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: var(--bg-color);
        border-radius: 15px;
        padding: 10px 25px;
        color: var(--text-light);
        font-weight: 500;
        box-shadow: 4px 4px 8px var(--shadow-dark), 
                    -4px -4px 8px var(--shadow-light);
        border: none;
        margin-bottom: 10px;
    }

    .stTabs [aria-selected="true"] {
        box-shadow: inset 4px 4px 8px var(--shadow-dark), 
                    inset -4px -4px 8px var(--shadow-light) !important;
        color: var(--text-color) !important;
    }

    /* Result Panels */
    .neu-panel {
        border-radius: 25px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        line-height: 1.7;
    }

    .panel-blue { background-color: var(--pastel-blue); box-shadow: inset 4px 4px 8px #C1D5E3, inset -4px -4px 8px #FFFFFF; }
    .panel-purple { background-color: var(--pastel-purple); box-shadow: inset 4px 4px 8px #D6C9D9, inset -4px -4px 8px #FFFFFF; }

    /* Neumorphic Metrics */
    .metric-card {
        background-color: var(--bg-color);
        padding: 2rem;
        border-radius: 30px;
        text-align: center;
        box-shadow: 10px 10px 20px var(--shadow-dark), 
                    -10px -10px 20px var(--shadow-light);
    }

    .metric-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--text-light);
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--text-color);
    }

</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_ai_analyzer():
    return AIAnalyzer()

ai_analyzer = get_ai_analyzer()

# --- User Authentication (Placeholder for now) ---
def authenticate_user(username, password):
    db: Session = next(get_db())
    user = db.query(User).filter(User.username == username).first()
    if user and user.password_hash == password: # In real app, use hashed passwords
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["user_id"] = user.id
        st.session_state["user_role"] = user.role
        return True
    return False

def register_user(username, password):
    db: Session = next(get_db())
    if db.query(User).filter(User.username == username).first():
        return False # User already exists
    new_user = User(username=username, password_hash=password) # Hash password in real app
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return True

def logout_user():
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["user_id"] = None
    st.session_state["user_role"] = None

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("<div class=\"sidebar-logo\">Contract Analyzer AI</div>", unsafe_allow_html=True)
    
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        st.subheader("Login / Register")
        login_tab, register_tab = st.tabs(["Login", "Register"])
        with login_tab:
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", key="login_button"):
                if authenticate_user(username, password):
                    st.success("Logged in successfully!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password")
        with register_tab:
            new_username = st.text_input("New Username", key="register_username")
            new_password = st.text_input("New Password", type="password", key="register_password")
            if st.button("Register", key="register_button"):
                if register_user(new_username, new_password):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Username already exists")
    else:
        st.write(f"Welcome, {st.session_state['username']} ({st.session_state['user_role']})")
        choice = st.selectbox("WORKSPACE", ["Document Analysis", "Semantic Search", "Dashboard", "Admin Panel"])
        if st.button("Logout"):
            logout_user()
            st.experimental_rerun()

# --- Main Content ---
if st.session_state["logged_in"]:
    if choice == "Document Analysis":
        st.markdown("<div class=\"header-section\"><h1>AI-Powered Contract Analysis</h1><p class=\"tagline\">Upload and analyze your legal documents for risks and insights.</p></div>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload Document", type=["txt", "pdf", "docx"])
        if uploaded_file:
            temp_file_path = os.path.join("temp_docs", uploaded_file.name)
            os.makedirs("temp_docs", exist_ok=True)
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                document_content = read_file(temp_file_path)
                st.success("Document uploaded and read successfully!")
                
                if st.button("Analyze Document"):
                    with st.spinner("Analyzing document for clauses and risks..."):
                        analysis_result = ai_analyzer.analyze_document(document_content)
                        summary_result = ai_analyzer.summarize_document(document_content)
                        
                        # Placeholder for saving to DB and displaying results
                        db: Session = next(get_db())
                        new_doc = Document(
                            user_id=st.session_state["user_id"],
                            filename=uploaded_file.name,
                            content=document_content,
                            executive_summary=summary_result # This needs parsing from summary_result
                            # Populate other fields from analysis_result and summary_result
                        )
                        db.add(new_doc)
                        db.commit()
                        st.session_state["last_analysis"] = {"analysis": analysis_result, "summary": summary_result, "content": document_content}
                        st.success("Analysis complete!")
                        
                        st.subheader("Analysis Results")
                        st.markdown(f'<div class="neu-panel panel-blue">{analysis_result}</div>', unsafe_allow_html=True)
                        
                        st.subheader("Executive Summary")
                        st.markdown(f'<div class="neu-panel panel-purple">{summary_result}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error processing document: {e}")
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

    elif choice == "Semantic Search":
        st.markdown("<div class=\"header-section\"><h1>Semantic Search</h1><p class=\"tagline\">Search your uploaded documents using natural language queries.</p></div>", unsafe_allow_html=True)
        
        user_query = st.text_input("Enter your search query:")
        if user_query and st.button("Search Documents"):
            db: Session = next(get_db())
            user_docs = db.query(Document).filter(Document.user_id == st.session_state["user_id"]).all()
            
            if not user_docs:
                st.info("No documents uploaded yet. Please upload documents in the 'Document Analysis' section.")
            else:
                st.subheader("Search Results")
                for doc in user_docs:
                    search_results = ai_analyzer.semantic_search(doc.content, user_query)
                    if search_results:
                        st.markdown(f"**Document: {doc.filename}**")
                        st.markdown(f'<div class="neu-panel panel-blue">{search_results}</div>', unsafe_allow_html=True)
                    else:
                        st.info(f"No relevant information found in {doc.filename} for your query.")

    elif choice == "Dashboard":
        st.markdown("<div class=\"header-section\"><h1>Dashboard</h1><p class=\"tagline\">Overview of your document analysis and risks.</p></div>", unsafe_allow_html=True)
        db: Session = next(get_db())
        user_docs = db.query(Document).filter(Document.user_id == st.session_state["user_id"]).all()

        total_docs = len(user_docs)
        avg_risk_score = sum([doc.risk_score for doc in user_docs]) / total_docs if total_docs > 0 else 0
        high_risk_docs = [doc.filename for doc in user_docs if doc.risk_score > 0.7] # Example threshold

        st.markdown(f'<div class="metric-card"><p class="metric-label">Total Documents</p><p class="metric-value">{total_docs}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><p class="metric-label">Average Risk Score</p><p class="metric-value">{avg_risk_score:.2f}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><p class="metric-label">High Risk Documents</p><p class="metric-value">{len(high_risk_docs)}</p></div>', unsafe_allow_html=True)

        if high_risk_docs:
            st.subheader("High Risk Documents")
            for doc_name in high_risk_docs:
                st.write(f"- {doc_name}")

        st.subheader("Processing History")
        for doc in user_docs:
            with st.expander(f"Document: {doc.filename} (Uploaded: {doc.upload_date.strftime('%Y-%m-%d %H:%M')})"):
                st.json({
                    "Contract Type": doc.contract_type,
                    "Risk Score": doc.risk_score,
                    "Executive Summary": doc.executive_summary[:200] + "..." if doc.executive_summary else "N/A"
                })

    elif choice == "Admin Panel":
        if st.session_state["user_role"] == "admin":
            st.markdown("<div class=\"header-section\"><h1>Admin Panel</h1><p class=\"tagline\">Manage users and monitor system activity.</p></div>", unsafe_allow_html=True)
            
            db: Session = next(get_db())
            users = db.query(User).all()
            st.subheader("Manage Users")
            for user in users:
                st.write(f"User ID: {user.id}, Username: {user.username}, Role: {user.role}")
            
            st.subheader("Processing Statistics (Placeholder)")
            st.info("Detailed processing statistics and system logs would be displayed here.")

        else:
            st.error("You do not have administrative privileges to access this panel.")

else:
    st.markdown("<div class=\"header-section\"><h1>Welcome to the AI-Powered Contract & Legal Document Risk Analyzer</h1><p class=\"tagline\">Please login or register to continue.</p></div>", unsafe_allow_html=True)
