"""
Ollama model adapter for local LLMs.
"""
import requests
from .base import BaseModel

class OllamaAdapter(BaseModel):
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def generate(self, prompt: str, context: str = None) -> str:
        """
        Generate a response using a local Ollama model.
        
        Args:
            prompt: The user's prompt or question.
            context: Optional context retrieved from the vector store.
            
        Returns:
            The model's generated response.
        """
        if context:
            full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
        else:
            full_prompt = prompt
            
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7
                }
            }
        )
        response.raise_for_status()
        return response.json()["response"]