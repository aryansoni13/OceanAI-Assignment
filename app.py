import streamlit as st
import os
import shutil
from dotenv import load_dotenv
from backend.ingestion import load_documents, create_vector_db, get_vector_store
from backend.rag_agent import generate_test_cases, generate_selenium_script
from backend.utils import save_uploaded_file, read_file_content
from backend.qa_validator import validate_project

# Load environment variables from .env file
load_dotenv()

st.set_page_config(
    page_title="Autonomous QA Agent", 
    layout="wide",
    page_icon="🤖",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        font-size: 3rem;
        margin: 0;
    }
    .main-header p {
        color: #f0f0f0;
        font-size: 1.2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        font-size: 1.1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="main-header">
        <h1>🤖 Autonomous QA Agent</h1>
        <p>Generate Test Cases and Selenium Scripts from your documentation</p>
    </div>
""", unsafe_allow_html=True)

# Load API key silently from .env
api_key = os.getenv("GOOGLE_API_KEY", "")

# Check if API key is available
if not api_key:
    st.error("⚠️ **API Key Not Found!** Please add `GOOGLE_API_KEY` to your `.env` file to use this application.")
    st.info("💡 **How to fix:** Create a `.env` file in the project root and add: `GOOGLE_API_KEY=your_api_key_here`")
    st.stop()

# Tabs
tab1, tab2, tab3 = st.tabs(["📚 Knowledge Base", "🧪 Test Cases", "📜 Selenium Scripts"])

# --- Tab 1: Knowledge Base ---
with tab1:
    st.header("Build Knowledge Base")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Upload Support Documents")
        uploaded_docs = st.file_uploader("Upload MD, TXT, JSON", accept_multiple_files=True, type=['md', 'txt', 'json'])
        
    with col2:
        st.subheader("Upload Target HTML")
        uploaded_html = st.file_uploader("Upload checkout.html", type=['html'])

    if st.button("Build Knowledge Base"):
        if not uploaded_docs or not uploaded_html:
            st.error("Please upload both support documents and the HTML file.")
        else:
            with st.spinner("Building Knowledge Base..."):
                # Save files
                base_path = os.path.join(os.getcwd(), "qa_agent", "temp_uploads")
                if os.path.exists(base_path):
                    shutil.rmtree(base_path)
                os.makedirs(base_path)
                
                doc_paths = []
                for doc in uploaded_docs:
                    path = save_uploaded_file(doc, base_path)
                    doc_paths.append(path)
                
                html_path = save_uploaded_file(uploaded_html, base_path)
                # We also treat HTML as a doc for context if needed, but primarily we need it for script gen
                # For now, let's add HTML to the vector store as well so the agent 'knows' the structure
                # But usually, raw HTML is too noisy. Let's just keep it for the script generation phase.
                # However, the prompt says "ingest... HTML structure". 
                # Let's add it to doc_paths for ingestion.
                doc_paths.append(html_path)
                
                # Ingest
                docs = load_documents(doc_paths)
                create_vector_db(docs, force_rebuild=True)
                
                st.success("Knowledge Base Built Successfully! 🚀")
                st.session_state['kb_built'] = True
                st.session_state['html_path'] = html_path
                
                # Run QA Validation and show suggestions
                st.markdown("---")
                st.subheader("🔍 Quick Fix Suggestions")
                
                with st.spinner("Analyzing HTML and documentation..."):
                    # Read HTML content
                    html_content = read_file_content(html_path)
                    
                    # Combine all documentation content
                    docs_text = ""
                    for doc_path in doc_paths[:-1]:  # Exclude HTML from docs
                        docs_text += read_file_content(doc_path) + "\n\n"
                    
                    # Run validation
                    suggestions = validate_project(html_content, docs_text)
                    st.markdown(suggestions)

# --- Tab 2: Test Cases ---
with tab2:
    st.header("Generate Test Cases")
    
    if not st.session_state.get('kb_built'):
        st.warning("Please build the Knowledge Base first.")
    else:
        topic = st.text_input("Enter Feature or Topic (e.g., 'Discount Code', 'Shipping Logic')")
        
        if st.button("Generate Test Cases"):
            if not api_key:
                st.error("API Key required.")
            elif not topic:
                st.error("Please enter a topic.")
            else:
                with st.spinner("Generating Test Cases..."):
                    vector_store = get_vector_store()
                    try:
                        result = generate_test_cases(vector_store, topic, api_key)
                        st.markdown(result)
                        st.session_state['last_test_cases'] = result
                    except Exception as e:
                        st.error(f"Error: {e}")

# --- Tab 3: Selenium Scripts ---
with tab3:
    st.header("Generate Selenium Script")
    
    if not st.session_state.get('kb_built'):
        st.warning("Please build the Knowledge Base first.")
    else:
        # Simple text area to paste a test case or select from previous generation (mock selection)
        st.markdown("### Selected Test Case")
        
        # If we have generated test cases, try to parse them or just let user copy-paste
        # For this assignment, a text area is flexible.
        test_case_input = st.text_area("Paste a Test Case here (or copy from the previous tab)", height=150)
        
        if st.button("Generate Script"):
            if not api_key:
                st.error("API Key required.")
            elif not test_case_input:
                st.error("Please provide a test case.")
            else:
                with st.spinner("Generating Selenium Script..."):
                    vector_store = get_vector_store()
                    html_content = read_file_content(st.session_state['html_path'])
                    try:
                        script = generate_selenium_script(vector_store, test_case_input, html_content, api_key)
                        st.code(script, language='python')
                    except Exception as e:
                        st.error(f"Error: {e}")
