# Premium RAG Frontend 🚀

A state-of-the-art Streamlit interface for the RAG-SQL-Python-Assistant, designed for speed, security, and transparency.

## ✨ Features

- **Glassmorphism UI**: Modern "ChatGPT-like" aesthetic with custom CSS.
- **SSE Streaming**: Real-time token streaming with incremental buffering for smoothness.
- **RAG Transparency**: Detailed debugging panel showing retrieved/reranked chunks and LLM context.
- **Secure**: Sensitive keys stored in `.streamlit/secrets.toml`.
- **Robust**: Request isolation (`request_id`), stop generation logic, and mid-stream error recovery.
- **Analytics**: Real-time token speed (tok/s) and system status indicators.

## 🛠 Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Secrets**:
   Edit `frontend/.streamlit/secrets.toml` and add your `X-API-KEY`.

3. **Run the App**:
   ```bash
   streamlit run app.py
   ```

## 🏗 Architecture

- `app.py`: Main entry point and layout.
- `components/`: Modular UI components (Sidebar, Chat, Debug, Status).
- `services/`: API communication layer (SSE, Async).
- `state/`: Streamlit session state management and request isolation.
- `utils/`: Helpers for sanitization and stats.
- `styles/`: Custom CSS for premium aesthetics.

## 🔒 Security

- **XSS Protection**: All markdown is sanitized using `bleach`.
- **API Key**: Not exposed in client-side code; handled via Streamlit secrets.
- **Isolation**: Each generation request is isolated via `request_id`.
