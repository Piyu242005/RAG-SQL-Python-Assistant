import bleach
import time
import streamlit as st

def sanitize_markdown(content: str) -> str:
    """Sanitize markdown content to prevent XSS."""
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
        'code', 'pre', 'ul', 'ol', 'li', 'blockquote', 'a', 'img',
        'table', 'thead', 'tbody', 'tr', 'th', 'td', 'span'
    ]
    allowed_attrs = {
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title'],
        'code': ['class'],
        'span': ['class']
    }
    return bleach.clean(content, tags=allowed_tags, attributes=allowed_attrs)

def calculate_stats(start_time, token_count):
    """Calculate tokens per second."""
    duration = time.time() - start_time
    if duration <= 0:
        return 0
    return round(token_count / duration, 2)

def format_timestamp(iso_str: str) -> str:
    """Format ISO timestamp for display."""
    from datetime import datetime
    dt = datetime.fromisoformat(iso_str)
    return dt.strftime("%H:%M")

def inject_custom_css():
    """Inject the main CSS file into the Streamlit app."""
    with open("styles/main.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def render_svg(svg_path: str):
    """Helper to render SVG icons."""
    with open(svg_path, "r") as f:
        st.markdown(f, unsafe_allow_html=True)
