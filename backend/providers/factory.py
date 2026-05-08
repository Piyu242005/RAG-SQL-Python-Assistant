from providers.base import BaseLLMProvider
from providers.ollama import OllamaProvider
from core.config import settings

class LLMFactory:
    """Factory for creating LLM providers."""
    
    @staticmethod
    def get_provider() -> BaseLLMProvider:
        provider_type = settings.llm_provider.lower()
        
        if provider_type == "ollama":
            return OllamaProvider()
        # Add other providers here (openai, claude)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_type}")
