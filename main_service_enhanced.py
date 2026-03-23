"""
Enhanced Main Service for AI Customer Service System
Integrates all components with Feishu notifications and improved error handling
"""

import logging
import os
import sys
from typing import List, Dict, Optional
from pathlib import Path
import json
from datetime import datetime, timedelta
import traceback

# Import core components
from services.vector_store_service import VectorStoreService
from services.document_parser import DocumentParser
from services.web_scraper import WebScraper
from services.llm_provider import LLMManager, OpenAIProvider, ClaudeProvider, ZhipuAIProvider, DashScopeProvider
from services.feishu_notifier import FeishuNotifier

# API error handling patterns (from api-error-handling skill)
class APIErrorHandler:
    """
    Centralized error handler following API error handling best practices
    """
    
    @staticmethod
    def handle_exception(e: Exception, context: str = "") -> Dict:
        """
        Handle exceptions and return standardized error response
        
        Args:
            e: Exception that occurred
            context: Context where error occurred
            
        Returns:
            Standardized error dictionary
        """
        error_id = str(hash(f"{datetime.now().timestamp()}_{context}_{str(e)}"))[-8:]
        
        error_info = {
            "error": True,
            "error_id": error_id,
            "context": context,
            "message": str(e),
            "type": type(e).__name__,
            "timestamp": datetime.now().isoformat()
        }
        
        # Extract specific error messages based on exception type
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            try:
                # Try to extract API error message
                resp_json = e.response.json()
                if 'message' in resp_json:
                    error_info['api_message'] = resp_json['message']
                if 'error' in resp_json:
                    error_info['api_error'] = resp_json['error']
            except:
                error_info['raw_response'] = e.response.text[:500]
        
        # Log error with full traceback for debugging
        logging.error(f"API Error [{error_id}] in {context}: {str(e)}")
        logging.debug(traceback.format_exc())
        
        return error_info
    
    @staticmethod
    def create_error_response(error_info: Dict, user_message: Optional[str] = None) -> Dict:
        """
        Create user-friendly error response
        
        Args:
            error_info: Error information dictionary
            user_message: Optional custom user message
            
        Returns:
            Response dictionary with success=False and error details
        """
        response = {
            "success": False,
            "error": user_message or "An error occurred while processing your request.",
            "error_id": error_info.get("error_id"),
            "timestamp": error_info.get("timestamp")
        }
        
        # Add debug info in development
        if os.getenv("FLASK_ENV") == "development":
            response["debug"] = {
                "context": error_info.get("context"),
                "type": error_info.get("type"),
                "details": error_info.get("message")
            }
        
        return response


