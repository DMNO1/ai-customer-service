"""
Abstract base class for LLM models.
"""
from abc import ABC, abstractmethod

class BaseModel(ABC):
    @abstractmethod
    def generate(self, prompt: str, context: str = None) -> str:
        """
        Generate a response from the model.
        
        Args:
            prompt: The user's prompt or question.
            context: Optional context retrieved from the vector store.
            
        Returns:
            The model's generated response.
        """
        pass