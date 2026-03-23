"""
自定义异常类定义
"""

class AppException(Exception):
    """应用基础异常"""
    def __init__(self, message: str, code: str = "APP_ERROR", details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

class ValidationException(AppException):
    """数据验证异常"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)

class NotFoundException(AppException):
    """资源未找到异常"""
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            f"{resource} with id '{identifier}' not found",
            code="NOT_FOUND",
            details={"resource": resource, "id": identifier}
        )

class UnauthorizedException(AppException):
    """认证失败异常"""
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, code="UNAUTHORIZED")

class PaymentException(AppException):
    """支付相关异常"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, code="PAYMENT_ERROR", details=details)

class LLMException(AppException):
    """大模型调用异常"""
    def __init__(self, message: str, provider: str = None, details: dict = None):
        d = details or {}
        if provider:
            d["provider"] = provider
        super().__init__(message, code="LLM_ERROR", details=d)

class VectorStoreException(AppException):
    """向量数据库异常"""
    def __init__(self, message: str, operation: str = None, details: dict = None):
        d = details or {}
        if operation:
            d["operation"] = operation
        super().__init__(message, code="VECTOR_STORE_ERROR", details=d)

class DocumentParseException(AppException):
    """文档解析异常"""
    def __init__(self, message: str, file_type: str = None, file_path: str = None):
        details = {}
        if file_type:
            details["file_type"] = file_type
        if file_path:
            details["file_path"] = file_path
        super().__init__(message, code="DOCUMENT_PARSE_ERROR", details=details)

class FeishuNotificationException(AppException):
    """飞书通知异常"""
    def __init__(self, message: str, webhook_url: str = None):
        details = {}
        if webhook_url:
            details["webhook_url"] = webhook_url
        super().__init__(message, code="FEISHU_NOTIFICATION_ERROR", details=details)
