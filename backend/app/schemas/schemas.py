"""
API 请求/响应数据模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator


# ========== 知识库相关 ==========

class KnowledgeBaseCreate(BaseModel):
    """创建知识库请求"""
    name: str = Field(..., min_length=1, max_length=100, description="知识库名称")
    description: Optional[str] = Field(default=None, max_length=500, description="描述")


class KnowledgeBaseResponse(BaseModel):
    """知识库响应"""
    id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    document_count: int = 0

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """文档上传响应"""
    id: str
    filename: str
    file_type: str
    status: str  # processing, completed, failed
    message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    """向量检索请求"""
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=50)
    score_threshold: Optional[float] = Field(default=0.6, ge=0, le=1)


class SearchResult(BaseModel):
    """检索结果"""
    text: str
    metadata: Dict[str, Any]
    score: Optional[float] = None
    distance: Optional[float] = None


# ========== 对话相关 ==========

class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., regex="^(user|assistant|system)$")
    content: str = Field(..., min_length=1, max_length=10000)


class ChatRequest(BaseModel):
    """对话请求"""
    knowledge_base_id: str = Field(..., description="知识库ID")
    message: str = Field(..., min_length=1, max_length=4000)
    provider: Optional[str] = Field(default=None, description="LLM 提供者：openai/claude/zhipu/dashscope")
    temperature: float = Field(default=0.7, ge=0, le=2)
    stream: bool = Field(default=False)
    history: Optional[List[ChatMessage]] = Field(default=None, max_length=20)


class ChatResponse(BaseModel):
    """对话响应"""
    answer: str
    sources: List[SearchResult] = []
    provider: str
    tokens_used: Optional[int] = None
    conversation_id: Optional[str] = None


# ========== 用户与会话 ==========

class UserCreate(BaseModel):
    """创建用户"""
    email: str = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100)
    name: Optional[str] = Field(default=None, max_length=50)


class UserResponse(BaseModel):
    """用户响应"""
    id: str
    email: str
    name: Optional[str] = None
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT Token"""
    access_token: str
    token_type: str = "bearer"


# ========== 支付相关 ==========

class OrderCreate(BaseModel):
    """创建订单"""
    plan_id: str = Field(..., description="套餐ID")
    payment_method: str = Field(..., regex="^(alipay|wechat)$")


class OrderResponse(BaseModel):
    """订单响应"""
    id: str
    amount: float
    status: str  # pending, paid, cancelled
    payment_method: str
    payment_url: Optional[str] = None  # 支付跳转链接
    created_at: datetime

    class Config:
        from_attributes = True


class PaymentNotify(BaseModel):
    """支付回调通知"""
    # 支付宝/微信支付回调的具体字段由 SDK 决定
    pass


class InvoiceRequest(BaseModel):
    """开票请求"""
    order_id: str
    invoice_type: str = Field(..., regex="^(personal|company)$")
    title: str = Field(..., max_length=200)
    tax_no: Optional[str] = Field(default=None, max_length=50)


# ========== 系统通知 ==========

class NotificationRequest(BaseModel):
    """飞书通知请求"""
    title: str = Field(..., max_length=200)
    content: str = Field(..., max_length=5000)
    at_all: bool = False
    at_users: Optional[List[str]] = None
    send_card: bool = False
    theme_color: str = Field(default="blue", regex="^(blue|green|orange|red)$")


# ========== 设置相关 ==========

class ModelSettingsUpdate(BaseModel):
    """模型设置更新"""
    default_provider: str = Field(..., description="默认 LLM 提供者")
    temperature: Optional[float] = Field(default=0.7, ge=0, le=2)
    top_k: Optional[int] = Field(default=5, ge=1, le=50)


class ApiKeyUpdate(BaseModel):
    """API 密钥更新"""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    zhipu_api_key: Optional[str] = None
    dashscope_api_key: Optional[str] = None

    @validator('openai_api_key', 'anthropic_api_key', 'zhipu_api_key', 'dashscope_api_key')
    def validate_keys(cls, v):
        if v and len(v) < 10:
            raise ValueError("API 密钥格式不正确")
        return v


class SystemInfo(BaseModel):
    """系统信息"""
    version: str
    environment: str
    vector_db: str
    llm_providers: List[str]
    uptime: float

