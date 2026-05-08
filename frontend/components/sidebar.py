import streamlit as st
from services.api_service import APIService
from state.session import start_new_chat

def render_sidebar():
    """Render the collapsible sidebar with navigation and settings."""
    api = APIService()
    
    with st.sidebar:
        st.title("🚀 RAG Assistant")
        st.markdown("---")
        
        # New Chat Button
        if st.button("➕ New Conversation", use_container_width=True):
            start_new_chat()
            st.rerun()
            
        st.markdown("### 💬 Conversations")
        # Placeholder for history list
        if not st.session_state.chat_history:
            st.info("No recent chats")
        else:
            for chat in st.session_state.chat_history:
                if st.button(f"📄 {chat['title'][:20]}...", key=chat['id'], use_container_width=True):
                    # Logic to switch chat
                    pass

        st.markdown("---")
        st.markdown("### 🛠 Settings")
        
        # Document Filter
        st.session_state.settings["doc_filter"] = st.selectbox(
            "Knowledge Base",
            options=["all", "mysql", "python"],
            index=["all", "mysql", "python"].index(st.session_state.settings["doc_filter"])
        )
        
        # Model Selection
        health = api.check_health()
        available_models = health.get("available_models", ["llama3.2"])
        st.session_state.settings["model"] = st.selectbox(
            "Active Model",
            options=available_models,
            index=0 if st.session_state.settings["model"] not in available_models else available_models.index(st.session_state.settings["model"])
        )

        st.markdown("---")
        st.markdown("### 📂 Upload Documents")
        uploaded_file = st.file_uploader("Upload PDF", type="pdf")
        if uploaded_file:
            if st.button("Index Document", use_container_width=True):
                with st.spinner("Processing..."):
                    res = api.upload_pdf(uploaded_file.getvalue(), uploaded_file.name, st.session_state.settings["doc_filter"])
                    if res.get("success"):
                        st.success("Indexed!")
                        st.cache_data.clear() # Clear document list cache
                    else:
                        st.error(res.get("error", "Upload failed"))

        st.markdown("---")
        # Status Bar in Sidebar
        render_status_bar(health)

def render_status_bar(health):
    """Render system status indicators."""
    st.markdown("#### System Status")
    
    status = health.get("status", "offline")
    color = "#00ff88" if status == "healthy" else "#ff4b4b"
    
    st.markdown(f"""
    <div style='display: flex; align-items: center; gap: 10px; font-size: 0.8rem;'>
        <div style='width: 8px; height: 8px; border-radius: 50%; background-color: {color}; box-shadow: 0 0 5px {color};'></div>
        <span>Backend: {status.capitalize()}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Ready Check
    ready = APIService().check_ready()
    ready_color = "#00ff88" if ready.get("ready") else "#ff9900"
    ready_text = "Ready" if ready.get("ready") else "Initializing"
    
    st.markdown(f"""
    <div style='display: flex; align-items: center; gap: 10px; font-size: 0.8rem; margin-top: 5px;'>
        <div style='width: 8px; height: 8px; border-radius: 50%; background-color: {ready_color}; box-shadow: 0 0 5px {ready_color};'></div>
        <span>RAG Pipeline: {ready_text}</span>
    </div>
    """, unsafe_allow_html=True)
