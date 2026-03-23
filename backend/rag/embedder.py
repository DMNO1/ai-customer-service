"""
Embedder module using sentence-transformers.
"""
from sentence_transformers import SentenceTransformer
from .config import EMBEDDING_MODEL_NAME

class Embedder:
    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        self.model = SentenceTransformer(model_name)

    def text_to_embedding(self, text: str) -> list:
        """
        Convert a text string to an embedding vector.
        
        Args:
            text: The input text.
            
        Returns:
            A list representing the embedding vector.
        """
        embedding = self.model.encode(text)
        return embedding.tolist()