from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Optional, Any

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a complete response."""
        pass
    
    @abstractmethod
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream response tokens."""
        pass

    @abstractmethod
    def validate_setup(self) -> dict:
        """Validate provider configuration and connectivity."""
        pass
