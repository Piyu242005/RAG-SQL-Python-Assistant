import httpx
import json
import time
import streamlit as st
from typing import Generator, Optional

class APIService:
    def __init__(self):
        self.base_url = st.secrets.get("api", {}).get("BACKEND_URL", "http://localhost:8000")
        self.api_key = st.secrets.get("api", {}).get("X_API_KEY", "")
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    @st.cache_data(ttl=15)
    def check_health(_self):
        """Check if backend is healthy."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{_self.base_url}/api/health", headers=_self.headers)
                return response.json() if response.status_code == 200 else {"status": "error"}
        except Exception as e:
            return {"status": "offline", "error": str(e)}

    @st.cache_data(ttl=15)
    def check_ready(_self):
        """Check if RAG system is ready."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{_self.base_url}/api/ready", headers=_self.headers)
                return response.json() if response.status_code == 200 else {"ready": False}
        except Exception as e:
            return {"ready": False, "error": str(e)}

    @st.cache_data(ttl=60)
    def get_documents(_self):
        """Get document stats."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{_self.base_url}/api/documents", headers=_self.headers)
                return response.json() if response.status_code == 200 else {}
        except Exception as e:
            return {"error": str(e)}

    async def stream_chat(self, query: str, conversation_id: str, doc_type: Optional[str] = None, request_id: str = None) -> Generator[dict, None, None]:
        """Stream chat response using SSE with buffering and request isolation."""
        payload = {
            "query": query,
            "conversation_id": conversation_id,
            "doc_type": doc_type
        }
        
        buffer = []
        buffer_size = 5 # Number of tokens to buffer before yielding
        
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=5.0)) as client:
                async with client.stream("POST", f"{self.base_url}/api/chat/stream", json=payload, headers=self.headers) as response:
                    if response.status_code != 200:
                        yield {"error": f"API Error: {response.status_code}"}
                        return

                    async for line in response.aiter_lines():
                        # Check for stop signal
                        if st.session_state.get("stop_generation", False):
                            yield {"control": "stopped"}
                            break
                            
                        # Validate request_id to prevent leak
                        if request_id and st.session_state.get("request_id") != request_id:
                            break

                        if line.startswith("data: "):
                            data_str = line[6:]
                            try:
                                data = json.loads(data_str)
                                
                                # Handle metadata/control messages immediately
                                if "type" in data and data["type"] != "token":
                                    yield data
                                    continue
                                    
                                # Buffer tokens for smoothness
                                if "token" in data:
                                    buffer.append(data["token"])
                                    if len(buffer) >= buffer_size:
                                        yield {"type": "token_chunk", "content": "".join(buffer)}
                                        buffer = []
                                        
                                # Handle final context/sources
                                if "answer" in data:
                                    if buffer:
                                        yield {"type": "token_chunk", "content": "".join(buffer)}
                                        buffer = []
                                    yield data
                                    
                            except json.JSONDecodeError:
                                continue

                    # Flush remaining buffer
                    if buffer:
                        yield {"type": "token_chunk", "content": "".join(buffer)}
        except Exception as e:
            yield {"error": str(e)}

    def upload_pdf(self, file_bytes, filename, doc_type="custom"):
        """Upload a PDF file."""
        try:
            files = {"file": (filename, file_bytes, "application/pdf")}
            data = {"doc_type": doc_type}
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.base_url}/api/upload", 
                    files=files, 
                    data=data,
                    headers={"x-api-key": self.api_key}
                )
                return response.json()
        except Exception as e:
            return {"success": False, "error": str(e)}
