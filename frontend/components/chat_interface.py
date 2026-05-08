import streamlit as st
import asyncio
import time
from services.api_service import APIService
from state.session import add_message, set_streaming, generate_request_id
from utils.helpers import sanitize_markdown, calculate_stats

def render_chat_interface():
    """Render the main chat window and handle user input."""
    api = APIService()
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(sanitize_markdown(msg["content"]), unsafe_allow_html=True)
            if msg.get("metadata", {}).get("sources"):
                render_sources(msg["metadata"]["sources"])

    # Chat Input
    if query := st.chat_input("Ask me anything about SQL or Python...", disabled=st.session_state.is_streaming):
        # Add user message
        add_message("user", query)
        with st.chat_message("user"):
            st.markdown(query)
            
        # Generation Logic
        handle_generation(query, api)

def handle_generation(query, api):
    """Handle the streaming response generation."""
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        stats_placeholder = st.empty()
        
        full_response = ""
        token_count = 0
        start_time = time.time()
        
        # Lock conversation and generate request ID
        set_streaming(True)
        req_id = generate_request_id()
        
        # Stop button logic
        if st.button("⏹ Stop Generation", key=f"stop_{req_id}"):
            st.session_state.stop_generation = True
            
        try:
            # We use an async loop inside streamlit (needs bridge)
            async def run_stream():
                nonlocal full_response, token_count
                async for chunk in api.stream_chat(
                    query, 
                    st.session_state.current_conversation_id, 
                    st.session_state.settings["doc_filter"],
                    request_id=req_id
                ):
                    if "error" in chunk:
                        st.error(chunk["error"])
                        break
                        
                    if chunk.get("control") == "stopped":
                        break
                        
                    if chunk.get("type") == "token_chunk":
                        full_response += chunk["content"]
                        token_count += len(chunk["content"].split()) # Rough estimate
                        
                        # Update UI with sanitized content
                        response_placeholder.markdown(sanitize_markdown(full_response) + "▌", unsafe_allow_html=True)
                        
                        # Update Stats
                        tps = calculate_stats(start_time, token_count)
                        stats_placeholder.caption(f"⚡ {tps} tok/s")
                    
                    if "answer" in full_response and "sources" in chunk:
                        # Final metadata update
                        pass

            # Bridge async to sync for Streamlit
            asyncio.run(run_stream())
            
            # Final render without cursor
            response_placeholder.markdown(sanitize_markdown(full_response), unsafe_allow_html=True)
            
            # Save to state
            add_message("assistant", full_response)
            
        finally:
            set_streaming(False)
            st.session_state.stop_generation = False
            st.rerun()

def render_sources(sources):
    """Render source citation cards."""
    with st.expander("📚 Sources & Citations"):
        cols = st.columns(2)
        for i, source in enumerate(sources):
            with cols[i % 2]:
                st.markdown(f"""
                <div class='source-card'>
                    <strong>{source['metadata'].get('source', 'Unknown')}</strong> (Page {source['metadata'].get('page', '?')})<br/>
                    <small>Relevance: {round(source.get('score', 0) * 100)}%</small>
                </div>
                """, unsafe_allow_html=True)
