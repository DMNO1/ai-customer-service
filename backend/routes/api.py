"""
API路由模块
定义AI客服系统的所有API端点
"""

from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any
import os

from backend.utils.error_handler import (
    handle_api_error,
    success_response,
    ValidationError,
    NotFoundError,
    ServiceUnavailableError,
    validate_required_fields,
    validate_string_not_empty
)
from backend.utils.logger import system_logger
from backend.utils.health_checker import health_checker

# 创建蓝图
api_bp = Blueprint('api', __name__)

# 服务实例（将在应用启动时初始化）
rag_service = None
doc_parser = None
web_scraper = None


def init_services():
    """初始化所有服务（延迟加载，带优雅降级）"""
    global rag_service, doc_parser, web_scraper
    
    # RAG服务初始化（带超时和降级）
    try:
        import signal
        from contextlib import contextmanager
        
        @contextmanager
        def timeout(seconds):
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Operation timed out after {seconds} seconds")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                yield
            finally:
                signal.alarm(0)
        
        try:
            with timeout(30):  # 30秒超时
                from rag.query_engine import QueryEngine
                # 测试RAG服务是否真的可用
                rag_service = QueryEngine()
                # 快速健康检查
                try:
                    # 尝试一个简单的查询来验证
                    test_result = rag_service.query("test", n_results=1)
                    system_logger.info("RAG service initialized and health-check passed")
                except Exception as health_e:
                    system_logger.warning(f"RAG service initialized but health-check failed: {health_e}")
                    raise  # 重新抛出，进入except块
        except (TimeoutError, Exception) as e:
            system_logger.error(f"RAG service failed to initialize: {e}")
            system_logger.warning("RAG service will be disabled due to initialization failure")
            rag_service = None
            
    except ImportError as e:
        system_logger.error(f"Failed to import RAG modules: {e}")
        rag_service = None
    
    try:
        # 导入文档解析服务 - 使用绝对导入
        import sys
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        from services.document_parser import DocumentParser
        doc_parser = DocumentParser()
        system_logger.info("Document parser initialized successfully")
    except Exception as e:
        system_logger.error(f"Failed to initialize document parser: {e}")
        system_logger.error(f"Exception details: {str(e)}")
    
    try:
        # 导入网页抓取服务 - 使用绝对导入
        from services.web_scraper import WebScraper
        web_scraper = WebScraper()
        system_logger.info("Web scraper initialized successfully")
    except Exception as e:
        system_logger.error(f"Failed to initialize web scraper: {e}")
        system_logger.error(f"Exception details: {str(e)}")


# ==================== RAG API ====================

@api_bp.route('/v1/rag/query', methods=['POST'])
def rag_query():
    """
    RAG查询接口
    
    请求体:
    {
        "question": "用户问题",
        "top_k": 5,  # 可选，默认5
        "filter": {}  # 可选，元数据过滤
    }
    
    响应:
    {
        "success": true,
        "data": {
            "answer": "AI回答",
            "sources": [...],
            "confidence": 0.95
        }
    }
    """
    try:
        system_logger.info("Received RAG query request")
        
        # 解析请求
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")
        
        # 验证必需字段
        validate_required_fields(data, ['question'])
        validate_string_not_empty(data['question'], 'question')
        
        # 检查服务可用性
        if rag_service is None:
            raise ServiceUnavailableError("RAG service", "Service not initialized")
        
        # 获取参数
        question = data['question'].strip()
        top_k = data.get('top_k', 5)
        filters = data.get('filter', {})
        
        system_logger.info(f"Processing RAG query: {question[:50]}...")
        
        # 执行查询
        result = rag_service.query(
            query=question,
            top_k=top_k,
            filters=filters
        )
        
        # 格式化响应
        response_data = {
            "answer": result.get("answer", ""),
            "sources": result.get("sources", []),
            "context": result.get("context", {}),
            "confidence": result.get("confidence", 0.0)
        }
        
        system_logger.info(f"RAG query completed successfully")
        return success_response(data=response_data, message="Query processed successfully")
        
    except Exception as e:
        return handle_api_error(e)


@api_bp.route('/v1/rag/documents', methods=['POST'])
def add_documents():
    """
    添加文档到知识库
    
    请求体:
    {
        "documents": [
            {
                "content": "文档内容",
                "metadata": {"source": "...", "title": "..."}
            }
        ]
    }
    """
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")
        
        validate_required_fields(data, ['documents'])
        
        if not isinstance(data['documents'], list):
            raise ValidationError("'documents' must be an array")
        
        if rag_service is None:
            raise ServiceUnavailableError("RAG service")
        
        # 添加文档
        doc_ids = rag_service.add_documents(data['documents'])
        
        system_logger.info(f"Added {len(doc_ids)} documents to knowledge base")
        
        return success_response(
            data={"document_ids": doc_ids, "count": len(doc_ids)},
            message=f"Successfully added {len(doc_ids)} documents"
        )
        
    except Exception as e:
        return handle_api_error(e)


