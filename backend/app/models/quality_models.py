"""
质检相关数据库模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.models import Base

class QualityInspection(Base):
    """对话质检记录表"""
    __tablename__ = "quality_inspections"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)  # 针对哪条助手回复
    inspection_type = Column(String(50), default="auto")  # auto, manual
    response_time_seconds = Column(Float, default=0.0)  # 响应时间(秒)
    keywords_detected = Column(Text, default="[]")  # JSON数组: 检测到的关键词
    quality_score = Column(Integer, default=0)  # 总分 0-100
    has_issues = Column(Boolean, default=False)  # 是否发现问题
    issues_found = Column(Text, default="[]")  # JSON数组: 发现的问题详情
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 质检员(人工质检时)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 关系
    conversation = relationship("Conversation", back_populates="quality_inspections")
    message = relationship("Message", back_populates="quality_inspections")
    inspector = relationship("User", back_populates="quality_inspections")

    def __repr__(self):
        return f"<QualityInspection(id={self.id}, score={self.quality_score}, has_issues={self.has_issues})>"

class QualityRule(Base):
    """质检规则配置表"""
    __tablename__ = "quality_rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String(100), nullable=False)  # 规则名称
    rule_type = Column(String(50), nullable=False)  # response_time, keywords, length, sentiment
    condition = Column(Text, nullable=False)  # JSON: {"threshold": 5, "operator": ">"} 等
    score_impact = Column(Integer, default=0)  # 对总分的扣分/加分
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<QualityRule(id={self.id}, name={self.rule_name}, type={self.rule_type})>"