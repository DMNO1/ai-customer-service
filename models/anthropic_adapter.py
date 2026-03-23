"""
Anthropic model adapter.
"""
import os
from anthropic import Anthropic
from .base import BaseModel

class AnthropicAdapter(BaseModel):
    def __init__(self, api_key: str = None, model: str = "claude-3-opus-20240229"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        self.client = Anthropic(api_key=self.api_key)
        self.model = model

    def generate(self, prompt: str, context: str = None) -> str:
        """
        Generate a response using Anthropic's API.
        
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
            
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system="You are a helpful customer service assistant.",
            messages=[
                {"role": "user", "content": full_prompt}
            ]
        )
        return response.content[0].text