"""
Test script for the RAG system with minimal dependencies.
This script tests the core functionality without loading the full model.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag.embedder import Embedder
from rag.vector_store import VectorStore

def test_rag_components():
    """
    Test the RAG components in isolation.
    """
    print("Testing Embedder...")
    embedder = Embedder()
    embedding = embedder.text_to_embedding("Hello, world!")
    print(f"Embedding dimension: {len(embedding)}")
    
    print("\nTesting Vector Store...")
    vector_store = VectorStore()
    vector_store.add_document(
        doc_id="test_doc",
        text="This is a test document about customer service policies.",
        embedding=embedding,
        metadata={"source": "test"}
    )
    
    print("\nQuerying Vector Store...")
    results = vector_store.query(embedding, n_results=1)
    print(f"Retrieved document: {results['documents'][0][0][:50]}...")
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    test_rag_components()