# ==================== 文档解析 API ====================

@api_bp.route('/v1/docs/parse', methods=['POST'])
def parse_document():
    """
    文档解析接口
    
    支持文件上传或URL
    
    请求:
    - multipart/form-data: 上传文件
    - JSON: {"url": "文档URL"}
    
    响应:
    {
        "success": true,
        "data": {
            "text": "解析后的文本",
            "metadata": {"filename": "...", "pages": 10}
        }
    }
    """
    try:
        system_logger.info("Received document parse request")
        
        if doc_parser is None:
            raise ServiceUnavailableError("Document parser")
        
        # 处理文件上传
        if 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                raise ValidationError("No file selected")
            
            # 读取文件内容
            file_content = file.read()
            filename = file.filename
            
            system_logger.info(f"Parsing uploaded file: {filename}")
            
            # 解析文档
            result = doc_parser.parse_file(file_content, filename)
            
        # 处理URL
        elif request.is_json:
            data = request.get_json()
            validate_required_fields(data, ['url'])
            
            url = data['url']
            system_logger.info(f"Parsing document from URL: {url}")
            
            result = doc_parser.parse_url(url)
        else:
            raise ValidationError("Either upload a file or provide a URL")
        
        return success_response(
            data={
                "text": result.get("text", ""),
                "metadata": result.get("metadata", {})
            },
            message="Document parsed successfully"
        )
        
    except Exception as e:
        return handle_api_error(e)


# ==================== 网页抓取 API ====================

@api_bp.route('/v1/web/scrape', methods=['POST'])
def scrape_webpage():
    """
    网页内容抓取接口
    
    请求体:
    {
        "url": "https://example.com",
        "selector": "article",  # 可选，CSS选择器
        "extract_links": false  # 可选，是否提取链接
    }
    
    响应:
    {
        "success": true,
        "data": {
            "title": "页面标题",
            "content": "清洗后的内容",
            "links": [...]  # 如果extract_links为true
        }
    }
    """
    try:
        system_logger.info("Received web scrape request")
        
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")
        
        validate_required_fields(data, ['url'])
        validate_string_not_empty(data['url'], 'url')
        
        if web_scraper is None:
            raise ServiceUnavailableError("Web scraper")
        
        url = data['url'].strip()
        selector = data.get('selector')
        extract_links = data.get('extract_links', False)
        
        system_logger.info(f"Scraping webpage: {url}")
        
        # 执行抓取
        result = web_scraper.scrape(
            url=url,
            selector=selector,
            extract_links=extract_links
        )
        
        return success_response(
            data={
                "title": result.get("title", ""),
                "content": result.get("content", ""),
                "links": result.get("links", []) if extract_links else None,
                "metadata": result.get("metadata", {})
            },
            message="Webpage scraped successfully"
        )
        
    except Exception as e:
        return handle_api_error(e)


# ==================== 健康检查 API ====================

@api_bp.route('/v1/health', methods=['GET'])
def health_check():
    """
    系统健康检查接口
    
    返回所有组件的健康状态
    """
    try:
        result = health_checker.check_all()
        
        # 根据整体状态返回不同的HTTP状态码
        status_code = 200 if result['status'] == 'healthy' else 503
        
        return jsonify({
            "success": result['status'] == 'healthy',
            "data": result
        }), status_code
        
    except Exception as e:
        return handle_api_error(e)


@api_bp.route('/v1/health/simple', methods=['GET'])
def simple_health_check():
    """
    简化健康检查接口
    仅返回服务是否可用
    """
    return jsonify({
        "success": True,
        "status": "healthy",
        "service": "AI Customer Service API",
        "version": "1.0.0"
    })


# ==================== 聊天 Widget API ====================

@api_bp.route('/v1/chat', methods=['POST'])
def chat():
    """
    聊天接口（Widget用）
    
    请求体:
    {
        "message": "用户消息",
        "session_id": "会话ID",  # 可选
        "context": {}  # 可选，上下文信息
    }
    """
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("Request body is required")
        
        validate_required_fields(data, ['message'])
        validate_string_not_empty(data['message'], 'message')
        
        if rag_service is None:
            raise ServiceUnavailableError("Chat service")
        
        message = data['message'].strip()
        session_id = data.get('session_id')
        context = data.get('context', {})
        
        system_logger.info(f"Chat message received: {message[:50]}...")
        
        # 使用RAG服务生成回复
        result = rag_service.query(
            query=message,
            top_k=5,
            session_id=session_id,
            context=context
        )
        
        return success_response(
            data={
                "reply": result.get("answer", ""),
                "sources": result.get("sources", []),
                "session_id": session_id or result.get("session_id"),
                "suggestions": result.get("suggestions", [])
            },
            message="Message processed successfully"
        )
        
    except Exception as e:
        return handle_api_error(e)


# ==================== 错误处理 ====================

@api_bp.errorhandler(Exception)
def handle_error(error):
    """全局错误处理"""
    return handle_api_error(error)
