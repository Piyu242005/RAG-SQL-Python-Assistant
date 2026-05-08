import streamlit as st
from state.session import init_session_state
from components.sidebar import render_sidebar
from components.chat_interface import render_chat_interface
from components.debug_panel import render_debug_panel
from utils.helpers import inject_custom_css

# Page Configuration
st.set_page_config(
    page_title=st.secrets.get("ui", {}).get("APP_TITLE", "RAG AI Assistant"),
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
init_session_state()

# Inject Custom Styles
inject_custom_css()

# Layout
col_chat, col_debug = st.columns([0.7, 0.3])

with col_chat:
    # Main Header
    st.markdown(f"""
    <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 2rem;'>
        <h1>{st.secrets.get("ui", {}).get("APP_TITLE", "RAG AI Assistant")}</h1>
        <div style='display: flex; gap: 10px;'>
            <span style='background: rgba(0, 212, 255, 0.1); padding: 4px 12px; border-radius: 20px; color: #00d4ff; border: 1px solid rgba(0, 212, 255, 0.2); font-size: 0.8rem;'>
                {st.session_state.settings["model"]}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat Window
    render_chat_interface()

with col_debug:
    # Sidebar
    render_sidebar()
    
    # Debug Panel
    render_debug_panel()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.8rem;'>"
    "Powered by Ollama + ChromaDB + Streamlit | Built with ❤️ by Piyu"
    "</div>", 
    unsafe_allow_html=True
)

# Fragment for background status updates
@st.fragment
def background_sync():
    # This could check for new messages or system status without full rerun
    pass

background_sync()
