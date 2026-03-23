"""
Vector Store Service for AI Customer Service System
Implements RAG (Retrieval Augmented Generation) functionality with ChromaDB
"""

import os
import logging
from typing import List, Dict, Optional
from pathlib import Path
import uuid

try:
    import chromadb
    from chromadb.config import Settings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
    from langchain_chroma import Chroma
    from langchain_openai import OpenAIEmbeddings
except ImportError as e:
    logging.error(f"Missing required packages for vector store: {e}")
    raise


class VectorStoreService:
    """
    Service class for handling vector storage operations
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the vector store service
        
        Args:
            persist_directory: Directory to persist vector database
        """
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Initialize embeddings lazily (only when needed)
        self._embeddings = None
        
        logging.info(f"VectorStoreService initialized with persist directory: {persist_directory}")
    
    @property
    def embeddings(self):
        """Lazy load embeddings when first accessed"""
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings()
        return self._embeddings

    def _load_document(self, file_path: str) -> List[str]:
        """
        Load document based on file type
        
        Args:
            file_path: Path to the document
            
        Returns:
            List of text chunks from the document
        """
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            loader = PyPDFLoader(file_path)
        elif file_extension == '.docx':
            loader = Docx2txtLoader(file_path)
        elif file_extension == '.txt':
            loader = TextLoader(file_path, encoding='utf-8')
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        documents = loader.load()
        texts = [doc.page_content for doc in documents]
        
        # Split the text into chunks
        chunks = []
        for text in texts:
            chunks.extend(self.text_splitter.split_text(text))
        
        return chunks

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
            # Load and split the document
            chunks = self._load_document(file_path)
            
            # Create collection for this knowledge base
            collection_name = f"kb_{knowledge_base_id}"
            
            # Add chunks to the collection
            vector_store = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
                client=self.client
            )
            
            # Prepare metadata for each chunk
            metadatas = []
            for i, chunk in enumerate(chunks):
                meta = {
                    "source": file_path,
                    "chunk_index": i,
                    "knowledge_base_id": knowledge_base_id,
                    "document_id": str(uuid.uuid4())
                }
                if metadata:
                    meta.update(metadata)
                metadatas.append(meta)
            
            # Add documents to the collection
            vector_store.add_texts(
                texts=chunks,
                metadatas=metadatas
            )
            
            logging.info(f"Added {len(chunks)} chunks from {file_path} to collection {collection_name}")
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
            
            # Initialize the vector store
            vector_store = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory,
                client=self.client
            )
            
            # Perform similarity search
            results = vector_store.similarity_search_with_score(query, k=k)
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                })
            
            logging.info(f"Found {len(formatted_results)} results for query in knowledge base {knowledge_base_id}")
            return formatted_results
            
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
            self.client.delete_collection(collection_name)
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
            collections = self.client.list_collections()
            kb_ids = []
            for collection in collections:
                if collection.name.startswith("kb_"):
                    kb_ids.append(collection.name.replace("kb_", ""))
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