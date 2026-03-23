"""
Factory for creating model instances based on configuration.
"""
import os
from .base import BaseModel
from .openai_adapter import OpenAIAdapter
from .anthropic_adapter import AnthropicAdapter
from .ollama_adapter import OllamaAdapter

def get_model() -> BaseModel:
    """
    Factory function to get the configured model instance.
    
    Returns:
        An instance of a BaseModel subclass.
        
    Raises:
        ValueError: If the configured model provider is not supported.
    """
    provider = os.getenv("MODEL_PROVIDER", "ollama").lower()
    
    if provider == "openai":
        return OpenAIAdapter()
    elif provider == "anthropic":
        return AnthropicAdapter()
    elif provider == "ollama":
        return OllamaAdapter()
    else:
        raise ValueError(f"Unsupported model provider: {provider}")