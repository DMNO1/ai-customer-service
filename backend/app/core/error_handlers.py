"""
全局异常处理器
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.core.exceptions import (
    AppException,
    ValidationException,
    NotFoundException,
    LLMException,
    VectorStoreException,
    DocumentParseException,
    FeishuNotificationException
)
import structlog

logger = structlog.get_logger()

async def app_exception_handler(request: Request, exc: AppException):
    """应用异常处理器"""
    logger.error(
        "app_exception",
        path=request.url.path,
        code=exc.code,
        message=exc.message,
        details=exc.details
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 异常处理器"""
    logger.warning(
        "http_exception",
        path=request.url.path,
        status_code=exc.status_code,
        detail=exc.detail
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail
            }
        }
    )

async def validation_exception_handler(request: Request, exc: ValidationException):
    """验证异常处理器"""
    logger.info(
        "validation_error",
        path=request.url.path,
        message=exc.message
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": exc.message,
                "details": exc.details
            }
        }
    )

async def not_found_handler(request: Request, exc: NotFoundException):
    """资源未找到处理器"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": exc.message,
                "details": exc.details
            }
        }
    )

async def llm_exception_handler(request: Request, exc: LLMException):
    """LLM 异常处理器"""
    logger.error(
        "llm_error",
        path=request.url.path,
        provider=exc.details.get("provider"),
        error=exc.message
    )
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={
            "success": False,
            "error": {
                "code": "LLM_ERROR",
                "message": exc.message,
                "details": exc.details
            }
        }
    )

async def vector_store_exception_handler(request: Request, exc: VectorStoreException):
    """向量存储异常处理器"""
    logger.error(
        "vector_store_error",
        path=request.url.path,
        operation=exc.details.get("operation"),
        error=exc.message
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "VECTOR_STORE_ERROR",
                "message": exc.message,
                "details": exc.details
            }
        }
    )

def setup_exception_handlers(app):
    """注册所有异常处理器"""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(ValidationException, validation_exception_handler)
    app.add_exception_handler(NotFoundException, not_found_handler)
    app.add_exception_handler(LLMException, llm_exception_handler)
    app.add_exception_handler(VectorStoreException, vector_store_exception_handler)
