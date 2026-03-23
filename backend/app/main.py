"""
FastAPI 主应用入口
"""

import os
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.core.config import settings
from app.core.error_handlers import setup_exception_handlers
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service  # noqa: F401
from app.api import knowledge, chat, settings as settings_api, payment, quality

# 配置结构化日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("starting_application", env=settings.environment)
    yield
    # 关闭时
    logger.info("shutting_down_application")

app = FastAPI(
    title= "AI Customer Service API",
    version="1.0.0",
    description="智能客服系统后端 API",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"] if settings.debug else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(knowledge.router)
app.include_router(chat.router)
app.include_router(settings_api.router)
app.include_router(payment.router)
app.include_router(quality.router)

# 注册异常处理器
setup_exception_handlers(app)

@app.get("/")
async def root():
    """健康检查"""
    return {
        "service": "ai-customer-service-api",
        "status": "running",
        "time": datetime.utcnow().isoformat(),
        "environment": settings.environment
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        # 检查向量库连接
        stats = vector_store.get_collection_stats()

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "vector_db": stats,
            "llm_providers": llm_service.list_available_providers()
        }
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/metrics")
async def metrics():
    """Prometheus 指标（TODO）"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.environment
    )