class EnhancedAICustomerService:
    """
    Enhanced AI Customer Service with Feishu notifications and robust error handling
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the enhanced AI customer service
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.error_handler = APIErrorHandler()
        
        # Initialize components
        try:
            self.vector_store = VectorStoreService(
                persist_directory=self.config.get("vector_store_dir", "./chroma_db")
            )
            logging.info("✓ VectorStoreService initialized")
        except Exception as e:
            error = self.error_handler.handle_exception(e, "VectorStoreService.init")
            self.vector_store = None
            self._send_alert("error", "Failed to initialize VectorStoreService", error)
        
        try:
            self.document_parser = DocumentParser()
            logging.info("✓ DocumentParser initialized")
        except Exception as e:
            error = self.error_handler.handle_exception(e, "DocumentParser.init")
            self.document_parser = None
            self._send_alert("error", "Failed to initialize DocumentParser", error)
        
        try:
            self.web_scraper = WebScraper(timeout=self.config.get("scraper_timeout", 30))
            logging.info("✓ WebScraper initialized")
        except Exception as e:
            error = self.error_handler.handle_exception(e, "WebScraper.init")
            self.web_scraper = None
            self._send_alert("error", "Failed to initialize WebScraper", error)
        
        try:
            self.llm_manager = LLMManager()
            self._initialize_llm_providers()
            logging.info("✓ LLMManager initialized")
        except Exception as e:
            error = self.error_handler.handle_exception(e, "LLMManager.init")
            self.llm_manager = None
            self._send_alert("error", "Failed to initialize LLMManager", error)
        
        try:
            self.feishu_notifier = FeishuNotifier()
            logging.info("✓ FeishuNotifier initialized")
        except Exception as e:
            error = self.error_handler.handle_exception(e, "FeishuNotifier.init")
            self.feishu_notifier = None
            logging.warning("Feishu notifications disabled due to initialization error")
        
        logging.info("EnhancedAICustomerService initialization complete")
    
    def _initialize_llm_providers(self):
        """
        Initialize LLM providers based on available API keys
        """
        providers_initialized = []
        
        # OpenAI
        if os.getenv("OPENAI_API_KEY"):
            try:
                self.llm_manager.register_provider("openai", OpenAIProvider())
                providers_initialized.append("openai")
            except Exception as e:
                logging.warning(f"Failed to initialize OpenAI provider: {e}")
        
        # Claude
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                self.llm_manager.register_provider("claude", ClaudeProvider())
                providers_initialized.append("claude")
            except Exception as e:
                logging.warning(f"Failed to initialize Claude provider: {e}")
        
        # ZhipuAI
        if os.getenv("ZHIPU_API_KEY"):
            try:
                self.llm_manager.register_provider("zhipu", ZhipuAIProvider())
                providers_initialized.append("zhipu")
            except Exception as e:
                logging.warning(f"Failed to initialize ZhipuAI provider: {e}")
        
        # DashScope
        if os.getenv("DASHSCOPE_API_KEY"):
            try:
                self.llm_manager.register_provider("dashscope", DashScopeProvider())
                providers_initialized.append("dashscope")
            except Exception as e:
                logging.warning(f"Failed to initialize DashScope provider: {e}")
        
        # Set default provider
        if providers_initialized:
            default = self.config.get("default_llm_provider", providers_initialized[0])
            if default not in providers_initialized:
                default = providers_initialized[0]
            try:
                self.llm_manager.set_default_provider(default)
                logging.info(f"Default LLM provider set to: {default}")
            except Exception as e:
                logging.warning(f"Failed to set default provider: {e}")
        else:
            logging.warning("No LLM providers initialized. Please set API keys.")
    
    def _send_alert(self, alert_type: str, message: str, details: Optional[Dict] = None):
        """
        Send alert via Feishu if available
        
        Args:
            alert_type: Alert type (error, warning, info, success)
            message: Alert message
            details: Additional details
        """
        if self.feishu_notifier:
            try:
                self.feishu_notifier.send_system_alert(alert_type, message, details)
            except Exception as e:
                logging.warning(f"Failed to send Feishu alert: {e}")
    
    def add_document_to_knowledge_base(self, knowledge_base_id: str, file_path: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Add a document to a knowledge base (with enhanced error handling)
        """
        if not self.vector_store:
            error = {"error": "Vector store not initialized"}
            self._send_alert("error", "Cannot add document: Vector store unavailable", error)
            return self.error_handler.create_error_response(error, "Service temporarily unavailable")
        
        if not self.document_parser:
            error = {"error": "Document parser not initialized"}
            self._send_alert("error", "Cannot add document: Parser unavailable", error)
            return self.error_handler.create_error_response(error, "Service temporarily unavailable")
        
        try:
            # Validate file exists
            if not os.path.exists(file_path):
                return self.error_handler.create_error_response(
                    {"file": file_path, "error": "File not found"},
                    f"File {file_path} does not exist"
                )
            
            # Parse the document
            parsed_content = self.document_parser.parse_document(file_path)
            
            if not parsed_content.strip():
                error = {"error": "Empty document"}
                self._send_alert("warning", f"Empty document uploaded: {file_path}", error)
                return self.error_handler.create_error_response(error, "The document appears to be empty")
            
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
            
            # Send success notification
            self._send_alert("success", 
                f"Document added to knowledge base '{knowledge_base_id}'",
                {"file": Path(file_path).name, "size": len(parsed_content)})
            
            return result
            
        except Exception as e:
            error_info = self.error_handler.handle_exception(e, "add_document_to_knowledge_base")
            self._send_alert("error", "Failed to add document to knowledge base", error_info)
            return self.error_handler.create_error_response(error_info, "Failed to process document")
    
    async def add_url_to_knowledge_base(self, knowledge_base_id: str, url: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Add content from a URL to a knowledge base (with enhanced error handling)
        """
        if not self.vector_store:
            error = {"error": "Vector store not initialized"}
            self._send_alert("error", "Cannot add URL: Vector store unavailable", error)
            return self.error_handler.create_error_response(error, "Service temporarily unavailable")
        
        if not self.web_scraper:
            error = {"error": "Web scraper not initialized"}
            self._send_alert("error", "Cannot add URL: Scraper unavailable", error)
            return self.error_handler.create_error_response(error, "Service temporarily unavailable")
        
        try:
            # Validate URL
            if not url.startswith(('http://', 'https://')):
                return self.error_handler.create_error_response(
                    {"url": url, "error": "Invalid URL format"},
                    "URL must start with http:// or https://"
                )
            
            # Scrape the URL content
            content = await self.web_scraper.scrape_url(url)
            
            if not content.strip():
                error = {"url": url, "error": "Empty content"}
                self._send_alert("warning", f"URL returned empty content: {url}", error)
                return self.error_handler.create_error_response(error, "The URL contains no extractable content")
            
            # Save content temporarily
            temp_file_path = f"./temp_scraped_{knowledge_base_id}_{hash(url) % 10000}.txt"
            try:
                with open(temp_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Add to vector store
                collection_name = self.vector_store.add_document(knowledge_base_id, temp_file_path, metadata)
                
                # Get metadata
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
                
                # Send success notification
                self._send_alert("success",
                    f"URL content added to knowledge base '{knowledge_base_id}'",
                    {"url": url, "title": metadata_result.get('title', 'Unknown')})
                
                return result
                
            finally:
                # Clean up
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
            
        except Exception as e:
            error_info = self.error_handler.handle_exception(e, "add_url_to_knowledge_base")
            self._send_alert("error", f"Failed to add URL content: {url}", error_info)
            return self.error_handler.create_error_response(error_info, "Failed to scrape and process URL")
    
    def query_knowledge_base(self, knowledge_base_id: str, query: str, k: int = 5) -> Dict:
        """
        Query a knowledge base for relevant information
        """
        if not self.vector_store:
            error = {"error": "Vector store not initialized"}
            return self.error_handler.create_error_response(error, "Service temporarily unavailable")
        
        try:
            if not query.strip():
                return self.error_handler.create_error_response(
                    {"query": query, "error": "Empty query"},
                    "Query cannot be empty"
                )
            
            results = self.vector_store.similarity_search(knowledge_base_id, query, k)
            
            result = {
                "success": True,
                "knowledge_base_id": knowledge_base_id,
                "query": query,
                "results": results,
                "count": len(results),
                "timestamp": datetime.now().isoformat()
            }
            
            logging.info(f"Successfully queried knowledge base with {len(results)} results")
            return result
            
        except Exception as e:
            error_info = self.error_handler.handle_exception(e, "query_knowledge_base")
            return self.error_handler.create_error_response(error_info, "Failed to search knowledge base")
    
    def generate_response(self, messages: List[Dict], provider: Optional[str] = None, **kwargs) -> Dict:
        """
        Generate a response using the LLM
        """
        if not self.llm_manager or not self.llm_manager.list_providers():
            error = {"error": "No LLM providers available"}
            return self.error_handler.create_error_response(error, "AI service is currently unavailable")
        
        try:
            if not messages:
                return self.error_handler.create_error_response(
                    {"messages": "empty", "error": "No messages provided"},
                    "Messages cannot be empty"
                )
            
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
            error_info = self.error_handler.handle_exception(e, "generate_response")
            return self.error_handler.create_error_response(error_info, "Failed to generate AI response")
    
    def create_knowledge_base(self, knowledge_base_id: str, name: str, description: str = "") -> Dict:
        """
        Create a new knowledge base
        """
        try:
            existing_kbs = self.vector_store.list_knowledge_bases() if self.vector_store else []
            
            result = {
                "success": True,
                "knowledge_base_id": knowledge_base_id,
                "name": name,
                "description": description,
                "already_exists": knowledge_base_id in existing_kbs,
                "timestamp": datetime.now().isoformat()
            }
            
            logging.info(f"Processed knowledge base creation request: {result}")
            
            # Send notification
            self._send_alert("info",
                f"Knowledge base '{name}' {'already exists' if result['already_exists'] else 'created'}",
                {"id": knowledge_base_id})
            
            return result
            
        except Exception as e:
            error_info = self.error_handler.handle_exception(e, "create_knowledge_base")
            self._send_alert("error", "Failed to create knowledge base", error_info)
            return self.error_handler.create_error_response(error_info, "Failed to create knowledge base")
    
    def list_knowledge_bases(self) -> Dict:
        """
        List all available knowledge bases
        """
        try:
            kb_list = self.vector_store.list_knowledge_bases() if self.vector_store else []
            
            result = {
                "success": True,
                "knowledge_bases": kb_list,
                "count": len(kb_list),
                "timestamp": datetime.now().isoformat()
            }
            
            logging.info(f"Listed {result['count']} knowledge bases")
            return result
            
        except Exception as e:
            error_info = self.error_handler.handle_exception(e, "list_knowledge_bases")
            return self.error_handler.create_error_response(error_info, "Failed to list knowledge bases")
    
    def get_system_health(self) -> Dict:
        """
        Get system health status
        
        Returns:
            Health status dictionary
        """
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # Check each component
        components = {
            "vector_store": self.vector_store,
            "document_parser": self.document_parser,
            "web_scraper": self.web_scraper,
            "llm_manager": self.llm_manager,
            "feishu_notifier": self.feishu_notifier
        }
        
        unhealthy_count = 0
        for name, component in components.items():
            if component:
                health["components"][name] = {"status": "healthy"}
            else:
                health["components"][name] = {"status": "unavailable"}
                unhealthy_count += 1
        
        if unhealthy_count > 0:
            health["status"] = "degraded" if unhealthy_count < len(components) else "unhealthy"
        
        return health
    
    def send_daily_report(self, custom_data: Optional[Dict] = None) -> Dict:
        """
        Generate and send daily operational report
        
        Args:
            custom_data: Optional custom data to include in report
            
        Returns:
            Result of sending report
        """
        try:
            # Collect basic stats
            health = self.get_system_health()
            kb_stats = self.list_knowledge_bases()
            
            report_data = {
                "total_knowledge_bases": kb_stats.get("count", 0),
                "llm_providers": self.llm_manager.list_providers() if self.llm_manager else [],
                "system_status": health["status"],
                "report_date": datetime.now().strftime("%Y-%m-%d")
            }
            
            # Add custom data if provided
            if custom_data:
                report_data.update(custom_data)
            
            # Send via Feishu if available
            if self.feishu_notifier:
                result = self.feishu_notifier.send_daily_report(report_data)
                if result.get("success"):
                    logging.info("Daily report sent successfully")
                    return {"success": True, "message": "Report sent", "data": report_data}
                else:
                    return {"success": False, "error": result.get("error"), "data": report_data}
            else:
                logging.info("Feishu notifier not available, report data logged instead")
                return {"success": True, "message": "Report data prepared (no Feishu)", "data": report_data}
                
        except Exception as e:
            error_info = self.error_handler.handle_exception(e, "send_daily_report")
            return self.error_handler.create_error_response(error_info, "Failed to generate daily report")


def create_flask_app(service: EnhancedAICustomerService):
    """
    Create a Flask app to serve the AI customer service API
    """
    try:
        from flask import Flask, request, jsonify
        from flask_cors import CORS
    except ImportError:
        raise ImportError("Flask is required. Install with: pip install flask flask-cors")
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        health = service.get_system_health()
        status_code = 200 if health["status"] in ["healthy", "degraded"] else 503
        return jsonify(health), status_code
    
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
            error_info = service.error_handler.handle_exception(e, "api.create_knowledge_base")
            return jsonify(service.error_handler.create_error_response(error_info)), 500
    
    @app.route('/knowledge/bases', methods=['GET'])
    def list_knowledge_bases():
        """List all knowledge bases"""
        try:
            result = service.list_knowledge_bases()
            return jsonify(result), 200 if result["success"] else 500
            
        except Exception as e:
            error_info = service.error_handler.handle_exception(e, "api.list_knowledge_bases")
            return jsonify(service.error_handler.create_error_response(error_info)), 500
    
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
            temp_path = f"./temp_upload_{kb_id}_{int(datetime.now().timestamp())}_{file.filename}"
            file.save(temp_path)
            
            try:
                # Parse metadata
                metadata = None
                if request.form.get('metadata'):
                    metadata = json.loads(request.form.get('metadata'))
                
                result = service.add_document_to_knowledge_base(kb_id, temp_path, metadata)
                return jsonify(result), 201 if result["success"] else 500
                
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
        except Exception as e:
            error_info = service.error_handler.handle_exception(e, "api.add_document")
            return jsonify(service.error_handler.create_error_response(error_info)), 500
    
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
            error_info = service.error_handler.handle_exception(e, "api.add_url")
            return jsonify(service.error_handler.create_error_response(error_info)), 500
    
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
            error_info = service.error_handler.handle_exception(e, "api.search")
            return jsonify(service.error_handler.create_error_response(error_info)), 500
    
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
            error_info = service.error_handler.handle_exception(e, "api.chat")
            return jsonify(service.error_handler.create_error_response(error_info)), 500
    
    @app.route('/admin/daily-report', methods=['POST'])
    def trigger_daily_report():
        """Manually trigger daily report (admin endpoint)"""
        try:
            result = service.send_daily_report()
            return jsonify(result), 200 if result["success"] else 500
        except Exception as e:
            error_info = service.error_handler.handle_exception(e, "api.daily_report")
            return jsonify(service.error_handler.create_error_response(error_info)), 500
    
    @app.route('/admin/health', methods=['GET'])
    def admin_health():
        """Detailed health check"""
        try:
            health = service.get_system_health()
            return jsonify(health), 200
        except Exception as e:
            error_info = service.error_handler.handle_exception(e, "api.admin_health")
            return jsonify(service.error_handler.create_error_response(error_info)), 500
    
    return app


def main():
    """
    Main entry point for standalone execution
    """
    print("Initializing Enhanced AI Customer Service...")
    
    # Initialize the service
    service = EnhancedAICustomerService()
    
    # Print summary
    print("\n" + "="*60)
    print("SYSTEM INITIALIZATION COMPLETE")
    print("="*60)
    
    health = service.get_system_health()
    print(f"System Status: {health['status'].upper()}")
    
    print("\nComponents:")
    for comp, status in health["components"].items():
        status_icon = "✓" if status["status"] == "healthy" else "✗"
        print(f"  {status_icon} {comp}: {status['status']}")
    
    if service.llm_manager:
        providers = service.llm_manager.list_providers()
        print(f"\nAvailable LLM providers: {', '.join(providers) if providers else 'None'}")
    
    if service.feishu_notifier:
        print("Feishu notifications: enabled")
    else:
        print("Feishu notifications: disabled (configure FEISHU_* env vars)")
    
    print("\n" + "="*60)
    
    # Check if Flask is available
    try:
        from flask import Flask
        print("Starting Flask API server on port 8000...")
        app = create_flask_app(service)
        port = int(os.getenv("PORT", 8000))
        app.run(host='0.0.0.0', port=port, debug=False)
    except ImportError:
        print("Flask not available. Running in standalone mode.")
        print("Service is ready for use via code interface.")
        
        # Keep the service alive for interactive testing
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")


if __name__ == "__main__":
    main()