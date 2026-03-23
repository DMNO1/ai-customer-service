"""
Main Routes
定义AI客服系统的主要API端点。
"""

from flask import Blueprint, request, jsonify
from ..utils.error_handler import handle_api_error
from ...scripts.rag_pipeline import RAGPipeline

# 创建蓝图
main_bp = Blueprint('main', __name__)

# 初始化RAG管道（在实际应用中，这应该是一个单例或通过依赖注入）
rag_pipeline = None

def init_rag():
    global rag_pipeline
    if rag_pipeline is None:
        try:
            rag_pipeline = RAGPipeline()
        except Exception as e:
            print(f"Failed to initialize RAG pipeline: {e}")
            rag_pipeline = None

@main_bp.route('/api/ask', methods=['POST'])
def ask_question():
    """
    处理用户提问的API端点。
    """
    try:
        # 确保RAG管道已初始化
        if rag_pipeline is None:
            init_rag()
            if rag_pipeline is None:
                return jsonify({
                    "success": False,
                    "error": {
                        "code": 503,
                        "message": "Service unavailable",
                        "details": "The AI service is not ready. Please try again later."
                    }
                }), 503
        
        # 解析请求
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({
                "success": False,
                "error": {
                    "code": 400,
                    "message": "Bad request",
                    "details": "Missing 'question' field in request body."
                }
            }), 400
        
        question = data['question']
        if not isinstance(question, str) or len(question.strip()) == 0:
            return jsonify({
                "success": False,
                "error": {
                    "code": 400,
                    "message": "Bad request",
                    "details": "'question' must be a non-empty string."
                }
            }), 400
        
        # 获取答案
        result = rag_pipeline.answer_question(question)
        
        return jsonify({
            "success": True,
            "answer": result["answer"],
            "sources": result["sources"]
        })
    except Exception as e:
        # 使用错误处理程序
        return handle_api_error(e)

@main_bp.route('/api/health', methods=['GET'])
def health_check():
    """
    健康检查端点。
    """
    return jsonify({
        "success": True,
        "status": "healthy",
        "service": "AI Customer Service"
    })