"""Ollama LLM configuration and utilities."""
import ollama
from typing import Optional
from config import settings

class OllamaManager:
    """Manage Ollama LLM connection and configuration."""
    
    def __init__(self):
        """Initialize Ollama manager."""
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.client = None
    
    def check_ollama_running(self) -> bool:
        """Check if Ollama service is running.
        
        Returns:
            True if Ollama is running, False otherwise
        """
        try:
            response = ollama.list()
            return True
        except Exception as e:
            print(f"[!] Ollama connection error: {str(e)}")
            return False
    
    def check_model_available(self, model_name: Optional[str] = None) -> bool:
        """Check if specified model is available.
        
        Args:
            model_name: Name of model to check (defaults to configured model)
            
        Returns:
            True if model is available, False otherwise
        """
        model_name = model_name or self.model
        
        try:
            response = ollama.list()
            # Handle both old dict-style and new object-style API
            model_list = response.get('models', []) if isinstance(response, dict) else getattr(response, 'models', [])
            available_models = []
            for m in model_list:
                name = m.get('name', '') if isinstance(m, dict) else getattr(m, 'model', getattr(m, 'name', ''))
                if name:
                    available_models.append(name)
            
            # Check for exact match or base model name
            for available in available_models:
                if model_name in available or available.startswith(model_name):
                    return True
            
            return False
        except Exception as e:
            print(f"[!] Error checking models: {str(e)}")
            return False
    
    def list_models(self) -> list:
        """List all available models.
        
        Returns:
            List of available model names
        """
        try:
            response = ollama.list()
            model_list = response.get('models', []) if isinstance(response, dict) else getattr(response, 'models', [])
            names = []
            for m in model_list:
                name = m.get('name', '') if isinstance(m, dict) else getattr(m, 'model', getattr(m, 'name', ''))
                if name:
                    names.append(name)
            return names
        except Exception as e:
            print(f"Error listing models: {str(e)}")
            return []
    
    def pull_model(self, model_name: Optional[str] = None) -> bool:
        """Pull a model from Ollama library.
        
        Args:
            model_name: Name of model to pull (defaults to configured model)
            
        Returns:
            True if successful, False otherwise
        """
        model_name = model_name or self.model
        
        try:
            print(f"[*] Pulling model: {model_name}...")
            print("This may take a few minutes...")
            ollama.pull(model_name)
            print(f"✓ Model {model_name} pulled successfully")
            return True
        except Exception as e:
            print(f"✗ Error pulling model: {str(e)}")
            return False
    
    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        """Generate response using Ollama.
        
        Args:
            prompt: User prompt
            system: Optional system prompt
            **kwargs: Additional Ollama parameters
            
        Returns:
            Generated response text
        """
        try:
            messages = []
            
            if system:
                messages.append({"role": "system", "content": system})
            
            messages.append({"role": "user", "content": prompt})
            
            response = ollama.chat(
                model=self.model,
                messages=messages,
                **kwargs
            )
            
            return response['message']['content']
        except Exception as e:
            raise Exception(f"Ollama generation error: {str(e)}")
    
    def validate_setup(self) -> dict:
        """Validate Ollama setup and return status.
        
        Returns:
            Dictionary with validation status
        """
        status = {
            "ollama_running": False,
            "model_available": False,
            "available_models": [],
            "configured_model": self.model,
            "errors": []
        }
        
        # Check if Ollama is running
        if not self.check_ollama_running():
            status["errors"].append("Ollama service is not running. Please start Ollama.")
            return status
        
        status["ollama_running"] = True
        
        # List available models
        status["available_models"] = self.list_models()
        
        # Check if configured model is available
        if self.check_model_available():
            status["model_available"] = True
        else:
            status["errors"].append(
                f"Model '{self.model}' not found. "
                f"Run: ollama pull {self.model}"
            )
        
        return status


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("Ollama Setup Validation")
    print("=" * 60)
    
    manager = OllamaManager()
    status = manager.validate_setup()
    
    print(f"\n[OK] Ollama Running: {status['ollama_running']}")
    print(f"[OK] Model Available: {status['model_available']}")
    print(f"[OK] Configured Model: {status['configured_model']}")
    
    if status['available_models']:
        print(f"\n[*] Available Models:")
        for model in status['available_models']:
            print(f"  - {model}")
    
    if status['errors']:
        print("\n[!] Errors:")
        for error in status['errors']:
            print(f"  - {error}")
    else:
        print("\n[OK] Ollama setup is valid!")
        
        # Test generation
        print("\n[*] Testing generation...")
        try:
            response = manager.generate("Say 'Hello, World!' in one sentence.")
            print(f"Response: {response}")
        except Exception as e:
            print(f"Generation test failed: {str(e)}")
