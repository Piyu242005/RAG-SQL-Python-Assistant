import streamlit as st

def render_debug_panel():
    """Render the RAG debugging panel (Retrieved, Reranked, Context)."""
    
    if not st.session_state.retrieval_debug.get("last_retrieved"):
        return

    with st.expander("🔍 Retrieval Debugging Panel"):
        tab1, tab2, tab3 = st.tabs(["Retrieved Chunks", "Reranked Chunks", "LLM Context"])
        
        with tab1:
            for i, doc in enumerate(st.session_state.retrieval_debug["last_retrieved"]):
                st.markdown(f"**Chunk {i+1}** (Score: {doc.get('score', 'N/A')})")
                st.code(doc.get("page_content", "")[:300] + "...", language="text")
                st.markdown("---")
                
        with tab2:
            if not st.session_state.retrieval_debug["last_reranked"]:
                st.info("No reranking applied")
            else:
                for i, doc in enumerate(st.session_state.retrieval_debug["last_reranked"]):
                    st.markdown(f"**Reranked Chunk {i+1}**")
                    st.code(doc.get("page_content", "")[:300] + "...", language="text")
                    st.markdown("---")
                    
        with tab3:
            st.markdown("#### Final Context Sent to LLM")
            st.text_area("Context", value=st.session_state.retrieval_debug["last_context"], height=300, disabled=True)
            
        # Timeline Visualization
        st.markdown("#### Pipeline Timeline")
        timeline = st.session_state.retrieval_debug.get("timeline", [])
        if timeline:
            st.markdown(" → ".join([f"`{step}`" for step in timeline]))
