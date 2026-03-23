"""
Main Service for AI Customer Service System
Integrates all components: vector store, document parsing, web scraping, and LLM providers
"""

import logging
import os
from typing import List, Dict, Optional
from pathlib import Path
import json
from datetime import datetime

from vector_store_service import VectorStoreService
from document_parser import DocumentParser
from web_scraper import WebScraper
from llm_provider import LLMManager, OpenAIProvider, ClaudeProvider, ZhipuAIProvider, DashScopeProvider

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
except ImportError:
    Flask = None
    CORS = None
    logging.warning("Flask not available. Running in standalone mode.")


class AICustomerService:
    """
    Main service class that integrates all AI customer service components
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the AI customer service
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.vector_store = VectorStoreService(
            persist_directory=self.config.get("vector_store_dir", "./chroma_db")
        )
        self.document_parser = DocumentParser()
        self.web_scraper = WebScraper(timeout=self.config.get("scraper_timeout", 30))
        self.llm_manager = LLMManager()
        
        # Initialize LLM providers based on environment variables
        self._initialize_llm_providers()
        
        # Set up logging
        log_level = self.config.get("log_level", "INFO")
        logging.basicConfig(level=getattr(logging, log_level))
        
        logging.info("AICustomerService initialized successfully")
    
    def _initialize_llm_providers(self):
        """
        Initialize LLM providers based on available API keys
        """
        # Register OpenAI provider if key is available
        if os.getenv("OPENAI_API_KEY"):
            self.llm_manager.register_provider("openai", OpenAIProvider())
        
        # Register Claude provider if key is available
        if os.getenv("ANTHROPIC_API_KEY"):
            self.llm_manager.register_provider("anthropic", ClaudeProvider())
        
        # Register ZhipuAI provider if key is available
        if os.getenv("ZHIPU_API_KEY"):
            self.llm_manager.register_provider("zhipu", ZhipuAIProvider())
        
        # Register DashScope provider if key is available
        if os.getenv("DASHSCOPE_API_KEY"):
            self.llm_manager.register_provider("dashscope", DashScopeProvider())
        
        # Set default provider
        if self.llm_manager.list_providers():
            default_provider = self.config.get("default_llm_provider", self.llm_manager.list_providers()[0])
            try:
                self.llm_manager.set_default_provider(default_provider)
            except ValueError:
                # If default provider not available, use first available
                self.llm_manager.set_default_provider(self.llm_manager.list_providers()[0])
        
        logging.info(f"Initialized LLM providers: {self.llm_manager.list_providers()}")
    
    def add_document_to_knowledge_base(self, knowledge_base_id: str, file_path: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Add a document to a knowledge base
        
        Args:
            knowledge_base_id: ID of the knowledge base
            file_path: Path to the document to add
            metadata: Additional metadata to store with the document
            
        Returns:
            Result dictionary with success status and details
        """
        try:
            # Parse the document to verify it's valid
            parsed_content = self.document_parser.parse_document(file_path)
            
            if not parsed_content.strip():
                raise ValueError(f"Document {file_path} appears to be empty after parsing")
            
            # Add document to vector store
            collection_name = self.vector_store.add_document(knowledge_base_id, file_path, metadata)
            
            result = {
                "success": True,
                "knowledge_base_id": knowledge_base_id,
                "collection_name": collection_name,
                "file_path": file_path,
                "document_parsed_length": len(parsed_content),
                "timestamp": datetime.now().isoformat()
            }
            
            logging.info(f"Successfully added document to knowledge base: {result}")
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "knowledge_base_id": knowledge_base_id,
                "file_path": file_path,
                "timestamp": datetime.now().isoformat()
            }
            logging.error(f"Failed to add document to knowledge base: {error_result}")
            return error_result
    
    async def add_url_to_knowledge_base(self, knowledge_base_id: str, url: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Add content from a URL to a knowledge base
        
        Args:
            knowledge_base_id: ID of the knowledge base
            url: URL to scrape and add
            metadata: Additional metadata to store with the content
            
        Returns:
            Result dictionary with success status and details
        """
        try:
            # Scrape the URL content
            content = await self.web_scraper.scrape_url(url)
            
            if not content.strip():
                raise ValueError(f"URL {url} returned empty content after scraping")
            
            # Save content temporarily to add to vector store
            temp_file_path = f"./temp_scraped_content_{knowledge_base_id}_{hash(url)}.txt"
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Add to vector store
            collection_name = self.vector_store.add_document(knowledge_base_id, temp_file_path, metadata)
            
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            # Also extract and store metadata
            metadata_result = await self.web_scraper.extract_metadata(url)
            
            result = {
                "success": True,
                "knowledge_base_id": knowledge_base_id,
                "collection_name": collection_name,
                "url": url,
                "content_length": len(content),
                "scraped_metadata": metadata_result,
                "timestamp": datetime.now().isoformat()
            }
            
            logging.info(f"Successfully added URL content to knowledge base: {result}")
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "knowledge_base_id": knowledge_base_id,
                "url": url,
                "timestamp": datetime.now().isoformat()
            }
            logging.error(f"Failed to add URL content to knowledge base: {error_result}")
            # Clean up temporary file if it exists
            temp_file_path = f"./temp_scraped_content_{knowledge_base_id}_{hash(url)}.txt"
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return error_result
    
    def query_knowledge_base(self, knowledge_base_id: str, query: str, k: int = 5) -> Dict:
        """
        Query a knowledge base for relevant information
        
        Args:
            knowledge_base_id: ID of the knowledge base to query
            query: Query string
            k: Number of results to return
            
        Returns:
            Results dictionary with relevant information
        """
        try:
            results = self.vector_store.similarity_search(knowledge_base_id, query, k)
            
            result = {
                "success": True,
                "knowledge_base_id": knowledge_base_id,
                "query": query,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
            logging.info(f"Successfully queried knowledge base with {len(results)} results")
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "knowledge_base_id": knowledge_base_id,
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
            logging.error(f"Failed to query knowledge base: {error_result}")
            return error_result
    
    def generate_response(self, messages: List[Dict], provider: Optional[str] = None, **kwargs) -> Dict:
        """
        Generate a response using the LLM
        
        Args:
            messages: List of messages in the conversation
            provider: LLM provider to use (uses default if None)
            **kwargs: Additional parameters for the LLM
            
        Returns:
            Response dictionary with generated text
        """
        try:
            response_text = self.llm_manager.chat_completion(messages, provider, **kwargs)
            
            result = {
                "success": True,
                "response": response_text,
                "provider_used": provider or self.llm_manager.default_provider,
                "timestamp": datetime.now().isoformat(),
                "message_count": len(messages)
            }
            
            logging.info(f"Successfully generated response using {result['provider_used']}")
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "provider_requested": provider,
                "timestamp": datetime.now().isoformat()
            }
            logging.error(f"Failed to generate response: {error_result}")
            return error_result
    
    def create_knowledge_base(self, knowledge_base_id: str, name: str, description: str = "") -> Dict:
        """
        Create a new knowledge base (verification through vector store initialization)
        
        Args:
            knowledge_base_id: Unique ID for the knowledge base
            name: Display name for the knowledge base
            description: Description of the knowledge base
            
        Returns:
            Result dictionary with creation details
        """
        try:
            # Simply test that we can perform operations on this knowledge base
            # The vector store handles collection creation automatically
            existing_kbs = self.vector_store.list_knowledge_bases()
            
            result = {
                "success": True,
                "knowledge_base_id": knowledge_base_id,
                "name": name,
                "description": description,
                "already_exists": knowledge_base_id in existing_kbs,
                "timestamp": datetime.now().isoformat()
            }
            
            logging.info(f"Processed knowledge base creation request: {result}")
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "knowledge_base_id": knowledge_base_id,
                "timestamp": datetime.now().isoformat()
            }
            logging.error(f"Failed to create knowledge base: {error_result}")
            return error_result
    
    def list_knowledge_bases(self) -> Dict:
        """
        List all available knowledge bases
        
        Returns:
            Result dictionary with list of knowledge base IDs
        """
        try:
            kb_list = self.vector_store.list_knowledge_bases()
            
            result = {
                "success": True,
                "knowledge_bases": kb_list,
                "count": len(kb_list),
                "timestamp": datetime.now().isoformat()
            }
            
            logging.info(f"Listed {result['count']} knowledge bases")
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logging.error(f"Failed to list knowledge bases: {error_result}")
            return error_result


def create_flask_app(service: AICustomerService):
    """
    Create a Flask app to serve the AI customer service API
    
    Args:
        service: Initialized AICustomerService instance
        
    Returns:
        Flask app instance
    """
    if Flask is None:
        raise ImportError("Flask is required to create the web API. Please install it with: pip install flask flask-cors")
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})
    
    @app.route('/knowledge/base', methods=['POST'])
    def create_knowledge_base():
        """Create a new knowledge base"""
        try:
            data = request.get_json()
            kb_id = data.get('id')
            name = data.get('name')
            description = data.get('description', '')
            
            if not kb_id or not name:
                return jsonify({"error": "id and name are required"}), 400
            
            result = service.create_knowledge_base(kb_id, name, description)
            return jsonify(result), 201 if result["success"] else 500
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/knowledge/bases', methods=['GET'])
    def list_knowledge_bases():
        """List all knowledge bases"""
        try:
            result = service.list_knowledge_bases()
            return jsonify(result), 200 if result["success"] else 500
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/knowledge/<kb_id>/document', methods=['POST'])
    def add_document_to_knowledge_base(kb_id):
        """Add a document to a knowledge base"""
        try:
            if 'file' not in request.files:
                return jsonify({"error": "file is required"}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({"error": "no file selected"}), 400
            
            # Save file temporarily
            temp_path = f"./temp_upload_{kb_id}_{file.filename}"
            file.save(temp_path)
            
            # Add to knowledge base
            metadata = request.form.get('metadata')
            if metadata:
                metadata = json.loads(metadata)
            
            result = service.add_document_to_knowledge_base(kb_id, temp_path, metadata)
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return jsonify(result), 201 if result["success"] else 500
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/knowledge/<kb_id>/url', methods=['POST'])
    async def add_url_to_knowledge_base(kb_id):
        """Add content from URL to a knowledge base"""
        try:
            data = request.get_json()
            url = data.get('url')
            
            if not url:
                return jsonify({"error": "url is required"}), 400
            
            result = await service.add_url_to_knowledge_base(kb_id, url)
            return jsonify(result), 201 if result["success"] else 500
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/knowledge/<kb_id>/search', methods=['POST'])
    def query_knowledge_base(kb_id):
        """Query a knowledge base"""
        try:
            data = request.get_json()
            query = data.get('query')
            k = data.get('k', 5)
            
            if not query:
                return jsonify({"error": "query is required"}), 400
            
            result = service.query_knowledge_base(kb_id, query, k)
            return jsonify(result), 200 if result["success"] else 500
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route('/chat', methods=['POST'])
    def generate_response():
        """Generate a chat response"""
        try:
            data = request.get_json()
            messages = data.get('messages', [])
            provider = data.get('provider')
            
            if not messages:
                return jsonify({"error": "messages are required"}), 400
            
            result = service.generate_response(messages, provider)
            return jsonify(result), 200 if result["success"] else 500
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return app


# Initialize logging
logging.basicConfig(level=logging.INFO)


def main():
    """
    Main entry point for standalone execution
    """
    print("Initializing AI Customer Service...")
    
    # Initialize the service
    service = AICustomerService()
    
    # Print available LLM providers
    print(f"Available LLM providers: {service.llm_manager.list_providers()}")
    
    # Print knowledge bases
    kb_result = service.list_knowledge_bases()
    print(f"Existing knowledge bases: {kb_result}")
    
    print("AI Customer Service initialized successfully!")
    
    # Optionally start the Flask API server
    if Flask is not None:
        print("Starting Flask API server...")
        app = create_flask_app(service)
        port = int(os.getenv("PORT", 8000))
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        print("Flask not available. Running in standalone mode.")


if __name__ == "__main__":
    main()