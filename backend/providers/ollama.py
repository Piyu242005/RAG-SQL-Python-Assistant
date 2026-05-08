from langchain_ollama import ChatOllama
import logging

class OllamaProvider:
    def __init__(self, model: str = "llama3.2"):
        self.llm = ChatOllama(
            model=model,
            temperature=0.2,
            # base_url="http://ollama:11434" # Use this if running in Docker
        )

    async def stream(self, prompt: str):
        try:
            async for chunk in self.llm.astream(prompt):
                yield chunk.content
        except Exception as e:
            logging.error(f"Error streaming from Ollama: {str(e)}")
            yield f"Error: {str(e)}"
