"""
Settings UI Generator
生成设置页面的后端API。
"""

from flask import Blueprint, request, jsonify
import os
from dotenv import load_dotenv, set_key

# 加载环境变量
load_dotenv()

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/api/settings', methods=['GET'])
def get_settings():
    """
    获取当前系统设置（不包含敏感信息）。
    """
    return jsonify({
        "success": True,
        "data": {
            "flask_env": os.getenv("FLASK_ENV", "production"),
            "database_url_set": bool(os.getenv("DATABASE_URL")),
            "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic_api_key_set": bool(os.getenv("ANTHROPIC_API_KEY")),
            "pinecone_api_key_set": bool(os.getenv("PINECONE_API_KEY")),
            "stripe_secret_key_set": bool(os.getenv("STRIPE_SECRET_KEY")),
            "smtp_server_set": bool(os.getenv("SMTP_SERVER"))
        }
    })

@settings_bp.route('/api/settings', methods=['POST'])
def update_settings():
    """
    更新系统设置。
    注意：在生产环境中，此端点应有严格的认证和授权。
    """
    try:
        data = request.get_json()
        env_file = ".env"
        
        # 更新每个接收到的设置
        for key, value in data.items():
            if key.upper() in [
                "FLASK_ENV", "DATABASE_URL", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
                "OLLAMA_BASE_URL", "PINECONE_API_KEY", "PINECONE_ENVIRONMENT",
                "STRIPE_SECRET_KEY", "ALIPAY_APP_ID", "SMTP_SERVER", "SMTP_PORT",
                "SMTP_USERNAME", "SMTP_PASSWORD"
            ]:
                set_key(env_file, key.upper(), str(value))
        
        # 重新加载环境变量
        load_dotenv(override=True)
        
        return jsonify({"success": True, "message": "设置已更新"})
    except Exception as e:
        return jsonify({
            "success": False,
            "error": {
                "code": 500,
                "message": str(e),
                "details": "更新设置时发生错误。"
            }
        }), 500