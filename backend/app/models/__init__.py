"""
数据库模型基类
"""

# 从 models.py 导入所有模型和 Base
from app.models.models import (
    Base,
    User,
    KnowledgeBase,
    Document,
    Conversation,
    Message,
    Subscription,
    Order,
    QualityInspection,
    QualityRule,
    AuditLog
)

__all__ = [
    "Base",
    "User",
    "KnowledgeBase",
    "Document",
    "Conversation",
    "Message",
    "Subscription",
    "Order",
    "QualityInspection",
    "QualityRule",
    "AuditLog"
]
