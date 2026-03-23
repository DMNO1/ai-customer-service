"""
配置管理模块 - 环境变量加载与验证
"""
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional
import os

class Settings(BaseSettings):
    """应用配置"""

    # 数据库
    database_url: str = Field(default="postgresql+psycopg2://postgres:password@localhost:5432/cs", alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # API 密钥
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    zhipu_api_key: Optional[str] = Field(default=None, alias="ZHIPU_API_KEY")
    dashscope_api_key: Optional[str] = Field(default=None, alias="DASHSCOPE_API_KEY")

    # 飞书
    feishu_webhook_url: Optional[str] = Field(default=None, alias="FEISHU_WEBHOOK_URL")
    feishu_app_id: Optional[str] = Field(default=None, alias="FEISHU_APP_ID")
    feishu_app_secret: Optional[str] = Field(default=None, alias="FEISHU_APP_SECRET")

    # 支付
    alipay_app_id: Optional[str] = Field(default=None, alias="ALIPAY_APP_ID")
    alipay_private_key: Optional[str] = Field(default=None, alias="ALIPAY_PRIVATE_KEY")
    alipay_public_key: Optional[str] = Field(default=None, alias="ALIPAY_PUBLIC_KEY")
    wechat_app_id: Optional[str] = Field(default=None, alias="WECHAT_APP_ID")
    wechat_mch_id: Optional[str] = Field(default=None, alias="WECHAT_MCH_ID")
    wechat_api_key: Optional[str] = Field(default=None, alias="WECHAT_API_KEY")

    # JWT
    secret_key: str = Field(default="dev-secret-change-in-production", alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # 应用
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")

    # 向量数据库
    vector_db: str = Field(default="chroma", alias="VECTOR_DB")
    chroma_persist_dir: str = Field(default="./data/chroma", alias="CHROMA_PERSIST_DIR")
    milvus_host: str = Field(default="localhost", alias="MILVUS_HOST")
    milvus_port: int = Field(default=19530, alias="MILVUS_PORT")

    # 邮件
    smtp_host: str = Field(default="smtp.gmail.com", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, alias="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, alias="SMTP_PASSWORD")
    email_from: str = Field(default="noreply@example.com", alias="EMAIL_FROM")

    # 质检配置
    quality_inspection_enabled: bool = Field(default=True, alias="QUALITY_INSPECTION_ENABLED")
    quality_response_time_threshold: int = Field(default=5, alias="QUALITY_RESPONSE_TIME_THRESHOLD")
    quality_min_response_length: int = Field(default=10, alias="QUALITY_MIN_RESPONSE_LENGTH")
    quality_max_response_length: int = Field(default=2000, alias="QUALITY_MAX_RESPONSE_LENGTH")
    quality_batch_schedule: Optional[str] = Field(default=None, alias="QUALITY_BATCH_SCHEDULE")
    quality_alert_webhook: Optional[str] = Field(default=None, alias="QUALITY_ALERT_WEBHOOK")

    @field_validator("database_url")
    @classmethod
    def validate_db_url(cls, v):
        if not v.startswith("postgresql"):
            raise ValueError("仅支持 PostgreSQL 数据库")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
