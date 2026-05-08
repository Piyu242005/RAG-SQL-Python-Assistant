import logging
import httpx
from typing import AsyncGenerator, Dict, Any
from langchain_ollama import OllamaLLM
from providers.base import BaseLLMProvider
from core.config import settings

logger = logging.getLogger("ollama-provider")

class OllamaProvider(BaseLLMProvider):
    """Ollama LLM provider implementation."""
    
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.llm = OllamaLLM(
            base_url=self.base_url,
            model=self.model,
            temperature=0.1,
            num_ctx=4096,
            num_predict=1024,
            timeout=settings.llm_timeout_sec
        )

    async def generate(self, prompt: str, **kwargs) -> str:
        try:
            return await self.llm.ainvoke(prompt, **kwargs)
        except Exception as e:
            logger.error(f"Ollama generate error: {e}")
            raise

    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        try:
            async for chunk in self.llm.astream(prompt, **kwargs):
                yield str(chunk)
        except Exception as e:
            logger.error(f"Ollama stream error: {e}")
            raise

    def validate_setup(self) -> Dict[str, Any]:
        """Check if Ollama is running and model is available."""
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=2.0)
            if response.status_code != 200:
                return {"ollama_running": False, "model_available": False}
            
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]
            
            # Check for exact or tag-less match
            model_available = any(
                self.model in name or name.startswith(self.model) 
                for name in model_names
            )
            
            return {
                "ollama_running": True,
                "model_available": model_available,
                "available_models": model_names,
                "configured_model": self.model
            }
        except Exception as e:
            logger.error(f"Ollama validation failed: {e}")
            return {"ollama_running": False, "model_available": False, "error": str(e)}
