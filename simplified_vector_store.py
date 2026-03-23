"""
Simplified Vector Store Service for AI Customer Service System
Uses in-memory storage instead of ChromaDB for initial implementation
"""

import os
import logging
from typing import List, Dict, Optional
from pathlib import Path
import uuid
import pickle
from datetime import datetime

# Use scikit-learn for basic vectorization instead of heavy langchain/chroma dependencies
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
except ImportError:
    logging.warning("sklearn not available, using basic similarity search")
    TfidfVectorizer = None
    cosine_similarity = None
    np = None


class VectorStoreService:
    """
    Simplified vector store service using TF-IDF for similarity search
    """
    
    def __init__(self, persist_directory: str = "./vector_store_data"):
        """
        Initialize the vector store service
        
        Args:
            persist_directory: Directory to persist vector database
        """
        self.persist_directory = persist_directory
        self.collections = {}  # {collection_name: {documents: [], metadatas: [], vectors: []}}
        self.vectorizers = {}  # {collection_name: TfidfVectorizer}
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        logging.info(f"VectorStoreService initialized with persist directory: {persist_directory}")

    def _load_collection(self, collection_name: str):
        """Load collection from disk if it exists"""
        file_path = os.path.join(self.persist_directory, f"{collection_name}.pkl")
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return pickle.load(f)
        return {"documents": [], "metadatas": [], "vectors": []}

    def _save_collection(self, collection_name: str):
        """Save collection to disk"""
        file_path = os.path.join(self.persist_directory, f"{collection_name}.pkl")
        with open(file_path, 'wb') as f:
            pickle.dump(self.collections[collection_name], f)

    def _ensure_collection_exists(self, collection_name: str):
        """Ensure collection exists in memory and on disk"""
        if collection_name not in self.collections:
            self.collections[collection_name] = self._load_collection(collection_name)
        
        # Initialize vectorizer if needed
        if collection_name not in self.vectorizers and TfidfVectorizer is not None:
            self.vectorizers[collection_name] = TfidfVectorizer(max_features=5000, stop_words='english')

    def add_document(self, knowledge_base_id: str, file_path: str, metadata: Optional[Dict] = None) -> str:
        """
        Add a document to the vector store
        
        Args:
            knowledge_base_id: ID of the knowledge base
            file_path: Path to the document to add
            metadata: Additional metadata to store with the document
            
        Returns:
            Collection name where the document was added
        """
        try:
            # For now, just simulate loading the document content
            # In a real implementation, we would use the DocumentParser here
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()[:1000]  # Take first 1000 chars as sample
            
            collection_name = f"kb_{knowledge_base_id}"
            self._ensure_collection_exists(collection_name)
            
            # Prepare metadata
            doc_metadata = {
                "source": file_path,
                "chunk_index": len(self.collections[collection_name]["documents"]),
                "knowledge_base_id": knowledge_base_id,
                "document_id": str(uuid.uuid4()),
                "added_at": datetime.now().isoformat()
            }
            if metadata:
                doc_metadata.update(metadata)
            
            # Add to collection
            self.collections[collection_name]["documents"].append(content)
            self.collections[collection_name]["metadatas"].append(doc_metadata)
            
            # Rebuild vectors for this collection (simplified approach)
            if TfidfVectorizer is not None:
                docs = self.collections[collection_name]["documents"]
                if docs:
                    vectorizer = self.vectorizers[collection_name]
                    vectors = vectorizer.fit_transform(docs)
                    self.collections[collection_name]["vectors"] = vectors
            
            # Save to disk
            self._save_collection(collection_name)
            
            logging.info(f"Added document to collection {collection_name}")
            return collection_name
            
        except Exception as e:
            logging.error(f"Error adding document {file_path} to vector store: {str(e)}")
            raise

    def similarity_search(self, knowledge_base_id: str, query: str, k: int = 5) -> List[Dict]:
        """
        Perform similarity search in the vector store
        
        Args:
            knowledge_base_id: ID of the knowledge base to search in
            query: Query string to search for
            k: Number of results to return
            
        Returns:
            List of matching documents with metadata
        """
        try:
            collection_name = f"kb_{knowledge_base_id}"
            
            if collection_name not in self.collections:
                self._ensure_collection_exists(collection_name)
            
            collection = self.collections[collection_name]
            documents = collection["documents"]
            
            if not documents:
                return []
            
            # Perform similarity search
            results = []
            
            if TfidfVectorizer is not None and len(collection["vectors"]) > 0:
                # Use TF-IDF based similarity
                vectorizer = self.vectorizers[collection_name]
                query_vector = vectorizer.transform([query])
                similarities = cosine_similarity(query_vector, collection["vectors"]).flatten()
                
                # Get top-k results
                top_indices = similarities.argsort()[-k:][::-1]
                
                for idx in top_indices:
                    results.append({
                        "content": documents[idx],
                        "metadata": collection["metadatas"][idx],
                        "score": float(similarities[idx])
                    })
            else:
                # Fallback to basic keyword matching
                query_lower = query.lower()
                scored_docs = []
                
                for i, doc in enumerate(documents):
                    doc_lower = doc.lower()
                    score = sum(1 for word in query_lower.split() if word in doc_lower)
                    scored_docs.append((i, score))
                
                # Sort by score and take top-k
                scored_docs.sort(key=lambda x: x[1], reverse=True)
                top_indices = [item[0] for item in scored_docs[:k]]
                
                for idx in top_indices:
                    results.append({
                        "content": documents[idx],
                        "metadata": collection["metadatas"][idx],
                        "score": scored_docs[top_indices.index(idx)][1]
                    })
            
            logging.info(f"Found {len(results)} results for query in knowledge base {knowledge_base_id}")
            return results
            
        except Exception as e:
            logging.error(f"Error performing similarity search in knowledge base {knowledge_base_id}: {str(e)}")
            raise

    def delete_knowledge_base(self, knowledge_base_id: str):
        """
        Delete an entire knowledge base collection
        
        Args:
            knowledge_base_id: ID of the knowledge base to delete
        """
        try:
            collection_name = f"kb_{knowledge_base_id}"
            if collection_name in self.collections:
                del self.collections[collection_name]
            
            # Remove from disk
            file_path = os.path.join(self.persist_directory, f"{collection_name}.pkl")
            if os.path.exists(file_path):
                os.remove(file_path)
                
            # Remove vectorizer
            if collection_name in self.vectorizers:
                del self.vectorizers[collection_name]
                
            logging.info(f"Deleted knowledge base collection: {collection_name}")
        except Exception as e:
            logging.error(f"Error deleting knowledge base {knowledge_base_id}: {str(e)}")
            raise

    def list_knowledge_bases(self) -> List[str]:
        """
        List all knowledge base collections
        
        Returns:
            List of knowledge base IDs
        """
        try:
            kb_ids = []
            for collection_name in self.collections.keys():
                if collection_name.startswith("kb_"):
                    kb_ids.append(collection_name.replace("kb_", ""))
            
            # Also include collections saved on disk
            for filename in os.listdir(self.persist_directory):
                if filename.endswith(".pkl"):
                    collection_name = filename[:-4]  # Remove .pkl
                    if collection_name.startswith("kb_") and collection_name not in [f"kb_{kb}" for kb in kb_ids]:
                        kb_ids.append(collection_name.replace("kb_", ""))
                        
            return kb_ids
        except Exception as e:
            logging.error(f"Error listing knowledge bases: {str(e)}")
            raise


# Initialize logging
logging.basicConfig(level=logging.INFO)


def test_vector_store():
    """
    Test function for the vector store service
    """
    print("Testing Vector Store Service...")
    
    # Initialize service
    service = VectorStoreService()
    
    # Example usage would go here
    print("Vector Store Service initialized successfully")


if __name__ == "__main__":
    test_vector_store()