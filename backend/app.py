"""
AI Customer Service - Backend Application
FastAPI/Flask后端主应用入口
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv(project_root / '.env')

from backend.utils.logger import setup_logger, system_logger
from backend.utils.error_handler import handle_api_error, APIError
from backend.utils.health_checker import health_checker


def create_app(config_name: str = None) -> Flask:
    """
    应用工厂函数
    
    Args:
        config_name: 配置环境名称 (development, production, testing)
        
    Returns:
        配置好的Flask应用实例
    """
    # 创建Flask应用
    app = Flask(__name__)
    
    # 加载配置
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    
    if config_name == 'production':
        app.config.from_mapping(
            DEBUG=False,
            TESTING=False,
            SECRET_KEY=os.getenv('SECRET_KEY', 'prod-secret-key-change-in-production'),
            DATABASE_URL=os.getenv('DATABASE_URL'),
            MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max file upload
        )
    elif config_name == 'testing':
        app.config.from_mapping(
            DEBUG=True,
            TESTING=True,
            SECRET_KEY='test-secret-key',
            DATABASE_URL=os.getenv('TEST_DATABASE_URL', 'sqlite:///:memory:'),
            MAX_CONTENT_LENGTH=16 * 1024 * 1024
        )
    else:  # development
        app.config.from_mapping(
            DEBUG=True,
            TESTING=False,
            SECRET_KEY=os.getenv('SECRET_KEY', 'dev-secret-key'),
            DATABASE_URL=os.getenv('DATABASE_URL', 'postgresql://localhost:5432/aics_dev'),
            MAX_CONTENT_LENGTH=16 * 1024 * 1024
        )
    
    # 启用CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": os.getenv('CORS_ORIGINS', '*').split(','),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 配置日志
    log_dir = project_root / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    logger = setup_logger(
        name='ai_customer_service',
        level=os.getenv('LOG_LEVEL', 'INFO'),
        log_dir=str(log_dir),
        enable_feishu=os.getenv('ENABLE_FEISHU_ALERT', 'false').lower() == 'true'
    )
    
    system_logger.info(f"Starting AI Customer Service in {config_name} mode")
    
    # 注册蓝图
    _register_blueprints(app)
    
    # 注册错误处理器
    _register_error_handlers(app)
    
    # 注册启动和关闭事件
    _register_lifecycle_events(app)
    
    # 根路由
    @app.route('/')
    def index():
        """API根目录"""
        return jsonify({
            "name": "AI Customer Service API",
            "version": "1.0.0",
            "status": "running",
            "docs": "/api/v1/docs",
            "health": "/api/v1/health"
        })
    
    system_logger.info("Application initialized successfully")
    
    return app


def _register_blueprints(app: Flask):
    """注册所有蓝图"""
    try:
        from backend.routes.api import api_bp
        
        # 注册API蓝图
        app.register_blueprint(api_bp, url_prefix='/api')
        
        # 初始化服务 - 在应用上下文外延迟初始化
        system_logger.info("Blueprints registered successfully")
        
        # 延迟服务初始化
        try:
            from backend.routes.api import init_services
            init_services()
            system_logger.info("Services initialized successfully")
        except Exception as e:
            system_logger.error(f"Failed to initialize services: {e}")
            # 继续运行，即使服务初始化失败
            system_logger.warning("Continuing without services...")
        
    except Exception as e:
        system_logger.error(f"Failed to register blueprints: {e}")
        raise


def _register_error_handlers(app: Flask):
    """注册错误处理器"""
    
    @app.errorhandler(APIError)
    def handle_api_exception(error: APIError):
        """处理自定义API错误"""
        return handle_api_error(error)
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """处理404错误"""
        return jsonify({
            "success": False,
            "error": {
                "code": 404,
                "type": "not_found",
                "message": "The requested resource was not found",
                "details": str(error)
            }
        }), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """处理405错误"""
        return jsonify({
            "success": False,
            "error": {
                "code": 405,
                "type": "method_not_allowed",
                "message": "The method is not allowed for this endpoint",
                "details": str(error)
            }
        }), 405
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """处理500错误"""
        system_logger.error(f"Internal server error: {error}")
        return jsonify({
            "success": False,
            "error": {
                "code": 500,
                "type": "internal_server_error",
                "message": "An internal server error occurred",
                "details": "Please contact support if the problem persists"
            }
        }), 500
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """处理所有未捕获的异常"""
        return handle_api_error(error)
    
    system_logger.info("Error handlers registered successfully")


def _register_lifecycle_events(app: Flask):
    """注册应用生命周期事件"""
    
    @app.before_request
    def before_request():
        """请求前处理"""
        pass  # 可以添加请求日志、认证检查等
    
    @app.after_request
    def after_request(response):
        """请求后处理"""
        # 添加安全响应头
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    @app.teardown_appcontext
    def teardown_appcontext(exception=None):
        """应用上下文销毁时处理"""
        pass  # 清理资源


def run_app():
    """运行应用"""
    app = create_app()
    
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'true').lower() == 'true'
    
    system_logger.info(f"Starting server on {host}:{port}")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )


if __name__ == '__main__':
    run_app()
