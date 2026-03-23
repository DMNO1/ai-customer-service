"""
Configuration for the RAG module.
"""
import os

# Vector store settings
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "customer_service_docs")

# Embedding model settings
EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
)