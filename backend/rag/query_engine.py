"""
Query engine for the RAG system.
"""
from .embedder import Embedder
from .vector_store import VectorStore

class QueryEngine:
    def __init__(self):
        self.embedder = Embedder()
        self.vector_store = VectorStore()

    def query(self, user_question: str, n_results: int = 5) -> dict:
        """
        Process a user question and return relevant context from the vector store.
        
        Args:
            user_question: The question from the user.
            n_results: Number of relevant documents to retrieve.
            
        Returns:
            A dictionary containing the retrieved context and the original question.
        """
        # Step 1: Embed the user's question
        query_embedding = self.embedder.text_to_embedding(user_question)
        
        # Step 2: Retrieve relevant documents
        results = self.vector_store.query(query_embedding, n_results=n_results)
        
        # Step 3: Package the results
        # The actual LLM call will be handled by the main application
        return {
            "question": user_question,
            "context": results
        }