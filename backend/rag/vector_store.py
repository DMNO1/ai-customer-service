"""
Vector store module using ChromaDB.
"""
import chromadb
from chromadb.utils import embedding_functions
from .config import VECTOR_STORE_PATH, COLLECTION_NAME

class VectorStore:
    def __init__(self, path: str = VECTOR_STORE_PATH, collection_name: str = COLLECTION_NAME):
        self.client = chromadb.PersistentClient(path=path)
        # We'll use the default embedding function for now, as we handle embedding separately
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=None  # We will provide pre-computed embeddings
        )

    def add_document(self, doc_id: str, text: str, embedding: list, metadata: dict = None):
        """
        Add a document to the vector store.
        
        Args:
            doc_id: Unique identifier for the document.
            text: The raw text of the document.
            embedding: The pre-computed embedding vector.
            metadata: Optional metadata dictionary.
        """
        self.collection.add(
            ids=[doc_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata] if metadata else None
        )

    def query(self, query_embedding: list, n_results: int = 5) -> dict:
        """
        Query the vector store for similar documents.
        
        Args:
            query_embedding: The embedding of the query.
            n_results: Number of results to return.
            
        Returns:
            A dictionary containing the query results.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results