"""
错误处理模块
提供统一的API错误处理和响应格式化
"""

import traceback
from typing import Dict, Any, Optional
from flask import jsonify, Response
from .logger import system_logger


class APIError(Exception):
    """
    自定义API错误类
    用于标准化的错误响应
    """
    
    def __init__(
        self,
        message: str,
        code: int = 500,
        details: Optional[str] = None,
        error_type: str = "internal_error"
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or message
        self.error_type = error_type


class ValidationError(APIError):
    """请求参数验证错误"""
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message, 400, details, "validation_error")


class AuthenticationError(APIError):
    """认证错误"""
    def __init__(self, message: str = "Authentication failed", details: Optional[str] = None):
        super().__init__(message, 401, details, "authentication_error")


class AuthorizationError(APIError):
    """授权错误"""
    def __init__(self, message: str = "Permission denied", details: Optional[str] = None):
        super().__init__(message, 403, details, "authorization_error")


class NotFoundError(APIError):
    """资源不存在错误"""
    def __init__(self, resource: str = "Resource", details: Optional[str] = None):
        super().__init__(f"{resource} not found", 404, details, "not_found")


class ServiceUnavailableError(APIError):
    """服务不可用错误"""
    def __init__(self, service: str = "Service", details: Optional[str] = None):
        super().__init__(f"{service} is unavailable", 503, details, "service_unavailable")


class RateLimitError(APIError):
    """请求频率限制错误"""
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[str] = None):
        super().__init__(message, 429, details, "rate_limit_exceeded")


def handle_api_error(error: Exception) -> Response:
    """
    通用API错误处理函数
    
    Args:
        error: 捕获的异常
        
    Returns:
        JSON格式的错误响应
    """
    # 如果是自定义API错误
    if isinstance(error, APIError):
        system_logger.error(
            f"API Error [{error.code}]: {error.message} - {error.error_type}",
            extra={'error_type': error.error_type, 'status_code': error.code}
        )
        
        response = {
            "success": False,
            "error": {
                "code": error.code,
                "type": error.error_type,
                "message": error.message,
                "details": error.details
            }
        }
        return jsonify(response), error.code
    
    # 处理其他未知错误
    error_traceback = traceback.format_exc()
    system_logger.error(f"Unexpected error: {str(error)}\n{error_traceback}")
    
    response = {
        "success": False,
        "error": {
            "code": 500,
            "type": "internal_server_error",
            "message": "An unexpected error occurred",
            "details": str(error) if system_logger.level <= 10 else "Please contact support"
        }
    }
    
    return jsonify(response), 500


def success_response(
    data: Any = None,
    message: str = "Success",
    meta: Optional[Dict[str, Any]] = None
) -> Response:
    """
    生成标准化的成功响应
    
    Args:
        data: 响应数据
        message: 成功消息
        meta: 元数据（如分页信息）
        
    Returns:
        JSON格式的成功响应
    """
    response = {
        "success": True,
        "message": message
    }
    
    if data is not None:
        response["data"] = data
    
    if meta is not None:
        response["meta"] = meta
    
    return jsonify(response)


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """
    验证请求数据中是否包含所有必需字段
    
    Args:
        data: 请求数据字典
        required_fields: 必需字段列表
        
    Raises:
        ValidationError: 当缺少必需字段时
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing_fields:
        raise ValidationError(
            message="Missing required fields",
            details=f"The following fields are required: {', '.join(missing_fields)}"
        )


def validate_field_type(value: Any, field_name: str, expected_type: type) -> None:
    """
    验证字段类型
    
    Args:
        value: 字段值
        field_name: 字段名称
        expected_type: 期望的类型
        
    Raises:
        ValidationError: 当类型不匹配时
    """
    if not isinstance(value, expected_type):
        raise ValidationError(
            message=f"Invalid type for field '{field_name}'",
            details=f"Expected {expected_type.__name__}, got {type(value).__name__}"
        )


def validate_string_not_empty(value: str, field_name: str) -> None:
    """
    验证字符串字段非空
    
    Args:
        value: 字段值
        field_name: 字段名称
        
    Raises:
        ValidationError: 当字符串为空时
    """
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(
            message=f"Field '{field_name}' cannot be empty",
            details=f"'{field_name}' must be a non-empty string"
        )
