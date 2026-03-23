"""
OpenAI model adapter.
"""
import os
from openai import OpenAI
from .base import BaseModel

class OpenAIAdapter(BaseModel):
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def generate(self, prompt: str, context: str = None) -> str:
        """
        Generate a response using OpenAI's API.
        
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
            
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful customer service assistant."},
                {"role": "user", "content": full_prompt}
            ]
        )
        return response.choices[0].message.content