"""
系统设置 API 路由
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.api.schemas import ModelSettingsUpdate, ApiKeyUpdate, SystemInfo
from app.core.config import settings
from app.services.llm_service import llm_service
from app.services.vector_store import vector_store
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/settings", tags=["settings"])

@router.get("/models", response_model=dict)
async def get_model_settings():
    """获取模型配置"""
    return {
        "default_provider": llm_service.default_provider,
        "available_providers": llm_service.list_available_providers(),
        "vector_db": settings.vector_db
    }

@router.put("/models")
async def update_model_settings(data: ModelSettingsUpdate):
    """更新模型配置（重载服务）"""
    # 注意：这里仅更新内存配置，实际生产环境需要持久化到数据库
    llm_service.default_provider = data.default_provider

    logger.info("model_settings_updated",
                provider=data.default_provider,
                temperature=data.temperature)
    return {"success": True, "message": "配置已更新"}

@router.get("/system", response_model=SystemInfo)
async def get_system_info():
    """获取系统信息"""
    stats = vector_store.get_collection_stats()

    return SystemInfo(
        version="1.0.0",
        environment=settings.environment,
        vector_db=settings.vector_db,
        llm_providers=llm_service.list_available_providers(),
        uptime=0.0  # TODO: 记录启动时间
    )

@router.get("/api-keys")
async def get_api_key_status():
    """查看已配置的 API 密钥状态（不暴露密钥）"""
    return {
        "openai": bool(settings.openai_api_key),
        "anthropic": bool(settings.anthropic_api_key),
        "zhipu": bool(settings.zhipu_api_key),
        "dashscope": bool(settings.dashscope_api_key),
        "feishu": bool(settings.feishu_webhook_url)
    }

@router.post("/api-keys")
async def update_api_keys(data: ApiKeyUpdate):
    """更新 API 密钥（需要重载环境变量）"""
    # 这里应该将密钥写入 .env 文件或密钥管理服务
    # 当前版本仅返回确认信息
    logger.info("api_keys_update_requested")
    return {
        "success": True,
        "message": "API 密钥更新请求已接收，请重启服务以生效"
    }
