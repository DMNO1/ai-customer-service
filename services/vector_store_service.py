"""
Vector Store Service for AI Customer Service System
Implements RAG (Retrieval Augmented Generation) functionality using ChromaDB
"""

import logging
from typing import List, Dict, Any, Optional
# Try different Chroma import strategies for compatibility
try:
    from langchain_chroma import Chroma
except ImportError:
    try:
        from langchain_community.vectorstores import Chroma
    except ImportError:
        from langchain.vectorstores import Chroma
# Try different OpenAI embeddings import strategies for compatibility
try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    try:
        from langchain_community.embeddings import OpenAIEmbeddings
    except ImportError:
        from langchain.embeddings import OpenAIEmbeddings
# Import text splitter with compatibility for new langchain-text-splitters package
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    except ImportError:
        raise ImportError("RecursiveCharacterTextSplitter not found. Please install langchain-text-splitters.")
# Import document loaders with error handling for compatibility
import importlib

def import_loader(module_name, class_name):
    try:
        module = importlib.import_module(module_name)
        return getattr(module, class_name)
    except ImportError:
        return None

# Try different import strategies for document loaders
PyPDFLoader = import_loader("langchain_community.document_loaders", "PyPDFLoader")
if PyPDFLoader is None:
    PyPDFLoader = import_loader("langchain.document_loaders", "PyPDFLoader")

Docx2txtLoader = import_loader("langchain_community.document_loaders", "Docx2txtLoader")
if Docx2txtLoader is None:
    Docx2txtLoader = import_loader("langchain.document_loaders", "Docx2txtLoader")

TextLoader = import_loader("langchain_community.document_loaders", "TextLoader")
if TextLoader is None:
    TextLoader = import_loader("langchain.document_loaders", "TextLoader")

# Import docx2txt as fallback
try:
    import docx2txt
except ImportError:
    docx2txt = None

# Import Document from langchain core
try:
    from langchain_core.documents import Document
except ImportError:
    try:
        from langchain.schema import Document
    except ImportError:
        from langchain.text_splitter import Document
from pathlib import Path
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStoreService:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the Vector Store Service
        :param persist_directory: Directory to persist vector database
        """
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Create persist directory if it doesn't exist
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize Chroma client
        self.db = Chroma(
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )
        
        logger.info("VectorStoreService initialized successfully")

    def add_document(self, knowledge_base_id: str, file_path: str) -> bool:
        """
        Add a document to the vector store
        :param knowledge_base_id: Identifier for the knowledge base
        :param file_path: Path to the document file
        :return: True if successful, False otherwise
        """
        try:
            logger.info(f"Adding document {file_path} to knowledge base {knowledge_base_id}")
            
            # Load document based on file type
            file_ext = Path(file_path).suffix.lower()
            documents = []
            
            if file_ext == '.pdf':
                if PyPDFLoader:
                    loader = PyPDFLoader(file_path)
                    documents = loader.load()
                else:
                    raise ValueError("PyPDFLoader not available")
            elif file_ext in ['.docx', '.doc']:
                if Docx2txtLoader:
                    try:
                        # Try using the langchain loader first
                        loader = Docx2txtLoader(file_path)
                        documents = loader.load()
                    except:
                        # Fallback to direct docx2txt usage
                        if docx2txt:
                            text = docx2txt.process(file_path)
                            documents = [Document(page_content=text, metadata={"source": file_path})]
                        else:
                            raise ValueError("Neither Docx2txtLoader nor docx2txt module is available")
                else:
                    # Fallback to direct docx2txt usage
                    if docx2txt:
                        text = docx2txt.process(file_path)
                        documents = [Document(page_content=text, metadata={"source": file_path})]
                    else:
                        raise ValueError("Neither Docx2txtLoader nor docx2txt module is available")
            elif file_ext == '.txt':
                if TextLoader:
                    loader = TextLoader(file_path, encoding='utf-8')
                    documents = loader.load()
                else:
                    # Fallback: read file directly
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    documents = [Document(page_content=text, metadata={"source": file_path})]
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            # Split documents
            texts = self.text_splitter.split_documents(documents)
            
            # Add to vector store with metadata
            self.db.add_texts(
                texts=[doc.page_content for doc in texts],
                metadatas=[
                    {
                        "source": file_path,
                        "knowledge_base_id": knowledge_base_id,
                        **doc.metadata
                    } for doc in texts
                ],
                ids=[f"{knowledge_base_id}_{i}" for i in range(len(texts))]
            )
            
            logger.info(f"Successfully added document {file_path} to knowledge base {knowledge_base_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document {file_path} to knowledge base {knowledge_base_id}: {str(e)}")
            return False

    def similarity_search(self, knowledge_base_id: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform similarity search in the vector store
        :param knowledge_base_id: Identifier for the knowledge base to search in
        :param query: Query string
        :param k: Number of results to return
        :return: List of similar documents with metadata
        """
        try:
            logger.info(f"Performing similarity search in knowledge base {knowledge_base_id} for query: {query}")
            
            # Filter by knowledge_base_id
            results = self.db.similarity_search_with_score(
                query,
                k=k,
                filter={"knowledge_base_id": knowledge_base_id}
            )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                })
            
            logger.info(f"Found {len(formatted_results)} results for query in knowledge base {knowledge_base_id}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error performing similarity search in knowledge base {knowledge_base_id}: {str(e)}")
            return []

    def delete_knowledge_base(self, knowledge_base_id: str) -> bool:
        """
        Delete all documents associated with a knowledge base
        :param knowledge_base_id: Identifier for the knowledge base to delete
        :return: True if successful, False otherwise
        """
        try:
            logger.info(f"Deleting knowledge base {knowledge_base_id}")
            
            # In Chroma, we can't directly delete by metadata, so we'll need to get all items
            # and delete those that match our knowledge_base_id
            collection = self.db._collection
            results = collection.get(where={"knowledge_base_id": knowledge_base_id})
            
            if results['ids']:
                collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} documents from knowledge base {knowledge_base_id}")
            
            return True
        except Exception as e:
            logger.error(f"Error deleting knowledge base {knowledge_base_id}: {str(e)}")
            return False

# Example usage and testing
if __name__ == "__main__":
    # Initialize the service
    vss = VectorStoreService()
    
    # Example: Add a document (uncomment to test with actual file)
    # success = vss.add_document("test_kb", "path/to/your/document.pdf")
    
    # Example: Search (uncomment to test)
    # results = vss.similarity_search("test_kb", "your search query")
    # print(results)