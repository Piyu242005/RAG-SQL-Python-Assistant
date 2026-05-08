import streamlit as st
import uuid
import time
from datetime import datetime

def init_session_state():
    """Initialize all session state variables with defaults."""
    
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    if "chat_history" not in st.session_state:
        # List of past conversations metadata
        st.session_state.chat_history = []
        
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = str(uuid.uuid4())
        
    if "is_streaming" not in st.session_state:
        st.session_state.is_streaming = False
        
    if "stop_generation" not in st.session_state:
        st.session_state.stop_generation = False
        
    if "request_id" not in st.session_state:
        st.session_state.request_id = None
        
    if "settings" not in st.session_state:
        st.session_state.settings = {
            "theme": "dark",
            "model": "llama3.2",
            "doc_filter": "all",
            "chunk_size": 600,
            "max_context": 3000
        }
        
    if "retrieval_debug" not in st.session_state:
        st.session_state.retrieval_debug = {
            "last_retrieved": [],
            "last_reranked": [],
            "last_context": "",
            "latency": 0.0,
            "timeline": []
        }

def start_new_chat():
    """Reset current chat session but keep history metadata."""
    st.session_state.messages = []
    st.session_state.current_conversation_id = str(uuid.uuid4())
    st.session_state.request_id = None
    st.session_state.stop_generation = False
    st.session_state.is_streaming = False

def add_message(role, content, metadata=None):
    """Add a message to the current session."""
    message = {
        "id": str(uuid.uuid4()),
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    st.session_state.messages.append(message)
    return message

def set_streaming(status):
    """Lock or unlock conversation during streaming."""
    st.session_state.is_streaming = status

def generate_request_id():
    """Generate a unique ID for the current generation request."""
    st.session_state.request_id = str(uuid.uuid4())
    return st.session_state.request_id

def validate_request_id(req_id):
    """Check if the provided request ID matches the current active one."""
    return st.session_state.request_id == req_id
